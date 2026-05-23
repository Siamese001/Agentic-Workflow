#!/usr/bin/env python3
"""Build Wave 3 redo report from runtime executive_summary artifact directory."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
OUT_DIR = REPO / "docs/reports/apps_rg"


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def _capture_fail_closed_proof() -> dict[str, Any]:
    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool
    from apps_rg.runtime.spine.front_contracts import SectionFrontSpinePreconditionError

    try:
        resolve_section_proof_pool(section="competencies", repo_root=REPO, product_visible=True)
        return {"raised": False, "error_type": "", "message": ""}
    except SectionFrontSpinePreconditionError as exc:
        return {"raised": True, "error_type": type(exc).__name__, "message": str(exc)}
    except Exception as exc:
        return {"raised": True, "error_type": type(exc).__name__, "message": str(exc)}


def build_redo_report(artifact_root: Path, *, runtime_command: str, runtime_exit: int) -> dict[str, Any]:
    ts = datetime.now(timezone.utc).isoformat()
    root = artifact_root.resolve()
    files = {
        "validated_request": root / "validated_request.json",
        "l1_plan_contract": root / "l1_plan_contract.json",
        "route_contract": root / "route_contract.json",
        "section_front_spine_receipt": root / "section_front_spine_receipt.json",
        "runtime_payload": root / "runtime_payload.json",
        "x2_source_fact_pool_receipt": root / "x2_source_fact_pool_receipt.json",
    }
    vr = _load(files["validated_request"])
    l1 = _load(files["l1_plan_contract"])
    route = _load(files["route_contract"])
    receipt = _load(files["section_front_spine_receipt"])
    payload = _load(files["runtime_payload"])
    pool_rcpt = _load(files["x2_source_fact_pool_receipt"])

    request_id = str(vr.get("request_id") or vr.get("payload", {}).get("request_id") or "")
    run_id = str(vr.get("run_id") or vr.get("payload", {}).get("run_id") or root.name)

    fail_closed = _capture_fail_closed_proof()
    blocked_proof_path = OUT_DIR / "section_front_spine_precondition_blocked_proof.json"
    blocked_proof_path.write_text(
        json.dumps(
            {
                "schema_version": "section_front_spine_precondition_blocked_proof_v1",
                "generated_at_utc": ts,
                "product_visible": True,
                "fixture_dev_only": False,
                "non_product_certified": False,
                **fail_closed,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    def row(
        claim: str,
        artifact_key: str,
        fields: list[str],
        expected: str,
        actual: str,
        status: str,
    ) -> dict[str, str]:
        apath = _rel(files[artifact_key]) if artifact_key in files and files[artifact_key].is_file() else (
            _rel(blocked_proof_path) if artifact_key == "blocked_proof" else "MISSING"
        )
        return {
            "claim": claim,
            "runtime_command": runtime_command,
            "artifact_path": apath,
            "fields_inspected": ", ".join(fields),
            "expected": expected,
            "actual": actual,
            "status": status,
        }

    pre = receipt.get("proof_pool_preconditions") or {}
    pp_pre = payload.get("proof_pool_front_spine_preconditions") or {}
    matrix: list[dict[str, str]] = []

    matrix.append(
        row(
            "1. Product-visible run emitted ValidatedRequest",
            "validated_request",
            ["contract_type", "producer_stage", "consumer_stage", "validation_status"],
            "ValidatedRequest / U0 / L1 / validation_status PASS",
            f"{vr.get('contract_type')} / {vr.get('producer_stage')} / {vr.get('consumer_stage')} / {vr.get('validation_status')}",
            "PASS"
            if vr.get("contract_type") == "ValidatedRequest"
            and vr.get("producer_stage") == "U0"
            and vr.get("validation_status") == "PASS"
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "2. Product-visible run emitted L1PlanContract",
            "l1_plan_contract",
            ["contract_type", "producer_stage", "consumer_stage", "validated_request_ref", "parent_contract_ref"],
            "L1PlanContract / L1 / L0 / refs to ValidatedRequest",
            f"{l1.get('contract_type')} / {l1.get('producer_stage')} / {l1.get('consumer_stage')} / {l1.get('validated_request_ref')} / parent={l1.get('parent_contract_ref', '')[:8]}…",
            "PASS"
            if l1.get("contract_type") == "L1PlanContract"
            and l1.get("validated_request_ref") == "validated_request.json"
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "3. Product-visible run emitted RouteContract",
            "route_contract",
            [
                "contract_type",
                "producer_stage",
                "consumer_stage",
                "l1_plan_contract_ref",
                "grounding_required",
                "execution_form",
            ],
            "RouteContract / L0 / section_lane_modular / l1 ref / grounding+execution_form",
            f"{route.get('contract_type')} / {route.get('producer_stage')} / {route.get('consumer_stage')} / {route.get('l1_plan_contract_ref')} / gr={route.get('grounding_required')} / ef={route.get('execution_form')}",
            "PASS"
            if route.get("contract_type") == "RouteContract"
            and route.get("l1_plan_contract_ref") == "l1_plan_contract.json"
            and route.get("execution_form")
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "4. proof_pool_resolver ran only after front-spine preconditions",
            "section_front_spine_receipt",
            [
                "precondition_status",
                "validated_request_ref",
                "l1_plan_contract_ref",
                "route_contract_ref",
                "proof_pool_entry_allowed",
            ],
            "precondition PASS + refs + proof_pool_entry_allowed true",
            f"precond={receipt.get('precondition_status')}; entry_allowed={receipt.get('proof_pool_entry_allowed')}; payload_precond={pp_pre.get('precondition_status')}",
            "PASS"
            if receipt.get("precondition_status") == "PASS"
            and receipt.get("proof_pool_entry_allowed") is True
            and pp_pre.get("proof_pool_entry_allowed") is True
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "5. Product-visible bypass blocked without front spine",
            "blocked_proof",
            ["raised", "error_type", "message"],
            "SectionFrontSpinePreconditionError raised",
            f"raised={fail_closed.get('raised')}; type={fail_closed.get('error_type')}",
            "PASS"
            if fail_closed.get("raised") and fail_closed.get("error_type") == "SectionFrontSpinePreconditionError"
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "6. Fixture/dev bypass non-product-certified on product run",
            "section_front_spine_receipt",
            ["fixture_dev_only", "non_product_certified", "product_certification"],
            "fixture_dev_only false; non_product_certified false; NOT_CLAIMED",
            f"fixture_dev_only={receipt.get('fixture_dev_only')}; non_product_certified={receipt.get('non_product_certified')}; cert={receipt.get('product_certification')}",
            "PASS"
            if receipt.get("fixture_dev_only") is False
            and receipt.get("non_product_certified") is False
            and receipt.get("product_certification") == "NOT_CLAIMED"
            else "FAIL",
        )
    )
    matrix.append(
        row(
            "7. Downstream remains non-claimed",
            "section_front_spine_receipt",
            ["spine_mode", "canonical_c0_claimed", "canonical_exit_claimed", "product_certification"],
            "section_lane_modular; c0/exit false; NOT_CLAIMED",
            f"spine_mode={receipt.get('spine_mode')}; c0={receipt.get('canonical_c0_claimed')}; exit={receipt.get('canonical_exit_claimed')}; cert={receipt.get('product_certification')}",
            "PASS"
            if receipt.get("spine_mode") == "section_lane_modular"
            and receipt.get("canonical_c0_claimed") is False
            and receipt.get("canonical_exit_claimed") is False
            else "FAIL",
        )
    )

    all_pass = all(r["status"] == "PASS" for r in matrix) and runtime_exit == 0
    required_present = all(files[k].is_file() for k in ("validated_request", "l1_plan_contract", "route_contract", "section_front_spine_receipt"))

    return {
        "schema_version": "one_spine_front_bridge_w3_redo_v1",
        "generated_at_utc": ts,
        "plan_slug": "one-canonical-spine",
        "wave": "3-redo",
        "status": "PASS" if all_pass and required_present else ("PARTIAL" if required_present else "FAIL"),
        "runtime_command": runtime_command,
        "runtime_exit_code": runtime_exit,
        "artifact_root": _rel(root),
        "run_dir": root.name,
        "run_id": run_id,
        "request_id": request_id,
        "artifact_file_list": sorted(p.name for p in root.iterdir() if p.is_file()),
        "precondition_blocked_proof_artifact": _rel(blocked_proof_path),
        "artifact_proof_matrix": matrix,
        "explicit_non_claims": receipt.get("explicit_non_claims") or [],
        "not_proven_claims": [
            "full tests/_apps_contract suite",
            "canonical C0/PA/L2/Exit migration",
            "product certification / release signoff",
            "proof_eligible as durable-write authorization",
        ],
        "blockers": [] if required_present else ["required front-spine artifact files missing"],
    }


def _md(doc: dict[str, Any]) -> str:
    lines = [
        "# One-spine front bridge Wave 3 redo (runtime artifact proof)",
        "",
        f"Generated: {doc['generated_at_utc']}",
        f"**STATUS: {doc['status']}**",
        "",
        f"**Runtime command:** `{doc['runtime_command']}` (exit {doc['runtime_exit_code']})",
        "",
        f"**ARTIFACT_ROOT:** `{doc['artifact_root']}`",
        f"**RUN_DIR:** `{doc['run_dir']}`",
        "",
        "## ARTIFACT_PROOF_MATRIX",
        "",
        "| Claim | Artifact | Fields | Expected | Actual | Status |",
        "|-------|----------|--------|----------|--------|--------|",
    ]
    for r in doc["artifact_proof_matrix"]:
        lines.append(
            f"| {r['claim']} | `{r['artifact_path']}` | {r['fields_inspected']} | "
            f"{r['expected']} | {r['actual']} | **{r['status']}** |"
        )
    lines.extend(["", "## Explicit non-claims", ""])
    for c in doc.get("explicit_non_claims", []):
        lines.append(f"- {c}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: emit_one_spine_front_bridge_w3_redo.py <artifact_root> [exit_code] [runtime_command...]", file=sys.stderr)
        return 2
    root = Path(sys.argv[1])
    exit_code = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    cmd = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else (
        "python -m apps_rg --section executive_summary --allow-non-allow-exit-zero"
    )
    if not root.is_dir():
        print(f"artifact root not found: {root}", file=sys.stderr)
        return 2
    doc = build_redo_report(root, runtime_command=cmd, runtime_exit=exit_code)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "one_spine_front_bridge_w3_redo.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "one_spine_front_bridge_w3_redo.md").write_text(_md(doc), encoding="utf-8")
    print(json.dumps({"status": doc["status"], "artifact_root": doc["artifact_root"]}, indent=2))
    return 0 if doc["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
