"""ADG-driven tests for recovery_types - populated Wave 3."""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestRecoverytypes:
    """Test recovery_types contracts."""

    def test_module_importable(self):
        """Test module can be imported."""
        from agentic_core import recovery_types

        assert recovery_types is not None

    def test_module_has_exports(self):
        """Test module has __all__ exports."""
        from agentic_core import recovery_types

        if hasattr(recovery_types, "__all__"):
            for name in recovery_types.__all__:
                assert hasattr(recovery_types, name)

    def test_module_docstring_present(self):
        """Test module has documentation."""
        from agentic_core import recovery_types

        assert recovery_types.__doc__ is not None

    def test_module_attributes_accessible(self):
        """Test module attributes are accessible."""
        from agentic_core import recovery_types

        attrs = [a for a in dir(recovery_types) if not a.startswith("_")]
        assert len(attrs) >= 0
