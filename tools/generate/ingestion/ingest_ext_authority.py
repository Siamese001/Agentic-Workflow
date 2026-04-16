"""Wave B2/B6 ingestion — ext_authority ChromaDB collection.

Status  : Active (Wave B6 — gap-close additions)
Replaces: web-source portions of ingest_curated_agent_docs.py (RETIRED in Wave B2)
See     : docs/requirements/wave_b_chromadb_topology.md
          docs/requirements/wave_b_metadata_contract.md

Ingest 25 vetted external web sources into the ``ext_authority`` collection.
B6 additions (7 sources) close proven blocking families F06/F08/F09/F12/F13/F14/F17/F25.

Lane A — target_state_authority / T2_standard:
    MCP Python SDK README (canonical spec source)

Lane B — supporting_guidance / T3_guidance:
    17 OpenAI Agents Python, Anthropic cookbook, LangGraph, AutoGen documents

Chunking strategy:
    Section-aware parent/child hierarchy per heading level.
    H2 sections are parents; H3 sub-sections are children.
    Large sections are char-split with overlap; code fences and tables are
    never broken mid-block.  Each chunk carries parent_id and child_ids.

Metadata contract:
    Wave B mandatory fields enforced fail-closed at validate_metadata().
    17 required fields (14 mandatory + version_or_date, parent_id, child_ids).

Fail-closed rules:
    required=True fetch failure  → raise IngestionError (abort)
    malformed metadata           → raise MetadataContractError (abort)
    garbage / too-short body     → skip silently

Usage:
    python tools/generate/ingestion/ingest_ext_authority.py [--dry-run]
    python tools/generate/ingestion/ingest_ext_authority.py [--store-path PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL_STORE = REPO_ROOT / "data" / "cache" / "chromadb"
COLLECTION_NAME = "ext_authority"
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
BATCH_SIZE = 32
CHUNK_CHARS = 2000
CHUNK_OVERLAP = 200
MIN_BODY_CHARS = 80
REQUEST_TIMEOUT = 20

# Wave B mandatory fields for ext_authority (17 total).
REQUIRED_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "source_collection",
        "source_band",
        "authority_tier",
        "normative_scope",
        "invalid_for_normative_use",
        "source_type",
        "topic_bucket",
        "doc_family",
        "source_url",
        "heading_path",
        "collapse_group",
        "title",
        "chunk_index",
        "canonical_digest",
        "version_or_date",
        "parent_id",
        "child_ids",
    }
)

_VALID_SOURCE_BANDS: frozenset[str] = frozenset({"target_state_authority", "supporting_guidance"})
_VALID_AUTHORITY_TIERS: frozenset[str] = frozenset({"T2_standard", "T3_guidance"})

# URLs that map to Lane A (target_state_authority / T2_standard).
_LANE_A_URLS: frozenset[str] = frozenset(
    {
        "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md",
    }
)

# ── Source catalogue ──────────────────────────────────────────────────────────
# 18 vetted external web documents.  Source band is derived by _assign_source_band().

EXT_AUTHORITY_SOURCES: list[dict] = [
    # Lane A — target_state_authority (T2_standard)
    {
        "path": "https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md",
        "title": "MCP Python SDK — FastMCP Server Authoring Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "tool_contracts",
        "collapse_group": "mcp_protocol_sdk",
        "required": True,
    },
    # Lane B — supporting_guidance (T3_guidance) — OpenAI Agents Python
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/guardrails.md",
        "title": "OpenAI Agents Python — Guardrails Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "safety_eval",
        "collapse_group": "openai_agents_raw_github",
        "required": True,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/agents.md",
        "title": "OpenAI Agents Python — Agents Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "openai_agents_raw_github",
        "required": True,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/tools.md",
        "title": "OpenAI Agents Python — Tools Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "tool_contracts",
        "collapse_group": "openai_agents_raw_github",
        "required": True,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/README.md",
        "title": "OpenAI Agents Python README",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "openai_agents_raw_github",
        "required": True,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/handoffs.md",
        "title": "OpenAI Agents Python — Handoffs Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "openai_agents_raw_github",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/running_agents.md",
        "title": "OpenAI Agents Python — Running Agents Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "openai_agents_raw_github",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/tracing.md",
        "title": "OpenAI Agents Python — Tracing Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "observability",
        "collapse_group": "openai_agents_raw_github",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/mcp.md",
        "title": "OpenAI Agents Python — MCP Integration Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "tool_contracts",
        "collapse_group": "openai_agents_raw_github",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/context.md",
        "title": "OpenAI Agents Python — Context Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "openai_agents_raw_github",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/results.md",
        "title": "OpenAI Agents Python — Results Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "openai_agents_raw_github",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/openai/openai-agents-python/main/docs/models.md",
        "title": "OpenAI Agents Python — Models Reference",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "openai_agents_raw_github",
        "required": False,
    },
    # Anthropic cookbook patterns
    {
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/evaluator_optimizer.ipynb",
        "title": "Anthropic — Evaluator-Optimizer Pattern",
        "doc_type": "notebook",
        "doc_family": "guide",
        "topic_bucket": "safety_eval",
        "collapse_group": "anthropic_agent_patterns",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/orchestrator_workers.ipynb",
        "title": "Anthropic — Orchestrator-Workers Pattern",
        "doc_type": "notebook",
        "doc_family": "guide",
        "topic_bucket": "orchestration",
        "collapse_group": "anthropic_agent_patterns",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/basic_workflows.ipynb",
        "title": "Anthropic — Agent Basic Workflows",
        "doc_type": "notebook",
        "doc_family": "guide",
        "topic_bucket": "orchestration",
        "collapse_group": "anthropic_agent_patterns",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/subagent.ipynb",
        "title": "Anthropic — Sub-agent Delegation Pattern",
        "doc_type": "notebook",
        "doc_family": "guide",
        "topic_bucket": "orchestration",
        "collapse_group": "anthropic_agent_patterns",
        "required": False,
    },
    # Multi-agent framework diversity
    {
        "path": "https://raw.githubusercontent.com/langchain-ai/langgraph/main/README.md",
        "title": "LangGraph — Multi-Agent Graph Orchestration",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "langgraph",
        "required": False,
    },
    {
        "path": "https://raw.githubusercontent.com/microsoft/autogen/main/README.md",
        "title": "AutoGen — Microsoft Multi-Agent Framework",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "autogen",
        "required": False,
    },
    # ── B6 gap-close additions (P1–P8) ─────────────────────────────────────────
    # P1 — Deterministic exact-response caching / policy-key short-circuit (F08)
    {
        "path": "https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/misc/prompt_caching.ipynb",
        "title": "Anthropic — Prompt Caching: Exact API-Level Response Caching with Cache Control",
        "doc_type": "notebook",
        "doc_family": "guide",
        "topic_bucket": "retrieval_cache",
        "collapse_group": "langchain_caching",
        "required": False,
    },
    # P2 — Semantic / vector-similarity query caching (F09)
    {
        "path": "https://raw.githubusercontent.com/zilliztech/GPTCache/main/README.md",
        "title": "GPTCache — Semantic Caching Library for LLM Applications",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "retrieval_cache",
        "collapse_group": "gptcache",
        "required": False,
    },
    # P3 — Hybrid dense+sparse retrieval with BM25 score fusion (F12)
    {
        "path": "https://raw.githubusercontent.com/deepset-ai/haystack/main/README.md",
        "title": "Haystack — BM25 and Dense Hybrid Retrieval Pipeline with Score Fusion",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "retrieval_rag",
        "collapse_group": "haystack",
        "required": False,
    },
    # P4 — Cross-encoder reranking pipeline + P7 embedding model selection (F12, F13)
    {
        "path": "https://raw.githubusercontent.com/UKPLab/sentence-transformers/master/README.md",
        "title": "Sentence Transformers — Embedding Models and Cross-Encoder Reranking",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "retrieval_rag",
        "collapse_group": "sentence_transformers",
        "required": False,
    },
    # P5 — Parent-child document / chunk expansion retrieval (F12)
    {
        "path": "https://raw.githubusercontent.com/run-llama/llama_index/main/README.md",
        "title": "LlamaIndex — Hierarchical Node Parser and Parent-Child Chunk Retrieval",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "retrieval_rag",
        "collapse_group": "llamaindex",
        "required": False,
    },
    # P6 — Abstain / refine / graceful fallback guidance (F06, F14, F17)
    {
        "path": "https://raw.githubusercontent.com/openai/openai-cookbook/main/articles/techniques_to_improve_reliability.md",
        "title": "OpenAI Cookbook — Techniques to Improve LLM Reliability and Graceful Abstain",
        "doc_type": "markdown",
        "doc_family": "guide",
        "topic_bucket": "safety_eval",
        "collapse_group": "openai_cookbook",
        "required": False,
    },
    # P8 — Tiered healing / remediation / escalation patterns for agentic systems (F25)
    {
        "path": "https://raw.githubusercontent.com/openai/swarm/main/README.md",
        "title": "OpenAI Swarm — Agent Handoff Routing, Error Recovery and Escalation Patterns",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "openai_swarm",
        "required": False,
    },
    # ── B6.1 gap-close additions (P9–P12) ──────────────────────────────────────
    # P9 — Dedicated hybrid BM25+dense retrieval tutorial with score fusion (F12)
    {
        "path": "https://raw.githubusercontent.com/weaviate/weaviate/main/README.md",
        "title": "Weaviate — Hybrid BM25 and Dense Vector Search with Fusion Ranking",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "retrieval_rag",
        "collapse_group": "weaviate",
        "required": False,
    },
    # P10 — Retrieval faithfulness / evidence insufficiency evaluation framework (F14)
    {
        "path": "https://raw.githubusercontent.com/explodinggradients/ragas/main/README.md",
        "title": "RAGAS — RAG Evaluation: Faithfulness, Context Precision and Evidence Sufficiency",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "safety_eval",
        "collapse_group": "ragas",
        "required": False,
    },
    # P11 — Graceful fallback / abstain / validation failure routing in agent systems (F17)
    {
        "path": "https://raw.githubusercontent.com/guardrails-ai/guardrails/main/README.md",
        "title": "Guardrails AI — Validation Failure Routing, Fallback Values and Abstain Handling",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "safety_eval",
        "collapse_group": "guardrails_ai",
        "required": False,
    },
    # P12 — Tiered retry / escalation ladder / workflow failure recovery (F25)
    {
        "path": "https://raw.githubusercontent.com/temporalio/sdk-python/main/README.md",
        "title": "Temporal Python SDK — Retry Policies, Workflow Failure Handling and Escalation Tiers",
        "doc_type": "markdown",
        "doc_family": "reference",
        "topic_bucket": "orchestration",
        "collapse_group": "temporal",
        "required": False,
    },
]


# ── Exceptions ────────────────────────────────────────────────────────────────


class IngestionError(RuntimeError):
    """Fail-closed: required source fetch failure or config error."""


class MetadataContractError(ValueError):
    """Fail-closed: chunk metadata violates Wave B mandatory contract."""


# ── Utilities ─────────────────────────────────────────────────────────────────


def compute_digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def make_chunk_id(source_url: str, heading_path: str, chunk_index: int) -> str:
    raw = f"{source_url.rstrip('/')}::{heading_path}::{chunk_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def is_garbage(text: str) -> bool:
    if not text or len(text.strip()) < MIN_BODY_CHARS:
        return True
    return "Loading..Loading.." in text or "Loading..." in text[:30]


def fetch_url(url: str) -> str | None:
    """Return raw response body or None on failure (never raises)."""
    try:
        import urllib.request

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
        ct = resp.headers.get("Content-Type", "")
        if "charset=" in ct:
            charset = ct.split("charset=")[-1].strip().split(";")[0]
        return raw.decode(charset, errors="replace")
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"    FETCH ERROR {url}: {exc}", file=sys.stderr)
        return None


def ipynb_to_text(raw: str) -> str:
    """Extract concatenated cell source text from a Jupyter notebook JSON string."""
    try:
        nb = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw
    lines: list[str] = []
    for cell in nb.get("cells", []):
        source = cell.get("source", [])
        text = "".join(source) if isinstance(source, list) else str(source)
        if text.strip():
            lines.append(text.strip())
    return "\n\n".join(lines)


# ── Chunking ──────────────────────────────────────────────────────────────────


def _find_protected_regions(text: str) -> list[tuple[int, int]]:
    """Return (start, end) char ranges for code fences and table blocks — must not be split."""
    regions: list[tuple[int, int]] = []
    pos = 0
    lines = text.splitlines(keepends=True)
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]
            region_start = pos
            pos += len(line)
            i += 1
            while i < len(lines):
                s = lines[i].strip()
                pos += len(lines[i])
                i += 1
                if s == fence or (s.startswith(fence) and len(s) == len(fence)):
                    break
            regions.append((region_start, pos))
            continue
        if stripped.startswith("|") or stripped.startswith("|-"):
            region_start = pos
            while i < len(lines) and (lines[i].strip().startswith("|") or lines[i].strip().startswith("|-")):
                pos += len(lines[i])
                i += 1
            regions.append((region_start, pos))
            continue
        pos += len(line)
        i += 1
    return regions


def _split_protected(
    text: str,
    max_chars: int = CHUNK_CHARS,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Char-split text without breaking code fences or table rows."""
    if len(text) <= max_chars:
        return [text] if text.strip() else []
    protected = _find_protected_regions(text)

    def _in_protected(p: int) -> bool:
        return any(s <= p < e for s, e in protected)

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        if end >= len(text):
            tail = text[start:].strip()
            if tail:
                chunks.append(tail)
            break
        half = start + (end - start) // 2
        split_at = -1
        para = text.rfind("\n\n", half, end)
        if para != -1 and not _in_protected(para):
            split_at = para + 2
        if split_at == -1:
            nl = text.rfind("\n", half, end)
            if nl != -1 and not _in_protected(nl):
                split_at = nl + 1
        if split_at == -1:
            for p in range(end, max(start, end - 100), -1):
                if not _in_protected(p):
                    split_at = p
                    break
        if split_at == -1 or split_at <= start:
            split_at = end
        chunk = text[start:split_at].strip()
        if chunk:
            chunks.append(chunk)
        next_start = split_at - overlap
        start = next_start if next_start > start else split_at
    return [c for c in chunks if c.strip()]


