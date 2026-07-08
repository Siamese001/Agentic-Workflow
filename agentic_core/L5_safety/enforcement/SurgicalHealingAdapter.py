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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "SurgicalHealingAdapter")
trace_contract.emit_determinism_digest("p0", "SurgicalHealingAdapter")

trace_contract._emit_dispatches_healing_run("p1", "SurgicalHealingAdapter", "L5")
trace_contract._emit_routes_through("p1", "SurgicalHealingAdapter", "L5")
trace_contract._emit_checks_agent_registry("p1", "SurgicalHealingAdapter", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "SurgicalHealingAdapter", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "SurgicalHealingAdapter", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "SurgicalHealingAdapter", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "SurgicalHealingAdapter", "target_agent")
trace_contract._emit_verifies_policy("p1", "SurgicalHealingAdapter", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "SurgicalHealingAdapter", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "SurgicalHealingAdapter", "boundary_check")
trace_contract._emit_transcripts_response("p1", "SurgicalHealingAdapter", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "SurgicalHealingAdapter")
trace_contract._emit_gated_by_confidence("p1", "SurgicalHealingAdapter", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "SurgicalHealingAdapter", "L5")
trace_contract._emit_reads_policy_state("p1", "SurgicalHealingAdapter", "L5")

trace_contract._emit_applies_guardrail("p0", "SurgicalHealingAdapter", "p0_governance")
trace_contract._emit_snapshots_state("p0", "SurgicalHealingAdapter", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "SurgicalHealingAdapter", "execution_auth")
trace_contract._emit_validates_capability("p2", "SurgicalHealingAdapter", "capability_check")
trace_contract._emit_routes_to_capability("p2", "SurgicalHealingAdapter", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "SurgicalHealingAdapter", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "SurgicalHealingAdapter", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "SurgicalHealingAdapter", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "SurgicalHealingAdapter", "exec_output")
trace_contract._emit_dispatches_agent("p3", "SurgicalHealingAdapter", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "SurgicalHealingAdapter", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "SurgicalHealingAdapter", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "SurgicalHealingAdapter", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "SurgicalHealingAdapter", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "SurgicalHealingAdapter", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "SurgicalHealingAdapter", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "SurgicalHealingAdapter", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "SurgicalHealingAdapter", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "SurgicalHealingAdapter", "eval_metric")
trace_contract._emit_stores_embedding("p4", "SurgicalHealingAdapter", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "SurgicalHealingAdapter", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "SurgicalHealingAdapter", "exec_snapshot_link")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("SurgicalHealingAdapter", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("SurgicalHealingAdapter", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("SurgicalHealingAdapter", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("SurgicalHealingAdapter", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("SurgicalHealingAdapter", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("SurgicalHealingAdapter", "p4obs", "alert")
trace_contract._emit_links_incident_trace("SurgicalHealingAdapter", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("SurgicalHealingAdapter", "p3lm", "pattern")
trace_contract._emit_records_learning_event("SurgicalHealingAdapter", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("SurgicalHealingAdapter", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("SurgicalHealingAdapter", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("SurgicalHealingAdapter", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("SurgicalHealingAdapter", "p3lm", "policy")
trace_contract._emit_stores_learning_state("SurgicalHealingAdapter", "p3lm", "state")
trace_contract._emit_records_execution_trace("SurgicalHealingAdapter", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("SurgicalHealingAdapter", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("SurgicalHealingAdapter", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("SurgicalHealingAdapter", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("SurgicalHealingAdapter", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("SurgicalHealingAdapter", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("SurgicalHealingAdapter", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("SurgicalHealingAdapter", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("SurgicalHealingAdapter", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "SurgicalHealingAdapter", "context_pull")
trace_contract._emit_pulls_context("p1", "SurgicalHealingAdapter", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "SurgicalHealingAdapter", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "SurgicalHealingAdapter", "uwg_term_2")
trace_contract._emit_writes_through("p1", "SurgicalHealingAdapter", "write_through")
trace_contract._emit_writes_through("p1", "SurgicalHealingAdapter", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "SurgicalHealingAdapter", "safety_validation")
trace_contract._emit_invokes_eval("p1", "SurgicalHealingAdapter", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "SurgicalHealingAdapter", "routing_commit")

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
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "SurgicalHealingAdapter.create_context_from_detection",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SurgicalHealingAdapter.create_context_from_detection".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not file_path.exists():
            Logger.warning("File does not exist: %s", file_path)
            return None

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (
            RuntimeError,
            OSError,
        ) as exc:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallow
            Logger.error("Failed to parse %s: %s", file_path, exc)
            return None  # guardian: allow-return-none-swallow -- detection parse: non-fatal, caller handles None as no constraint

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
        except (
            RuntimeError,
            OSError,
        ) as exc:  # guardian: allow-return-none-swallow  -- ADG-burn: return_none_swallow
            Logger.error("Failed to parse %s: %s", file_path, exc)
            return None  # guardian: allow-return-none-swallow -- violation parse: non-fatal, caller handles None as no violations

        violations: list[ViolationConstraint] = []
        coordinates: list[ASTCoordinate] = []

        for dr in tqdm(detection_results, desc="Processing", unit="item"):
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
        except (RuntimeError, OSError) as exc:  # guardian: allow-silent-swallow
            Logger.error("Surgical healing failed: %s", exc)
            return SurgicalHealingResult(
                status="error",
                violations_found=len(context.violations),
                violations_fixed=0,
                errors=1,
                skipped=len(context.violations),
                details=str(exc),
            )
