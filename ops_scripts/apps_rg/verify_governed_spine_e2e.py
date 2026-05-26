"""Post-run verifier — apps_rg governed spine (section lane or integrated R4).

Asserts U0→L1→L0 binding, governed C0/PA/L2/Exit, and no product shadow bypasses.

Usage:
    python ops_scripts/apps_rg/verify_governed_spine_e2e.py --section-dir <artifact_dir>
    python ops_scripts/apps_rg/verify_governed_spine_e2e.py --integrated-dir <run_dir>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

SECTION_REQUIRED = (
    "validated_request.json",
    "l1_plan_contract.json",
    "route_contract.json",
    "section_front_spine_receipt.json",
    "c0_evidence_room_receipt.json",
    "section_spine_c0_retrieve_receipt.json",
    "compiled_prompt_artifact.json",
    "sealed_l2_artifact.json",
    "exit_spine_receipt.json",
    "exit_disposition_receipt.json",
    "x3_disposition.json",
    "runtime_exhaust_bundle.json",
    "spine_span_emit_receipt.jsonl",
)

C0_ROOM_ARTIFACTS = (
    "c01_retrieval_plan.json",
    "c02_atoms.json",
    "c02_vector_query.json",
)


def _load(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and isinstance(raw.get("payload"), dict):
            return raw["payload"]
        return raw if isinstance(raw, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def verify_section_run(artifact_dir: Path) -> dict[str, Any]:
    errors: list[str] = []
    artifact_dir = artifact_dir.resolve()
    if not artifact_dir.is_dir():
        return {"status": "FAIL", "mode": "section", "errors": [f"missing dir {artifact_dir}"]}

    for name in SECTION_REQUIRED:
        if not (artifact_dir / name).is_file():
            _fail(errors, f"missing_required:{name}")

    for name in C0_ROOM_ARTIFACTS:
        if not (artifact_dir / name).is_file():
            _fail(errors, f"missing_c0_room:{name}")

    front = _load(artifact_dir / "section_front_spine_receipt.json") or {}
    if not front.get("u0_runtime_package_ingested"):
        _fail(errors, "u0_runtime_package_ingested_false")
    if front.get("fixture_dev_only_bypass"):
        _fail(errors, "fixture_dev_only_bypass_true")
    if front.get("product_visible") is False:
        _fail(errors, "product_visible_false")
    downstream = front.get("downstream_classification") or {}
    if downstream.get("is_second_spine"):
        _fail(errors, "is_second_spine_true")
    chain = downstream.get("observed_chain") or front.get("observed_chain") or []
    for stage in ("U0", "L1", "L0", "section_PA", "section_L2", "section_X3"):
        if stage not in chain:
            _fail(errors, f"observed_chain_missing:{stage}")

    l1 = _load(artifact_dir / "l1_plan_contract.json") or {}
    route = _load(artifact_dir / "route_contract.json") or {}
    if l1.get("grounding_required") is not True:
        _fail(errors, f"l1_grounding_required={l1.get('grounding_required')!r}")
    if route.get("grounding_required") is not True:
        _fail(errors, f"route_grounding_required={route.get('grounding_required')!r}")

    vr = _load(artifact_dir / "validated_request.json") or {}
    app_payload = vr.get("app_payload") if isinstance(vr.get("app_payload"), dict) else {}
    from apps_rg.runtime.bindings.briefing_u0_signals import briefing_supplied_at_u0

    briefing_supplied = briefing_supplied_at_u0(app_payload)

    payload = _load(artifact_dir / "runtime_payload.json") or {}
    if payload.get("raw_proof_pool_direct_to_pa") is True:
        _fail(errors, "raw_proof_pool_direct_to_pa_true")

    c0_room = _load(artifact_dir / "c0_evidence_room_receipt.json") or {}
    bridge = c0_room.get("bridge_doc") or c0_room
    c07 = (bridge.get("c0_evidence_room") or {}).get("c07") or c0_room.get("c07") or {}
    handoff_safe = c07.get("handoff_safe") if isinstance(c07, dict) else bridge.get("c07_handoff_safe")
    if handoff_safe is False:
        _fail(errors, "c07_handoff_safe_false")

    spine_c0 = _load(artifact_dir / "section_spine_c0_retrieve_receipt.json") or {}
    if not spine_c0.get("canonical_c0_2_dense_claimed"):
        _fail(errors, "spine_c0_dense_not_claimed")

    x3 = _load(artifact_dir / "x3_disposition.json") or {}
    code = str(x3.get("x3_code") or x3.get("disposition") or "")
    if code.startswith("X3_BLOCK") or code.startswith("BLOCK"):
        _fail(errors, f"x3_blocked:{code}")

    exit_spine = _load(artifact_dir / "exit_spine_receipt.json") or {}
    exit_chain = exit_spine.get("observed_chain") or []
    for stage in ("U0", "L1", "L0", "c0_retrieve_apps_rg", "pa_compose_apps_rg", "l2_execute_apps_rg"):
        if stage not in exit_chain:
            _fail(errors, f"exit_spine_chain_missing:{stage}")

    bundle = _load(artifact_dir / "section_runtime_proof_bundle.json") or {}
    if bundle.get("certified") is True:
        _fail(errors, "section_run_falsely_certified_full_l7")

    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "mode": "section",
        "artifact_dir": str(artifact_dir).replace("\\", "/"),
        "section_id": front.get("section_id") or payload.get("section_id"),
        "grounding_required": l1.get("grounding_required"),
        "apps_research_call_required": l1.get("apps_research_call_required"),
        "briefing_supplied_at_u0": briefing_supplied,
        "observed_chain": chain,
        "x3_code": code,
        "pipeline_quality_allow": code in ("X3_ALLOW", "ALLOW"),
        "errors": errors,
    }


def verify_integrated_run(run_dir: Path) -> dict[str, Any]:
    from apps_rg.runtime.integrated_product_proof_gate import validate_integrated_product_proof

    run_dir = run_dir.resolve()
    result = validate_integrated_product_proof(run_dir)
    out: dict[str, Any] = {
        "status": result.status,
        "mode": "integrated",
        "run_dir": str(run_dir).replace("\\", "/"),
        "decisive_reason": result.decisive_reason,
        "integrated_r4_invoked": result.integrated_r4_invoked,
        "canonical_entrypoint": result.canonical_entrypoint,
        "section_mode": result.section_mode,
        "required_artifacts_missing": result.required_artifacts_missing,
        "no_bypass_assertions_present": result.no_bypass_assertions_present,
        "errors": [],
    }
    if result.status != "PASS":
        out["errors"].append(result.decisive_reason or f"integrated_gate_{result.status}")
    if not result.integrated_r4_invoked:
        out["errors"].append("integrated_r4_not_invoked")
    if result.section_mode:
        out["errors"].append("integrated_dir_is_section_mode")
    route_path = None
    for p in run_dir.rglob("route_contract.json"):
        route_path = p
        break
    route = _load(route_path) if route_path else {}
    if route.get("grounding_required") is not True:
        out["errors"].append(f"route_grounding_required={route.get('grounding_required')!r}")
    if out["errors"]:
        out["status"] = "FAIL"
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify apps_rg governed spine E2E artifacts")
    parser.add_argument("--section-dir", type=Path, default=None)
    parser.add_argument("--integrated-dir", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args(argv)

    if bool(args.section_dir) == bool(args.integrated_dir):
        print("Specify exactly one of --section-dir or --integrated-dir", file=sys.stderr)
        return 2

    if args.section_dir:
        report = verify_section_run(args.section_dir)
    else:
        report = verify_integrated_run(args.integrated_dir)

    text = json.dumps(report, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text)
    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
