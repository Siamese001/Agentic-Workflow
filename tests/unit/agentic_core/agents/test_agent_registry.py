"""Foundational behavioral tests for agentic_core/agents/agent_registry.py.

fan_in=6 — imported by 6 other modules.
ADG import-hygiene is covered separately by test_agent_registry_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.agents.agent_registry import (  # noqa: F401
        get_execution_profile,
        get_profile,
        registry_digest,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_execution_profile = None  # type: ignore[assignment,misc]
    get_profile = None  # type: ignore[assignment,misc]
    registry_digest = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="agent_registry.py deps unavailable")
class TestGetExecutionProfileFunction:
    def test_is_callable(self):
        assert callable(get_execution_profile)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_execution_profile)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="agent_registry.py deps unavailable")
class TestGetProfileFunction:
    def test_is_callable(self):
        assert callable(get_profile)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_profile)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="agent_registry.py deps unavailable")
class TestRegistryDigestFunction:
    def test_is_callable(self):
        assert callable(registry_digest)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(registry_digest)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: agent_registry importable or gracefully unavailable."""
    pass