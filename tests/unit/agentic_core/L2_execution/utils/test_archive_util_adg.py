"""Smoke tests for archive_util exports."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution._agentic_core_smoke import import_attr_or_skip


@pytest.mark.unit
class TestArchiveutil:
    """Smoke tests for archive_util exports."""

    def test_module_importable(self) -> None:
        """Import the module export."""
        module = import_attr_or_skip("agentic_core", "archive_util")
        assert module is not None

    def test_module_has_exports(self) -> None:
        """Validate __all__ exports when declared."""
        module = import_attr_or_skip("agentic_core", "archive_util")
        exports = getattr(module, "__all__", ())
        assert all(hasattr(module, name) for name in exports)

    def test_module_docstring_present(self) -> None:
        """Ensure the module docstring is present."""
        module = import_attr_or_skip("agentic_core", "archive_util")
        assert module.__doc__ is not None

    def test_module_attributes_accessible(self) -> None:
        """Ensure public attributes can be enumerated."""
        module = import_attr_or_skip("agentic_core", "archive_util")
        attrs = [name for name in dir(module) if not name.startswith("_")]
        assert isinstance(attrs, list)