def chunk_with_hierarchy(
    text: str,
    source_url: str,
    max_chars: int = CHUNK_CHARS,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict]:
    """Section-aware chunking with deterministic parent/child IDs.

    Returns list of dicts::

        {heading_path, text, chunk_index, parent_id, child_ids (JSON str), doc_id}

    Algorithm:
        1. Parse H1-H3 headings into section tree.
        2. Each section is char-split (code fences + tables protected).
        3. H2 (or H1) sections are parents; H3 sub-sections are children.
        4. First sub-chunk of each H2 carries child_ids pointing to first H3 sub-chunks.
        5. H3 sub-chunks carry parent_id pointing to their H2 parent.
        6. Continuation sub-chunks (local_idx > 0) have empty parent_id and child_ids=[].
    """
    heading_re = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
    matches = list(heading_re.finditer(text))

    if not matches:
        flat = _split_protected(text, max_chars, overlap)
        return [
            {
                "heading_path": "no-headings",
                "text": body,
                "chunk_index": i,
                "parent_id": "",
                "child_ids": "[]",
                "doc_id": make_chunk_id(source_url, "no-headings", i),
            }
            for i, body in enumerate(flat)
        ]

    boundaries: list[tuple[int, int, str]] = [
        (m.start(), len(m.group(1)), m.group(2).strip()) for m in matches
    ]
    boundaries.append((len(text), 0, ""))

    stack: list[str] = ["", "", ""]
    sections: list[dict] = []
    for i, (pos, level, title) in enumerate(boundaries[:-1]):
        if level == 0:
            continue
        next_pos = boundaries[i + 1][0]
        if level == 1:
            stack = [title, "", ""]
        elif level == 2:
            stack[1] = title
            stack[2] = ""
        elif level == 3:
            stack[2] = title
        heading_path = " > ".join(h for h in stack if h)
        h2_path = " > ".join(h for h in stack[:2] if h)
        body = text[pos:next_pos].strip()
        if len(body) < MIN_BODY_CHARS:
            continue
        sections.append({"level": level, "heading_path": heading_path, "h2_path": h2_path, "body": body})

    if not sections:
        flat = _split_protected(text, max_chars, overlap)
        return [
            {
                "heading_path": "no-headings",
                "text": body,
                "chunk_index": i,
                "parent_id": "",
                "child_ids": "[]",
                "doc_id": make_chunk_id(source_url, "no-headings", i),
            }
            for i, body in enumerate(flat)
        ]

    global_idx = 0
    expanded: list[dict] = []
    for sec in sections:
        sub_chunks = _split_protected(sec["body"], max_chars, overlap)
        for local_i, sub in enumerate(sub_chunks):
            doc_id = make_chunk_id(source_url, sec["heading_path"], global_idx)
            expanded.append(
                {
                    "level": sec["level"],
                    "heading_path": sec["heading_path"],
                    "h2_path": sec["h2_path"],
                    "text": sub,
                    "local_idx": local_i,
                    "chunk_index": global_idx,
                    "doc_id": doc_id,
                    "parent_id": "",
                    "child_ids": "[]",
                }
            )
            global_idx += 1

    if not expanded:
        return []

    h2_parents: dict[str, dict] = {}
    h3_firsts: dict[str, list[dict]] = {}

    for rec in expanded:
        h2_path = rec["h2_path"]
        if rec["level"] <= 2 and rec["local_idx"] == 0 and h2_path not in h2_parents:
            h2_parents[h2_path] = rec
        elif rec["level"] == 3 and rec["local_idx"] == 0:
            h3_firsts.setdefault(h2_path, []).append(rec)

    for rec in expanded:
        h2_path = rec["h2_path"]
        if rec["level"] <= 2:
            parent_rec = h2_parents.get(h2_path)
            if parent_rec and parent_rec["doc_id"] == rec["doc_id"]:
                children = h3_firsts.get(h2_path, [])
                rec["child_ids"] = json.dumps([c["doc_id"] for c in children])
            rec["parent_id"] = ""
        elif rec["level"] == 3:
            parent_rec = h2_parents.get(h2_path)
            rec["parent_id"] = parent_rec["doc_id"] if parent_rec else ""

    return [
        {
            "heading_path": r["heading_path"],
            "text": r["text"],
            "chunk_index": r["chunk_index"],
            "parent_id": r["parent_id"],
            "child_ids": r["child_ids"],
            "doc_id": r["doc_id"],
        }
        for r in expanded
    ]


