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
