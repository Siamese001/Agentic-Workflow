# FILE: 10_10/observability.py
"""
Observability Utilities (v10_10)
================================

This module provides a SAFE, MINIMAL, and DETERMINISTIC observability layer
for the v10_10 agentic architecture.

Responsibilities:
    • Structured span logging
    • Structured event logging
    • Structured exception logging

Non-Responsibilities:
    • No metrics aggregation
    • No domain summaries
    • No meta-learning updates
    • No orchestration or state mutation
    • No provider calls
    • No CostTracker or HIL summaries
    • No async decorators or cross-layer logic

This design aligns with:
    - Layering Pillar (#1)
    - Observability Pillar (#10)
    - Execution Sandbox Pillar (#14)
    - v10_10's strict L1–L5 boundaries
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from typing import Any, Dict, Optional


# =============================================================================
# Safe Output Helper
# =============================================================================

def _safe_emit(payload: Dict[str, Any]) -> None:
    """
    Emit a JSON record to stdout. Never raise exceptions.
    """
    try:
        sys.stdout.write(json.dumps(payload) + "\n")
        sys.stdout.flush()
    except Exception:
        # Observability must NEVER interrupt the main workflow
        pass


# =============================================================================
# Spans
# =============================================================================

def start_span(name: str, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Start a structured span.

    Returns:
        A span context dict with:
            {
                "span_id": int,
                "span_name": str,
                "start_ts": float,
                "ctx": dict   # user-supplied contextual info
            }
    """
    now = time.time()
    span = {
        "span_id": int(now * 1_000_000),
        "span_name": name,
        "start_ts": now,
        "ctx": ctx or {},
    }

    _safe_emit({
        "type": "span_start",
        "span_id": span["span_id"],
        "span_name": name,
        "ts": now,
        "ctx": span["ctx"],
    })

    return span


def end_span(span: Dict[str, Any]) -> None:
    """
    End a span created by start_span().
    """
    try:
        duration = time.time() - span.get("start_ts", 0.0)
    except Exception:
        duration = None

    _safe_emit({
        "type": "span_end",
        "span_id": span.get("span_id"),
        "span_name": span.get("span_name"),
        "duration_s": duration,
        "ts": time.time(),
    })


# =============================================================================
# Events
# =============================================================================

def record_event(event_name: str, data: Dict[str, Any]) -> None:
    """
    Emit a simple structured event.
    """
    _safe_emit({
        "type": "event",
        "event": event_name,
        "data": data,
        "ts": time.time(),
    })


def record_exception(event_name: str, exc: Exception) -> None:
    """
    Emit a structured exception event with full traceback.
    """
    _safe_emit({
        "type": "exception",
        "event": event_name,
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "ts": time.time(),
    })
