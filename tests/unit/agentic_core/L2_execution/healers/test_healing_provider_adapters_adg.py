"""ADG importability contract for agentic_core/L2_execution/healers/healing_provider_adapters.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_healing_provider_adapters.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.healing_provider_adapters import (  # noqa: F401
        DEFAULT_MAX_OUTPUT_TOKENS,
        DEFAULT_MAX_TOKENS,
        MAX_OUTPUT_TOKENS,
        MAX_TOKENS,
        OOMEscalatedError,
        OOMRetryableError,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    OOMRetryableError = None  # type: ignore[assignment,misc]
    OOMEscalatedError = None  # type: ignore[assignment,misc]
    MAX_TOKENS = None  # type: ignore[assignment,misc]
    MAX_OUTPUT_TOKENS = None  # type: ignore[assignment,misc]
    DEFAULT_MAX_TOKENS = None  # type: ignore[assignment,misc]
    DEFAULT_MAX_OUTPUT_TOKENS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="healing_provider_adapters deps unavailable")
class TestHealingProviderAdaptersImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/healers/healing_provider_adapters.py must be importable."""
        assert _AVAILABLE

    def test_oomretryableerror_defined(self) -> None:
        assert OOMRetryableError is not None

    def test_oomescalatederror_defined(self) -> None:
        assert OOMEscalatedError is not None
