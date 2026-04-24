#!/usr/bin/env python3
"""Categorize the 337 collection errors by root cause."""

import re
import subprocess
from collections import Counter

result = subprocess.run(
    ["python", "-m", "pytest", "tests/unit/agentic_core/", "-q", "--tb=line", "--no-header"],
    capture_output=True,
    text=True,
    cwd=".",
)

output = result.stdout + result.stderr

# Parse ERROR lines
error_files = []
current_file = None
for line in output.splitlines():
    m = re.match(r"_ ERROR collecting (.+?) _", line)
    if m:
        current_file = m.group(1).strip()
    if current_file and line.startswith("E "):
        error_msg = line[2:].strip()
        # Categorize
        if "IndentationError" in error_msg:
            category = "IndentationError_in_source_module"
        elif "SyntaxError" in error_msg:
            category = "SyntaxError_in_source_module"
        elif "cannot import name 'BATCH_SIZE'" in error_msg:
            category = "missing_BATCH_SIZE_constant"
        elif "cannot import name" in error_msg:
            category = "missing_named_import"
        elif "FileNotFoundError" in error_msg:
            category = "FileNotFoundError_at_import"
        elif "ModuleNotFoundError" in error_msg:
            category = "ModuleNotFoundError"
        elif "ImportError" in error_msg:
            category = "other_ImportError"
        elif "NameError" in error_msg:
            category = "NameError_in_source"
        elif "OSError" in error_msg or "PermissionError" in error_msg:
            category = "OSError"
        else:
            category = "other"

        error_files.append(
            {
                "file": current_file,
                "category": category,
                "message": error_msg[:120],
            }
        )
        current_file = None  # Reset for next error

# Count categories
cat_counter = Counter()
for e in error_files:
    cat_counter[e["category"]] += 1

print("COLLECTION ERROR CATEGORIES:")
for cat, count in cat_counter.most_common():
    print(f"  {cat}: {count}")

print(f"\nTotal categorized errors: {len(error_files)}")

# Show samples of each
for cat in [
    "IndentationError_in_source_module",
    "SyntaxError_in_source_module",
    "missing_BATCH_SIZE_constant",
    "FileNotFoundError_at_import",
    "ModuleNotFoundError",
    "missing_named_import",
]:
    samples = [e for e in error_files if e["category"] == cat]
    if samples:
        print(f"\n--- {cat} ({len(samples)}) ---")
        for s in samples[:5]:
            print(f"  {s['file']}")
            print(f"    {s['message']}")

# Check: how many of these error files are our enhanced files vs pre-existing?
enhanced_errors = [
    e
    for e in error_files
    if "MODULE_PATH" in open(e["file"], encoding="utf-8").read()
    if "Behavioral contract tests" in open(e["file"], encoding="utf-8").read()
]
print("\nEnhanced files causing errors: check below")

# Better: check if the file has our fixture pattern
from pathlib import Path

our_files = 0
other_files = 0
for e in error_files:
    try:
        content = Path(e["file"]).read_text("utf-8")
        if "@pytest.fixture" in content and "FIRST-PARTY IMPORT FAILED" in content:
            our_files += 1
        else:
            other_files += 1
    except Exception:  # guardian: allow-broad-exception -- offline tooling, reports failure
        other_files += 1

print(f"Our enhanced files with errors: {our_files}")
print(f"Other (pre-existing) files with errors: {other_files}")
