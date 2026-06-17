"""CI gate: holdout corpus isolation contract.

Plan: `.claude/plans/holdout-corpus-authoring-b5d2f6.md`.
Author-Gate: `dec_19dedcd1c109ebf25` (option_a_lock_in_doctrine).

Enforces: every row in `apps_eval/fixtures/holdout/<app>.jsonl` MUST
carry the `SYNTHETIC_SEED_ONLY` tag UNLESS it ALSO carries the
`RELEASE_GATE` tag. The `RELEASE_GATE` tag may only be added by a
human curator in a workstream isolated from Codex per Anthropic
holdout doctrine — this gate cannot detect curator identity, but it
DOES enforce a structural invariant: a row with neither tag is
ambiguous and forbidden.

The constraint:
- Row WITH `SYNTHETIC_SEED_ONLY` and WITHOUT `RELEASE_GATE` → OK (synthetic scaffold)
- Row WITHOUT `SYNTHETIC_SEED_ONLY` and WITH `RELEASE_GATE` → OK (real corpus)
- Row WITH BOTH tags → FAIL (contradiction)
- Row WITH NEITHER tag → FAIL (ambiguous)

Bypass: `HOLDOUT_ISOLATION_BYPASS=1` (logged).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Iterator

REPO_ROOT = Path(__file__).resolve().parents[2]
HOLDOUT_DIR = REPO_ROOT / "apps_eval" / "fixtures" / "holdout"


def _iter_rows(path: Path) -> Iterator[tuple[int, dict]]:
    if not path.is_file():
        return
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            yield i, json.loads(line)
        except json.JSONDecodeError as exc:
            yield i, {"_parse_error": str(exc)}


def _classify(tags: list) -> str:
    has_synth = "SYNTHETIC_SEED_ONLY" in tags
    has_release = "RELEASE_GATE" in tags
    if has_synth and has_release:
        return "contradiction"
    if not has_synth and not has_release:
        return "ambiguous"
    if has_synth:
        return "synthetic"
    return "release"


def _safe_rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def check(holdout_dir: Path = HOLDOUT_DIR) -> int:
    if os.getenv("HOLDOUT_ISOLATION_BYPASS") == "1":
        print("[check_holdout_isolation] BYPASS=1 — gate disabled", file=sys.stderr)
        return 0
    if not holdout_dir.is_dir():
        print(f"[check_holdout_isolation] OK — no holdout dir at {holdout_dir}")
        return 0

    violations: list[str] = []
    files_checked = 0
    rows_checked = 0
    for path in sorted(holdout_dir.glob("*.jsonl")):
        files_checked += 1
        for line_no, row in _iter_rows(path):
            rows_checked += 1
            if "_parse_error" in row:
                violations.append(
                    f"{_safe_rel(path)}:{line_no} parse error: {row['_parse_error']}"
                )
                continue
            tags = row.get("tags") or []
            if not isinstance(tags, list):
                violations.append(
                    f"{_safe_rel(path)}:{line_no} 'tags' must be a list, got {type(tags).__name__}"
                )
                continue
            kind = _classify(tags)
            if kind == "contradiction":
                violations.append(
                    f"{_safe_rel(path)}:{line_no} carries BOTH SYNTHETIC_SEED_ONLY and RELEASE_GATE — choose one"
                )
            elif kind == "ambiguous":
                violations.append(
                    f"{_safe_rel(path)}:{line_no} carries NEITHER SYNTHETIC_SEED_ONLY nor RELEASE_GATE — required by holdout-isolation contract"
                )

    if violations:
        print(f"[check_holdout_isolation] FAIL — {len(violations)} violation(s):", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print(
            "Fix: add SYNTHETIC_SEED_ONLY (legacy editor-Agent-authorable scaffold) OR RELEASE_GATE "
            "(human-curator-only) tag to every row.\nDoctrine: see plan "
            "holdout-corpus-authoring-b5d2f6 + Author-Gate dec_19dedcd1c109ebf25.\n"
            "Bypass: HOLDOUT_ISOLATION_BYPASS=1 (logged).",
            file=sys.stderr,
        )
        return 1

    print(
        f"[check_holdout_isolation] OK — {rows_checked} rows across {files_checked} files; "
        "all tagged exactly one of SYNTHETIC_SEED_ONLY|RELEASE_GATE"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Holdout isolation contract gate")
    p.add_argument("--holdout-dir", type=Path, default=HOLDOUT_DIR)
    args = p.parse_args(argv)
    return check(args.holdout_dir)


if __name__ == "__main__":
    sys.exit(main())
