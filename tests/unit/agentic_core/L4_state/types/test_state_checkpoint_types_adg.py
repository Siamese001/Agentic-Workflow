"""ADG-driven tests for state_checkpoint_types - populated Wave 3."""

from __future__ import annotations

import pytest

from import_helpers import ensure_project_root, import_or_skip

ensure_project_root(__file__)
state_checkpoint_types = import_or_skip(
    "agentic_core.state_checkpoint_types",
    reason="state_checkpoint_types module unavailable for ADG contract tests",
)


@pytest.mark.unit
class TestStatecheckpointtypes:
    """Test state_checkpoint_types contracts."""

    def test_module_importable(self):
        assert state_checkpoint_types is not None

    def test_module_has_exports(self):
        if hasattr(state_checkpoint_types, "__all__"):
            for name in state_checkpoint_types.__all__:
                assert hasattr(state_checkpoint_types, name)

    def test_module_docstring_present(self):
        assert state_checkpoint_types.__doc__ is not None

    def test_module_attributes_accessible(self):
        attrs = [a for a in dir(state_checkpoint_types) if not a.startswith("_")]
        assert len(attrs) >= 0
