"""Diagnose agentic_core collection errors per subdirectory."""
import os
import re
import subprocess
import sys
from collections import Counter

root = r"C:\Git\Agentic-Workflow"
ac_dir = os.path.join(root, "tests", "unit", "agentic_core")
all_errors = []

for sd in sorted(os.listdir(ac_dir)):
    sdp = os.path.join(ac_dir, sd)
    if not os.path.isdir(sdp) or sd.startswith("_"):
        continue
    r = subprocess.run(
        [sys.executable, "-m", "pytest", f"tests/unit/agentic_core/{sd}",
         "-c", "tools/pytest_minimal.ini", "--co", "--tb=short", "-p", "no:warnings"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=root,
        timeout=60
    )
    out = r.stdout + r.stderr
    lines = out.splitlines()

    # Find error lines by looking for patterns
    for i, line in enumerate(lines):
        if "ERROR collecting" in line:
            # Get E   lines that follow
            src_file = ""
            e_msg = ""
            for j in range(i+1, min(i+20, len(lines))):
                l = lines[j].strip()
                if l.startswith("E   "):
                    e_msg = l[4:]
                    break
                # Capture the source file that caused the error
                if ".py:" in l and not l.startswith("E"):
                    src_file = l

            test_match = re.search(r"ERROR collecting (.+?) _", line)
            test_file = test_match.group(1).strip() if test_match else line
            all_errors.append((sd, test_file, src_file, e_msg))

print(f"Total collection errors: {len(all_errors)}\n")

# Group by error type
cats = Counter()
for sd, tf, sf, em in all_errors:
    if "NameError" in em:
        match = re.search(r"name '(\w+)' is not defined", em)
        name = match.group(1) if match else "?"
        cats[f"NameError: {name}"] += 1
        print(f"[NameError:{name}] src={sf[:80]}  test={tf[:60]}")
    elif "FileNotFoundError" in em:
        cats["FileNotFoundError"] += 1
    elif "ImportError" in em:
        cats["ImportError"] += 1
        print(f"[ImportError] {em[:100]}  src={sf[:60]}")
    elif "ModuleNotFoundError" in em:
        cats["ModuleNotFoundError"] += 1
        print(f"[ModuleNotFound] {em[:100]}")
    elif "TypeError" in em:
        cats["TypeError"] += 1
        print(f"[TypeError] {em[:100]}  src={sf[:60]}")
    elif "pydantic" in em.lower():
        cats["Pydantic"] += 1
        print(f"[Pydantic] src={sf[:80]}")
    elif "OSError" in em:
        cats["OSError"] += 1
    elif "AttributeError" in em:
        cats["AttributeError"] += 1
        print(f"[AttrError] {em[:100]}  src={sf[:60]}")
    else:
        cats["Other"] += 1
        if em:
            print(f"[Other] {em[:100]}")

print("\n=== Summary by category ===")
for cat, cnt in cats.most_common():
    print(f"  [{cnt:2d}] {cat}")
