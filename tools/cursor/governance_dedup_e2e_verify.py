#!/usr/bin/env python3
"""E2E verification for governance-dedup-closeout-e8a4c2 (W0–W5)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

GATES: list[tuple[str, list[str]]] = [
    ("check_ag_hook_wiring", ["python", "ops_scripts/ci/check_ag_hook_wiring.py"]),
    ("check_agents_md_sync", ["python", "ops_scripts/ci/check_agents_md_sync.py"]),
    ("check_cursor_optimized_config", ["python", ".claude/governance/scripts/check_cursor_optimized_config.py"]),
    ("generate_rules_index_check", ["python", ".claude/governance/scripts/generate_rules_index.py", "--check"]),
    ("check_always_on_token_budget", ["python", "ops_scripts/ci/check_always_on_token_budget.py"]),
    (
        "check_cursor_native_config_strict",
        ["python", ".claude/governance/scripts/check_cursor_native_config.py", "--strict"],
    ),
    (
        "governance_w3_hook_audit_matrix",
        ["python", "ops_scripts/ci/governance_w3_hook_audit_matrix.py", "--check"],
    ),
]

REQUIRED_PATHS = [
    "docs/reports/cursor/governance_dedup_closeout_receipt.json",
    "docs/reports/cursor/governance_dedup_closeout_receipt.md",
    "docs/reports/cursor/governance_dedup_w0_receipt.json",
    "docs/reports/cursor/governance_dedup_w1_receipt.json",
    "docs/reports/cursor/governance_dedup_w2_receipt.json",
    "docs/reports/cursor/governance_dedup_w3_receipt.json",
    "docs/reports/cursor/governance_dedup_w4_receipt.json",
    "docs/reports/cursor/plan_sprawl_inventory_20260526.csv",
    "docs/reports/cursor/windsurf_always_on_demotion_map_20260526.md",
    ".cursor/hooks/after_agent_governance_dispatch.py",
    ".claude/plans/_archive/2026-05",
    "docs/reports/decommission/legacy_tree_classification_9f2c47.json",
]

CLOSEOUT_SLUG = "governance-dedup-closeout-e8a4c2"


def _run_gate(name: str, argv: list[str]) -> dict[str, object]:
    proc = subprocess.run(
        argv,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        shell=False,
    )
    return {
        "name": name,
        "argv": " ".join(argv),
        "exit_code": proc.returncode,
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "stderr_tail": (proc.stderr or "")[-500:],
    }


def _validate_closeout_manifest() -> list[str]:
    errors: list[str] = []
    path = REPO / "docs/reports/cursor/governance_dedup_closeout_receipt.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("plan_id") != CLOSEOUT_SLUG:
        errors.append(f"plan_id mismatch: {data.get('plan_id')}")
    if data.get("status") != "PASS":
        errors.append(f"closeout status not PASS: {data.get('status')}")
    waves = data.get("waves_completed") or []
    for w in ("W0", "W1", "W2", "W3", "W4", "W5"):
        if w not in waves:
            errors.append(f"missing wave in closeout: {w}")
    gaps = {g.get("gap_id"): g for g in data.get("deferred_items") or []}
    for gap_id in ("GAP-1", "GAP-2", "GAP-3", "GAP-4", "GAP-5", "GAP-6"):
        if gap_id not in gaps:
            errors.append(f"missing gap: {gap_id}")
    if gaps.get("GAP-4", {}).get("status") != "DEFERRED":
        errors.append("GAP-4 must be DEFERRED")
    metrics = data.get("final_metrics") or {}
    if metrics.get("active_plan_files_count", 99) > 20:
        errors.append(f"active_plan_files_count > 20: {metrics.get('active_plan_files_count')}")
    if metrics.get("windsurf_always_on_bytes", 1) != 0:
        errors.append(f"windsurf_always_on_bytes != 0: {metrics.get('windsurf_always_on_bytes')}")
    return errors


def _structural_checks() -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (REPO / rel).exists():
            errors.append(f"missing path: {rel}")
    hooks_json = REPO / ".cursor/hooks.json"
    if hooks_json.is_file():
        text = hooks_json.read_text(encoding="utf-8")
        if "after_agent_governance_dispatch.py" not in text:
            errors.append("hooks.json missing after_agent_governance_dispatch.py")
        if "after_agent_author_gate_audits.py" in text:
            errors.append("hooks.json still wires legacy after_agent_author_gate_audits.py")
    sys.path.insert(0, str(REPO / "ops_scripts" / "ci"))
    from governance_tier_measurement import scan_windsurf_always_on_md  # noqa: E402

    if scan_windsurf_always_on_md():
        errors.append("windsurf still has trigger: always_on files")
    plan_count = sum(
        1 for p in (REPO / ".claude/plans").iterdir() if p.is_file() and p.suffix == ".md"
    )
    if plan_count > 20:
        errors.append(f"top-level plan count {plan_count} > 20")
    return errors


def main() -> int:
    results: list[dict[str, object]] = []
    failures: list[str] = []

    for rel in REQUIRED_PATHS:
        ok = (REPO / rel).exists()
        results.append({"check": f"exists:{rel}", "status": "PASS" if ok else "FAIL"})
        if not ok:
            failures.append(f"missing: {rel}")

    manifest_errs = _validate_closeout_manifest()
    results.append(
        {
            "check": "closeout_manifest",
            "status": "PASS" if not manifest_errs else "FAIL",
            "errors": manifest_errs,
        }
    )
    failures.extend(manifest_errs)

    struct_errs = _structural_checks()
    results.append(
        {
            "check": "structural",
            "status": "PASS" if not struct_errs else "FAIL",
            "errors": struct_errs,
        }
    )
    failures.extend(struct_errs)

    for name, argv in GATES:
        gate = _run_gate(name, argv)
        results.append(gate)
        if gate["status"] != "PASS":
            failures.append(f"{name} exit {gate['exit_code']}")

    pytest_argv = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/ops_scripts/hooks/cursor/",
        "tests/unit/ops_scripts/ci/test_check_ag_hook_wiring.py",
        "-q",
        "-o",
        "addopts=",
    ]
    proc = subprocess.run(
        pytest_argv,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        shell=False,
        env={**dict(**{"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}), **dict(__import__("os").environ)},
    )
    results.append(
        {
            "name": "pytest_hooks_and_wiring",
            "exit_code": proc.returncode,
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "stdout_tail": (proc.stdout or "")[-400:],
        }
    )
    if proc.returncode != 0:
        failures.append(f"pytest exit {proc.returncode}")

    summary = {
        "plan_id": CLOSEOUT_SLUG,
        "e2e_status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "results": results,
    }
    out = REPO / "docs/reports/cursor/governance_dedup_e2e_verify_20260526.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
