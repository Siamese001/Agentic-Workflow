"""Tests for pre_user_prompt_adg_ssot_gate.py — ADG SQLite-SSOT green-light gate.

Plan: adg-redis-hotcache-enforcement-b9f4c2.

Contract under test:
  - SQLite SSOT is the authority: T2/T3 + SSOT red (no readable snapshot) → exit 2.
  - Redis is a non-authoritative hot cache: cold/absent Redis → advisory only, exit 0.
  - T0/T1 prompts are never gated, even when the SSOT is red.
  - Bypass env and empty/invalid input fail open (exit 0).
  - Both payload shapes ({"prompt": ...} and {"tool_info": {"prompt": ...}}) parse.
"""

from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".claude" / "governance/scripts"))

import pre_user_prompt_adg_ssot_gate as gate  # noqa: E402


def _run(payload_json: str, *, sqlite_red: bool = False, redis_up: bool = True, adg_hot: bool = True) -> int:
    with patch("sys.stdin", StringIO(payload_json)):
        with patch("pre_prompt_classifier.check_adg_health_red", return_value=sqlite_red):
            with patch("pre_prompt_classifier.check_redis_up", return_value=redis_up):
                with patch("pre_prompt_classifier.check_redis_adg_hot", return_value=adg_hot):
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
