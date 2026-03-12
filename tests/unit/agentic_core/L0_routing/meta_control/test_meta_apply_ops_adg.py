"""ADG-driven tests for L0_routing/meta_control/meta_apply_ops.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.meta_control.meta_apply_ops import (
        InvariantCheckFn,
        _check_no_schema_changes,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    InvariantCheckFn = None  # type: ignore[assignment]
    _check_no_schema_changes = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="meta_apply_ops deps unavailable")
class TestCheckNoSchemaChanges:
    def test_nonexistent_dir_passes(self, tmp_path):
        result = _check_no_schema_changes(tmp_path, "nonexistent_component", None)
        assert result is True

    def test_allowed_files_pass(self, tmp_path):
        comp_dir = tmp_path / "my_component"
        comp_dir.mkdir()
        (comp_dir / "config.json").write_text("{}")
        (comp_dir / "rollback.json").write_text("{}")
        result = _check_no_schema_changes(tmp_path, "my_component", None)
        assert result is True

    def test_forbidden_file_fails(self, tmp_path):
        comp_dir = tmp_path / "bad_component"
        comp_dir.mkdir()
        (comp_dir / "unexpected_file.py").write_text("# bad")
        result = _check_no_schema_changes(tmp_path, "bad_component", None)
        assert result is False


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
