"""Audit git publication state for Codex main-publish automations.

This script is read-only except for the optional ``git fetch origin --prune``
used to refresh remote-tracking refs before branch containment checks.
"""

from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path
from typing import Any

from worktree_hygiene import (
    find_dirty_protected_worktrees,
    parse_worktrees,
    run_git,
    summarize_dirty_worktrees,
    summarize_single_main_worktree_issues,
    verify_single_main_worktree,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AUTOMATION_CONTRACT = REPO_ROOT / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"


def _branch_lines(stdout: str) -> list[str]:
    return [line.strip() for line in stdout.splitlines() if line.strip()]


def _rev_parse(root: Path, ref: str) -> str | None:
    rc, stdout, _ = run_git("rev-parse", "--verify", ref, cwd=root)
    return stdout if rc == 0 and stdout else None


def _github_main_sha(root: Path) -> str | None:
    rc, stdout, _ = run_git("ls-remote", "origin", "refs/heads/main", cwd=root)
    if rc != 0 or not stdout:
        return None
    return stdout.split()[0]


def _status(root: Path) -> dict[str, Any]:
    rc, stdout, stderr = run_git("status", "--short", "--branch", cwd=root)
    return {
        "ok": rc == 0,
        "raw": stdout,
        "error": stderr,
        "dirty": bool(stdout and any(not line.startswith("##") for line in stdout.splitlines())),
        "conflicted": any(line[:2] in {"AA", "DD", "UU", "AU", "UA", "DU", "UD"} for line in stdout.splitlines()),
    }


def _worktrees(root: Path) -> list[dict[str, str]]:
    rc, stdout, _ = run_git("worktree", "list", "--porcelain", cwd=root)
    return parse_worktrees(stdout) if rc == 0 else []


def _unmerged_branches(root: Path, base_ref: str, limit: int) -> list[dict[str, Any]]:
    rc, stdout, stderr = run_git(
        "branch",
        "--no-merged",
        base_ref,
        "--format=%(refname:short)",
        cwd=root,
    )
    if rc != 0:
        return [{"error": stderr}]

    branches: list[dict[str, Any]] = []
    for branch in _branch_lines(stdout)[:limit]:
        rc_cherry, cherry, cherry_err = run_git("cherry", "-v", base_ref, branch, cwd=root)
        cherry_lines = _branch_lines(cherry) if rc_cherry == 0 else []
        branches.append(
            {
                "branch": branch,
                "cherry_status": "ok" if rc_cherry == 0 else "error",
                "cherry_error": cherry_err,
                "patch_equivalent_commits": [line for line in cherry_lines if line.startswith("- ")],
                "patch_unique_commits": [line for line in cherry_lines if line.startswith("+ ")],
            }
        )
    return branches


def _pr_flow_contract(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "required": False,
            "clean": False,
            "path": str(path),
            "issues": [{"code": "missing_contract", "detail": "automation contract file not found"}],
        }
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        return {
            "required": False,
            "clean": False,
            "path": str(path),
            "issues": [{"code": "invalid_toml", "detail": str(exc)}],
        }

    publication_mode = data.get("publication_mode")
    allow_direct_main_push = data.get("allow_direct_main_push")
    require_github_ci_green = data.get("require_github_ci_green")
    allow_bypass_merge = data.get("allow_bypass_merge")
    issues: list[dict[str, str]] = []
    if publication_mode != "pull_request":
        issues.append(
            {
                "code": "publication_mode",
                "detail": f"expected=pull_request actual={publication_mode!r}",
            }
        )
    if allow_direct_main_push is not False:
        issues.append(
            {
                "code": "allow_direct_main_push",
                "detail": f"expected=false actual={allow_direct_main_push!r}",
            }
        )
    if require_github_ci_green is not True:
        issues.append(
            {
                "code": "require_github_ci_green",
                "detail": f"expected=true actual={require_github_ci_green!r}",
            }
        )
    if allow_bypass_merge is not False:
        issues.append(
            {
                "code": "allow_bypass_merge",
                "detail": f"expected=false actual={allow_bypass_merge!r}",
            }
        )

    return {
        "required": True,
        "clean": not issues,
        "path": str(path),
        "publication_mode": publication_mode,
        "allow_direct_main_push": allow_direct_main_push,
        "require_github_ci_green": require_github_ci_green,
        "allow_bypass_merge": allow_bypass_merge,
        "issues": issues,
        "rule": "This automation must publish through a GitHub Pull Request, wait for green GitHub CI, and avoid bypass/forced merges.",
    }


def build_publication_audit(
    root: Path = REPO_ROOT,
    *,
    fetch: bool = True,
    base_ref: str = "origin/main",
    branch_limit: int = 100,
    require_ancestor_cleanup: bool = False,
    require_single_main_worktree: bool = False,
    require_pr_flow: bool = False,
    expected_worktree_path: Path | None = None,
    automation_contract_path: Path | None = None,
) -> dict[str, Any]:
    fetch_result: dict[str, Any] | None = None
    if fetch:
        rc, stdout, stderr = run_git("fetch", "origin", "--prune", cwd=root)
        fetch_result = {"ok": rc == 0, "stdout": stdout, "stderr": stderr}

    origin_main = _rev_parse(root, base_ref)
    github_main = _github_main_sha(root)
    protected_issues = find_dirty_protected_worktrees(root, skip_paths=(root,))
    status = _status(root)
    unmerged = _unmerged_branches(root, base_ref, branch_limit) if origin_main else []
    single_main_issues = verify_single_main_worktree(
        root,
        expected_path=expected_worktree_path,
        base_ref=base_ref,
        fetch=False,
    )
    pr_flow = (
        _pr_flow_contract(automation_contract_path or DEFAULT_AUTOMATION_CONTRACT)
        if require_pr_flow
        else {
            "required": False,
            "clean": True,
            "path": str(automation_contract_path or DEFAULT_AUTOMATION_CONTRACT),
            "issues": [],
            "rule": "PR flow contract is advisory unless --require-pr-flow is supplied.",
        }
    )

    blockers: list[str] = []
    warnings: list[str] = []
    if not status["ok"]:
        blockers.append("git_status_failed")
    recovery_required: list[str] = []
    if status["dirty"]:
        recovery_required.append("current_worktree_dirty")
        if require_single_main_worktree:
            blockers.append("current_worktree_dirty")
        else:
            warnings.append("current_worktree_dirty")
    if status["conflicted"]:
        blockers.append("current_worktree_conflicted")
    if protected_issues:
        warnings.append("dirty_protected_worktrees")
    if not origin_main:
        blockers.append("origin_main_missing")
    if not github_main:
        blockers.append("github_main_unavailable")
    if origin_main and github_main and origin_main != github_main:
        blockers.append("origin_main_differs_from_github_main")
    if fetch_result is not None and not fetch_result["ok"]:
        blockers.append("fetch_failed")
    if unmerged:
        if require_ancestor_cleanup:
            blockers.append("branches_not_ancestor_contained")
        else:
            warnings.append("branches_not_ancestor_contained")
    if single_main_issues:
        if require_single_main_worktree:
            blockers.append("single_main_worktree_violation")
        else:
            warnings.append("single_main_worktree_violation")
    if require_pr_flow and not pr_flow.get("clean"):
        blockers.append("pr_flow_contract_violation")

    unique_count = 0
    equivalent_count = 0
    for row in unmerged:
        if isinstance(row, dict):
            unique_count += len(row.get("patch_unique_commits") or [])
            equivalent_count += len(row.get("patch_equivalent_commits") or [])

    return {
        "schema_version": "codex-publication-audit/v1",
        "repo_root": str(root),
        "status": "FAIL" if blockers else ("WARN" if warnings else "PASS"),
        "blockers": blockers,
        "warnings": warnings,
        "recovery_required": recovery_required,
        "fetch": fetch_result,
        "refs": {
            "base_ref": base_ref,
            "origin_main": origin_main,
            "github_main": github_main,
            "origin_main_equals_github_main": bool(origin_main and github_main and origin_main == github_main),
        },
        "current_worktree": status,
        "worktrees": _worktrees(root),
        "dirty_protected_worktrees": [
            {
                "branch": issue.branch,
                "worktree": str(issue.worktree),
                "dirty_files": list(issue.dirty_files),
            }
            for issue in protected_issues
        ],
        "dirty_protected_summary": summarize_dirty_worktrees(protected_issues),
        "recommended_execution_surface": (
            "clean_detached_origin_main_worktree"
            if status["dirty"] or protected_issues
            else "current_worktree"
        ),
        "ancestor_cleanup": {
            "required": require_ancestor_cleanup,
            "clean": not bool(unmerged),
            "unmerged_branch_count": len(unmerged),
            "patch_unique_commit_count": unique_count,
            "patch_equivalent_commit_count": equivalent_count,
            "rule": "A branch is done only when its tip is ancestor-contained in origin/main. Patch equivalence is evidence for an ours merge, not cleanup proof.",
        },
        "single_main_worktree": {
            "required": require_single_main_worktree,
            "clean": not bool(single_main_issues),
            "issues": [
                {"code": issue.code, "detail": issue.detail}
                for issue in single_main_issues
            ],
            "summary": summarize_single_main_worktree_issues(single_main_issues),
            "rule": "Post-PR local closeout requires exactly one clean main worktree at the expected repo path, with HEAD equal to the base ref.",
        },
        "pr_flow": pr_flow,
        "unmerged_branches": unmerged,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--no-fetch", action="store_true", help="Skip git fetch origin --prune")
    parser.add_argument("--base-ref", default="origin/main", help="Base ref for branch containment checks")
    parser.add_argument("--branch-limit", type=int, default=100, help="Maximum unmerged branches to inspect")
    parser.add_argument(
        "--require-ancestor-cleanup",
        action="store_true",
        help="Fail if any local branch is not ancestor-contained in the base ref.",
    )
    parser.add_argument(
        "--require-single-main-worktree",
        action="store_true",
        help="Fail unless the local repo is exactly one clean main worktree.",
    )
    parser.add_argument(
        "--require-pr-flow",
        action="store_true",
        help="Fail unless the on-demand PR publisher contract forbids direct main push.",
    )
    parser.add_argument(
        "--automation-contract",
        type=Path,
        default=None,
        help="Automation TOML contract to inspect for --require-pr-flow.",
    )
    parser.add_argument(
        "--expected-worktree-path",
        type=Path,
        default=None,
        help="Required sole worktree path. Defaults to the repo root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_publication_audit(
        fetch=not args.no_fetch,
        base_ref=args.base_ref,
        branch_limit=args.branch_limit,
        require_ancestor_cleanup=args.require_ancestor_cleanup,
        require_single_main_worktree=args.require_single_main_worktree,
        require_pr_flow=args.require_pr_flow,
        expected_worktree_path=args.expected_worktree_path,
        automation_contract_path=args.automation_contract,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Codex publication audit: {report['status']}")
        for blocker in report["blockers"]:
            print(f"- {blocker}")
        dirty_summary = report.get("dirty_protected_summary")
        if dirty_summary:
            print(dirty_summary)
        single_main_summary = report.get("single_main_worktree", {}).get("summary")
        if single_main_summary:
            print(single_main_summary)
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
