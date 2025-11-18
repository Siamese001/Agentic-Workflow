# FILE: runtime_utils.py
"""
Unified Runtime Utilities (v10_9) — FULL AGENTIC IMPLEMENTATION (REFINED)

This module consolidates ALL deterministic utility functions needed by
the v10_9 agentic runtime:

SECTIONS:
    1. Constants
    2. Exceptions
    3. Telemetry primitives
    4. Cost & Optimization helpers
    5. Retrieval utilities
    6. Ranking utilities
    7. RAGUtils (normalization + fusion)

Design constraints:
    • NO cognition (L1) — no planning logic.
    • NO execution (L2) — no tool/LLM calls.
    • NO orchestration (L3) — no control-flow logic.
    • NO state mutation (L4) — no state adapters.
    • NO safety/policy (L5) — no safety decisions.

Everything here is safe, deterministic, and side-effect-free except
for the in-memory telemetry buffer.
"""

from __future__ import annotations

import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Iterable


# ============================================================================
# 1. CONSTANTS
# ============================================================================


class Constants:
    """
    Lightweight constant container for runtime-wide enums and defaults.

    NOTE:
        These are intentionally string-based to avoid import cycles with
        the main models module. Higher layers may map to models.WorkflowPhase
        / NodeStatus where needed.
    """

    class WorkflowPhase:
        INIT = "init"
        PLANNING = "planning"
        EXECUTING = "executing"
        REVIEWING = "reviewing"
        COMPLETE = "complete"
        FAILED = "failed"

    class NodeStatus:
        SUCCESS = "success"
        FAILURE = "failure"
        PENDING = "pending"

    # Default canonical model used if none is specified
    CANONICAL_MODEL_DEFAULT: str = "gpt-4.1"


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


# Global in-memory telemetry store
_TELEMETRY_EVENTS: List[Dict[str, Any]] = []


def record_event(name: str, payload: Dict[str, Any]) -> None:
    """
    Append a telemetry event to the in-memory list.
    This is intentionally simple; callers are free to ship it elsewhere.
    """
    _TELEMETRY_EVENTS.append(
        {
            "name": name,
            "timestamp": time.time(),
            "payload": payload,
        }
    )


def get_events() -> List[Dict[str, Any]]:
    """
    Return a shallow copy of the telemetry events list.
    """
    return list(_TELEMETRY_EVENTS)


# ============================================================================
# 4. COST & OPTIMIZATION  (span tracking + deterministic hints)
# ============================================================================


@dataclass
class CostTracker:
    """
    Minimal span-based timing helper used by orchestration layers.

    Usage:
        ct = CostTracker()
        ct.start_span("planning")
        ...
        ct.end_span("planning")
        snapshot = ct.snapshot()
    """

    spans: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def start_span(self, name: str) -> None:
        """
        Start a span with the given name. Overwrites any existing start time.
        """
        self.spans[name] = {"start": time.perf_counter(), "end": None}

    def end_span(self, name: str) -> None:
        """
        End a span with the given name if it has not already been ended.
        """
        if name in self.spans and self.spans[name]["end"] is None:
            self.spans[name]["end"] = time.perf_counter()

    def snapshot(self) -> Dict[str, Any]:
        """
        Return a deterministic snapshot of spans as a list of
        {"name": ..., "duration_ms": ...} entries.
        """
        out: List[Dict[str, Any]] = []
        for n, s in sorted(self.spans.items()):
            start = s.get("start") or 0.0
            end = s.get("end") or start
            dur_ms = max(0.0, (end - start) * 1000.0)
            out.append({"name": n, "duration_ms": dur_ms})
        return {"spans": out}


