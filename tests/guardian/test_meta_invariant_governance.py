"""
V15 P6 Compliance Tests — Meta-Invariants & Typed Boundaries.

Regression tests proving all 4 P6 items + meta-governor are COMPLIANT:
  §1.5  — SSOT Binding (node_id resolves to structure_blueprint)
  §3.8  — Context Retrieval Request Artifact (L0→L4, read-only)
  §12.1 — Inter-agent schema validation
  §2.4  — Boundary schema validation
  META  — MetaInvariantReport + fail_closed_on_violation
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.enforcement.boundary_contracts import (
    BoundarySchemaError,
    ContextRetrievalError,
    MetaInvariantError,
    SSOTBindingError,
    assert_chain_closure,
    assert_cross_run_pins,
    build_boundary_schema,
    build_context_retrieval_request,
    fail_closed_on_violation,
    resolve_ssot_binding,
    run_meta_invariants,
    validate_boundary_schema,
    validate_context_retrieval_read_only,
)
from agentic_core.L0_routing.types.boundary_types import (
    BoundarySchemaDescriptor,
    ContextRetrievalRequest,
    InvariantCheck,
    InvariantSeverity,
    InvariantViolation,
    MetaInvariantReport,
    SchemaValidationStatus,
    SSOTBinding,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_meta_invariant_governance", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_invariant_governance", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_invariant_governance", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_invariant_governance", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_invariant_governance", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_invariant_governance", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_invariant_governance", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_invariant_governance", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_invariant_governance", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_invariant_governance", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_invariant_governance", "p4obs", "alert")
_emit_links_incident_trace("test_meta_invariant_governance", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_invariant_governance", "p3lm", "pattern")
_emit_records_learning_event("test_meta_invariant_governance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_invariant_governance", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_invariant_governance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_invariant_governance", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_invariant_governance", "p3lm", "policy")
_emit_stores_learning_state("test_meta_invariant_governance", "p3lm", "state")
_emit_records_execution_trace("test_meta_invariant_governance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_invariant_governance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_invariant_governance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_invariant_governance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_invariant_governance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_invariant_governance", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_invariant_governance", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_invariant_governance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_invariant_governance", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_meta_invariant_governance")
_emit_applies_guardrail("p0", "test_meta_invariant_governance", "p0_governance")
_emit_reads_policy_state("p0", "test_meta_invariant_governance", "policy_binding")
_emit_snapshots_state("p0", "test_meta_invariant_governance", "state_snapshot")
_emit_pulls_context("p1", "test_meta_invariant_governance", "context_pull")
_emit_pulls_context("p1", "test_meta_invariant_governance", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_meta_invariant_governance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_invariant_governance", "uwg_term_secondary")
_emit_writes_through("p1", "test_meta_invariant_governance", "write_through")
_emit_writes_through("p1", "test_meta_invariant_governance", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_meta_invariant_governance", "safety_validation")
_emit_invokes_eval("p1", "test_meta_invariant_governance", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_invariant_governance", "routing_commit")
emit_replay_key("p0", "test_meta_invariant_governance")
emit_determinism_digest("p0", "test_meta_invariant_governance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_meta_invariant_governance", "execution_auth")
_emit_validates_capability("p2", "test_meta_invariant_governance", "capability_check")
_emit_routes_to_capability("p2", "test_meta_invariant_governance", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_invariant_governance", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_invariant_governance", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_invariant_governance", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_invariant_governance", "exec_output")
_emit_dispatches_agent("p3", "test_meta_invariant_governance", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_invariant_governance", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_invariant_governance", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_invariant_governance", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_invariant_governance", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_invariant_governance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_invariant_governance", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_invariant_governance", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_invariant_governance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_invariant_governance", "eval_metric")
_emit_stores_embedding("p4", "test_meta_invariant_governance", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_invariant_governance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_invariant_governance", "exec_snapshot_link")

# ---- fixtures ---------------------------------------------------------------

SAMPLE_BLUEPRINT = {
    "module.StructureHealerAgent.heal_repository": "L5_safety/reasoning/StructureHealerAgent",
    "module.CodeHealerAgent.heal_all": "L5_safety/reasoning/CodeHealerAgent",
}

KNOWN_SCHEMAS = {
    "surgical_manifest_v1": "1.0.0",
    "evidence_pack_v1": "1.0.0",
    "boundary_snapshot_v1": "1.0.0",
}

PINNED_DISCOVERY_HASH = "f09ec166b82746f6d62cf1c7e9215de70ec29534f784bee95d13798b04da4fd4"
PINNED_SCHEMA_VERSION = "1.3.0"

EXPECTED_ARTIFACTS = frozenset(
    {
        "SurgicalManifest",
        "EvidencePack",
        "PolicyExceptionArtifact",
        "PolicyUpdateProposal",
        "SignatureEnvelope",
        "CognitiveDiffBundle",
    },
)


# =============================================================================
# §1.5 — SSOT Binding
# =============================================================================


class TestP6_15_SSOTBinding:
    """§1.5: node_id resolves to a valid SSOT definition."""

    def test_all_required_fields(self):
        required = {"node_id", "blueprint_entry", "resolved"}
        actual = {f.name for f in dataclasses.fields(SSOTBinding)}
        assert required.issubset(actual)

    def test_frozen(self):
        binding = resolve_ssot_binding(
            "module.StructureHealerAgent.heal_repository",
            SAMPLE_BLUEPRINT,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            binding.node_id = "x"  # type: ignore[misc]

    def test_resolves_valid_node(self):
        binding = resolve_ssot_binding(
            "module.StructureHealerAgent.heal_repository",
            SAMPLE_BLUEPRINT,
        )
        assert binding.resolved is True
        assert "StructureHealerAgent" in binding.blueprint_entry

    def test_unresolved_node_fails(self):
        with pytest.raises(SSOTBindingError, match="does not resolve"):
            resolve_ssot_binding("nonexistent.node", SAMPLE_BLUEPRINT)

    def test_empty_node_id_fails(self):
        with pytest.raises(SSOTBindingError, match="non-empty"):
            resolve_ssot_binding("", SAMPLE_BLUEPRINT)


# =============================================================================
# §3.8 — Context Retrieval Request
# =============================================================================


class TestP6_38_ContextRetrievalRequest:
    """§3.8: Typed L0→L4 request, advisory-only, read-only."""

    def test_all_required_fields(self):
        required = {"trace_id", "query_hash", "semantic_clock_tick"}
        actual = {f.name for f in dataclasses.fields(ContextRetrievalRequest)}
        assert required.issubset(actual)

    def test_frozen(self):
        req = build_context_retrieval_request("t1", "hash123", 5)
        with pytest.raises(dataclasses.FrozenInstanceError):
            req.trace_id = "x"  # type: ignore[misc]

    def test_builds_valid(self):
        req = build_context_retrieval_request("t1", "hash123", 5)
        assert req.source_layer == "L0"
        assert req.target_layer == "L4"
        assert req.read_only is True

    def test_empty_trace_id_rejected(self):
        with pytest.raises(ContextRetrievalError, match="FAIL"):
            build_context_retrieval_request("", "hash", 0)

    def test_empty_query_hash_rejected(self):
        with pytest.raises(ContextRetrievalError, match="FAIL"):
            build_context_retrieval_request("t1", "", 0)

    def test_negative_tick_rejected(self):
        with pytest.raises(ContextRetrievalError, match="FAIL"):
            build_context_retrieval_request("t1", "hash", -1)

    def test_read_only_enforced(self):
        req = build_context_retrieval_request("t1", "hash", 0)
        assert validate_context_retrieval_read_only(req) is True

    def test_write_attempt_rejected(self):
        # Construct with read_only=False via direct init to bypass default
        with pytest.raises(ValueError, match="read_only"):
            ContextRetrievalRequest(
                trace_id="t1",
                query_hash="h",
                semantic_clock_tick=0,
                read_only=False,
            )


# =============================================================================
# §12.1 / §2.4 — Boundary Schema Validation
# =============================================================================


class TestP6_121_BoundarySchemaValidation:
    """§12.1 / §2.4: Inter-agent schema validation, typed boundaries."""

    def test_all_required_fields(self):
        required = {
            "schema_id",
            "schema_version",
            "source_layer",
            "target_layer",
            "validation_status",
        }
        actual = {f.name for f in dataclasses.fields(BoundarySchemaDescriptor)}
        assert required.issubset(actual)

    def test_frozen(self):
        desc = build_boundary_schema("s1", "1.0.0", "L0", "L2", KNOWN_SCHEMAS)
        with pytest.raises(dataclasses.FrozenInstanceError):
            desc.schema_id = "x"  # type: ignore[misc]

    def test_valid_schema_passes(self):
        desc = build_boundary_schema(
            "surgical_manifest_v1",
            "1.0.0",
            "L2",
            "L5",
            KNOWN_SCHEMAS,
        )
        assert desc.validation_status == SchemaValidationStatus.VALID
        assert validate_boundary_schema(desc) is True

    def test_missing_schema_detected(self):
        desc = build_boundary_schema(
            "unknown_schema",
            "1.0.0",
            "L0",
            "L4",
            KNOWN_SCHEMAS,
        )
        assert desc.validation_status == SchemaValidationStatus.MISSING

    def test_missing_schema_fails_validation(self):
        desc = build_boundary_schema(
            "unknown_schema",
            "1.0.0",
            "L0",
            "L4",
            KNOWN_SCHEMAS,
        )
        with pytest.raises(BoundarySchemaError, match="MISSING"):
            validate_boundary_schema(desc)

    def test_version_mismatch_detected(self):
        desc = build_boundary_schema(
            "surgical_manifest_v1",
            "2.0.0",
            "L2",
            "L5",
            KNOWN_SCHEMAS,
        )
        assert desc.validation_status == SchemaValidationStatus.INVALID

    def test_version_mismatch_fails_validation(self):
        desc = build_boundary_schema(
            "surgical_manifest_v1",
            "2.0.0",
            "L2",
            "L5",
            KNOWN_SCHEMAS,
        )
        with pytest.raises(BoundarySchemaError, match="INVALID"):
            validate_boundary_schema(desc)

    def test_no_registry_defaults_valid(self):
        desc = build_boundary_schema("any", "1.0.0", "L0", "L2")
        assert desc.validation_status == SchemaValidationStatus.VALID

    def test_non_descriptor_rejected(self):
        with pytest.raises(BoundarySchemaError, match="dict"):
            validate_boundary_schema({"schema_id": "x"})  # type: ignore[arg-type]

    def test_empty_schema_id_rejected(self):
        with pytest.raises(ValueError, match="schema_id"):
            BoundarySchemaDescriptor(
                schema_id="",
                schema_version="1.0",
                source_layer="L0",
                target_layer="L2",
                validation_status=SchemaValidationStatus.VALID,
            )


# =============================================================================
# Meta-Governor: Cross-Run Pins
# =============================================================================


class TestP6_MetaCrossRunPins:
    """Meta-governor: cross-run pinned values."""

    def test_matching_pins_pass(self):
        check, violation = assert_cross_run_pins(
            PINNED_DISCOVERY_HASH,
            PINNED_DISCOVERY_HASH,
            PINNED_SCHEMA_VERSION,
            PINNED_SCHEMA_VERSION,
        )
        assert check.passed is True
        assert violation is None

    def test_discovery_hash_mismatch_fails(self):
        check, violation = assert_cross_run_pins(
            "wrong_hash",
            PINNED_DISCOVERY_HASH,
            PINNED_SCHEMA_VERSION,
            PINNED_SCHEMA_VERSION,
        )
        assert check.passed is False
        assert violation is not None
        assert violation.severity == InvariantSeverity.CRITICAL
        assert "discovery_hash" in violation.details

    def test_schema_version_mismatch_fails(self):
        check, violation = assert_cross_run_pins(
            PINNED_DISCOVERY_HASH,
            PINNED_DISCOVERY_HASH,
            "9.9.9",
            PINNED_SCHEMA_VERSION,
        )
        assert check.passed is False
        assert violation is not None
        assert "schema_version" in violation.details

    def test_both_mismatch_captures_both(self):
        check, violation = assert_cross_run_pins(
            "wrong",
            PINNED_DISCOVERY_HASH,
            "wrong",
            PINNED_SCHEMA_VERSION,
        )
        assert check.passed is False
        assert violation is not None
        assert "discovery_hash" in violation.details
        assert "schema_version" in violation.details


# =============================================================================
# Meta-Governor: Chain Closure
# =============================================================================


class TestP6_MetaChainClosure:
    """Meta-governor: artifact chain closure detection."""

    def test_matching_sets_pass(self):
        check, violation = assert_chain_closure(
            EXPECTED_ARTIFACTS,
            EXPECTED_ARTIFACTS,
        )
        assert check.passed is True
        assert violation is None

    def test_missing_artifact_detected(self):
        actual = EXPECTED_ARTIFACTS - {"EvidencePack"}
        check, violation = assert_chain_closure(EXPECTED_ARTIFACTS, actual)
        assert check.passed is False
        assert violation is not None
        assert "missing" in violation.details

    def test_orphan_artifact_detected(self):
        actual = EXPECTED_ARTIFACTS | {"UnknownArtifact"}
        check, violation = assert_chain_closure(EXPECTED_ARTIFACTS, actual)
        assert check.passed is False
        assert violation is not None
        assert "orphans" in violation.details

    def test_both_missing_and_orphan(self):
        actual = (EXPECTED_ARTIFACTS - {"EvidencePack"}) | {"Orphan"}
        check, violation = assert_chain_closure(EXPECTED_ARTIFACTS, actual)
        assert check.passed is False
        assert "missing" in violation.details
        assert "orphans" in violation.details


# =============================================================================
# Meta-Governor: run_meta_invariants + fail_closed_on_violation
# =============================================================================


class TestP6_MetaGovernor:
    """Meta-governor: full report + fail-closed."""

    def test_all_green_report(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-001",
            semantic_clock_tick=10,
            discovery_hash=PINNED_DISCOVERY_HASH,
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS,
        )
        assert report.pass_fail is True
        assert len(report.violations) == 0
        assert len(report.checks) == 2
        assert fail_closed_on_violation(report) is True

    def test_violation_report(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-002",
            semantic_clock_tick=10,
            discovery_hash="wrong",
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS,
        )
        assert report.pass_fail is False
        assert len(report.violations) == 1

    def test_fail_closed_raises(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-003",
            semantic_clock_tick=10,
            discovery_hash="wrong",
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS,
        )
        with pytest.raises(MetaInvariantError, match="FAIL"):
            fail_closed_on_violation(report)

    def test_report_frozen(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-001",
            semantic_clock_tick=0,
            discovery_hash=PINNED_DISCOVERY_HASH,
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            report.pass_fail = False  # type: ignore[misc]

    def test_report_fields(self):
        required = {
            "trace_id",
            "run_id",
            "semantic_clock_tick",
            "checks",
            "pass_fail",
            "violations",
        }
        actual = {f.name for f in dataclasses.fields(MetaInvariantReport)}
        assert required.issubset(actual)

    def test_report_rejects_pass_with_violations(self):
        violation = InvariantViolation(
            invariant_id="test",
            severity=InvariantSeverity.HIGH,
            evidence_paths=("file.py",),
            details="test violation",
        )
        with pytest.raises(ValueError, match="pass_fail cannot be True"):
            MetaInvariantReport(
                trace_id="t1",
                run_id="r1",
                semantic_clock_tick=0,
                checks=(),
                pass_fail=True,
                violations=(violation,),
            )

    def test_multiple_violations_all_captured(self):
        report = run_meta_invariants(
            trace_id="t1",
            run_id="run-004",
            semantic_clock_tick=10,
            discovery_hash="wrong",
            expected_discovery_hash=PINNED_DISCOVERY_HASH,
            schema_version=PINNED_SCHEMA_VERSION,
            expected_schema_version=PINNED_SCHEMA_VERSION,
            expected_artifacts=EXPECTED_ARTIFACTS,
            actual_artifacts=EXPECTED_ARTIFACTS - {"EvidencePack"},
        )
        assert report.pass_fail is False
        assert len(report.violations) == 2

    def test_invariant_violation_fields(self):
        required = {"invariant_id", "severity", "evidence_paths", "details"}
        actual = {f.name for f in dataclasses.fields(InvariantViolation)}
        assert required.issubset(actual)

    def test_invariant_check_fields(self):
        required = {"check_id", "description", "passed", "evidence"}
        actual = {f.name for f in dataclasses.fields(InvariantCheck)}
        assert required.issubset(actual)
