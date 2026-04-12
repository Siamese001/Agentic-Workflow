"""Find the SOURCE production files causing the most test collection errors.

Runs pytest --co --tb=short on the unit/ subdirectories and extracts the
production file paths from the traceback lines.
"""

import os
import re
import subprocess
from collections import Counter

ROOT = r"C:\Git\Agentic-Workflow"

# Run on unit subdirectories with errors
source_errors = Counter()  # source_file -> count
error_types = {}  # source_file -> error message

for subdir in ["agentic_core", "apps_lic", "apps_rg", "apps_shared", "system_learning", "prompt_governance"]:
    path = f"tests/unit/{subdir}"
    if not os.path.isdir(os.path.join(ROOT, path)):
        continue
    r = subprocess.run(
        ["python", "-m", "pytest", path, "--co", "--tb=short", "-p", "no:logging", "-q"],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=60,
    )
    clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
    lines = clean.split("\n")

    i = 0
    while i < len(lines):
        if "ERROR collecting" not in lines[i]:
            i += 1
            continue

        # Scan the traceback block for source file and error
        src_file = None
        err_msg = None
        for j in range(i + 1, min(i + 30, len(lines))):
            s = lines[j].strip()
            # Look for source file in traceback (non-test, non-pytest files)
            m = re.match(
                r"^(agentic_core[\\/]\S+\.py|apps_\w+[\\/]\S+\.py|system_learning[\\/]\S+\.py):(\d+):", s
            )
            if m:
                src_file = m.group(1).replace("\\", "/")
            if s.startswith("E   ") and ("Error" in s or "cannot import" in s or "No module" in s):
                err_msg = s[4:].strip()[:150]
                break

        if src_file and err_msg:
            source_errors[src_file] += 1
            error_types[src_file] = err_msg
        elif err_msg:
            source_errors["unknown"] += 1

        i += 1

print("=== Top source files causing test collection errors ===\n")
for src, count in source_errors.most_common(30):
    err = error_types.get(src, "unknown")
    print(f"[{count:3d}] {src}")
    print(f"       {err}")
