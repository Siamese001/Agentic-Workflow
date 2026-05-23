#!/usr/bin/env python3
"""Release-gate alias: ``uwg_sole_admission_validator`` (REQ-UWG-SOLE-DURABLE-WRITE-001)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/uwg/test_no_direct_l4_write.py",
        "tests/governance/test_apps_rg_l4_uwg.py",
        "-q",
        "--tb=short",
    ]
    env = {**dict(**__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(cmd, cwd=ROOT, env=env, check=False)
    if proc.returncode == 0:
        print("[uwg_sole_admission_validator] PASS")
    else:
        print("[uwg_sole_admission_validator] FAIL", file=sys.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
