"""L6 eval-before-learn receipt — promotion blocked until eval + gauntlet (W6)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.spine.governed_l6_shadow_compose import PROMOTION_STATUS_BLOCKED

L6_EVAL_BEFORE_LEARN_RECEIPT_ARTIFACT = "l6_eval_before_learn_receipt.json"
SCOPE_SSOT = "apps_rg/config/domain_contract/L6_eval_before_learn_scope.md"


def build_l6_eval_before_learn_receipt(
    *,
    section_id: str,
    run_id: str,
    governed_envelope: dict[str, Any] | None = None,
    runtime_exhaust_ref: str = "",
    exit_disposition_ref: str = "",
) -> dict[str, Any]:
    env = governed_envelope if isinstance(governed_envelope, dict) else {}
    return {
        "schema_version": "apps_rg_l6_eval_before_learn_receipt_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "section_id": section_id,
        "run_id": run_id,
        "scope_ssot": SCOPE_SSOT,
        "promotion_status": env.get("promotion_status") or PROMOTION_STATUS_BLOCKED,
        "promotion_allowed": False,
        "eval_before_learn_required": bool(env.get("eval_before_learn_required", True)),
        "eval_before_learn_satisfied": bool(env.get("eval_before_learn_satisfied", False)),
        "gauntlet_required": bool(env.get("gauntlet_required", True)),
        "gauntlet_satisfied": bool(env.get("gauntlet_satisfied", False)),
        "runtime_exhaust_bundle_ref": runtime_exhaust_ref
        or str(env.get("runtime_exhaust_bundle_ref") or ""),
        "exit_disposition_ref": exit_disposition_ref or str(env.get("exit_disposition_ref") or ""),
        "governed_l6_shadow_mode": str(env.get("governed_l6_shadow_mode") or ""),
        "no_l6_current_run_rescue_assertion": bool(env.get("no_l6_current_run_rescue_assertion", True)),
        "explicit_non_claims": list(env.get("explicit_non_claims") or [])
        or [
            "shadow ingest only; promotion requires human eval labels + gauntlet",
            "section-only lanes: eval pipeline N/A until stratified labels exist",
        ],
    }


def emit_l6_eval_before_learn_receipt(
    artifact_dir: Path | str,
    receipt: dict[str, Any],
) -> Path:
    root = Path(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / L6_EVAL_BEFORE_LEARN_RECEIPT_ARTIFACT
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


__all__ = [
    "L6_EVAL_BEFORE_LEARN_RECEIPT_ARTIFACT",
    "SCOPE_SSOT",
    "build_l6_eval_before_learn_receipt",
    "emit_l6_eval_before_learn_receipt",
]
