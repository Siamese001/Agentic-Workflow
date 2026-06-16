"""Validate and run the Claude hook contract from Codex.

Claude Code owns the canonical hook matrix in ``.claude/settings.json``. Codex
does not get those hooks injected by the host, so this adapter verifies that the
registered hook targets exist and offers explicit runners for Codex preflight.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
SETTINGS_REL = Path(".claude/settings.json")
HOOK_TIMEOUT_SECONDS = 30

_PATH_RE = re.compile(r'([^\s"\']*\.(?:py|sh))')


@dataclass(frozen=True)
class HookRegistration:
    event: str
    matcher: str
    target: str
    command: str


@dataclass(frozen=True)
class HookRun:
    target: str
    returncode: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


def _read_json(path: Path) -> Mapping[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _target_from_command(command: str) -> str:
    match = _PATH_RE.search(command or "")
    if not match:
        return ""
    raw = match.group(1).strip().strip('"').strip("'")
    raw = raw.replace("${CLAUDE_PROJECT_DIR}", "").replace("$CLAUDE_PROJECT_DIR", "")
    raw = raw.lstrip("/\\").replace("\\", "/")
    return raw


def load_registered_hooks(root: Path = REPO_ROOT) -> list[HookRegistration]:
    """Load hook registrations from the repo-owned Claude settings file."""
    settings_path = root / SETTINGS_REL
    settings = _read_json(settings_path)
    registrations: list[HookRegistration] = []
    hooks_by_event = settings.get("hooks")
    if not isinstance(hooks_by_event, Mapping):
        return registrations
    for event, groups in hooks_by_event.items():
        if not isinstance(groups, list):
            continue
        for group in groups:
            if not isinstance(group, Mapping):
                continue
            matcher = str(group.get("matcher") or "")
            hooks = group.get("hooks")
            if not isinstance(hooks, list):
                continue
            for hook in hooks:
                if not isinstance(hook, Mapping):
                    continue
                command = str(hook.get("command") or "")
                registrations.append(
                    HookRegistration(
                        event=str(event),
                        matcher=matcher,
                        target=_target_from_command(command),
                        command=command,
                    )
                )
    return registrations


def validate_hook_matrix(root: Path = REPO_ROOT) -> list[str]:
    """Return failures for malformed settings registrations or missing hook targets.

    ``.claude/settings.json`` is the hook matrix SSOT. Codex validates the
    registered matrix; it does not maintain a copied required-hook registry.
    """
    failures: list[str] = []
    settings_path = root / SETTINGS_REL
    if not settings_path.is_file():
        return [f"{settings_path}: missing Claude settings hook matrix"]
    try:
        registrations = load_registered_hooks(root)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{settings_path}: unreadable hook matrix: {exc}"]

    for hook in registrations:
        if not hook.target:
            failures.append(f"{settings_path}: hook command has no script target: {hook.command!r}")
            continue
        target_path = root / hook.target
        if not target_path.is_file():
            matcher = f" matcher={hook.matcher!r}" if hook.matcher else ""
            failures.append(f"{settings_path}: {hook.event}{matcher} target missing -> {hook.target}")

    return failures


def _matcher_matches(matcher: str, tool_name: str) -> bool:
    if not matcher:
        return True
    try:
        return re.fullmatch(matcher, tool_name) is not None
    except re.error:
        return matcher == tool_name


def matching_hooks(
    root: Path,
    *,
    event: str,
    tool_name: str = "",
) -> list[HookRegistration]:
    hooks = []
    for hook in load_registered_hooks(root):
        if hook.event != event:
            continue
        if event in {"PreToolUse", "PostToolUse"} and not _matcher_matches(hook.matcher, tool_name):
            continue
        hooks.append(hook)
    return hooks


def _hook_env(root: Path, overrides: Mapping[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    pythonpath = [str(root), str(root / ".claude" / "hooks")]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env.update(
        {
            "CLAUDE_PROJECT_DIR": str(root),
            "PYTHONPATH": os.pathsep.join(pythonpath),
            "WORKTREE_IDE_OWNER": "codex",
        }
    )
    if overrides:
        env.update({str(key): str(value) for key, value in overrides.items()})
    return env


def run_hook_target(
    root: Path,
    target: str,
    payload: Mapping[str, Any],
    *,
    env_overrides: Mapping[str, str] | None = None,
    timeout: int = HOOK_TIMEOUT_SECONDS,
) -> HookRun:
    """Run a Python hook target with a Claude-shaped JSON payload."""
    target_path = root / target
    if target_path.suffix != ".py":
        return HookRun(target=target, returncode=0, stderr="non-python hook not executed")
    try:
        proc = subprocess.run(
            [sys.executable, str(target_path)],
            input=json.dumps(payload),
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=_hook_env(root, env_overrides),
        )
    except subprocess.TimeoutExpired as exc:
        return HookRun(
            target=target,
            returncode=1,
            stdout=str(exc.stdout or ""),
            stderr=str(exc.stderr or "hook timed out"),
            timed_out=True,
        )
    except OSError as exc:
        return HookRun(target=target, returncode=1, stderr=str(exc))
    return HookRun(target=target, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def run_event_hooks(
    root: Path,
    *,
    event: str,
    payload: Mapping[str, Any],
    tool_name: str = "",
    env_overrides: Mapping[str, str] | None = None,
) -> list[HookRun]:
    """Run all settings-registered Python hooks for an event/tool pair."""
    return [
        run_hook_target(root, hook.target, payload, env_overrides=env_overrides)
        for hook in matching_hooks(root, event=event, tool_name=tool_name)
    ]


def _git_branch(root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _expected_branch_guard_exit(root: Path) -> int:
    branch = _git_branch(root)
    if not branch:
        return 0
    if branch in {"main", "master"}:
        return 2
    if branch.startswith("codex-") and root.name == branch:
        return 0
    return 2


def _expected_north_star_exit(root: Path) -> int:
    state_path = root / "config" / "north_star_state.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
        if not state.get("enabled", True):
            return 0
        passing = int(state.get("lanes_passing", 0))
        total = int(state.get("lanes_total", 11))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return 0
    return 0 if passing >= total else 2


def _probe(
    root: Path,
    *,
    name: str,
    target: str,
    payload: Mapping[str, Any],
    expected_exit: int,
    env_overrides: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    run = run_hook_target(root, target, payload, env_overrides=env_overrides)
    status = "PASS" if run.returncode == expected_exit and not run.timed_out else "FAIL"
    return {
        "name": name,
        "status": status,
        "expected_exit": expected_exit,
        **asdict(run),
    }


def run_probe_suite(root: Path = REPO_ROOT) -> list[dict[str, Any]]:
    """Run bounded synthetic probes for the most important blocking hooks."""
    probe_plan_path = str(root / "plans" / f"__codex_hook_parity_probe_{os.getpid()}.md")
    return [
        _probe(
            root,
            name="branch_guard_current_worktree",
            target=".claude/hooks/before_file_edit_branch_guard.py",
            payload={
                "tool_name": "Edit",
                "tool_input": {"file_path": str(root / "scripts/governance/codex_hook_parity.py")},
            },
            expected_exit=_expected_branch_guard_exit(root),
        ),
        _probe(
            root,
            name="plan_mint_blocks_new_plan",
            target=".claude/hooks/pre_write_plan_mint_gate.py",
            payload={"tool_name": "Write", "tool_input": {"file_path": probe_plan_path}},
            expected_exit=2,
        ),
        _probe(
            root,
            name="north_star_blocks_off_star_when_unshipped",
            target=".claude/hooks/pre_write_north_star_gate.py",
            payload={
                "tool_name": "Edit",
                "tool_input": {"file_path": str(root / ".claude/hooks/__codex_hook_parity_probe.py")},
            },
            expected_exit=_expected_north_star_exit(root),
        ),
        _probe(
            root,
            name="stop_audit_blocks_missing_status_floor",
            target=".claude/hooks/stop_task_audit.py",
            payload={
                "session_id": "codex-hook-parity",
                "tool_info": {
                    "response": "Here is the work.\nFILES_CHANGED:\n- foo.py\nCOMMANDS_RUN:\n- ran it\n"
                },
            },
            expected_exit=2,
        ),
    ]


def build_report(root: Path = REPO_ROOT, *, run_probes: bool = True) -> dict[str, Any]:
    matrix_failures = validate_hook_matrix(root)
    probes = [] if matrix_failures or not run_probes else run_probe_suite(root)
    probe_failures = [probe for probe in probes if probe["status"] != "PASS"]
    status = "FAIL" if matrix_failures or probe_failures else "PASS"
    return {
        "schema_version": "codex-hook-parity/v1",
        "repo_root": str(root),
        "status": status,
        "matrix_failures": matrix_failures,
        "probes": probes,
    }


def _exit_for_runs(runs: Sequence[HookRun]) -> int:
    if any(run.returncode == 2 for run in runs):
        return 2
    if any(run.returncode != 0 or run.timed_out for run in runs):
        return 1
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root to inspect")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    subparsers = parser.add_subparsers(dest="command")

    check = subparsers.add_parser("check", help="Validate hook matrix and run bounded probes")
    check.add_argument("--no-probes", action="store_true", help="Only validate settings registrations")

    pre = subparsers.add_parser("run-pre-tool", help="Run matching PreToolUse hooks")
    pre.add_argument("tool_name", help="Claude tool name, for example Edit, Write, Bash, or mcp__memory__search_nodes")
    pre.add_argument("--file-path", help="Optional tool_input.file_path")
    pre.add_argument("--command", dest="tool_command", help="Optional tool_input.command")
    pre.add_argument("--bypass-north-star", action="store_true", help="Set NORTH_STAR_GATE_BYPASS=1 for this preflight")

    stop = subparsers.add_parser("run-stop", help="Run Stop hooks against a response file")
    stop.add_argument("response_file", type=Path, help="File containing the candidate final response")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    command = args.command or "check"
    root = args.root.resolve()

    if command == "check":
        report = build_report(root, run_probes=not getattr(args, "no_probes", False))
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(f"Codex hook parity: {report['status']}")
            for failure in report["matrix_failures"]:
                print(f"- FAIL {failure}")
            for probe in report["probes"]:
                print(f"- {probe['status']} {probe['name']}: exit {probe['returncode']} expected {probe['expected_exit']}")
        return 1 if report["status"] == "FAIL" else 0

    if command == "run-pre-tool":
        tool_input: dict[str, Any] = {}
        if args.file_path:
            tool_input["file_path"] = args.file_path
        if args.tool_command:
            tool_input["command"] = args.tool_command
        env = {"NORTH_STAR_GATE_BYPASS": "1"} if args.bypass_north_star else None
        runs = run_event_hooks(
            root,
            event="PreToolUse",
            tool_name=args.tool_name,
            payload={"tool_name": args.tool_name, "tool_input": tool_input},
            env_overrides=env,
        )
        payload = [asdict(run) for run in runs]
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for run in runs:
                print(f"{run.target}: exit {run.returncode}")
                if run.stderr.strip():
                    print(run.stderr.strip())
        return _exit_for_runs(runs)

    if command == "run-stop":
        response = args.response_file.read_text(encoding="utf-8")
        runs = run_event_hooks(
            root,
            event="Stop",
            payload={"session_id": "codex-stop-preflight", "tool_info": {"response": response}},
        )
        payload = [asdict(run) for run in runs]
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            for run in runs:
                print(f"{run.target}: exit {run.returncode}")
                if run.stderr.strip():
                    print(run.stderr.strip())
        return _exit_for_runs(runs)

    raise AssertionError(f"unhandled command {command!r}")


if __name__ == "__main__":
    raise SystemExit(main())
