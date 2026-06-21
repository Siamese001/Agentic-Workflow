"""Tests for the SessionStart shell hook."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
SESSION_START = REPO_ROOT / ".codex" / "hooks" / "session-start.sh"


def test_session_start_persists_gitkraken_path_into_claude_env_file() -> None:
    text = SESSION_START.read_text(encoding="utf-8")

    assert text.count("GITKRAKEN_GK_PATH") >= 2
    assert 'echo "export GITKRAKEN_GK_PATH=\\"$GITKRAKEN_GK_PATH\\""' in text


def test_session_start_persists_memory_db_into_claude_env_file() -> None:
    text = SESSION_START.read_text(encoding="utf-8")

    assert text.count("MEMORY_DB") >= 3
    assert 'export MEMORY_DB="$MEMORY_DB"' in text
    assert 'echo "export MEMORY_DB=\\"$MEMORY_DB\\""' in text
