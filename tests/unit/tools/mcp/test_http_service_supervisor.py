from __future__ import annotations

from pathlib import Path

from tools.mcp.http_service_supervisor import (
    HttpMcpServiceSpec,
    configure_http_mcp,
    preflight_payload,
    resolve_path,
)


class _Settings:
    host = "0.0.0.0"
    port = 1
    streamable_http_path = "/old"


class _Mcp:
    settings = _Settings()


def test_configure_http_mcp_sets_streamable_http_settings() -> None:
    mcp = _Mcp()

    configure_http_mcp(mcp, host="127.0.0.1", port=8765, path="/mcp")

    assert mcp.settings.host == "127.0.0.1"
    assert mcp.settings.port == 8765
    assert mcp.settings.streamable_http_path == "/mcp"


def test_preflight_payload_rejects_path_without_leading_slash() -> None:
    spec = HttpMcpServiceSpec(
        server_id="unit",
        module="unit.module",
        mcp_attr="mcp",
        default_host="127.0.0.1",
        default_port=1,
        default_path="/mcp",
        state_relative_path=Path("artifacts/mcp_heartbeat/unit.json"),
        service_log_relative_path=Path("artifacts/mcp/unit.jsonl"),
        required_tools=("unit_health",),
        preflight=lambda: {"status": "ok", "issues": []},
    )

    payload = preflight_payload(spec, host="127.0.0.1", port=8765, path="mcp")

    assert payload["status"] == "critical"
    assert payload["issues"] == ["streamable HTTP path must start with '/'"]


def test_resolve_path_keeps_absolute_path(tmp_path: Path) -> None:
    assert resolve_path(tmp_path / "x.json", Path("fallback.json")) == tmp_path / "x.json"
