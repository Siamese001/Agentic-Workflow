import pytest
from pydantic import ValidationError

from src.lic_agentic.reasoning.toggles import ReasoningToggles


def test_toggle_defaults():
    toggles = ReasoningToggles()
    assert toggles.cot
    assert toggles.reflexion
    assert 1 <= toggles.tot_branches <= 4
    assert 1 <= toggles.min_tot_depth <= 3
    assert 1 <= toggles.self_consistency <= 5
    assert 0.1 <= toggles.temperature_cap <= 0.9


def test_toggle_bounds_too_many_branches():
    with pytest.raises(ValidationError):
        ReasoningToggles(tot_branches=7)


def test_toggle_bounds_temperature_cap():
    with pytest.raises(ValidationError):
        ReasoningToggles(temperature_cap=1.1)


def test_toggle_bounds_min_depth():
    with pytest.raises(ValidationError):
        ReasoningToggles(min_tot_depth=0)


def test_toggle_bounds_self_consistency():
    with pytest.raises(ValidationError):
        ReasoningToggles(self_consistency=0)


def test_toggle_temperature_lower_bound():
    with pytest.raises(ValidationError):
        ReasoningToggles(temperature_cap=0.05)


def test_toggle_normalizes_numeric_inputs():
    toggles = ReasoningToggles(tot_branches=3.0, self_consistency=4.0)
    assert isinstance(toggles.tot_branches, int)
    assert isinstance(toggles.self_consistency, int)
