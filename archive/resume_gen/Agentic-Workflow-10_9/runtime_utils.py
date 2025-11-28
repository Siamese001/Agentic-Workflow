# FILE: runtime_utils.py
"""
Unified Runtime Utilities (v10_9) — META / INFRASTRUCTURE ONLY (REFINED)

This module consolidates deterministic utility functions needed by the
v10_9 agentic runtime. It lives strictly **outside** L1–L5:

SECTIONS:
    1. Constants
    2. Exceptions
    3. Telemetry primitives
    4. Cost & Optimization helpers
    5. Retrieval utilities
    6. Ranking utilities
    7. RAGUtils (normalization + fusion)

Agentic Guardrails (must hold at 14/14 maturity):

    • NO L1 cognition — no PlanObject creation or task planning.
    • NO L2 execution — no tool/LLM/provider calls.
    • NO L3 orchestration — no DAG/phase transitions.
    • NO L4 state mutation — no StateAdapter or persistence writes.
    • NO L5 safety/policy decisions — no SafetyEngine/PolicyEngine logic.
    • NO external API/SDK calls (Anthropic/OpenAI/Gemini/etc.).

All behavior here is deterministic and side-effect free, except for the
ephemeral in-memory telemetry buffer (_TELEMETRY_EVENTS), which is
intentionally local to the process for diagnostics and meta-learning.
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
    """
    Lightweight constant container for runtime-wide enums and defaults.

    NOTE:
        These are intentionally string-based to avoid import cycles with
        the main models module. Higher layers may map to
        models.WorkflowPhase / NodeStatus where needed.
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

    # Default canonical model used if none is specified (routing-level only)
    CANONICAL_MODEL_DEFAULT: str = "gpt-4.1"


# ============================================================================
# 2. EXCEPTIONS (RUNTIME-ONLY SURFACES)
# ============================================================================


class ValidationError(Exception):
    """Malformed state, plan, or configuration (runtime-level)."""


class ToolExecutionError(Exception):
    """Execution error during L2 stage (propagated up to L3/L5)."""


class ModelClientError(Exception):
    """Model provider call failed (provider layer only)."""


class SafetyException(Exception):
    """Safety contract violation (L5 error surface)."""


class WorkflowTimeoutError(Exception):
    """Async workflow exceeded time budget (L3/L2 wrappers)."""


# ============================================================================
# 3. TELEMETRY (IN-MEMORY EVENTS)
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
    tags: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceContext:
    """Simple trace context container (optional)."""
    trace_id: str
    spans: Dict[str, SpanEvent]


# Ephemeral telemetry buffer
_TELEMETRY_EVENTS: List[Dict[str, Any]] = []


def record_event(name: str, payload: Dict[str, Any]) -> None:
    """
    Append a telemetry event to the in-memory list.

    This function must NEVER raise in normal operation.
    """
    try:
        _TELEMETRY_EVENTS.append(
            {
                "name": name,
                "timestamp": time.time(),
                "payload": dict(payload),
            }
        )
    except Exception:
        # Telemetry is best-effort only.
        pass


def get_events() -> List[Dict[str, Any]]:
    """
    Return a shallow copy of the telemetry event list.

    Intended for tests, diagnostics, or offline meta-learning.
    """
    return list(_TELEMETRY_EVENTS)


# ============================================================================
# 4. COST & OPTIMIZATION (SPAN TRACKING)
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

    The snapshot is consumed by:
        • observability.summarize_run
        • meta_profile.update_from_spans
        • runtime_utils.Optimization.compute_hint
    """

    spans: Dict[str, Dict[str, Optional[float]]] = field(default_factory=dict)

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
        Return a deterministic snapshot of spans:

            {"spans": [{"name": str, "duration_ms": float}, ...]}
        """
        out: List[Dict[str, Any]] = []
        for n in sorted(self.spans.keys()):
            s = self.spans.get(n) or {}
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
    Namespace wrapper for optimization helpers.

    Used by meta and orchestration layers to get coarse-grained hints.
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
    results. These are used by:

        • retrieval.py (RAG normalization + fusion)
        • L2.RAGExecutor (through retrieval.py)
        • meta-learning diagnostics
    """

    @staticmethod
    def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normalize retrieval items into canonical:

            {"query": str, "evidence": str, "rank": int}

        Missing keys are defaulted to safe values.
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
        Remove duplicate (query, evidence) pairs while preserving the
        first occurrence.
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
        Optional post-ranking pass based on strategy.

        Currently:
            • "hybrid" → sort by rank ascending for stability.
            • others   → no-op.
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
        sorted by (query, rank).
        """
        merged: List[Dict[str, Any]] = []
        for lst in lists or []:
            for item in lst or []:
                merged.append(dict(item))
        return sorted(merged, key=lambda x: (x.get("query", ""), x.get("rank", 0)))


