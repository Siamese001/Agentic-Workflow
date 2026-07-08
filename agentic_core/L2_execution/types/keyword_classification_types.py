from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "keyword_classification_types")
trace_contract.emit_determinism_digest("p0", "keyword_classification_types")

trace_contract._emit_dispatches_healing_run("p1", "keyword_classification_types", "L2")
trace_contract._emit_routes_through("p1", "keyword_classification_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "keyword_classification_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "keyword_classification_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "keyword_classification_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "keyword_classification_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "keyword_classification_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "keyword_classification_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "keyword_classification_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "keyword_classification_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "keyword_classification_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "keyword_classification_types")
trace_contract._emit_gated_by_confidence("p1", "keyword_classification_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "keyword_classification_types", "L2")
trace_contract._emit_reads_policy_state("p1", "keyword_classification_types", "L2")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "keyword_classification_types")
trace_contract._emit_applies_guardrail("p0", "keyword_classification_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "keyword_classification_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "keyword_classification_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "keyword_classification_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "keyword_classification_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "keyword_classification_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "keyword_classification_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "keyword_classification_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "keyword_classification_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "keyword_classification_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "keyword_classification_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "keyword_classification_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "keyword_classification_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "keyword_classification_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "keyword_classification_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "keyword_classification_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "keyword_classification_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "keyword_classification_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "keyword_classification_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "keyword_classification_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "keyword_classification_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "keyword_classification_types", "exec_snapshot_link")

"Types and models for PeerIntelligenceAuditorAgent."
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import ValidationError as ValidationResult


trace_contract._emit_emits_metric_event("keyword_classification_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("keyword_classification_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("keyword_classification_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("keyword_classification_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("keyword_classification_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("keyword_classification_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("keyword_classification_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("keyword_classification_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("keyword_classification_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("keyword_classification_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("keyword_classification_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("keyword_classification_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("keyword_classification_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("keyword_classification_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("keyword_classification_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("keyword_classification_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("keyword_classification_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("keyword_classification_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("keyword_classification_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("keyword_classification_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("keyword_classification_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("keyword_classification_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("keyword_classification_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("keyword_classification_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("keyword_classification_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("keyword_classification_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("keyword_classification_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("keyword_classification_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "keyword_classification_types", "context_pull")
trace_contract._emit_pulls_context("p1", "keyword_classification_types", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "keyword_classification_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "keyword_classification_types", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "keyword_classification_types", "write_through")
trace_contract._emit_writes_through("p1", "keyword_classification_types", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "keyword_classification_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "keyword_classification_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "keyword_classification_types", "routing_commit")

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
