# FILE: v10_9_clean/runtime_utils.py
"""
Unified Runtime Utilities (v10_9)

This module consolidates ALL former "shared" components into a single,
logically-namespaced file using nested classes:

    • Models       (PlanObject, WorkflowState, ExecutionResult, etc.)
    • Constants    (WorkflowPhase, NodeStatus, etc.)
    • Exceptions   (ValidationError, ToolExecutionError, etc.)
    • Config       (system configuration structures)
    • Telemetry    (metrics, spans, trace context)
    • Optimization (cost/latency optimization hints)
    • Retrieval    (normalize, dedupe, merge, prune)
    • Ranking      (bm25, dense, hybrid)
    • RAGUtils     (rag normalization + fusion logic)

All logic is stateless and safe to import anywhere in the runtime.

Pure utilities only:
    • No planning (L1)
    • No execution (L2)
    • No orchestration (L3)
    • No state mutation (L4)
    • No safety/policy (L5)
"""

from __future__ import annotations
import time
import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================================
# CONSTANTS
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

    CANONICAL_MODEL_DEFAULT = "gpt-4.1"


# ============================================================================
# EXCEPTIONS
# ============================================================================

class Exceptions:
    class ValidationError(Exception):
        pass

    class ModelClientError(Exception):
        pass

    class ToolExecutionError(Exception):
        pass

    class SafetyException(Exception):
        pass


# ============================================================================
# MODELS
# ============================================================================

class Models:

    @dataclass
    class PlanObject(dict):
        """
        Generic dict-backed plan container used by L1 layers.
        """
        def __getattr__(self, item):
            return self.get(item)

    @dataclass
    class ExecutionResult:
        status: str
        payload: Dict[str, Any]
        model: str
        usage: Dict[str, Any]

        SUCCESS = "success"
        FAILURE = "failure"

    @dataclass
    class WorkflowState:
        workflow_id: str
        phase: str
        nodes: Dict[str, Any]
        state: Dict[str, Any]
        phase_metadata: Dict[str, Any]

    @dataclass
    class PhaseMetadata:
        phase: str
        note: str = ""

    @dataclass
    class StatePatch:
        key: str
        value: Any
        scope: str = "local"


# ============================================================================
# CONFIG
# ============================================================================

class Config:
    @dataclass
    class ConfigV10_9:
        default_model: str = Constants.CANONICAL_MODEL_DEFAULT
        model_aliases: Dict[str, str] = field(default_factory=dict)
        cache: Dict[str, Any] = field(default_factory=dict)
        budget: Dict[str, Any] = field(default_factory=dict)
        telemetry: Dict[str, Any] = field(default_factory=dict)
        validators: Dict[str, Any] = field(default_factory=dict)
        tuning: Dict[str, Any] = field(default_factory=dict)

        def canonical_alias_map(self) -> Dict[str, str]:
            return {k.lower(): v for k, v in self.model_aliases.items()}


# ============================================================================
# TELEMETRY
# ============================================================================

class Telemetry:

    @dataclass
    class MetricEvent:
        name: str
        value: float
        tags: Dict[str, Any]

    @dataclass
    class SpanEvent:
        name: str
        start_time_ms: int
        end_time_ms: int
        tags: Dict[str, Any]

    @dataclass
    class TraceContext:
        trace_id: str
        spans: Dict[str, SpanEvent]

    _EVENTS: List[Dict[str, Any]] = []

    @classmethod
    def record_event(cls, name: str, payload: Dict[str, Any]) -> None:
        cls._EVENTS.append({"name": name, "payload": payload})

    @classmethod
    def get_events(cls) -> List[Dict[str, Any]]:
        return list(cls._EVENTS)


# ============================================================================
# COST TRACKING & OPTIMIZATION
# ============================================================================

