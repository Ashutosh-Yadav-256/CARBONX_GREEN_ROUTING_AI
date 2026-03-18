"""
Centralized configuration for the AI Chatbot backend.
All settings can be overridden via environment variables.
"""

import os
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
STATIC_DIR = BASE_DIR / "static"
GENERATED_IMAGES_DIR = STATIC_DIR / "generated"
DATABASE_DIR = PROJECT_DIR / "database"
DOCUMENTS_DIR = DATABASE_DIR / "documents"
FAISS_INDEX_DIR = DATABASE_DIR / "faiss_index"

# Create dirs on import
for d in [STATIC_DIR, GENERATED_IMAGES_DIR, DATABASE_DIR, DOCUMENTS_DIR, FAISS_INDEX_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── LLM (Ollama) ────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# ─── Image Generation ────────────────────────────────────────────────────────
IMAGE_MODEL_ID = os.getenv("IMAGE_MODEL_ID", "runwayml/stable-diffusion-v1-5")
IMAGE_INFERENCE_STEPS = int(os.getenv("IMAGE_INFERENCE_STEPS", "25"))
IMAGE_USE_GPU = os.getenv("IMAGE_USE_GPU", "auto")  # "auto", "true", "false"
IMAGE_FALLBACK_MODE = os.getenv("IMAGE_FALLBACK_MODE", "true")  # Use placeholder if model unavailable

# ─── Search ───────────────────────────────────────────────────────────────────
SEARCH_MAX_RESULTS = int(os.getenv("SEARCH_MAX_RESULTS", "5"))

# ─── RAG ──────────────────────────────────────────────────────────────────────
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "500"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))

# ─── Server ───────────────────────────────────────────────────────────────────
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
