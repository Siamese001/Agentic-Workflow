"""Validate GitHub workflow/action references.

The default CI posture is changed-file-first: validate only workflow/action
files touched by the diff so this migration does not fail PRs for stale
untouched YAML. Use ``--all`` for full inventory checks.
"""

from __future__ import annotations

import argparse
import dataclasses
import fnmatch
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs pyyaml; fallback keeps local message useful.
    yaml = None


WORKFLOW_GLOBS = (".github/workflows/*.yml", ".github/workflows/*.yaml")
ACTION_GLOB = ".github/actions/**/action.yml"
CHECKABLE_PREFIXES = (".github/workflows/", ".github/actions/")

DELETED_REFERENCES = {
    ".github/workflows/r1b-terminal-smoke.yml",
    ".github/workflows/runtime-spine-smoke.yml",
    ".github/workflows/uwg-block-smoke.yml",
    ".github/actions/common-setup",
    "r1b-terminal-smoke",
    "runtime-spine-smoke",
    "uwg-block-smoke",
    "Guardian Tests (Mandatory)",
    "Author-Gate Harness HITL",
    "old Windsurf Governance Health Check",
}

OLD_GUARDIAN_MODULES = {
    "agentic_core.L0_routing.guardian",
    "agentic_core.guardian_tests",
    "tests.guardian.old_",
}


@dataclasses.dataclass(frozen=True)
class Issue:
    path: Path
    message: str
    line: int | None = None

    def format(self) -> str:
        location = str(self.path).replace("\\", "/")
        if self.line is not None:
            location = f"{location}:{self.line}"
        return f"{location}: {self.message}"


