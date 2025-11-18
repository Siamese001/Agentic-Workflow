# FILE: v10_9_clean/l4/rag_state_adapter.py
"""
L4 — RAG State Adapter (v10_9)

Helpers to integrate RAG execution outputs into the orchestration state in a
deterministic, L4-safe way (no planning, no execution — just state shaping).
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List

from shared.rag_normalization import normalize_rag_results


def attach_rag_result(
    state: Dict[str, Any],
    rag_payload: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Attach a single RAG execution payload into state.

    Expected rag_payload shape:
        {
            "queries": [...],
            "filters": {...},
            "ranking": {...},
            "documents": [ { "query": ..., "evidence": ..., "rank": ... }, ... ],
        }

    This function:
        • normalizes documents
        • appends to `rag_history`
        • updates `rag.results` & `rag.last_run`
    """

    new_state = copy.deepcopy(state) if isinstance(state, dict) else {}

    raw_docs: List[Dict[str, Any]] = rag_payload.get("documents") or []
    normalized_docs = normalize_rag_results(raw_docs)

    # Maintain cumulative RAG history
    history = new_state.get("rag_history")
    if not isinstance(history, list):
        history = []
    history.extend(normalized_docs)
    new_state["rag_history"] = history

    # Maintain current RAG bucket
    rag_bucket = new_state.get("rag")
    if not isinstance(rag_bucket, dict):
        rag_bucket = {}

    rag_bucket["results"] = normalized_docs
    rag_bucket["last_run"] = {
        "queries": rag_payload.get("queries", []),
        "filters": rag_payload.get("filters", {}),
        "ranking": rag_payload.get("ranking", {}),
    }

    new_state["rag"] = rag_bucket
    return new_state
