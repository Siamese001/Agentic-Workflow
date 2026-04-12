#!/usr/bin/env python3
"""Analyze common syntax error patterns."""

import json
from collections import Counter

with open("C:/Git/Agentic-Workflow/syntax_error_report.json") as f:
    report = json.load(f)

# Count error patterns
patterns = Counter()
for err in report["details"]:
    msg = err["message"]
    # Extract common patterns
    if "unexpected indent" in msg:
        patterns["unexpected indent"] += 1
    elif "expected an indented block" in msg:
        patterns["expected indented block"] += 1
    elif "invalid syntax" in msg:
        patterns["invalid syntax"] += 1
    elif "expected 'except' or 'finally'" in msg:
        patterns["missing except/finally"] += 1
    elif "{" in msg and "never closed" in msg:
        patterns["unclosed brace"] += 1
    else:
        patterns["other"] += 1

print("=== SYNTAX ERROR PATTERNS ===")
for pattern, count in patterns.most_common():
    print(f"{pattern}: {count} files")

# Show examples of each pattern
print("\n=== EXAMPLES ===")
for err in report["details"][:10]:
    print(f"{err['file']}:{err['line']} - {err['message'][:80]}...")
