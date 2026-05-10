"""Tests for ask_user_question_ledger.py.

Plan: author-gate-ask-ui-consolidated-a1e3f7 W4.
"""

import json
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from tools.ledgers.ask_user_question_ledger import (
    AskUserQuestionDecision,
    ensure_schema,
    write_decision,
    get_decision,
    list_recent_decisions,
    LEDGER_PATH,
)


@pytest.fixture
def temp_ledger(tmp_path):
    """Create a temporary ledger for testing."""
    # Temporarily override LEDGER_PATH
    import tools.ledgers.ask_user_question_ledger as ledger_module
    original_path = ledger_module.LEDGER_PATH
    
    temp_db = tmp_path / "test_ledger.sqlite"
    ledger_module.LEDGER_PATH = temp_db
    
    yield temp_db
    
    # Restore original path
    ledger_module.LEDGER_PATH = original_path


class TestEnsureSchema:
    """Test schema creation."""
    
    def test_creates_table(self, temp_ledger):
        ensure_schema()
        
        conn = sqlite3.connect(temp_ledger)
        try:
            result = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='ask_user_question_decisions'"
            ).fetchone()
            assert result is not None
        finally:
            conn.close()
    
    def test_creates_indexes(self, temp_ledger):
        ensure_schema()
        
        conn = sqlite3.connect(temp_ledger)
        try:
            indexes = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_auq%'"
            ).fetchall()
            assert len(indexes) >= 3  # created_at, context, type indexes
        finally:
            conn.close()
    
    def test_idempotent(self, temp_ledger):
        """Running ensure_schema twice should not fail."""
        ensure_schema()
        ensure_schema()  # Should not raise
        
        conn = sqlite3.connect(temp_ledger)
        try:
            result = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='ask_user_question_decisions'"
            ).fetchone()
            assert result is not None
        finally:
            conn.close()


class TestWriteDecision:
    """Test writing decisions to ledger."""
    
    def test_writes_basic_packet(self, temp_ledger):
        packet = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "context": "test",
            "timestamp": "2026-05-10T10:00:00+00:00",
            "option_count": 2,
            "recommended_index": 0,
            "confidence_source": "heuristic_default",
            "confidence_score": 0.74,
            "invariants": ["confidence_prefix", "tradeoff_segment"],
        }
        
        decision_id = write_decision(packet, selected_index=0)
        
        assert decision_id.startswith("auq_")
    
    def test_preserves_packet_json(self, temp_ledger):
        packet = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "context": "branch-resolution",
            "timestamp": "2026-05-10T10:00:00+00:00",
            "option_count": 3,
            "recommended_index": 1,
            "confidence_source": "explicit",
            "confidence_score": 0.88,
            "invariants": ["confidence_prefix", "tradeoff_segment", "star_marker"],
        }
        
        decision_id = write_decision(packet)
        
        # Verify by reading back
        conn = sqlite3.connect(temp_ledger)
        try:
            row = conn.execute(
                "SELECT packet_json FROM ask_user_question_decisions WHERE decision_id = ?",
                (decision_id,)
            ).fetchone()
            
            stored_packet = json.loads(row[0])
            assert stored_packet["context"] == "branch-resolution"
            assert stored_packet["option_count"] == 3
        finally:
            conn.close()


class TestGetDecision:
    """Test retrieving decisions."""
    
    def test_gets_existing_decision(self, temp_ledger):
        packet = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "context": "test",
            "timestamp": "2026-05-10T10:00:00+00:00",
            "option_count": 2,
            "recommended_index": 0,
            "confidence_source": "heuristic_default",
            "confidence_score": 0.74,
        }
        
        decision_id = write_decision(packet)
        result = get_decision(decision_id)
        
        assert result is not None
        assert result["decision_id"] == decision_id
        assert result["option_count"] == 2
    
    def test_returns_none_for_missing(self, temp_ledger):
        result = get_decision("auq_nonexistent")
        
        assert result is None
    
    def test_returns_none_if_no_ledger(self):
        # Don't create ledger
        result = get_decision("auq_anything")
        
        assert result is None


