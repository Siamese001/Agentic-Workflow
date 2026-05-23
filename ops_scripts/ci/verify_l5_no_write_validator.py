#!/usr/bin/env python3
"""Release-gate alias: ``l5_no_write_validator`` (REQ-L5-NO-WRITE-001)."""

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
        "tests/uwg/test_no_direct_l4_write.py::test_direct_write_from_non_authorized_surface_blocked[L5]",
        "-q",
        "--tb=short",
    ]
    env = {**dict(**__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(cmd, cwd=ROOT, env=env, check=False)
    if proc.returncode == 0:
        print("[l5_no_write_validator] PASS")
    else:
        print("[l5_no_write_validator] FAIL", file=sys.stderr)
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
