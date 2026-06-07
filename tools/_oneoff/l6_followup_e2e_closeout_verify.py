"""Follow-up plan E2E verifier — l6-reorg-deferred-followup-f3a9c2."""
from __future__ import annotations

import importlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAN_ID = "l6-reorg-deferred-followup-f3a9c2"
RECEIPT = REPO / "docs/reports/cursor/l6_followup_plan_e2e_closeout_20260525.json"


def main() -> int:
    failures: list[str] = []
    results: dict[str, str] = {}

    def check(name: str, ok: bool, detail: str = "") -> None:
        results[name] = "PASS" if ok else "FAIL"
        tag = "PASS" if ok else "FAIL"
        print(f"[{tag}] {name}" + (f" — {detail}" if detail and not ok else ""))
        if not ok:
            failures.append(f"{name}: {detail}")

    # Parent structural + governance bundle
    p = subprocess.run(
        [sys.executable, "tools/_oneoff/l6_e2e_closeout_verify.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    parent_ok = p.returncode == 0
    check("parent_l6_e2e_closeout", parent_ok, (p.stdout or p.stderr)[-500:])

    # W0 reconcile
    w0 = subprocess.run(
        [sys.executable, "tools/_oneoff/l6_followup_w0_reconcile.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    w0_ok = w0.returncode == 0
    check("w0_inventory_yaml_reconcile", w0_ok, (w0.stdout or w0.stderr)[-300:])

    # Arch exceptions gate
    arch = subprocess.run(
        [sys.executable, "ops_scripts/ci/check_l6_architectural_exceptions.py"],
        cwd=REPO,
        env={**__import__("os").environ, "L6_ARCH_EXCEPTIONS_FAIL_CLOSED": "1"},
        capture_output=True,
        text=True,
        timeout=60,
    )
    check("gate_l6_arch_exceptions", arch.returncode == 0, (arch.stdout or arch.stderr)[-300:])

    artifacts = [
        "docs/architecture/adr/ADR-086-l6-eval-surface-consolidation.md",
        "docs/architecture/adr/ADR-087-l6-passive-layout-followup.md",
        "docs/architecture/adr/ADR-088-l6-category-a-shared-permanent-exception.md",
        "docs/reports/cursor/l6_w6_gravity_edge_inventory_fresh.json",
        "docs/reports/cursor/l6_followup_deferred_closeout_20260525.json",
        "agentic_core/_shared/types/README.md",
        "agentic_core/L6_observability/shadow_eval/legacy_parallel/README.md",
        "agentic_core/L6_observability/shadow_eval/legacy_parallel/shadow_eval_pipeline.py",
        "docs/reports/cursor/l6_adr086_m3_closeout_20260525.json",
        "agentic_core/L6_system_learning/promotion/generic_l6_profile_consumer.py",
        "agentic_core/L6_system_learning/engines/README.md",
        "docs/reports/cursor/l6_category_a_shared_spike_20260525.md",
        "docs/reports/cursor/l6_followup_w1_w4_batch_receipt_20260525.json",
        "docs/reports/cursor/l6_reorg_deferred_scope_register_20260525.md",
        ".claude/plans/l6-reorg-deferred-followup-f3a9c2.md",
        "docs/reports/cursor/l6_followup_w0_reconcile_20260525.json",
    ]
    for rel in artifacts:
        check(f"artifact:{rel}", (REPO / rel).is_file())

    check(
        "no_passive_promotion_dir",
        not (REPO / "agentic_core/L6_observability/promotion").exists(),
    )
    check(
        "runtime_trace_otel_impl",
        (REPO / "agentic_core/L6_observability/runtime_trace/otel_runtime_ingest.py").is_file(),
    )

    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))

    imports = [
        "agentic_core.L6_system_learning.promotion.generic_l6_profile_consumer",
        "agentic_core.L6_observability.otel_runtime_ingest",
        "agentic_core.L6_observability.runtime_trace.otel_runtime_ingest",
        "agentic_core.L6_observability.utils.evaluation.async_eval_packet",
        "ops_scripts.reports.async_eval_packet",
        "ops_scripts.reports.governed_handoff",
        "ops_scripts.reports.desk_d_governed_board",
    ]
    for mod in imports:
        try:
            importlib.import_module(mod)
            check(f"import:{mod}", True)
        except Exception as exc:
            check(f"import:{mod}", False, str(exc))

    otel_py = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/unit/agentic_core/L6_observability/test_otel_runtime_ingest.py",
            "tests/unit/agentic_core/L6_observability/test_heal_router_otel.py",
            "-q",
            "-o",
            "addopts=",
        ],
        cwd=REPO,
        env={**__import__("os").environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        capture_output=True,
        text=True,
        timeout=300,
    )
    check("pytest_otel_followup", otel_py.returncode == 0, (otel_py.stdout or otel_py.stderr)[-400:])

    plan_text = (REPO / ".claude/plans/l6-reorg-deferred-followup-f3a9c2.md").read_text(encoding="utf-8")
    check("plan_status_done", "PLAN_STATUS: DONE" in plan_text)
    check("plan_wave_complete", "CURRENT_WAVE: COMPLETE" in plan_text)

    receipt = {
        "plan_id": PLAN_ID,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "checks_total": len(results),
        "checks_pass": sum(1 for v in results.values() if v == "PASS"),
        "checks_fail": len(failures),
        "results": results,
        "failures": failures,
        "parent_e2e": "tools/_oneoff/l6_e2e_closeout_verify.py",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("---")
    if failures:
        print(f"FOLLOWUP_E2E: FAIL ({len(failures)} checks)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"FOLLOWUP_E2E: PASS ({receipt['checks_pass']}/{receipt['checks_total']} checks)")
    print(f"Receipt: {RECEIPT.relative_to(REPO).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
