"""Tests for ReasoningToggles validation logic."""
import pytest
from pydantic import ValidationError
from src.lic_agentic.reasoning.toggles import ReasoningToggles


def test_toggle_defaults():
    toggles = ReasoningToggles()
    assert toggles.cot
    assert toggles.reflexion
    assert 1 <= toggles.tot_branches <= 4


def test_toggle_bounds_for_tot_branches():
    with pytest.raises(ValidationError):
        ReasoningToggles(tot_branches=7)


def test_toggle_bounds_for_min_tot_depth():
    with pytest.raises(ValidationError):
        ReasoningToggles(min_tot_depth=5)


def test_toggle_bounds_for_temperature():
    with pytest.raises(ValidationError):
        ReasoningToggles(temperature_cap=0.05)


def test_toggle_bounds_for_self_consistency():
    with pytest.raises(ValidationError):
        ReasoningToggles(self_consistency=10)
