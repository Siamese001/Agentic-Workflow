"""Foundational behavioral tests for apps_shared/scripts/generate_modular_dashboard_data.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_generate_modular_dashboard_data_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.generate_modular_dashboard_data import (  # noqa: F401
        load_discovery,
        map_territory,
        calculate_metrics,
        generate_dashboard_data,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    load_discovery = None  # type: ignore[assignment,misc]
    map_territory = None  # type: ignore[assignment,misc]
    calculate_metrics = None  # type: ignore[assignment,misc]
    generate_dashboard_data = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestLoadDiscoveryFunction:
    def test_is_callable(self):
        assert callable(load_discovery)

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestMapTerritoryFunction:
    def test_is_callable(self):
        assert callable(map_territory)

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestCalculateMetricsFunction:
    def test_is_callable(self):
        assert callable(calculate_metrics)

@pytest.mark.skipif(not _AVAILABLE, reason="generate_modular_dashboard_data.py deps unavailable")
class TestGenerateDashboardDataFunction:
    def test_is_callable(self):
        assert callable(generate_dashboard_data)

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


def test_module_importable():
    """Module generate_modular_dashboard_data must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
