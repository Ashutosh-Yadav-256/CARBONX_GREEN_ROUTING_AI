"""
FastAPI Server — Main entry point for the AI Chatbot backend.
"""

import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from config import CORS_ORIGINS, STATIC_DIR, SERVER_HOST, SERVER_PORT

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-18s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("server")

# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Chatbot",
    description="A multi-tool AI chatbot with chat, web search, image generation, and RAG.",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (generated images, etc.)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Serve frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


# ─── Models ───────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    type: str
    content: str
    image_url: str | None = None


class IngestRequest(BaseModel):
    text: str
    source_name: str = "manual_input"


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        return FileResponse(str(index_path), headers=headers)
    return {"message": "AI Chatbot API is running. Frontend not found at /frontend/index.html"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "AI Chatbot"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint. Automatically routes to the right tool
    based on the query intent (chat, search, image, RAG).
    """
    from agent import run_agent

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"📨 Query: {request.query[:100]}...")
    result = run_agent(request.query)

    return ChatResponse(
        type=result.get("type", "chat"),
        content=result.get("content", ""),
        image_url=result.get("image_url"),
    )


@app.post("/api/search")
async def search_endpoint(request: ChatRequest):
    """Direct search endpoint."""
    from search_tool import search_and_summarize

    response = search_and_summarize(request.query)
    return {"type": "search", "content": response}


@app.post("/api/generate-image")
async def image_endpoint(request: ChatRequest):
    """Direct image generation endpoint."""
    from image_generator import generate_image

    result = generate_image(request.query)
    return result


@app.post("/api/rag")
async def rag_endpoint(request: ChatRequest):
    """Direct RAG endpoint."""
    from rag import query as rag_query

    response = rag_query(request.query)
    return {"type": "rag", "content": response}


@app.post("/api/rag/ingest")
async def ingest_endpoint(request: IngestRequest):
    """Ingest text into the RAG knowledge base."""
    from rag import ingest_text

    result = ingest_text(request.text, request.source_name)
    return {"result": result}


# ─── Frontend static assets ──────────────────────────────────────────────────

@app.get("/style.css")
async def serve_css():
    css_path = FRONTEND_DIR / "style.css"
    if css_path.exists():
        return FileResponse(str(css_path), media_type="text/css")
    raise HTTPException(status_code=404, detail="CSS not found")


@app.get("/app.js")
async def serve_js():
    js_path = FRONTEND_DIR / "app.js"
    if js_path.exists():
        headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        return FileResponse(str(js_path), media_type="application/javascript", headers=headers)
    raise HTTPException(status_code=404, detail="JS not found")


# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 AI Chatbot server starting...")
    logger.info(f"   📂 Frontend: {FRONTEND_DIR}")
    logger.info(f"   📂 Static:   {STATIC_DIR}")
    logger.info(f"   🌐 CORS:     {CORS_ORIGINS}")
    logger.info("=" * 50)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
