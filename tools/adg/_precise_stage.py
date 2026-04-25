"""Precisely stage only the stub-archive deletions + my tool files.

Iterates the candidates JSON and stages each source individually with
`git add -u --`, which stages tracked deletions without co-staging unrelated
workspace mods.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAN = REPO / "artifacts" / "adg" / "stub_archive_candidates.json"


def run(args: list[str]) -> tuple[int, str]:
    r = subprocess.run(args, capture_output=True, text=True, cwd=str(REPO), timeout=30, check=False)
    return r.returncode, (r.stderr or r.stdout)


def main() -> int:
    data = json.loads(PLAN.read_text(encoding="utf-8"))
    sources = [c["source"] for c in data["candidates"]]

    # Filter to only sources still tracked
    rc, tracked_out = run(["git", "ls-files", "--", *sources])
    if rc != 0:
        print(f"ls-files failed: {tracked_out}", file=sys.stderr)
        return 1
    tracked = {line.strip().replace("\\", "/") for line in tracked_out.splitlines() if line.strip()}
    targets = [s for s in sources if s in tracked]

    staged_ok = 0
    staged_fail: list[tuple[str, str]] = []
    total = len(targets)
    for idx, path in enumerate(targets, 1):
        rc, msg = run(["git", "add", "-u", "--", path])
        if rc != 0:
            staged_fail.append((path, msg.strip()))
        else:
            staged_ok += 1
        if idx == total or idx % 10 == 0:
            sys.stderr.write(f"\r[{idx}/{total}] staged={staged_ok} fail={len(staged_fail)}")
            sys.stderr.flush()
    sys.stderr.write("\n")

    # Stage my own tool files
    for tool in (
        "tools/adg/adg_stub_triage.py",
        "tools/adg/_run_stub_archive.py",
        "tools/adg/_stage_archive_deletes.py",
        "tools/adg/_precise_stage.py",
    ):
        rc, msg = run(["git", "add", "--", tool])
        if rc != 0:
            staged_fail.append((tool, msg.strip()))

    print(f"result: staged_ok={staged_ok} failed={len(staged_fail)}")
    for p, m in staged_fail[:5]:
        print(f"  FAIL {p}: {m}")
    return 0 if not staged_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
