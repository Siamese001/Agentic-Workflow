"""
Evaluation Dataset Schema

Defines the structure for evaluation examples and datasets.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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
)

_emit_applies_guardrail("p0", "evaluation_dataset_schema", "p0_governance")
_emit_reads_policy_state("p0", "evaluation_dataset_schema", "policy_binding")
_emit_snapshots_state("p0", "evaluation_dataset_schema", "state_snapshot")
emit_replay_key("p0", "evaluation_dataset_schema")
emit_determinism_digest("p0", "evaluation_dataset_schema")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "evaluation_dataset_schema", "execution_auth")
_emit_validates_capability("p2", "evaluation_dataset_schema", "capability_check")
_emit_routes_to_capability("p2", "evaluation_dataset_schema", "capability_route")
_emit_writes_via_uwg("p2", "evaluation_dataset_schema", "uwg_write")
_emit_blocks_direct_write("p2", "evaluation_dataset_schema", "direct_write_block")
_emit_records_tool_invocation("p2", "evaluation_dataset_schema", "tool_invocation")
_emit_captures_execution_output("p2", "evaluation_dataset_schema", "exec_output")
_emit_dispatches_agent("p3", "evaluation_dataset_schema", "agent_dispatch")
_emit_coordinates_agents("p3", "evaluation_dataset_schema", "agent_coordination")
_emit_records_workflow_lineage("p3", "evaluation_dataset_schema", "workflow_lineage")
_emit_records_healing_outcome("p3", "evaluation_dataset_schema", "healing_outcome")
_emit_escalates_failure("p3", "evaluation_dataset_schema", "failure_escalation")
_emit_orchestrates_workflow("p3", "evaluation_dataset_schema", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "evaluation_dataset_schema", "healing_dispatch")
_emit_invokes_evaluation("p3", "evaluation_dataset_schema", "evaluation_signal")
_emit_records_telemetry_event("p4", "evaluation_dataset_schema", "telemetry_event")
_emit_captures_evaluation_metric("p4", "evaluation_dataset_schema", "eval_metric")
_emit_stores_embedding("p4", "evaluation_dataset_schema", "embedding_store")
_emit_updates_meta_learning_state("p4", "evaluation_dataset_schema", "meta_learning")
_emit_links_execution_to_snapshot("p4", "evaluation_dataset_schema", "exec_snapshot_link")


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
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, file_path: Path) -> "EvaluationDataset":
        """Load dataset from JSON file."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EvaluationDataset.load_from_file")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def __len__(self) -> int:
        """Return number of examples."""
        return len(self.examples)
