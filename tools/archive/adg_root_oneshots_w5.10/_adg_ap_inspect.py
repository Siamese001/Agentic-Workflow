#!/usr/bin/env python3
"""Inspect the 9 stuck violations - show evidence text and surrounding lines."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKIP = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "archives"}

STUCK = [
    ("SubAtomicRegistryAgent.py", 626),
    ("ArchitectureGovernorAgent.py", 1581),
    ("CodeDeduplicationAgent.py", 836),
    ("CodeDeduplicationAgent.py", 695),
    ("CredentialScannerAgent.py", 406),
    ("LocationHealerAgent.py", 2635),
    ("SystemArchitectAgent.py", 451),
    ("dependencygraph_validator.py", 380),
    ("dependencygraph_validator.py", 400),
]

# Get full checker output for category info
r = subprocess.run(
    [sys.executable, "ops_scripts/ci/check_anti_patterns.py"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    cwd=str(REPO),
)
# Build map: (stem, lineno) -> category + evidence
info: dict[tuple[str, int], dict] = {}
lines = r.stdout.splitlines()
i = 0
while i < len(lines):
    if lines[i].startswith("[FAIL]"):
        loc = lines[i][7:].strip()
        parts = loc.rsplit(":", 1)
        stem = parts[0].strip()
        try:
            lineno = int(parts[1].strip())
        except (IndexError, ValueError):
            i += 1
            continue
        cat = evid = fix = ""
        if i + 1 < len(lines) and "[" in lines[i + 1]:
            cat = lines[i + 1].strip().split("]")[0].lstrip("[")
        if i + 2 < len(lines) and "Evidence:" in lines[i + 2]:
            evid = lines[i + 2].strip()
        if i + 3 < len(lines) and "[FIX]" in lines[i + 3]:
            fix = lines[i + 3].strip()
        info[(stem, lineno)] = {"cat": cat, "evid": evid, "fix": fix}
    i += 1

for stem, lineno in STUCK:
    hits = [p for p in REPO.rglob(stem) if not any(s in p.parts for s in SKIP)]
    if not hits:
        print(f"\n{stem}:{lineno}  FILE NOT FOUND")
        continue
    path = hits[0]
    file_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    key = (stem, lineno)
    d = info.get(key, {})
    print(f"\n{'=' * 60}")
    print(f"{path.relative_to(REPO)}:{lineno}  [{d.get('cat', '')}]")
    print(f"  {d.get('evid', '')}")
    print(f"  {d.get('fix', '')}")
    # Show context: lines lineno-3..lineno+1
    start = max(0, lineno - 4)
    end = min(len(file_lines), lineno + 2)
    for j in range(start, end):
        marker = ">>>" if j == lineno - 1 else "   "
        print(f"  {marker} {j + 1:4}: {file_lines[j]}")
