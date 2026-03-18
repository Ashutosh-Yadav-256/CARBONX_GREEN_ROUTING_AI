"""
LLM integration via Ollama.
Falls back to simple echo responses if Ollama is not available.
"""

import logging
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS

logger = logging.getLogger(__name__)

# ─── Globals ──────────────────────────────────────────────────────────────────
_llm = None
_ollama_available = False


def _init_ollama():
    """Try to initialize the Ollama LLM."""
    global _llm, _ollama_available
    try:
        from langchain_ollama import OllamaLLM
        _llm = OllamaLLM(
            base_url=OLLAMA_BASE_URL,
            model=OLLAMA_MODEL,
            temperature=LLM_TEMPERATURE,
            num_predict=LLM_MAX_TOKENS,
        )
        # Quick test
        _llm.invoke("Hello")
        _ollama_available = True
        logger.info(f"✅ Ollama connected — model: {OLLAMA_MODEL}")
    except Exception as e:
        _ollama_available = False
        logger.warning(f"⚠️  Ollama not available ({e}). Using fallback mode.")


def get_llm():
    """Return the LLM instance (lazy init)."""
    global _llm, _ollama_available
    if _llm is None:
        _init_ollama()
    return _llm


def is_available() -> bool:
    """Check if Ollama is available."""
    if _llm is None:
        _init_ollama()
    return _ollama_available


def chat(prompt: str, context: str = "") -> str:
    """
    Send a prompt to the LLM and get a response.
    Falls back to a simple echo if Ollama is unavailable.
    """
    if not is_available():
        return _fallback_response(prompt)

    try:
        full_prompt = prompt
        if context:
            full_prompt = (
                f"Use the following context to help answer the question.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {prompt}\n\n"
                f"Answer:"
            )

        response = _llm.invoke(full_prompt)
        return response.strip()
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return _fallback_response(prompt)


def _fallback_response(prompt: str) -> str:
    """Provide a fallback response when Ollama is not available."""
    return (
        f"🤖 **[Fallback Mode]** — Ollama is not running.\n\n"
        f"To enable full AI responses:\n"
        f"1. Install Ollama from https://ollama.com\n"
        f"2. Run `ollama pull {OLLAMA_MODEL}`\n"
        f"3. Start Ollama\n\n"
        f"Your query was: *\"{prompt}\"*"
    )
