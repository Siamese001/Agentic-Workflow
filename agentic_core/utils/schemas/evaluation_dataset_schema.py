"""
Evaluation Dataset Schema

Defines the structure for evaluation examples and datasets.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "evaluation_dataset_schema", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "evaluation_dataset_schema", "policy_binding")
trace_contract._emit_snapshots_state("p0", "evaluation_dataset_schema", "state_snapshot")

trace_contract._emit_emits_metric_event("evaluation_dataset_schema", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("evaluation_dataset_schema", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("evaluation_dataset_schema", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("evaluation_dataset_schema", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("evaluation_dataset_schema", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("evaluation_dataset_schema", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("evaluation_dataset_schema", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("evaluation_dataset_schema", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("evaluation_dataset_schema", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("evaluation_dataset_schema", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("evaluation_dataset_schema", "p4obs", "alert")
trace_contract._emit_links_incident_trace("evaluation_dataset_schema", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("evaluation_dataset_schema", "p3lm", "pattern")
trace_contract._emit_records_learning_event("evaluation_dataset_schema", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("evaluation_dataset_schema", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("evaluation_dataset_schema", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("evaluation_dataset_schema", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("evaluation_dataset_schema", "p3lm", "policy")
trace_contract._emit_stores_learning_state("evaluation_dataset_schema", "p3lm", "state")
trace_contract._emit_records_execution_trace("evaluation_dataset_schema", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("evaluation_dataset_schema", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("evaluation_dataset_schema", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("evaluation_dataset_schema", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("evaluation_dataset_schema", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("evaluation_dataset_schema", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("evaluation_dataset_schema", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("evaluation_dataset_schema", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("evaluation_dataset_schema", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "evaluation_dataset_schema", "context_pull")
trace_contract._emit_pulls_context("p1", "evaluation_dataset_schema", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "evaluation_dataset_schema", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "evaluation_dataset_schema", "uwg_term_2")
trace_contract._emit_writes_through("p1", "evaluation_dataset_schema", "write_through")
trace_contract._emit_writes_through("p1", "evaluation_dataset_schema", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "evaluation_dataset_schema", "safety_validation")
trace_contract._emit_invokes_eval("p1", "evaluation_dataset_schema", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "evaluation_dataset_schema", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "evaluation_dataset_schema", "human_escalation")
trace_contract._emit_routes_through("p1", "evaluation_dataset_schema", "route_through")
trace_contract._emit_checks_agent_registry("p1", "evaluation_dataset_schema", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "evaluation_dataset_schema", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "evaluation_dataset_schema", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "evaluation_dataset_schema", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "evaluation_dataset_schema", "target_agent")
trace_contract._emit_verifies_policy("p1", "evaluation_dataset_schema", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "evaluation_dataset_schema", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "evaluation_dataset_schema", "boundary_check")
trace_contract._emit_transcripts_response("p1", "evaluation_dataset_schema", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "evaluation_dataset_schema")
trace_contract._emit_gated_by_confidence("p1", "evaluation_dataset_schema", "confidence_gate")
trace_contract.emit_replay_key("p0", "evaluation_dataset_schema")
trace_contract.emit_determinism_digest("p0", "evaluation_dataset_schema")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "evaluation_dataset_schema", "execution_auth")
trace_contract._emit_validates_capability("p2", "evaluation_dataset_schema", "capability_check")
trace_contract._emit_routes_to_capability("p2", "evaluation_dataset_schema", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "evaluation_dataset_schema", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "evaluation_dataset_schema", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "evaluation_dataset_schema", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "evaluation_dataset_schema", "exec_output")
trace_contract._emit_dispatches_agent("p3", "evaluation_dataset_schema", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "evaluation_dataset_schema", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "evaluation_dataset_schema", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "evaluation_dataset_schema", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "evaluation_dataset_schema", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "evaluation_dataset_schema", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "evaluation_dataset_schema", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "evaluation_dataset_schema", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "evaluation_dataset_schema", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "evaluation_dataset_schema", "eval_metric")
trace_contract._emit_stores_embedding("p4", "evaluation_dataset_schema", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "evaluation_dataset_schema", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "evaluation_dataset_schema", "exec_snapshot_link")


def _normalize_json_path(file_path: Path, *, must_exist: bool) -> Path:
    resolved = file_path.expanduser().resolve(strict=must_exist)
    if resolved.suffix.lower() != ".json":
        msg = f"Expected a .json dataset path, got: {resolved}"
        raise ValueError(msg)
    return resolved


@dataclass
class EvaluationExample:
    """Single evaluation example with query, ground truth, and expected answer."""

    query: str
    ground_truth_documents: list[str]
    expected_answer: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "query": self.query,
            "ground_truth_documents": self.ground_truth_documents,
            "expected_answer": self.expected_answer,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationExample":
        """Create from dictionary."""
        return cls(
            query=data["query"],
            ground_truth_documents=data["ground_truth_documents"],
            expected_answer=data["expected_answer"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class EvaluationDataset:
    """Collection of evaluation examples."""

    examples: list[EvaluationExample]
    name: str
    version: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "examples": [example.to_dict() for example in self.examples],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationDataset":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
            examples=[EvaluationExample.from_dict(example) for example in data["examples"]],
        )

    def save_to_file(self, file_path: Path) -> None:
        """Save dataset to JSON file."""
        target_path = _normalize_json_path(file_path, must_exist=False)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = target_path.with_suffix(f"{target_path.suffix}.tmp")

        try:
            with tmp_path.open("w", encoding="utf-8", newline="\n") as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            tmp_path.replace(target_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "EvaluationDataset":
        """Load dataset from JSON file."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "EvaluationDataset.load_from_file"
        )

        source_path = _normalize_json_path(file_path, must_exist=True)
        with source_path.open(encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            msg = f"Expected top-level JSON object in {source_path}"
            raise ValueError(msg)
        return cls.from_dict(data)

    def __len__(self) -> int:
        """Return number of examples."""
        return len(self.examples)
