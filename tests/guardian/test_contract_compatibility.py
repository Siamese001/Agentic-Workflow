"""
Phase A: Contract Compatibility Ratchet.

Ensures the GuardianResult schema cannot drift without a version bump.
Snapshots the frozen key structure and asserts compatibility on every run.

Tests:
1. Top-level keys match CONTRACT_SCHEMA_SNAPSHOT
2. Check-level keys match CHECK_SCHEMA_KEYS
3. Artifact-level keys match ARTIFACT_SCHEMA_KEYS
4. check_schema_compatibility catches extra keys
5. check_schema_compatibility catches missing keys
6. Version bump required on key change (migration test)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_contract_compatibility")
_emit_applies_guardrail("p0", "test_contract_compatibility", "p0_governance")
_emit_reads_policy_state("p0", "test_contract_compatibility", "policy_binding")
_emit_snapshots_state("p0", "test_contract_compatibility", "state_snapshot")
emit_replay_key("p0", "test_contract_compatibility")
emit_determinism_digest("p0", "test_contract_compatibility")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_contract_compatibility", "execution_auth")
_emit_validates_capability("p2", "test_contract_compatibility", "capability_check")
_emit_routes_to_capability("p2", "test_contract_compatibility", "capability_route")
_emit_writes_via_uwg("p2", "test_contract_compatibility", "uwg_write")
_emit_blocks_direct_write("p2", "test_contract_compatibility", "direct_write_block")
_emit_records_tool_invocation("p2", "test_contract_compatibility", "tool_invocation")
_emit_captures_execution_output("p2", "test_contract_compatibility", "exec_output")
_emit_dispatches_agent("p3", "test_contract_compatibility", "agent_dispatch")
_emit_coordinates_agents("p3", "test_contract_compatibility", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_contract_compatibility", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_contract_compatibility", "healing_outcome")
_emit_escalates_failure("p3", "test_contract_compatibility", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_contract_compatibility", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_contract_compatibility", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_contract_compatibility", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_contract_compatibility", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_contract_compatibility", "eval_metric")
_emit_stores_embedding("p4", "test_contract_compatibility", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_contract_compatibility", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_contract_compatibility", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.types.guardian_contract_types import (
    ARTIFACT_SCHEMA_KEYS,
    ARTIFACT_TYPE_VALUES,
    CHECK_SCHEMA_KEYS,
    CHECK_STATUS_VALUES,
    CONTRACT_SCHEMA_SNAPSHOT,
    CONTRACT_VERSION,
    GUARDIAN_STATUS_VALUES,
    ArtifactType,
    CheckStatus,
    GuardianResult,
    GuardianStatus,
    check_schema_compatibility,
    validate_against_json_schema,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
)

_emit_emits_metric_event("test_contract_compatibility", "p4obs", "metric_1")
_emit_emits_metric_event("test_contract_compatibility", "p4obs", "metric_2")
_emit_emits_metric_event("test_contract_compatibility", "p4obs", "metric_3")
_emit_emits_metric_event("test_contract_compatibility", "p4obs", "metric_4")
_emit_emits_metric_event("test_contract_compatibility", "p4obs", "metric_5")
_emit_emits_metric_event("test_contract_compatibility", "p4obs", "metric_6")
_emit_records_incident_event("test_contract_compatibility", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_contract_compatibility", "p4obs", "anomaly")
_emit_writes_observability_log("test_contract_compatibility", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_contract_compatibility", "p4obs", "mon_state")
_emit_triggers_alert("test_contract_compatibility", "p4obs", "alert")
_emit_links_incident_trace("test_contract_compatibility", "p4obs", "trace_link")
_emit_captures_pattern("test_contract_compatibility", "p3lm", "pattern")
_emit_records_learning_event("test_contract_compatibility", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_contract_compatibility", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_contract_compatibility", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_contract_compatibility", "p3lm", "routing")
_emit_improves_agent_policy("test_contract_compatibility", "p3lm", "policy")
_emit_stores_learning_state("test_contract_compatibility", "p3lm", "state")
_emit_records_execution_trace("test_contract_compatibility", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_contract_compatibility", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_contract_compatibility", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_contract_compatibility", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_contract_compatibility", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_contract_compatibility", "env_read", "p2_env_1")
_emit_reads_environ("test_contract_compatibility", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_contract_compatibility", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_contract_compatibility", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_contract_compatibility", "context_pull")
_emit_pulls_context("p1", "test_contract_compatibility", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_contract_compatibility", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_contract_compatibility", "uwg_term_2")
_emit_writes_through("p1", "test_contract_compatibility", "write_through")
_emit_writes_through("p1", "test_contract_compatibility", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_contract_compatibility", "safety_validation")
_emit_invokes_eval("p1", "test_contract_compatibility", "eval_call")
_emit_proposal_commits_routing("p1", "test_contract_compatibility", "routing_commit")
_emit_escalates_to_human("p1", "test_contract_compatibility", "human_escalation")
_emit_routes_through("p1", "test_contract_compatibility", "route_through")
_emit_checks_agent_registry("p1", "test_contract_compatibility", "agent_registry")
_emit_validates_agent_capability("p1", "test_contract_compatibility", "capability")
_emit_dispatches_execution_plan("p1", "test_contract_compatibility", "exec_plan")
_emit_agent_executes_agent("p1", "test_contract_compatibility", "sub_agent")
_emit_routes_to_agent("p1", "test_contract_compatibility", "target_agent")
_emit_verifies_policy("p1", "test_contract_compatibility", "policy_check")
_emit_observes_runtime_state("p1", "test_contract_compatibility", "runtime_state")
_emit_verifies_boundary("p1", "test_contract_compatibility", "boundary_check")
_emit_transcripts_response("p1", "test_contract_compatibility", "transcript")
_emit_hard_fails_untranscripted("p1", "test_contract_compatibility")
_emit_gated_by_confidence("p1", "test_contract_compatibility", "confidence_gate")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# 1. Snapshot fidelity — top-level keys
# ---------------------------------------------------------------------------


class TestSchemaSnapshot:
    """The serialized shape of GuardianResult must match the frozen snapshot."""

    EXPECTED_REQUIRED_KEYS = {
        "guardian_id",
        "version",
        "status",
        "summary",
        "checks",
        "artifacts",
        "metrics",
        "remediation_hints",
    }
    EXPECTED_OPTIONAL_KEYS = {
        "timestamp",
        "correlation_id",
        "index",
        "artifact_class",
        "v15_trace_id",
        "v15_signature",
        "v15_commit_hash",
        "certification_hash",
    }

    def test_snapshot_has_all_required_keys(self):
        assert self.EXPECTED_REQUIRED_KEYS.issubset(CONTRACT_SCHEMA_SNAPSHOT.keys())

    def test_snapshot_has_optional_keys(self):
        assert self.EXPECTED_OPTIONAL_KEYS.issubset(CONTRACT_SCHEMA_SNAPSHOT.keys())

    def test_snapshot_has_no_extra_keys(self):
        all_expected = self.EXPECTED_REQUIRED_KEYS | self.EXPECTED_OPTIONAL_KEYS
        assert set(CONTRACT_SCHEMA_SNAPSHOT.keys()) == all_expected

    def test_result_serialization_matches_snapshot(self):
        r = GuardianResult(guardian_id="compat_test")
        r.add_check("c1", CheckStatus.PASS, "ok")
        r.add_artifact(ArtifactType.JSON, "foo/bar.json", "test")
        d = r.to_dict()
        errors = check_schema_compatibility(d)
        assert errors == [], f"Schema drift: {errors}"

    def test_result_with_optionals_matches(self):
        r = GuardianResult(
            guardian_id="compat_test",
            timestamp="2026-01-01T00:00:00Z",
            correlation_id="abc-123",
        )
        d = r.to_dict()
        errors = check_schema_compatibility(d)
        assert errors == [], f"Schema drift with optionals: {errors}"


# ---------------------------------------------------------------------------
# 2. Check-level key snapshot
# ---------------------------------------------------------------------------


class TestCheckKeySnapshot:
    def test_check_keys_frozen(self):
        assert CHECK_SCHEMA_KEYS == {"check_id", "status", "details", "evidence"}

    def test_check_serialization_matches(self):
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok", evidence={"x": 1})
        check_dict = r.to_dict()["checks"][0]
        assert set(check_dict.keys()) == CHECK_SCHEMA_KEYS


# ---------------------------------------------------------------------------
# 3. Artifact-level key snapshot
# ---------------------------------------------------------------------------


class TestArtifactKeySnapshot:
    def test_artifact_keys_frozen(self):
        assert ARTIFACT_SCHEMA_KEYS == {"type", "path", "description"}

    def test_artifact_serialization_matches(self):
        r = GuardianResult(guardian_id="test")
        r.add_artifact(ArtifactType.JSON, "foo.json", "desc")
        artifact_dict = r.to_dict()["artifacts"][0]
        assert set(artifact_dict.keys()) == ARTIFACT_SCHEMA_KEYS


# ---------------------------------------------------------------------------
# 4. Compatibility gate catches drift
# ---------------------------------------------------------------------------


class TestCompatibilityGate:
    def test_extra_key_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["rogue_key"] = "bad"
        errors = check_schema_compatibility(d)
        assert any("rogue_key" in e for e in errors)

    def test_missing_required_key_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        del d["metrics"]
        errors = check_schema_compatibility(d)
        assert any("metrics" in e for e in errors)

    def test_extra_check_key_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["checks"] = [{"check_id": "c1", "status": "PASS", "details": "ok", "evidence": {}, "extra": True}]
        errors = check_schema_compatibility(d)
        assert any("Check keys mismatch" in e for e in errors)

    def test_clean_result_passes_gate(self):
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok")
        errors = check_schema_compatibility(r.to_dict())
        assert errors == []

    def test_extra_artifact_key_detected(self):
        """Artifact with unexpected key triggers artifact-keys mismatch branch."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["artifacts"] = [
            {"type": "json", "path": "foo.json", "description": "desc", "extra": "x"},
        ]
        errors = check_schema_compatibility(d)
        assert any("Artifact keys mismatch" in e for e in errors)


