"""Tests for repo MCP config sync helper."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SYNC_PATH = Path(__file__).resolve().parents[3] / ".codex" / "governance" / "scripts" / "sync_mcp_config.py"

_spec = importlib.util.spec_from_file_location("_sync_mcp_config_under_test", _SYNC_PATH)
assert _spec is not None and _spec.loader is not None
sync_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = sync_mod
_spec.loader.exec_module(sync_mod)


def _repo_data() -> dict:
    return {
        "mcpServers": {
            "GitKraken": {
                "command": "${GITKRAKEN_GK_PATH}",
                "args": ["mcp", "--readonly"],
            },
            "filesystem": {
                "command": "node",
                "args": ["${env:AGENTIC_REPO_ROOT}/.codex/governance/scripts/filesystem_mcp_launcher.js"],
            },
            "memory": {
                "command": "python",
                "args": ["-u", "-m", "tools.mcp.launch_memory_mcp"],
                "env": {
                    "AGENTIC_REPO_ROOT": "${AGENTIC_REPO_ROOT}",
                    "MEMORY_DB": "${MEMORY_DB}",
                },
            },
            "notion": {
                "command": "cmd",
                "args": ["/c", "npx", "-y", "@notionhq/notion-mcp-server"],
                "env": {"NOTION_TOKEN": "${NOTION_TOKEN}"},
            },
            "context7": {"url": "https://mcp.context7.com/mcp"},
            "playwright": {
                "command": "cmd",
                "args": ["/c", "npx", "-y", "@playwright/mcp"],
            },
        }
    }


def test_validate_config_accepts_repo_data() -> None:
    assert sync_mod.validate_config(_repo_data()) == []


def test_sync_global_config_writes_alternate_path(tmp_path: Path) -> None:
    target = tmp_path / "editor.toml"

    assert sync_mod.sync_global_config(_repo_data(), global_path=target) is True
    assert json.loads(target.read_text(encoding="utf-8")) == _repo_data()


def test_sync_global_config_noop_when_target_is_repo_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    same_path = tmp_path / ".mcp.json"
    same_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(sync_mod, "repo_config", same_path)

    assert sync_mod.sync_global_config(_repo_data(), global_path=same_path) is False


def test_run_check_only_reports_ok(capsys: pytest.CaptureFixture[str]) -> None:
    assert sync_mod.run(check_only=True) == 0

    captured = capsys.readouterr().out
    assert "[mcp_sync] OK:" in captured


def test_run_dry_run_reports_actions(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    agents_path = tmp_path / "AGENTS.md"
    agents_path.write_text("stub", encoding="utf-8")
    monkeypatch.setattr(sync_mod, "repo_config", tmp_path / ".mcp.json")
    monkeypatch.setattr(sync_mod, "agents_md", agents_path)
    monkeypatch.setattr(sync_mod, "load_repo_config", lambda: _repo_data())

    assert sync_mod.run(dry_run=True) == 0

    captured = capsys.readouterr().out
    assert "[mcp_sync] DRY RUN:" in captured
    assert "would refresh" in captured
