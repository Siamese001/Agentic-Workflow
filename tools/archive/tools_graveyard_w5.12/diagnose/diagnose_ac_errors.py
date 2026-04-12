"""Diagnose agentic_core collection errors and output source file + error pairs."""

import re
import subprocess
import sys
from collections import Counter

root = r"C:\Git\Agentic-Workflow"
r = subprocess.run(
    [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/agentic_core",
        "-c",
        "tools/pytest_minimal.ini",
        "--co",
        "--tb=short",
        "-p",
        "no:warnings",
    ],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=root,
)
out = r.stdout + r.stderr
lines = out.splitlines()

errors = []
i = 0
while i < len(lines):
    if "_ ERROR collecting" in lines[i]:
        test_file = lines[i].split("_ ERROR collecting")[-1].strip().rstrip(" _")
        src_file = ""
        e_msg = ""
        for j in range(i + 1, min(i + 15, len(lines))):
            l = lines[j].strip()
            if l.startswith("E   "):
                e_msg = l[4:]
                break
            if ".py:" in l and "in <module>" in l:
                src_file = l.split(":")[0]
        errors.append((test_file, src_file, e_msg))
    i += 1

# Group by source file
from collections import defaultdict

by_src = defaultdict(list)
for tf, sf, em in errors:
    by_src[sf or "unknown"].append((tf, em))

print(f"Total errors: {len(errors)}\n")
for sf, items in sorted(by_src.items()):
    print(f"Source: {sf}")
    for tf, em in items:
        print(f"  Test: {tf}")
        print(f"  Error: {em[:120]}")
    print()

# Summary by error type
cats = Counter()
for tf, sf, em in errors:
    if "NameError" in em:
        match = re.search(r"name '(\w+)' is not defined", em)
        name = match.group(1) if match else em
        cats[f"NameError: {name}"] += 1
    elif "FileNotFoundError" in em:
        cats["FileNotFoundError"] += 1
    elif "ImportError" in em:
        cats["ImportError"] += 1
    elif "ModuleNotFoundError" in em:
        cats["ModuleNotFoundError"] += 1
    elif "TypeError" in em:
        cats["TypeError (MRO)"] += 1
    elif "pydantic" in em.lower():
        cats["PydanticUserError"] += 1
    elif "OSError" in em:
        cats["OSError (stdin)"] += 1
    elif "AttributeError" in em:
        cats["AttributeError"] += 1
    else:
        cats[f"Other: {em[:60]}"] += 1

print("\n=== Summary ===")
for cat, cnt in cats.most_common():
    print(f"  [{cnt:2d}] {cat}")
