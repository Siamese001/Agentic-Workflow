"""Foundational behavioral tests for apps_lic/engines/control_plane.py."""
from __future__ import annotations

import pytest

from apps_lic.engines.control_plane import ControlPlane, PolicyAction

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module control_plane must be importable."""
    import apps_lic.engines.control_plane  # noqa: F401

    assert apps_lic.engines.control_plane is not None


def test_get_prompt_happy_path_returns_template_text():
    """Test that get_prompt returns actual template text for known prompt."""
    cp = ControlPlane()

    value = cp.get_prompt("lic_connection_request")

    assert cp.get_stats()["knowledge_available"] is True
    assert len(value) > 0
    assert "Recipient Profile:" in value  # Template contains required placeholder


def test_get_prompt_failure_path_raises_keyerror_for_unknown_prompt():
    """Test that get_prompt raises KeyError for unknown prompt_id."""
    cp = ControlPlane()

    with pytest.raises(KeyError):
        cp.get_prompt("missing_prompt_id")


def test_get_prompt_edge_path_returns_empty_when_knowledge_absent():
    """Test that get_prompt returns empty string when knowledge is disabled."""
    cp = ControlPlane()
    cp.knowledge = None

    assert cp.get_prompt("lic_connection_request") == ""


def test_get_node_config_happy_path_returns_config():
    """Test that get_node_config returns node configuration."""
    cp = ControlPlane()

    config = cp.get_node_config("archetype")

    assert config is not None
    assert config.node_id == "archetype"


def test_get_node_config_edge_path_returns_none_when_knowledge_absent():
    """Test that get_node_config returns None when knowledge is disabled."""
    cp = ControlPlane()
    cp.knowledge = None

    assert cp.get_node_config("archetype") is None


def test_knowledge_base_exports():
    """Test that knowledge_base module exports expected symbols."""
    from apps_lic.config import knowledge_base

    assert hasattr(knowledge_base, "FROZEN_SNAPSHOT")
    assert hasattr(knowledge_base, "get_prompt")
    assert hasattr(knowledge_base, "get_node_config")
    assert hasattr(knowledge_base, "list_all_prompts")
    assert len(knowledge_base.list_all_prompts()) > 0


def test_control_plane_evaluate_input_detects_pii():
    """Test that ControlPlane detects PII in input."""
    cp = ControlPlane()

    result = cp.evaluate_input("My ssn is 123-45-6789")

    assert result.action == PolicyAction.BLOCK
    assert result.is_safe is False
    assert "PII detected" in result.errors[0]


def test_control_plane_evaluate_input_allows_safe_content():
    """Test that ControlPlane allows safe content."""
    cp = ControlPlane()

    result = cp.evaluate_input("Hello, this is a safe message.")

    assert result.action == PolicyAction.ALLOW
    assert result.is_safe is True
