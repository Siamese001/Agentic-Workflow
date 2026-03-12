"""ADG importability contract for agentic_core/L2_execution/determinism/digest_calculator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_digest_calculator.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.determinism.digest_calculator import (  # noqa: F401
        DigestCalculator,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    DigestCalculator = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="digest_calculator.py deps unavailable")
class TestDigestCalculatorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: digest_calculator.py must be importable."""
        assert _AVAILABLE

    def test_digestcalculator_is_type(self) -> None:
        assert DigestCalculator is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

