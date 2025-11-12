import pytest
from pydantic import ValidationError

from src.lic_agentic.reasoning.toggles import ReasoningToggles


def test_toggle_defaults():
    toggles = ReasoningToggles()
    assert toggles.cot
    assert toggles.reflexion
    assert 1 <= toggles.tot_branches <= 4


def test_toggle_bounds():
    with pytest.raises(ValidationError):
        ReasoningToggles(tot_branches=7)