class TestListRecentDecisions:
    """Test listing recent decisions."""
    
    def test_lists_empty_if_no_decisions(self, temp_ledger):
        decisions = list_recent_decisions()
        
        assert decisions == []
    
    def test_lists_recent_decisions(self, temp_ledger):
        # Write multiple decisions
        for i in range(5):
            packet = {
                "packet_type": "ASK_USER_QUESTION_PACKET",
                "context": f"test-{i}",
                "timestamp": f"2026-05-10T10:0{i}:00+00:00",
                "option_count": 2,
                "recommended_index": 0,
                "confidence_source": "heuristic_default",
            }
            write_decision(packet)
        
        decisions = list_recent_decisions(limit=3)
        
        assert len(decisions) == 3
    
    def test_filters_by_context(self, temp_ledger):
        # Write decisions with different contexts
        for ctx in ["alpha", "beta", "alpha", "gamma"]:
            packet = {
                "packet_type": "ASK_USER_QUESTION_PACKET",
                "context": ctx,
                "timestamp": "2026-05-10T10:00:00+00:00",
                "option_count": 2,
                "recommended_index": 0,
                "confidence_source": "heuristic_default",
            }
            write_decision(packet)
        
        decisions = list_recent_decisions(context="alpha")
        
        assert len(decisions) == 2
        for d in decisions:
            assert d["context"] == "alpha"


class TestAskUserQuestionDecision:
    """Test the dataclass."""
    
    def test_default_values(self):
        decision = AskUserQuestionDecision()
        
        assert decision.decision_type == "enriched_choice"
        assert decision.confidence_source == "heuristic_default"
        assert decision.decision_id.startswith("auq_")
        assert decision.created_at  # Should have timestamp
    
    def test_to_dict(self):
        decision = AskUserQuestionDecision(
            question="Test?",
            option_count=3,
            confidence_score=0.88,
        )
        
        d = decision.to_dict()
        
        assert d["question"] == "Test?"
        assert d["option_count"] == 3
        assert d["confidence_score"] == 0.88


# ========================== Hardened SQLite Round-Trip Tests ==========================
# Author-Gate style: verify full build→write→read pipeline with confidence,
# star, tradeoff, and invariants preserved through SQLite persistence.


class TestSQLiteRoundTripIntegrity:
    """Verify packets survive SQLite write→read with full fidelity."""

    def test_full_packet_round_trip_preserves_all_fields(self, temp_ledger):
        """Write a fully-populated packet and verify every field survives."""
        packet = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "decision_id": "auq_roundtrip_001",
            "context": "refactor-scope",
            "timestamp": "2026-05-10T12:00:00+00:00",
            "option_count": 3,
            "recommended_index": 1,
            "confidence_source": "explicit",
            "confidence_score": 0.88,
            "invariants": ["confidence_prefix", "tradeoff_segment", "star_marker"],
            "decision_type": "enriched_choice",
        }
        
        decision_id = write_decision(packet, selected_index=1)
        assert decision_id == "auq_roundtrip_001"
        
        result = get_decision(decision_id)
        assert result is not None
        assert result["decision_id"] == "auq_roundtrip_001"
        assert result["context"] == "refactor-scope"
        assert result["option_count"] == 3
        assert result["recommended_index"] == 1
        assert result["selected_index"] == 1
        assert result["confidence_source"] == "explicit"
        assert result["confidence_score"] == 0.88
        
        stored_packet = json.loads(result["packet_json"])
        assert stored_packet["packet_type"] == "ASK_USER_QUESTION_PACKET"
        assert stored_packet["confidence_score"] == 0.88
        assert "star_marker" in stored_packet["invariants"]

    def test_invariants_json_survives_round_trip(self, temp_ledger):
        """Invariants list is serialized/deserialized correctly."""
        invariants = ["confidence_prefix", "tradeoff_segment", "star_marker"]
        packet = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "context": "invariant-test",
            "timestamp": "2026-05-10T12:00:00+00:00",
            "option_count": 2,
            "invariants": invariants,
        }
        
        decision_id = write_decision(packet)
        result = get_decision(decision_id)
        
        stored_invariants = json.loads(result["invariants_json"])
        assert stored_invariants == invariants

    def test_confidence_score_precision_preserved(self, temp_ledger):
        """Confidence scores with varying precision survive SQLite REAL storage."""
        for score in [0.0, 0.72, 0.85, 0.999, 1.0]:
            packet = {
                "packet_type": "ASK_USER_QUESTION_PACKET",
                "context": f"precision-{score}",
                "timestamp": "2026-05-10T12:00:00+00:00",
                "option_count": 1,
                "confidence_score": score,
            }
            decision_id = write_decision(packet)
            result = get_decision(decision_id)
            assert abs(result["confidence_score"] - score) < 1e-10, (
                f"Score {score} mutated to {result['confidence_score']}"
            )

    def test_duplicate_decision_id_rejected(self, temp_ledger):
        """Writing the same decision_id twice raises IntegrityError."""
        packet = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "decision_id": "auq_dup_test_001",
            "context": "dup-test",
            "timestamp": "2026-05-10T12:00:00+00:00",
            "option_count": 2,
        }
        
        write_decision(packet)
        with pytest.raises(sqlite3.IntegrityError):
            write_decision(packet)

    def test_selected_index_none_when_not_provided(self, temp_ledger):
        """Omitting selected_index writes NULL, not 0."""
        packet = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "context": "null-selected",
            "timestamp": "2026-05-10T12:00:00+00:00",
            "option_count": 2,
        }
        
        decision_id = write_decision(packet)  # No selected_index
        result = get_decision(decision_id)
        assert result["selected_index"] is None

    def test_heuristic_default_confidence_source_persisted(self, temp_ledger):
        """Packets without explicit confidence_source default to heuristic_default."""
        packet = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "context": "heuristic-default",
            "timestamp": "2026-05-10T12:00:00+00:00",
            "option_count": 1,
        }
        
        decision_id = write_decision(packet)
        result = get_decision(decision_id)
        assert result["confidence_source"] == "heuristic_default"
        assert result["confidence_score"] == 0.72  # DEFAULT

    def test_list_recent_ordered_by_created_at_desc(self, temp_ledger):
        """list_recent_decisions returns most recent first."""
        for i in range(5):
            packet = {
                "packet_type": "ASK_USER_QUESTION_PACKET",
                "context": "order-test",
                "timestamp": f"2026-05-10T10:0{i}:00+00:00",
                "option_count": 1,
            }
            write_decision(packet)
        
        decisions = list_recent_decisions(context="order-test")
        timestamps = [d["created_at"] for d in decisions]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_packet_json_contains_full_original_packet(self, temp_ledger):
        """packet_json column stores the complete original input dict."""
        original = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "context": "full-packet-test",
            "timestamp": "2026-05-10T12:00:00+00:00",
            "option_count": 4,
            "recommended_index": 2,
            "confidence_source": "explicit",
            "confidence_score": 0.91,
            "invariants": ["confidence_prefix", "tradeoff_segment", "star_marker"],
            "custom_field": "should_survive",
        }
        
        decision_id = write_decision(original)
        result = get_decision(decision_id)
        stored = json.loads(result["packet_json"])
        
        for key in original:
            assert stored[key] == original[key], f"Key {key} mutated in packet_json"