def _run_git(root: Path, args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=30,
        shell=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def _repo_relative(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        try:
            return path.resolve().relative_to(root.resolve())
        except ValueError:
            return path
    return Path(raw_path.replace("\\", "/"))


def _all_checkable_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in WORKFLOW_GLOBS:
        files.extend(root.glob(pattern))
    files.extend(root.glob(ACTION_GLOB))
    return sorted({p.relative_to(root) for p in files if p.is_file()})


def _is_checkable(path: Path) -> bool:
    as_posix = path.as_posix()
    return as_posix.startswith(CHECKABLE_PREFIXES) and (
        fnmatch.fnmatch(as_posix, ".github/workflows/*.yml")
        or fnmatch.fnmatch(as_posix, ".github/workflows/*.yaml")
        or fnmatch.fnmatch(as_posix, ".github/actions/**/action.yml")
    )


def changed_files(root: Path, args: argparse.Namespace) -> list[Path]:
    if args.all:
        return _all_checkable_files(root)

    if args.changed_files:
        return [_repo_relative(root, p) for p in args.changed_files]

    if args.base_sha and args.head_sha:
        return [_repo_relative(root, p) for p in _run_git(root, ["diff", "--name-only", args.base_sha, args.head_sha])]

    if args.base_ref:
        _run_git(root, ["fetch", "--no-tags", "--depth=1", "origin", args.base_ref])
        return [_repo_relative(root, p) for p in _run_git(root, ["diff", "--name-only", f"origin/{args.base_ref}...HEAD"])]

    if args.changed_only:
        return [_repo_relative(root, p) for p in _run_git(root, ["diff", "--name-only", "HEAD"])]

    return _all_checkable_files(root)


def _load_workflow(text: str) -> dict:
    if yaml is None:
        return {}
    try:
        data = yaml.load(text, Loader=yaml.BaseLoader)
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _event_config(workflow: dict) -> object:
    if "on" in workflow:
        return workflow["on"]
    return workflow.get(True, {})


def _has_event(workflow: dict, event: str) -> bool:
    on_config = _event_config(workflow)
    if isinstance(on_config, str):
        return on_config == event
    if isinstance(on_config, list):
        return event in on_config
    if isinstance(on_config, dict):
        return event in on_config
    return False


def _event_has_paths(workflow: dict, event: str) -> bool:
    on_config = _event_config(workflow)
    if not isinstance(on_config, dict):
        return False
    event_config = on_config.get(event)
    return isinstance(event_config, dict) and ("paths" in event_config or "paths-ignore" in event_config)


def _strip_comment_lines(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def _line_number(text: str, needle: str) -> int | None:
    for index, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return index
    return None


def _path_exists(root: Path, token: str) -> bool:
    cleaned = token.strip().strip("'\"").rstrip(",")
    if not cleaned or cleaned.startswith("-") or "${{" in cleaned or "$" in cleaned:
        return True
    if cleaned.startswith("./"):
        cleaned = cleaned[2:]
    if any(ch in cleaned for ch in "*?["):
        return any(root.glob(cleaned))
    return (root / cleaned).exists()


def _extract_pytest_paths(text: str) -> Iterable[str]:
    command_text = text.replace("\\\n", " ")
    for match in re.finditer(r"(?:python\s+-m\s+pytest|pytest)\s+([^\n;&|]+)", command_text):
        try:
            tokens = shlex.split(match.group(1), posix=True)
        except ValueError:
            continue
        for token in tokens:
            if token.startswith("-") or "=" in token:
                continue
            if token.startswith("tests/") or token.endswith(".py"):
                yield token


def _extract_python_script_paths(text: str) -> Iterable[str]:
    for match in re.finditer(r"\bpython(?:3)?\s+(?!-m\b)(?!- <<)([A-Za-z0-9_./\\-]+\.py)\b", text):
        yield match.group(1).replace("\\", "/")


def _workflow_jobs(workflow: dict) -> dict:
    jobs = workflow.get("jobs", {})
    return jobs if isinstance(jobs, dict) else {}


def _validate_file(root: Path, path: Path) -> list[Issue]:
    absolute = root / path
    if not absolute.exists():
        return []

    text = absolute.read_text(encoding="utf-8")
    text_no_comments = _strip_comment_lines(text)
    workflow = _load_workflow(text)
    issues: list[Issue] = []

    if "requirements.txt" in text_no_comments and not (root / "requirements.txt").exists():
        issues.append(Issue(path, "references requirements.txt, but requirements.txt is absent", _line_number(text, "requirements.txt")))

    if "./.github/actions/common-setup" in text_no_comments or ".github/actions/common-setup" in text_no_comments:
        issues.append(Issue(path, "references deleted common-setup action", _line_number(text, "common-setup")))

    for match in re.finditer(r"uses:\s+(\./\.github/actions/[^\s#]+)", text_no_comments):
        local_action = match.group(1).split("@", 1)[0]
        action_file = root / local_action[2:] / "action.yml"
        if not action_file.exists():
            issues.append(Issue(path, f"uses missing local action {local_action}", _line_number(text, match.group(0))))

    for script_path in _extract_python_script_paths(text_no_comments):
        if not _path_exists(root, script_path):
            issues.append(Issue(path, f"runs missing python script {script_path}", _line_number(text, script_path)))

    for pytest_path in _extract_pytest_paths(text_no_comments):
        if not _path_exists(root, pytest_path):
            issues.append(Issue(path, f"runs pytest against missing path {pytest_path}", _line_number(text, pytest_path)))

    has_pr = _has_event(workflow, "pull_request")
    has_schedule = _has_event(workflow, "schedule")
    has_changes_job = "changes" in _workflow_jobs(workflow)
    has_changed_file_command = "--changed-only" in text_no_comments or "--changed-files" in text_no_comments

    if has_pr and not _event_has_paths(workflow, "pull_request") and not has_changes_job and not has_changed_file_command:
        issues.append(Issue(path, "has broad pull_request trigger without paths or a changes job"))

    if re.search(r"github\.event_name\s*(?:==|=)\s*['\"]schedule['\"]", text_no_comments) and not has_schedule:
        issues.append(Issue(path, "contains schedule event logic but has no on.schedule trigger", _line_number(text, "schedule")))

    if re.search(r"github\.event_name\s*(?:==|=)\s*['\"]pull_request['\"]", text_no_comments) and not has_pr:
        issues.append(Issue(path, "contains pull_request event logic but has no on.pull_request trigger", _line_number(text, "pull_request")))

    if "pull-requests: write" in text_no_comments and not has_pr:
        issues.append(Issue(path, "requests pull-requests: write without an on.pull_request trigger", _line_number(text, "pull-requests: write")))

    for deleted in sorted(DELETED_REFERENCES):
        if deleted in text_no_comments:
            issues.append(Issue(path, f"references deleted or retired workflow/action name {deleted}", _line_number(text, deleted)))

    for old_guardian in sorted(OLD_GUARDIAN_MODULES):
        if old_guardian in text_no_comments:
            issues.append(Issue(path, f"references old guardian module path {old_guardian}", _line_number(text, old_guardian)))

    return issues


def find_reference_issues(root: Path, files: Iterable[Path]) -> list[Issue]:
    issues: list[Issue] = []
    for path in sorted({_repo_relative(root, str(p)) for p in files}):
        if not _is_checkable(path):
            continue
        issues.extend(_validate_file(root, path))
    return issues


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--changed-only", action="store_true", help="validate only changed workflow/action files")
    mode.add_argument("--all", action="store_true", help="validate all workflow/action files")
    parser.add_argument("--base-sha")
    parser.add_argument("--head-sha")
    parser.add_argument("--base-ref")
    parser.add_argument("--changed-files", nargs="*")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path.cwd()
    try:
        selected = changed_files(root, args)
    except RuntimeError as exc:
        print(f"workflow reference check failed to compute changed files: {exc}", file=sys.stderr)
        return 2

    issues = find_reference_issues(root, selected)
    if issues:
        for issue in issues:
            print(f"::error file={issue.path.as_posix()}::{issue.format()}")
        print(f"workflow reference check failed: {len(issues)} issue(s)")
        return 1

    checked = [p.as_posix() for p in selected if _is_checkable(p) and (root / p).exists()]
    if checked:
        print("workflow reference check passed for:")
        for path in checked:
            print(f"  - {path}")
    else:
        print("workflow reference check passed: no changed workflow/action files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
