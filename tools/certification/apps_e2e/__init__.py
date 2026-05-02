"""Shared end-to-end auditability harness for all apps_* packages.

Generalizes the apps_rg_e2e pattern (tools/certification/apps_rg_e2e/) into
a single declarative harness that:

  * discovers each runnable apps_* package
  * runs `python -m <app>` via the canonical entrypoint
  * collects spine receipts (U0/L1/L0/L3/C0/PA/L2/Exit/L6/OTEL)
  * emits a hash-bound proof bundle per app
  * rolls per-app bundles up into one apps_e2e_matrix.json

Apps remain overlays. The harness reads spine artifacts; it never executes
spine work itself.

Plan: .windsurf/plans/apps-e2e-auditability-harness-7c2a91.md
"""
from __future__ import annotations

__all__: tuple[str, ...] = (
    "PROOF_SCHEMA_VERSION",
    "HARNESS_SCHEMA_VERSION",
    "MATRIX_SCHEMA_VERSION",
)

PROOF_SCHEMA_VERSION = "apps_e2e_proof/2026-05-01/v1"
HARNESS_SCHEMA_VERSION = "apps_e2e_harness/2026-05-01/v1"
MATRIX_SCHEMA_VERSION = "apps_e2e_matrix/2026-05-01/v1"