# ---------------------------------------------------------------------------
# 5. Version bump migration test
# ---------------------------------------------------------------------------


class TestVersionBump:
    def test_contract_version_is_integer(self):
        assert isinstance(CONTRACT_VERSION, int)
        assert CONTRACT_VERSION >= 1

    def test_version_in_result_matches_contract(self):
        r = GuardianResult(guardian_id="test")
        assert r.version == CONTRACT_VERSION

    def test_snapshot_key_count_is_locked(self):
        """If this fails, CONTRACT_VERSION must be bumped."""
        assert len(CONTRACT_SCHEMA_SNAPSHOT) == 16, (
            f"Schema key count changed from 16 to {len(CONTRACT_SCHEMA_SNAPSHOT)}. "
            f"Bump CONTRACT_VERSION from {CONTRACT_VERSION}."
        )


# ---------------------------------------------------------------------------
# 6. JSON Schema validation (Phase 2: Schema-level compatibility)
# ---------------------------------------------------------------------------


class TestJsonSchemaValidation:
    """Validate results against the full JSON Schema snapshot."""

    def test_valid_result_passes_schema(self):
        r = GuardianResult(guardian_id="test")
        r.add_check("c1", CheckStatus.PASS, "ok")
        r.add_artifact(ArtifactType.JSON, "foo.json", "desc")
        errors = validate_against_json_schema(r.to_dict())
        assert errors == [], f"Schema validation errors: {errors}"

    def test_invalid_status_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["status"] = "INVALID_STATUS"
        errors = validate_against_json_schema(d)
        assert any("enum" in e and "INVALID_STATUS" in e for e in errors)

    def test_invalid_check_status_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["checks"] = [{"check_id": "c1", "status": "BADSTATUS", "details": "ok", "evidence": {}}]
        errors = validate_against_json_schema(d)
        assert any("enum" in e for e in errors)

    def test_invalid_artifact_type_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["artifacts"] = [{"type": "badtype", "path": "foo.json", "description": "desc"}]
        errors = validate_against_json_schema(d)
        assert any("enum" in e for e in errors)

    def test_missing_required_field_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        del d["summary"]
        errors = validate_against_json_schema(d)
        assert any("summary" in e for e in errors)

    def test_extra_field_detected(self):
        d = GuardianResult(guardian_id="test").to_dict()
        d["extra_field"] = "should not be here"
        errors = validate_against_json_schema(d)
        assert any("extra_field" in e for e in errors)


