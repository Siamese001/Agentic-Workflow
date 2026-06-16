"""Tests for scripts/governance/codex_hook_parity.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import codex_hook_parity as mod  # noqa: E402


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


HOOK_SPECS: tuple[tuple[str, str, str], ...] = (
    ("PreToolUse", "Edit|Write|MultiEdit", ".claude/hooks/before_file_edit_branch_guard.py"),
    ("PreToolUse", "Bash", ".claude/hooks/before_shell_execution.py"),
    ("Stop", "", ".claude/hooks/stop_task_audit.py"),
)


def _write_hook_settings(root: Path, *, missing_target: str = "") -> None:
    groups: dict[tuple[str, str], list[str]] = {}
    for event, matcher, target in HOOK_SPECS:
        if target != missing_target:
            _write(root / target, "print('hook')\n")
        groups.setdefault((event, matcher), []).append(target)

    settings_hooks: dict[str, list[dict]] = {}
    for (event, matcher), targets in groups.items():
        group = {
            "hooks": [
                {
                    "type": "command",
                    "command": (
                        f'"$CLAUDE_PROJECT_DIR/{target}"'
                        if target.endswith(".sh")
                        else f'python "$CLAUDE_PROJECT_DIR/{target}"'
                    ),
                }
                for target in targets
            ]
        }
        if matcher:
            group["matcher"] = matcher
        settings_hooks.setdefault(event, []).append(group)
    _write(root / ".claude/settings.json", json.dumps({"hooks": settings_hooks}))


def test_validate_hook_matrix_accepts_required_settings(tmp_path: Path) -> None:
    _write_hook_settings(tmp_path)

    assert mod.validate_hook_matrix(tmp_path) == []


def test_validate_hook_matrix_allows_removed_hook_registration(tmp_path: Path) -> None:
    _write_hook_settings(tmp_path)
    settings = json.loads((tmp_path / ".claude/settings.json").read_text(encoding="utf-8"))
    settings["hooks"]["PreToolUse"] = [
        group
        for group in settings["hooks"]["PreToolUse"]
        if group.get("matcher") != "Bash"
    ]
    _write(tmp_path / ".claude/settings.json", json.dumps(settings))

    assert mod.validate_hook_matrix(tmp_path) == []


def test_validate_hook_matrix_reports_registered_missing_target(tmp_path: Path) -> None:
    _write_hook_settings(tmp_path, missing_target=".claude/hooks/before_shell_execution.py")

    failures = mod.validate_hook_matrix(tmp_path)

    assert any("before_shell_execution.py" in failure for failure in failures)


def test_matching_hooks_uses_tool_matcher(tmp_path: Path) -> None:
    _write_hook_settings(tmp_path)

    hooks = mod.matching_hooks(tmp_path, event="PreToolUse", tool_name="Edit")

    targets = {hook.target for hook in hooks}
    assert ".claude/hooks/before_file_edit_branch_guard.py" in targets
    assert ".claude/hooks/before_shell_execution.py" not in targets


def test_build_report_skips_probes_when_matrix_fails(tmp_path: Path) -> None:
    _write_hook_settings(tmp_path, missing_target=".claude/hooks/before_shell_execution.py")

    report = mod.build_report(tmp_path)

    assert report["status"] == "FAIL"
    assert report["matrix_failures"]
    assert report["probes"] == []


def test_parse_run_pre_tool_preserves_subcommand_when_tool_command_present() -> None:
    args = mod.parse_args(
        [
            "run-pre-tool",
            "Bash",
            "--command",
            "pytest",
        ]
    )

    assert args.command == "run-pre-tool"
    assert args.tool_command == "pytest"
