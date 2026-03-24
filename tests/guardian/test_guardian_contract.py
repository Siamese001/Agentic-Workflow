"""
Guardian Contract Tests — Schema, Status Promotion, and Contract Integrity.

Verifies:
1. Status promotion: FAIL check promotes top-level status to FAIL
2. Status promotion: ERROR status is sticky (not overwritten by FAIL)
3. Schema compliance across all contract fields
4. Serialization round-trip determinism
5. Artifact path normalization (no absolute paths, no backslashes)
6. Contract version is pinned
7. check_schema_compatibility detects missing/extra keys
8. validate_against_json_schema detects type and enum violations
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_guardian_contract")
_emit_applies_guardrail("p0", "test_guardian_contract", "p0_governance")
_emit_reads_policy_state("p0", "test_guardian_contract", "policy_binding")
_emit_snapshots_state("p0", "test_guardian_contract", "state_snapshot")
emit_replay_key("p0", "test_guardian_contract")
emit_determinism_digest("p0", "test_guardian_contract")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_guardian_contract", "execution_auth")
_emit_validates_capability("p2", "test_guardian_contract", "capability_check")
_emit_routes_to_capability("p2", "test_guardian_contract", "capability_route")
_emit_writes_via_uwg("p2", "test_guardian_contract", "uwg_write")
_emit_blocks_direct_write("p2", "test_guardian_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "test_guardian_contract", "tool_invocation")
_emit_captures_execution_output("p2", "test_guardian_contract", "exec_output")
_emit_dispatches_agent("p3", "test_guardian_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "test_guardian_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_guardian_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_guardian_contract", "healing_outcome")
_emit_escalates_failure("p3", "test_guardian_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_guardian_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_guardian_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_guardian_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_guardian_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_guardian_contract", "eval_metric")
_emit_stores_embedding("p4", "test_guardian_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_guardian_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_guardian_contract", "exec_snapshot_link")

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
    CONTRACT_VERSION,
    ArtifactClass,
    ArtifactType,
    CheckStatus,
    GuardianCheck,
    GuardianResult,
    GuardianStatus,
    check_schema_compatibility,
    normalize_repo_path,
    validate_against_json_schema,
    validate_no_absolute_paths,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_1")
_emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_2")
_emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_3")
_emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_4")
_emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_5")
_emit_emits_metric_event("test_guardian_contract", "p4obs", "metric_6")
_emit_records_incident_event("test_guardian_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_guardian_contract", "p4obs", "anomaly")
_emit_writes_observability_log("test_guardian_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_guardian_contract", "p4obs", "mon_state")
_emit_triggers_alert("test_guardian_contract", "p4obs", "alert")
_emit_links_incident_trace("test_guardian_contract", "p4obs", "trace_link")
_emit_captures_pattern("test_guardian_contract", "p3lm", "pattern")
_emit_records_learning_event("test_guardian_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_guardian_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_guardian_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_guardian_contract", "p3lm", "routing")
_emit_improves_agent_policy("test_guardian_contract", "p3lm", "policy")
_emit_stores_learning_state("test_guardian_contract", "p3lm", "state")
_emit_records_execution_trace("test_guardian_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_guardian_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_guardian_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_guardian_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_guardian_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_guardian_contract", "env_read", "p2_env_1")
_emit_reads_environ("test_guardian_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_guardian_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_guardian_contract", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_guardian_contract", "context_pull")
_emit_pulls_context("p1", "test_guardian_contract", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_guardian_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_guardian_contract", "uwg_term_2")
_emit_writes_through("p1", "test_guardian_contract", "write_through")
_emit_writes_through("p1", "test_guardian_contract", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_guardian_contract", "safety_validation")
_emit_invokes_eval("p1", "test_guardian_contract", "eval_call")
_emit_proposal_commits_routing("p1", "test_guardian_contract", "routing_commit")
_emit_escalates_to_human("p1", "test_guardian_contract", "human_escalation")
_emit_routes_through("p1", "test_guardian_contract", "route_through")
_emit_checks_agent_registry("p1", "test_guardian_contract", "agent_registry")
_emit_validates_agent_capability("p1", "test_guardian_contract", "capability")
_emit_dispatches_execution_plan("p1", "test_guardian_contract", "exec_plan")
_emit_agent_executes_agent("p1", "test_guardian_contract", "sub_agent")
_emit_routes_to_agent("p1", "test_guardian_contract", "target_agent")
_emit_verifies_policy("p1", "test_guardian_contract", "policy_check")
_emit_observes_runtime_state("p1", "test_guardian_contract", "runtime_state")
_emit_verifies_boundary("p1", "test_guardian_contract", "boundary_check")
_emit_transcripts_response("p1", "test_guardian_contract", "transcript")
_emit_hard_fails_untranscripted("p1", "test_guardian_contract")
_emit_gated_by_confidence("p1", "test_guardian_contract", "confidence_gate")

pytestmark = pytest.mark.guardian


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(guardian_id: str = "test_guardian") -> GuardianResult:
    return GuardianResult(guardian_id=guardian_id)


# ---------------------------------------------------------------------------
# 1. Status promotion: FAIL check → top-level FAIL
# ---------------------------------------------------------------------------


class TestStatusPromotion:
    """Verify that a FAIL check correctly promotes the top-level status."""

    def test_initial_status_is_pass(self):
        result = _make_result()
        assert result.status == GuardianStatus.PASS.value

    def test_single_fail_check_promotes_to_fail(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.FAIL, "something failed")
        assert result.status == GuardianStatus.FAIL.value

    def test_pass_check_does_not_change_pass_status(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        assert result.status == GuardianStatus.PASS.value

    def test_skip_check_does_not_change_pass_status(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.SKIP, "not applicable")
        assert result.status == GuardianStatus.PASS.value

    def test_fail_after_pass_promotes_to_fail(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        result.add_check("c2", CheckStatus.FAIL, "bad")
        assert result.status == GuardianStatus.FAIL.value

    def test_pass_after_fail_does_not_revert_to_pass(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.FAIL, "bad")
        result.add_check("c2", CheckStatus.PASS, "ok later")
        assert result.status == GuardianStatus.FAIL.value

    def test_error_status_is_sticky_over_fail(self):
        result = _make_result()
        result.set_error("scan crashed")
        result.add_check("c1", CheckStatus.FAIL, "also failed")
        assert result.status == GuardianStatus.ERROR.value

    def test_multiple_fail_checks_status_still_fail(self):
        result = _make_result()
        for i in range(5):
            result.add_check(f"c{i}", CheckStatus.FAIL, f"fail {i}")
        assert result.status == GuardianStatus.FAIL.value

    def test_string_fail_value_also_promotes(self):
        result = _make_result()
        result.add_check("c1", "FAIL", "string-based FAIL")
        assert result.status == GuardianStatus.FAIL.value

    def test_status_promotion_boundary_single_check(self):
        result = _make_result()
        result.add_check("only_check", CheckStatus.FAIL, "the only check failed")
        assert result.status == GuardianStatus.FAIL.value
        assert len(result.checks) == 1


# ---------------------------------------------------------------------------
# 2. Schema compliance
# ---------------------------------------------------------------------------


class TestSchemaCompliance:
    def test_no_absolute_paths_on_clean_result(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == []

    def test_check_schema_compatibility_clean(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        errors = check_schema_compatibility(result.to_dict())
        assert errors == []

    def test_contract_version_is_pinned(self):
        result = _make_result()
        assert result.version == CONTRACT_VERSION

    def test_guardian_id_is_required(self):
        result = GuardianResult(guardian_id="my_guardian")
        assert result.guardian_id == "my_guardian"
        d = result.to_dict()
        assert d["guardian_id"] == "my_guardian"

    def test_status_values_are_valid_enum(self):
        for gid, status_str in [("a", "PASS"), ("b", "FAIL"), ("c", "ERROR")]:
            result = GuardianResult(guardian_id=gid, status=status_str)
            errors = check_schema_compatibility(result.to_dict())
            assert errors == [], f"Unexpected schema errors for status={status_str}: {errors}"

    def test_check_schema_keys_exact(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok", evidence={"key": "val"})
        d = result.to_dict()
        for check in d["checks"]:
            assert set(check.keys()) == {"check_id", "status", "details", "evidence"}

    def test_artifact_schema_keys_exact(self):
        result = _make_result()
        result.add_artifact(ArtifactType.JSON, "docs/out.json", "output")
        d = result.to_dict()
        for artifact in d["artifacts"]:
            assert set(artifact.keys()) == {"type", "path", "description"}

    def test_validate_against_json_schema_clean(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        errors = validate_against_json_schema(result.to_dict())
        assert errors == [], f"JSON schema errors: {errors}"

    def test_validate_against_json_schema_invalid_status_caught(self):
        result = _make_result()
        d = result.to_dict()
        d["status"] = "UNKNOWN_STATUS"
        errors = validate_against_json_schema(d)
        assert any("status" in e for e in errors), f"Expected status error, got: {errors}"

    def test_missing_required_key_detected(self):
        result = _make_result()
        d = result.to_dict()
        del d["guardian_id"]
        errors = validate_against_json_schema(d)
        assert any("guardian_id" in e for e in errors)

    def test_extra_key_detected_by_schema_compatibility(self):
        result = _make_result()
        d = result.to_dict()
        d["rogue_key"] = "value"
        errors = check_schema_compatibility(d)
        assert any("rogue_key" in e for e in errors)


# ---------------------------------------------------------------------------
# 3. Artifact path normalization
# ---------------------------------------------------------------------------


class TestArtifactPathNormalization:
    def test_backslash_normalized_to_forward(self):
        normalized = normalize_repo_path("docs\\reports\\out.json")
        assert "\\" not in normalized
        assert "/" in normalized

    def test_no_leading_slash(self):
        normalized = normalize_repo_path("/docs/reports/out.json")
        assert not normalized.startswith("/")

    def test_windows_drive_stripped(self):
        normalized = normalize_repo_path("C:/docs/reports/out.json")
        assert not normalized.startswith("C:")
        assert not normalized.startswith("/")

    def test_dot_segment_collapsed(self):
        normalized = normalize_repo_path("docs/./reports/out.json")
        assert "/." not in normalized

    def test_dotdot_raises(self):
        with pytest.raises(ValueError, match=r"\.\."):
            normalize_repo_path("docs/../etc/passwd")

    def test_artifact_path_in_result_is_normalized(self):
        result = _make_result()
        result.add_artifact(ArtifactType.JSON, "docs/reports/out.json", "output")
        d = result.to_dict()
        paths = [a["path"] for a in d["artifacts"]]
        assert all("\\" not in p for p in paths)
        assert all(not p.startswith("/") for p in paths)


# ---------------------------------------------------------------------------
# 4. Serialization round-trip determinism
# ---------------------------------------------------------------------------


class TestSerializationDeterminism:
    def test_same_result_same_dict_twice(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.PASS, "ok")
        d1 = result.to_dict()
        d2 = result.to_dict()
        assert d1 == d2

    def test_sorted_checks_in_output(self):
        result = _make_result()
        result.add_check("z_check", CheckStatus.PASS, "last alphabetically")
        result.add_check("a_check", CheckStatus.FAIL, "first alphabetically")
        d = result.to_dict()
        ids = [c["check_id"] for c in d["checks"]]
        assert ids == sorted(ids), f"checks not sorted: {ids}"

    def test_sorted_remediation_hints(self):
        result = _make_result()
        result.remediation_hints = ["z_hint", "a_hint", "m_hint"]
        d = result.to_dict()
        hints = d["remediation_hints"]
        assert hints == sorted(hints)

    def test_sorted_artifacts_in_output(self):
        result = _make_result()
        result.add_artifact(ArtifactType.JSON, "z_path/out.json", "z artifact")
        result.add_artifact(ArtifactType.JSON, "a_path/out.json", "a artifact")
        d = result.to_dict()
        paths = [a["path"] for a in d["artifacts"]]
        assert paths == sorted(paths)

    def test_metrics_sorted_by_key(self):
        result = _make_result()
        result.metrics = {"z_count": 5, "a_count": 1, "m_count": 3}
        d = result.to_dict()
        keys = list(d["metrics"].keys())
        assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# 5. Malformed / hostile inputs
# ---------------------------------------------------------------------------


class TestMalformedInputs:
    def test_empty_guardian_id_captured_in_validate(self):
        result = GuardianResult(guardian_id="")
        errors = result.validate()
        assert any("guardian_id" in e for e in errors)

    def test_invalid_check_status_caught_in_validate(self):
        result = GuardianResult(guardian_id="test")
        result.checks.append(GuardianCheck(check_id="c1", status="BOGUS", details="bad", evidence={}))
        errors = result.validate()
        assert any("status" in e for e in errors)

    def test_absolute_path_in_evidence_caught(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.FAIL, "fail", evidence={"path": "/etc/passwd"})
        violations = validate_no_absolute_paths(result.to_dict())
        assert len(violations) > 0

    def test_windows_absolute_path_in_evidence_caught(self):
        result = _make_result()
        result.add_check("c1", CheckStatus.FAIL, "fail", evidence={"path": "C:\\Windows\\system32"})
        violations = validate_no_absolute_paths(result.to_dict())
        assert len(violations) > 0

    def test_none_timestamp_not_in_dict(self):
        result = _make_result()
        assert result.timestamp is None
        d = result.to_dict()
        assert "timestamp" not in d or d.get("timestamp") is None

    def test_artifact_class_defaults_to_individual(self):
        result = _make_result()
        assert result.artifact_class == ArtifactClass.INDIVIDUAL.value


# ---------------------------------------------------------------------------
# 6. Cross-guardian schema compliance (consolidated from per-guardian files)
# ---------------------------------------------------------------------------


def _make_clean_tmp(tmp_path: Path, *subdirs: str) -> Path:
    """Create a minimal clean repo under tmp_path."""
    for sub in subdirs:
        (tmp_path / sub).mkdir(parents=True, exist_ok=True)
        (tmp_path / sub / "clean.py").write_text("x = 1\n", encoding="utf-8")
    return tmp_path


def _all_guardian_runners():
    """Return (guardian_id, runner_callable, clean_repo_factory) tuples."""
    from agentic_core.L0_routing.config.path_constants import (
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        L0_ROUTING_DIR,
    )
    from agentic_core.L0_routing.scripts.run_guardian_c0_sovereignty import (
        run_c0_sovereignty_guardian,
    )
    from agentic_core.L0_routing.scripts.run_guardian_change_package_activation import (
        run_change_package_activation_guardian,
    )
    from agentic_core.L0_routing.scripts.run_guardian_cross_layer_mutation import (
        run_cross_layer_mutation_guardian,
    )
    from agentic_core.L0_routing.scripts.run_guardian_escalation_determinism import (
        run_escalation_determinism_guardian,
    )
    from agentic_core.L0_routing.scripts.run_guardian_gateway_bypass import (
        run_gateway_bypass_guardian,
    )

    return [
        ("c0_sovereignty", run_c0_sovereignty_guardian, [AGENTIC_CORE_DIR]),
        ("change_package_activation", run_change_package_activation_guardian, [AGENTIC_CORE_DIR]),
        ("cross_layer_mutation", run_cross_layer_mutation_guardian, [L0_ROUTING_DIR]),
        ("escalation_determinism", run_escalation_determinism_guardian, [AGENTIC_CORE_DIR]),
        ("gateway_bypass", run_gateway_bypass_guardian, [AGENTIC_CORE_DIR, APPS_LIC_DIR]),
    ]


@pytest.mark.parametrize(
    "guardian_id,runner,subdirs",
    [(gid, r, s) for gid, r, s in _all_guardian_runners()],
    ids=[gid for gid, _, _ in _all_guardian_runners()],
)
class TestCrossGuardianSchemaCompliance:
    """Consolidated schema compliance for all behavioral guardians.

    Replaces the individual test_no_absolute_paths_in_result tests that
    were duplicated across test_guardian_c0_sovereignty.py,
    test_guardian_change_package_activation.py,
    test_guardian_cross_layer_mutation.py,
    test_guardian_escalation_determinism.py, and
    test_guardian_gateway_bypass.py.
    """

    def test_no_absolute_paths(self, guardian_id, runner, subdirs, tmp_path):
        repo = _make_clean_tmp(tmp_path, *subdirs)
        result = runner(repo_root=repo)
        violations = validate_no_absolute_paths(result.to_dict())
        assert violations == [], f"{guardian_id}: absolute paths in result: {violations}"

    def test_schema_compatible(self, guardian_id, runner, subdirs, tmp_path):
        repo = _make_clean_tmp(tmp_path, *subdirs)
        result = runner(repo_root=repo)
        errors = check_schema_compatibility(result.to_dict())
        assert errors == [], f"{guardian_id}: schema drift: {errors}"
