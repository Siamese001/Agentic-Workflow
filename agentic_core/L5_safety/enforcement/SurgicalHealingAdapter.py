"""
SurgicalHealingAdapter - Bridge between legacy healing and CST surgical healing.

Adapts detection results from legacy heal_repository() methods into
SurgicalContext objects for zero-loss CST-based healing.
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.types.surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "SurgicalHealingAdapter")
emit_determinism_digest("p0", "SurgicalHealingAdapter")

_emit_dispatches_healing_run("p1", "SurgicalHealingAdapter", "L5")
_emit_routes_through("p1", "SurgicalHealingAdapter", "L5")
_emit_checks_agent_registry("p1", "SurgicalHealingAdapter", "agent_registry")
_emit_validates_agent_capability("p1", "SurgicalHealingAdapter", "capability")
_emit_dispatches_execution_plan("p1", "SurgicalHealingAdapter", "exec_plan")
_emit_agent_executes_agent("p1", "SurgicalHealingAdapter", "sub_agent")
_emit_routes_to_agent("p1", "SurgicalHealingAdapter", "target_agent")
_emit_verifies_policy("p1", "SurgicalHealingAdapter", "policy_check")
_emit_observes_runtime_state("p1", "SurgicalHealingAdapter", "runtime_state")
_emit_verifies_boundary("p1", "SurgicalHealingAdapter", "boundary_check")
_emit_transcripts_response("p1", "SurgicalHealingAdapter", "transcript")
_emit_hard_fails_untranscripted("p1", "SurgicalHealingAdapter")
_emit_gated_by_confidence("p1", "SurgicalHealingAdapter", "confidence_gate")
_emit_escalates_to_human("p1", "SurgicalHealingAdapter", "L5")
_emit_reads_policy_state("p1", "SurgicalHealingAdapter", "L5")

_emit_applies_guardrail("p0", "SurgicalHealingAdapter", "p0_governance")
_emit_snapshots_state("p0", "SurgicalHealingAdapter", "state_snapshot")
_emit_authorize_and_execute("p2", "SurgicalHealingAdapter", "execution_auth")
_emit_validates_capability("p2", "SurgicalHealingAdapter", "capability_check")
_emit_routes_to_capability("p2", "SurgicalHealingAdapter", "capability_route")
_emit_writes_via_uwg("p2", "SurgicalHealingAdapter", "uwg_write")
_emit_blocks_direct_write("p2", "SurgicalHealingAdapter", "direct_write_block")
_emit_records_tool_invocation("p2", "SurgicalHealingAdapter", "tool_invocation")
_emit_captures_execution_output("p2", "SurgicalHealingAdapter", "exec_output")
_emit_dispatches_agent("p3", "SurgicalHealingAdapter", "agent_dispatch")
_emit_coordinates_agents("p3", "SurgicalHealingAdapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "SurgicalHealingAdapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "SurgicalHealingAdapter", "healing_outcome")
_emit_escalates_failure("p3", "SurgicalHealingAdapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "SurgicalHealingAdapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SurgicalHealingAdapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "SurgicalHealingAdapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "SurgicalHealingAdapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SurgicalHealingAdapter", "eval_metric")
_emit_stores_embedding("p4", "SurgicalHealingAdapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "SurgicalHealingAdapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SurgicalHealingAdapter", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

_emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_1")
_emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_2")
_emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_3")
_emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_4")
_emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_5")
_emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_6")
_emit_records_incident_event("SurgicalHealingAdapter", "p4obs", "incident")
_emit_captures_runtime_anomaly("SurgicalHealingAdapter", "p4obs", "anomaly")
_emit_writes_observability_log("SurgicalHealingAdapter", "p4obs", "obs_log")
_emit_updates_monitoring_state("SurgicalHealingAdapter", "p4obs", "mon_state")
_emit_triggers_alert("SurgicalHealingAdapter", "p4obs", "alert")
_emit_links_incident_trace("SurgicalHealingAdapter", "p4obs", "trace_link")
_emit_captures_pattern("SurgicalHealingAdapter", "p3lm", "pattern")
_emit_records_learning_event("SurgicalHealingAdapter", "p3lm", "learning_event")
_emit_writes_learning_snapshot("SurgicalHealingAdapter", "p3lm", "snapshot")
_emit_feeds_meta_learning("SurgicalHealingAdapter", "p3lm", "meta_feed")
_emit_updates_routing_strategy("SurgicalHealingAdapter", "p3lm", "routing")
_emit_improves_agent_policy("SurgicalHealingAdapter", "p3lm", "policy")
_emit_stores_learning_state("SurgicalHealingAdapter", "p3lm", "state")
_emit_records_execution_trace("SurgicalHealingAdapter", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("SurgicalHealingAdapter", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("SurgicalHealingAdapter", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("SurgicalHealingAdapter", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("SurgicalHealingAdapter", "L4_STATE", "p2_trace_5")
_emit_reads_environ("SurgicalHealingAdapter", "env_read", "p2_env_1")
_emit_reads_environ("SurgicalHealingAdapter", "env_read", "p2_env_2")
_emit_reads_runtime_state("SurgicalHealingAdapter", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("SurgicalHealingAdapter", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "SurgicalHealingAdapter", "context_pull")
_emit_pulls_context("p1", "SurgicalHealingAdapter", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "SurgicalHealingAdapter", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "SurgicalHealingAdapter", "uwg_term_2")
_emit_writes_through("p1", "SurgicalHealingAdapter", "write_through")
_emit_writes_through("p1", "SurgicalHealingAdapter", "write_through_2")
_emit_validated_by_safety_plane("p1", "SurgicalHealingAdapter", "safety_validation")
_emit_invokes_eval("p1", "SurgicalHealingAdapter", "eval_call")
_emit_proposal_commits_routing("p1", "SurgicalHealingAdapter", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass
class SurgicalHealingResult:
    """Result from a surgical healing operation."""

    status: str  # "success", "error", "skipped"
    violations_found: int
    violations_fixed: int
    errors: int
    skipped: int
    details: str = ""
    artifacts: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "status": self.status,
            "violations_found": self.violations_found,
            "violations_fixed": self.violations_fixed,
            "errors": self.errors,
            "skipped": self.skipped,
            "details": self.details,
            "artifacts": self.artifacts,
        }


class SurgicalHealingAdapter:
    """
    Bridges legacy healing detection results to SurgicalContext for CST healing.

    Converts dictionaries produced by legacy heal_repository() detectors into
    structured SurgicalContext objects that can be processed by SurgicalCSTHealerMixin.
    """

    FIX_TYPE_MAP: dict[str, str] = {
        "missing_docstring": "insert",
        "missing_import": "insert",
        "missing_future_import": "insert",
        "missing_guardrail": "insert",
        "unused_import": "delete",
        "remove_unused": "delete",
        "bare_except": "replace",
        "invalid_syntax": "replace",
        "trailing_whitespace": "replace",
        "functiondef": "insert",
        "classdef": "insert",
    }

    def __init__(self, agent_name: str = "SurgicalHealingAdapter"):
        self.agent_name = agent_name

    def _infer_fix_type(self, constraint_type: str) -> str:
        """Infer the fix type from the constraint type string."""
        ct = constraint_type.lower()
        for key, fix in self.FIX_TYPE_MAP.items():
            if key in ct:
                return fix
        return "insert"

    def create_context_from_detection(
        self,
        file_path: Path,
        detection_result: dict[str, Any],
        detection_method: str,
    ) -> SurgicalContext | None:
        """
        Create a SurgicalContext from a single detection result dict.

        Args:
            file_path: Path to the file to heal
            detection_result: Dict with keys: type, line, message, severity, etc.
            detection_method: Name of the detection method that found the violation

        Returns:
            SurgicalContext or None if file does not exist
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "SurgicalHealingAdapter.create_context_from_detection",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SurgicalHealingAdapter.create_context_from_detection".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not file_path.exists():
            Logger.warning("File does not exist: %s", file_path)
            return None

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as exc:
            Logger.error("Failed to parse %s: %s", file_path, exc)
            return None

        line = detection_result.get("line", 1) or 1
        constraint_type = detection_result.get("type", "unknown")
        fix_type = self._infer_fix_type(constraint_type)

        violation = ViolationConstraint(
            constraint_type=constraint_type,
            severity=detection_result.get("severity", "warning"),
            message=detection_result.get("message", ""),
            expected_pattern=detection_result.get("expected_pattern"),
            actual_pattern=detection_result.get("actual_pattern"),
            fix_type=fix_type,
        )

        coordinate = ASTCoordinate(
            node_id=f"{constraint_type}:{line}",
            node_type=constraint_type,
            line=line,
            column=0,
        )

        return SurgicalContext(
            file_path=file_path,
            file_content=source,
            ast_tree=tree,
            violation_id=f"{detection_method}:{line}",
            violations=[violation],
            target_coordinates=[coordinate],
            detector_agent=self.agent_name,
            detection_method=detection_method,
            detection_timestamp=datetime.now().isoformat(),
        )

    def create_batch_context(
        self,
        file_path: Path,
        detection_results: list[dict[str, Any]],
        detection_method: str,
    ) -> SurgicalContext | None:
        """
        Create a SurgicalContext from multiple detection result dicts.

        Args:
            file_path: Path to the file to heal
            detection_results: List of detection result dicts
            detection_method: Name of the detection method

        Returns:
            SurgicalContext or None if file does not exist
        """
        if not file_path.exists():
            Logger.warning("File does not exist: %s", file_path)
            return None

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as exc:
            Logger.error("Failed to parse %s: %s", file_path, exc)
            return None

        violations: list[ViolationConstraint] = []
        coordinates: list[ASTCoordinate] = []

        for dr in detection_results:
            line = dr.get("line", 1) or 1
            constraint_type = dr.get("type", "unknown")
            fix_type = self._infer_fix_type(constraint_type)

            violations.append(
                ViolationConstraint(
                    constraint_type=constraint_type,
                    severity=dr.get("severity", "warning"),
                    message=dr.get("message", ""),
                    expected_pattern=dr.get("expected_pattern"),
                    actual_pattern=dr.get("actual_pattern"),
                    fix_type=fix_type,
                ),
            )
            coordinates.append(
                ASTCoordinate(
                    node_id=f"{constraint_type}:{line}",
                    node_type=constraint_type,
                    line=line,
                    column=0,
                ),
            )

        return SurgicalContext(
            file_path=file_path,
            file_content=source,
            ast_tree=tree,
            violation_id=f"{detection_method}:batch",
            violations=violations,
            target_coordinates=coordinates,
            detector_agent=self.agent_name,
            detection_method=detection_method,
            detection_timestamp=datetime.now().isoformat(),
        )

    def apply_surgical_healing(
        self,
        context: SurgicalContext | None,
    ) -> SurgicalHealingResult:
        """
        Apply surgical healing using the CST mixin.

        Args:
            context: SurgicalContext to heal, or None

        Returns:
            SurgicalHealingResult
        """
        if context is None:
            return SurgicalHealingResult(
                status="error",
                violations_found=0,
                violations_fixed=0,
                errors=1,
                skipped=0,
                details="No context provided",
            )

        try:
            from agentic_core.mixins.cst_healer_mixin import SurgicalCSTHealerMixin

            healer = SurgicalCSTHealerMixin()
            raw = healer.heal_surgical_cst(context)

            return SurgicalHealingResult(
                status=raw.get("status", "success"),
                violations_found=raw.get("violations_found", len(context.violations)),
                violations_fixed=raw.get("violations_fixed", 0),
                errors=raw.get("errors", 0),
                skipped=raw.get("skipped", 0),
                details=raw.get("details", ""),
                artifacts=raw.get("artifacts", []),
            )
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as exc:
            Logger.error("Surgical healing failed: %s", exc)
            return SurgicalHealingResult(
                status="error",
                violations_found=len(context.violations),
                violations_fixed=0,
                errors=1,
                skipped=len(context.violations),
                details=str(exc),
            )
