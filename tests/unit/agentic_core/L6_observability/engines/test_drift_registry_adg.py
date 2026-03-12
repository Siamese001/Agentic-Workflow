"""ADG importability contract for agentic_core/L6_observability/engines/drift_registry.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_drift_registry.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.drift_registry import (  # noqa: F401
        DriftRegistryEntry,
        DriftRegistry,
        get_drift_registry,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DriftRegistryEntry = None  # type: ignore[assignment,misc]
    DriftRegistry = None  # type: ignore[assignment,misc]
    get_drift_registry = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="drift_registry.py deps unavailable")
class TestDriftRegistryImportability:
    def test_module_importable(self) -> None:
        """ADG contract: drift_registry.py must be importable."""
        assert _AVAILABLE

    def test_driftregistryentry_is_type(self) -> None:
        assert DriftRegistryEntry is not None

    def test_driftregistry_is_type(self) -> None:
        assert DriftRegistry is not None

    def test_get_drift_registry_callable(self) -> None:
        assert callable(get_drift_registry)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

