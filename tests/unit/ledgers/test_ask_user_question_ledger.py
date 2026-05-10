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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
