"""Fetch and ingest agent-framework documentation into ext_knowledge ChromaDB collection.

Targets:
  - Anthropic Claude agent docs  (docs.anthropic.com)
  - OpenAI Agents Python docs    (openai.github.io/openai-agents-python)

These were absent from ext_knowledge (audit 2026-04-14).
Uses BAAI/bge-m3 (1024-dim cosine) — same model as ingest_ext_knowledge.py.

Usage:
    python tools/generate/ingestion/ingest_agent_framework_docs.py [--dry-run] [--store-path PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "ext_knowledge"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 64
CHUNK_CHARS = 2000
CHUNK_OVERLAP = 200
MIN_BODY_CHARS = 80
REQUEST_TIMEOUT = 20

# All known valid URLs — ordered by priority
FETCH_URLS: list[dict] = [
    # Anthropic Claude — GitHub raw (docs.anthropic.com is a Next.js SPA; raw GitHub is the only
    # reliable plain-text source for Anthropic agent patterns)
    {
        "url": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/README.md",
        "domain": "docs.anthropic.com",
        "title": "Anthropic Cookbook README",
    },
    {
        "url": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/basic_workflows.ipynb",
        "domain": "docs.anthropic.com",
        "title": "Anthropic — Agent basic workflows",
    },
    {
        "url": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/orchestrator_workers.ipynb",
        "domain": "docs.anthropic.com",
        "title": "Anthropic — Orchestrator-workers pattern",
    },
    {
        "url": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/evaluator_optimizer.ipynb",
        "domain": "docs.anthropic.com",
        "title": "Anthropic — Evaluator-optimizer pattern",
    },
    {
        "url": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/tool_use/customer_service_agent.ipynb",
        "domain": "docs.anthropic.com",
        "title": "Anthropic — Tool use customer service agent",
    },
    # OpenAI Agents Python
    {
        "url": "https://openai.github.io/openai-agents-python/",
        "domain": "openai.github.io",
        "title": "OpenAI Agents Python — home",
    },
    {
        "url": "https://openai.github.io/openai-agents-python/agents/",
        "domain": "openai.github.io",
        "title": "OpenAI Agents Python — agents",
    },
    {
        "url": "https://openai.github.io/openai-agents-python/tools/",
        "domain": "openai.github.io",
        "title": "OpenAI Agents Python — tools",
    },
    {
        "url": "https://openai.github.io/openai-agents-python/handoffs/",
        "domain": "openai.github.io",
        "title": "OpenAI Agents Python — handoffs",
    },
    {
        "url": "https://openai.github.io/openai-agents-python/guardrails/",
        "domain": "openai.github.io",
        "title": "OpenAI Agents Python — guardrails",
    },
    {
        "url": "https://openai.github.io/openai-agents-python/tracing/",
        "domain": "openai.github.io",
        "title": "OpenAI Agents Python — tracing",
    },
    {
        "url": "https://openai.github.io/openai-agents-python/running_agents/",
        "domain": "openai.github.io",
        "title": "OpenAI Agents Python — running agents",
    },
    {
        "url": "https://openai.github.io/openai-agents-python/results/",
        "domain": "openai.github.io",
        "title": "OpenAI Agents Python — results",
    },
    # OpenAI Agents Python — GitHub raw source docs (platform.openai.com is 403-blocked)
    {
        "url": "https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md",
        "domain": "openai.com",
        "title": "OpenAI Agents Python README",
    },
    {
        "url": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/agents.md",
        "domain": "openai.com",
        "title": "OpenAI Agents Python — agents reference",
    },
    {
        "url": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/tools.md",
        "domain": "openai.com",
        "title": "OpenAI Agents Python — tools reference",
    },
    {
        "url": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/guardrails.md",
        "domain": "openai.com",
        "title": "OpenAI Agents Python — guardrails reference",
    },
    {
        "url": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/handoffs.md",
        "domain": "openai.com",
        "title": "OpenAI Agents Python — handoffs reference",
    },
    {
        "url": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/tracing.md",
        "domain": "openai.com",
        "title": "OpenAI Agents Python — tracing reference",
    },
    {
        "url": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/running_agents.md",
        "domain": "openai.com",
        "title": "OpenAI Agents Python — running agents reference",
    },
    # ext_knowledge backfill — source diversity for RETR and TOOL queries
    {
        "url": "https://raw.githubusercontent.com/chroma-core/chroma/main/README.md",
        "domain": "docs.trychroma.com",
        "title": "ChromaDB — Canonical README",
    },
    {
        "url": "https://raw.githubusercontent.com/modelcontextprotocol/specification/main/README.md",
        "domain": "modelcontextprotocol.io",
        "title": "MCP Specification — Protocol Overview",
    },
]

GARBAGE_PATTERNS = ["Loading...", "Loading..Loading.."]


def is_garbage(text: str) -> bool:
    if not text or len(text.strip()) < MIN_BODY_CHARS:
        return True
    return any(p in text for p in GARBAGE_PATTERNS)


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def make_doc_id(id_parts: tuple) -> str:
    return hashlib.sha256(":".join(id_parts).encode("utf-8")).hexdigest()[:24]


def chunk_text(text: str, chunk_size: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            boundary = text.rfind("\n\n", start, end)
            if boundary > start + chunk_size // 2:
                end = boundary
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start >= len(text):
            break
    return chunks


def fetch_url(url: str) -> str | None:
    """Fetch URL text; return None on failure."""
    try:
        import urllib.request
        import urllib.error

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; AgenticWorkflow/1.0; "
                "+https://github.com/Siamese001/Agentic-Workflow)"
            ),
            "Accept": "text/html,text/plain,*/*",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:  # noqa: S310
            raw = resp.read()
        charset = "utf-8"
        content_type = resp.headers.get("Content-Type", "")
        if "charset=" in content_type:
            charset = content_type.split("charset=")[-1].strip().split(";")[0]
        text = raw.decode(charset, errors="replace")
        return text
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"    FETCH ERROR: {exc}")
        return None


def html_to_text(html: str) -> str:
    """Very lightweight HTML -> plain text stripping."""
    import re

    # Remove scripts / styles
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    # Replace block tags with newlines
    html = re.sub(r"<(br|p|div|h[1-6]|li|tr|td|th)[^>]*>", "\n", html, flags=re.IGNORECASE)
    # Strip remaining tags
    html = re.sub(r"<[^>]+>", " ", html)
    # Decode common HTML entities
    for ent, char in [
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&quot;", '"'),
        ("&#39;", "'"),
        ("&nbsp;", " "),
    ]:
        html = html.replace(ent, char)
    # Collapse whitespace
    html = re.sub(r"\n{3,}", "\n\n", html)
    html = re.sub(r" {2,}", " ", html)
    return html.strip()


def embed_batch(model, texts: list[str]) -> list[list[float]]:
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        batch_size=32,
        show_progress_bar=False,
    ).tolist()
    return [[float(x) for x in emb] for emb in embeddings]


def validate_dim(embeddings: list[list[float]], expected: int = EMBEDDING_DIM) -> None:
    for i, emb in enumerate(embeddings):
        if len(emb) != expected:
            raise ValueError(f"Embedding[{i}] dim={len(emb)}, expected={expected}. Model mismatch.")


def run(store_path: Path, dry_run: bool = False) -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from tqdm import tqdm

    print(f"\nFetching {len(FETCH_URLS)} agent-framework doc pages ...")
    all_docs: list[dict] = []
    fetch_ok = 0
    fetch_fail = 0

    for entry in tqdm(FETCH_URLS, desc="Fetching", unit="url"):
        url = entry["url"]
        domain = entry["domain"]
        title = entry["title"]
        print(f"  -> {url}")

        raw = fetch_url(url)
        if raw is None:
            fetch_fail += 1
            continue

        # Plain text if .txt, otherwise strip HTML
        if url.endswith(".txt"):
            body = raw
        else:
            body = html_to_text(raw)

        if is_garbage(body):
            print(f"     SKIP (garbage / too short: {len(body)} chars)")
            fetch_fail += 1
            continue

        print(f"     OK ({len(body):,} chars)")
        fetch_ok += 1
        content_hash = compute_digest(body)

        for chunk_idx, chunk in enumerate(chunk_text(body)):
            all_docs.append(
                {
                    "text": chunk,
                    "metadata": {
                        "artifact_type": "ext_knowledge",
                        "doc_type": "web",
                        "domain": domain,
                        "source_url": url,
                        "document_title": title[:200],
                        "file_path": url[:200],
                        "layer": "ext",
                        "chunk_index": chunk_idx,
                        "canonical_digest": content_hash,
                        "source": "agent_framework_docs",
                    },
                    "id_parts": ("web", domain, content_hash[:16], str(chunk_idx)),
                }
            )

    print(f"\nFetch summary: {fetch_ok} OK, {fetch_fail} failed")
    print(f"Total chunks collected: {len(all_docs)}")

    if not all_docs:
        print("ERROR: No documents collected — aborting.")
        sys.exit(1)

    if dry_run:
        print("DRY RUN — not writing to Chroma.")
        return

    # Load embedding model
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        print("ERROR: sentence-transformers not installed.")
        raise SystemExit(1) from exc
    try:
        import chromadb
    except ImportError as exc:
        print("ERROR: chromadb not installed.")
        raise SystemExit(1) from exc

    print(f"\nLoading embedding model: {EMBEDDING_MODEL} ...")
    model = SentenceTransformer(EMBEDDING_MODEL, device="cuda")
    model.max_seq_length = 512
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != EMBEDDING_DIM:
        raise RuntimeError(f"Model dim mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model ready. dim={actual_dim}")

    from tools.progress_display import ProgressReporter

    # Deduplicate
    ids = [make_doc_id(tuple(d["id_parts"])) for d in all_docs]
    texts = [d["text"] for d in all_docs]
    metadatas = [d["metadata"] for d in all_docs]
    seen_ids: dict[str, int] = {}
    for i, doc_id in enumerate(ids):
        seen_ids[doc_id] = i
    dedup = sorted(seen_ids.values())
    ids = [ids[i] for i in dedup]
    texts = [texts[i] for i in dedup]
    metadatas = [metadatas[i] for i in dedup]
    print(f"After dedup: {len(ids)} unique chunks")

    print(f"Connecting to Chroma store: {store_path}")
    client = chromadb.PersistentClient(path=str(store_path))
    existing = {c.name for c in client.list_collections()}
    if COLLECTION_NAME in existing:
        collection = client.get_collection(COLLECTION_NAME)
        before_count = collection.count()
        print(f"Collection '{COLLECTION_NAME}' exists ({before_count:,} docs) — upserting.")
    else:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dim": EMBEDDING_DIM,
            },
        )
        before_count = 0
        print(f"Created collection '{COLLECTION_NAME}'")

    total = len(ids)
    reporter = ProgressReporter(total=total, label="Embedding + upserting agent_framework_docs")
    t0 = time.time()

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch_embeddings = embed_batch(model, texts[batch_start:batch_end])
        validate_dim(batch_embeddings)
        collection.upsert(
            ids=ids[batch_start:batch_end],
            embeddings=batch_embeddings,
            documents=texts[batch_start:batch_end],
            metadatas=metadatas[batch_start:batch_end],
        )
        reporter.update(batch_end - batch_start, label=f"batch {batch_end}/{total}")

    reporter.done()
    elapsed = time.time() - t0
    after_count = collection.count()
    print(f"\nDone. collection='{COLLECTION_NAME}'")
    print(f"  Before: {before_count:,} docs")
    print(f"  After:  {after_count:,} docs  (+{after_count - before_count:,})")
    print(f"  Elapsed: {elapsed:.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest agent-framework docs into ext_knowledge")
    parser.add_argument(
        "--store-path",
        type=Path,
        default=CANONICAL_STORE,
        help=f"ChromaDB persistence directory (default: {CANONICAL_STORE})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Fetch only, do not write to Chroma")
    args = parser.parse_args()
    run(store_path=args.store_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
