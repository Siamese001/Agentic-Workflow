from __future__ import annotations

import os

from tools.mcp import launch_adg_sqlite_http_mcp, launch_memory_http_mcp


def test_adg_http_launcher_spec_uses_expected_route_and_tools() -> None:
    spec = launch_adg_sqlite_http_mcp.SPEC

    assert spec.default_port == 8765
    assert spec.default_path == "/mcp"
    assert "adg_health" in spec.required_tools
    assert "adg_process_identity" in spec.required_tools
    assert "adg_runtime_info" in spec.required_tools


def test_memory_http_launcher_spec_uses_expected_route_and_tools() -> None:
    spec = launch_memory_http_mcp.SPEC

    assert spec.default_port == 8766
    assert spec.default_path == "/mcp"
    assert spec.required_tools == ("memory_health", "mem_process_identity")


def test_memory_preflight_requires_redis(monkeypatch) -> None:
    monkeypatch.delenv("ADG_REDIS_URL", raising=False)

    result = launch_memory_http_mcp.memory_preflight_status()

    assert result["status"] == "critical"
    assert "ADG_REDIS_URL is required for memory MCP startup" in result["issues"]


def test_memory_preflight_accepts_configured_redis(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("ADG_REDIS_URL", "redis://127.0.0.1:6379/0")
    monkeypatch.setenv("MEMORY_DB", str(tmp_path / "memory.sqlite"))

    result = launch_memory_http_mcp.memory_preflight_status()

    assert result["status"] == "ok"
    assert result["redis"]["configured"] is True

