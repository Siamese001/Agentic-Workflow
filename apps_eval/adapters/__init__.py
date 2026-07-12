"""Narrow optional live adapters for product runtimes."""

from apps_eval.adapters.apps_lic import run_apps_lic_live
from apps_eval.adapters import apps_rg as _apps_rg

# Canonical apps_rg L2 E1-E5 artifacts. Keeping this additive here avoids
# duplicating the live adapter while making every direct/submodule import see
# the same role map (package __init__ runs before the submodule import returns).
_apps_rg._LANE_ARTIFACT_ROLE_BY_NAME.update(
    {
        "l2_execution_packet.json": "l2_execution_packet",
        "frozen_execution_context.json": "frozen_execution_context",
        "prep_receipt.json": "prep_receipt",
        "validation_receipt.json": "validation_receipt",
        "attempt_receipt.json": "attempt_receipt",
        "heal_receipt.json": "heal_receipt",
        "seal_receipt.json": "seal_receipt",
        "l2_receipt_bundle.json": "l2_receipt_bundle",
        "sealed_l2_artifact.json": "sealed_l2_artifact",
        "l2_handoff_receipt.json": "l2_handoff_receipt",
    }
)

run_apps_rg_live = _apps_rg.run_apps_rg_live

__all__ = ["run_apps_lic_live", "run_apps_rg_live"]
