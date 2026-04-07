"""Tests for RetrievalSafetyGate.

G5 fix: Adds test coverage for L5 retrieval safety gate.
"""

import pytest
from agentic_core.L5_safety.retrieval import RetrievalSafetyGate


class TestRetrievalSafetyGate:
    """Test suite for RetrievalSafetyGate."""

    def test_init_default_config(self):
        """Test initialization with default config."""
        gate = RetrievalSafetyGate()
        assert gate.config == {}
        assert gate._check_count == 0

    def test_init_custom_config(self):
        """Test initialization with custom config."""
        config = {"strict_mode": True}
        gate = RetrievalSafetyGate(config)
        assert gate.config == {"strict_mode": True}

    # ---------- validate_retrieval_request tests ----------

    def test_validate_retrieval_request_success(self):
        """Happy path: valid query returns approved result."""
        gate = RetrievalSafetyGate()
        result = gate.validate_retrieval_request("test query", {})

        assert result["approved"] is True
        assert result["check_id"] == "retrieval_check_1"
        assert "query_hash" in result

    def test_validate_retrieval_request_increments_counter(self):
        """Each call increments the check counter."""
        gate = RetrievalSafetyGate()
        gate.validate_retrieval_request("query 1", {})
        gate.validate_retrieval_request("query 2", {})
        result = gate.validate_retrieval_request("query 3", {})

        assert result["check_id"] == "retrieval_check_3"

    def test_validate_retrieval_request_empty_string_raises(self):
        """Failure path: empty string raises ValueError."""
        gate = RetrievalSafetyGate()
        with pytest.raises(ValueError, match="cannot be empty"):
            gate.validate_retrieval_request("", {})

    def test_validate_retrieval_request_whitespace_only_raises(self):
        """Failure path: whitespace-only string raises ValueError."""
        gate = RetrievalSafetyGate()
        with pytest.raises(ValueError, match="cannot be empty"):
            gate.validate_retrieval_request("   ", {})

    def test_validate_retrieval_request_non_string_raises(self):
        """Failure path: non-string query raises ValueError."""
        gate = RetrievalSafetyGate()
        with pytest.raises(ValueError, match="must be a string"):
            gate.validate_retrieval_request(123, {})

    def test_validate_retrieval_request_context_used(self):
        """Context parameter is accepted (edge case)."""
        gate = RetrievalSafetyGate()
        result = gate.validate_retrieval_request("query", {"user_id": "test"})
        assert result["approved"] is True

    # ---------- apply_guardrails tests ----------

    def test_apply_guardrails_success(self):
        """Happy path: returns results list unchanged."""
        gate = RetrievalSafetyGate()
        results = [{"doc_id": "1"}, {"doc_id": "2"}]
        output = gate.apply_guardrails(results)

        assert output == results

    def test_apply_guardrails_empty_list(self):
        """Edge case: empty list returns empty list."""
        gate = RetrievalSafetyGate()
        output = gate.apply_guardrails([])

        assert output == []

    def test_apply_guardrails_non_list_raises(self):
        """Failure path: non-list input raises TypeError."""
        gate = RetrievalSafetyGate()
        with pytest.raises(TypeError, match="Expected list"):
            gate.apply_guardrails("not a list")

    def test_apply_guardrails_dict_raises(self):
        """Failure path: dict input raises TypeError."""
        gate = RetrievalSafetyGate()
        with pytest.raises(TypeError, match="Expected list"):
            gate.apply_guardrails({"key": "value"})

    def test_apply_guardrails_none_raises(self):
        """Failure path: None input raises TypeError."""
        gate = RetrievalSafetyGate()
        with pytest.raises(TypeError, match="Expected list"):
            gate.apply_guardrails(None)
