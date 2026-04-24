"""Stage only the _adg.py deletions under tests/ plus my 2 tool files.

Avoids co-staging unrelated workspace edits. Idempotent.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAN = REPO / "artifacts" / "adg" / "stub_archive_candidates.json"


def run(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(
        args, capture_output=True, text=True, cwd=str(REPO), timeout=60, check=False
    )
    return result.returncode, result.stdout, result.stderr


def main() -> int:
    data = json.loads(PLAN.read_text(encoding="utf-8"))
    # Stage only sources that: (a) git still tracks, AND (b) are now missing from disk.
    # Skip entries already committed-and-removed (from the first 13-file commit).
    all_sources = [c["source"] for c in data["candidates"]]
    rc, tracked_out, _err = run(["git", "ls-files", "--", *all_sources])
    if rc != 0:
        return 1
    tracked = {line.strip().replace("\\", "/") for line in tracked_out.splitlines() if line.strip()}
    paths: list[str] = [s for s in all_sources if s in tracked]
    paths.extend(
        [
            "tools/adg/adg_stub_triage.py",
            "tools/adg/_run_stub_archive.py",
            "tools/adg/_stage_archive_deletes.py",
        ]
    )
    # Split: deletions go through `git rm`, tool files go through `git add`.
    deletions = [p for p in paths if p.startswith("tests/")]
    adds = [p for p in paths if not p.startswith("tests/")]
    chunk = 40
    for i in range(0, len(deletions), chunk):
        batch = deletions[i : i + chunk]
        rc, _out, err = run(["git", "rm", "-q", "--ignore-unmatch", "--", *batch])
        if rc != 0:
            print(f"git rm failed rc={rc}\nstderr={err}", file=sys.stderr)
            return 1
    for i in range(0, len(adds), chunk):
        batch = adds[i : i + chunk]
        rc, _out, err = run(["git", "add", "--", *batch])
        if rc != 0:
            print(f"git add failed rc={rc}\nstderr={err}", file=sys.stderr)
            return 1
    print(f"staged deletions={len(deletions)} adds={len(adds)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
