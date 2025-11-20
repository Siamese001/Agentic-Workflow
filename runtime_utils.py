# FILE: runtime_utils.py
"""
Unified Runtime Utilities (v10_10) — PURE INFRASTRUCTURE (REFACTORED)

This module provides the foundational "libc" for the agent.
It contains zero dependencies on L1-L5 logic to prevent circular imports.

Responsibilities:
    1. Exception Definitions: The standard error hierarchy (Pillar 8).
    2. Cost Tracking: Low-level span timing primitives (Pillar 11).
    3. Retrieval Math: BM25/Fusion algorithms for RAG (Pillar 7).
    4. Event Logging: Minimal sink for runtime events.

Refactor Highlights (v10_10):
    • Stripped of active Telemetry Buffer (moved to observability.py).
    • Pure functions only (stateless).
"""

from __future__ import annotations

import time
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# =============================================================================
# 1. STANDARD EXCEPTIONS (Pillar 8: Resilience)
# =============================================================================

class AgenticError(Exception):
    """Base class for all architecture errors."""

class ValidationError(AgenticError):
    """Data contract violation (Pydantic/Schema)."""

class ToolExecutionError(AgenticError):
    """Sandbox failure (timeout, crash)."""

class ModelClientError(AgenticError):
    """Gateway failure (API down, rate limit)."""

class WorkflowTimeoutError(AgenticError):
    """Orchestration timeout."""

class CircuitBreakerError(AgenticError):
    """Batch processing safety trip."""


# =============================================================================
# 2. COST & SPAN TRACKING (Pillar 11)
# =============================================================================

@dataclass
class CostTracker:
    """
    Minimal span timer used by L3/Gateway.
    """
    spans: Dict[str, Dict[str, Optional[float]]] = field(default_factory=dict)

    def start_span(self, name: str) -> None:
        self.spans[name] = {"start": time.perf_counter(), "end": None}

    def end_span(self, name: str) -> None:
        if name in self.spans and self.spans[name]["end"] is None:
            self.spans[name]["end"] = time.perf_counter()

    def snapshot(self) -> Dict[str, Any]:
        """Returns duration in ms."""
        out: List[Dict[str, Any]] = []
        for n, s in self.spans.items():
            start = s.get("start") or 0.0
            end = s.get("end") or start
            dur_ms = max(0.0, (end - start) * 1000.0)
            out.append({"name": n, "duration_ms": dur_ms})
        return {"spans": out}


# =============================================================================
# 3. EVENT LOGGING (Pillar 10)
# =============================================================================

# Simple global sink. In prod, this hooks to Datadog/Splunk/LangSmith.
_GLOBAL_EVENT_LOG: List[Dict[str, Any]] = []

def record_event(name: str, payload: Dict[str, Any]) -> None:
    """
    Low-level event recorder. 
    Used by Sandbox/Gateway where we can't import the full Observability stack.
    """
    event = {
        "event": name,
        "timestamp": time.time(),
        "payload": payload
    }
    _GLOBAL_EVENT_LOG.append(event)
    # In a CLI run, we might print specific high-value events
    if name in ("circuit_breaker_open", "tool_failure"):
        print(f"[\033[91mALERT\033[0m] {name}: {payload}")


# =============================================================================
# 4. RETRIEVAL ALGORITHMS (Pillar 7: RAG)
# =============================================================================

class Retrieval:
    """
    Pure-logic helpers for normalizing and deduplicating results.
    """
    @staticmethod
    def normalize_documents(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out = []
        for r in results:
            out.append({
                "query": str(r.get("query", "")),
                "evidence": str(r.get("evidence", "")),
                "rank": int(r.get("rank", 0) or 0)
            })
        return out

    @staticmethod
    def dedupe_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        # Stub for re-ranking logic
        return sorted(items, key=lambda x: x.get("rank", 0))

    @staticmethod
    def fuse_results(lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        merged = []
        for lst in lists:
            merged.extend(lst)
        # Simple Reciprocal Rank Fusion simulation
        return sorted(merged, key=lambda x: x.get("rank", 0))


class Ranking:
    """
    Deterministic scoring algorithms.
    """
    @staticmethod
    def bm25_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Length-heuristic simulation of BM25."""
        for it in items:
            it["score"] = len(it.get("evidence", ""))
        return sorted(items, key=lambda x: -x["score"])

    @staticmethod
    def dense_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Hash-based simulation of Vector Similarity."""
        for it in items:
            # deterministic pseudo-random score
            h = hashlib.sha256(it.get("evidence", "").encode()).hexdigest()
            it["score"] = int(h, 16) % 100
        return sorted(items, key=lambda x: -x["score"])

    @staticmethod
    def hybrid_rank(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Average of BM25 and Dense."""
        bm = Ranking.bm25_rank([dict(i) for i in items])
        dn = Ranking.dense_rank([dict(i) for i in items])
        
        # Merge scores (simplified O(N^2) for demo)
        for i in items:
            s1 = next((x["score"] for x in bm if x["evidence"] == i["evidence"]), 0)
            s2 = next((x["score"] for x in dn if x["evidence"] == i["evidence"]), 0)
            i["score"] = (s1 + s2) / 2
            
        return sorted(items, key=lambda x: -x["score"])


class RAGUtils:
    """
    Helpers for snippet extraction and metadata.
    """
    @staticmethod
    def normalize_rag_results(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Ensure every item has a 'metadata' dict
        for it in items:
            if "metadata" not in it:
                it["metadata"] = {
                    "snippet": it.get("evidence", "")[:50] + "..."
                }
        return items
