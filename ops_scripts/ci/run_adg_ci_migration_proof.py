#!/usr/bin/env python3
"""One-shot proof bundle for adg-ci-unified-migration-a7f3b2 (all scope)."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

RECEIPT = REPO_ROOT / "docs/reports/cursor/adg_ci_unified_migration_receipt.json"


def _run(cmd: list[str], *, timeout: int = 7200) -> dict[str, object]:
    try:
        proc = subprocess.run(  # noqa: S603
            cmd,
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "cmd": " ".join(cmd),
            "exit_code": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-800:],
            "stderr_tail": (proc.stderr or "")[-800:],
        }
    except subprocess.TimeoutExpired:
        return {"cmd": " ".join(cmd), "exit_code": 124, "stdout_tail": "", "stderr_tail": "timeout"}


def main() -> int:
    steps: list[dict[str, object]] = []
    py = sys.executable

    steps.append(
        _run(
            [py, "-m", "pytest", "tests/unit/ops_scripts/ci/test_adg_enforcement_report.py",
             "tests/unit/ops_scripts/ci/test_check_adg_certified_rollup.py",
             "tests/unit/ops_scripts/ci/test_adg_three_graph_negative_fixtures.py",
             "tests/unit/tools_adg/test_run_full_adg_audit.py", "-q", "--tb=line"],
            timeout=600,
        )
    )
    steps.append(_run([py, "ops_scripts/ci/check_consumer_mode_declared.py"], timeout=300))
    steps.append(_run([py, "ops_scripts/ci/run_adg_three_graph_quick_gate.py"], timeout=900))

    cert = _run(
        [py, "tools/adg/run_full_adg_audit.py", "--mode", "certification", "--format", "both"],
        timeout=7200,
    )
    steps.append(cert)

    enforcement = REPO_ROOT / "artifacts/adg/adg_enforcement_report_latest.json"
    receipt = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plan_id": "adg-ci-unified-migration-a7f3b2",
        "steps": steps,
        "enforcement_report": str(enforcement) if enforcement.is_file() else None,
        "certification_status": "clean" if cert.get("exit_code") == 0 else "failed",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if all(int(s.get("exit_code", 1)) == 0 for s in steps[:3]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
