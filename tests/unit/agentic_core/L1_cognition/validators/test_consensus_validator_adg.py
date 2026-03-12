"""ADG-driven tests for L1_cognition/validators/consensus_validator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L1_cognition.validators.consensus_validator import ConsensusEngine


class TestConsensusEngine:
    def test_creates_with_defaults(self):
        engine = ConsensusEngine()
        assert engine is not None

    def test_critical_keywords_is_list(self):
        assert isinstance(ConsensusEngine.CRITICAL_KEYWORDS, list)

    def test_majority_threshold(self):
        assert 0 < ConsensusEngine.MAJORITY_THRESHOLD <= 1.0

    def test_model_check_config_is_dict(self):
        assert isinstance(ConsensusEngine.MODEL_CHECK_CONFIG, dict)
