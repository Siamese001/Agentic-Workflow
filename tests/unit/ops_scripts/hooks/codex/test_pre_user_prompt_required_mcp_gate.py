"""Tests for the per-turn required MCP transport gate."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
GATE_PATH = REPO_ROOT / ".codex" / "governance" / "scripts" / "pre_user_prompt_required_mcp_gate.py"

_spec = importlib.util.spec_from_file_location("_required_mcp_gate_under_test", GATE_PATH)
assert _spec is not None and _spec.loader is not None
gate = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gate
_spec.loader.exec_module(gate)


def _write_config(path: Path, servers: dict[str, dict[str, Any]]) -> Path:
    path.write_text(json.dumps({"mcpServers": servers}), encoding="utf-8")
    return path


def _payload(prompt: str = "refactor this feature") -> str:
    return json.dumps({"session_id": "s1", "prompt": prompt})


def _callability_green(_servers: tuple[str, ...]) -> list:
    return []


def test_all_enabled_repo_mcps_must_probe_green(tmp_path: Path, monkeypatch) -> None:
    config = _write_config(
        tmp_path / ".mcp.json",
        {
            "adg_sqlite": {"command": "python", "args": ["-m", "server"]},
            "memory": {"command": "python", "args": ["server.py"]},
            "deepwiki": {"url": "https://example.test/mcp"},
            "disabled_one": {"command": "python", "disabled": True},
        },
    )
    monkeypatch.delenv(gate.SERVER_LIST_ENV, raising=False)
    seen: list[tuple[str, str]] = []

    def probe(spec: gate.ProbeSpec, timeout: float) -> gate.ProbeResult:
        seen.append((spec.server_id, spec.transport))
        return gate.ProbeResult(spec.server_id, "ok", transport=spec.transport, tools_count=1)

    assert (
        gate.run_gate(
            _payload(),
            config_path=config,
            probe_func=probe,
            callability_check_func=_callability_green,
            timeout=0.1,
        )
        == 0
    )

    assert sorted(seen) == [
        ("adg_sqlite", "stdio"),
        ("deepwiki", "http"),
        ("memory", "stdio"),
    ]


def test_any_red_required_mcp_blocks(tmp_path: Path, capsys, monkeypatch) -> None:
    config = _write_config(
        tmp_path / ".mcp.json",
        {
            "adg_sqlite": {"command": "python"},
            "memory": {"command": "python"},
        },
    )
    monkeypatch.delenv(gate.SERVER_LIST_ENV, raising=False)

    def probe(spec: gate.ProbeSpec, timeout: float) -> gate.ProbeResult:
        if spec.server_id == "memory":
            return gate.ProbeResult(spec.server_id, "fail", "connection closed", spec.transport)
        return gate.ProbeResult(spec.server_id, "ok", transport=spec.transport, tools_count=1)

    assert (
        gate.run_gate(
            _payload(),
            config_path=config,
            probe_func=probe,
            callability_check_func=_callability_green,
            timeout=0.1,
        )
        == 2
    )
    err = capsys.readouterr().err
    assert "BLOCKED" in err
    assert "memory" in err
    assert "connection closed" in err


def test_protocol_green_still_blocks_when_callability_route_red(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    config = _write_config(tmp_path / ".mcp.json", {"memory": {"command": "python"}})
    monkeypatch.delenv(gate.SERVER_LIST_ENV, raising=False)
    monkeypatch.delenv(gate.CALLABILITY_SERVER_LIST_ENV, raising=False)

    def probe(spec: gate.ProbeSpec, timeout: float) -> gate.ProbeResult:
        return gate.ProbeResult(spec.server_id, "ok", transport=spec.transport, tools_count=1)

    def callability_check(required_servers: tuple[str, ...]) -> list[gate.ProbeResult]:
        assert required_servers == gate.DEFAULT_CALLABILITY_REQUIRED_SERVERS
        assert "vector_db" in required_servers
        return [
            gate.ProbeResult(
                "memory",
                "fail",
                "classification=PROCESS_ONLY",
                "codex-route",
            )
        ]

    assert (
        gate.run_gate(
            _payload(),
            config_path=config,
            probe_func=probe,
            callability_check_func=callability_check,
            timeout=0.1,
        )
        == 2
    )
    err = capsys.readouterr().err
    assert "memory" in err
    assert "classification=PROCESS_ONLY" in err


def test_mcp_repair_prompt_allows_without_probing(tmp_path: Path, monkeypatch, capsys) -> None:
    config = _write_config(tmp_path / ".mcp.json", {"adg_sqlite": {"command": "python"}})
    monkeypatch.delenv(gate.SERVER_LIST_ENV, raising=False)
    monkeypatch.delenv(gate.DISABLE_REPAIR_BYPASS_ENV, raising=False)

    def probe(_spec: gate.ProbeSpec, _timeout: float) -> gate.ProbeResult:
        raise AssertionError("repair prompts must not require a green transport first")

    assert (
        gate.run_gate(
            _payload("debug and fix MCP transport RCA"),
            config_path=config,
            probe_func=probe,
            timeout=0.1,
        )
        == 0
    )
    assert "repair/RCA prompt" in capsys.readouterr().err


def test_mcp_green_health_words_do_not_bypass_without_repair_intent(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    config = _write_config(tmp_path / ".mcp.json", {"adg_sqlite": {"command": "python"}})
    monkeypatch.delenv(gate.SERVER_LIST_ENV, raising=False)
    monkeypatch.delenv(gate.DISABLE_REPAIR_BYPASS_ENV, raising=False)

    def probe(spec: gate.ProbeSpec, _timeout: float) -> gate.ProbeResult:
        return gate.ProbeResult(spec.server_id, "fail", "transport closed", spec.transport)

    assert (
        gate.run_gate(
            _payload("prove MCP fleet green and healthy"),
            config_path=config,
            probe_func=probe,
            callability_check_func=_callability_green,
            timeout=0.1,
        )
        == 2
    )
    err = capsys.readouterr().err
    assert "BLOCKED" in err
    assert "transport closed" in err


def test_disable_repair_bypass_forces_probe_even_for_explicit_repair_prompt(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    config = _write_config(tmp_path / ".mcp.json", {"adg_sqlite": {"command": "python"}})
    monkeypatch.delenv(gate.SERVER_LIST_ENV, raising=False)
    monkeypatch.setenv(gate.DISABLE_REPAIR_BYPASS_ENV, "1")

    def probe(spec: gate.ProbeSpec, _timeout: float) -> gate.ProbeResult:
        return gate.ProbeResult(spec.server_id, "fail", "transport closed", spec.transport)

    assert (
        gate.run_gate(
            _payload("MCP_REPAIR: repair MCP transport"),
            config_path=config,
            probe_func=probe,
            callability_check_func=_callability_green,
            timeout=0.1,
        )
        == 2
    )
    err = capsys.readouterr().err
    assert "BLOCKED" in err
    assert "transport closed" in err


def test_missing_auth_passthrough_env_blocks_before_spawn(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    config = _write_config(
        tmp_path / ".mcp.json",
        {
            "notion": {
                "command": "cmd",
                "args": ["/c", "npx", "-y", "@notionhq/notion-mcp-server"],
                "env": {"NOTION_TOKEN": "${NOTION_TOKEN}"},
            }
        },
    )
    monkeypatch.delenv("NOTION_TOKEN", raising=False)
    monkeypatch.delenv(gate.SERVER_LIST_ENV, raising=False)

    assert gate.run_gate(_payload(), config_path=config, timeout=0.1) == 2
    err = capsys.readouterr().err
    assert "notion" in err
    assert "NOTION_TOKEN" in err


def test_server_filter_env_limits_required_set(tmp_path: Path, monkeypatch) -> None:
    config = _write_config(
        tmp_path / ".mcp.json",
        {
            "adg_sqlite": {"command": "python"},
            "memory": {"command": "python"},
        },
    )
    monkeypatch.setenv(gate.SERVER_LIST_ENV, "memory")
    seen: list[str] = []

    def probe(spec: gate.ProbeSpec, timeout: float) -> gate.ProbeResult:
        seen.append(spec.server_id)
        return gate.ProbeResult(spec.server_id, "ok", transport=spec.transport, tools_count=1)

    assert (
        gate.run_gate(
            _payload(),
            config_path=config,
            probe_func=probe,
            callability_check_func=_callability_green,
            timeout=0.1,
        )
        == 0
    )
    assert seen == ["memory"]


def test_sse_http_messages_parse_tools_list() -> None:
    text = (
        "event: message\r\n"
        'data: {"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"ask_question"}]}}\r\n'
        "\r\n"
    )

    messages = gate._json_messages_from_text(text)
    tools, reason = gate._tools_from_messages(messages)

    assert reason == ""
    assert tools == [{"name": "ask_question"}]


def test_before_submit_prompt_dispatches_required_mcp_gate() -> None:
    hook_text = (REPO_ROOT / ".codex" / "hooks" / "before_submit_prompt.py").read_text(
        encoding="utf-8"
    )

    assert "pre_user_prompt_required_mcp_gate.py" in hook_text
    assert "_run_required_mcp_gate" in hook_text
