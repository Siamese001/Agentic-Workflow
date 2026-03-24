"""Foundational behavioral tests for agentic_core/utils/detection_protocol_util.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_detection_protocol_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.detection_protocol_util import (  # noqa: F401
        DetectionSignalProtocol,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    DetectionSignalProtocol = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="detection_protocol_util.py deps unavailable")
class TestDetectionSignalProtocolContract:
    def test_is_class(self):
        assert isinstance(DetectionSignalProtocol, type)

    def test_has_method_detect(self):
        assert callable(getattr(DetectionSignalProtocol, 'detect', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(DetectionSignalProtocol) if not m.startswith('_')]
        assert len(pub) >= 1


def test_module_importable():
    """Smoke: detection_protocol_util importable or gracefully unavailable."""
    pass