def compute_optimization_hint(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Deterministic optimization hint based on planning/execution durations.

    Logic:
        • If planning > execution → suggest "reroute_fast"
        • Else → suggest "normal"

    This is intentionally simple and only used as a hint; higher layers
    decide what to do (e.g., adjust routing, change model).
    """
    planning = next((s for s in spans if s.get("name") == "planning"), {"duration_ms": 0})
    execution = next((s for s in spans if s.get("name") == "execution"), {"duration_ms": 0})

    p_ms = float(planning.get("duration_ms", 0) or 0.0)
    e_ms = float(execution.get("duration_ms", 0) or 0.0)

    if p_ms > e_ms:
        return {"suggestion": "reroute_fast"}
    return {"suggestion": "normal"}


class Optimization:
    """
    Small wrapper class for optimization helpers, to provide a clear
    namespace when imported elsewhere (e.g., L2).

    Example:
        hint = Optimization.compute_hint(cost_tracker.snapshot()["spans"])
    """

    @staticmethod
    def compute_hint(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        return compute_optimization_hint(spans)


# ============================================================================
# 5. RETRIEVAL UTILITIES
# ============================================================================


class Retrieval:
    """
    Deterministic, side-effect-free utilities for operating on retrieval
    results. These are used by RAG executors and RAG planners.
    """

    @staticmethod
    def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize retrieval items into canonical:
            {query: str, evidence: str, rank: int}

        Any missing keys are defaulted to safe values.
        """
        out: List[Dict[str, Any]] = []
        for r in results or []:
            out.append(
                {
                    "query": str(r.get("query", "")),
                    "evidence": str(r.get("evidence", "")),
                    "rank": int(r.get("rank", 0) or 0),
                }
            )
        return out

    @staticmethod
    def dedupe_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate (query, evidence) pairs while preserving first occurrence.
        """
        seen = set()
        out: List[Dict[str, Any]] = []
        for it in items or []:
            key = (it.get("query", ""), it.get("evidence", ""))
            if key not in seen:
                seen.add(key)
                out.append(it)
        return out

    @staticmethod
    def rerank_results(items: List[Dict[str, Any]], strategy: str) -> List[Dict[str, Any]]:
        """
        Optional post-ranking pass based on a strategy name.

        For now, this is a no-op for most strategies; for "hybrid" we
        sort by rank ascending for stability.
        """
        if not items:
            return items
        if strategy == "hybrid":
            return sorted(items, key=lambda x: x.get("rank", 0))
        return items

    @staticmethod
    def fuse_results(lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Merge multiple retrieval lists into a single normalized list,
        preserving deterministic ordering (by query, then rank).
        """
        merged: List[Dict[str, Any]] = []
        for lst in lists or []:
            for item in lst or []:
                merged.append(dict(item))
        return sorted(merged, key=lambda x: (x.get("query", ""), x.get("rank", 0)))


# ============================================================================
# 6. RANKING UTILITIES (BM25, dense, hybrid)
# ============================================================================


class Ranking:
    """
    Heuristic ranking utilities used by RAG executors.

    These are deliberately lightweight and deterministic; they DO NOT
    call any external services or libraries.
    """

    @staticmethod
    def _score_dense(text: str) -> int:
        """
        Compute a pseudo-dense score via SHA-256 hash.

        This is not a real embedding, but it gives a stable pseudo-random
        ordering for comparison and testing.
        """
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return int(digest, 16) % 100

    @staticmethod
    def bm25_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Heuristic BM25-like ranking based on evidence length.
        """
        scored: List[Dict[str, Any]] = []
        for it in items or []:
            evidence = str(it.get("evidence", ""))
            score = len(evidence)
            scored.append({**it, "score": score})
        scored.sort(key=lambda x: -x["score"])
        return scored

    @staticmethod
    def dense_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Heuristic dense ranking based on SHA hash entropy.

        The idea is to produce a stable numeric score per query.
        """
        scored: List[Dict[str, Any]] = []
        for it in items or []:
            query = str(it.get("query", ""))
            score = Ranking._score_dense(query)
            scored.append({**it, "score": score})
        scored.sort(key=lambda x: -x["score"])
        return scored

    @staticmethod
    def hybrid_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hybrid = (dense + BM25) / 2.

        Combines heuristic BM25 (evidence-length) and dense scores.
        """
        scored: List[Dict[str, Any]] = []
        for it in items or []:
            evidence = str(it.get("evidence", ""))
            query = str(it.get("query", ""))
            bm = len(evidence)
            dn = Ranking._score_dense(query)
            score = (bm + dn) / 2.0
            scored.append(
                {
                    **it,
                    "bm25_score": bm,
                    "dense_score": dn,
                    "hybrid_score": score,
                    "score": score,
                }
            )
        scored.sort(key=lambda x: -x["score"])
        return scored


# ============================================================================
# 7. RAG UTILS (Normalization, Metadata, Fusion)
# ============================================================================


class RAGUtils:
    """
    Additional utility helpers for RAG post-processing.

    These are layered on top of Retrieval + Ranking to support
    richer metadata and multi-query fusion.
    """

    @staticmethod
    def normalize_evidence(evidence: Any) -> str:
        """
        Normalize evidence into a clean string.
        """
        if evidence is None:
            return ""
        return str(evidence).strip()

    @staticmethod
    def extract_snippet(evidence: str, max_len: int = 350) -> str:
        """
        Extract a tail-trimmed snippet of evidence for preview.

        We keep the first max_len characters and strip trailing whitespace.
        """
        if not evidence:
            return ""
        return evidence[:max_len].rstrip()

    @staticmethod
    def build_metadata(query: str, evidence: str, rank: int) -> Dict[str, Any]:
        """
        Build deterministic metadata for a (query, evidence, rank) triple.
        """
        snippet = RAGUtils.extract_snippet(evidence)
        return {
            "query": query,
            "rank": rank,
            "snippet": snippet,
            "evidence_length": len(evidence),
        }

    @staticmethod
    def normalize_rag_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize a list of RAG items into the canonical structure:
            {
                "query": str,
                "evidence": str,
                "rank": int,
                "metadata": {...}
            }
        """
        out: List[Dict[str, Any]] = []
        for it in items or []:
            q = str(it.get("query", ""))
            ev = RAGUtils.normalize_evidence(it.get("evidence"))
            r = int(it.get("rank", 0) or 0)
            out.append(
                {
                    "query": q,
                    "evidence": ev,
                    "rank": r,
                    "metadata": RAGUtils.build_metadata(q, ev, r),
                }
            )
        return out

    @staticmethod
    def fuse_multi_query_results(sources: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Fuse results from multiple queries into a single, deduplicated,
        ranked list.

        Steps:
            1. Flatten all sources.
            2. Deduplicate by (query.lower(), evidence.lower()).
            3. Assign a fusion score reflecting both rank and evidence length.
            4. Sort by fusion score descending.
            5. Reassign ranks deterministically.
        """
        merged: List[Dict[str, Any]] = []
        for lst in sources or []:
            if not lst:
                continue
            merged.extend(lst)

        # Deduplicate
        deduped: Dict[tuple, Dict[str, Any]] = {}
        for item in merged:
            key = (
                str(item.get("query", "")).lower(),
                str(item.get("evidence", "")).lower(),
            )
            if key not in deduped:
                deduped[key] = dict(item)

        items = list(deduped.values())

        # Assign fusion scores
        for it in items:
            base_rank = int(it.get("rank", 0) or 0)
            ev = str(it.get("evidence", ""))
            # Higher score if lower rank and longer evidence
            it["_fusion_score"] = (100 - base_rank) + 0.1 * len(ev)

        # Sort by fusion score descending
        items.sort(key=lambda x: -x.get("_fusion_score", 0.0))

        # Reassign ranks and drop fusion_score
        for idx, it in enumerate(items):
            it["rank"] = idx + 1
            if "_fusion_score" in it:
                del it["_fusion_score"]

        return items
