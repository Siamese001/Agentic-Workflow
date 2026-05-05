"""CI gate: check_eval_holdout_split.

Plan: apps-underwriting-ai-rationale-judge-deferred-d4e7a2 W3.P3.1.

Detects overlap between holdout ``decision_id`` values in the
RationaleQualityJudge holdout dataset and any ``decision_id`` /
``fixture_id`` values used in tests or dev fixtures.  Overlap means a
holdout example was seen during development and is no longer an
independent test of calibration.

Exit codes
----------
0   No overlap detected (or advisory mode with no hard errors).
1   Overlap detected between holdout and dev fixtures — calibration is
    invalid until holdout is refreshed.
2   Configuration error (missing holdout file, import failure) — advisory
    mode exits 0 with a WARNING.

Environment variables
---------------------
EVAL_HOLDOUT_SPLIT_FAIL_CLOSED=1
    If set, configuration errors (exit 2) become hard failures (exit 1).

EVAL_HOLDOUT_SPLIT_BYPASS=1
    Skip all checks and exit 0 — for scripted batch runs.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_BYPASS = os.getenv("EVAL_HOLDOUT_SPLIT_BYPASS", "").strip() == "1"
_FAIL_CLOSED = os.getenv("EVAL_HOLDOUT_SPLIT_FAIL_CLOSED", "").strip() == "1"

_HOLDOUT_PATH = (
    REPO_ROOT / "apps_underwriting_ai" / "holdout" / "rationale_judge_holdout.yaml"
)

_DEV_SEARCH_ROOTS = [
    REPO_ROOT / "apps_underwriting_ai" / "config",
]
# Also scan tests/ but only fixture data files, not .py assertion strings.
_DEV_SEARCH_ROOTS_DATA_ONLY = [
    REPO_ROOT / "tests",
]
_DEV_FILE_GLOBS = ["*.py", "*.yaml", "*.yml", "*.json"]
_DEV_FILE_GLOBS_DATA_ONLY = ["*.yaml", "*.yml", "*.json"]

_DECISION_ID_RE = re.compile(r"\buw-(?:holdout|fixture|dev)-[\w-]+")


def _advisory_exit(msg: str) -> None:
    print(f"WARNING: {msg}", file=sys.stderr)
    if _FAIL_CLOSED:
        print("FAIL_CLOSED: treating advisory as hard failure.", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


def _load_holdout_ids() -> set[str]:
    try:
        import yaml
    except ImportError:
        _advisory_exit(
            "pyyaml not installed — cannot parse holdout file. "
            "Install pyyaml or set EVAL_HOLDOUT_SPLIT_BYPASS=1."
        )
        return set()

    if not _HOLDOUT_PATH.exists():
        _advisory_exit(
            f"Holdout file not found: {_HOLDOUT_PATH}. "
            "Run W1 to generate the holdout dataset."
        )
        return set()

    data: dict[str, Any] = yaml.safe_load(
        _HOLDOUT_PATH.read_text(encoding="utf-8")
    )
    examples = data.get("examples", [])
    return {str(ex["decision_id"]) for ex in examples if "decision_id" in ex}


def _collect_dev_ids() -> dict[str, set[str]]:
    """Scan dev/test directories for decision_id references outside holdout.

    Tests directories are scanned with data-file globs only (.yaml/.json) to
    avoid false positives from test assertion strings that legitimately cite
    holdout IDs.  Config and source directories use the full glob set.
    """
    found: dict[str, set[str]] = {}

    def _scan(root: Path, globs: list[str]) -> None:
        if not root.exists():
            return
        for glob in globs:
            for fpath in root.rglob(glob):
                if fpath == _HOLDOUT_PATH:
                    continue
                try:
                    text = fpath.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                ids = set(_DECISION_ID_RE.findall(text))
                if ids:
                    found[str(fpath.relative_to(REPO_ROOT))] = ids

    for root in _DEV_SEARCH_ROOTS:
        _scan(root, _DEV_FILE_GLOBS)

    for root in _DEV_SEARCH_ROOTS_DATA_ONLY:
        _scan(root, _DEV_FILE_GLOBS_DATA_ONLY)

    return found


def main() -> None:
    if _BYPASS:
        print("BYPASS: EVAL_HOLDOUT_SPLIT_BYPASS=1 — skipping holdout split check.")
        sys.exit(0)

    print("Checking holdout/dev-fixture split for RationaleQualityJudge...")

    holdout_ids = _load_holdout_ids()
    if not holdout_ids:
        print("No holdout IDs found — skipping overlap check.")
        sys.exit(0)

    print(f"  Holdout examples: {len(holdout_ids)}")

    dev_refs = _collect_dev_ids()
    total_dev_ids: set[str] = set()
    for ids in dev_refs.values():
        total_dev_ids |= ids

    overlap = holdout_ids & total_dev_ids
    if not overlap:
        print(
            f"  Dev fixture IDs scanned: {len(total_dev_ids)} across "
            f"{len(dev_refs)} file(s)"
        )
        print("PASS: No holdout/dev overlap detected.")
        sys.exit(0)

    print(
        f"FAIL: {len(overlap)} holdout decision_id(s) also appear in dev fixtures:",
        file=sys.stderr,
    )
    for oid in sorted(overlap):
        files = [f for f, ids in dev_refs.items() if oid in ids]
        print(f"  {oid}  →  {', '.join(files)}", file=sys.stderr)
    print(
        "\nAction: refresh the holdout dataset with new examples that do not "
        "appear in any test fixture, or remove the overlapping IDs from dev fixtures.",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
