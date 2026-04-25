"""Debug A12 gate self-check on the known-bad gate."""

import re
from pathlib import Path

CLAIM_RE = re.compile(
    r"(edge_kind\s*=\s*['\"](\w+)['\"]|"
    r"relation_type\s*=\s*['\"](\w+)['\"]|"
    r"category\s*=\s*['\"](\w+)['\"]|"
    r"violation_class\s*=\s*['\"](\w+)['\"])",
)
SQL_RE = re.compile(
    r"(edge_kind|relation_type|category|violation_class)"
    r"\s*=\s*['\"](\w+)['\"]",
    re.IGNORECASE,
)

p = Path("ops_scripts/ci/check_unused_imports_ratchet.py")
txt = p.read_text(encoding="utf-8")

print("=== first 20 lines ===")
for i, ln in enumerate(txt.splitlines()[:20], 1):
    print(f"  {i:3d}: {ln}")

print("\n=== claim regex on first 60 lines ===")
head = "\n".join(txt.splitlines()[:60])
matches = CLAIM_RE.findall(head)
print(f"  found {len(matches)} claim matches")
for m in matches:
    print(f"  {m}")

print("\n=== sql regex on whole file ===")
sql_matches = SQL_RE.findall(txt)
print(f"  found {len(sql_matches)} SQL matches")
for m in sql_matches[:5]:
    print(f"  {m}")
