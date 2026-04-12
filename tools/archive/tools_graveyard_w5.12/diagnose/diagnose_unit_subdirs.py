"""Diagnose unit test errors by subdirectory."""

import os
import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"
UNIT = os.path.join(ROOT, "tests", "unit")

total_collected = 0
total_errors = 0

for d in sorted(os.listdir(UNIT)):
    dpath = os.path.join(UNIT, d)
    if not os.path.isdir(dpath) or d.startswith("_"):
        continue

    r = subprocess.run(
        ["python", "-m", "pytest", f"tests/unit/{d}", "--co", "-q", "-p", "no:logging", "--tb=no"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
    )
    clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
    last_line = ""
    for line in clean.strip().split("\n"):
        if line.strip():
            last_line = line.strip()

    match = re.search(r"(\d+)\s+tests?\s+collected", last_line)
    match_err = re.search(r"(\d+)\s+errors?", last_line)

    collected = int(match.group(1)) if match else 0
    errors = int(match_err.group(1)) if match_err else 0

    total_collected += collected
    total_errors += errors

    if errors > 0:
        print(f"  {d:40s}  collected={collected:5d}  errors={errors:2d}")

print(f"\nTotal: {total_collected} collected, {total_errors} errors")
