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
# guardian: allow-path-string
BAD_PATTERNS = [
    re.compile(
        '\\w+\\["'
        + "(?:tests|tools|reports|archives|agentic_core|apps_\\w+|system_learning|ops_scripts)"
        + '"\\]'
    ),
    re.compile("\\.get\\s*\\(\\s*[\"\\'](?:tests|tools|reports|archives|agentic_core|apps_\\w+)\\s*[\"\\']"),
    re.compile("in\\s+(?:kwargs|kw|options|config|params|settings)\\b"),
    re.compile("def\\s+\\w+.*=\\s*[\"\\']"),
    re.compile("(?:e\\.g\\.|i\\.e\\.|#\\s|\"\"\".*|\\'\\'\\'.*|Example:)"),
    re.compile('"(?:territory|domain|root|name|type|key|group|label|tag)":\\s*"'),
    re.compile("\\.(startswith|endswith)\\s*\\(\\s*[\"\\']"),
    re.compile("(?:print|log(?:ger)?\\.(?:info|debug|warning|error|critical))\\s*\\("),
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