class Optimization:

    @dataclass
    class CostTracker:
        spans: Dict[str, Dict[str, float]] = field(default_factory=dict)

        def start_span(self, name: str) -> None:
            self.spans[name] = {"start": time.perf_counter(), "end": None}

        def end_span(self, name: str) -> None:
            if name in self.spans and self.spans[name]["end"] is None:
                self.spans[name]["end"] = time.perf_counter()

        def snapshot(self) -> Dict[str, Any]:
            data = []
            for name, span in sorted(self.spans.items()):
                start = span["start"]
                end = span["end"] or start
                duration_ms = max((end - start) * 1000.0, 0.0)
                data.append({"name": name, "duration_ms": duration_ms})
            return {"spans": data}

    @staticmethod
    def compute_optimization_hint(spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        planning = next((s for s in spans if s.get("name") == "planning"), {"duration_ms": 0})
        execution = next((s for s in spans if s.get("name") == "execution"), {"duration_ms": 0})

        if float(planning.get("duration_ms", 0)) > float(execution.get("duration_ms", 0)):
            return {"suggestion": "reroute_fast"}
        return {"suggestion": "normal"}


# ============================================================================
# RETRIEVAL UTILITIES
# ============================================================================

class Retrieval:

    @staticmethod
    def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for r in results:
            out.append({
                "query": r.get("query", ""),
                "evidence": r.get("evidence", ""),
                "rank": r.get("rank", 0),
            })
        return out

    @staticmethod
    def dedupe_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        out = []
        for i in items:
            k = (i.get("query", ""), i.get("evidence", ""))
            if k not in seen:
                seen.add(k)
                out.append(i)
        return out

    @staticmethod
    def rerank_results(items: List[Dict[str, Any]], strategy: str = "hybrid") -> List[Dict[str, Any]]:
        return sorted(items, key=lambda x: x.get("rank", 0))

    @staticmethod
    def fuse_results(lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        merged = []
        for lst in lists:
            for item in lst:
                merged.append(dict(item))
        return sorted(merged, key=lambda x: (x.get("query", ""), x.get("rank", 0)))


# ============================================================================
# RANKING UTILITIES
# ============================================================================

class Ranking:

    @staticmethod
    def _score_dense(text: str) -> int:
        digest = hashlib.sha256(text.encode()).hexdigest()
        return int(digest, 16) % 100

    @staticmethod
    def bm25_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for it in items:
            score = len(str(it.get("evidence", "")))
            scored.append({**it, "score": score})
        return sorted(scored, key=lambda x: -x["score"])

    @staticmethod
    def dense_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for it in items:
            score = Ranking._score_dense(str(it.get("query", "")))
            scored.append({**it, "score": score})
        return sorted(scored, key=lambda x: -x["score"])

    @staticmethod
    def hybrid_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for it in items:
            bm = len(str(it.get("evidence", "")))
            dn = Ranking._score_dense(str(it.get("query", "")))
            score = (bm + dn) / 2
            scored.append({**it, "score": score})
        return sorted(scored, key=lambda x: -x["score"])


# ============================================================================
# RAG UTILS (Normalization + Fusion)
# ============================================================================

class RAGUtils:

    @staticmethod
    def normalize_evidence(evidence: Any) -> str:
        if evidence is None:
            return ""
        return str(evidence).strip()

    @staticmethod
    def extract_snippet(evidence: str, max_len: int = 350) -> str:
        return evidence[:max_len].rstrip() if evidence else ""

    @staticmethod
    def build_metadata(query: str, evidence: str, rank: int) -> Dict[str, Any]:
        return {
            "query": query,
            "rank": rank,
            "snippet": RAGUtils.extract_snippet(evidence),
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
        for it in items:
            it["_fusion_score"] = (
                (100 - it.get("rank", 0)) +
                0.1 * len(str(it.get("evidence", "")))
            )

        items.sort(key=lambda x: -x["_fusion_score"])
        for idx, it in enumerate(items):
            it["rank"] = idx + 1
            del it["_fusion_score"]

        return items
