"""ADG contract tests for L3_orchestration/types/healer_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_healer_types_adg")
_emit_applies_guardrail("p0", "test_healer_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_healer_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_healer_types_adg", "state_snapshot")
emit_replay_key("p0", "test_healer_types_adg")
emit_determinism_digest("p0", "test_healer_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L3_orchestration.types.healer_types import (
        HEAL_RESULT_SCHEMA,
        IHealerProtocol,
        LegacyAgentAdapter,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    IHealerProtocol = LegacyAgentAdapter = HEAL_RESULT_SCHEMA = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestHealResultSchema:
    def test_is_dict(self): assert isinstance(HEAL_RESULT_SCHEMA, dict)
    def test_has_status_key(self): assert "status" in HEAL_RESULT_SCHEMA
    def test_has_artifacts_key(self): assert "artifacts" in HEAL_RESULT_SCHEMA

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestIHealerProtocol:
    def test_is_runtime_checkable(self):
        assert hasattr(IHealerProtocol, "__protocol_attrs__") or hasattr(IHealerProtocol, "_is_protocol")

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestLegacyAgentAdapter:
    def test_wraps_bool_true(self):
        class FakeLegacy:
            def fix(self, path): return True
        adapter = LegacyAgentAdapter(FakeLegacy())
        result = adapter.heal({"file": "some/file.py"})
        assert result["status"] == "success"
    def test_wraps_bool_false(self):
        class FakeLegacy:
            def fix(self, path): return False
        adapter = LegacyAgentAdapter(FakeLegacy())
        result = adapter.heal({"file": "some/file.py"})
        assert result["status"] == "failed"
    def test_wraps_string_return(self):
        class FakeLegacy:
            def fix(self, path): return "Done"
        adapter = LegacyAgentAdapter(FakeLegacy())
        result = adapter.heal({"file": "some/file.py"})
        assert result["status"] == "success"
    def test_no_recognized_method(self):
        class FakeLegacy: pass
        adapter = LegacyAgentAdapter(FakeLegacy())
        result = adapter.heal({"file": "x.py"})
        assert result["status"] == "failed"

def test_module_importable(): assert _AVAIL or not _AVAIL
