"""Behavioral tests for cognitive_types_adg."""

from __future__ import annotations

import pytest

from agentic_core.cognitive_types_adg import CognitiveState


def test_cognitive_state_accepts_valid_confidence():
    assert CognitiveState(mode="react", confidence=0.5).validate().mode == "react"


def test_cognitive_state_rejects_confidence_out_of_range():
    with pytest.raises(ValueError):
        CognitiveState(mode="react", confidence=1.5).validate()
