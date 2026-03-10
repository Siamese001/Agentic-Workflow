"""
Categorise the dry-run ssot_fixes_applied.json into GOOD (safe to apply)
vs BAD (would break code) and print a summary.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "artifacts" / "adg" / "ssot_fixes_applied.json"

data: dict = json.loads(DATA.read_text(encoding="utf-8"))

# Patterns that indicate the replacement would BREAK the code
BAD_PATTERNS = [
    # results["tests"].append(...)  — dict key lookup, not a path
    re.compile(r'\w+\["' + r'(?:tests|tools|reports|archives|agentic_core|apps_\w+|system_learning|ops_scripts)' + r'"\]'),
    # .get("tests", ...)  — dict method call
    re.compile(r'\.get\s*\(\s*["\'](?:tests|tools|reports|archives|agentic_core|apps_\w+)\s*["\']'),
    # if "tools" in kwargs  — dict key membership test
    re.compile(r'in\s+(?:kwargs|kw|options|config|params|settings)\b'),
    # default argument  def foo(domain: str = "agentic_core")
    re.compile(r'def\s+\w+.*=\s*["\']'),
    # docstring example:  e.g. "agentic_core"  or  # comment
    re.compile(r'(?:e\.g\.|i\.e\.|#\s|""".*|\'\'\'.*|Example:)'),
    # string that's a data field name in a dict literal value (not a path)
    re.compile(r'"(?:territory|domain|root|name|type|key|group|label|tag)":\s*"'),
    # suffix check  .endswith("tests")  .startswith("agentic_core")
    re.compile(r'\.(startswith|endswith)\s*\(\s*["\']'),
    # logging/print statement with literal in message
    re.compile(r'(?:print|log(?:ger)?\.(?:info|debug|warning|error|critical))\s*\('),
]


good: list[dict] = []
bad: list[dict] = []

for fpath, fixes in data.items():
    for fix in fixes:
        orig = fix["original_line"]
        is_bad = any(pat.search(orig) for pat in BAD_PATTERNS)
        entry = {
            "file": fpath,
            "line": fix["lineno"],
            "const": fix["const"],
            "orig": orig.strip()[:110],
            "fixed": fix["fixed_line"].strip()[:110],
        }
        if is_bad:
            bad.append(entry)
        else:
            good.append(entry)

print(f"GOOD (safe to apply): {len(good)}")
print(f"BAD  (would break):   {len(bad)}")
print()

print("=== BAD FIXES (sample 30) ===")
for b in bad[:30]:
    print(f"  [{b['const']}] {b['file']}:{b['line']}")
    print(f"    ORIG:  {b['orig']}")
    print(f"    FIXED: {b['fixed']}")
    print()

print("=== GOOD FIXES (sample 30) ===")
for g in good[:30]:
    print(f"  [{g['const']}] {g['file']}:{g['line']}")
    print(f"    ORIG:  {g['orig']}")
    print(f"    FIXED: {g['fixed']}")
    print()
