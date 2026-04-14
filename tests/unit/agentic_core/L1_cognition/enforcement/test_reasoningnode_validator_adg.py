"""Behavioral tests for reasoningnode_validator_adg."""

from __future__ import annotations

import pytest

from agentic_core.reasoningnode_validator_adg import ReasoningNodeValidatorAdg


def test_reasoning_node_validator_accepts_non_empty_type():
    assert ReasoningNodeValidatorAdg(node_type="reasoning").validate().node_type == "reasoning"


def test_reasoning_node_validator_rejects_blank_type():
    with pytest.raises(ValueError):
        ReasoningNodeValidatorAdg(node_type=" ").validate()
