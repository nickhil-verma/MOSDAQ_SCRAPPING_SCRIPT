 
# 🛰️ MOSDAQ_SCRAPPING_SCRIPT

This script scrapes job or data listings from various websites using `Playwright` and `BeautifulSoup`, then injects structured data into an **LLM like LLaMA or Gemma 3** running locally via **Ollama** for intelligent processing or filtering.

---

## ⚙️ Features

- 🌐 Headless web scraping with Playwright
- 🧠 LLM integration (LLaMA/Gemma 3 via Ollama)
- 🧽 Data cleaning and structuring with Pydantic
- 📦 MongoDB storage of raw and processed results

---

## 🧩 Tech Stack

- `playwright`
- `beautifulsoup4`
- `requests`
- `pymongo`
- `pydantic`
- `langchain` with `ollama` support
- `.env` for secure configs

---

## 🚀 How to Run Locally

### 1. 📦 Clone the Repository

```bash
git clone https://github.com/your-org/MOSDAQ_SCRAPPING_SCRIPT.git
cd MOSDAQ_SCRAPPING_SCRIPT
````

### 2. 🐍 Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. 📄 Install Requirements

```bash
pip install -r requirements.txt
```

> If you haven't already installed Playwright browsers:

```bash
playwright install
```

---

### 4. 🛠️ Set Up Your `.env` File

Create a `.env` file in the root directory with the following values:

```env
MONGO_URI=mongodb://localhost:27017
OLLAMA_HOST=http://localhost:11434
MODEL_NAME=gemma:3b-instruct
```

You can customize the model name if you're using something else like `llama3`.

---

### 5. 🧠 Make Sure Ollama is Running Locally

If you haven’t already:

* Install Ollama: [https://ollama.com](https://ollama.com)
* Pull a model:

```bash
ollama pull gemma:3b-instruct
```

* Start the Ollama server (usually auto-starts on Mac/Linux/WSL)

---

### 6. ▶️ Run the Scraper Script

```bash
python main.py
```

Replace `main.py` with your actual entry-point script filename.

---

## 📤 Output

* ✅ Scraped job listings are printed and/or stored in MongoDB.
* ✅ Validated data is injected into the LLM to extract job relevance or classification.

---

## 🧠 Tip for Using LangChain + Ollama

You may be using code like:

```python
from langchain_community.llms import Ollama

llm = Ollama(base_url=os.getenv("OLLAMA_HOST"), model=os.getenv("MODEL_NAME"))
response = llm.invoke("Summarize this job description...")
```

---

 
 
