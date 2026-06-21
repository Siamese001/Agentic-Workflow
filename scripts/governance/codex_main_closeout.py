"""Single authority for local Codex main closeout.

The check is intentionally narrower than publication automation. It proves the
local repository ended in the desired state after publication:

- local ``main`` equals ``origin/main``;
- the working tree and index are clean;
- only the expected main worktree remains;
- no non-main local branches remain.

``--apply`` is conservative cleanup only. It may fast-forward clean local main
and delete clean, ancestor-contained non-main branches/worktrees. It never
resets, force-pushes, deletes dirty worktrees, or deletes unmerged branches.
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

    verifier_issues = worktree_hygiene.verify_single_main_worktree(
        root,
        expected_path=expected,
        base_ref=base_ref,
        fetch=fetch and not apply,
    )
    issues = [
        *(CloseoutIssue(issue.code, issue.detail) for issue in verifier_issues),
        *_extra_local_branch_issues(root),
        *apply_issues,
    ]
    return {
        "schema_version": "codex-main-closeout/v1",
        "status": "FAIL" if issues else "PASS",
        "mode": "apply" if apply else "check",
        "repo_root": str(root),
        "expected_path": str(expected),
        "base_ref": base_ref,
        "issues": [asdict(issue) for issue in issues],
        "actions": [asdict(action) for action in actions],
        "rule": (
            "Closeout requires local main == origin/main, a clean worktree and index, "
            "exactly one expected main worktree, and no non-main local branches."
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
    return 1 if report["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
