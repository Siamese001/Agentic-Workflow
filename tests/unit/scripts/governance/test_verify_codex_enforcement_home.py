"""Tests for scripts/governance/verify_codex_enforcement_home.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_enforcement_home as mod  # noqa: E402


def _write(path: Path, text: str = "placeholder") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _handoff_toml_block(automation_id: str, **overrides: object) -> str:
    expected = mod.ADG_HANDOFF_CONTRACTS.get(automation_id)
    if expected is None:
        return ""
    handoff = dict(expected)
    handoff.update(overrides)
    lines = ["", "[handoff]"]
    for field in expected:
        lines.append(f"{field} = {json.dumps(handoff[field])}")
    return "\n".join(lines)


def _automation_toml(
    automation_id: str,
    prompt: str,
    root: Path,
    **handoff_overrides: object,
) -> str:
    escaped_prompt = prompt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    escaped_root = str(root).replace("\\", "\\\\")
    text = "\n".join(
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
    return text + _handoff_toml_block(automation_id, **handoff_overrides)


def _publication_prompt() -> str:
    return "\n".join(mod.PUBLICATION_REQUIRED_PROMPT_SNIPPETS)


def _adg_prompt() -> str:
    return "\n".join(mod.ADG_REQUIRED_PROMPT_SNIPPETS)


def _adg_p0_p1_prompt() -> str:
    return "\n".join(mod.ADG_P0_P1_REQUIRED_PROMPT_SNIPPETS)


def _adg_p2_prompt() -> str:
    return "\n".join(mod.ADG_P2_REQUIRED_PROMPT_SNIPPETS)


def _adg_p3_prompt() -> str:
    return "\n".join(mod.ADG_P3_REQUIRED_PROMPT_SNIPPETS)


def _valid_root(tmp_path: Path) -> Path:
    prompt_by_id = {
        "on-demand-pr-main-publisher": _publication_prompt(),
        "weekly-adg-audit-and-burndown": _adg_prompt(),
        "adg-p0-p1-burndown": _adg_p0_p1_prompt(),
        "adg-bcg-p2-next-action": _adg_p2_prompt(),
        "adg-p3-promotion-hygiene": _adg_p3_prompt(),
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


def test_adg_handoff_graph_requires_producer_to_unblock_p0_p1(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "weekly-adg-audit-and-burndown")
    automation.write_text(
        _automation_toml(
            "weekly-adg-audit-and-burndown",
            _adg_prompt(),
            root,
            unblocks=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)
    assert any(issue.code == "adg_handoff_graph_edge" for issue in issues)


def test_adg_handoff_graph_requires_p0_p1_to_unblock_p2(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-p0-p1-burndown")
    automation.write_text(
        _automation_toml(
            "adg-p0-p1-burndown",
            _adg_p0_p1_prompt(),
            root,
            unblocks=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)
    assert any(issue.code == "adg_handoff_graph_edge" for issue in issues)


def test_adg_handoff_graph_requires_p2_to_depend_on_p0_p1(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-bcg-p2-next-action")
    automation.write_text(
        _automation_toml(
            "adg-bcg-p2-next-action",
            _adg_p2_prompt(),
            root,
            depends_on=["weekly-adg-audit-and-burndown"],
            requires_prior_lane_clean=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)
    assert any(issue.code == "adg_handoff_graph_dependency" for issue in issues)


def test_adg_handoff_graph_requires_p2_to_unblock_p3(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-bcg-p2-next-action")
    automation.write_text(
        _automation_toml(
            "adg-bcg-p2-next-action",
            _adg_p2_prompt(),
            root,
            unblocks=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)
    assert any(issue.code == "adg_handoff_graph_edge" for issue in issues)


def test_adg_handoff_graph_requires_p3_to_wait_for_p2_not_actionable(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-p3-promotion-hygiene")
    automation.write_text(
        _automation_toml(
            "adg-p3-promotion-hygiene",
            _adg_p3_prompt(),
            root,
            requires_prior_lane_not_actionable=[],
        ),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_handoff_contract" for issue in issues)


def test_p2_prompt_requires_p0_p1_clean_same_generation_gate(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-bcg-p2-next-action")
    automation.write_text(
        _automation_toml("adg-bcg-p2-next-action", "artifact_status=certified or artifact_status=repair_ready", root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_p2_prompt_missing" for issue in issues)


def test_p3_prompt_requires_p2_precedence_gate(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    automation = mod._automation_path(root, "adg-p3-promotion-hygiene")
    automation.write_text(
        _automation_toml("adg-p3-promotion-hygiene", "artifact_status=certified or artifact_status=repair_ready", root),
        encoding="utf-8",
    )

    issues = mod.validate(root, tmp_path / "user-codex")

    assert any(issue.code == "adg_p3_prompt_missing" for issue in issues)
