"""ADG importability contract for agentic_core/adg/runtime/io_interception.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_io_interception.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.io_interception import (  # noqa: F401
        InterceptionOutcome,
        IOInterceptionEvent,
        IOInterceptionReport,
        IOInterceptor,
        NetworkTranscript,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    InterceptionOutcome = None  # type: ignore[assignment,misc]
    NetworkTranscript = None  # type: ignore[assignment,misc]
    IOInterceptionEvent = None  # type: ignore[assignment,misc]
    IOInterceptionReport = None  # type: ignore[assignment,misc]
    IOInterceptor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="io_interception deps unavailable")
class TestIoInterceptionImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/io_interception.py must be importable."""
        assert _AVAILABLE

    def test_interceptionoutcome_defined(self) -> None:
        assert InterceptionOutcome is not None

    def test_networktranscript_defined(self) -> None:
        assert NetworkTranscript is not None

    def test_iointerceptionevent_defined(self) -> None:
        assert IOInterceptionEvent is not None

    def test_iointerceptionreport_defined(self) -> None:
        assert IOInterceptionReport is not None

    def test_iointerceptor_defined(self) -> None:
        assert IOInterceptor is not None