"""Fix all remaining NameErrors and ImportErrors in agentic_core source files."""
import os
import re
import subprocess
import sys

ROOT = r"C:\Git\Agentic-Workflow"


def get_errors():
    """Get all current source-file errors from pytest collection."""
    ac_dir = os.path.join(ROOT, "tests", "unit", "agentic_core")
    errors = []
    for sd in sorted(os.listdir(ac_dir)):
        sdp = os.path.join(ac_dir, sd)
        if not os.path.isdir(sdp) or sd.startswith("_"):
            continue
        r = subprocess.run(
            [sys.executable, "-m", "pytest", f"tests/unit/agentic_core/{sd}",
             "-c", "tools/pytest_minimal.ini", "--co", "--tb=short", "-p", "no:warnings"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=ROOT, timeout=60,
        )
        lines = (r.stdout + r.stderr).splitlines()
        for i, line in enumerate(lines):
            l = line.strip()
            if not l.startswith("E   "):
                continue
            err = l[4:]
            # Find source file
            src = ""
            for j in range(max(0, i-10), i):
                prev = lines[j].strip()
                if ".py:" in prev and "in <module>" in prev:
                    candidate = prev.split(":")[0].strip()
                    if not os.path.isabs(candidate):
                        candidate = os.path.join(ROOT, candidate)
                    if os.path.exists(candidate):
                        src = candidate
                        break
            if src:
                errors.append((src, err, sd))
    return errors


def categorize(errors):
    """Categorize errors."""
    from collections import Counter
    cats = Counter()
    for src, err, sd in errors:
        if "NameError" in err:
            m = re.search(r"name '(\w+)' is not defined", err)
            name = m.group(1) if m else "?"
            cats[f"NameError: {name}"] += 1
        elif "FileNotFoundError" in err:
            cats["FileNotFoundError"] += 1
        elif "ImportError" in err:
            cats["ImportError"] += 1
        elif "TypeError" in err:
            cats["TypeError"] += 1
        elif "OSError" in err:
            cats["OSError"] += 1
        elif "ModuleNotFoundError" in err:
            cats["ModuleNotFoundError"] += 1
        elif "pydantic" in err.lower():
            cats["Pydantic"] += 1
        elif "AttributeError" in err:
            cats["AttributeError"] += 1
        else:
            cats[f"Other: {err[:50]}"] += 1
    return cats


errors = get_errors()
cats = categorize(errors)
print(f"Total errors: {len(errors)}")
for cat, cnt in cats.most_common():
    print(f"  [{cnt:2d}] {cat}")

# List non-FileNotFoundError source files
print("\nNon-file-not-found errors:")
for src, err, sd in errors:
    if "FileNotFoundError" not in err:
        rel = os.path.relpath(src, ROOT)
        print(f"  [{sd}] {rel}  ->  {err[:100]}")