# ---------------------------------------------------------------------------
# 7. Enum value locking (Phase 2)
# ---------------------------------------------------------------------------


class TestEnumValueLocking:
    """Enum values are frozen; any change requires version bump."""

    def test_guardian_status_values_locked(self):
        assert GUARDIAN_STATUS_VALUES == {"PASS", "FAIL", "ERROR"}

    def test_check_status_values_locked(self):
        assert CHECK_STATUS_VALUES == {"PASS", "FAIL", "SKIP"}

    def test_artifact_type_values_locked(self):
        assert ARTIFACT_TYPE_VALUES == {"diff", "json", "log", "snapshot"}

    def test_enum_matches_frozen_values(self):
        assert {s.value for s in GuardianStatus} == GUARDIAN_STATUS_VALUES
        assert {s.value for s in CheckStatus} == CHECK_STATUS_VALUES
        assert {t.value for t in ArtifactType} == ARTIFACT_TYPE_VALUES


# ---------------------------------------------------------------------------
# 8. Synthetic breaking change test (Phase 2)
# ---------------------------------------------------------------------------


class TestSyntheticBreakingChange:
    """Demonstrate that schema violations are caught before version bump."""

    def test_new_required_field_fails_without_version_bump(self):
        """A result with a missing field fails validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        del d["remediation_hints"]
        errors = validate_against_json_schema(d)
        assert len(errors) > 0, "Missing required field should fail"

    def test_new_enum_value_fails_validation(self):
        """A result with an invalid enum value fails validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["status"] = "WARNING"  # New value not in schema
        errors = validate_against_json_schema(d)
        assert any("WARNING" in e for e in errors), "New enum value should fail"

    def test_type_change_fails_validation(self):
        """A result with wrong type fails validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["version"] = "1"  # String instead of int
        errors = validate_against_json_schema(d)
        assert any("integer" in e or "version" in e for e in errors)


# ---------------------------------------------------------------------------
# 9. Path validation (Phase 2 hardening)
# ---------------------------------------------------------------------------


class TestPathValidation:
    """Artifact paths must be repo-relative POSIX (no backslashes, no leading slash)."""

    def test_backslash_path_fails_validation(self):
        """Artifact path with backslash fails schema validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["artifacts"] = [{"type": "json", "path": "foo\\bar.json", "description": "desc"}]
        errors = validate_against_json_schema(d)
        assert any("pattern" in e or "path" in e for e in errors), "Backslash should fail"

    def test_absolute_path_fails_validation(self):
        """Artifact path with leading slash fails schema validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["artifacts"] = [{"type": "json", "path": "/foo/bar.json", "description": "desc"}]
        errors = validate_against_json_schema(d)
        assert any("pattern" in e or "path" in e for e in errors), "Leading slash should fail"

    def test_valid_posix_path_passes(self):
        """Valid repo-relative POSIX path passes validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["artifacts"] = [{"type": "json", "path": "docs/reports/foo.json", "description": "desc"}]
        errors = validate_against_json_schema(d)
        assert errors == [], f"Valid POSIX path should pass: {errors}"


