"""Compatibility shim that re-exports the canonical agent registry module."""

from __future__ import annotations

from agentic_core.agents.types import agent_registry as _canonical_agent_registry

AGENT_REGISTRY = _canonical_agent_registry.AGENT_REGISTRY
get_execution_profile = _canonical_agent_registry.get_execution_profile
get_profile = _canonical_agent_registry.get_profile
has_profile = _canonical_agent_registry.has_profile
list_agent_ids = _canonical_agent_registry.list_agent_ids
registry_digest = _canonical_agent_registry.registry_digest

__all__ = [
    "AGENT_REGISTRY",
    "get_execution_profile",
    "get_profile",
    "has_profile",
    "list_agent_ids",
    "registry_digest",
]
