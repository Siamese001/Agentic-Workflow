"""ADG contract tests for L0_routing/types/artifact_validators_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L0_routing.types.artifact_validators_types import (
    validate_result_artifact, to_result_artifact_dict,
    validate_healing_plan, to_healing_plan_dict,
    validate_incident_artifact,
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
