"""Tests for scripts/governance/verify_codex_primary.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

import verify_codex_primary as mod  # noqa: E402


def _write(path: Path, text: str = "placeholder") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _valid_root(tmp_path: Path) -> Path:
    for relative in mod.REQUIRED_FILES:
        _write(tmp_path / relative)
    _write(
        tmp_path / "AGENTS.md",
        "\n".join(
            [
                "## Codex primary execution adapter",
                "docs/codex-primary-execution.md",
                "scripts/governance/audit_codex_mcp_transports.py",
                "scripts/governance/codex_readiness.py",
                "scripts/governance/verify_codex_run_receipt.py",
                "scripts/governance/verify_codex_primary.py",
                "GitKraken",
                "Codex must ask a plain-text clarifying question directly in the assistant response",
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
                "scripts/governance/verify_codex_run_receipt.py",
                "scripts/governance/verify_codex_primary.py",
                "No parallel registry",
                "Codex must ask a plain-text clarifying question directly in the assistant response",
            ]
        ),
    )
    return tmp_path


def test_valid_primary_contract_passes(tmp_path: Path) -> None:
    assert mod.validate(_valid_root(tmp_path)) == []


def test_missing_anchor_fails(tmp_path: Path) -> None:
    root = _valid_root(tmp_path)
    (root / "AGENTS.md").write_text("## Codex primary execution adapter\n", encoding="utf-8")

    failures = mod.validate(root)

    assert any("missing anchor" in failure for failure in failures)


@pytest.mark.parametrize(
    ("relative_path", "forbidden_phrase"),
    [
        ("docs/codex-primary-execution.md", "Claude hook parity"),
        ("docs/codex-primary-execution.md", "AskUserQuestion"),
        ("AGENTS.md", "request_user_input"),
    ],
)
def test_forbidden_phrase_fails(tmp_path: Path, relative_path: str, forbidden_phrase: str) -> None:
    root = _valid_root(tmp_path)
    path = root / relative_path
    path.write_text(path.read_text(encoding="utf-8") + f"\n{forbidden_phrase}\n", encoding="utf-8")

    failures = mod.validate(root)

    assert any("forbidden phrase" in failure for failure in failures)
