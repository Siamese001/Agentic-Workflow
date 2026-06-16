"""Tests for scripts/governance/verify_codex_backup.py."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_backup as mod  # noqa: E402


def _write(path: Path, text: str = "placeholder") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _repo_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for relative in mod.REQUIRED_REPO_FILES:
        _write(root / relative)
    _write(
        root / "AGENTS.md",
        "\n".join(
            [
                "## Codex backup adapter",
                "CLAUDE.md",
                "agentic-workflow-governance",
                "scripts/governance/verify_codex_backup.py",
                ".claude/rules/plan-first-enforcement.md",
                ".claude/rules/plan-location.md",
            ]
        ),
    )
    _write(
        root / "docs/codex-backup-adapter.md",
        "\n".join(
            [
                ".claude/rules/windows-path-budget.md",
                ".claude/rules/plan-first-enforcement.md",
                ".claude/rules/plan-location.md",
                ".claude/templates/execution-plan-template.md",
                "scripts/governance/check_windows_path_budget.py",
                "scripts/governance/audit_codex_mcp_transports.py",
                ".claude/skills/structured-reasoning/SKILL.md",
                ".claude/skills/mcp-integration/SKILL.md",
                "agentic-workflow-verification",
            ]
        ),
    )
    _write(root / ".claude/settings.json", json.dumps({"hooks": {}}))
    return root


def test_missing_personal_skills_are_advisory_by_default(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    monkeypatch.setattr(mod, "REPO_ROOT", _repo_root(tmp_path))
    monkeypatch.setattr(mod, "CODEX_SKILLS_ROOT", tmp_path / "missing-skills")

    assert mod.main([]) == 0

    out = capsys.readouterr().out
    assert "Codex backup adapter verification passed" in out
    assert "Codex skill advisory warnings" in out


def test_missing_personal_skills_fail_in_strict_mode(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mod, "REPO_ROOT", _repo_root(tmp_path))
    monkeypatch.setattr(mod, "CODEX_SKILLS_ROOT", tmp_path / "missing-skills")

    assert mod.main(["--require-personal-skills"]) == 1


def test_repo_only_skips_personal_skill_warnings(monkeypatch, tmp_path: Path, capsys) -> None:
    monkeypatch.setattr(mod, "REPO_ROOT", _repo_root(tmp_path))
    monkeypatch.setattr(mod, "CODEX_SKILLS_ROOT", tmp_path / "missing-skills")

    assert mod.main(["--repo-only"]) == 0

    out = capsys.readouterr().out
    assert "codex skills: skipped (--repo-only)" in out
    assert "advisory warnings" not in out
