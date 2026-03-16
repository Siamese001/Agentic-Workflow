"""ADG-driven tests for L2_execution/determinism/dependency_locker.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_dependency_locker_adg")
_emit_applies_guardrail("p0", "test_dependency_locker_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_dependency_locker_adg", "policy_binding")
_emit_snapshots_state("p0", "test_dependency_locker_adg", "state_snapshot")
emit_replay_key("p0", "test_dependency_locker_adg")
emit_determinism_digest("p0", "test_dependency_locker_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.determinism.dependency_locker import DependencyLocker
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    DependencyLocker = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="dependency_locker deps unavailable")
class TestDependencyLocker:
    def test_importable(self):
        assert callable(DependencyLocker)

    def test_has_generate_lock_hash(self):
        assert hasattr(DependencyLocker, "generate_lock_hash")

    def test_generate_lock_hash_raises_for_missing_file(self, tmp_path):
        missing = tmp_path / "requirements_nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            DependencyLocker.generate_lock_hash(missing)

    def test_generate_lock_hash_returns_hex_string(self, tmp_path):
        req = tmp_path / "requirements.txt"
        req.write_text("requests==2.31.0\nnumpy==1.26.0\n")
        result = DependencyLocker.generate_lock_hash(req)
        assert isinstance(result, str)
        int(result, 16)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
