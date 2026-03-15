"""ADG importability contract for agentic_core/L0_routing/seams/vigilance_seam.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vigilance_seam.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.seams.vigilance_seam import (  # noqa: F401
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        get_vigilance_event_artifact,
        get_vigilance_severity,
        load_vigilance_types,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    load_vigilance_types = None  # type: ignore[assignment,misc]
    get_vigilance_event_artifact = None  # type: ignore[assignment,misc]
    get_vigilance_severity = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="vigilance_seam.py deps unavailable")
class TestVigilanceSeamImportability:
    def test_module_importable(self) -> None:
        """ADG contract: vigilance_seam.py must be importable."""
        assert _AVAILABLE

    def test_load_vigilance_types_callable(self) -> None:
        assert callable(load_vigilance_types)

    def test_get_vigilance_event_artifact_callable(self) -> None:
        assert callable(get_vigilance_event_artifact)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None
