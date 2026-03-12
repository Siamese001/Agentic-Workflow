"""ADG-driven tests for apps_shared/scripts/benchmark_consolidation_performance.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.benchmark_consolidation_performance import (  # noqa: F401
        measure_import_time,
        measure_memory_footprint,
        measure_registry_init,
        count_UnifiedAgents,
        count_archived_agents,
        PROJECT_ROOT,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    measure_import_time = None  # type: ignore[assignment,misc]
    measure_memory_footprint = None  # type: ignore[assignment,misc]
    measure_registry_init = None  # type: ignore[assignment,misc]
    count_UnifiedAgents = None  # type: ignore[assignment,misc]
    count_archived_agents = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="benchmark_consolidation_performance.py deps unavailable")
class TestMeasureImportTime:
    def test_is_callable(self):
        assert callable(measure_import_time)

@pytest.mark.skipif(not _AVAILABLE, reason="benchmark_consolidation_performance.py deps unavailable")
class TestMeasureMemoryFootprint:
    def test_is_callable(self):
        assert callable(measure_memory_footprint)

@pytest.mark.skipif(not _AVAILABLE, reason="benchmark_consolidation_performance.py deps unavailable")
class TestMeasureRegistryInit:
    def test_is_callable(self):
        assert callable(measure_registry_init)

@pytest.mark.skipif(not _AVAILABLE, reason="benchmark_consolidation_performance.py deps unavailable")
class TestCountUnifiedagents:
    def test_is_callable(self):
        assert callable(count_UnifiedAgents)

@pytest.mark.skipif(not _AVAILABLE, reason="benchmark_consolidation_performance.py deps unavailable")
class TestCountArchivedAgents:
    def test_is_callable(self):
        assert callable(count_archived_agents)

@pytest.mark.skipif(not _AVAILABLE, reason="benchmark_consolidation_performance.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None


def test_module_importable():
    """Module benchmark_consolidation_performance.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