# ── Source band ───────────────────────────────────────────────────────────────


def _assign_source_band(entry: dict) -> tuple[str, str]:
    """Return (source_band, authority_tier) for an EXT_AUTHORITY_SOURCES entry."""
    if entry["path"] in _LANE_A_URLS:
        return ("target_state_authority", "T2_standard")
    return ("supporting_guidance", "T3_guidance")


# ── Metadata ──────────────────────────────────────────────────────────────────


def _build_metadata(
    entry: dict,
    chunk: dict,
    canonical_digest: str,
    doc_title: str,
) -> dict:
    source_band, authority_tier = _assign_source_band(entry)
    return {
        "source_collection": COLLECTION_NAME,
        "source_band": source_band,
        "authority_tier": authority_tier,
        "normative_scope": "external_authority",
        "invalid_for_normative_use": False,
        "source_type": "web",
        "topic_bucket": entry["topic_bucket"],
        "doc_family": entry["doc_family"],
        "source_url": entry["path"][:200],
        "heading_path": chunk["heading_path"][:200],
        "collapse_group": entry["collapse_group"],
        "title": doc_title[:200],
        "chunk_index": chunk["chunk_index"],
        "canonical_digest": canonical_digest,
        "version_or_date": "",
        "parent_id": (chunk["parent_id"] or "")[:200],
        "child_ids": chunk["child_ids"],
    }


