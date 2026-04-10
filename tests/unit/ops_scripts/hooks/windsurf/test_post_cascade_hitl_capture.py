# pylint: disable=protected-access
"""
test_post_cascade_hitl_capture.py

Unit tests for .windsurf/scripts/post_cascade_hitl_capture.py

Coverage:
    _init_db           — schema creation, idempotency
    detect_and_capture — happy path, no-HITL-packet, dedup, option extraction
    _extract_response_text — dict payload, str payload, empty payload
    _infer_decision_type   — keyword matching, fallback to 'unknown'
    _make_decision_id      — deterministic, prefixed
    main()             — empty stdin, valid HITL payload, invalid JSON stdin
"""

import json
import sqlite3
import sys
import textwrap
from io import StringIO
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / ".windsurf" / "scripts"))

import post_cascade_hitl_capture as _m  # noqa: E402  (used for monkeypatching module globals)

from post_cascade_hitl_capture import (  # noqa: E402
    _DDL,
    _extract_response_text,
    _infer_decision_type,
    _init_db,
    _make_decision_id,
    detect_and_capture,
    main,
)


# ---------------------------------------------------------------------------
# Minimal HITL packet text that triggers detection
# ---------------------------------------------------------------------------

_HITL_PACKET = textwrap.dedent("""\
    Recommended: Minimal scope — single file refactor
    Why it wins: Lowest blast radius; no cross-layer changes needed.
    What you are optimizing for: Zero-regression refactor of L2 adapters.
    What is being traded off: Slightly less reuse than a full extract.
    Candidates evaluated: 3 | Surfaced: 2 | Suppressed (low confidence): 1 | Suppressed (non-distinct): 0

    Refactor the execution adapter into a dedicated module.
    Option 1. Minimal scope — single file refactor
    Option 2. Full extract — new sub-package
""")

