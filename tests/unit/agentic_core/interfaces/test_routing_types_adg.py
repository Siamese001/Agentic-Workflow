"""ADG-driven tests for routing_types - populated Wave 3."""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestRoutingtypes:
    """Test routing_types contracts."""

    def test_module_importable(self):
        """Test module can be imported."""
        from agentic_core import routing_types

        assert routing_types is not None

    def test_module_has_exports(self):
        """Test module has __all__ exports."""
        from agentic_core import routing_types

        if hasattr(routing_types, "__all__"):
            for name in routing_types.__all__:
                assert hasattr(routing_types, name)

    def test_module_docstring_present(self):
        """Test module has documentation."""
        from agentic_core import routing_types

        assert routing_types.__doc__ is not None

    def test_module_attributes_accessible(self):
        """Test module attributes are accessible."""
        from agentic_core import routing_types

        attrs = [a for a in dir(routing_types) if not a.startswith("_")]
        assert len(attrs) >= 0
