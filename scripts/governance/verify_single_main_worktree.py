"""Fail unless the local repo is one clean main worktree at the expected path."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parent
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

from worktree_hygiene import (  # noqa: E402
    summarize_single_main_worktree_issues,
    verify_single_main_worktree,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--expected-path",
        type=Path,
        default=None,
        help="Required sole worktree path. Defaults to --root.",
    )
    parser.add_argument("--base-ref", default="origin/main", help="Base ref for exact closeout checks")
    parser.add_argument("--fetch", action="store_true", help="Run git fetch origin --prune before checks")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    issues = verify_single_main_worktree(
        args.root,
        expected_path=args.expected_path,
        base_ref=args.base_ref,
        fetch=args.fetch,
    )
    status = "FAIL" if issues else "PASS"
    report = {
        "schema_version": "single-main-worktree/v1",
        "status": status,
        "repo_root": str(args.root.resolve()),
        "expected_path": str((args.expected_path or args.root).resolve()),
        "base_ref": args.base_ref,
        "issues": [{"code": issue.code, "detail": issue.detail} for issue in issues],
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"single-main-worktree: {status}")
        summary = summarize_single_main_worktree_issues(issues)
        if summary:
            print(summary)
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