# ============================================================================
# 6. RANKING UTILITIES
# ============================================================================

class Ranking:
    """
    Heuristic ranking utilities used by RAG executors.

    These are intentionally lightweight and deterministic. They DO NOT
    call external services.
    """

    @staticmethod
    def _score_dense(text: str) -> int:
        """
        Compute a pseudo-dense score via SHA-256 hash.

        Not a real embedding; stable pseudo-random ranking for tests.
        """
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return int(digest, 16) % 100000

    @staticmethod
    def bm25_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Heuristic BM25-like ranking based on evidence length.
        """
        scored: List[Dict[str, Any]] = []
        for it in items or []:
            ev = str(it.get("evidence", ""))
            score = len(ev)
            scored.append({**it, "score": score})
        scored.sort(key=lambda x: -x["score"])
        return scored

    @staticmethod
    def dense_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Heuristic dense ranking based on SHA hash of the query.
        """
        scored: List[Dict[str, Any]] = []
        for it in items or []:
            q = str(it.get("query", ""))
            score = Ranking._score_dense(q)
            scored.append({**it, "score": score})
        scored.sort(key=lambda x: -x["score"])
        return scored

    @staticmethod
    def hybrid_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Hybrid = average of (bm25_score + dense_score).

        This is a simple way of fusing lexical and pseudo-semantic signals.
        """
        scored: List[Dict[str, Any]] = []
        for it in items or []:
            ev = str(it.get("evidence", ""))
            q = str(it.get("query", ""))
            bm = len(ev)
            dn = Ranking._score_dense(q)
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
# 7. RAG UTILS (NORMALIZATION + FUSION)
# ============================================================================

class RAGUtils:
    """
    Utility helpers for RAG post-processing.

    These functions operate purely on Python data structures, adding
    additional metadata and performing multi-query fusion.
    """

    @staticmethod
    def normalize_evidence(evidence: Any) -> str:
        if evidence is None:
            return ""
        return str(evidence).strip()

    @staticmethod
    def extract_snippet(evidence: str, max_len: int = 350) -> str:
        if not evidence:
            return ""
        return evidence[:max_len].rstrip()

    @staticmethod
    def build_metadata(query: str, evidence: str, rank: int) -> Dict[str, Any]:
        """Build deterministic metadata for a query/evidence/rank triple."""
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

            {"query": str, "evidence": str, "rank": int, "metadata": {...}}
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
            3. Assign a fusion score combining rank and evidence length.
            4. Sort by fusion score descending.
            5. Reassign ranks deterministically.
        """
        merged: List[Dict[str, Any]] = []
        for source in sources or []:
            if not source:
                continue
            merged.extend(source)

        deduped: Dict[tuple, Dict[str, Any]] = {}
        for it in merged:
            key = (
                str(it.get("query", "")).lower(),
                str(it.get("evidence", "")).lower(),
            )
            if key not in deduped:
                deduped[key] = dict(it)

        items = list(deduped.values())

        for it in items:
            base_rank = int(it.get("rank", 0) or 0)
            ev = str(it.get("evidence", ""))
            it["_fusion_score"] = (100 - base_rank) + 0.1 * len(ev)

        items.sort(key=lambda x: -x.get("_fusion_score", 0.0))

        for i, it in enumerate(items):
            it["rank"] = i + 1
            it.pop("_fusion_score", None)

        return items
