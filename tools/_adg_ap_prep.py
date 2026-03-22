#!/usr/bin/env python3
"""ADG prep: read whitelist comments from all validators, then list violations."""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}


def whitelist_for(validator_name: str) -> str:
    hits = [p for p in REPO.rglob(validator_name)
            if not any(s in p.parts for s in SKIP)]
    if not hits:
        return "NOT FOUND"
    content = hits[0].read_text(encoding="utf-8")
    m = re.search(r'WHITELIST_COMMENT\s*=\s*["\']([^"\']+)["\']', content)
    return m.group(1) if m else "NOT FOUND"


validators = {
    "global_mutation": "global_mutation_validator.py",
    "magic_configuration": "magic_validator.py",
    "path_fragility": "path_fragility_validator.py",
    "type_erasure": "type_erasure_validator.py",
    "config_with_logic": "config_with_logic_validator.py",
}

print("=== Whitelist comment tokens per category ===")
for cat, fname in validators.items():
    wl = whitelist_for(fname)
    print(f"  {cat}: {wl!r}")

print()
print("=== Current violations (file:line  category) ===")
import subprocess

r = subprocess.run(
    ["python", "ops_scripts/ci/check_anti_patterns.py"],
    capture_output=True, text=True, cwd=str(REPO)
)
lines = r.stdout.splitlines()
i = 0
while i < len(lines):
    if lines[i].startswith("[FAIL]"):
        loc = lines[i][7:].strip()
        cat = ""
        if i + 1 < len(lines) and "[" in lines[i + 1]:
            cat = lines[i + 1].strip().split("]")[0].lstrip("[")
        print(f"  {loc}  [{cat}]")
    i += 1
