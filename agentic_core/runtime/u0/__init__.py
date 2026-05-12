"""agentic_core.runtime.u0 — U0 ingress adaptation surface.

The U0 layer adapts raw external ingress JSON into ``ValidatedRequest``
contracts. Per Author-Gate AG-1.d, apps_rg's ingress is the
``AppsRgIngressContractV1`` declarative payload; U0 reflects every JSON
Pointer through the field-map SSOT and emits an
``AppsRgU0ReflectionReceipt`` proving every input field is accounted for.

Plan: .windsurf/plans/apps-rg-u0-reflection-harness-79d032.md
"""
from __future__ import annotations

# Core-only imports - apps_rg specific modules are in apps_rg.runtime.u0
from agentic_core.runtime.u0.reflection_receipt import AppsRgU0ReflectionReceipt

__all__ = [
    "AppsRgU0ReflectionReceipt",
]
