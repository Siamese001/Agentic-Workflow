"""Categorize unit test collection errors — capture full output."""

import os
import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"

r = subprocess.run(
    ["python", "-m", "pytest", "tests/unit/", "--co", "--tb=line", "-p", "no:logging", "-q"],
    capture_output=True, text=True, cwd=ROOT, timeout=120
)
clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout + "\n" + r.stderr)

# Save raw output for inspection
with open(os.path.join(ROOT, "artifacts", "unit_errors_raw.txt"), "w", encoding="utf-8") as f:
    f.write(clean)

# Find all ERROR lines
error_lines = []
all_lines = clean.split("\n")
for i, line in enumerate(all_lines):
    s = line.strip()
    if s.startswith("ERROR tests/unit/"):
        error_lines.append(s)

print(f"Found {len(error_lines)} ERROR lines")

# Count unique error types from inline messages
categories = {}
for el in error_lines:
    parts = el.split(" - ", 1)
    msg = parts[1].strip() if len(parts) > 1 else "no inline msg"

    # Simplify message
    if "NameError" in msg:
        key = msg[:80]
    elif "ModuleNotFoundError" in msg:
        key = msg[:100]
    elif "ImportError" in msg:
        key = msg[:100]
    elif "FileNotFoundError" in msg:
        key = "FileNotFoundError"
    elif "AttributeError" in msg:
        key = msg[:80]
    elif "pydantic" in msg.lower():
        key = "PydanticError"
    elif "OSError" in msg:
        key = "OSError"
    else:
        key = msg[:60] if msg else "Unknown"

    categories.setdefault(key, []).append(parts[0].replace("ERROR ", ""))

for key, files in sorted(categories.items(), key=lambda x: -len(x[1])):
    print(f"\n[{len(files):2d}] {key}")
    for f in files[:5]:
        print(f"      {f}")
    if len(files) > 5:
        print(f"      ... +{len(files) - 5} more")

# Last 3 lines of output
print("\n--- Last 3 lines ---")
for line in all_lines[-3:]:
    print(f"  {line.strip()}")
