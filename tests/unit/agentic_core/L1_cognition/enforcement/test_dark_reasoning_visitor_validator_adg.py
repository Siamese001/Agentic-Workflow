"""Behavioral tests for dark_reasoning_visitor_validator_adg."""

from __future__ import annotations

import pytest

from agentic_core.dark_reasoning_visitor_validator_adg import DarkReasoningVisitorValidatorAdg


def test_default_contract_passes():
    assert DarkReasoningVisitorValidatorAdg().validate().max_hidden_hops == 0


def test_negative_hidden_hops_raises():
    with pytest.raises(ValueError):
        DarkReasoningVisitorValidatorAdg(max_hidden_hops=-1).validate()
