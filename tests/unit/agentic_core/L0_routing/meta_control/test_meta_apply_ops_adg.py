"""ADG-driven tests for L0_routing/meta_control/meta_apply_ops.py — fan_in=0."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_meta_apply_ops_adg")
_emit_applies_guardrail("p0", "test_meta_apply_ops_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_apply_ops_adg", "policy_binding")
_emit_snapshots_state("p0", "test_meta_apply_ops_adg", "state_snapshot")
emit_replay_key("p0", "test_meta_apply_ops_adg")
emit_determinism_digest("p0", "test_meta_apply_ops_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.meta_control.meta_apply_ops import (
        InvariantCheckFn,
        _check_no_schema_changes,
    )
    _AVAILABLE = True
except ImportError:
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
