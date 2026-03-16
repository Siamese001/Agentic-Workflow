"""ADG contract tests for L0_routing/types/artifact_validators_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_artifact_validators_types_adg")
_emit_applies_guardrail("p0", "test_artifact_validators_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_artifact_validators_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_artifact_validators_types_adg", "state_snapshot")
emit_replay_key("p0", "test_artifact_validators_types_adg")
emit_determinism_digest("p0", "test_artifact_validators_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L0_routing.types.artifact_validators_types import (
    validate_healing_plan,
    validate_incident_artifact,
    validate_result_artifact,
)


class TestValidateResultArtifact:
    def test_valid_dict(self):
        d = {"trace_id": "t1", "execution_outcome": "ok", "final_state_hash": "h1", "artifact_class": "ac"}
        r = validate_result_artifact(d); assert r["trace_id"] == "t1"
    def test_missing_field_raises(self):
        with pytest.raises(ValueError): validate_result_artifact({"trace_id": "t1"})
    def test_emitting_layer_defaults(self):
        d = {"trace_id": "t1", "execution_outcome": "ok", "final_state_hash": "h1", "artifact_class": "ac"}
        r = validate_result_artifact(d); assert r["emitting_layer"] == "L2"
    def test_unsupported_type_raises(self):
        with pytest.raises(TypeError): validate_result_artifact("not_a_dict")  # type: ignore[arg-type]

class TestValidateHealingPlan:
    def test_valid_dict(self):
        d = {"trace_id": "t1", "plan_id": "p1", "policy_liaison_node": "pln",
             "manifests": ["m1"], "semantic_clock_tick": 1}
        r = validate_healing_plan(d); assert r["plan_id"] == "p1"
    def test_missing_field_raises(self):
        with pytest.raises(ValueError): validate_healing_plan({"trace_id": "t1"})

class TestValidateIncidentArtifact:
    def test_valid_dict(self):
        d = {"trace_id": "t1", "incident_id": "i1", "correlation_hash": "ch",
             "severity_enum": "high", "telemetry_events": ["e1"]}
        r = validate_incident_artifact(d); assert r["incident_id"] == "i1"
