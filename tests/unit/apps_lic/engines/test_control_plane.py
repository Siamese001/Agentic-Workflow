"""Foundational behavioral tests for apps_lic/engines/control_plane.py."""

from __future__ import annotations

import pytest


# Lazy import fixture
@pytest.fixture
def control_plane():
    from apps_lic.engines.control_plane import ControlPlane

    return ControlPlane()


pytestmark = pytest.mark.unit


def test_module_importable():
    """Module control_plane must be importable."""
    import apps_lic.engines.control_plane  # noqa: F401

    assert apps_lic.engines.control_plane is not None


def test_get_prompt_happy_path_returns_template_text(control_plane):
    """Test that get_prompt returns actual template text for known prompt."""
    cp = control_plane

    value = cp.get_prompt("lic_connection_request")

    assert cp.get_stats()["knowledge_available"] is True
    assert len(value) > 0
    assert "Recipient Profile:" in value  # Template contains required placeholder


def test_get_prompt_failure_path_raises_keyerror_for_unknown_prompt(control_plane):
    """Test that get_prompt raises KeyError for unknown prompt_id."""
    cp = control_plane

    with pytest.raises(KeyError):
        cp.get_prompt("nonexistent_prompt_id")


def test_get_prompt_edge_path_returns_empty_when_knowledge_absent(control_plane):
    """Edge path: get_prompt returns empty string when knowledge absent."""
    cp = control_plane
    cp.knowledge = None  # Force unavailable
    with pytest.raises(RuntimeError, match="Knowledge base not available"):
        cp.get_prompt("lic_connection_request")


def test_get_node_config_happy_path_returns_config(control_plane):
    """Test that get_node_config returns node configuration."""
    cp = control_plane

    config = cp.get_node_config("archetype")

    assert config is not None
    assert config.node_id == "archetype"


def test_get_node_config_edge_path_returns_none_when_knowledge_absent(control_plane):
    """Edge path: get_node_config returns None when knowledge absent."""
    cp = control_plane
    cp.knowledge = None  # Force unavailable
    with pytest.raises(RuntimeError, match="Knowledge base not available"):
        cp.get_node_config("archetype")


def test_get_prompt_none_raises_typeerror(control_plane):
    """Test that get_prompt raises TypeError for None prompt_id."""
    cp = control_plane

    with pytest.raises(TypeError, match="prompt_id cannot be None"):
        cp.get_prompt(None)


def test_get_node_config_none_raises_typeerror(control_plane):
    """Test that get_node_config raises TypeError for None node_id."""
    cp = control_plane

    with pytest.raises(TypeError, match="node_id cannot be None"):
        cp.get_node_config(None)


def test_knowledge_base_exports():
    """Test that knowledge_base module exports expected symbols."""
    from apps_lic.config import knowledge_base

    assert hasattr(knowledge_base, "FROZEN_SNAPSHOT")
    assert hasattr(knowledge_base, "get_prompt")
    assert hasattr(knowledge_base, "get_node_config")
    assert hasattr(knowledge_base, "list_all_prompts")
    assert len(knowledge_base.list_all_prompts()) > 0


def test_control_plane_evaluate_input_detects_pii(control_plane):
    """Test that ControlPlane detects PII in input."""
    from apps_lic.engines.control_plane import PolicyAction

    cp = control_plane

    result = cp.evaluate_input("My ssn is 123-45-6789")

    assert result.action == PolicyAction.BLOCK
    assert result.is_safe is False
    assert "PII detected" in result.errors[0]


def test_control_plane_evaluate_input_allows_safe_content(control_plane):
    """Test that ControlPlane allows safe content."""
    from apps_lic.engines.control_plane import PolicyAction

    cp = control_plane

    result = cp.evaluate_input("Hello, this is a safe message.")

    assert result.action == PolicyAction.ALLOW
    assert result.is_safe is True
