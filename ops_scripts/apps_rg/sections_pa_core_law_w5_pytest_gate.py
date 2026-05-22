#!/usr/bin/env python3
"""W5 gate: run PA core-law drift + contract pytest rollup for sections rollout."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]

_W5_TEST_PATHS = [
    "tests/unit/apps_rg/test_exec_summary_prompt_drift_ratchet.py",
    "tests/unit/apps_rg/test_headline_prompt_drift_ratchet.py",
    "tests/unit/apps_rg/test_competencies_prompt_drift_ratchet.py",
    "tests/unit/apps_rg/test_unify_ibm_prompt_drift_ratchet.py",
    "tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w5_rollup.py",
    "tests/unit/apps_rg/prompt_assembly/test_sections_pa_core_law_w1.py",
    "tests/unit/apps_rg/prompt_assembly/test_pa_core_law_v1.py",
    "tests/unit/apps_rg/test_headline_tailor_v15_prompt_quality.py",
    "tests/_apps_contract/test_headline_pa_compiled_prompt.py",
    "tests/_apps_contract/test_competencies_pa_compiled_prompt.py",
    "tests/_apps_contract/test_unify_ibm_pa_compiled_prompt.py",
]


def main() -> int:
    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *_W5_TEST_PATHS,
        "-o",
        "addopts=",
        "-q",
        "--tb=short",
    ]
    proc = subprocess.run(cmd, cwd=_REPO, env=env, capture_output=True, text=True, timeout=300)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_dir = _REPO / "docs/reports/apps_rg"
    report_dir.mkdir(parents=True, exist_ok=True)
    md_path = report_dir / "sections_pa_core_law_rollout_w5_pytest_gate.md"
    body = (
        f"# Sections PA Core-Law — W5 Pytest Gate\n\n"
        f"**Generated:** {ts} (UTC)\n\n"
        f"**Exit code:** {proc.returncode}\n\n"
        f"## Command\n\n```bash\n{' '.join(cmd)}\n```\n\n"
        f"## Stdout\n\n```\n{proc.stdout[-8000:]}\n```\n\n"
    )
    if proc.stderr:
        body += f"## Stderr\n\n```\n{proc.stderr[-4000:]}\n```\n\n"
    body += "**Status:** " + ("PASS" if proc.returncode == 0 else "FAIL") + "\n"
    md_path.write_text(body, encoding="utf-8")
    print(proc.stdout)
    if proc.stderr:
        print(proc.stderr, file=sys.stderr)
    print(f"W5 gate report: {md_path}")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
