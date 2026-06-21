"""Tests for Codex MCP Python heartbeat process-marker matching."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / ".codex" / "governance" / "scripts"))

import mcp_python_heartbeat as mod  # noqa: E402


def test_placeholder_marker_matches_resolved_memory_process(monkeypatch) -> None:
    monkeypatch.setenv("AGENTIC_REPO_ROOT", "C:/Git/Agentic-Workflow-FRESH")

    marker = "${AGENTIC_REPO_ROOT}/tools/memory/adg_memory_server.py"
    command_line = (
        '"C:\\Users\\amita\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" '
        "-u C:/Git/Agentic-Workflow-FRESH/tools/memory/adg_memory_server.py"
    )

    assert mod._marker_matches_process(marker, command_line) is True


def test_env_placeholder_marker_matches_windows_slash_process(monkeypatch) -> None:
    monkeypatch.setenv("AGENTIC_REPO_ROOT", "C:/Git/Agentic-Workflow-FRESH")

    marker = "${env:AGENTIC_REPO_ROOT}\\tools\\memory\\adg_memory_server.py"
    command_line = (
        '"C:\\Users\\amita\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" '
        "-u C:\\Git\\Agentic-Workflow-FRESH\\tools\\memory\\adg_memory_server.py"
    )

    assert mod._marker_matches_process(marker, command_line) is True


def test_vector_marker_matches_by_python_script_basename(monkeypatch) -> None:
    monkeypatch.setenv("AGENTIC_REPO_ROOT", "C:/Git/Agentic-Workflow-FRESH")

    marker = "${AGENTIC_REPO_ROOT}/tools/mcp/vector_db_server.py"
    command_line = (
        '"C:\\Users\\amita\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" '
        "-u C:/temporary/mcp/vector_db_server.py"
    )

    assert mod._marker_matches_process(marker, command_line) is True
