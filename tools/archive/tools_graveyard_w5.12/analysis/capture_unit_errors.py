"""Capture unit test collection errors to a file, then parse them."""
import os
import re
import subprocess
from collections import Counter

ROOT = r"C:\Git\Agentic-Workflow"
OUT = os.path.join(ROOT, "artifacts", "unit_errors_short.txt")

# Run per-subdirectory to avoid pipe buffer issues
unit_dir = os.path.join(ROOT, "tests", "unit")
all_errors = []

for sd in sorted(os.listdir(unit_dir)):
    sdp = os.path.join(unit_dir, sd)
    if not os.path.isdir(sdp) or sd.startswith("_"):
        continue

    r = subprocess.run(
        ["python", "-m", "pytest", f"tests/unit/{sd}", "--co", "--tb=short", "-p", "no:logging", "-q"],
        capture_output=True, text=True, cwd=ROOT, timeout=60,
    )
    out = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)

    # Parse error blocks
    lines = out.split("\n")
    i = 0
    while i < len(lines):
        if "ERROR collecting" in lines[i]:
            test_file = lines[i].strip()
            err_msg = ""
            src_file = ""
            for j in range(i+1, min(i+30, len(lines))):
                s = lines[j].strip()
                if s.startswith("E   ") and len(s) > 6:
                    msg = s[4:].strip()
                    if not msg.startswith("File "):
                        err_msg = msg
                        break
                m = re.match(r"((?:agentic_core|apps_\w+|system_learning)[/\\].+\.py):(\d+)", s)
                if m:
                    src_file = m.group(1).replace("\\", "/")

            all_errors.append({
                "subdir": sd,
                "test_file": test_file,
                "src_file": src_file,
                "err_msg": err_msg,
            })
        i += 1

# Categorize
cats = Counter()
srcs = Counter()
for e in all_errors:
    msg = e["err_msg"]
    if "NameError" in msg:
        cats[msg[:80]] += 1
    elif "FileNotFoundError" in msg:
        cats["FileNotFoundError: " + msg.split("FileNotFoundError: ")[-1][:60]] += 1
    elif "ImportError" in msg:
        cats[msg[:100]] += 1
    elif "ModuleNotFoundError" in msg:
        cats[msg[:100]] += 1
    elif "pydantic" in msg.lower():
        cats["PydanticError: " + msg[:60]] += 1
    elif "OSError" in msg:
        cats["OSError: stdin"] += 1
    else:
        cats[msg[:60] if msg else "unknown"] += 1

    if e["src_file"]:
        srcs[e["src_file"]] += 1

print(f"=== {len(all_errors)} total unit test collection errors ===\n")
for k, v in cats.most_common(30):
    print(f"[{v:3d}] {k}")

print("\nTop source files causing errors:")
for k, v in srcs.most_common(15):
    print(f"  [{v:3d}] {k}")
