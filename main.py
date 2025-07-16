import asyncio
import os
import re
import json
import time
from urllib.parse import urlparse, urljoin
from collections import deque
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from pydantic import BaseModel
from pymongo import MongoClient

from langchain_community.llms import Ollama

# --- Configuration ---
BASE_URL = "https://www.mosdac.gov.in"
DOMAIN = urlparse(BASE_URL).netloc
HTML_DIR = "scraped_html2"
OUTPUT_JSON = "mosdac_kg_dataset2.json"
MONGO_URI = "mongodb+srv://brakinbad2504:SvMQutloVN98wtyk@cluster0.12bhpqv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "knowledge_graph"
COLLECTION_NAME = "mosdac_nodes"

# --- Setup ---
os.makedirs(HTML_DIR, exist_ok=True)
visited = set()
queue = deque([(BASE_URL, 0)])
structured_data = []

# MongoDB
client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]

# LangChain Ollama
llm = Ollama(model="gemma3")

# --- Knowledge Graph Node Schema ---
class KGNode(BaseModel):
    url: str
    title: str
    concepts: list[str]
    entities: list[str]
    facts: list[str]
    timestamp: str
    source_type: str
    language: str
    crawl_depth: int

# --- Utility Functions ---
def url_to_filename(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_") or "index"
    return f"{parsed.netloc}_{path}.html"

def save_html(url, html):
    filepath = os.path.join(HTML_DIR, url_to_filename(url))
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    return filepath

def build_prompt(url, depth, timestamp, text):
    return f"""
You are a structured web reasoning model.

Extract a knowledge graph node in this JSON format:

{{
  "url": "{url}",
  "title": "<title of the page>",
  "concepts": ["..."], 
  "entities": ["..."],
  "facts": ["..."],
  "timestamp": "{timestamp}",
  "source_type": "HTML",
  "language": "en",
  "crawl_depth": {depth}
}}

---

Rules:
- Extract 5–10 concepts (themes/topics)
- Extract entities (places, institutions, people, missions)
- Facts should be full sentences (5–10)
- Language is "en"
- Use UTC timestamp

---

Page Text:
\"\"\"{text}\"\"\"
"""

# LangChain + Ollama wrapper
def run_llama_prompt(prompt: str, max_retries: int = 5) -> dict:
    for attempt in range(max_retries):
        try:
            print(f"🤖 Running LLaMA (try {attempt + 1})...")
            response = llm.invoke(prompt)
            json_match = re.search(r'{[\s\S]+}', response)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"⚠️ LangChain/Ollama error: {e}")
            time.sleep(3)
    print("❌ Max retries reached. Skipping this page.")
    return {}

# --- Main Async Crawler ---
async def scrape_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        while queue:
            url, depth = queue.popleft()
            if url in visited or DOMAIN not in urlparse(url).netloc:
                continue
            visited.add(url)

            try:
                print(f"\n🌐 Crawling: {url}")
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("load")
                html = await page.content()

                save_html(url, html)
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text(separator=" ", strip=True)
                timestamp = datetime.now(timezone.utc).isoformat()

                prompt = build_prompt(url, depth, timestamp, text)
                llama_output = run_llama_prompt(prompt)

                if llama_output:
                    node = KGNode(**llama_output)
                    structured_data.append(node.dict())
                    collection.insert_one(node.dict())
                    print(f"✅ Parsed & stored KG for {url}")
                else:
                    print(f"❌ No valid output from LLaMA for {url}")

                # Enqueue links
                for a_tag in soup.find_all("a", href=True):
                    full_url = urljoin(url, a_tag["href"])
                    if full_url not in visited and DOMAIN in urlparse(full_url).netloc:
                        queue.append((full_url, depth + 1))

            except Exception as e:
                print(f"⚠️ Failed: {url} — {e}")
                continue

        await browser.close()

    # Save locally
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(structured_data, f, indent=2)
    print(f"\n📦 All data saved to {OUTPUT_JSON} and MongoDB")

# --- Entry Point ---
if __name__ == "__main__":
    asyncio.run(scrape_all())
