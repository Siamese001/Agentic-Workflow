"""Governed L6 shadow ingest — post-run exhaust only (W7).

Section lanes: ``runtime_exhaust_bundle.json`` + ``l6_shadow_handoff_receipt.json`` before
``build_l6_shadow_package``. Integrated: core ``RuntimeExhaustBundle`` from W6 governed exit.

No promotion without eval + gauntlet (REQ-L6-EVAL-BEFORE-LEARN-001) — documented N/A for
section-only shadow packets until human eval labels exist.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

GOVERNED_L6_SHADOW_MODE_SECTION = "section_lane_post_exhaust"
GOVERNED_L6_SHADOW_MODE_INTEGRATED = "integrated_spine_exhaust"
PROMOTION_STATUS_BLOCKED = "BLOCKED_EVAL_BEFORE_LEARN"


def governed_l6_shadow_enabled() -> bool:
    if os.environ.get("APPS_RG_GOVERNED_L6_SHADOW_SKIP", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    return True


def assert_l6_shadow_ingest_preconditions(
    artifact_dir: Path,
    *,
    section_id: str,
    runtime_payload: dict[str, Any] | None = None,
    product_visible: bool | None = None,
) -> None:
    """Fail closed before L6 shadow ingest on product-visible section lanes."""
    if not governed_l6_shadow_enabled():
        return
    from apps_rg.runtime.section_runtime_exhaust_lane_integration import (
        gate_section_l6_shadow_after_exhaust,
    )

    payload = dict(runtime_payload or {})
    payload.setdefault("section_id", section_id)
    if product_visible is not None:
        payload["product_visible"] = product_visible
    gate_section_l6_shadow_after_exhaust(artifact_dir, payload)


def assert_integrated_exhaust_may_feed_l6(exhaust: Any) -> None:
    """Integrated path — only sealed core ``RuntimeExhaustBundle`` may feed L6."""
    if not governed_l6_shadow_enabled():
        return
    if exhaust is None:
        raise ValueError("integrated L6 shadow requires RuntimeExhaustBundle from governed exit")
    if not bool(getattr(exhaust, "created_after_exit", False)):
        raise ValueError(
            "RuntimeExhaustBundle.created_after_exit must be True before L6 shadow ingest"
        )
    if not bool(getattr(exhaust, "current_run_closed", False)):
        raise ValueError(
            "RuntimeExhaustBundle.current_run_closed must be True before L6 shadow ingest"
        )
    exit_ref = str(getattr(exhaust, "exit_disposition_ref", "") or "").strip()
    if not exit_ref:
        raise ValueError("RuntimeExhaustBundle.exit_disposition_ref required for L6 handoff")


def build_governed_l6_handoff_envelope(
    *,
    section_id: str,
    run_id: str,
    mode: str,
    runtime_exhaust_ref: str,
    exit_disposition_ref: str = "",
    x3_code: str = "",
) -> dict[str, Any]:
    """Governed L6 handoff metadata — promotion blocked until eval + gauntlet."""
    return {
        "schema_version": "governed_l6_handoff_envelope_v1",
        "contract_type": "GovernedL6ShadowHandoffEnvelope",
        "section_id": section_id,
        "run_id": run_id,
        "governed_l6_shadow_mode": mode,
        "runtime_exhaust_bundle_ref": runtime_exhaust_ref,
        "exit_disposition_ref": exit_disposition_ref,
        "observed_x3_code": x3_code,
        "promotion_status": PROMOTION_STATUS_BLOCKED,
        "eval_before_learn_required": True,
        "eval_before_learn_satisfied": False,
        "gauntlet_required": True,
        "gauntlet_satisfied": False,
        "no_l6_current_run_rescue_assertion": True,
        "no_l6_current_run_mutation_assertion": True,
        "l6_can_change_x3": False,
        "l6_can_change_exit_disposition": False,
        "explicit_non_claims": [
            "shadow ingest only; not promotion or certification",
            "section-only lanes: eval+gauntlet N/A until human labels (see L6_eval_before_learn_scope.md)",
        ],
    }


def ingest_integrated_exhaust_for_l6_shadow(
    exhaust: Any,
    *,
    section_id: str = "integrated",
    run_id: str = "",
) -> dict[str, Any]:
    """Validate integrated exhaust and return governed L6 handoff envelope."""
    assert_integrated_exhaust_may_feed_l6(exhaust)
    rid = run_id or str(getattr(exhaust, "run_id", "") or "")
    exit_ref = str(getattr(exhaust, "exit_disposition_ref", "") or "")
    bundle_ref = str(
        getattr(exhaust, "deterministic_digest", "")
        or getattr(exhaust, "bundle_id", "")
        or "runtime_exhaust_bundle"
    )
    return build_governed_l6_handoff_envelope(
        section_id=section_id,
        run_id=rid,
        mode=GOVERNED_L6_SHADOW_MODE_INTEGRATED,
        runtime_exhaust_ref=bundle_ref,
        exit_disposition_ref=exit_ref,
    )


__all__ = [
    "GOVERNED_L6_SHADOW_MODE_INTEGRATED",
    "GOVERNED_L6_SHADOW_MODE_SECTION",
    "PROMOTION_STATUS_BLOCKED",
    "assert_integrated_exhaust_may_feed_l6",
    "assert_l6_shadow_ingest_preconditions",
    "build_governed_l6_handoff_envelope",
    "governed_l6_shadow_enabled",
    "ingest_integrated_exhaust_for_l6_shadow",
]
