"""Tests for L5_safety/identity/registry_loader.py."""

import pytest

from agentic_core.L5_safety.identity.registry_loader import (
    clear_active_snapshot,
    get_active_registry_snapshot,
    set_active_registry_snapshot,
)


def test_set_and_get_active_registry_snapshot(sample_registry_snapshot):
    """Test setting and retrieving the active registry snapshot."""
    set_active_registry_snapshot(sample_registry_snapshot)
    retrieved = get_active_registry_snapshot()
    
    assert retrieved is not None
    assert retrieved.policy_version == "v4.0.0"
    assert retrieved.registry_digest == "test_digest_abc123"
    assert len(retrieved.agents) == 1
    assert len(retrieved.tools) == 1
    assert len(retrieved.prompts) == 1
    assert len(retrieved.connectors) == 1


def test_get_active_registry_snapshot_returns_bootstrap_when_not_set():
    """Test that get_active_registry_snapshot returns bootstrap when not set."""
    # Clear any existing snapshot
    clear_active_snapshot()
    retrieved = get_active_registry_snapshot()
    
    # Bootstrap should have empty registries but valid structure
    assert retrieved is not None
    assert len(retrieved.agents) == 0
    assert len(retrieved.tools) == 0
    assert len(retrieved.prompts) == 0
    assert len(retrieved.connectors) == 0
