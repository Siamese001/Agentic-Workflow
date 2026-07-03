"""Single authority for local Codex main closeout.

The check is intentionally narrower than publication automation. It proves the
local repository ended in the desired state after publication. It reports two
separate closeout surfaces:

- publication closeout: local ``main`` equals ``origin/main``, the root
  working tree/index are clean, and no branch remains unmerged from
  ``origin/main``;
- workspace topology closeout: only the expected main worktree remains and no
  non-main local branches remain.

``--apply`` is conservative cleanup only. It may fast-forward clean local main
and delete clean, ancestor-contained non-main branches/worktrees. It never
resets, force-pushes, deletes dirty worktrees, deletes staging roots, or deletes
unmerged branches.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

GOVERNANCE_DIR = Path(__file__).resolve().parent
if str(GOVERNANCE_DIR) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE_DIR))

import worktree_hygiene  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class CloseoutIssue:
    code: str
    detail: str


@dataclass(frozen=True)
class CloseoutAction:
    action: str
    detail: str
    status: str


def _local_branches(root: Path) -> tuple[list[str], CloseoutIssue | None]:
    rc, stdout, stderr = worktree_hygiene.run_git(
        "branch",
        "--format=%(refname:short)",
        cwd=root,
    )
    if rc != 0:
        return [], CloseoutIssue("local_branch_list_failed", stderr)
    return [line.strip() for line in stdout.splitlines() if line.strip()], None


def _worktrees(root: Path) -> tuple[list[dict[str, str]], CloseoutIssue | None]:
    rc, stdout, stderr = worktree_hygiene.run_git("worktree", "list", "--porcelain", cwd=root)
    if rc != 0:
        return [], CloseoutIssue("worktree_list_failed", stderr)
    return worktree_hygiene.parse_worktrees(stdout), None


def _is_ancestor(root: Path, ref: str, base_ref: str) -> bool:
    rc, _, _ = worktree_hygiene.run_git("merge-base", "--is-ancestor", ref, base_ref, cwd=root)
    return rc == 0


def _status_rows(path: Path) -> tuple[list[str], CloseoutIssue | None]:
    rc, stdout, stderr = worktree_hygiene.run_git("status", "--short", cwd=path)
    if rc != 0:
        return [], CloseoutIssue("worktree_status_failed", f"{path}: {stderr}")
    return [line for line in stdout.splitlines() if line.strip()], None


def _extra_local_branch_issues(root: Path) -> list[CloseoutIssue]:
    branches, issue = _local_branches(root)
    if issue:
        return [issue]
    extra = [branch for branch in branches if branch != "main"]
    if not extra:
        return []
    return [CloseoutIssue("extra_local_branches", "\n".join(extra))]


def _publication_closeout_issues(root: Path, *, base_ref: str) -> list[CloseoutIssue]:
    issues: list[CloseoutIssue] = []

    rc_branch, branch, branch_err = worktree_hygiene.run_git("rev-parse", "--abbrev-ref", "HEAD", cwd=root)
    if rc_branch != 0:
        issues.append(CloseoutIssue("current_branch_failed", branch_err))
    elif branch != "main":
        issues.append(CloseoutIssue("not_on_main", f"expected=main actual={branch}"))

    rc_status, status, status_err = worktree_hygiene.run_git("status", "--short", "--branch", cwd=root)
    if rc_status != 0:
        issues.append(CloseoutIssue("status_failed", status_err))
    else:
        dirty_rows = [line for line in status.splitlines() if line and not line.startswith("##")]
        if dirty_rows:
            issues.append(CloseoutIssue("dirty_status", "\n".join(dirty_rows)))
        conflicted = [
            line
            for line in dirty_rows
            if line[:2] in {"AA", "DD", "UU", "AU", "UA", "DU", "UD"}
        ]
        if conflicted:
            issues.append(CloseoutIssue("conflicted_status", "\n".join(conflicted)))

    rc_diff, _, diff_err = worktree_hygiene.run_git("diff", "--quiet", cwd=root)
    if rc_diff != 0:
        issues.append(CloseoutIssue("unstaged_diff", diff_err or "git diff --quiet reported changes"))

    rc_cached, _, cached_err = worktree_hygiene.run_git("diff", "--cached", "--quiet", cwd=root)
    if rc_cached != 0:
        issues.append(CloseoutIssue("staged_diff", cached_err or "git diff --cached --quiet reported changes"))

    rc_head, head, head_err = worktree_hygiene.run_git("rev-parse", "--verify", "HEAD", cwd=root)
    rc_base, base, base_err = worktree_hygiene.run_git("rev-parse", "--verify", base_ref, cwd=root)
    if rc_head != 0:
        issues.append(CloseoutIssue("head_missing", head_err))
    if rc_base != 0:
        issues.append(CloseoutIssue("base_ref_missing", f"{base_ref}: {base_err}"))
    if rc_head == 0 and rc_base == 0 and head != base:
        issues.append(CloseoutIssue("head_not_base_ref", f"HEAD={head} {base_ref}={base}"))

    rc_unmerged, unmerged, unmerged_err = worktree_hygiene.run_git(
        "branch",
        "--no-merged",
        base_ref,
        "--format=%(refname:short)",
        cwd=root,
    )
    if rc_unmerged != 0:
        issues.append(CloseoutIssue("unmerged_branch_check_failed", unmerged_err))
    elif unmerged.strip():
        issues.append(CloseoutIssue("unmerged_branches", unmerged))

    return issues


def _workspace_topology_issues(
    root: Path,
    *,
    expected_path: Path,
    base_ref: str,
) -> list[CloseoutIssue]:
    verifier_issues = worktree_hygiene.verify_single_main_worktree(
        root,
        expected_path=expected_path,
        base_ref=base_ref,
        fetch=False,
    )
    publication_issue_codes = {
        "conflicted_status",
        "dirty_status",
        "head_missing",
        "head_not_base_ref",
        "base_ref_missing",
        "staged_diff",
        "status_failed",
        "unmerged_branch_check_failed",
        "unmerged_branches",
        "unstaged_diff",
    }
    return [
        CloseoutIssue(issue.code, issue.detail)
        for issue in verifier_issues
        if issue.code not in publication_issue_codes
    ]


def _section(name: str, issues: list[CloseoutIssue], *, required: bool, rule: str) -> dict:
    return {
        "name": name,
        "status": "FAIL" if issues else "PASS",
        "required": required,
        "issues": [asdict(issue) for issue in issues],
        "rule": rule,
    }


def _fast_forward_main(root: Path, base_ref: str) -> tuple[list[CloseoutAction], list[CloseoutIssue]]:
    actions: list[CloseoutAction] = []
    issues: list[CloseoutIssue] = []

    rc_branch, branch, branch_err = worktree_hygiene.run_git("rev-parse", "--abbrev-ref", "HEAD", cwd=root)
    if rc_branch != 0:
        return actions, [CloseoutIssue("current_branch_failed", branch_err)]
    if branch != "main":
        return actions, [CloseoutIssue("not_on_main", f"expected=main actual={branch}")]

    rc_head, head, head_err = worktree_hygiene.run_git("rev-parse", "--verify", "HEAD", cwd=root)
    rc_base, base, base_err = worktree_hygiene.run_git("rev-parse", "--verify", base_ref, cwd=root)
    if rc_head != 0:
        issues.append(CloseoutIssue("head_missing", head_err))
    if rc_base != 0:
        issues.append(CloseoutIssue("base_ref_missing", f"{base_ref}: {base_err}"))
    if issues or head == base:
        return actions, issues

    if not _is_ancestor(root, "HEAD", base_ref):
        issues.append(CloseoutIssue("main_not_fast_forwardable", f"HEAD={head} {base_ref}={base}"))
        return actions, issues

    rc_merge, stdout, stderr = worktree_hygiene.run_git("merge", "--ff-only", base_ref, cwd=root)
    status = "applied" if rc_merge == 0 else "failed"
    detail = stdout or stderr or f"merge --ff-only {base_ref}"
    actions.append(CloseoutAction("fast_forward_main", detail, status))
    if rc_merge != 0:
        issues.append(CloseoutIssue("fast_forward_main_failed", detail))
    return actions, issues


def _remove_safe_extra_worktrees(
    root: Path,
    *,
    expected_path: Path,
    base_ref: str,
) -> tuple[list[CloseoutAction], list[CloseoutIssue]]:
    actions: list[CloseoutAction] = []
    issues: list[CloseoutIssue] = []
    worktrees, issue = _worktrees(root)
    if issue:
        return actions, [issue]

    expected = expected_path.resolve()
    for row in worktrees:
        path_text = row.get("path", "")
        if not path_text:
            issues.append(CloseoutIssue("worktree_path_missing", repr(row)))
            continue
        path = Path(path_text).resolve()
        if path == expected:
            continue

        dirty_rows, dirty_issue = _status_rows(path)
        if dirty_issue:
            issues.append(dirty_issue)
            continue
        if dirty_rows:
            issues.append(CloseoutIssue("dirty_extra_worktree", f"{path}: " + "\n".join(dirty_rows)))
            continue

        branch = row.get("branch", "")
        head = row.get("head", "")
        proof_ref = branch if branch and branch != "DETACHED" else head
        if not proof_ref:
            issues.append(CloseoutIssue("extra_worktree_missing_ref", str(path)))
            continue
        if not _is_ancestor(root, proof_ref, base_ref):
            issues.append(CloseoutIssue("extra_worktree_not_merged", f"{proof_ref} @ {path}"))
            continue

        rc_remove, stdout, stderr = worktree_hygiene.run_git("worktree", "remove", str(path), cwd=root)
        status = "applied" if rc_remove == 0 else "failed"
        detail = stdout or stderr or str(path)
        actions.append(CloseoutAction("remove_extra_worktree", detail, status))
        if rc_remove != 0:
            issues.append(CloseoutIssue("remove_extra_worktree_failed", detail))

    return actions, issues


def _delete_safe_extra_branches(root: Path, *, base_ref: str) -> tuple[list[CloseoutAction], list[CloseoutIssue]]:
    actions: list[CloseoutAction] = []
    issues: list[CloseoutIssue] = []

    worktrees, worktree_issue = _worktrees(root)
    if worktree_issue:
        return actions, [worktree_issue]
    checked_out = {row.get("branch", "") for row in worktrees if row.get("branch")}

    branches, branch_issue = _local_branches(root)
    if branch_issue:
        return actions, [branch_issue]

    for branch in branches:
        if branch == "main":
            continue
        if branch in checked_out:
            issues.append(CloseoutIssue("branch_checked_out", branch))
            continue
        if not _is_ancestor(root, branch, base_ref):
            issues.append(CloseoutIssue("unmerged_local_branch", branch))
            continue
        rc_delete, stdout, stderr = worktree_hygiene.run_git("branch", "-d", branch, cwd=root)
        status = "applied" if rc_delete == 0 else "failed"
        detail = stdout or stderr or branch
        actions.append(CloseoutAction("delete_merged_local_branch", detail, status))
        if rc_delete != 0:
            issues.append(CloseoutIssue("delete_merged_local_branch_failed", detail))

    return actions, issues


def apply_main_closeout(
    root: Path,
    *,
    expected_path: Path,
    base_ref: str,
    fetch: bool,
) -> tuple[list[CloseoutAction], list[CloseoutIssue]]:
    actions: list[CloseoutAction] = []
    issues: list[CloseoutIssue] = []

    if fetch:
        rc_fetch, stdout, stderr = worktree_hygiene.run_git("fetch", "origin", "--prune", cwd=root)
        status = "applied" if rc_fetch == 0 else "failed"
        detail = stdout or stderr or "git fetch origin --prune"
        actions.append(CloseoutAction("fetch_origin_prune", detail, status))
        if rc_fetch != 0:
            return actions, [CloseoutIssue("fetch_failed", detail)]

    for step in (
        lambda: _remove_safe_extra_worktrees(root, expected_path=expected_path, base_ref=base_ref),
        lambda: _fast_forward_main(root, base_ref),
        lambda: _delete_safe_extra_branches(root, base_ref=base_ref),
    ):
        step_actions, step_issues = step()
        actions.extend(step_actions)
        issues.extend(step_issues)

    return actions, issues


def build_closeout_report(
    root: Path,
    *,
    expected_path: Path | None = None,
    base_ref: str = "origin/main",
    fetch: bool = False,
    apply: bool = False,
) -> dict:
    root = root.resolve()
    expected = (expected_path or root).resolve()

    actions: list[CloseoutAction] = []
    apply_issues: list[CloseoutIssue] = []
    if apply:
        actions, apply_issues = apply_main_closeout(root, expected_path=expected, base_ref=base_ref, fetch=fetch)
    elif fetch:
        rc_fetch, _, stderr = worktree_hygiene.run_git("fetch", "origin", "--prune", cwd=root)
        if rc_fetch != 0:
            apply_issues = [CloseoutIssue("fetch_failed", stderr)]

    publication_issues = [
        *_publication_closeout_issues(root, base_ref=base_ref),
        *(issue for issue in apply_issues if issue.code == "fetch_failed"),
    ]
    workspace_topology_issues = [
        *_workspace_topology_issues(root, expected_path=expected, base_ref=base_ref),
        *_extra_local_branch_issues(root),
        *(issue for issue in apply_issues if issue.code != "fetch_failed"),
    ]
    publication_closeout = _section(
        "publication_closeout",
        publication_issues,
        required=True,
        rule=(
            "Publication closeout requires local main == origin/main, a clean root "
            "worktree/index, and no branch unmerged from the base ref."
        ),
    )
    workspace_topology_closeout = _section(
        "workspace_topology_closeout",
        workspace_topology_issues,
        required=True,
        rule=(
            "Workspace topology closeout requires exactly one expected main worktree "
            "and no non-main local branches."
        ),
    )
    issues = [*publication_issues, *workspace_topology_issues]
    return {
        "schema_version": "codex-main-closeout/v1",
        "status": "FAIL" if issues else "PASS",
        "mode": "apply" if apply else "check",
        "repo_root": str(root),
        "expected_path": str(expected),
        "base_ref": base_ref,
        "publication_closeout": publication_closeout,
        "workspace_topology_closeout": workspace_topology_closeout,
        "issues": [asdict(issue) for issue in issues],
        "actions": [asdict(action) for action in actions],
        "rule": (
            "Strict closeout requires both publication closeout and workspace topology closeout to pass."
        ),
    }


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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Read-only closeout check. This is the default mode.")
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Safely fast-forward main and remove clean ancestor-contained extra branches/worktrees.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument(
        "--publication-only",
        action="store_true",
        help="Use publication_closeout, not strict topology closeout, for the process exit code.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_closeout_report(
        args.root,
        expected_path=args.expected_path,
        base_ref=args.base_ref,
        fetch=args.fetch,
        apply=args.apply,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"codex-main-closeout: {report['status']}")
        for action in report["actions"]:
            print(f"- {action['action']} [{action['status']}]: {action['detail']}")
        for issue in report["issues"]:
            print(f"- {issue['code']}: {issue['detail']}")
    status_key = "publication_closeout" if args.publication_only else None
    status = report[status_key]["status"] if status_key else report["status"]
    return 1 if status == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
