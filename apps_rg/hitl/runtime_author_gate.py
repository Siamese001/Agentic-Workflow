"""QUARANTINE NOTICE — AG-RGGOV-8: QUARANTINE_ALL_RUNTIME_HOPS

This file is QUARANTINED per the declarative ingress-only governance model.
apps_rg may NOT import from L5 safety runtime gates.

Original: apps_rg/hitl/runtime_author_gate.py
Quarantined: 2026-05-09
Reason: AG-RGGOV-W4-SCOPE — L5 safety gate import (runtime authority)

Importing this module raises RuntimeError immediately.
Core L5 owns all safety gates.

Original code archived to:
archives/apps_rg/quarantine_w4_20260509/hitl/runtime_author_gate.py.ORIGINAL
"""

raise RuntimeError(
    "QUARANTINE VIOLATION (AG-RGGOV-8): "
    "apps_rg.hitl.runtime_author_gate is QUARANTINED. "
    "apps_rg may NOT import from L5 safety gates. "
    "Core L5 owns all safety gates. "
    "See: .windsurf/plans/apps-rg-declarative-ingress-only-spinal-governance-c8b3e1.md §19"
)
