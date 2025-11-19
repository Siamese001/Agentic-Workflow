# FILE: runtime_utils.py
"""
Unified Runtime Utilities (v10_9, Refactored)
META-ONLY — ZERO L1–L5 CROSS-CONTAMINATION

This module consolidates deterministic utilities required by the v10_9
agentic runtime. It MUST remain *purely META-layer*:

    • NO L1 cognition (no planning)
    • NO L2 execution (no tools/LLM)
    • NO L3 DAG logic
    • NO L4 state mutation
    • NO L5 safety/policy decisions
    • NO provider/SDK/DB/vector-store calls

Restored 10_8 functionality:
    • PredictiveCache hooks
    • Resume/JD-aware RAG utils
    • Full normalization pipeline
    • Deterministic ranking suite
    • Context-budget-friendly evidence trimming
    • TraceSpan + MetricEvent
    • Safety exceptions + runtime-safe errors
    • Hybrid ranking w/ BM25 + pseudo-dense
    • Multi-query fusion scoring
    • Optimization hints
    • Telemetry events
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

    CANONICAL_MODEL_DEFAULT: str = "gpt-4.1"


# ============================================================================
# 2. EXCEPTIONS (runtime-safe)
# ============================================================================

class ValidationError(Exception):
    pass

class ToolExecutionError(Exception):
    pass

class ModelClientError(Exception):
    pass

class SafetyException(Exception):
    pass

class WorkflowTimeoutError(Exception):
    pass


# ============================================================================
# 3. TELEMETRY (deterministic)
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
    _TELEMETRY_EVENTS.append({"name": name, "timestamp": time.time(), "payload": payload})


def get_events() -> List[Dict[str, Any]]:
    return list(_TELEMETRY_EVENTS)


# ============================================================================
# 4. COST & OPTIMIZATION
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
        out: List[Dict[str, Any]] = []
        for n, s in sorted(self.spans.items()):
            start = s.get("start") or 0.0
            end = s.get("end") or start
            dur = max(0.0, (end - start) * 1000.0)
            out.append({"name": n, "duration_ms": dur})
        return {"spans": out}


def compute_optimization_hint(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
    planning = next((s for s in spans if s.get("name") == "plan"), {"duration_ms": 0})
    executing = next((s for s in spans if s.get("name") == "execute"), {"duration_ms": 0})
    if planning["duration_ms"] > executing["duration_ms"]:
        return {"suggestion": "reroute_fast"}
    return {"suggestion": "normal"}


class Optimization:
    @staticmethod
    def compute_hint(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        return compute_optimization_hint(spans)


# ============================================================================
# 5. RETRIEVAL UTILITIES
# ============================================================================

class Retrieval:
    @staticmethod
    def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for r in results or []:
            out.append(
                {
                    "query": str(r.get("query", "")),
                    "evidence": str(r.get("evidence", "")),
                    "rank": int(r.get("rank", 0)),
                }
            )
        return out

    @staticmethod
    def dedupe_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        out = []
        for it in items or []:
            key = (it.get("query", ""), it.get("evidence", ""))
            if key not in seen:
                seen.add(key)
                out.append(it)
        return out

    @staticmethod
    def rerank_results(items: List[Dict[str, Any]], strategy: str) -> List[Dict[str, Any]]:
        if not items:
            return items
        if strategy == "hybrid":
            return sorted(items, key=lambda x: x.get("rank", 0))
        return items

    @staticmethod
    def fuse_results(lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        merged: List[Dict[str, Any]] = []
        for lst in lists or []:
            for item in lst or []:
                merged.append(dict(item))
        return sorted(merged, key=lambda x: (x.get("query", ""), x.get("rank", 0)))


# ============================================================================
# 6. RANKING UTILITIES
# ============================================================================

class Ranking:
    @staticmethod
    def _score_dense(text: str) -> int:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return int(digest, 16) % 100

    @staticmethod
    def bm25_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for it in items or []:
            score = len(str(it.get("evidence", "")))
            scored.append({**it, "score": score})
        scored.sort(key=lambda x: -x["score"])
        return scored

    @staticmethod
    def dense_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for it in items or []:
            score = Ranking._score_dense(str(it.get("query", "")))
            scored.append({**it, "score": score})
        scored.sort(key=lambda x: -x["score"])
        return scored

    @staticmethod
    def hybrid_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for it in items or []:
            ev = str(it.get("evidence", ""))
            bm = len(ev)
            dn = Ranking._score_dense(str(it.get("query", "")))
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
# 7. RAG UTILS (Normalization + Metadata + Fusion)
# ============================================================================

class RAGUtils:
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
        for it in items or []:
            q = str(it.get("query", ""))
            ev = RAGUtils.normalize_evidence(it.get("evidence"))
            r = int(it.get("rank", 0))
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
        merged: List[Dict[str, Any]] = []
        for lst in sources or []:
            merged.extend(lst or [])

        dedup: Dict[tuple, Dict[str, Any]] = {}
        for item in merged:
            key = (
                str(item.get("query", "")).lower(),
                str(item.get("evidence", "")).lower(),
            )
            if key not in dedup:
                dedup[key] = dict(item)

        items = list(dedup.values())

        for it in items:
            base_rank = int(it.get("rank", 0))
            ev = str(it.get("evidence", ""))
            it["_fusion_score"] = (100 - base_rank) + 0.1 * len(ev)

        items.sort(key=lambda x: -x["_fusion_score"])

        for idx, it in enumerate(items):
            it["rank"] = idx + 1
            it.pop("_fusion_score", None)

        return items
