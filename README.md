# AI Chatbot — Multi-Tool Intelligent Assistant

A full-stack AI chatbot demonstrating **conversational AI**, **web search**, **image generation**, and **RAG (Retrieval-Augmented Generation)** — all using free, open-source tools.

---

## Features

| Feature | Tool | Description |
|---------|------|-------------|
| **Chat** | Ollama (Llama 3.2) | Local LLM for conversational AI |
| **Web Search** | DuckDuckGo | Real-time web search, no API key |
| **Image Gen** | Stable Diffusion | AI image generation |
| **Knowledge (RAG)** | FAISS + MiniLM | Query your own documents |

---

## Architecture

```
User → Frontend (HTML/CSS/JS) → FastAPI Backend → LangChain Agent
                                                    ├── Ollama LLM
                                                    ├── DuckDuckGo Search
                                                    ├── Stable Diffusion
                                                    └── FAISS Vector DB
```

---

## Project Structure

```
AI-Chatbot-Project/
├── frontend/
│   ├── index.html          # Chat UI
│   ├── style.css           # Dark glassmorphic theme
│   └── app.js              # Frontend logic
├── backend/
│   ├── main.py             # FastAPI server
│   ├── agent.py            # Agent controller
│   ├── llm.py              # Ollama LLM
│   ├── search_tool.py      # DuckDuckGo search
│   ├── image_generator.py  # Stable Diffusion
│   ├── rag.py              # FAISS RAG
│   ├── config.py           # Configuration
│   └── requirements.txt    # Dependencies
├── database/
│   ├── documents/          # RAG documents
│   └── faiss_index/        # Vector index
├── .env.example            # Environment template
└── README.md               # This file!
```

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** (optional, for LLM — [download](https://ollama.com))

### Step 1 — Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — (Optional) Install & Start Ollama

```bash
# Download from https://ollama.com
ollama pull llama3.2
ollama serve
```

### Step 3 — Run the Server

```bash
cd backend
python main.py
```

### Step 4 — Open the Chatbot

Visit: **http://localhost:8000**

---

## Usage

### Quick Commands

| Command | Example | Description |
|---------|---------|-------------|
| (none) | `Hello, how are you?` | Regular chat |
| `/search` | `/search latest AI news` | Web search |
| `/image` | `/image a futuristic city` | Generate image |
| `/rag` | `/rag what do my documents say?` | Query knowledge base |

### Using RAG

1. Add `.txt` or `.md` files to `database/documents/`
2. Restart the server (auto-indexes on startup)
3. Use `/rag your question` to query

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `llama3.2` | LLM model name |
| `IMAGE_FALLBACK_MODE` | `true` | Use placeholder images |
| `SEARCH_MAX_RESULTS` | `5` | Number of search results |
| `SERVER_PORT` | `8000` | Server port |

---

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| GPU | Not required | NVIDIA GPU (for image gen) |
| Storage | 5 GB | 20 GB (with full models) |

---

## License

This project is for educational purposes. All tools used are free and open-source.

---


