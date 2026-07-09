"""Tests for pre_user_prompt_adg_ssot_gate.py — ADG SQLite-SSOT green-light gate.

Plan: adg-redis-hotcache-enforcement-b9f4c2.

Contract under test:
  - SQLite SSOT is the authority: T2/T3 + SSOT red (no readable snapshot) → exit 2.
  - ADG MCP transport must be open for ordinary T2/T3 prompts.
  - Read-only analysis/recommendation prompts may proceed from SQLite SSOT with degraded provenance.
  - Explicit ADG transport recovery/RCA prompts may proceed while transport is closed.
  - Redis is a non-authoritative hot cache: cold/absent Redis → advisory only, exit 0.
  - T0/T1 prompts are never gated, even when the SSOT is red.
  - Bypass env and empty/invalid input fail open (exit 0).
  - Both payload shapes ({"prompt": ...} and {"tool_info": {"prompt": ...}}) parse.
"""

from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".codex" / "governance/scripts"))

import pre_user_prompt_adg_ssot_gate as gate  # noqa: E402
import mcp_callability_epoch as epoch  # noqa: E402


def _run(
    payload_json: str,
    *,
    sqlite_red: bool = False,
    redis_up: bool = True,
    adg_hot: bool = True,
    transport_open: bool = True,
    transport_status: str = "open",
) -> int:
    with patch("sys.stdin", StringIO(payload_json)):
        with patch("pre_prompt_classifier.check_adg_health_red", return_value=sqlite_red):
            with patch("pre_prompt_classifier.check_redis_up", return_value=redis_up):
                with patch("pre_prompt_classifier.check_redis_adg_hot", return_value=adg_hot):
                    with patch.object(
                        gate,
                        "_check_adg_transport_open",
                        return_value=(
                            transport_open,
                            transport_status,
                            {
                                "status": transport_status,
                                "heartbeat_authoritative_pids": [123],
                                "callable_proof": {
                                    "selected_source": "none",
                                    "proof_required": "proof required",
                                },
                            },
                        ),
                    ):
                        return gate.main()


class TestSsotAuthority:
    def test_t3_ssot_red_blocks(self):
        # SQLite SSOT unavailable → BLOCK regardless of Redis state.
        assert _run('{"prompt": "refactor the architecture across layers"}', sqlite_red=True) == 2

    def test_t3_ssot_green_allows(self):
        assert _run('{"prompt": "refactor the architecture across layers"}', sqlite_red=False) == 0

    def test_t3_ssot_red_blocks_even_with_redis_hot(self):
        # A Redis hot-cache hit may NOT substitute for an unavailable SSOT.
        assert _run('{"prompt": "refactor architecture across layers"}', sqlite_red=True, redis_up=True, adg_hot=True) == 2

    def test_block_message_mentions_ssot(self, capsys):
        _run('{"prompt": "refactor the architecture across layers"}', sqlite_red=True)
        err = capsys.readouterr().err
        assert "SSOT" in err and "BLOCKED" in err


class TestTransportAuthority:
    def test_t3_transport_closed_blocks_even_when_ssot_green(self):
        assert (
            _run(
                '{"prompt": "refactor the architecture across layers"}',
                sqlite_red=False,
                transport_open=False,
                transport_status="callability_unproven",
            )
            == 2
        )

    def test_block_message_mentions_transport(self, capsys):
        _run(
            '{"prompt": "refactor the architecture across layers"}',
            sqlite_red=False,
            transport_open=False,
            transport_status="closed_transport",
        )
        err = capsys.readouterr().err
        assert "ADG MCP transport" in err and "BLOCKED" in err

    def test_transport_recovery_prompt_allows_closed_transport(self, capsys):
        assert (
            _run(
                '{"prompt": "ADG MCP transport closed RCA restart proof before refactor architecture across layers"}',
                sqlite_red=False,
                transport_open=False,
                transport_status="closed_transport",
            )
            == 0
        )
        err = capsys.readouterr().err
        assert "recovery" in err.lower() and "closed_transport" in err

    def test_read_only_recommendation_allows_closed_transport(self, capsys):
        assert (
            _run(
                '{"prompt": "architecture review: recommend redundant T3 refactoring approvals across layers"}',
                sqlite_red=False,
                transport_open=False,
                transport_status="closed_transport",
            )
            == 0
        )
        err = capsys.readouterr().err
        assert "degraded provenance" in err
        assert "required before edits" in err

    def test_http_transport_opens_with_endpoint_matched_adg_health_proof(
        self,
        monkeypatch,
        tmp_path: Path,
    ):
        monkeypatch.setattr(gate, "_REPO_ROOT", tmp_path)
        epoch.write_restart_epoch(repo_root=tmp_path, session_id="s1", epoch_id="epoch-1")
        epoch.write_callability_proof(
            server_id="adg_sqlite",
            tool="adg_health",
            evidence='{"status":"ok"}',
            repo_root=tmp_path,
            route_kind="http",
            endpoint="http://127.0.0.1:8765/mcp",
        )

        open_, status, detail = gate._check_adg_http_transport_open("http://127.0.0.1:8765/mcp")

        assert open_ is True
        assert status == "codex_http_route_callable"
        assert detail["http_callability_acceptance"]["accepted"] is True

    def test_http_transport_rejects_wrong_adg_tool(self, monkeypatch, tmp_path: Path):
        monkeypatch.setattr(gate, "_REPO_ROOT", tmp_path)
        epoch.write_restart_epoch(repo_root=tmp_path, session_id="s1", epoch_id="epoch-1")
        epoch.write_callability_proof(
            server_id="adg_sqlite",
            tool="adg_edge_fanout",
            evidence='{"status":"ok"}',
            repo_root=tmp_path,
            route_kind="http",
            endpoint="http://127.0.0.1:8765/mcp",
        )

        open_, status, detail = gate._check_adg_http_transport_open("http://127.0.0.1:8765/mcp")

        assert open_ is False
        assert status == "codex_http_route_unproven"
        assert "adg_proof_tool_not_allowed" in detail["http_callability_acceptance"]["reasons"]


