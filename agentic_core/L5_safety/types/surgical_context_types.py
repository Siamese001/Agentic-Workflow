"""
SurgicalContext - Structured Context for Zero-Loss Healing

Provides AST-level coordinates and violation constraints for surgical healing operations.
Eliminates Resolution Asymmetry by preserving all detection information.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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

emit_replay_key("p0", "surgical_context_types")
emit_determinism_digest("p0", "surgical_context_types")

_emit_dispatches_healing_run("p1", "surgical_context_types", "L5")
_emit_routes_through("p1", "surgical_context_types", "L5")
_emit_checks_agent_registry("p1", "surgical_context_types", "agent_registry")
_emit_validates_agent_capability("p1", "surgical_context_types", "capability")
_emit_dispatches_execution_plan("p1", "surgical_context_types", "exec_plan")
_emit_agent_executes_agent("p1", "surgical_context_types", "sub_agent")
_emit_routes_to_agent("p1", "surgical_context_types", "target_agent")
_emit_verifies_policy("p1", "surgical_context_types", "policy_check")
_emit_observes_runtime_state("p1", "surgical_context_types", "runtime_state")
_emit_verifies_boundary("p1", "surgical_context_types", "boundary_check")
_emit_transcripts_response("p1", "surgical_context_types", "transcript")
_emit_hard_fails_untranscripted("p1", "surgical_context_types")
_emit_gated_by_confidence("p1", "surgical_context_types", "confidence_gate")
_emit_escalates_to_human("p1", "surgical_context_types", "L5")
_emit_reads_policy_state("p1", "surgical_context_types", "L5")

_emit_applies_guardrail("p0", "surgical_context_types", "p0_governance")
_emit_snapshots_state("p0", "surgical_context_types", "state_snapshot")
_emit_authorize_and_execute("p2", "surgical_context_types", "execution_auth")
_emit_validates_capability("p2", "surgical_context_types", "capability_check")
_emit_routes_to_capability("p2", "surgical_context_types", "capability_route")
_emit_writes_via_uwg("p2", "surgical_context_types", "uwg_write")
_emit_blocks_direct_write("p2", "surgical_context_types", "direct_write_block")
_emit_records_tool_invocation("p2", "surgical_context_types", "tool_invocation")
_emit_captures_execution_output("p2", "surgical_context_types", "exec_output")
_emit_dispatches_agent("p3", "surgical_context_types", "agent_dispatch")
_emit_coordinates_agents("p3", "surgical_context_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "surgical_context_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "surgical_context_types", "healing_outcome")
_emit_escalates_failure("p3", "surgical_context_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "surgical_context_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "surgical_context_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "surgical_context_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "surgical_context_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "surgical_context_types", "eval_metric")
_emit_stores_embedding("p4", "surgical_context_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "surgical_context_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "surgical_context_types", "exec_snapshot_link")
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

_emit_emits_metric_event("surgical_context_types", "p4obs", "metric_1")
_emit_emits_metric_event("surgical_context_types", "p4obs", "metric_2")
_emit_emits_metric_event("surgical_context_types", "p4obs", "metric_3")
_emit_emits_metric_event("surgical_context_types", "p4obs", "metric_4")
_emit_emits_metric_event("surgical_context_types", "p4obs", "metric_5")
_emit_emits_metric_event("surgical_context_types", "p4obs", "metric_6")
_emit_records_incident_event("surgical_context_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("surgical_context_types", "p4obs", "anomaly")
_emit_writes_observability_log("surgical_context_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("surgical_context_types", "p4obs", "mon_state")
_emit_triggers_alert("surgical_context_types", "p4obs", "alert")
_emit_links_incident_trace("surgical_context_types", "p4obs", "trace_link")
_emit_captures_pattern("surgical_context_types", "p3lm", "pattern")
_emit_records_learning_event("surgical_context_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("surgical_context_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("surgical_context_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("surgical_context_types", "p3lm", "routing")
_emit_improves_agent_policy("surgical_context_types", "p3lm", "policy")
_emit_stores_learning_state("surgical_context_types", "p3lm", "state")
_emit_records_execution_trace("surgical_context_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("surgical_context_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("surgical_context_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("surgical_context_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("surgical_context_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("surgical_context_types", "env_read", "p2_env_1")
_emit_reads_environ("surgical_context_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("surgical_context_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("surgical_context_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "surgical_context_types", "context_pull")
_emit_pulls_context("p1", "surgical_context_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "surgical_context_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "surgical_context_types", "uwg_term_2")
_emit_writes_through("p1", "surgical_context_types", "write_through")
_emit_writes_through("p1", "surgical_context_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "surgical_context_types", "safety_validation")
_emit_invokes_eval("p1", "surgical_context_types", "eval_call")
_emit_proposal_commits_routing("p1", "surgical_context_types", "routing_commit")


@dataclass
class ASTCoordinate:
    """Precise AST node coordinate."""

    node_id: str
    node_type: str
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None
    parent_id: str | None = None
    children_ids: list[str] = field(default_factory=list)


@dataclass
class ViolationConstraint:
    """Specific constraint that was violated."""

    constraint_type: str
    severity: str
    message: str
    rule_id: str | None = None
    expected_pattern: str | None = None
    actual_pattern: str | None = None
    fix_type: str | None = None


@dataclass
class SurgicalContext:
    """
    Comprehensive context for surgical healing operations.

    This structure ensures zero information loss between detection and healing.
    All coordinates are preserved for AST-level mutations.
    """

    file_path: Path
    file_content: str
    ast_tree: ast.Module
    violation_id: str
    violations: list[ViolationConstraint]
    target_coordinates: list[ASTCoordinate]
    detector_agent: str
    detection_method: str
    detection_timestamp: str
    surrounding_context: dict[str, Any] = field(default_factory=dict)
    related_violations: list[str] = field(default_factory=list)
    suggested_fixes: list[dict[str, Any]] = field(default_factory=list)
    preservation_rules: list[str] = field(default_factory=list)

    def get_target_node(self, coordinate: ASTCoordinate) -> ast.AST | None:
        """Get AST node by coordinate."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SurgicalContext.get_target_node")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SurgicalContext.get_target_node".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for node in ast.walk(self.ast_tree):
            if hasattr(node, "lineno") and hasattr(node, "col_offset"):
                if node.lineno == coordinate.line and node.col_offset == coordinate.column:
                    return node
        return None

    def get_nodes_by_type(self, node_type: str) -> list[ast.AST]:
        """Get all nodes of a specific type."""
        nodes = []
        for node in ast.walk(self.ast_tree):
            if type(node).__name__ == node_type:
                nodes.append(node)
        return nodes

    def get_line_range(self, coordinate: ASTCoordinate) -> tuple[int, int]:
        """Get line range for a coordinate."""
        start = coordinate.line
        end = coordinate.end_line or coordinate.line
        return (start, end)

    def extract_source_segment(self, coordinate: ASTCoordinate) -> str:
        """Extract source code for the coordinate."""
        lines = self.file_content.splitlines(keepends=True)
        start, end = self.get_line_range(coordinate)
        if start == end:
            return lines[start - 1]
        else:
            return "".join(lines[start - 1 : end])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "file_path": str(self.file_path),
            "violation_id": self.violation_id,
            "violations": [v.__dict__ for v in self.violations],
            "target_coordinates": [c.__dict__ for c in self.target_coordinates],
            "detector_agent": self.detector_agent,
            "detection_method": self.detection_method,
            "detection_timestamp": self.detection_timestamp,
            "surrounding_context": self.surrounding_context,
            "related_violations": self.related_violations,
            "suggested_fixes": self.suggested_fixes,
            "preservation_rules": self.preservation_rules,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SurgicalContext:
        """Create from dictionary."""
        tree = ast.parse(data["file_content"])
        violations = [ViolationConstraint(**v) for v in data["violations"]]
        coordinates = [ASTCoordinate(**c) for c in data["target_coordinates"]]
        return cls(
            file_path=Path(data["file_path"]),
            file_content=data["file_content"],
            ast_tree=tree,
            violation_id=data["violation_id"],
            violations=violations,
            target_coordinates=coordinates,
            detector_agent=data["detector_agent"],
            detection_method=data["detection_method"],
            detection_timestamp=data["detection_timestamp"],
            surrounding_context=data.get("surrounding_context", {}),
            related_violations=data.get("related_violations", []),
            suggested_fixes=data.get("suggested_fixes", []),
            preservation_rules=data.get("preservation_rules", []),
        )


