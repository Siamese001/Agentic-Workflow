# FILE: 10_10/observability.py
"""
Observability Utilities (v10_10)
================================

This module provides a minimal, safe, structured event logging system for
the v10_10 agentic workflow.

Goals:
    • Emit structured events for all L1–L5 layers.
    • Work safely in the Windsurf sandbox (stdout-based trace emission).
    • Avoid any external dependencies or network calls.
    • Never crash the workflow (observability must be failure-safe).
    • Provide spans for profiling and golden-state debugging.
    • Emit JSON records usable by:
         - CI/CD pipelines
         - Golden evaluation harness
         - Local debugging
         - Multi-run batch logs

Non-Responsibilities:
    • No persistent storage.
    • No distributed tracing.
    • No telemetry exports.
    • No state mutation.
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from typing import Dict, Any, Optional


# =============================================================================
# Internal Helper
# =============================================================================

def _safe_print(obj: Dict[str, Any]) -> None:
    """
    Safely emit a JSON event to stdout.
    No exceptions should propagate from here.
    """
    try:
        sys.stdout.write(json.dumps(obj) + "\n")
        sys.stdout.flush()
    except Exception:
        # Absolute fail-safe: swallow all errors
        pass


# =============================================================================
# Span Utilities
# =============================================================================

def start_span(name: str, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Start a structured span.

    Returns a span context object with:
        {
            "span_id": <int>,
            "span_name": <str>,
            "start_ts": <float>,
            "ctx": {...}
        }
    """
    span = {
        "span_id": int(time.time() * 1_000_000),
        "span_name": name,
        "start_ts": time.time(),
        "ctx": ctx or {},
    }

    _safe_print(
        {
            "type": "span_start",
            "span_id": span["span_id"],
            "span_name": name,
            "ctx": span["ctx"],
            "ts": span["start_ts"],
        }
    )

    return span


def end_span(span: Dict[str, Any]) -> None:
    """
    End a span previously created by start_span().
    """
    try:
        duration = time.time() - span["start_ts"]
    except Exception:
        duration = None

    _safe_print(
        {
            "type": "span_end",
            "span_id": span.get("span_id"),
            "span_name": span.get("span_name"),
            "duration_s": duration,
            "ts": time.time(),
        }
    )


# =============================================================================
# Event Logging
# =============================================================================

def record_event(event_name: str, data: Dict[str, Any]) -> None:
    """
    Emit a structured event.
    """
    _safe_print(
        {
            "type": "event",
            "event": event_name,
            "data": data,
            "ts": time.time(),
        }
    )


def record_exception(event_name: str, exc: Exception) -> None:
    """
    Emit a structured exception event with traceback.
    """
    _safe_print(
        {
            "type": "exception",
            "event": event_name,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "ts": time.time(),
        }
    )
