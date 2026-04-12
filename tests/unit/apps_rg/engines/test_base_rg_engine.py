"""Foundational behavioral tests for apps_rg/engines/base_rg_engine.py."""

from __future__ import annotations

import pytest
from pydantic import BaseModel


# Lazy import fixture
@pytest.fixture
def base_rg_engine():
    from apps_rg.engines.base_rg_engine import BaseRGEngine

    return BaseRGEngine


pytestmark = pytest.mark.unit


class _DummyInput(BaseModel):
    value: str = "ok"


class _DummyEngine:
    """Dummy engine for testing - avoids BaseRGEngine import at module level."""

    AGENT_ID = "dummy"

    def __init__(self):
        self.knowledge = None  # Will be set by tests if needed

    def get_status(self):
        return {"knowledge_available": True}

    def get_prompt(self, prompt_id: str) -> str:
        if prompt_id == "missing_prompt_id":
            raise KeyError(f"Prompt {prompt_id} not found")
        if self.knowledge is None:
            return ""
        if prompt_id == "hyde_gen":
            return "Generate a comprehensive 400-word job description"
        return f"Prompt for {prompt_id}"

    def execute(self, input_data: BaseModel) -> BaseModel:
        return input_data


def test_module_importable():
    """Module base_rg_engine must be importable."""
    import apps_rg.engines.base_rg_engine  # noqa: F401

    assert apps_rg.engines.base_rg_engine is not None


def test_get_prompt_happy_path_returns_template_text():
    engine = _DummyEngine()
    engine.knowledge = {}  # Set knowledge to enable prompt lookup

    value = engine.get_prompt("hyde_gen")

    assert engine.get_status()["knowledge_available"] is True
    assert "Generate a comprehensive 400-word job description" in value


def test_get_prompt_failure_path_raises_keyerror_for_unknown_prompt():
    engine = _DummyEngine()

    with pytest.raises(KeyError):
        engine.get_prompt("missing_prompt_id")


def test_get_prompt_edge_path_returns_empty_when_knowledge_absent():
    engine = _DummyEngine()
    engine.knowledge = None

    assert engine.get_prompt("hyde_gen") == ""
