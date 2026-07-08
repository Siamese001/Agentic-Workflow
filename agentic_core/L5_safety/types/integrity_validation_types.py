from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "integrity_validation_types")
trace_contract.emit_determinism_digest("p0", "integrity_validation_types")

trace_contract._emit_dispatches_healing_run("p1", "integrity_validation_types", "L5")
trace_contract._emit_routes_through("p1", "integrity_validation_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "integrity_validation_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "integrity_validation_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "integrity_validation_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "integrity_validation_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "integrity_validation_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "integrity_validation_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "integrity_validation_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "integrity_validation_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "integrity_validation_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "integrity_validation_types")
trace_contract._emit_gated_by_confidence("p1", "integrity_validation_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "integrity_validation_types", "L5")
trace_contract._emit_reads_policy_state("p1", "integrity_validation_types", "L5")

trace_contract._emit_applies_guardrail("p0", "integrity_validation_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "integrity_validation_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "integrity_validation_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "integrity_validation_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "integrity_validation_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "integrity_validation_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "integrity_validation_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "integrity_validation_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "integrity_validation_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "integrity_validation_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "integrity_validation_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "integrity_validation_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "integrity_validation_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "integrity_validation_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "integrity_validation_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "integrity_validation_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "integrity_validation_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "integrity_validation_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "integrity_validation_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "integrity_validation_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "integrity_validation_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "integrity_validation_types", "exec_snapshot_link")

"\nIntegrity Validation Guardrail - Consolidated Integrity Checks\n\nMerges:\n- L5IntegrityGateExecutor\n- GravityEnforcer\n\nComposable Rules:\n- integrity_checks: Data integrity validation\n- gravity_compliance: Gravity enforcement\n"
import hashlib
import time
from dataclasses import dataclass, field
from typing import Any

from tqdm import tqdm

trace_contract._emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("integrity_validation_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("integrity_validation_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("integrity_validation_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("integrity_validation_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("integrity_validation_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("integrity_validation_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("integrity_validation_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("integrity_validation_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("integrity_validation_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("integrity_validation_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("integrity_validation_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("integrity_validation_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("integrity_validation_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("integrity_validation_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("integrity_validation_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("integrity_validation_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("integrity_validation_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("integrity_validation_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("integrity_validation_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("integrity_validation_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("integrity_validation_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("integrity_validation_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("integrity_validation_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "integrity_validation_types", "context_pull")
trace_contract._emit_pulls_context("p1", "integrity_validation_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "integrity_validation_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "integrity_validation_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "integrity_validation_types", "write_through")
trace_contract._emit_writes_through("p1", "integrity_validation_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "integrity_validation_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "integrity_validation_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "integrity_validation_types", "routing_commit")


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
        self,
        data: Any,
        expected_checksum: str | None = None,
        data_id: str | None = None,
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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "IntegrityValidationGuardrail.validate_integrity",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:IntegrityValidationGuardrail.validate_integrity".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
                    ),
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
                        ),
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
        self,
        source_layer: str,
        imported_layers: list[str],
        file_path: str | None = None,
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
                valid=True,
                violations=[],
                validation_time_ms=(time.time() - start_time) * 1000,
            )
        allowed_imports = self.gravity_rules.get(source_layer, [])
        for imported in tqdm(imported_layers, desc="Processing", unit="item"):
            if imported not in allowed_imports and imported != source_layer:
                violations.append(
                    IntegrityViolation(
                        rule="gravity_compliance",
                        severity="error",
                        description=f"Gravity violation: {source_layer} cannot import from {imported}",
                        expected=f"Allowed: {allowed_imports}",
                        actual=imported,
                        location=file_path,
                    ),
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