class TestRedisAdvisory:
    def test_t3_green_redis_cold_allows(self):
        # Redis cold but SSOT green → advisory only, never blocks.
        assert _run('{"prompt": "refactor architecture across layers"}', sqlite_red=False, redis_up=True, adg_hot=False) == 0

    def test_t3_green_redis_down_allows(self):
        assert _run('{"prompt": "refactor architecture across layers"}', sqlite_red=False, redis_up=False, adg_hot=False) == 0

    def test_cold_message_is_advisory(self, capsys):
        _run('{"prompt": "refactor architecture across layers"}', sqlite_red=False, redis_up=True, adg_hot=False)
        err = capsys.readouterr().err
        assert "advisory" in err.lower() and "adg_redis_ingest" in err


class TestTierExemption:
    def test_t0_never_gated_even_if_ssot_red(self):
        assert _run('{"prompt": "explain how the gate works"}', sqlite_red=True) == 0

    def test_t1_never_gated_even_if_ssot_red(self):
        assert _run('{"prompt": "fix the typo in the docstring"}', sqlite_red=True) == 0


class TestFailOpenAndShapes:
    def test_empty_stdin_exits_0(self):
        assert _run("", sqlite_red=True) == 0

    def test_invalid_json_exits_0(self):
        assert _run("not json at all", sqlite_red=True) == 0

    def test_legacy_tool_info_shape_parses(self):
        assert _run('{"tool_info": {"prompt": "refactor the architecture across layers"}}', sqlite_red=True) == 2

    def test_user_prompt_alias_parses(self):
        assert _run('{"tool_info": {"user_prompt": "refactor the architecture across layers"}}', sqlite_red=True) == 2

    def test_session_id_passed_to_transport_probe(self):
        payload = json.dumps(
            {
                "session_id": "session-123",
                "prompt": "refactor the architecture across layers",
            }
        )
        with patch("sys.stdin", StringIO(payload)):
            with patch("pre_prompt_classifier.check_adg_health_red", return_value=False):
                with patch("pre_prompt_classifier.check_redis_up", return_value=True):
                    with patch("pre_prompt_classifier.check_redis_adg_hot", return_value=True):
                        with patch.object(
                            gate,
                            "_check_adg_transport_open",
                            return_value=(True, "open", {"status": "open"}),
                        ) as transport:
                            assert gate.main() == 0
        transport.assert_called_once_with("session-123")

    def test_bypass_env_allows_even_if_red(self, monkeypatch):
        monkeypatch.setenv("ADG_SSOT_GATE_BYPASS", "1")
        assert _run('{"prompt": "refactor the architecture across layers"}', sqlite_red=True) == 0


class TestReadPromptHelper:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ('{"prompt": "hi"}', "hi"),
            ('{"tool_info": {"prompt": "yo"}}', "yo"),
            ('{"tool_info": {"user_prompt": "hey"}}', "hey"),
            ("{}", ""),
            ("[]", ""),
            ("bad", ""),
        ],
    )
    def test_read_prompt(self, raw, expected):
        assert gate._read_prompt(raw) == expected

    def test_read_session_id(self):
        assert gate._read_session_id('{"session_id": "s1", "prompt": "hi"}') == "s1"
        assert gate._read_session_id('{"tool_info": {"sessionId": "s2", "prompt": "hi"}}') == "s2"
