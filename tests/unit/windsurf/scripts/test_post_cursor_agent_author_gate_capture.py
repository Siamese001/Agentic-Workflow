# pylint: disable=protected-access
"""
test_post_cursor_agent_author_gate_capture.py

Unit tests for .cursor/scripts/post_cursor_agent_author_gate_capture.py

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

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / ".cursor" / "scripts"))

import post_cursor_agent_author_gate_capture as _m  # noqa: E402  (used for monkeypatching module globals)

from post_cursor_agent_author_gate_capture import (  # noqa: E402
    _ddl,
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
    conn.executescript(_ddl)
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

    def test_extract_options_cap_at_six(self):
        lines = "\n".join(f"Option {i}. Choice number {i}" for i in range(1, 10))
        text = _HITL_PACKET + lines
        conn = _make_in_memory_conn()
        detect_and_capture(text, conn)
        row = conn.execute("SELECT options_json FROM decisions").fetchone()
        options = json.loads(row[0])
        assert len(options) <= 6, "_extract_options must cap at 6 entries"
        conn.close()


# ---------------------------------------------------------------------------
# _extract_response_text
# ---------------------------------------------------------------------------


class TestExtractResponseText:
    def test_str_payload_returned_directly(self):
        assert _extract_response_text("hello world") == "hello world"

    def test_dict_with_response_key(self):
        payload = {"response": "the cursor agent response text"}
        assert _extract_response_text(payload) == "the cursor agent response text"

    def test_dict_with_content_key(self):
        payload = {"content": "content field text"}
        assert _extract_response_text(payload) == "content field text"

    def test_dict_unknown_keys_falls_back_to_json(self):
        payload = {"foo": "bar"}
        result = _extract_response_text(payload)
        assert "foo" in result

    def test_empty_string_returns_empty(self):
        assert _extract_response_text("") == ""

    def test_dict_no_known_key(self):
        result = _extract_response_text({"unknown_key": "val"})
        assert result == json.dumps({"unknown_key": "val"})

    def test_tool_info_response_key(self):
        """Real post_cursor_agent_response format: text lives at tool_info.response."""
        payload = {
            "agent_action_name": "post_cursor_agent_response",
            "trajectory_id": "traj-abc123",
            "tool_info": {"response": "the actual cursor agent response text"},
        }
        assert _extract_response_text(payload) == "the actual cursor agent response text"

    def test_tool_info_takes_priority_over_toplevel(self):
        """tool_info.response is checked before a top-level 'response' key."""
        payload = {
            "response": "top-level fallback",
            "tool_info": {"response": "real text from tool_info"},
        }
        assert _extract_response_text(payload) == "real text from tool_info"

    def test_toplevel_response_used_when_no_tool_info(self):
        """Existing tests: top-level 'response' still works when tool_info absent."""
        assert _extract_response_text({"response": "abc"}) == "abc"


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
        # DB IS created by _init_db() even when no HITL packet is found;
        # must assert unconditionally — conditional silently skips on _init_db failure
        assert db.exists(), "_init_db() must create DB for non-empty text payload"
        conn = sqlite3.connect(str(db))
        count = conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0]
        conn.close()
        assert count == 0, "no HITL packet must produce zero records"

    def test_init_db_returns_none_exits_0(self, monkeypatch, tmp_path):
        monkeypatch.setattr(_m, "DB_DIR", tmp_path)
        monkeypatch.setattr(_m, "DB_PATH", tmp_path / "ledger.sqlite")
        monkeypatch.setattr(_m, "_init_db", lambda: None)
        payload = json.dumps({"response": _HITL_PACKET})
        monkeypatch.setattr(sys, "stdin", StringIO(payload))
        assert main() == 0  # must not raise even when _init_db returns None


# ---------------------------------------------------------------------------
# _capture_from_marker — structured DECISION_CAPTURED: path
# This is the PRIMARY live capture path (all 14 backfilled decisions used it).
# It was untested; the heuristic fallback was the only tested path.
# ---------------------------------------------------------------------------

_MARKER_TEXT = (
    "DECISION_CAPTURED: type=refactor_scope, "
    "repo_area=agentic_core/L2_execution, "
    "selected=Minimal scope refactor, outcome=executed"
)

_MARKER_AND_HEURISTIC = (
    "Recommended: Something else\n"
    "Why it wins: Because it is faster.\n"
    "Candidates evaluated: 2\n\n" + _MARKER_TEXT
)


class TestStructuredMarkerCapture:
    def test_marker_inserts_record(self):
        conn = _make_in_memory_conn()
        captured = detect_and_capture(_MARKER_TEXT, conn)
        assert captured is True
        row = conn.execute("SELECT decision_id FROM decisions").fetchone()
        assert row is not None
        assert row[0].startswith("dec_")
        conn.close()

    def test_marker_sets_decision_type_from_dtype_field(self):
        """decision_type must come from the marker dtype= field, not keyword inference."""
        conn = _make_in_memory_conn()
        detect_and_capture(_MARKER_TEXT, conn)
        row = conn.execute("SELECT decision_type FROM decisions").fetchone()
        assert row[0] == "refactor_scope"
        conn.close()

    def test_marker_outcome_executed_sets_executed_status(self):
        conn = _make_in_memory_conn()
        detect_and_capture(_MARKER_TEXT, conn)
        row = conn.execute("SELECT status FROM decisions").fetchone()
        assert row[0] == "executed"
        conn.close()

    def test_marker_outcome_other_sets_surfaced_status(self):
        text = (
            "DECISION_CAPTURED: type=anti_pattern, repo_area=agentic_core, selected=Option B, outcome=pending"
        )
        conn = _make_in_memory_conn()
        detect_and_capture(text, conn)
        row = conn.execute("SELECT status FROM decisions").fetchone()
        assert row[0] == "surfaced"
        conn.close()

    def test_marker_preferred_over_heuristic_packet(self):
        """When both a DECISION_CAPTURED marker and a heuristic packet header exist
        in the same text, the marker path takes priority.
        Proof: heuristic path leaves selected_option_id NULL; marker path sets it."""
        conn = _make_in_memory_conn()
        detect_and_capture(_MARKER_AND_HEURISTIC, conn)
        row = conn.execute("SELECT decision_type, selected_option_id FROM decisions").fetchone()
        assert row[0] == "refactor_scope", "decision_type must come from marker dtype="
        assert row[1] is not None, "marker path sets selected_option_id; heuristic does not"
        conn.close()

    def test_marker_dedup_same_text(self):
        conn = _make_in_memory_conn()
        first = detect_and_capture(_MARKER_TEXT, conn)
        second = detect_and_capture(_MARKER_TEXT, conn)
        assert first is True
        assert second is False
        assert conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0] == 1
        conn.close()

    def test_marker_fts_searchable_by_repo_area(self):
        conn = _make_in_memory_conn()
        detect_and_capture(_MARKER_TEXT, conn)
        rows = conn.execute(
            "SELECT decision_id FROM decisions_fts WHERE decisions_fts MATCH 'L2_execution'"
        ).fetchall()
        assert len(rows) >= 1
        conn.close()

    def test_marker_selected_and_recommended_both_set(self):
        conn = _make_in_memory_conn()
        detect_and_capture(_MARKER_TEXT, conn)
        row = conn.execute("SELECT recommended_option_id, selected_option_id FROM decisions").fetchone()
        assert row[0] == "Minimal scope refactor"
        assert row[1] == "Minimal scope refactor"
        conn.close()


# ---------------------------------------------------------------------------
# TestRealPayloadEndToEnd — full hook chain through the documented payload format
# ---------------------------------------------------------------------------

_REAL_HOOK_PAYLOAD = {
    "agent_action_name": "post_cursor_agent_response",
    "trajectory_id": "traj-test-0001",
    "execution_id": "exec-test-0001",
    "timestamp": "2026-04-11T15:00:00+00:00",
    "tool_info": {
        "response": (
            "### Planner Response\n\n"
            "Made the wiring change to hitl-enforcement.md.\n\n"
            "DECISION_CAPTURED: type=architecture_choice, "
            "repo_area=.windsurf/rules/hitl-enforcement.md, "
            "selected=extend Execute step with emission, outcome=executed\n\n"
            "Tests pass."
        )
    },
}


class TestRealPayloadEndToEnd:
    def test_real_payload_extracts_response_text(self):
        """_extract_response_text must return the inner string from tool_info.response."""
        text = _extract_response_text(_REAL_HOOK_PAYLOAD)
        assert "DECISION_CAPTURED:" in text
        assert "Planner Response" in text

    def test_real_payload_marker_captured(self):
        """Full chain: real hook payload → text extraction → DB insert."""
        text = _extract_response_text(_REAL_HOOK_PAYLOAD)
        conn = _make_in_memory_conn()
        captured = detect_and_capture(text, conn)
        assert captured is True
        row = conn.execute(
            "SELECT decision_type, normalized_intent, selected_option_id FROM decisions"
        ).fetchone()
        assert row[0] == "architecture_choice"
        assert ".windsurf/rules/hitl-enforcement.md" in row[1]
        assert row[2] == "extend Execute step with emission"
        conn.close()

    def test_real_payload_fts_searchable(self):
        """Decision inserted via real payload is searchable via FTS."""
        text = _extract_response_text(_REAL_HOOK_PAYLOAD)
        conn = _make_in_memory_conn()
        detect_and_capture(text, conn)
        rows = conn.execute(
            "SELECT decision_id FROM decisions_fts WHERE decisions_fts MATCH 'hitl'"
        ).fetchall()
        assert len(rows) >= 1
        conn.close()

    def test_v2_exit_criteria_extracted_simple(self):
        """W3.1: exit_criteria=<text> populates exit_criteria_json column."""
        marker = (
            "DECISION_CAPTURED: type=refactor_scope, repo_area=tools/foo, "
            "selected=opt-A, outcome=executed, "
            "exit_criteria=tests_pass; p_count_max:0; rollback_window_h:24"
        )
        conn = _make_in_memory_conn()
        assert detect_and_capture(marker, conn) is True
        ec = conn.execute("SELECT exit_criteria_json FROM decisions").fetchone()[0]
        assert ec is not None
        assert "tests_pass" in ec
        assert "p_count_max:0" in ec
        conn.close()

    def test_v2_exit_criteria_extracted_json(self):
        """W3.1: exit_criteria={...} JSON form is preserved verbatim."""
        marker = (
            "DECISION_CAPTURED: type=refactor_scope, repo_area=tools/bar, "
            "selected=opt-B, outcome=executed, "
            'exit_criteria={"tests_must_pass": ["tests/unit/foo/"], "p_count_max": 0}, '
            "principle=test-discipline"
        )
        conn = _make_in_memory_conn()
        assert detect_and_capture(marker, conn) is True
        row = conn.execute("SELECT exit_criteria_json, principle_at_stake FROM decisions").fetchone()
        assert row[0] is not None
        assert "tests_must_pass" in row[0]
        assert row[1] == "test-discipline"
        conn.close()

    def test_v2_exit_criteria_absent_leaves_null(self):
        """No exit_criteria= field => exit_criteria_json stays NULL."""
        marker = (
            "DECISION_CAPTURED: type=refactor_scope, repo_area=tools/baz, "
            "selected=opt-C, outcome=executed, principle=foo"
        )
        conn = _make_in_memory_conn()
        assert detect_and_capture(marker, conn) is True
        ec = conn.execute("SELECT exit_criteria_json FROM decisions").fetchone()[0]
        assert ec is None
        conn.close()

    def test_real_payload_dedup(self):
        """Sending the same payload twice produces exactly one DB row."""
        text = _extract_response_text(_REAL_HOOK_PAYLOAD)
        conn = _make_in_memory_conn()
        first = detect_and_capture(text, conn)
        second = detect_and_capture(text, conn)
        assert first is True
        assert second is False
        assert conn.execute("SELECT COUNT(*) FROM decisions").fetchone()[0] == 1
        conn.close()
