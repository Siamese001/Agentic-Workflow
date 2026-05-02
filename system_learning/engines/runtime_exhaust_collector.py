"""Compatibility shim — symbols promoted to agentic_core 2026-05-01.

The canonical home is now
``agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle``.
This module re-exports every public name so existing callers continue
to work without modification.

New code should import directly from agentic_core. This shim will be
kept for backward compatibility but is not the SSOT.
"""

from __future__ import annotations

from agentic_core.L6_observability.runtime_trace.runtime_exhaust_bundle import (
    REQUIRED_LINEAGE_FIELDS,
    ExhaustDefect,
    GapReport,
    RuntimeExhaustBundle,
    RuntimeExhaustCollector,
)

__all__ = [
    "REQUIRED_LINEAGE_FIELDS",
    "ExhaustDefect",
    "GapReport",
    "RuntimeExhaustBundle",
    "RuntimeExhaustCollector",
]
