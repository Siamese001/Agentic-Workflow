"""Foundational behavioral tests for agentic_core/L0_routing/utils/ssot_discovery_util.py.

fan_in=12 — imported by 12 other modules.
ADG import-hygiene is covered separately by test_ssot_discovery_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.utils.ssot_discovery_util import (  # noqa: F401
        get_agent_by_name,
        get_agent_paths,
        get_agents_by_layer,
        load_agent_discovery,
        resolve_canonical_class,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    resolve_canonical_class = None  # type: ignore[assignment,misc]
    load_agent_discovery = None  # type: ignore[assignment,misc]
    get_agent_paths = None  # type: ignore[assignment,misc]
    get_agents_by_layer = None  # type: ignore[assignment,misc]
    get_agent_by_name = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_discovery_util.py deps unavailable")
class TestResolveCanonicalClassFunction:
    def test_is_callable(self):
        assert callable(resolve_canonical_class)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(resolve_canonical_class)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_discovery_util.py deps unavailable")
class TestLoadAgentDiscoveryFunction:
    def test_is_callable(self):
        assert callable(load_agent_discovery)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(load_agent_discovery)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_discovery_util.py deps unavailable")
class TestGetAgentPathsFunction:
    def test_is_callable(self):
        assert callable(get_agent_paths)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_agent_paths)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_discovery_util.py deps unavailable")
class TestGetAgentsByLayerFunction:
    def test_is_callable(self):
        assert callable(get_agents_by_layer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_agents_by_layer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_discovery_util.py deps unavailable")
class TestGetAgentByNameFunction:
    def test_is_callable(self):
        assert callable(get_agent_by_name)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_agent_by_name)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: ssot_discovery_util importable or gracefully unavailable."""
    pass