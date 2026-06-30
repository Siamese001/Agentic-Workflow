"""Tests for scripts/governance/verify_codex_primary.py."""

from __future__ import annotations

import sys
import json
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_primary as mod  # noqa: E402


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
            'model = "gpt-5.5"',
            'reasoning_effort = "xhigh"',
            'execution_environment = "local"',
            f'cwds = ["{escaped_root}"]',
            "created_at = 1",
            "updated_at = 1",
        ]
    )


def _valid_root(tmp_path: Path) -> Path:
    for relative in mod.REQUIRED_FILES:
        _write(tmp_path / relative)
    _write(
        tmp_path / ".codex" / "automations" / "on-demand-pr-main-publisher" / "automation.toml",
        _automation_toml(
            "on-demand-pr-main-publisher",
            "\n".join(mod.verify_codex_enforcement_home.PUBLICATION_REQUIRED_PROMPT_SNIPPETS),
            tmp_path,
        ),
    )
    _write(
        tmp_path / ".codex" / "automations" / "weekly-adg-audit-and-burndown" / "automation.toml",
        _automation_toml(
            "weekly-adg-audit-and-burndown",
            "\n".join(mod.verify_codex_enforcement_home.ADG_REQUIRED_PROMPT_SNIPPETS),
            tmp_path,
        ),
    )
    _write(
        tmp_path / ".codex" / "automations" / "adg-p0-blocker-burndown" / "automation.toml",
        _automation_toml(
            "adg-p0-blocker-burndown",
            "\n".join(mod.verify_codex_enforcement_home.ADG_P0_REQUIRED_PROMPT_SNIPPETS),
            tmp_path,
        ),
    )
    _write(
        tmp_path / ".codex" / "automations" / "adg-p1-ratchet-burndown" / "automation.toml",
        _automation_toml(
            "adg-p1-ratchet-burndown",
            "\n".join(mod.verify_codex_enforcement_home.ADG_P1_REQUIRED_PROMPT_SNIPPETS),
            tmp_path,
        ),
    )
    _write(tmp_path / ".codex" / "hooks.json", json.dumps({"hooks": {}}))
    _write(
        tmp_path / "AGENTS.md",
        "\n".join(
            [
                "## Codex primary execution adapter",
                "docs/codex-primary-execution.md",
                "scripts/governance/audit_codex_mcp_transports.py",
                "scripts/governance/codex_readiness.py",
                "scripts/governance/codex_main_closeout.py",
                "scripts/governance/verify_codex_enforcement_home.py",
                "scripts/governance/verify_codex_run_receipt.py",
                "scripts/governance/verify_codex_primary.py",
                "GitKraken",
                "Codex must ask a plain-text clarifying question directly in the assistant response",
                ".codex/hooks.json",
                ".codex/automations/",
            ]
        ),
    )
    _write(
        tmp_path / "docs/codex-primary-execution.md",
        "\n".join(
            [
                "Codex primary execution surface",
                "GitKraken",
                "scripts/governance/audit_codex_mcp_transports.py",
                "scripts/governance/codex_readiness.py",
                "scripts/governance/codex_main_closeout.py",
                "scripts/governance/verify_codex_enforcement_home.py",
                "scripts/governance/verify_codex_run_receipt.py",
                "scripts/governance/verify_codex_primary.py",
                "No parallel registry",
                "Codex must ask a plain-text clarifying question directly in the assistant response",
                ".codex/hooks.json",
                ".codex/automations/",
            ]
        ),
    )
    return tmp_path


def test_valid_primary_contract_passes(tmp_path: Path) -> None:
    assert mod.validate(_valid_root(tmp_path), repo_only=True) == []


def test_parse_args_accepts_repo_only_flag() -> None:
    args = mod.parse_args(["--repo-only"])

    assert args.repo_only is True
    assert args.root == mod.REPO_ROOT


def test_repo_only_skips_enforcement_home_checks(tmp_path: Path, monkeypatch) -> None:
    root = _valid_root(tmp_path)
    monkeypatch.setattr(
        mod.verify_codex_enforcement_home,
        "validate",
        lambda _root: [SimpleNamespace(code="sentinel", detail="boom")],
    )

    assert mod.validate(root, repo_only=True) == []
    assert any("sentinel" in failure for failure in mod.validate(root))


def test_missing_anchor_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    (root / "AGENTS.md").write_text("## Codex primary execution adapter\n", encoding="utf-8")

    failures = mod.validate(root)

    assert any("missing anchor" in failure for failure in failures)
