"""
RAG (Retrieval-Augmented Generation) using FAISS vector database.
Ingests text documents and answers questions using similar content.
"""

import logging
from pathlib import Path
from config import DOCUMENTS_DIR, FAISS_INDEX_DIR, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP, RAG_TOP_K

logger = logging.getLogger(__name__)

# ─── Globals ──────────────────────────────────────────────────────────────────
_vectorstore = None
_rag_available = False


def _init_vectorstore():
    """Initialize FAISS vector store from documents."""
    global _vectorstore, _rag_available

    try:
        from langchain_community.vectorstores import FAISS
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain.text_splitter import RecursiveCharacterTextSplitter

        # Load embeddings model (small, runs on CPU)
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        # Check if we have a saved index
        index_file = FAISS_INDEX_DIR / "index.faiss"
        if index_file.exists():
            _vectorstore = FAISS.load_local(
                str(FAISS_INDEX_DIR), embeddings, allow_dangerous_deserialization=True
            )
            _rag_available = True
            logger.info("✅ FAISS index loaded from disk.")
            return

        # Otherwise, ingest documents
        docs = _load_documents()
        if not docs:
            logger.info("📂 No documents found in database/documents/. RAG inactive.")
            _rag_available = False
            return

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=RAG_CHUNK_SIZE,
            chunk_overlap=RAG_CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents(docs)

        # Create FAISS index
        _vectorstore = FAISS.from_documents(chunks, embeddings)
        _vectorstore.save_local(str(FAISS_INDEX_DIR))

        _rag_available = True
        logger.info(f"✅ FAISS index created with {len(chunks)} chunks from {len(docs)} documents.")

    except ImportError as e:
        _rag_available = False
        logger.warning(f"⚠️  RAG dependencies missing ({e}). Install: pip install faiss-cpu sentence-transformers")
    except Exception as e:
        _rag_available = False
        logger.warning(f"⚠️  RAG init failed: {e}")


def _load_documents():
    """Load text documents from the documents directory."""
    from langchain_community.document_loaders import TextLoader

    docs = []
    supported_extensions = {".txt", ".md", ".py", ".json", ".csv"}

    if not DOCUMENTS_DIR.exists():
        return docs

    for filepath in DOCUMENTS_DIR.iterdir():
        if filepath.is_file() and filepath.suffix.lower() in supported_extensions:
            try:
                loader = TextLoader(str(filepath), encoding="utf-8")
                docs.extend(loader.load())
                logger.info(f"📄 Loaded: {filepath.name}")
            except Exception as e:
                logger.warning(f"Failed to load {filepath.name}: {e}")

    return docs


def is_available() -> bool:
    """Check if RAG is available."""
    global _vectorstore, _rag_available
    if _vectorstore is None and not _rag_available:
        _init_vectorstore()
    return _rag_available


def query(question: str) -> str:
    """
    Query the RAG system.
    Retrieves similar documents and uses LLM to generate an answer.
    """
    if not is_available():
        return (
            "📚 **RAG is not active.**\n\n"
            "To use RAG:\n"
            "1. Add `.txt` or `.md` files to `database/documents/`\n"
            "2. Restart the server to index them\n"
            "3. Query with `/rag your question`"
        )

    try:
        # Retrieve similar documents
        results = _vectorstore.similarity_search(question, k=RAG_TOP_K)

        if not results:
            return f"No relevant documents found for: *\"{question}\"*"

        # Build context from retrieved docs
        context_parts = []
        sources = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "Unknown")
            context_parts.append(f"[Document {i}] ({source}):\n{doc.page_content}")
            if source not in sources:
                sources.append(source)

        context = "\n\n".join(context_parts)

        # Use LLM to generate answer
        try:
            import llm as llm_module
            if llm_module.is_available():
                answer = llm_module.chat(
                    prompt=question,
                    context=context,
                )
                source_list = "\n".join(f"- `{Path(s).name}`" for s in sources)
                return f"{answer}\n\n---\n**📚 Sources:**\n{source_list}"
        except Exception as e:
            logger.warning(f"LLM not available for RAG: {e}")

        # Fallback: return raw retrieved content
        source_list = "\n".join(f"- `{Path(s).name}`" for s in sources)
        return (
            f"📚 **Retrieved documents for:** *\"{question}\"*\n\n"
            f"{context}\n\n---\n**Sources:**\n{source_list}"
        )

    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        return f"⚠️ RAG query failed: {str(e)}"


def ingest_text(text: str, source_name: str = "manual_input") -> str:
    """Add new text to the vector store."""
    global _vectorstore, _rag_available

    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        doc = Document(page_content=text, metadata={"source": source_name})
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=RAG_CHUNK_SIZE,
            chunk_overlap=RAG_CHUNK_OVERLAP,
        )
        chunks = splitter.split_documents([doc])

        if _vectorstore is not None:
            _vectorstore.add_documents(chunks)
        else:
            _vectorstore = FAISS.from_documents(chunks, embeddings)

        _vectorstore.save_local(str(FAISS_INDEX_DIR))
        _rag_available = True

        return f"✅ Ingested {len(chunks)} chunks from '{source_name}' into the knowledge base."

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return f"⚠️ Ingestion failed: {str(e)}"
