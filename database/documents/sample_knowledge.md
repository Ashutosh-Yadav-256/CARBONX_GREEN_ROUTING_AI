# AI Chatbot — Sample Knowledge Base Document

This is a sample document for the RAG (Retrieval-Augmented Generation) system.
You can add your own .txt or .md files to this folder and they will be automatically
indexed when the server starts.

## About This Project

The AI Chatbot is a multi-tool intelligent assistant that combines:

- **Conversational AI**: Powered by Ollama with Llama 3.2 for natural language understanding
- **Web Search**: Real-time information retrieval via DuckDuckGo
- **Image Generation**: AI-powered image creation using Stable Diffusion
- **Knowledge Base (RAG)**: Query your own documents using FAISS vector search

## How RAG Works

1. Documents in this folder are loaded and split into chunks
2. Each chunk is converted into a numerical embedding using MiniLM
3. Embeddings are stored in a FAISS vector database
4. When you ask a question, it finds the most similar chunks
5. The LLM uses those chunks as context to generate an answer

## Supported File Types

- `.txt` — Plain text files
- `.md` — Markdown files
- `.py` — Python source files
- `.json` — JSON data files
- `.csv` — CSV data files

## Tips

- Keep documents focused on specific topics for better retrieval
- Shorter, well-structured documents work better than long, unstructured ones
- You can add documents at any time — just restart the server to re-index