def validate_metadata(meta: dict) -> None:
    """Raise MetadataContractError if Wave B mandatory fields are missing or type-invalid."""
    missing = REQUIRED_METADATA_KEYS - set(meta.keys())
    if missing:
        raise MetadataContractError(f"Missing mandatory Wave B fields: {sorted(missing)}")
    if not isinstance(meta["chunk_index"], int):
        raise MetadataContractError(f"chunk_index must be int, got {type(meta['chunk_index'])}")
    if not isinstance(meta["invalid_for_normative_use"], bool):
        raise MetadataContractError(
            f"invalid_for_normative_use must be bool, got {type(meta['invalid_for_normative_use'])}"
        )
    if meta["source_band"] not in _VALID_SOURCE_BANDS:
        raise MetadataContractError(f"source_band {meta['source_band']!r} not in {_VALID_SOURCE_BANDS}")
    if meta["authority_tier"] not in _VALID_AUTHORITY_TIERS:
        raise MetadataContractError(
            f"authority_tier {meta['authority_tier']!r} not in {_VALID_AUTHORITY_TIERS}"
        )


# ── Source collection ─────────────────────────────────────────────────────────


def collect_from_source(entry: dict) -> list[dict]:
    """Fetch, chunk, and validate metadata for one EXT_AUTHORITY_SOURCES entry.

    Returns list of dicts: ``{text, metadata, doc_id}``.
    Raises ``IngestionError`` when ``required=True`` and source cannot be read.
    """
    url = entry["path"]
    doc_type = entry["doc_type"]
    required = entry["required"]

    raw = fetch_url(url)
    if raw is None:
        if required:
            raise IngestionError(f"required=True fetch failure: {url}")
        return []

    body = ipynb_to_text(raw) if doc_type == "notebook" else raw

    if is_garbage(body):
        if required:
            raise IngestionError(f"required=True source returned garbage body: {url}")
        return []

    canonical_digest = compute_digest(body)
    doc_title = entry["title"]
    h1_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if h1_match:
        doc_title = h1_match.group(1).strip()[:200]

    chunks = chunk_with_hierarchy(body, url)
    if not chunks:
        if required:
            raise IngestionError(f"required=True source produced zero chunks: {url}")
        return []

    results: list[dict] = []
    for chunk in chunks:
        meta = _build_metadata(entry, chunk, canonical_digest, doc_title)
        validate_metadata(meta)
        results.append({"text": chunk["text"], "metadata": meta, "doc_id": chunk["doc_id"]})
    return results