_NO_HITL_TEXT = "This is a normal response with no HITL decision packet."


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_in_memory_conn():
    """Open an in-memory SQLite DB and initialise the schema."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(_DDL)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# _init_db
# ---------------------------------------------------------------------------


class TestInitDb:
    def test_creates_tables_on_disk(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_m, "DB_DIR", tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "test_ledger.sqlite")
        conn = _init_db()
        assert conn is not None
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert "decisions" in tables
        assert "decision_scope" in tables
        assert "decision_outcomes" in tables
        conn.close()

    def test_idempotent_second_call(self, tmp_path, monkeypatch):
        monkeypatch.setattr(_m, "DB_DIR", tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "test_ledger2.sqlite")
        c1 = _init_db()
        c1.close()
        c2 = _init_db()  # must not raise
        assert c2 is not None
        c2.close()


# ---------------------------------------------------------------------------
# detect_and_capture — happy path
# ---------------------------------------------------------------------------


class TestDetectAndCapture:
    def test_happy_path_inserts_record(self):
        conn = _make_in_memory_conn()
        captured = detect_and_capture(_HITL_PACKET, conn)
        assert captured is True
        row = conn.execute("SELECT * FROM decisions").fetchone()
        assert row is not None
        assert row[0].startswith("dec_")
        assert row[5] == "refactor_scope"  # decision_type inferred from 'Refactor'
        conn.close()

    def test_no_packet_returns_false(self):
        conn = _make_in_memory_conn()
        captured = detect_and_capture(_NO_HITL_TEXT, conn)
        assert captured is False
        count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        assert count == 0
        conn.close()

    def test_dedup_same_packet(self):
        conn = _make_in_memory_conn()
        first = detect_and_capture(_HITL_PACKET, conn)
        second = detect_and_capture(_HITL_PACKET, conn)
        assert first is True
        assert second is False
        count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        assert count == 1
        conn.close()

    def test_options_extracted(self):
        conn = _make_in_memory_conn()
        detect_and_capture(_HITL_PACKET, conn)
        row = conn.execute("SELECT options_json FROM decisions").fetchone()
        options = json.loads(row[0])
        assert isinstance(options, list)
        assert len(options) >= 1
        conn.close()

    def test_fts_row_inserted(self):
        conn = _make_in_memory_conn()
        detect_and_capture(_HITL_PACKET, conn)
        rows = conn.execute(
            "SELECT decision_id FROM decisions_fts WHERE decisions_fts MATCH 'refactor'"
        ).fetchall()
        assert len(rows) >= 1
        conn.close()

    def test_recommended_option_captured(self):
        conn = _make_in_memory_conn()
        detect_and_capture(_HITL_PACKET, conn)
        row = conn.execute("SELECT recommended_option_id FROM decisions").fetchone()
        assert "Minimal scope" in row[0]
        conn.close()


# ---------------------------------------------------------------------------
# _extract_response_text
# ---------------------------------------------------------------------------


class TestExtractResponseText:
    def test_str_payload_returned_directly(self):
        assert _extract_response_text("hello world") == "hello world"

    def test_dict_with_response_key(self):
        payload = {"response": "the cascade response text"}
        assert _extract_response_text(payload) == "the cascade response text"

    def test_dict_with_content_key(self):
        payload = {"content": "content field text"}
        assert _extract_response_text(payload) == "content field text"

    def test_dict_unknown_keys_falls_back_to_json(self):
        payload = {"foo": "bar"}
        result = _extract_response_text(payload)
        assert "foo" in result

    def test_empty_string_returns_empty(self):
        assert _extract_response_text("") == ""

    def test_non_str_non_dict_returns_empty(self):
        assert _extract_response_text(42) == ""
        assert _extract_response_text(None) == ""


# ---------------------------------------------------------------------------
# _infer_decision_type
# ---------------------------------------------------------------------------


class TestInferDecisionType:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("This is an architecture decision", "architecture_choice"),
            ("We need to refactor the module", "refactor_scope"),
            ("Introducing an anti-pattern here", "anti_pattern"),
            ("Adding a new dependency to requirements", "dependency_addition"),
            ("Test strategy for the new feature", "test_strategy"),
            ("Delete the old module", "deletion_strategy"),
            ("Error handling for the API client", "error_handling"),
            ("Some unrelated text", "unknown"),
        ],
    )
    def test_keyword_mapping(self, text, expected):
        assert _infer_decision_type(text) == expected

    def test_case_insensitive(self):
        assert _infer_decision_type("ARCHITECTURE CHOICE") == "architecture_choice"


# ---------------------------------------------------------------------------
# _make_decision_id
# ---------------------------------------------------------------------------


class TestMakeDecisionId:
    def test_has_dec_prefix(self):
        did = _make_decision_id("some text", "2026-04-10T10:00:00Z")
        assert did.startswith("dec_")

    def test_deterministic(self):
        ts = "2026-04-10T10:00:00Z"
        d1 = _make_decision_id("same text", ts)
        d2 = _make_decision_id("same text", ts)
        assert d1 == d2

    def test_different_text_different_id(self):
        ts = "2026-04-10T10:00:00Z"
        d1 = _make_decision_id("text A", ts)
        d2 = _make_decision_id("text B", ts)
        assert d1 != d2


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    def test_empty_stdin_exits_0(self, monkeypatch):
        monkeypatch.setattr(sys, "stdin", StringIO(""))
        assert main() == 0

    def test_invalid_json_exits_0(self, monkeypatch, tmp_path):
        monkeypatch.setattr(_m, "DB_DIR", tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "ledger.sqlite")
        monkeypatch.setattr(sys, "stdin", StringIO("not valid json <<<"))
        assert main() == 0

    def test_valid_hitl_payload_exits_0_and_inserts(self, monkeypatch, tmp_path):
        monkeypatch.setattr(_m, "DB_DIR", tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "ledger.sqlite")
        payload = json.dumps({"response": _HITL_PACKET})
        monkeypatch.setattr(sys, "stdin", StringIO(payload))
        result = main()
        assert result == 0
        conn = sqlite3.connect(str(tmp_path / "ledger.sqlite"))
        count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        conn.close()
        assert count == 1

    def test_no_hitl_in_payload_exits_0_no_insert(self, monkeypatch, tmp_path):
        monkeypatch.setattr(_m, "DB_DIR", tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "ledger.sqlite")
        payload = json.dumps({"response": _NO_HITL_TEXT})
        monkeypatch.setattr(sys, "stdin", StringIO(payload))
        assert main() == 0
        db = tmp_path / "ledger.sqlite"
        if db.exists():
            conn = sqlite3.connect(str(db))
            count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
            conn.close()
            assert count == 0
