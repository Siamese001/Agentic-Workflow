# FILE: v10_9_clean/shared/rag_normalization.py
"""
RAG Normalization Utilities (v10_9)

Centralizes evidence cleaning, snippet extraction, metadata shaping,
and deterministic normalization logic derived from 10_7 behavior.

Used by RAG execution (L2) and RAG state integration (L4).
"""

from __future__ import annotations
from typing import Any, Dict, List


def normalize_evidence(evidence: Any) -> str:
    """Convert evidence into a clean, deterministic string."""
    if evidence is None:
        return ""
    if isinstance(evidence, str):
        return evidence.strip()
    return str(evidence).strip()


def extract_snippet(evidence: str, max_len: int = 350) -> str:
    """Extract a safe display snippet from evidence."""
    if not evidence:
        return ""
    snippet = evidence[:max_len].rstrip()
    return snippet


def build_metadata(
    query: str,
    evidence: str,
    rank: int,
) -> Dict[str, Any]:
    """Construct deterministic metadata block for a retrieval item."""
    snippet = extract_snippet(evidence)
    return {
        "query": query,
        "rank": rank,
        "snippet": snippet,
        "evidence_length": len(evidence),
    }


def normalize_rag_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert raw RAG results into canonical structures:

    Input format (flexible):
        {"query": str, "evidence": Any, "rank": int}

    Output format (strict):
        {"query": str, "evidence": str, "rank": int, "metadata": {...}}
    """
    out: List[Dict[str, Any]] = []

    for item in items:
        q = str(item.get("query", ""))
        ev = normalize_evidence(item.get("evidence"))
        r = int(item.get("rank", 0))

        out.append(
            {
                "query": q,
                "evidence": ev,
                "rank": r,
                "metadata": build_metadata(q, ev, r),
            }
        )

    return out
