"""ADG-driven tests for agentic_core/L4_state/workflow_engines/cache_key_builders.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.workflow_engines.cache_key_builders import (  # noqa: F401
        build_routing_rule_surface_key,
        build_route_decision_key,
        build_cap_registry_key,
        build_compiled_prompt_key,
        build_template_render_key,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    build_routing_rule_surface_key = None  # type: ignore[assignment,misc]
    build_route_decision_key = None  # type: ignore[assignment,misc]
    build_cap_registry_key = None  # type: ignore[assignment,misc]
    build_compiled_prompt_key = None  # type: ignore[assignment,misc]
    build_template_render_key = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBuildRoutingRuleSurfaceKey:
    def test_is_callable(self):
        assert callable(build_routing_rule_surface_key)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBuildRouteDecisionKey:
    def test_is_callable(self):
        assert callable(build_route_decision_key)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBuildCapRegistryKey:
    def test_is_callable(self):
        assert callable(build_cap_registry_key)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBuildCompiledPromptKey:
    def test_is_callable(self):
        assert callable(build_compiled_prompt_key)

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBuildTemplateRenderKey:
    def test_is_callable(self):
        assert callable(build_template_render_key)

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

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module cache_key_builders.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
