"""Tests that the legacy Claude governance island has been removed."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def test_root_legacy_compat_files_are_gone() -> None:
    assert not (REPO_ROOT / ("." + "claude")).exists()
    assert (REPO_ROOT / "AGENTS.md").exists()
    assert (REPO_ROOT / "docs" / "codex-primary-execution.md").exists()
    assert (REPO_ROOT / ".codex" / "hooks.json").exists()
    assert not (REPO_ROOT / "scripts" / "governance" / "codex_hook_parity.py").exists()
    assert not (REPO_ROOT / "scripts" / "governance" / "verify_codex_backup.py").exists()
