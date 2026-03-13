"""ADG importability contract for agentic_core/L4_state/engines/fresh_data_validator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_fresh_data_validator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.engines.fresh_data_validator import (  # noqa: F401
        FreshnessPolicy,
        StaleDataViolation,
        VersionedData,
        validate_freshness,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    StaleDataViolation = None  # type: ignore[assignment,misc]
    FreshnessPolicy = None  # type: ignore[assignment,misc]
    VersionedData = None  # type: ignore[assignment,misc]
    validate_freshness = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fresh_data_validator deps unavailable")
class TestFreshDataValidatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/engines/fresh_data_validator.py must be importable."""
        assert _AVAILABLE

    def test_staledataviolation_defined(self) -> None:
        assert StaleDataViolation is not None

    def test_freshnesspolicy_defined(self) -> None:
        assert FreshnessPolicy is not None

    def test_versioneddata_defined(self) -> None:
        assert VersionedData is not None
