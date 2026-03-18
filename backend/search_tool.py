"""
Web search tool using DuckDuckGo.
Free, no API key required.
"""

import logging
from config import SEARCH_MAX_RESULTS

logger = logging.getLogger(__name__)


def search_web(query: str, max_results: int = None) -> dict:
    """
    Search the web using DuckDuckGo and return formatted results.

    Returns:
        dict with 'results' list and 'summary' string
    """
    if max_results is None:
        max_results = SEARCH_MAX_RESULTS

    try:
        from ddgs import DDGS

        results = []
        ddgs = DDGS()
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", ""),
            })

        if not results:
            return {
                "results": [],
                "summary": f"No results found for '{query}'.",
            }

        # Build a human-readable summary
        summary_lines = [f"🔍 **Search results for:** *\"{query}\"*\n"]
        for i, r in enumerate(results, 1):
            summary_lines.append(
                f"**{i}. [{r['title']}]({r['url']})**\n"
                f"   {r['snippet']}\n"
            )

        return {
            "results": results,
            "summary": "\n".join(summary_lines),
        }

    except ImportError:
        logger.error("duckduckgo-search not installed")
        return {
            "results": [],
            "summary": "⚠️ Search unavailable — install `duckduckgo-search` package.",
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {
            "results": [],
            "summary": f"⚠️ Search failed: {str(e)}",
        }


def search_and_summarize(query: str) -> str:
    """Search the web, then use the LLM to summarize results."""
    search_result = search_web(query)

    if not search_result["results"]:
        return search_result["summary"]

    # Try to use LLM to create a better summary
    try:
        import llm as llm_module
        if llm_module.is_available():
            context = "\n\n".join(
                f"Source: {r['title']} ({r['url']})\n{r['snippet']}"
                for r in search_result["results"]
            )
            answer = llm_module.chat(
                prompt=f"Based on these search results, answer: {query}",
                context=context,
            )
            sources = "\n".join(
                f"- [{r['title']}]({r['url']})"
                for r in search_result["results"]
            )
            return f"{answer}\n\n---\n**Sources:**\n{sources}"
    except Exception as e:
        logger.warning(f"LLM summarization failed: {e}")

    # Fallback: return raw results
    return search_result["summary"]
