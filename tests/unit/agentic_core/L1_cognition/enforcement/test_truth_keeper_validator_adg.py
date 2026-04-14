"""Behavioral tests for truth_keeper_validator_adg."""

from __future__ import annotations

from agentic_core.truth_keeper_validator_adg import TruthKeeperValidatorAdg


def test_truth_keeper_default_requires_evidence():
    assert TruthKeeperValidatorAdg().validate().evidence_required is True
