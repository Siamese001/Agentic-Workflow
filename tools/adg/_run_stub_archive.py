"""One-shot runner: execute the archive plan from stub_archive_candidates.json.

Reads artifacts/adg/stub_archive_candidates.json and executes `git mv` for
each candidate, creating destination directories as needed.

Idempotent: if dest exists and source is gone, skips. If both exist, fails.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAN = REPO / "artifacts" / "adg" / "stub_archive_candidates.json"


def main() -> int:
    if not PLAN.is_file():
        print(f"Plan missing: {PLAN}", file=sys.stderr)
        return 1
    data = json.loads(PLAN.read_text(encoding="utf-8"))
    candidates = data.get("candidates", [])
    if not candidates:
        print("No candidates to archive.")
        return 0

    moved: list[str] = []
    skipped: list[str] = []
    failed: list[tuple[str, str]] = []

    total = len(candidates)
    bar_width = 40
    for idx, c in enumerate(candidates, 1):
        src = REPO / c["source"]
        dest = REPO / c["dest"]

        # Progress bar
        pct = idx / total
        filled = int(bar_width * pct)
        bar = "\u2588" * filled + "\u2591" * (bar_width - filled)
        color = (
            "\033[92m" if pct >= 0.9
            else "\033[94m" if pct >= 0.7
            else "\033[93m" if pct >= 0.4
            else "\033[91m"
        )
        sys.stderr.write(
            f"\r{color}[{bar}]\033[0m {int(pct*100):3d}% ({idx}/{total}) archiving"
        )
        sys.stderr.flush()

        if not src.exists() and dest.exists():
            skipped.append(c["source"])
            continue
        if dest.exists():
            failed.append((c["source"], f"dest exists: {dest}"))
            continue
        if not src.exists():
            failed.append((c["source"], f"source missing: {src}"))
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            result = subprocess.run(
                ["git", "mv", str(src), str(dest)],
                capture_output=True,
                text=True,
                cwd=str(REPO),
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            failed.append((c["source"], f"{type(exc).__name__}: {exc}"))
            continue
        if result.returncode != 0:
            failed.append((c["source"], result.stderr.strip() or f"rc={result.returncode}"))
            continue
        moved.append(c["source"])

    sys.stderr.write("\n")
    print(f"moved={len(moved)} skipped={len(skipped)} failed={len(failed)}")
    if failed:
        print("FAILED:")
        for src, reason in failed:
            print(f"  {src} :: {reason}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
