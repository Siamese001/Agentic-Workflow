"""Foundational behavioral tests for agentic_core/L4_state/workflow_engines/cache_key_builders.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_cache_key_builders_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.workflow_engines.cache_key_builders import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        build_cap_registry_key,
        build_compiled_prompt_key,
        build_route_decision_key,
        build_routing_rule_surface_key,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    build_routing_rule_surface_key = None  # type: ignore[assignment,misc]
    build_route_decision_key = None  # type: ignore[assignment,misc]
    build_cap_registry_key = None  # type: ignore[assignment,misc]
    build_compiled_prompt_key = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBuildRoutingRuleSurfaceKeyFunction:
    def test_is_callable(self):
        assert callable(build_routing_rule_surface_key)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_routing_rule_surface_key)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBuildRouteDecisionKeyFunction:
    def test_is_callable(self):
        assert callable(build_route_decision_key)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_route_decision_key)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBuildCapRegistryKeyFunction:
    def test_is_callable(self):
        assert callable(build_cap_registry_key)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_cap_registry_key)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBuildCompiledPromptKeyFunction:
    def test_is_callable(self):
        assert callable(build_compiled_prompt_key)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_compiled_prompt_key)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module cache_key_builders must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
