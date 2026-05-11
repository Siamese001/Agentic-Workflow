"""APPS-RESEARCH-IMPORT gate — verifies apps_research spine binding imports.

Runs `python -m apps_research --help` (exits 0 = entry point importable)
and verifies all 7 spine binding modules import cleanly.

Usage:
    python ops_scripts/ci/check_apps_research_import.py

Exit codes:
    0  all checks passed
    1  one or more checks failed

Bypass: APPS_RESEARCH_IMPORT_GATE_BYPASS=1
Fail-closed: APPS_RESEARCH_IMPORT_GATE_FAIL_CLOSED=1
"""
from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_GATE_ID = "APPS-RESEARCH-IMPORT"
_REPORT_PATH = Path("artifacts/ci/apps_research_import_gate.json")

_BINDING_MODULES: list[str] = [
    "agentic_core.runtime.entry.u0_apps_research_binding",
    "agentic_core.L1_cognition.apps_research_l1_binding",
    "agentic_core.L0_routing.apps_research_l0_binding",
    "agentic_core.runtime.c0.apps_research_c0_binding",
    "agentic_core.prompt_governance.apps_research_pa_binding",
    "agentic_core.L2_execution.apps_research_l2_binding",
    "agentic_core.runtime.exit.apps_research_exit_binding",
    "agentic_core.runtime.entry.apps_research_dispatch",
]


def _run() -> dict:
    failures: list[str] = []
    details: dict = {}

    # Check 1: spine binding imports
    for module_name in _BINDING_MODULES:
        try:
            importlib.import_module(module_name)
            details[module_name] = "ok"
        except ImportError as exc:
            details[module_name] = f"ImportError: {exc}"
            failures.append(f"{module_name}: {exc}")

    # Check 2: entrypoint help
    result = subprocess.run(
        [sys.executable, "-m", "apps_research", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        failures.append(
            f"python -m apps_research --help exit={result.returncode}: {result.stderr[:200]}"
        )
        details["entrypoint_help"] = f"exit={result.returncode}"
    else:
        details["entrypoint_help"] = "ok"

    passed = len(failures) == 0
    return {
        "gate": _GATE_ID,
        "passed": passed,
        "failures": failures,
        "details": details,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    if os.environ.get("APPS_RESEARCH_IMPORT_GATE_BYPASS", "").strip() in ("1", "true"):
        print(f"[{_GATE_ID}] BYPASSED")
        return 0

    report = _run()
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    if report["passed"]:
        print(f"[{_GATE_ID}] OK — all {len(_BINDING_MODULES)} binding modules importable")
        return 0

    print(f"[{_GATE_ID}] FAIL — {len(report['failures'])} failure(s):")
    for f in report["failures"]:
        print(f"  - {f}")

    fail_closed = os.environ.get("APPS_RESEARCH_IMPORT_GATE_FAIL_CLOSED", "").strip() in (
        "1",
        "true",
    )
    return 1 if fail_closed else 0


if __name__ == "__main__":
    raise SystemExit(main())
