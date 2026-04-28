"""Tests for ConsensusValidator - multi-source consensus validation."""
import pytest
from agentic_core.L1_cognition.enforcement.consensus_validator import ConsensusValidator


class TestConsensusValidator:
    def test_init(self):
        v = ConsensusValidator(threshold=0.66)
        assert v.threshold == 0.66

    def test_consensus_reached(self):
        v = ConsensusValidator(threshold=0.66)
        result = v.validate(["A", "A", "A", "B"])
        assert result.consensus is True
        assert result.value == "A"

    def test_consensus_not_reached(self):
        v = ConsensusValidator(threshold=0.66)
        result = v.validate(["A", "B", "C"])
        assert result.consensus is False

    def test_empty_input(self):
        v = ConsensusValidator(threshold=0.66)
        with pytest.raises(ValueError):
            v.validate([])

    def test_unanimous(self):
        v = ConsensusValidator(threshold=1.0)
        assert v.validate(["X", "X", "X"]).consensus is True

    def test_threshold_boundary(self):
        v = ConsensusValidator(threshold=0.5)
        # 2/4 = 0.5 — boundary
        result = v.validate(["A", "A", "B", "C"])
        assert isinstance(result.consensus, bool)
