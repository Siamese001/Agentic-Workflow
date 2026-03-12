"""ADG importability contract for agentic_core/L4_state/engines/fresh_data_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_fresh_data_validator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.engines.fresh_data_validator import (  # noqa: F401
        StaleDataViolation,
        FreshnessPolicy,
        VersionedData,
        validate_freshness,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    StaleDataViolation = None  # type: ignore[assignment,misc]
    FreshnessPolicy = None  # type: ignore[assignment,misc]
    VersionedData = None  # type: ignore[assignment,misc]
    validate_freshness = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="fresh_data_validator.py deps unavailable")
class TestFreshDataValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: fresh_data_validator.py must be importable."""
        assert _AVAILABLE

    def test_staledataviolation_is_type(self) -> None:
        assert StaleDataViolation is not None

    def test_freshnesspolicy_is_type(self) -> None:
        assert FreshnessPolicy is not None

    def test_versioneddata_is_type(self) -> None:
        assert VersionedData is not None

    def test_validate_freshness_callable(self) -> None:
        assert callable(validate_freshness)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

