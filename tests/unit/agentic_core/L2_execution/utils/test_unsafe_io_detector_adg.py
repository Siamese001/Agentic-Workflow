"""Smoke tests for unsafe_io_detector_adg exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestUnsafeIoDetectorAdg:
    """Smoke tests for unsafe_io_detector_adg exports."""

    def test_unsafe_io_detector_adg_imports(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "unsafe_io_detector_adg")
        assert module is not None

    def test_unsafe_io_detector_adg_class(self) -> None:
        """Import the class export."""
        klass = import_attr_or_skip("agentic_core", "UnsafeIoDetectorAdg")
        assert klass is not None

    def test_unsafe_io_detector_adg_callable(self) -> None:
        """Import the validator export."""
        validator = import_attr_or_skip("agentic_core", "validate_unsafe_io_detector_adg")
        assert callable(validator)