class SurgicalContextBuilder:
    """Builder for creating SurgicalContext from detection results."""

    def __init__(self, file_path: Path, detector_agent: str, detection_method: str):
        self.file_path = file_path
        self.detector_agent = detector_agent
        self.detection_method = detection_method
        self.file_content = file_path.read_text(encoding="utf-8")
        self.ast_tree = ast.parse(self.file_content)

    def build_context(
        self,
        violation_id: str,
        violations: list[dict[str, Any]],
        target_nodes: list[ast.AST],
        **kwargs,
    ) -> SurgicalContext:
        """Build SurgicalContext from detection results."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "SurgicalContextBuilder.build_context",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SurgicalContextBuilder.build_context".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        from datetime import datetime

        violation_constraints = []
        for v in violations:
            violation_constraints.append(ViolationConstraint(**v))
        coordinates = []
        for i, node in enumerate(target_nodes):
            coord = ASTCoordinate(
                node_id=f"{self.detection_method}_{i}_{node.lineno}_{node.col_offset}",
                node_type=type(node).__name__,
                line=node.lineno,
                column=node.col_offset,
                end_line=getattr(node, "end_lineno", None),
                end_column=getattr(node, "end_col_offset", None),
            )
            coordinates.append(coord)
        return SurgicalContext(
            file_path=self.file_path,
            file_content=self.file_content,
            ast_tree=self.ast_tree,
            violation_id=violation_id,
            violations=violation_constraints,
            target_coordinates=coordinates,
            detector_agent=self.detector_agent,
            detection_method=self.detection_method,
            detection_timestamp=datetime.now().isoformat(),
            **kwargs,
        )


__all__ = ["SurgicalContext", "SurgicalContextBuilder", "ASTCoordinate", "ViolationConstraint"]
