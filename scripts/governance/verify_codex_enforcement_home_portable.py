"""Run the Codex enforcement-home verifier across local and CI checkout roots.

Repo automation contracts intentionally pin the canonical Windows workstation
root. GitHub Actions checks out the same repository under a transient Linux
path. The base verifier correctly reports those paths as different. This
adapter suppresses only ``automation_cwd`` findings when the checked automation
already contains the canonical ``EXPECTED_REPO`` root; every other base issue
is preserved unchanged.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import verify_codex_enforcement_home as base

REPO_ROOT = base.REPO_ROOT
DEFAULT_USER_CODEX_HOME = base.DEFAULT_USER_CODEX_HOME

# Re-export constants used by verifier tests and downstream contract checks.
PUBLICATION_REQUIRED_PROMPT_SNIPPETS = base.PUBLICATION_REQUIRED_PROMPT_SNIPPETS
ADG_REQUIRED_PROMPT_SNIPPETS = base.ADG_REQUIRED_PROMPT_SNIPPETS
ADG_P0_REQUIRED_PROMPT_SNIPPETS = base.ADG_P0_REQUIRED_PROMPT_SNIPPETS
ADG_P1_REQUIRED_PROMPT_SNIPPETS = base.ADG_P1_REQUIRED_PROMPT_SNIPPETS
ADG_P2_REQUIRED_PROMPT_SNIPPETS = base.ADG_P2_REQUIRED_PROMPT_SNIPPETS
ADG_P3_REQUIRED_PROMPT_SNIPPETS = base.ADG_P3_REQUIRED_PROMPT_SNIPPETS
SVP_DOCS_REQUIRED_PROMPT_SNIPPETS = base.SVP_DOCS_REQUIRED_PROMPT_SNIPPETS


def _automation_id_from_cwd_issue(detail: str) -> str | None:
    automation_id, separator, _ = detail.partition(":")
    if not separator or automation_id not in base.AUTOMATION_IDS:
        return None
    return automation_id


def _has_canonical_contract_cwd(root: Path, automation_id: str) -> bool:
    path = base._automation_path(root, automation_id)
    data, error = base._load_toml(path)
    if data is None or error is not None:
        return False
    cwds = data.get("cwds")
    if not isinstance(cwds, list):
        return False
    expected = base._norm_path(base.EXPECTED_REPO)
    return expected in {base._norm_path(str(item)) for item in cwds}


def validate(
    root: Path = REPO_ROOT,
    user_codex_home: Path = DEFAULT_USER_CODEX_HOME,
) -> list[base.EnforcementHomeIssue]:
    root = root.resolve()
    issues = base.validate(root, user_codex_home)
    portable: list[base.EnforcementHomeIssue] = []
    for issue in issues:
        if issue.code != "automation_cwd":
            portable.append(issue)
            continue
        automation_id = _automation_id_from_cwd_issue(issue.detail)
        if automation_id is None or not _has_canonical_contract_cwd(root, automation_id):
            portable.append(issue)
    return portable


def build_report(
    root: Path = REPO_ROOT,
    user_codex_home: Path = DEFAULT_USER_CODEX_HOME,
) -> dict[str, Any]:
    issues = validate(root, user_codex_home)
    return {
        "schema_version": "codex-enforcement-home/v1",
        "status": "FAIL" if issues else "PASS",
        "repo_root": str(root.resolve()),
        "user_codex_home": str(user_codex_home.resolve()),
        "portable_checkout": base._norm_path(root) != base._norm_path(base.EXPECTED_REPO),
        "canonical_contract_root": str(base.EXPECTED_REPO),
        "issues": [asdict(issue) for issue in issues],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--user-codex-home", type=Path, default=DEFAULT_USER_CODEX_HOME)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report(args.root, args.user_codex_home)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"codex-enforcement-home-portable: {report['status']}")
        for issue in report["issues"]:
            print(f"- {issue['code']}: {issue['detail']}")
    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
