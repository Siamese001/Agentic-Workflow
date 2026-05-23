"""APPS-RG-SPINE-CONVERGENCE — W8 CI ratchet (plan pa-exec-flowchart-gap-f2a8c3).

Verifies governed spine seams (W5–W7), span checklist SSOT, dual-path gate, and
refreshes spine REQ gap audit JSON.

Fail-closed by default. Bypass: APPS_RG_SPINE_CONVERGENCE_BYPASS=1
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

REPORT_JSON = REPO_ROOT / "artifacts" / "ci" / "apps_rg_spine_convergence_w8_gate.json"
SPAN_CHECKLIST_JSON = REPO_ROOT / "artifacts" / "apps_rg" / "plans" / "apps_rg_spine_span_checklist.json"

BINDING_CHECKS: tuple[tuple[str, str], ...] = (
    ("apps_rg/runtime/bindings/pa_binding.py", "governed_pa_compose_integrated"),
    ("apps_rg/runtime/bindings/l2_binding_adapter.py", "governed_l2_seal_integrated"),
    ("apps_rg/runtime/bindings/exit_binding.py", "governed_exit_finalize_integrated"),
    ("apps_rg/runtime/shadow/l6_handoff_packet.py", "assert_l6_shadow_ingest_preconditions"),
    ("apps_rg/runtime/spine/section_c0_retrieve.py", "c0_retrieve_apps_rg"),
    ("apps_rg/runtime/spine/governed_pa_compose.py", "assemble_prompt"),
    ("apps_rg/runtime/spine/governed_l2_exit_compose.py", "ExitEvalPipeline"),
    ("apps_rg/runtime/spine/governed_l6_shadow_compose.py", "ingest_integrated_exhaust_for_l6_shadow"),
)

REQUIRED_MODULES: tuple[str, ...] = (
    "apps_rg/runtime/spine/governed_pa_compose.py",
    "apps_rg/runtime/spine/governed_l2_exit_compose.py",
    "apps_rg/runtime/spine/governed_l6_shadow_compose.py",
    "apps_rg/runtime/spine/spine_span_emit.py",
    "tests/_apps_contract/test_apps_rg_spine_harden_edge_cases.py",
    "apps_rg/runtime/spine/c0_graph_lane_receipt.py",
    "apps_rg/runtime/spine/l6_eval_before_learn_receipt.py",
    "ops_scripts/ci/check_apps_rg_spine_span_emit_sites.py",
    "ops_scripts/apps_rg/live_section_spine_smoke_all_lanes.py",
    "tests/_apps_contract/test_apps_rg_spine_waves_w4_w7.py",
    "apps_rg/runtime/spine/spine_contract_loaders.py",
    "apps_rg/runtime/spine/l2_handoff_receipt.py",
    "apps_rg/config/domain_contract/L6_eval_before_learn_scope.md",
    "apps_rg/config/domain_contract/C0_graph_lane_deferral.md",
)


def _errors_from_binding_checks() -> list[str]:
    errs: list[str] = []
    for rel, needle in BINDING_CHECKS:
        path = REPO_ROOT / rel.replace("/", os.sep)
        if not path.is_file():
            errs.append(f"MISSING_FILE {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if needle not in text:
            errs.append(f"MISSING_WIRING {rel} expected {needle!r}")
    for rel in REQUIRED_MODULES:
        if not (REPO_ROOT / rel.replace("/", os.sep)).is_file():
            errs.append(f"MISSING_MODULE {rel}")
    return errs


def _emit_span_checklist() -> None:
    from system_learning.runtime_adg.span_contracts import apps_rg_spine_span_checklist_report

    report = apps_rg_spine_span_checklist_report()
    SPAN_CHECKLIST_JSON.parent.mkdir(parents=True, exist_ok=True)
    SPAN_CHECKLIST_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def _run_gap_audit() -> dict[str, object]:
    script = REPO_ROOT / "ops_scripts" / "apps_rg" / "apps_rg_spine_req_gap_audit.py"
    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"apps_rg_spine_req_gap_audit failed: {completed.stderr[-500:]}"
        )
    audit_path = REPO_ROOT / "artifacts" / "apps_rg" / "plans" / "apps_rg_spine_req_gap_audit.json"
    return json.loads(audit_path.read_text(encoding="utf-8"))


def _run_single_spine_gate() -> int:
    gate = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_single_spine.py"
    env = dict(os.environ)
    env.pop("APPS_RG_SINGLE_SPINE_GATE_BYPASS", None)
    env.pop("APPS_RG_SINGLE_SPINE_GATE_ADVISORY", None)
    completed = subprocess.run(
        [sys.executable, str(gate)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env=env,
    )
    return int(completed.returncode)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="apps_rg spine convergence W8 gate")
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args(argv)

    if os.environ.get("APPS_RG_SPINE_CONVERGENCE_BYPASS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        print("[APPS-RG-SPINE-CONVERGENCE] BYPASS")
        REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
        REPORT_JSON.write_text(json.dumps({"status": "BYPASS"}, indent=2), encoding="utf-8")
        return 0

    errors = _errors_from_binding_checks()
    _emit_span_checklist()
    audit: dict[str, object] = {}
    try:
        audit = _run_gap_audit()
    except Exception as exc:  # guardian: allow-broad-exception -- CI gate must surface audit failure
        errors.append(f"GAP_AUDIT_FAILED {exc}")

    if int(audit.get("p0_count", 99)) != 0:
        errors.append(f"SPINE_GAP_AUDIT_P0_OPEN count={audit.get('p0_count')}")

    spine_rc = _run_single_spine_gate()
    if spine_rc != 0:
        errors.append(f"SINGLE_SPINE_GATE exit={spine_rc}")

    span_sites = REPO_ROOT / "ops_scripts" / "ci" / "check_apps_rg_spine_span_emit_sites.py"
    span_rc = subprocess.run(
        [sys.executable, str(span_sites)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    ).returncode
    if span_rc != 0:
        errors.append(f"SPAN_EMIT_SITES_GATE exit={span_rc}")

    status = "PASS" if not errors else "FAIL"
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(
            {
                "gate": "APPS-RG-SPINE-CONVERGENCE",
                "plan_id": "pa-exec-flowchart-gap-f2a8c3",
                "wave": "W8",
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "status": status,
                "errors": errors,
                "spine_gap_audit": {
                    "p0_count": audit.get("p0_count"),
                    "p0_partial_count": audit.get("p0_partial_count"),
                    "convergence_status": audit.get("convergence_status"),
                },
                "span_checklist_artifact": str(SPAN_CHECKLIST_JSON.relative_to(REPO_ROOT)).replace(
                    "\\", "/"
                ),
                "proof_classification": "CI_STATIC_CONTRACT_SCAN",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    for err in errors:
        print(f"[APPS-RG-SPINE-CONVERGENCE] {err}")

    if args.report_only:
        return 0
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
