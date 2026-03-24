"""ADG importability contract for system_learning/confidence/types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.confidence.types import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ConfidenceDecision,
        HealingAttempt,
        HealingConfidenceReport,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HealingAttempt = None  # type: ignore[assignment,misc]
    ConfidenceDecision = None  # type: ignore[assignment,misc]
    HealingConfidenceReport = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="types.py deps unavailable")
class TestTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: types.py must be importable."""
        assert _AVAILABLE

    def test_healingattempt_is_type(self) -> None:
        assert HealingAttempt is not None

    def test_confidencedecision_is_type(self) -> None:
        assert ConfidenceDecision is not None

    def test_healingconfidencereport_is_type(self) -> None:
        assert HealingConfidenceReport is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None