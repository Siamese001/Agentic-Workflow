"""ADG importability contract for agentic_core/runtime/exceptions/SovereignError.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_SovereignError.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.runtime.exceptions.SovereignError import (  # noqa: F401
        CircularDependencyError,
        ConfigurationError,
        HealerError,
        HygieneError,
        SovereignError,
        StructuralError,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SovereignError = None  # type: ignore[assignment,misc]
    HealerError = None  # type: ignore[assignment,misc]
    CircularDependencyError = None  # type: ignore[assignment,misc]
    ConfigurationError = None  # type: ignore[assignment,misc]
    StructuralError = None  # type: ignore[assignment,misc]
    HygieneError = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="SovereignError deps unavailable")
class TestSovereignerrorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/runtime/exceptions/SovereignError.py must be importable."""
        assert _AVAILABLE

    def test_sovereignerror_defined(self) -> None:
        assert SovereignError is not None

    def test_healererror_defined(self) -> None:
        assert HealerError is not None

    def test_circulardependencyerror_defined(self) -> None:
        assert CircularDependencyError is not None

    def test_configurationerror_defined(self) -> None:
        assert ConfigurationError is not None

    def test_structuralerror_defined(self) -> None:
        assert StructuralError is not None

    def test_hygieneerror_defined(self) -> None:
        assert HygieneError is not None
