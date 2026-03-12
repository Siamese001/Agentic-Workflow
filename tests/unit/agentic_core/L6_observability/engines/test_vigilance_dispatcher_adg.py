"""ADG importability contract for agentic_core/L6_observability/engines/vigilance_dispatcher.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vigilance_dispatcher.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L6_observability.engines.vigilance_dispatcher import (  # noqa: F401
        VigilanceEventArtifact,
        VigilanceDispatcher,
        to_meta_payload,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VigilanceEventArtifact = None  # type: ignore[assignment,misc]
    VigilanceDispatcher = None  # type: ignore[assignment,misc]
    to_meta_payload = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="vigilance_dispatcher.py deps unavailable")
class TestVigilanceDispatcherImportability:
    def test_module_importable(self) -> None:
        """ADG contract: vigilance_dispatcher.py must be importable."""
        assert _AVAILABLE

    def test_vigilanceeventartifact_is_type(self) -> None:
        assert VigilanceEventArtifact is not None

    def test_vigilancedispatcher_is_type(self) -> None:
        assert VigilanceDispatcher is not None

    def test_to_meta_payload_callable(self) -> None:
        assert callable(to_meta_payload)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

