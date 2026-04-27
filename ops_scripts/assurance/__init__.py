"""Assurance Plane (G-11 / `calibration_assurance_planes.md` §3) — out-of-band module.

Hosts the assurance-plane runners (red-team CI, threat-intel ingest, agentic
misalignment evals, vuln management). Reports here NEVER alter the current
certified run; their outputs feed the promotion gate
(`evaluation-promotion-gate.md`) which produces a ``PromotionReceipt``
consumed by the v5 plane out-of-band invariant guard.
"""

from __future__ import annotations

from ops_scripts.assurance.red_team_runner import (  # noqa: F401
    AssuranceReport,
    run_red_team_smoke,
)

__all__ = ["AssuranceReport", "run_red_team_smoke"]
