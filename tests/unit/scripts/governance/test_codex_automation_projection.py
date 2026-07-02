"""Tests for scripts/governance/codex_automation_projection.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import codex_automation_projection as projection  # noqa: E402
import verify_codex_enforcement_home as enforcement_home  # noqa: E402


def _write(path: Path, text: str = "placeholder") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _handoff_toml_block(automation_id: str) -> str:
    expected = enforcement_home.ADG_HANDOFF_CONTRACTS.get(automation_id)
    if expected is None:
        return ""
    lines = ["", "[handoff]"]
    for field, value in expected.items():
        lines.append(f"{field} = {json.dumps(value)}")
    return "\n".join(lines)


def _automation_toml(automation_id: str, root: Path, *, cron: bool = True) -> str:
    escaped_root = str(root).replace("\\", "\\\\")
    prompt = "approved prompt"
    if automation_id == "weekly-adg-audit-and-burndown":
        prompt = "\\n".join(enforcement_home.ADG_REQUIRED_PROMPT_SNIPPETS)
    if cron:
        return "\n".join(
            [
                "version = 1",
                f'id = "{automation_id}"',
                'kind = "cron"',
                f'name = "{automation_id}"',
                f'prompt = "{prompt}"',
                'status = "ACTIVE"',
                'rrule = "RRULE:FREQ=WEEKLY;BYHOUR=22;BYMINUTE=0;BYDAY=SU,MO,TU,WE,TH,FR,SA"',
                'model = "gpt-5.4-mini"',
                'reasoning_effort = "xhigh"',
                'execution_environment = "local"',
                f'cwds = ["{escaped_root}"]',
            ]
        ) + _handoff_toml_block(automation_id)
    return "\n".join(
        [
            "version = 1",
            f'id = "{automation_id}"',
            'kind = "manual"',
            f'name = "{automation_id}"',
            'prompt = "approved prompt"',
            'status = "ON_DEMAND"',
            'model = "gpt-5.4-mini"',
            'reasoning_effort = "xhigh"',
            'execution_environment = "local"',
            f'cwds = ["{escaped_root}"]',
        ]
    )


def test_projection_report_excludes_manual_automation(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    monkeypatch.setattr(
        enforcement_home,
        "AUTOMATION_IDS",
        ("on-demand-pr-main-publisher", "weekly-adg-audit-and-burndown"),
    )
    _write(enforcement_home._automation_path(root, "on-demand-pr-main-publisher"), _automation_toml("on-demand-pr-main-publisher", root, cron=False))
    _write(enforcement_home._automation_path(root, "weekly-adg-audit-and-burndown"), _automation_toml("weekly-adg-audit-and-burndown", root))

    report = projection.build_report(root=root, user_codex_home=tmp_path / "user-codex", write_user_profile=False)

    assert "weekly-adg-audit-and-burndown" in report["expected_projection_ids"]
    assert "on-demand-pr-main-publisher" not in report["expected_projection_ids"]


def test_write_user_profile_projection_is_validator_compliant(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "repo"
    user_codex_home = tmp_path / "user-codex"
    monkeypatch.setattr(enforcement_home, "AUTOMATION_IDS", ("weekly-adg-audit-and-burndown",))
    monkeypatch.setattr(enforcement_home, "REPO_SKILL_IDS", ())
    _write(enforcement_home._automation_path(root, "weekly-adg-audit-and-burndown"), _automation_toml("weekly-adg-audit-and-burndown", root))

    written = projection.write_user_profile_projections(root=root, user_codex_home=user_codex_home)

    assert len(written) == 1
    assert enforcement_home.validate(root, user_codex_home) == []
