"""Emit no_agentic_core_diff_receipt.json for plan closeout (H-9)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PLAN_SCOPE_PREFIXES: tuple[str, ...] = (
    "apps_rg/runtime/sections/executive_summary_",
    "apps_rg/runtime/sections/executive_summary_candidate_pool.py",
    "apps_rg/runtime/sections/executive_summary_regen_delta_policy.py",
    "tests/unit/apps_rg/test_executive_summary_g1_ledger_metric_sync.py",
    "tests/unit/apps_rg/test_executive_summary_candidate_pool.py",
    "tests/unit/apps_rg/test_executive_summary_regen_delta_policy.py",
    "tests/unit/apps_rg/test_executive_summary_judge_remediation.py",
    "tests/unit/apps_rg/test_executive_summary_judge_regen_loop.py",
    "tools/cursor/run_exec_summary_floor_matrix.py",
    "tools/cursor/verify_exec_summary_judge_regen_w5_artifacts.py",
    "tools/cursor/emit_no_agentic_core_diff_receipt.py",
    "docs/reports/cursor/exec_summary_judge_regen_control_loop_",
    ".claude/plans/exec-summary-judge-regen-control-loop-f8a3c2.md",
)


def _git_changed_paths() -> list[str]:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    lines: list[str] = []
    for raw in (proc.stdout or "").splitlines():
        if len(raw) < 4:
            continue
        path = raw[3:].strip().replace("\\", "/")
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if path:
            lines.append(path)
    return lines


def _in_plan_scope(path: str) -> bool:
    return any(path.startswith(prefix) or path == prefix.rstrip("/") for prefix in PLAN_SCOPE_PREFIXES)


def main() -> int:
    all_changed = _git_changed_paths()
    agentic_core = sorted(p for p in all_changed if p.startswith("agentic_core/"))
    plan_scope = sorted(p for p in all_changed if _in_plan_scope(p))
    receipt = {
        "schema": "no_agentic_core_diff_receipt_v1",
        "plan_id": "exec-summary-judge-regen-control-loop-f8a3c2",
        "verified_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agentic_core_files_changed": agentic_core,
        "agentic_core_diff_count": len(agentic_core),
        "plan_scope_files_changed": plan_scope,
        "plan_scope_diff_count": len(plan_scope),
        "passed": len(agentic_core) == 0,
    }
    out = ROOT / "docs/reports/cursor/no_agentic_core_diff_receipt.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
