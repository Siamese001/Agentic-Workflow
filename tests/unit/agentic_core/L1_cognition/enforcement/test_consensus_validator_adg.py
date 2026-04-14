"""Behavioral tests for consensus_validator_adg."""

from __future__ import annotations

import pytest

from agentic_core.consensus_validator_adg import ConsensusValidatorAdg, validate_consensus_validator_adg


def test_default_validator_passes():
    assert validate_consensus_validator_adg() == ConsensusValidatorAdg()


def test_invalid_required_votes_raises():
    with pytest.raises(ValueError):
        ConsensusValidatorAdg(required_votes=0).validate()
