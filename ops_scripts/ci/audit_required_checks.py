"""Audit the branch-protection required-check manifest.

This is intentionally read-only. By default it validates the repo-local target
manifest in ``.github/workflow-config.yaml`` against active job check names.
Use ``--live`` to compare the same target with GitHub branch protection via the
``gh`` CLI when authenticated.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - CI installs pyyaml via python-setup minimal.
    yaml = None


DEFAULT_CONFIG = Path(".github/workflow-config.yaml")


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("pyyaml is required to audit required checks")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise RuntimeError(f"{path} must contain a YAML mapping")
    return data


def _job_display_name(job_key: str, job: object) -> str:
    if isinstance(job, dict) and job.get("name"):
        return str(job["name"])
    return job_key


def active_check_contexts(root: Path) -> set[str]:
    contexts: set[str] = set()
    for workflow_path in sorted((root / ".github" / "workflows").glob("*.yml")):
        workflow = _load_yaml(workflow_path)
        jobs = workflow.get("jobs", {})
        if not isinstance(jobs, dict):
            continue
        for job_key, job in jobs.items():
            contexts.add(_job_display_name(str(job_key), job))
    return contexts


def required_checks(config: dict) -> list[str]:
    protection = config.get("branch_protection", {})
    if not isinstance(protection, dict):
        return []
    values = protection.get("required_checks", [])
    if not isinstance(values, list):
        raise RuntimeError("branch_protection.required_checks must be a list")
    return [str(value) for value in values]


def removed_checks(config: dict) -> list[str]:
    protection = config.get("branch_protection", {})
    if not isinstance(protection, dict):
        return []
    values = protection.get("remove_required_checks", [])
    if not isinstance(values, list):
        raise RuntimeError("branch_protection.remove_required_checks must be a list")
    return [str(value) for value in values]


def _run_gh_json(args: list[str], root: Path) -> dict:
    result = subprocess.run(
        ["gh", *args],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=30,
        shell=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gh command failed")
    return json.loads(result.stdout or "{}")


def _repo_slug(root: Path) -> str:
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=30,
        shell=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError("could not read remote.origin.url")
    remote = result.stdout.strip()
    if remote.endswith(".git"):
        remote = remote[:-4]
    if remote.startswith("git@github.com:"):
        return remote.removeprefix("git@github.com:")
    if "github.com/" in remote:
        return remote.split("github.com/", 1)[1]
    raise RuntimeError(f"unsupported GitHub remote URL: {remote}")


def live_required_contexts(root: Path, branch: str) -> set[str]:
    repo = _repo_slug(root)
    payload = _run_gh_json(
        ["api", f"repos/{repo}/branches/{branch}/protection/required_status_checks"],
        root,
    )
    contexts = payload.get("contexts", [])
    if not isinstance(contexts, list):
        raise RuntimeError("GitHub protection response did not contain a contexts list")
    return {str(context) for context in contexts}


def _print_list(title: str, values: Iterable[str]) -> None:
    print(title)
    for value in sorted(values):
        print(f"  - {value}")


def audit_local(root: Path, config: dict) -> int:
    active = active_check_contexts(root)
    required = set(required_checks(config))
    removed = set(removed_checks(config))

    missing = required - active
    conflicting = required & removed
    if missing:
        _print_list("Required checks not produced by active workflows:", missing)
    if conflicting:
        _print_list("Checks listed as both required and removed:", conflicting)

    if missing or conflicting:
        return 1

    _print_list("Required checks validated against active workflows:", required)
    return 0


def audit_live(root: Path, config: dict, branch: str, strict: bool) -> int:
    desired = set(required_checks(config))
    remove = set(removed_checks(config))
    current = live_required_contexts(root, branch)
    missing = desired - current
    extra = current - desired
    stale = current & remove

    if missing:
        _print_list("Missing required checks in live branch protection:", missing)
    if extra:
        _print_list("Live required checks outside target manifest:", extra)
    if stale:
        _print_list("Live branch protection still requires retired checks:", stale)

    if not missing and not extra and not stale:
        print(f"Live branch protection for {branch} matches .github/workflow-config.yaml.")
        return 0

    print("GitHub settings update needed; this script is read-only.")
    return 1 if strict else 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--live", action="store_true", help="compare manifest to live GitHub branch protection")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--strict-live", action="store_true", help="make live drift exit non-zero")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path.cwd()
    try:
        config = _load_yaml(root / args.config)
        local_code = audit_local(root, config)
        if local_code != 0:
            return local_code
        if args.live:
            return audit_live(root, config, args.branch, args.strict_live)
        return 0
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"required-check audit failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
