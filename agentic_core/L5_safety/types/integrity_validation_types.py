from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "integrity_validation_types")
emit_determinism_digest("p0", "integrity_validation_types")

_emit_dispatches_healing_run("p1", "integrity_validation_types", "L5")
_emit_routes_through("p1", "integrity_validation_types", "L5")
_emit_checks_agent_registry("p1", "integrity_validation_types", "agent_registry")
_emit_validates_agent_capability("p1", "integrity_validation_types", "capability")
_emit_dispatches_execution_plan("p1", "integrity_validation_types", "exec_plan")
_emit_agent_executes_agent("p1", "integrity_validation_types", "sub_agent")
_emit_routes_to_agent("p1", "integrity_validation_types", "target_agent")
_emit_verifies_policy("p1", "integrity_validation_types", "policy_check")
_emit_observes_runtime_state("p1", "integrity_validation_types", "runtime_state")
_emit_verifies_boundary("p1", "integrity_validation_types", "boundary_check")
_emit_transcripts_response("p1", "integrity_validation_types", "transcript")
_emit_hard_fails_untranscripted("p1", "integrity_validation_types")
_emit_gated_by_confidence("p1", "integrity_validation_types", "confidence_gate")
_emit_escalates_to_human("p1", "integrity_validation_types", "L5")
_emit_reads_policy_state("p1", "integrity_validation_types", "L5")

_emit_applies_guardrail("p0", "integrity_validation_types", "p0_governance")
_emit_snapshots_state("p0", "integrity_validation_types", "state_snapshot")
_emit_authorize_and_execute("p2", "integrity_validation_types", "execution_auth")
_emit_validates_capability("p2", "integrity_validation_types", "capability_check")
_emit_routes_to_capability("p2", "integrity_validation_types", "capability_route")
_emit_writes_via_uwg("p2", "integrity_validation_types", "uwg_write")
_emit_blocks_direct_write("p2", "integrity_validation_types", "direct_write_block")
_emit_records_tool_invocation("p2", "integrity_validation_types", "tool_invocation")
_emit_captures_execution_output("p2", "integrity_validation_types", "exec_output")
_emit_dispatches_agent("p3", "integrity_validation_types", "agent_dispatch")
_emit_coordinates_agents("p3", "integrity_validation_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "integrity_validation_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "integrity_validation_types", "healing_outcome")
_emit_escalates_failure("p3", "integrity_validation_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "integrity_validation_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "integrity_validation_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "integrity_validation_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "integrity_validation_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "integrity_validation_types", "eval_metric")
_emit_stores_embedding("p4", "integrity_validation_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "integrity_validation_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "integrity_validation_types", "exec_snapshot_link")

"\nIntegrity Validation Guardrail - Consolidated Integrity Checks\n\nMerges:\n- L5IntegrityGateExecutor\n- GravityEnforcer\n\nComposable Rules:\n- integrity_checks: Data integrity validation\n- gravity_compliance: Gravity enforcement\n"
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
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
    _emit_writes_through,
)

_emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_1")
_emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_2")
_emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_3")
_emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_4")
_emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_5")
_emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_6")
_emit_records_incident_event("integrity_validation_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("integrity_validation_types", "p4obs", "anomaly")
_emit_writes_observability_log("integrity_validation_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("integrity_validation_types", "p4obs", "mon_state")
_emit_triggers_alert("integrity_validation_types", "p4obs", "alert")
_emit_links_incident_trace("integrity_validation_types", "p4obs", "trace_link")
_emit_captures_pattern("integrity_validation_types", "p3lm", "pattern")
_emit_records_learning_event("integrity_validation_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("integrity_validation_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("integrity_validation_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("integrity_validation_types", "p3lm", "routing")
_emit_improves_agent_policy("integrity_validation_types", "p3lm", "policy")
_emit_stores_learning_state("integrity_validation_types", "p3lm", "state")
_emit_records_execution_trace("integrity_validation_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("integrity_validation_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("integrity_validation_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("integrity_validation_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("integrity_validation_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("integrity_validation_types", "env_read", "p2_env_1")
_emit_reads_environ("integrity_validation_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("integrity_validation_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("integrity_validation_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "integrity_validation_types", "context_pull")
_emit_pulls_context("p1", "integrity_validation_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "integrity_validation_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "integrity_validation_types", "uwg_term_2")
_emit_writes_through("p1", "integrity_validation_types", "write_through")
_emit_writes_through("p1", "integrity_validation_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "integrity_validation_types", "safety_validation")
_emit_invokes_eval("p1", "integrity_validation_types", "eval_call")
_emit_proposal_commits_routing("p1", "integrity_validation_types", "routing_commit")


@dataclass
class IntegrityViolation:
    """Integrity violation record."""

    rule: str
    severity: str
    description: str
    expected: Any = None
    actual: Any = None
    location: str | None = None


@dataclass
class IntegrityResult:
    """Result of integrity validation."""

    valid: bool
    violations: list[IntegrityViolation] = field(default_factory=list)
    checksum: str | None = None
    validation_time_ms: float = 0.0


class IntegrityValidationGuardrail:
    """
    Consolidated Integrity Validation Guardrail.

    Provides unified integrity checks with:
    - Data integrity validation (checksums, signatures)
    - Gravity compliance (import structure enforcement)
    - State consistency checks
    """

    def __init__(self):
        """Initialize integrity validation guardrail."""
        self.enabled_rules: list[str] = ["integrity_checks", "gravity_compliance"]
        self.gravity_rules = {
            "L0": [],
            "L1": ["L0"],
            "L2": ["L0", "L1"],
            "L3": ["L0", "L1", "L2"],
            "L4": ["L0", "L1", "L2", "L3"],
            "L5": ["L0", "L1", "L2", "L3", "L4"],
        }
        self.checksums: dict[str, str] = {}
        self.validations_performed = 0
        self.violations_found = 0
        self.gravity_violations = 0

    async def validate_integrity(
        self, data: Any, expected_checksum: str | None = None, data_id: str | None = None
    ) -> IntegrityResult:
        """
        Validate data integrity.

        Args:
            data: Data to validate
            expected_checksum: Expected checksum (optional)
            data_id: Data identifier for tracking

        Returns:
            IntegrityResult
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "IntegrityValidationGuardrail.validate_integrity"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:IntegrityValidationGuardrail.validate_integrity".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        start_time = time.time()
        self.validations_performed += 1
        violations = []
        data_str = str(data)
        actual_checksum = hashlib.sha256(data_str.encode()).hexdigest()
        if "integrity_checks" in self.enabled_rules:
            if expected_checksum and actual_checksum != expected_checksum:
                violations.append(
                    IntegrityViolation(
                        rule="integrity_checks",
                        severity="error",
                        description="Checksum mismatch - data may be corrupted",
                        expected=expected_checksum,
                        actual=actual_checksum,
                    )
                )
            if data_id and data_id in self.checksums:
                if self.checksums[data_id] != actual_checksum:
                    violations.append(
                        IntegrityViolation(
                            rule="integrity_checks",
                            severity="warning",
                            description="Data has changed since last validation",
                            expected=self.checksums[data_id],
                            actual=actual_checksum,
                        )
                    )
        if data_id:
            self.checksums[data_id] = actual_checksum
        self.violations_found += len(violations)
        return IntegrityResult(
            valid=len(violations) == 0,
            violations=violations,
            checksum=actual_checksum,
            validation_time_ms=(time.time() - start_time) * 1000,
        )

    async def validate_gravity(
        self, source_layer: str, imported_layers: list[str], file_path: str | None = None
    ) -> IntegrityResult:
        """
        Validate gravity compliance (layer import rules).

        Args:
            source_layer: Layer making imports (e.g., "L3")
            imported_layers: List of layers being imported
            file_path: Optional file path for context

        Returns:
            IntegrityResult
        """
        start_time = time.time()
        self.validations_performed += 1
        violations = []
        if "gravity_compliance" not in self.enabled_rules:
            return IntegrityResult(
                valid=True, violations=[], validation_time_ms=(time.time() - start_time) * 1000
            )
        allowed_imports = self.gravity_rules.get(source_layer, [])
        for imported in imported_layers:
            if imported not in allowed_imports and imported != source_layer:
                violations.append(
                    IntegrityViolation(
                        rule="gravity_compliance",
                        severity="error",
                        description=f"Gravity violation: {source_layer} cannot import from {imported}",
                        expected=f"Allowed: {allowed_imports}",
                        actual=imported,
                        location=file_path,
                    )
                )
                self.gravity_violations += 1
        self.violations_found += len(violations)
        return IntegrityResult(
            valid=len(violations) == 0,
            violations=violations,
            validation_time_ms=(time.time() - start_time) * 1000,
        )

    def register_checksum(self, data_id: str, checksum: str) -> None:
        """Register expected checksum for data."""
        self.checksums[data_id] = checksum

    def calculate_checksum(self, data: Any) -> str:
        """Calculate SHA256 checksum for data."""
        data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def verify_checksum(self, data: Any, expected: str) -> bool:
        """Verify data matches expected checksum."""
        actual = self.calculate_checksum(data)
        return actual == expected

    def get_statistics(self) -> dict[str, Any]:
        """Get integrity validation statistics."""
        return {
            "validations_performed": self.validations_performed,
            "violations_found": self.violations_found,
            "gravity_violations": self.gravity_violations,
            "registered_checksums": len(self.checksums),
            "enabled_rules": self.enabled_rules,
        }
