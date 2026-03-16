"""ADG contract tests for L0_routing/types/artifact_validate_compat_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_artifact_validate_compat_types_adg")
_emit_applies_guardrail("p0", "test_artifact_validate_compat_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_artifact_validate_compat_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_artifact_validate_compat_types_adg", "state_snapshot")
emit_replay_key("p0", "test_artifact_validate_compat_types_adg")
emit_determinism_digest("p0", "test_artifact_validate_compat_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
pytestmark = pytest.mark.unit
from agentic_core.L0_routing.types.artifact_validate_compat_types import (
    to_healing_plan_dict,
    to_result_artifact_dict,
    validate_healing_plan,
    validate_incident_artifact,
    validate_result_artifact,
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
