"""Foundational behavioral tests for apps_research/engines/base_research_engine.py."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from pydantic import BaseModel

    from apps_research.engines.base_research_engine import BaseResearchEngine
except ImportError as _import_err:
    pytest.skip(f"base_research_engine not available: {_import_err}", allow_module_level=True)

pytestmark = pytest.mark.unit


class _DummyInput(BaseModel):
    value: str = "ok"


class _DummyEngine(BaseResearchEngine):
    AGENT_ID = "dummy"

    def execute(self, input_data: BaseModel) -> BaseModel:
        return input_data


def test_module_importable():
    """Module base_research_engine must be importable."""
    import apps_research.engines.base_research_engine  # noqa: F401

    assert apps_research.engines.base_research_engine is not None


def test_get_prompt_happy_path_returns_template_text():
    """Test that get_prompt returns actual template text for known prompt."""
    engine = _DummyEngine()

    value = engine.get_prompt("research_query_expansion")

    assert engine.get_status()["knowledge_available"] is True
    assert len(value) > 0
    assert "Original Query:" in value  # Template contains required placeholder


def test_get_prompt_failure_path_raises_keyerror_for_unknown_prompt():
    """Test that get_prompt raises KeyError for unknown prompt_id."""
    engine = _DummyEngine()

    with pytest.raises(KeyError):
        engine.get_prompt("missing_prompt_id")


def test_get_prompt_edge_path_returns_empty_when_knowledge_absent():
    """Edge path: get_prompt returns empty string when knowledge absent."""
    be = _DummyEngine()
    be.knowledge = None  # Force unavailable
    with pytest.raises(RuntimeError, match="Knowledge base not available"):
        be.get_prompt("research_query_expansion")


def test_get_node_config_happy_path_returns_config():
    """Test that get_node_config returns node configuration."""
    engine = _DummyEngine()

    config = engine.get_node_config("discovery")

    assert config is not None
    assert config.node_id == "discovery"


def test_get_node_config_edge_path_returns_none_when_knowledge_absent():
    """Edge path: get_node_config returns None when knowledge absent."""
    be = _DummyEngine()
    be.knowledge = None  # Force unavailable
    with pytest.raises(RuntimeError, match="Knowledge base not available"):
        be.get_node_config("discovery")


def test_get_prompt_none_raises_typeerror():
    """Test that get_prompt raises TypeError for None prompt_id."""
    engine = _DummyEngine()

    with pytest.raises(TypeError, match="prompt_id cannot be None"):
        engine.get_prompt(None)


def test_get_node_config_none_raises_typeerror():
    """Test that get_node_config raises TypeError for None node_id."""
    engine = _DummyEngine()

    with pytest.raises(TypeError, match="node_id cannot be None"):
        engine.get_node_config(None)


def test_knowledge_base_exports():
    """Test that knowledge_base module exports expected symbols."""
    from apps_research.config import knowledge_base

    assert hasattr(knowledge_base, "FROZEN_SNAPSHOT")
    assert hasattr(knowledge_base, "get_prompt")
    assert hasattr(knowledge_base, "get_node_config")
    assert hasattr(knowledge_base, "list_all_prompts")
    assert len(knowledge_base.list_all_prompts()) > 0