# ========================== Build + Ledger Integration Tests ==========================
# Prove the enriched_choice_builder → ledger pipeline works end-to-end.


class TestBuildToLedgerIntegration:
    """Verify enriched_choice_builder output writes correctly to the ledger."""

    def test_builder_telemetry_writes_to_ledger(self, temp_ledger):
        """Telemetry packet from build_enriched_choice_question writes to ledger."""
        # Importing here since this test file already has REPO_ROOT on path
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question
        
        payload = build_enriched_choice_question(
            question="Which approach for the refactoring?",
            options=[
                {
                    "id": "A",
                    "label": "Extract method",
                    "description": "Pull shared logic into utility",
                    "tradeoff": "Increases import count but reduces duplication across modules",
                    "confidence": 0.88,
                },
                {
                    "id": "B",
                    "label": "Inline and simplify",
                    "description": "Merge callers into single function",
                    "tradeoff": "Simpler call graph but longer function bodies per module",
                    "confidence": 0.72,
                },
            ],
            recommended_id="A",
            telemetry_context="refactor-scope",
        )
        
        telem = payload["telemetry_packet"]
        decision_id = write_decision(telem, selected_index=0)
        
        result = get_decision(decision_id)
        assert result is not None
        assert result["context"] == "refactor-scope"
        assert result["confidence_source"] == "explicit"
        assert result["option_count"] == 2
        assert result["recommended_index"] == 0
        assert result["selected_index"] == 0

    def test_builder_no_recommendation_writes_null_recommended(self, temp_ledger):
        """No-recommendation builder output writes NULL recommended_index."""
        from tools.decisions.enriched_choice_builder import build_enriched_choice_question
        
        payload = build_enriched_choice_question(
            question="Pick one",
            options=[
                {"id": "X", "label": "X", "description": "D", "tradeoff": "Tradeoff X is meaningful"},
                {"id": "Y", "label": "Y", "description": "D", "tradeoff": "Tradeoff Y is meaningful"},
            ],
        )
        
        telem = payload["telemetry_packet"]
        decision_id = write_decision(telem)
        result = get_decision(decision_id)
        assert result["recommended_index"] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
