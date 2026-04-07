"""Comprehensive error categorization across all test directories."""

import os
import re
import subprocess

ROOT = r"C:\Git\Agentic-Workflow"

# Run pytest collect on all tests at once with --tb=line
r = subprocess.run(
    ["python", "-m", "pytest", "tests/", "--co", "--tb=line", "-p", "no:logging", "-q", "--no-header"],
    capture_output=True, text=True, cwd=ROOT, timeout=180,
)
clean = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout + "\n" + r.stderr)

# Save raw
with open(os.path.join(ROOT, "artifacts", "all_errors_raw.txt"), "w", encoding="utf-8") as f:
    f.write(clean)

# Parse: look for lines like "path/to/file.py:LINE: ErrorType: message"
# These appear in --tb=line format
error_pattern = re.compile(r'^(.+\.py):(\d+): (\w+Error(?:\w*)?): (.+)$', re.MULTILINE)
matches = error_pattern.findall(clean)

categories = {}
for filepath, lineno, errtype, msg in matches:
    # Simplify message
    short_msg = msg.strip()[:120]
    key = f"{errtype}: {short_msg}"
    if key not in categories:
        categories[key] = []
    # Store source file (the one causing the error)
    categories[key].append(f"{filepath}:{lineno}")

print(f"Found {len(matches)} error instances in {len(categories)} categories\n")

for key, sources in sorted(categories.items(), key=lambda x: -len(x[1])):
    print(f"[{len(sources):3d}] {key}")
    # Show unique source files
    unique_sources = sorted(set(sources))
    for s in unique_sources[:3]:
        print(f"       {s}")
    if len(unique_sources) > 3:
        print(f"       ... +{len(unique_sources)-3} more source files")
