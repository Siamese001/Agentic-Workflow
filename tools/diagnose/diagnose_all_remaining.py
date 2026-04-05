"""Get error details for ALL test directories with remaining errors."""

import os
import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"

for d in ["adg", "performance", "reasoning", "system_learning"]:
    r = subprocess.run(
        ["python", "-m", "pytest", f"tests/{d}", "--co", "--tb=short", "-p", "no:logging", "-q"],
        capture_output=True, text=True, cwd=ROOT, timeout=60
    )
    clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)

    errors = []
    lines = clean.split("\n")
    i = 0
    while i < len(lines):
        if "ERROR collecting" in lines[i]:
            err_file = lines[i].strip()
            err_msg = ""
            j = i + 1
            while j < len(lines):
                s = lines[j].strip()
                if s.startswith("E   ") and ("Error" in s or "cannot import" in s or "No module" in s):
                    err_msg = s[4:]
                    break
                j += 1
            errors.append((err_file, err_msg))
            i = j + 1
        else:
            i += 1

    if errors:
        print(f"\n=== tests/{d}/ ({len(errors)} errors) ===")
        for err_file, err_msg in errors:
            fname = err_file.split("ERROR collecting ")[-1].split(" ")[0] if "ERROR collecting" in err_file else err_file
            print(f"  {fname}")
            if err_msg:
                print(f"    -> {err_msg[:200]}")

# Also check unit/ errors with --tb=line but save to file for parsing
print("\n=== Analyzing tests/unit/ errors ===")
r = subprocess.run(
    ["python", "-m", "pytest", "tests/unit/", "--co", "--tb=no", "-p", "no:logging", "-q", "--no-header"],
    capture_output=True, text=True, cwd=ROOT, timeout=120
)
clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
with open(os.path.join(ROOT, "artifacts", "unit_errors_tbno.txt"), "w", encoding="utf-8") as f:
    f.write(clean)

# Count and show summary line
for line in clean.strip().split("\n")[-3:]:
    if "error" in line.lower() or "collected" in line.lower():
        print(f"  {line.strip()}")
