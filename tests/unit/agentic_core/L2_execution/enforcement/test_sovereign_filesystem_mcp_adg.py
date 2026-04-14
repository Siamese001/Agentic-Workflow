"""Targeted gap-closure tests for SovereignFilesystemMcp path-validation hardening.

Covers the newly hardened _validate_path logic:
- forbidden_path_patterns ('..' / '.env' / '/etc') raise PermissionError
- absolute paths raise PermissionError from _resolve_repo_relative_path
- a relative allowed path passes when _is_allowed_root returns True
"""

from __future__ import annotations

import pytest

_SOVEREIGN_FILESYSTEM_MCP = pytest.importorskip(
    "agentic_core.L2_execution.enforcement.sovereign_filesystem_mcp",
    reason="SovereignFilesystemMcp tests require agentic_core runtime modules",
)

SovereignFilesystemMcp = _SOVEREIGN_FILESYSTEM_MCP.SovereignFilesystemMcp


def _mcp(mission_id: str = "test-mission") -> SovereignFilesystemMcp:
    return SovereignFilesystemMcp(manager=None, mission_id=mission_id)  # type: ignore[arg-type]


def test_dotdot_in_path_raises_permission_error() -> None:
    mcp = _mcp()
    with pytest.raises(PermissionError, match="Sovereignty Breach"):
        mcp._validate_path("some/../../../etc/passwd")


def test_dotenv_in_path_raises_permission_error() -> None:
    mcp = _mcp()
    with pytest.raises(PermissionError, match="Sovereignty Breach"):
        mcp._validate_path("config/.env")


def test_etc_pattern_raises_permission_error() -> None:
    mcp = _mcp()
    with pytest.raises(PermissionError, match="Sovereignty Breach"):
        mcp._validate_path("/etc/hosts")


def test_absolute_path_raises_permission_error() -> None:
    mcp = _mcp()
    with pytest.raises(PermissionError, match="Sovereignty Breach"):
        mcp._validate_path("/absolute/path/to/file.txt")


def test_relative_allowed_path_passes(monkeypatch) -> None:
    mcp = _mcp()
    monkeypatch.setattr(mcp, "_is_allowed_root", lambda _resolved: True)
    result = mcp._validate_path("config/settings.yaml")
    assert isinstance(result, str)
    assert "settings.yaml" in result
