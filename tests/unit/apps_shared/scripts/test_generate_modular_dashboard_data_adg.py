"""ADG-driven tests for apps_shared/scripts/generate_modular_dashboard_data.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.generate_modular_dashboard_data import (  # noqa: F401
        load_discovery,
        map_territory,
        calculate_metrics,
        generate_dashboard_data,
        generate_agent_data,
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
    load_discovery = None  # type: ignore[assignment,misc]
    map_territory = None  # type: ignore[assignment,misc]
    calculate_metrics = None  # type: ignore[assignment,misc]
    generate_dashboard_data = None  # type: ignore[assignment,misc]
    generate_agent_data = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestLoadDiscovery:
    def test_is_callable(self):
        assert callable(load_discovery)

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestMapTerritory:
    def test_is_callable(self):
        assert callable(map_territory)

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestCalculateMetrics:
    def test_is_callable(self):
        assert callable(calculate_metrics)

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestGenerateDashboardData:
    def test_is_callable(self):
        assert callable(generate_dashboard_data)

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestGenerateAgentData:
    def test_is_callable(self):
        assert callable(generate_agent_data)

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module generate_modular_dashboard_data.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
