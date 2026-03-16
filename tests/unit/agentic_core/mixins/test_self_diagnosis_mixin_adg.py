"""ADG-driven tests for mixins/self_diagnosis_mixin.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_self_diagnosis_mixin_adg")
_emit_applies_guardrail("p0", "test_self_diagnosis_mixin_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_self_diagnosis_mixin_adg", "policy_binding")
_emit_snapshots_state("p0", "test_self_diagnosis_mixin_adg", "state_snapshot")
emit_replay_key("p0", "test_self_diagnosis_mixin_adg")
emit_determinism_digest("p0", "test_self_diagnosis_mixin_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.mixins.self_diagnosis_mixin import SelfDiagnosisMixin


class TestSelfDiagnosisMixin:
    def test_importable(self):
        assert callable(SelfDiagnosisMixin)

    def test_mandatory_components_default_empty(self):
        assert SelfDiagnosisMixin.MANDATORY_COMPONENTS == []

    def test_has_self_diagnose(self):
        assert hasattr(SelfDiagnosisMixin, "self_diagnose")

    def test_creates(self):
        mixin = SelfDiagnosisMixin()
        assert mixin is not None
