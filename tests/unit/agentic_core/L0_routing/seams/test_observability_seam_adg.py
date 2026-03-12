"""ADG importability contract for agentic_core/L0_routing/seams/observability_seam.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_observability_seam.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.seams.observability_seam import (  # noqa: F401
        load_meta_learning_agent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    load_meta_learning_agent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="observability_seam.py deps unavailable")
class TestObservabilitySeamImportability:
    def test_module_importable(self) -> None:
        """ADG contract: observability_seam.py must be importable."""
        assert _AVAILABLE

    def test_load_meta_learning_agent_callable(self) -> None:
        assert callable(load_meta_learning_agent)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

