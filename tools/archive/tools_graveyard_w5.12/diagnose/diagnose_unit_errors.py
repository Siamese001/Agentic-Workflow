"""Categorize unit test collection errors by error type."""

import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"

r = subprocess.run(
    ["python", "-m", "pytest", "tests/unit/", "--co", "--tb=line", "-p", "no:logging", "-q"],
    capture_output=True, text=True, cwd=ROOT, timeout=120,
)
clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout)

# Parse ERROR lines and their associated error messages
errors = []
lines = clean.split("\n")
for i, line in enumerate(lines):
    if line.strip().startswith("ERROR tests/"):
        # Get the error detail from the same line (after " - ")
        parts = line.strip().split(" - ", 1)
        test_file = parts[0].replace("ERROR ", "").strip()
        err_msg = parts[1].strip() if len(parts) > 1 else ""

        # If no inline error, look for E   lines nearby
        if not err_msg:
            for j in range(max(0, i-5), min(len(lines), i+5)):
                s = lines[j].strip()
                if s.startswith("E   ") and ("Error" in s or "cannot import" in s or "No module" in s):
                    err_msg = s[4:].strip()
                    break

        errors.append((test_file, err_msg))

# Categorize
categories = {}
for test_file, err_msg in errors:
    # Extract error type
    if "NameError:" in err_msg:
        cat = "NameError: " + err_msg.split("NameError: ")[-1][:60]
    elif "ModuleNotFoundError:" in err_msg:
        cat = "ModuleNotFoundError: " + err_msg.split("ModuleNotFoundError: ")[-1][:80]
    elif "ImportError:" in err_msg:
        cat = "ImportError: " + err_msg.split("ImportError: ")[-1][:80]
    elif "FileNotFoundError:" in err_msg:
        cat = "FileNotFoundError"
    elif "AttributeError:" in err_msg:
        cat = "AttributeError: " + err_msg.split("AttributeError: ")[-1][:60]
    elif "pydantic" in err_msg.lower():
        cat = "PydanticError"
    elif "OSError" in err_msg:
        cat = "OSError"
    else:
        cat = err_msg[:80] if err_msg else "Unknown"

    categories.setdefault(cat, []).append(test_file)

print(f"=== {len(errors)} unit test collection errors ===\n")
for cat, files in sorted(categories.items(), key=lambda x: -len(x[1])):
    print(f"[{len(files):2d}] {cat}")
    for f in files[:3]:
        print(f"      {f}")
    if len(files) > 3:
        print(f"      ... and {len(files) - 3} more")
