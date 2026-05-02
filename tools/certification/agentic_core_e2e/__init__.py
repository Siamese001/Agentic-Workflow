"""Standalone agentic_core spine harness.

Distinct from tools.certification.apps_e2e.* — proves the core spine
works WITHOUT any apps_* overlay.

Boundary invariant (constitutional §31, plan §14):
  * tools.certification.agentic_core_e2e.* MUST NOT import from
    tools.certification.apps_e2e.* and vice versa.
  * Apps harness proves app→spine. Core harness proves spine alone.
  * Neither can satisfy the other's contract.

Plan: .windsurf/plans/apps-e2e-auditability-harness-7c2a91.md  (Wave 5)
"""
from __future__ import annotations

__all__: tuple[str, ...] = (
    "CORE_PROOF_SCHEMA_VERSION",
    "CORE_HARNESS_SCHEMA_VERSION",
    "CORE_ROUTE_MATRIX_SCHEMA_VERSION",
)

CORE_PROOF_SCHEMA_VERSION = "agentic_core_e2e_proof/2026-05-01/v1"
CORE_HARNESS_SCHEMA_VERSION = "agentic_core_e2e_harness/2026-05-01/v1"
CORE_ROUTE_MATRIX_SCHEMA_VERSION = "agentic_core_e2e_route_matrix/2026-05-01/v1"