# ---------------------------------------------------------------------------
# 10. Schema policy enforcement (Phase 2 hardening)
# ---------------------------------------------------------------------------


class TestSchemaPolicyEnforcement:
    """Schema changes that break policy must fail validation."""

    def test_required_to_optional_breaks_policy(self):
        """Removing a required field is a breaking change."""
        # This test documents the policy: if a field is required,
        # removing it from a result should fail validation.
        d = GuardianResult(guardian_id="test").to_dict()
        del d["checks"]  # Required field
        errors = validate_against_json_schema(d)
        assert any("checks" in e for e in errors), "Missing required field should fail"

    def test_additional_properties_false_enforced(self):
        """additionalProperties: false prevents schema widening."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["new_field"] = "not allowed"
        errors = validate_against_json_schema(d)
        assert any("new_field" in e or "additional" in e.lower() for e in errors)

    def test_check_additional_properties_false_enforced(self):
        """Check objects must not allow additional properties."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["checks"] = [
            {
                "check_id": "c1",
                "status": "PASS",
                "details": "ok",
                "evidence": {},
                "extra_field": "not allowed",
            },
        ]
        errors = validate_against_json_schema(d)
        assert any("extra_field" in e or "additional" in e.lower() for e in errors)

    def test_artifact_additional_properties_false_enforced(self):
        """Artifact objects must not allow additional properties."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["artifacts"] = [
            {
                "type": "json",
                "path": "foo.json",
                "description": "desc",
                "extra_field": "not allowed",
            },
        ]
        errors = validate_against_json_schema(d)
        assert any("extra_field" in e or "additional" in e.lower() for e in errors)


# ---------------------------------------------------------------------------
# 11. Schema bounds enforcement (Phase 2b: metrics/evidence constraints)
# ---------------------------------------------------------------------------


class TestSchemaBoundsEnforcement:
    """Metrics and evidence must respect size and property count bounds."""

    def test_metrics_within_bounds_passes(self):
        """Metrics dict with reasonable size passes validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["metrics"] = {"count": 5, "elapsed_ms": 12.3, "label": "ok"}
        errors = validate_against_json_schema(d)
        assert errors == [], f"Valid metrics should pass: {errors}"

    def test_metrics_exceeding_max_properties_fails(self):
        """Metrics dict with >50 properties fails validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["metrics"] = {f"key_{i}": i for i in range(55)}
        errors = validate_against_json_schema(d)
        assert any("maxProperties" in e or "50" in e for e in errors), (
            f"Exceeding maxProperties should fail: {errors}"
        )

    def test_evidence_within_bounds_passes(self):
        """Evidence dict with reasonable size passes validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["checks"] = [
            {
                "check_id": "c1",
                "status": "PASS",
                "details": "ok",
                "evidence": {"paths": ["a.py", "b.py"], "count": 2},
            },
        ]
        errors = validate_against_json_schema(d)
        assert errors == [], f"Valid evidence should pass: {errors}"

    def test_evidence_exceeding_max_properties_fails(self):
        """Evidence dict with >30 properties fails validation."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["checks"] = [
            {
                "check_id": "c1",
                "status": "PASS",
                "details": "ok",
                "evidence": {f"key_{i}": i for i in range(35)},
            },
        ]
        errors = validate_against_json_schema(d)
        assert any("maxProperties" in e or "30" in e for e in errors), (
            f"Exceeding evidence maxProperties should fail: {errors}"
        )

    def test_payload_size_within_bounds_passes(self):
        """Serialized payload within MAX_PAYLOAD_BYTES passes."""
        d = GuardianResult(guardian_id="test").to_dict()
        errors = validate_against_json_schema(d)
        assert not any("payload" in e.lower() for e in errors)

    def test_payload_size_exceeding_limit_fails(self):
        """Serialized payload exceeding MAX_PAYLOAD_BYTES fails."""
        d = GuardianResult(guardian_id="test").to_dict()
        # Create a large payload that exceeds 512KB
        d["metrics"] = {"big_data": "x" * (600 * 1024)}
        errors = validate_against_json_schema(d)
        assert any("MAX_PAYLOAD_BYTES" in e or "payload" in e.lower() for e in errors), (
            f"Oversized payload should fail: {errors}"
        )


class TestSchemaBoundsConstantsLocked:
    """Schema bounds constants must be immutable and have expected values."""

    def test_max_metrics_properties_value(self):
        from agentic_core.L0_routing.types.guardian_contract_types import MAX_METRICS_PROPERTIES

        assert MAX_METRICS_PROPERTIES == 50

    def test_max_evidence_properties_value(self):
        from agentic_core.L0_routing.types.guardian_contract_types import MAX_EVIDENCE_PROPERTIES

        assert MAX_EVIDENCE_PROPERTIES == 30

    def test_max_payload_bytes_value(self):
        from agentic_core.L0_routing.types.guardian_contract_types import MAX_PAYLOAD_BYTES

        assert MAX_PAYLOAD_BYTES == 512 * 1024

    def test_max_evidence_depth_value(self):
        from agentic_core.L0_routing.types.guardian_contract_types import MAX_EVIDENCE_DEPTH

        assert MAX_EVIDENCE_DEPTH == 4


class TestEvidenceDepthEnforcement:
    """Evidence nesting depth must be enforced by the validator."""

    def _make_result_with_evidence(self, evidence: dict) -> dict:
        d = GuardianResult(guardian_id="depth_test").to_dict()
        d["checks"] = [
            {"check_id": "c1", "status": "PASS", "details": "ok", "evidence": evidence},
        ]
        return d

    def test_evidence_at_max_depth_passes(self):
        """Evidence nested exactly at MAX_EVIDENCE_DEPTH should pass."""
        from agentic_core.L0_routing.types.guardian_contract_types import MAX_EVIDENCE_DEPTH

        # Build nested dict at exactly MAX_EVIDENCE_DEPTH levels
        evidence: dict = {"leaf": "value"}
        for i in range(MAX_EVIDENCE_DEPTH - 1):
            evidence = {f"level_{i}": evidence}

        d = self._make_result_with_evidence(evidence)
        errors = validate_against_json_schema(d)
        depth_errors = [e for e in errors if "MAX_EVIDENCE_DEPTH" in e]
        assert depth_errors == [], f"Evidence at max depth should pass: {depth_errors}"

    def test_evidence_exceeding_max_depth_fails(self):
        """Evidence nested beyond MAX_EVIDENCE_DEPTH must be rejected."""
        from agentic_core.L0_routing.types.guardian_contract_types import MAX_EVIDENCE_DEPTH

        # Build nested dict at MAX_EVIDENCE_DEPTH + 1 levels
        evidence: dict = {"leaf": "value"}
        for i in range(MAX_EVIDENCE_DEPTH):
            evidence = {f"level_{i}": evidence}

        d = self._make_result_with_evidence(evidence)
        errors = validate_against_json_schema(d)
        depth_errors = [e for e in errors if "MAX_EVIDENCE_DEPTH" in e]
        assert len(depth_errors) > 0, f"Evidence at depth {MAX_EVIDENCE_DEPTH + 1} must fail validation"

    def test_evidence_depth_via_array_nesting_fails(self):
        """Arrays in evidence also count towards depth."""
        from agentic_core.L0_routing.types.guardian_contract_types import MAX_EVIDENCE_DEPTH

        # Build mixed dict/list nesting beyond MAX_EVIDENCE_DEPTH
        evidence: dict = {"leaf": "value"}
        for i in range(MAX_EVIDENCE_DEPTH):
            evidence = {f"level_{i}": [evidence]}

        d = self._make_result_with_evidence(evidence)
        errors = validate_against_json_schema(d)
        depth_errors = [e for e in errors if "MAX_EVIDENCE_DEPTH" in e]
        assert len(depth_errors) > 0, "Array-nested evidence beyond max depth must fail validation"

    def test_deeply_nested_metrics_does_not_trigger_evidence_depth(self):
        """Depth guard applies only to evidence, not metrics."""
        d = GuardianResult(guardian_id="test").to_dict()
        d["metrics"] = {"a": {"b": {"c": {"d": {"e": "deep"}}}}}
        errors = validate_against_json_schema(d)
        depth_errors = [e for e in errors if "MAX_EVIDENCE_DEPTH" in e]
        assert depth_errors == [], f"Metrics depth should not trigger evidence depth guard: {depth_errors}"


class TestAggregateOnlyIndexEnforcement:
    """The 'index' field is aggregate-only — forbidden on non-aggregate results."""

    def test_individual_result_with_index_fails(self):
        """Individual (artifact_class=individual) emitting index must fail."""
        from agentic_core.L0_routing.types.guardian_contract_types import ArtifactClass

        d = GuardianResult(guardian_id="hygiene").to_dict()
        assert d.get("artifact_class") == ArtifactClass.INDIVIDUAL.value
        d["index"] = {"hygiene": {"status": "PASS", "artifacts": []}}
        errors = validate_against_json_schema(d)
        index_errors = [e for e in errors if "aggregate-only" in e]
        assert len(index_errors) > 0, "Individual result with index must fail validation"
        assert ArtifactClass.AGGREGATE.value in index_errors[0]

    def test_aggregate_result_with_index_passes(self):
        """Aggregate (artifact_class=aggregate) may have index."""
        from agentic_core.L0_routing.types.guardian_contract_types import (
            AGGREGATE_GUARDIAN_ID,
            ArtifactClass,
        )

        d = GuardianResult(
            guardian_id=AGGREGATE_GUARDIAN_ID,
            artifact_class=ArtifactClass.AGGREGATE,
        ).to_dict()
        d["index"] = {"hygiene": {"status": "PASS", "artifacts": []}}
        errors = validate_against_json_schema(d)
        index_errors = [e for e in errors if "aggregate-only" in e]
        assert index_errors == [], f"Aggregate result with index should pass: {index_errors}"

    def test_non_aggregate_artifact_class_with_index_fails(self):
        """Even with aggregate guardian_id, if artifact_class != aggregate, index rejected."""
        from agentic_core.L0_routing.types.guardian_contract_types import AGGREGATE_GUARDIAN_ID

        d = GuardianResult(guardian_id=AGGREGATE_GUARDIAN_ID).to_dict()
        d["artifact_class"] = "individual"
        d["index"] = {"hygiene": {"status": "PASS", "artifacts": []}}
        errors = validate_against_json_schema(d)
        index_errors = [e for e in errors if "aggregate-only" in e]
        assert len(index_errors) > 0, "Non-aggregate artifact_class with index must fail"

    def test_individual_result_without_index_passes(self):
        """Individual result without index is valid (index is optional)."""
        d = GuardianResult(guardian_id="hygiene").to_dict()
        assert "index" not in d  # to_dict omits empty index
        errors = validate_against_json_schema(d)
        index_errors = [e for e in errors if "aggregate-only" in e or "index" in e.lower()]
        assert index_errors == [], f"Individual without index should pass: {index_errors}"

    def test_aggregate_guardian_id_constant_is_locked(self):
        """AGGREGATE_GUARDIAN_ID must match the hardcoded aggregator value."""
        from agentic_core.L0_routing.types.guardian_contract_types import AGGREGATE_GUARDIAN_ID

        assert AGGREGATE_GUARDIAN_ID == "combined"

    def test_default_artifact_class_is_individual(self):
        """GuardianResult defaults to artifact_class=individual."""
        from agentic_core.L0_routing.types.guardian_contract_types import ArtifactClass

        r = GuardianResult(guardian_id="test")
        assert r.artifact_class == ArtifactClass.INDIVIDUAL.value
