# FILE: runtime_utils.py
"""
Unified Runtime Utilities (v10_9) — FULL AGENTIC IMPLEMENTATION

This module consolidates ALL deterministic utility functions needed by
the v10_9 agentic runtime:

SECTIONS:
    1. Constants
    2. Exceptions
    3. Telemetry
    4. Optimization (cost + span tracking)
    5. Retrieval utilities
    6. Ranking utilities
    7. RAGUtils (evidence normalization + fusion)

Pure utilities:
    • NO cognition (L1)
    • NO execution (L2)
    • NO orchestration (L3)
    • NO state mutation (L4)
    • NO policy (L5)
"""

from __future__ import annotations

import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================================
# 1. CONSTANTS
# ============================================================================

class Constants:

    class WorkflowPhase:
        INIT       = "init"
        PLANNING   = "planning"
        EXECUTING  = "executing"
        REVIEWING  = "reviewing"
        COMPLETE   = "complete"
        FAILED     = "failed"

    class NodeStatus:
        SUCCESS = "success"
        FAILURE = "failure"
        PENDING = "pending"

    # Default canonical model
    CANONICAL_MODEL_DEFAULT = "gpt-4.1"


# ============================================================================
# 2. EXCEPTIONS  (lightweight, runtime-safe)
# ============================================================================

class ValidationError(Exception):
    """Malformed state, plan, or configuration."""

class ToolExecutionError(Exception):
    """Execution error during L2 stage."""

class ModelClientError(Exception):
    """Model provider call failed."""

class SafetyException(Exception):
    """Safety constraint violation."""

class WorkflowTimeoutError(Exception):
    """Async workflow exceeded time budget."""


# ============================================================================
# 3. TELEMETRY  (optional, deterministic)
# ============================================================================

@dataclass
class MetricEvent:
    name: str
    value: float
    tags: Dict[str, Any]

@dataclass
class SpanEvent:
    name: str
    start_time_ms: float
    end_time_ms: float
    tags: Dict[str, Any]

@dataclass
class TraceContext:
    trace_id: str
    spans: Dict[str, SpanEvent]

_TELEMETRY_EVENTS: List[Dict[str, Any]] = []

def record_event(name: str, payload: Dict[str, Any]) -> None:
    _TELEMETRY_EVENTS.append({
        "name": name,
        "timestamp": time.time(),
        "payload": payload,
    })

def get_events() -> List[Dict[str, Any]]:
    return list(_TELEMETRY_EVENTS)


# ============================================================================
# 4. OPTIMIZATION  (cost tracking + deterministic hints)
# ============================================================================

@dataclass
class CostTracker:
    spans: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def start_span(self, name: str) -> None:
        self.spans[name] = {"start": time.perf_counter(), "end": None}

    def end_span(self, name: str) -> None:
        if name in self.spans and self.spans[name]["end"] is None:
            self.spans[name]["end"] = time.perf_counter()

    def snapshot(self) -> Dict[str, Any]:
        out = []
        for n, s in sorted(self.spans.items()):
            start = s["start"]
            end = s["end"] or start
            dur = max(0.0, (end - start) * 1000)
            out.append({"name": n, "duration_ms": dur})
        return {"spans": out}


