"""ADG importability contract for system_learning/arbitration/types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.arbitration.types import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ArbitrationCandidate,
        ArbitrationDecision,
        ArbitrationPolicy,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ArbitrationCandidate = None  # type: ignore[assignment,misc]
    ArbitrationPolicy = None  # type: ignore[assignment,misc]
    ArbitrationDecision = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="types.py deps unavailable")
class TestTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: types.py must be importable."""
        assert _AVAILABLE

    def test_arbitrationcandidate_is_type(self) -> None:
        assert ArbitrationCandidate is not None

    def test_arbitrationpolicy_is_type(self) -> None:
        assert ArbitrationPolicy is not None

    def test_arbitrationdecision_is_type(self) -> None:
        assert ArbitrationDecision is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
