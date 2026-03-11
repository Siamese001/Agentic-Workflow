#!/usr/bin/env python3
"""Run ADG SQLite validation and capture full output to file."""
import subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"

result = subprocess.run(
    [sys.executable, "-u", str(ROOT / "docs/reports/plans/_adg_sqlite_validation.py")],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=str(ROOT), env=env
)
output = result.stdout + result.stderr
report_path = ROOT / "docs/reports/plans/_adg_validation_full_output.txt"
report_path.write_text(output, encoding="utf-8")
print(f"Saved {len(output)} chars to {report_path.name}")
print(f"Exit code: {result.returncode}")
lines = output.splitlines()
for line in lines:
    print(line)
