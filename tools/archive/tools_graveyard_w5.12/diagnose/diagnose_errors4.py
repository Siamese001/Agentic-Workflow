"""Get specific error messages per directory."""

import os
import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"
TESTS_DIR = os.path.join(ROOT, "tests")

for d in ["evaluation", "guardian", "integration", "unit_min_deps", "agentic_core"]:
    dpath = os.path.join(TESTS_DIR, d)
    if not os.path.isdir(dpath):
        continue

    r = subprocess.run(
        ["python", "-m", "pytest", f"tests/{d}", "--co", "-q", "-p", "no:logging", "--tb=line"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
    )
    clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout + "\n" + r.stderr)

    print(f"\n=== tests/{d}/ ===")
    for line in clean.split("\n"):
        s = line.strip()
        if s.startswith("ERROR tests/"):
            print(f"  {s[:200]}")
        elif "ImportError" in s or "ModuleNotFoundError" in s or "NameError" in s:
            if s.startswith("E ") or "Traceback" not in s:
                print(f"    {s[:200]}")
