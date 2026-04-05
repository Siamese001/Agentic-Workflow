"""Comprehensive error categorization — parse E   lines from --tb=short."""

import os
import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"

dirs_with_errors = ["adg", "ci", "e2e", "guardian", "integration", "misc",
                     "performance", "unit_min_deps"]

categories = {}
source_files = {}

for d in dirs_with_errors:
    r = subprocess.run(
        ["python", "-m", "pytest", f"tests/{d}", "--co", "--tb=short", "-p", "no:logging", "-q"],
        capture_output=True, text=True, cwd=ROOT, timeout=60
    )
    clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
    lines = clean.split("\n")

    for i, line in enumerate(lines):
        if "ERROR collecting" not in line:
            continue
        # Get the E   error line
        for j in range(i+1, min(i+20, len(lines))):
            s = lines[j].strip()
            if s.startswith("E   ") and len(s) > 6:
                msg = s[4:].strip()
                if msg.startswith("File "):
                    continue
                # Also find the source .py file
                for k in range(j-1, j+5):
                    if k < len(lines):
                        m = re.search(r'(\S+\.py):\d+', lines[k])
                        if m:
                            src = m.group(1)
                            break
                else:
                    src = "unknown"

                # Simplify
                if "NameError" in msg:
                    key = msg[:80]
                elif "ModuleNotFoundError" in msg:
                    key = msg[:120]
                elif "ImportError" in msg:
                    key = msg[:120]
                elif "FileNotFoundError" in msg:
                    key = "FileNotFoundError: " + msg.split("FileNotFoundError: ")[-1][:80]
                elif "AttributeError" in msg:
                    key = msg[:80]
                else:
                    key = msg[:80]

                categories.setdefault(key, 0)
                categories[key] += 1
                source_files.setdefault(key, set())
                source_files[key].add(src)
                break

# Now handle unit/ separately with per-subdir scans
unit_dir = os.path.join(ROOT, "tests", "unit")
for sd in sorted(os.listdir(unit_dir)):
    sdp = os.path.join(unit_dir, sd)
    if not os.path.isdir(sdp) or sd.startswith("_"):
        continue
    r = subprocess.run(
        ["python", "-m", "pytest", f"tests/unit/{sd}", "--co", "--tb=short", "-p", "no:logging", "-q"],
        capture_output=True, text=True, cwd=ROOT, timeout=60
    )
    clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)
    lines = clean.split("\n")

    for i, line in enumerate(lines):
        if "ERROR collecting" not in line:
            continue
        for j in range(i+1, min(i+20, len(lines))):
            s = lines[j].strip()
            if s.startswith("E   ") and len(s) > 6:
                msg = s[4:].strip()
                if msg.startswith("File "):
                    continue
                for k in range(j-1, j+5):
                    if k < len(lines):
                        m = re.search(r'(\S+\.py):\d+', lines[k])
                        if m:
                            src = m.group(1)
                            break
                else:
                    src = "unknown"

                if "NameError" in msg:
                    key = msg[:80]
                elif "ModuleNotFoundError" in msg:
                    key = msg[:120]
                elif "ImportError" in msg:
                    key = msg[:120]
                elif "FileNotFoundError" in msg:
                    key = "FileNotFoundError: " + msg.split("FileNotFoundError: ")[-1][:80]
                elif "AttributeError" in msg:
                    key = msg[:80]
                else:
                    key = msg[:80]

                categories.setdefault(key, 0)
                categories[key] += 1
                source_files.setdefault(key, set())
                source_files[key].add(src)
                break

total = sum(categories.values())
print(f"=== {total} errors in {len(categories)} categories ===\n")

for key, count in sorted(categories.items(), key=lambda x: -x[1]):
    srcs = sorted(source_files.get(key, set()))
    print(f"[{count:3d}] {key}")
    for s in srcs[:3]:
        print(f"       src: {s}")
    if len(srcs) > 3:
        print(f"       ... +{len(srcs)-3} more")
