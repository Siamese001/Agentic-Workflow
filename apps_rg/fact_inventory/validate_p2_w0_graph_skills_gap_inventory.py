"""P2-W0 gap inventory validator — inventory-only wave; no competencies runtime changes."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
INVENTORY_JSON = ROOT / "docs/reports/apps_rg/graph_skills_hardening_gap_inventory.json"
INVENTORY_MD = ROOT / "docs/reports/apps_rg/graph_skills_hardening_gap_inventory.md"
P1_W4_CLOSEOUT = ROOT / "docs/reports/apps_rg/career_track_p1_w4_closeout_receipt.json"
P1_W5_RECEIPT = ROOT / "docs/reports/apps_rg/career_track_p1_w5_track_balanced_sections_receipt.json"

REQUIRED_WAVES = tuple(f"P2-W{i}" for i in range(1, 10))


class P2W0GapInventoryError(ValueError):
    """P2-W0 inventory contract violation."""


def validate_p2_w0_graph_skills_gap_inventory(payload: dict[str, Any]) -> None:
    errors: list[str] = []

    if str(payload.get("wave") or "") != "P2-W0":
        errors.append(f"wave must be P2-W0; got {payload.get('wave')!r}")
    if payload.get("inventory_only") is not True:
        errors.append("inventory_only must be true")
    if payload.get("live_competencies_runtime_modified") is not True:
        if payload.get("live_competencies_runtime_modified") is not False:
            errors.append("live_competencies_runtime_modified must be false")
    if payload.get("live_competencies_x3_allow_claimed") is True:
        errors.append("live_competencies_x3_allow_claimed must be false")
    if payload.get("broad_skills_ledger_accepted_future_authority") is True:
        errors.append("broad_skills_ledger must not be accepted as future authority")

    gap = payload.get("broad_skills_ledger_current_state") or {}
    superseded = payload.get("p2_w1a_supersession") or {}
    if superseded.get("gap_closed") is True:
        if gap.get("is_current_proof_pool_authority") is not False:
            errors.append(
                "after P2-W1A, broad_skills_ledger_current_state.is_current_proof_pool_authority must be false"
            )
    elif gap.get("is_current_proof_pool_authority") is not True:
        errors.append("broad_skills_ledger_current_state.is_current_proof_pool_authority must be true")
    if gap.get("accepted_future_product_authority") is not False:
        errors.append("broad_skills_ledger accepted_future_product_authority must be false")
    if superseded.get("gap_closed") is True:
        if payload.get("competencies_graph_proof_pool_implemented") is not True:
            errors.append("competencies_graph_proof_pool_implemented must be true after P2-W1A supersession")

    targets = payload.get("p2_wave_targets") or {}
    for wave in REQUIRED_WAVES:
        if wave not in targets:
            errors.append(f"missing p2_wave_targets.{wave}")
            continue
        block = targets[wave]
        for key in ("target_files", "intended_behavior", "acceptance_test", "required_receipt_or_artifact", "non_claims"):
            if key not in block:
                errors.append(f"{wave} missing {key}")

    refs = payload.get("part1_proof_refs") or {}
    for key in ("p1_w4_closeout_receipt_ref", "p1_w5_projection_receipt_ref", "p1_w4_c03_graph_bound_status", "p1_w5_live_competencies_runtime_modified"):
        if key not in refs:
            errors.append(f"part1_proof_refs missing {key}")
    if str(refs.get("p1_w4_c03_graph_bound_status") or "") != "BOUND":
        errors.append("part1_proof_refs.p1_w4_c03_graph_bound_status must be BOUND")
    if refs.get("p1_w5_live_competencies_runtime_modified") is not False:
        errors.append("p1_w5_live_competencies_runtime_modified must be false")

    matrix = payload.get("gap_matrix") or []
    if len(matrix) < 8:
        errors.append("gap_matrix must have >= 8 rows")

    if errors:
        raise P2W0GapInventoryError("; ".join(errors))


def validate_p2_w0_artifact_files_exist(repo_root: Path | None = None) -> None:
    root = repo_root or ROOT
    missing: list[str] = []
    for rel in (
        "docs/reports/apps_rg/graph_skills_hardening_gap_inventory.json",
        "docs/reports/apps_rg/graph_skills_hardening_gap_inventory.md",
        "docs/reports/apps_rg/career_track_p1_w4_closeout_receipt.json",
        "docs/reports/apps_rg/career_track_p1_w5_track_balanced_sections_receipt.json",
    ):
        if not (root / rel).is_file():
            missing.append(rel)
    if missing:
        raise P2W0GapInventoryError(f"missing artifact files: {missing}")


def load_and_validate_inventory(*, repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or ROOT
    validate_p2_w0_artifact_files_exist(repo_root=root)
    payload = json.loads((root / "docs/reports/apps_rg/graph_skills_hardening_gap_inventory.json").read_text(encoding="utf-8"))
    validate_p2_w0_graph_skills_gap_inventory(payload)
    return payload


def main() -> None:
    payload = load_and_validate_inventory()
    print(
        json.dumps(
            {
                "status": "PASS",
                "wave": payload.get("wave"),
                "inventory_only": payload.get("inventory_only"),
                "p2_wave_target_count": len(payload.get("p2_wave_targets") or {}),
                "broad_skills_ledger_current_gap": not (
                    (payload.get("p2_w1a_supersession") or {}).get("gap_closed")
                ),
                "p2_w1a_superseded": bool((payload.get("p2_w1a_supersession") or {}).get("gap_closed")),
                "live_competencies_x3_allow_claimed": payload.get("live_competencies_x3_allow_claimed"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
