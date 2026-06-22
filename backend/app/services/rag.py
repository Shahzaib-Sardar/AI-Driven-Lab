from __future__ import annotations

import json
import logging
import math
import os
from pathlib import Path
from typing import Any, Dict, List
from urllib import request as urlrequest, error as urlerror

LOG = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_FILE = DATA_DIR / "knowledge_docs.json"
STORE_FILE = DATA_DIR / "rag_store.json"

EMBEDDING_MODEL = "text-embedding-3-small"


def _load_knowledge_docs() -> List[Dict[str, Any]]:
    if not KNOWLEDGE_FILE.exists():
        # create a small default knowledge base
        docs = [
            {
                "id": "tips-1",
                "title": "Budgeting Basics",
                "text": "Set a monthly budget, track expenses weekly, and keep 3-6 months of expenses in an emergency fund. Prioritize high-interest debt for repayment.",
                "source": "built-in"
            },
            {
                "id": "tips-2",
                "title": "Saving on Food",
                "text": "Plan meals, buy in bulk, reduce takeout to save on food. Use a shopping list to avoid impulse buys.",
                "source": "built-in"
            },
            {
                "id": "tips-3",
                "title": "Transport Savings",
                "text": "Combine errands, use public transport or a bike where possible, and review subscriptions for car services you no longer use.",
                "source": "built-in"
            },
        ]
        KNOWLEDGE_FILE.write_text(json.dumps(docs, indent=2, ensure_ascii=False), encoding="utf-8")
        return docs

    try:
        return json.loads(KNOWLEDGE_FILE.read_text(encoding="utf-8"))
    except Exception:
        LOG.exception("Failed to read knowledge docs; returning empty list")
        return []


def _chunk_text(text: str, max_chars: int = 500) -> List[str]:
    text = text.strip()
    if not text:
        return []
    chunks: List[str] = []
    while text:
        chunk = text[:max_chars]
        # try to cut at sentence boundary
        last_period = chunk.rfind('. ')
        if last_period != -1 and last_period > max_chars // 2:
            chunk = chunk[: last_period + 1]
        chunks.append(chunk.strip())
        text = text[len(chunk):].strip()
    return chunks


def _embed_text_openai(text: str) -> List[float] | None:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    endpoint = "https://api.openai.com/v1/embeddings"
    payload = json.dumps({"model": EMBEDDING_MODEL, "input": text}).encode("utf-8")
    req = urlrequest.Request(
        endpoint,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=15) as resp:
            resp_payload = json.loads(resp.read().decode("utf-8"))
            return resp_payload["data"][0]["embedding"]
    except (urlerror.URLError, TimeoutError, KeyError, IndexError, ValueError, OSError):
        LOG.exception("Embedding request failed")
        return None


def _pseudo_embedding(text: str, dim: int = 1536) -> List[float]:
    # deterministic lightweight fallback embedding when no API key is available
    # maps characters to a small vector using unicode codes
    vec = [0.0] * 128
    for i, ch in enumerate(text[:1000]):
        vec[i % 128] += (ord(ch) % 31) / 31.0
    # pad/trim to a reasonable size
    return [float(x) for x in (vec * ((dim // 128) + 1))[:dim]]


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return -1.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return -1.0
    return dot / (norm_a * norm_b)


def build_store(force: bool = False) -> None:
    """Build the RAG store from knowledge docs. Skips if store exists unless force=True."""
    if STORE_FILE.exists() and not force:
        LOG.info("RAG store already exists; skipping build")
        return

    docs = _load_knowledge_docs()
    entries: List[Dict[str, Any]] = []
    for doc in docs:
        chunks = _chunk_text(doc.get("text", ""), max_chars=500)
        for idx, chunk in enumerate(chunks):
            emb = _embed_text_openai(chunk)
            if emb is None:
                emb = _pseudo_embedding(chunk)
            entry = {
                "id": f"{doc.get('id')}-chunk-{idx}",
                "doc_id": doc.get("id"),
                "title": doc.get("title"),
                "text": chunk,
                "embedding": emb,
                "metadata": {"source": doc.get("source", "built-in")},
            }
            entries.append(entry)
    try:
        STORE_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
        LOG.info("RAG store built with %d chunks", len(entries))
    except Exception:
        LOG.exception("Failed to write RAG store")


def _load_store() -> List[Dict[str, Any]]:
    if not STORE_FILE.exists():
        build_store()
    try:
        return json.loads(STORE_FILE.read_text(encoding="utf-8"))
    except Exception:
        LOG.exception("Failed to load RAG store")
        return []


def retrieve(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve top_k chunks for the query. Returns list of {text,metadata,score,id} entries."""
    if not query or not str(query).strip():
        return []
    store = _load_store()
    emb = _embed_text_openai(query)
    if emb is None:
        emb = _pseudo_embedding(query)

    results: List[Dict[str, Any]] = []
    for item in store:
        score = _cosine(emb, item.get("embedding", []))
        results.append({"id": item.get("id"), "text": item.get("text"), "metadata": item.get("metadata", {}), "score": score, "title": item.get("title")})

    results = sorted([r for r in results if r["score"] > -0.9999], key=lambda r: r["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    # quick local build for convenience
    logging.basicConfig(level=logging.INFO)
    build_store(force=True)
    print("Built RAG store at", STORE_FILE)
