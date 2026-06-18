"""Tests that the legacy compatibility island has been removed."""

from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


def test_root_legacy_compat_files_are_gone() -> None:
    assert not (REPO_ROOT / "CLAUDE.md").exists()
    assert not (REPO_ROOT / "apps_rg" / "CLAUDE.md").exists()
    assert not (REPO_ROOT / "docs" / "codex-backup-adapter.md").exists()
    assert not (REPO_ROOT / "scripts" / "governance" / "codex_hook_parity.py").exists()
    assert not (REPO_ROOT / "scripts" / "governance" / "verify_codex_backup.py").exists()
