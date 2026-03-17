"""Run the full agentic_core test suite and aggregate results."""
import os
import re
import subprocess
import sys

ROOT = r"C:\Git\Agentic-Workflow"
AC = os.path.join(ROOT, "tests", "unit", "agentic_core")

tp = ts = tf = te = 0
for sd in sorted(os.listdir(AC)):
    p = os.path.join(AC, sd)
    if not os.path.isdir(p) or sd.startswith("_"):
        continue
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/unit/agentic_core/{sd}",
         "-c", "tools/pytest_minimal.ini", "--tb=no", "-p", "no:warnings", "-q"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=ROOT, timeout=600, stdin=subprocess.DEVNULL,
    )
    for line in r.stdout.splitlines()[-3:]:
        if "passed" in line or "failed" in line or "error" in line or "skipped" in line:
            m = re.search(r"(\d+) passed", line)
            if m:
                tp += int(m.group(1))
            m = re.search(r"(\d+) skipped", line)
            if m:
                ts += int(m.group(1))
            m = re.search(r"(\d+) failed", line)
            if m:
                tf += int(m.group(1))
            m = re.search(r"(\d+) error", line)
            if m:
                te += int(m.group(1))
            print(f"{sd:30s} {line.strip()[:80]}")

print(f"---\nTOTAL: passed={tp} skipped={ts} failed={tf} errors={te}")
total = tp + ts + tf
if total > 0:
    print(f"Pass rate: {tp}/{total} = {100*tp/total:.1f}%")
