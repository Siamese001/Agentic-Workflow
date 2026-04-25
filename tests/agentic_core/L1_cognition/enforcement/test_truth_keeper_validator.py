"""Tests for TruthKeeperValidator - factuality validation."""
import pytest
from unittest.mock import Mock
from agentic_core.L1_cognition.enforcement.truth_keeper_validator import TruthKeeperValidator


class TestTruthKeeperValidator:
    def test_init(self):
        v = TruthKeeperValidator()
        assert v is not None

    def test_validate_grounded_claim(self):
        v = TruthKeeperValidator()
        result = v.validate(
            claim="X is Y",
            evidence=[{"source": "doc", "text": "X is Y"}]
        )
        assert result.grounded is True

    def test_validate_ungrounded_claim(self):
        v = TruthKeeperValidator()
        result = v.validate(claim="X is Y", evidence=[])
        assert result.grounded is False

    def test_classify_directly_observed(self):
        v = TruthKeeperValidator()
        c = v.classify(claim="X", evidence_strength=1.0)
        assert c == "DIRECTLY OBSERVED"

    def test_classify_derived(self):
        v = TruthKeeperValidator()
        c = v.classify(claim="X", evidence_strength=0.6)
        assert c == "DERIVED"

    def test_classify_unresolved(self):
        v = TruthKeeperValidator()
        c = v.classify(claim="X", evidence_strength=0.0)
        assert c == "UNRESOLVED"

    def test_extract_evidence(self):
        v = TruthKeeperValidator()
        ev = v.extract_evidence(text="The sky is blue. [src: NASA]")
        assert isinstance(ev, list)
