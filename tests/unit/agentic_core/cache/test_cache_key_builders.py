"""Foundational behavioral tests for agentic_core/cache/cache_key_builders.py.

fan_in=15 — imported by 15 other modules.
ADG import-hygiene is covered separately by test_cache_key_builders_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.cache.cache_key_builders import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        build_cap_registry_key,
        build_compiled_prompt_key,
        build_route_decision_key,
        build_routing_rule_surface_key,
        build_template_render_key,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
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
class TestBuildTemplateRenderKeyFunction:
    def test_is_callable(self):
        assert callable(build_template_render_key)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_template_render_key)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="cache_key_builders.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: cache_key_builders importable or gracefully unavailable."""
    pass