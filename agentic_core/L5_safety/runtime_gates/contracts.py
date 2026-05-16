"""Stable public runtime gate contracts (W3C fan-in facade).

Canonical definitions live in :mod:`agentic_core.L5_safety.runtime_gates.types`.
Runtime bridges, CI, tests, and gate implementations should import gate mesh
types from **this** module so ADG fan-in concentrates on a thin re-export
layer instead of ``types.py``.

``types`` remains the SSOT for dataclasses/enums; legacy
``from ...runtime_gates.types import ...`` is still valid during migration.
"""

from __future__ import annotations

from agentic_core.L5_safety.runtime_gates.types import (
    SCHEMA_VERSION,
    DecisionAlias,
    Disposition,
    GateContext,
    GateDecision,
    GraderType,
    RegressionSignal,
    Result,
    Severity,
)

__all__ = [
    "SCHEMA_VERSION",
    "DecisionAlias",
    "Disposition",
    "GateContext",
    "GateDecision",
    "GraderType",
    "RegressionSignal",
    "Result",
    "Severity",
]
