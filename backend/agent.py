"""
AI Agent Controller — routes user queries to the appropriate tool.
Uses intent detection to decide: chat, search, image generation, or RAG.
"""

import logging

logger = logging.getLogger(__name__)


# ─── Intent Detection Keywords ────────────────────────────────────────────────
IMAGE_KEYWORDS = [
    "generate image", "create image", "draw", "picture of", "illustration",
    "generate a photo", "make an image", "generate art", "create art",
    "design", "visualize", "imagine", "paint",
]

SEARCH_KEYWORDS = [
    "search", "latest", "news", "current", "today",
    "what is happening", "find out", "look up", "google",
    "who is", "what happened", "recent",
]

RAG_KEYWORDS = [
    "document", "knowledge base", "from the files", "in the database",
    "uploaded", "from my docs",
]


def detect_intent(query: str) -> str:
    """
    Detect the intent of a user query.

    Returns one of: 'image', 'search', 'rag', 'chat'
    """
    q = query.lower().strip()

    # Explicit command prefixes (highest priority)
    if q.startswith("/image ") or q.startswith("/img "):
        return "image"
    if q.startswith("/search ") or q.startswith("/s "):
        return "search"
    if q.startswith("/rag ") or q.startswith("/doc "):
        return "rag"

    # Keyword-based detection
    for kw in IMAGE_KEYWORDS:
        if kw in q:
            return "image"

    for kw in SEARCH_KEYWORDS:
        if kw in q:
            return "search"

    for kw in RAG_KEYWORDS:
        if kw in q:
            return "rag"

    return "chat"


def strip_command(query: str) -> str:
    """Remove command prefix from query."""
    prefixes = ["/image ", "/img ", "/search ", "/s ", "/rag ", "/doc "]
    q = query.strip()
    for prefix in prefixes:
        if q.lower().startswith(prefix):
            return q[len(prefix):].strip()
    return q


def run_agent(query: str) -> dict:
    """
    Main agent entry point. Detects intent and routes to appropriate tool.

    Returns:
        dict with 'type', 'content', and optionally 'image_url'
    """
    intent = detect_intent(query)
    clean_query = strip_command(query)

    logger.info(f"🧠 Intent: {intent} | Query: {clean_query[:80]}...")

    try:
        if intent == "image":
            return _handle_image(clean_query)
        elif intent == "search":
            return _handle_search(clean_query)
        elif intent == "rag":
            return _handle_rag(clean_query)
        else:
            return _handle_chat(clean_query)

    except Exception as e:
        logger.error(f"Agent error: {e}")
        return {
            "type": "error",
            "content": f"⚠️ Something went wrong: {str(e)}",
        }


def _handle_chat(query: str) -> dict:
    """Handle a general chat query."""
    import llm as llm_module
    response = llm_module.chat(query)
    return {
        "type": "chat",
        "content": response,
    }


def _handle_search(query: str) -> dict:
    """Handle a web search query."""
    from search_tool import search_and_summarize
    response = search_and_summarize(query)
    return {
        "type": "search",
        "content": response,
    }


def _handle_image(prompt: str) -> dict:
    """Handle an image generation request."""
    from image_generator import generate_image
    result = generate_image(prompt)
    return {
        "type": "image",
        "content": result["message"],
        "image_url": result["image_url"],
    }


def _handle_rag(query: str) -> dict:
    """Handle a RAG query."""
    from rag import query as rag_query
    response = rag_query(query)
    return {
        "type": "rag",
        "content": response,
    }
