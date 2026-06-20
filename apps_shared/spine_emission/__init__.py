"""apps_shared.spine_emission — shared spine-receipt emission for apps_e2e certification.

Generalized from `apps_rg/runtime/` (the only previously-certified baseline)
to support multiple apps at once without each cloning ~700 LOC. Used by
any `apps_*` package that wants to reach
`SPINE_COMPLETE_CERTIFIED` under the two-gate certification model.

Plan: `.codex/plans/apps-e2e-spine-cert-wireup-e1c4d7.md` W1.
"""
from __future__ import annotations

from apps_shared.spine_emission.context import EmissionConfig, GovernedRun, governed_run
from apps_shared.spine_emission.otel_trace import StageTracer

__all__ = [
    "EmissionConfig",
    "GovernedRun",
    "governed_run",
    "StageTracer",
]
