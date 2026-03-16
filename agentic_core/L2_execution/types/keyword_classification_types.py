from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "keyword_classification_types")
emit_determinism_digest("p0", "keyword_classification_types")

_emit_dispatches_healing_run("p1", "keyword_classification_types", "L2")
_emit_routes_through("p1", "keyword_classification_types", "L2")
_emit_escalates_to_human("p1", "keyword_classification_types", "L2")
_emit_reads_policy_state("p1", "keyword_classification_types", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "keyword_classification_types")
_emit_applies_guardrail("p0", "keyword_classification_types", "p0_governance")
_emit_snapshots_state("p0", "keyword_classification_types", "state_snapshot")
_emit_authorize_and_execute("p2", "keyword_classification_types", "execution_auth")
_emit_validates_capability("p2", "keyword_classification_types", "capability_check")
_emit_routes_to_capability("p2", "keyword_classification_types", "capability_route")
_emit_writes_via_uwg("p2", "keyword_classification_types", "uwg_write")
_emit_blocks_direct_write("p2", "keyword_classification_types", "direct_write_block")
_emit_records_tool_invocation("p2", "keyword_classification_types", "tool_invocation")
_emit_captures_execution_output("p2", "keyword_classification_types", "exec_output")
_emit_dispatches_agent("p3", "keyword_classification_types", "agent_dispatch")
_emit_coordinates_agents("p3", "keyword_classification_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "keyword_classification_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "keyword_classification_types", "healing_outcome")
_emit_escalates_failure("p3", "keyword_classification_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "keyword_classification_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "keyword_classification_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "keyword_classification_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "keyword_classification_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "keyword_classification_types", "eval_metric")
_emit_stores_embedding("p4", "keyword_classification_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "keyword_classification_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "keyword_classification_types", "exec_snapshot_link")

"Types and models for PeerIntelligenceAuditorAgent."
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import ValidationError as ValidationResult

Logger: Any = logging.getLogger(__name__)


class KeywordClassification(Enum):
    """TODO: Add docstring."""

    TABLE_STAKES: Any = "TABLE_STAKES"
    DIFFERENTIATOR: Any = "DIFFERENTIATOR"
    UNKNOWN: Any = "UNKNOWN"


@dataclass
class RagHop:
    """Docstring."""

    hop_number: int
    search_queries: list[str]
    results: list[dict[str, Any]]
    keywords_found: set[str]


@dataclass
class KeywordAnalysis:
    """Docstring."""

    keyword: str
    classification: KeywordClassification
    frequency_score: float
    competitive_density: float
    reasoning: str


@dataclass
class PeerIntelligenceConfig:
    """Docstring."""

    total_searches: int = 24
    total_hops: int = 3
    searches_per_hop: int = 8
    differentiator_threshold: float = 0.3


@dataclass
class PeerIntelligenceResult:
    """Docstring."""

    hops: list[RAGHop]
    keyword_analyses: list[KeywordAnalysis]
    table_stakes: list[str]
    differentiators: list[str]
    validation_results: list[ValidationResult]
    success: bool
    total_searches_executed: int
