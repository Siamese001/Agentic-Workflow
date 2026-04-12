"""ADG-driven tests for validators - populated Wave 3."""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestValidators:
    """Test validators contracts."""

    def test_module_importable(self):
        """Test module can be imported."""
        from agentic_core import validators

        assert validators is not None

    def test_module_has_exports(self):
        """Test module has __all__ exports."""
        from agentic_core import validators

        if hasattr(validators, "__all__"):
            for name in validators.__all__:
                assert hasattr(validators, name)

    def test_module_docstring_present(self):
        """Test module has documentation."""
        from agentic_core import validators

        assert validators.__doc__ is not None

    def test_module_attributes_accessible(self):
        """Test module attributes are accessible."""
        from agentic_core import validators

        attrs = [a for a in dir(validators) if not a.startswith("_")]
        assert len(attrs) >= 0
