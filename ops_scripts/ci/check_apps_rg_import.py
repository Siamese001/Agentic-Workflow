"""APPS-IMPORT CI gate — verify `python -m apps_rg --help` succeeds.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 W6 (DoD discipline).

This gate prevents the c8b3e1 failure mode: a plan was marked Completed
while `python -m apps_rg` raised ImportError on the first line of import
because dependencies had been quarantined without replacement. A `--help`
invocation is the cheapest possible "the entry point is reachable"
signal — it forces argparse to construct, which forces all module-level
imports of `apps_rg/__main__.py` to resolve.

Exit 0 → entry point importable + argparse OK.
Exit 1 → entry point broken (advisory by default, fail-closed via
APPS_RG_IMPORT_GATE_FAIL_CLOSED=1).
Bypass: APPS_RG_IMPORT_GATE_BYPASS=1.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REPORT_PATH = _REPO_ROOT / "artifacts" / "ci" / "apps_rg_import_gate.json"
_TIMEOUT_S = 30


def _emit_report(status: str, exit_code: int, stdout: str, stderr: str) -> None:
    _REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    _REPORT_PATH.write_text(
        json.dumps(
            {
                "gate": "APPS-IMPORT",
                "status": status,
                "subprocess_exit_code": exit_code,
                "stdout_tail": stdout[-2000:],
                "stderr_tail": stderr[-2000:],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    _ = argv
    if os.environ.get("APPS_RG_IMPORT_GATE_BYPASS", "").strip() in ("1", "true", "yes"):
        print("[APPS-IMPORT] BYPASS — APPS_RG_IMPORT_GATE_BYPASS=1")
        _emit_report("bypassed", 0, "", "")
        return 0

    fail_closed = os.environ.get("APPS_RG_IMPORT_GATE_FAIL_CLOSED", "").strip() in (
        "1",
        "true",
        "yes",
    )

    try:
        completed = subprocess.run(
            [sys.executable, "-m", "apps_rg", "--help"],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired:
        msg = f"`python -m apps_rg --help` timed out after {_TIMEOUT_S}s"
        print(f"[APPS-IMPORT] FAIL — {msg}")
        _emit_report("timeout", -1, "", msg)
        return 1 if fail_closed else 0
    except OSError as exc:
        msg = f"could not invoke subprocess: {exc}"
        print(f"[APPS-IMPORT] FAIL — {msg}")
        _emit_report("subprocess_error", -1, "", str(exc))
        return 1 if fail_closed else 0

    if completed.returncode == 0:
        print("[APPS-IMPORT] OK — `python -m apps_rg --help` exit 0")
        _emit_report("pass", 0, completed.stdout, completed.stderr)
        return 0

    print(
        f"[APPS-IMPORT] FAIL — `python -m apps_rg --help` exit {completed.returncode}"
    )
    print(f"  stderr tail:\n{completed.stderr[-1000:]}")
    _emit_report("fail", completed.returncode, completed.stdout, completed.stderr)
    return 1 if fail_closed else 0


if __name__ == "__main__":
    sys.exit(main())
