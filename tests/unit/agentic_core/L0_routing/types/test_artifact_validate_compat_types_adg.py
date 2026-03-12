"""ADG contract tests for L0_routing/types/artifact_validate_compat_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L0_routing.types.artifact_validate_compat_types import (
    validate_result_artifact, validate_healing_plan, validate_incident_artifact,
    to_result_artifact_dict, to_healing_plan_dict,
)

class TestCompatReExports:
    def test_validate_result_artifact_callable(self): assert callable(validate_result_artifact)
    def test_validate_healing_plan_callable(self): assert callable(validate_healing_plan)
    def test_validate_incident_artifact_callable(self): assert callable(validate_incident_artifact)
    def test_to_result_artifact_dict_callable(self): assert callable(to_result_artifact_dict)
    def test_to_healing_plan_dict_callable(self): assert callable(to_healing_plan_dict)
    def test_result_artifact_works(self):
        d = {"trace_id": "t1", "execution_outcome": "ok", "final_state_hash": "h1", "artifact_class": "ac"}
        r = validate_result_artifact(d); assert r["trace_id"] == "t1"
