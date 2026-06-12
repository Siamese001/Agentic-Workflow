"""Retired SelectedRoleFactSet runtime surface.

SRFS is no longer a valid proof authority for apps_rg section lanes. Runtime
code must use apps_rg.runtime.sections.graph_evidence_contract plus
selected_graph_evidence_plan instead.
"""

from __future__ import annotations

raise RuntimeError(
    "SelectedRoleFactSet/SRFS runtime surface is retired. "
    "Use graph_evidence_contract and selected_graph_evidence_plan."
)