# ── Embedding helpers ─────────────────────────────────────────────────────────


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
            raise ValueError(
                f"Embedding[{i}] dim={len(emb)}, expected={expected}. Model mismatch — aborting."
            )


# ── Run ───────────────────────────────────────────────────────────────────────


def run(store_path: Path, dry_run: bool = False) -> None:
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

    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    from tools.progress_display import ProgressReporter

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    try:
        import torch as _torch

        _device = "cuda" if _torch.cuda.is_available() else "cpu"
    except ImportError:
        _device = "cpu"
    print(f"Using device: {_device}")
    model = SentenceTransformer(EMBEDDING_MODEL, device=_device)
    model.max_seq_length = 512
    actual_dim = model.get_sentence_embedding_dimension()
    if actual_dim != EMBEDDING_DIM:
        raise RuntimeError(f"Model dim mismatch: got {actual_dim}, expected {EMBEDDING_DIM}")
    print(f"Model loaded. dim={actual_dim}")

    from tqdm import tqdm

    print(f"Collecting {len(EXT_AUTHORITY_SOURCES)} ext_authority sources ...")
    all_docs: list[dict] = []
    required_ok = 0
    required_fail = 0
    optional_fail = 0

    for entry in tqdm(EXT_AUTHORITY_SOURCES, desc="Fetching sources"):
        try:
            chunks = collect_from_source(entry)
            all_docs.extend(chunks)
            if entry["required"]:
                required_ok += 1
        except IngestionError as exc:
            print(f"  FATAL: {exc}", file=sys.stderr)
            if entry["required"]:
                required_fail += 1
                raise
            optional_fail += 1

    print(
        f"Collected: {len(all_docs)} chunks "
        f"(required_ok={required_ok} required_fail={required_fail} optional_fail={optional_fail})"
    )

    if dry_run:
        print(f"DRY RUN — stopping before Chroma write. chunks={len(all_docs)}")
        return

    print(f"Connecting to Chroma store: {store_path}")
    client = chromadb.PersistentClient(path=str(store_path))

    existing = {c.name for c in client.list_collections()}
    if COLLECTION_NAME in existing:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' exists ({collection.count()} docs) — upserting.")
    else:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine",
                "description": (
                    "Wave B: vetted external authority (Lane A target_state_authority + "
                    "Lane B supporting_guidance). Section-aware parent/child chunked."
                ),
                "embedding_model": EMBEDDING_MODEL,
                "embedding_dim": EMBEDDING_DIM,
                "wave": "B2",
            },
        )
        print(f"Created collection '{COLLECTION_NAME}'")

    ids = [d["doc_id"] for d in all_docs]
    texts = [d["text"] for d in all_docs]
    metadatas = [d["metadata"] for d in all_docs]

    seen: dict[str, int] = {}
    for i, doc_id in enumerate(ids):
        seen[doc_id] = i
    dedup = sorted(seen.values())
    ids = [ids[i] for i in dedup]
    texts = [texts[i] for i in dedup]
    metadatas = [metadatas[i] for i in dedup]
    print(f"After dedup: {len(ids)} unique chunks")

    total = len(ids)
    reporter = ProgressReporter(total=total, label=f"Embedding + upserting {COLLECTION_NAME}")
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
        reporter.update(batch_end - batch_start, label=f"Upserted batch ending at {batch_end}")

    reporter.done()
    elapsed = time.time() - t0
    print(f"\nDone. collection='{COLLECTION_NAME}' count={collection.count()} elapsed={elapsed:.1f}s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Wave B2: Ingest vetted external web sources into ext_authority"
    )
    parser.add_argument(
        "--store-path",
        type=Path,
        default=CANONICAL_STORE,
        help=f"ChromaDB persistence directory (default: {CANONICAL_STORE})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Collect without writing to Chroma")
    args = parser.parse_args()
    run(store_path=args.store_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