def compute_optimization_hint(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic optimization hint based on planning/execution time.
    """
    planning = next((s for s in spans if s.get("name") == "planning"), {"duration_ms": 0})
    execution = next((s for s in spans if s.get("name") == "execution"), {"duration_ms": 0})

    if float(planning["duration_ms"]) > float(execution["duration_ms"]):
        return {"suggestion": "reroute_fast"}
    return {"suggestion": "normal"}


# ============================================================================
# 5. RETRIEVAL UTILITIES
# ============================================================================

class Retrieval:

    @staticmethod
    def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize retrieval items into canonical:
            {query: str, evidence: str, rank: int}
        """
        out = []
        for r in results:
            out.append({
                "query": str(r.get("query", "")),
                "evidence": str(r.get("evidence", "")),
                "rank": int(r.get("rank", 0)),
            })
        return out

    @staticmethod
    def dedupe_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate (query, evidence) pairs.
        """
        seen = set()
        out = []
        for it in items:
            key = (it.get("query", ""), it.get("evidence", ""))
            if key not in seen:
                seen.add(key)
                out.append(it)
        return out

    @staticmethod
    def rerank_results(items: List[Dict[str, Any]], strategy: str) -> List[Dict[str, Any]]:
        """
        Optional post-ranking shuffle based on strategy.
        """
        if not items:
            return items
        if strategy == "hybrid":
            return sorted(items, key=lambda x: x.get("rank", 0))
        return items

    @staticmethod
    def fuse_results(lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Merge multiple retrieval lists.
        """
        merged = []
        for lst in lists:
            for item in lst:
                merged.append(dict(item))
        return sorted(merged, key=lambda x: (x.get("query", ""), x.get("rank", 0)))


# ============================================================================
# 6. RANKING UTILITIES (BM25, dense, hybrid)
# ============================================================================

class Ranking:

    @staticmethod
    def _score_dense(text: str) -> int:
        digest = hashlib.sha256(text.encode()).hexdigest()
        return int(digest, 16) % 100

    @staticmethod
    def bm25_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Heuristic BM25-like ranking based on evidence length.
        """
        scored = []
        for it in items:
            score = len(str(it.get("evidence", "")))
            scored.append({**it, "score": score})
        return sorted(scored, key=lambda x: -x["score"])

    @staticmethod
    def dense_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Heuristic dense ranking based on SHA hash entropy.
        """
        scored = []
        for it in items:
            score = Ranking._score_dense(str(it.get("query", "")))
            scored.append({**it, "score": score})
        return sorted(scored, key=lambda x: -x["score"])

    @staticmethod
    def hybrid_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hybrid = (dense + BM25)/2.
        """
        scored = []
        for it in items:
            bm = len(str(it.get("evidence", "")))
            dn = Ranking._score_dense(str(it.get("query", "")))
            score = (bm + dn) / 2
            scored.append({**it, "score": score})
        return sorted(scored, key=lambda x: -x["score"])


# ============================================================================
# 7. RAG UTILS (Normalization, Metadata, Fusion)
# ============================================================================

class RAGUtils:

    @staticmethod
    def normalize_evidence(evidence: Any) -> str:
        return "" if evidence is None else str(evidence).strip()

    @staticmethod
    def extract_snippet(evidence: str, max_len: int = 350) -> str:
        return evidence[:max_len].rstrip() if evidence else ""

    @staticmethod
    def build_metadata(query: str, evidence: str, rank: int) -> Dict[str, Any]:
        snippet = RAGUtils.extract_snippet(evidence)
        return {
            "query": query,
            "rank": rank,
            "snippet": snippet,
            "evidence_length": len(evidence),
        }

    @staticmethod
    def normalize_rag_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for it in items:
            q = str(it.get("query", ""))
            ev = RAGUtils.normalize_evidence(it.get("evidence"))
            r = int(it.get("rank", 0))
            out.append({
                "query": q,
                "evidence": ev,
                "rank": r,
                "metadata": RAGUtils.build_metadata(q, ev, r),
            })
        return out

    @staticmethod
    def fuse_multi_query_results(sources: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        merged = []
        for lst in sources:
            merged.extend(lst)

        deduped = {}
        for item in merged:
            key = (item.get("query", "").lower(), item.get("evidence", "").lower())
            if key not in deduped:
                deduped[key] = item

        items = list(deduped.values())

        # Assign fusion scores
        for it in items:
            it["_fusion_score"] = (
                (100 - it.get("rank", 0)) +
                0.1 * len(str(it.get("evidence", "")))
            )

        # Sort by fusion score descending
        items.sort(key=lambda x: -x["_fusion_score"])

        # Reassign ranks deterministically
        for idx, it in enumerate(items):
            it["rank"] = idx + 1
            del it["_fusion_score"]

        return items
