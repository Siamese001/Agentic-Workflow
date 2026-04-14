"""Behavioral tests for semantic_gatekeeper_validator_adg."""

from __future__ import annotations

import pytest

from agentic_core.semantic_gatekeeper_validator_adg import SemanticGatekeeperValidatorAdg


def test_similarity_threshold_within_range_passes():
    assert SemanticGatekeeperValidatorAdg(min_similarity=0.8).validate().min_similarity == 0.8


def test_similarity_threshold_out_of_range_raises():
    with pytest.raises(ValueError):
        SemanticGatekeeperValidatorAdg(min_similarity=1.2).validate()
