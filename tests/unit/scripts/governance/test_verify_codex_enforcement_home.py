"""Tests for scripts/governance/verify_codex_enforcement_home.py."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_enforcement_home as mod  # noqa: E402


def _write(path: Path, text: str = "placeholder") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _automation_toml(automation_id: str, prompt: str, root: Path) -> str:
    escaped_prompt = prompt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    escaped_root = str(root).replace("\\", "\\\\")
    return "\n".join(
        [
            "version = 1",
            f'id = "{automation_id}"',
            'kind = "cron"',
            f'name = "{automation_id}"',
            f'prompt = "{escaped_prompt}"',
            'status = "ACTIVE"',
            'rrule = "RRULE:FREQ=WEEKLY;BYHOUR=22;BYMINUTE=0;BYDAY=SU,MO,TU,WE,TH,FR,SA"',
            'model = "gpt-5.4-mini"',
            'reasoning_effort = "xhigh"',
            'execution_environment = "local"',
            f'cwds = ["{escaped_root}"]',
            "created_at = 1",
            "updated_at = 1",
        ]
    )


def _publication_prompt() -> str:
    return "\n".join(mod.PUBLICATION_REQUIRED_PROMPT_SNIPPETS)


def _adg_prompt() -> str:
    return "\n".join(mod.ADG_REQUIRED_PROMPT_SNIPPETS)


def _adg_p0_p1_prompt() -> str:
    return "\n".join(mod.ADG_P0_P1_REQUIRED_PROMPT_SNIPPETS)


def _valid_root(tmp_path: Path) -> Path:
    prompt_by_id = {
        "on-demand-pr-main-publisher": _publication_prompt(),
        "weekly-adg-audit-and-burndown": _adg_prompt(),
        "adg-p0-p1-burndown": _adg_p0_p1_prompt(),
    }
    for automation_id in mod.AUTOMATION_IDS:
        _write(
            mod._automation_path(tmp_path, automation_id),
            _automation_toml(automation_id, prompt_by_id.get(automation_id, "placeholder prompt"), tmp_path),
        )
    for skill_id in mod.REPO_SKILL_IDS:
        _write(tmp_path / ".codex" / "skills" / skill_id / "SKILL.md")
    return tmp_path


def test_repo_owned_enforcement_passes(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    user_codex_home = tmp_path / "user-codex"

    assert mod.validate(root, user_codex_home) == []


def test_user_profile_automation_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    _write(user_codex_home / "automations" / "on-demand-pr-main-publisher" / "automation.toml")

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_repo_local_singular_automation_tree_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    _write(root / ".codex" / "automation" / "misplaced.toml")

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "repo_duplicate_enforcement_home" for issue in issues)


def test_user_profile_skill_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path / "repo")
    user_codex_home = tmp_path / "user-codex"
    _write(user_codex_home / "skills" / "agentic-workflow-governance" / "SKILL.md")

    issues = mod.validate(root, user_codex_home)

    assert any(issue.code == "user_profile_enforcement_artifact" for issue in issues)


def test_publication_prompt_requires_strict_single_main_contract(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    automation.write_text(
        _automation_toml("on-demand-pr-main-publisher", "HEAD == origin/main", root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_prompt_missing" for issue in issues)


def test_publication_prompt_rejects_obsolete_dirty_success_wording(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = root / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml"
    automation.write_text(
        _automation_toml(
            "on-demand-pr-main-publisher",
            _publication_prompt() + "\ndirty protected worktrees reported and preserved",
            root,
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "publication_prompt_obsolete" for issue in issues)


def test_wrong_cwd_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "weekly-adg-audit-and-burndown")
    automation.write_text(
        _automation_toml("weekly-adg-audit-and-burndown", _adg_prompt(), tmp_path / "other"),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "automation_cwd" for issue in issues)
