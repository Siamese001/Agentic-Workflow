"""Wave D sandbox file verification."""

from __future__ import annotations

import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
NOISE = ("docs/reports/", "tools/archive/", "artifacts/", "docs/archive/windsurf/legacy-tree/plans/", "archives/")

targets = [
    "agentic_core/L2_execution/enforcement/docker_sandbox.py",
    "agentic_core/L2_execution/enforcement/preventative_sandbox.py",
    "agentic_core/L2_execution/enforcement/sovereign_sandbox_isolation.py",
    "agentic_core/L2_execution/types/sandbox_envelope_types.py",
    "agentic_core/adg/runtime/sandbox_airlock.py",
]


def run(args: list[str]) -> str:
    r = subprocess.run(args, capture_output=True, text=True, cwd=ROOT, timeout=60, check=False)
    return r.stdout


for t in targets:
    exists = (ROOT / t).exists()
    print(f"\n{t}  exists={exists}")
    if not exists:
        continue
    mod = t.replace(".py", "").replace("/", ".")
    refs: set[str] = set()
    for q in (f"from {mod} import", f"import {mod}", f'"{mod}"', f"'{mod}'", f'"{t}"'):
        out = run(["git", "grep", "-l", "--", q])
        for line in out.splitlines():
            line = line.strip()
            if line and line != t and not any(line.startswith(p) for p in NOISE):
                refs.add(f"{q[:30]}:{line}")
    print(f"  refs: {len(refs)}")
    for r in sorted(refs)[:8]:
        print(f"    {r}")
