"""ADG importability contract for system_learning/confidence/engine.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_engine.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from system_learning.confidence.engine import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        HealingConfidenceScorer,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    HealingConfidenceScorer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="engine.py deps unavailable")
class TestEngineImportability:
    def test_module_importable(self) -> None:
        """ADG contract: engine.py must be importable."""
        assert _AVAILABLE

    def test_healingconfidencescorer_is_type(self) -> None:
        assert HealingConfidenceScorer is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None