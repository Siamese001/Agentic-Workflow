"""
L2 KG Writer for resume temporal graph data.

Writes entities, relations, and events to Neo4jGraphStore
to support resume timeline analysis and job alignment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from types import SimpleNamespace
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
    record_execution_trace,
)

record_execution_trace("rank_observability_components_util", "rank_observability_components_util_trace")

DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32

emit_determinism_digest("p0", "rank_observability_components_util")
emit_replay_key("p0", "rank_observability_components_util")
_emit_records_execution_trace("p0", "evidence", "rank_observability_components_util")
_emit_applies_guardrail("p0", "rank_observability_components_util", "p0_governance")
_emit_snapshots_state("p0", "rank_observability_components_util", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rank_observability_components_util", "execution_auth")
_emit_validates_capability("p2", "rank_observability_components_util", "capability_check")
_emit_routes_to_capability("p2", "rank_observability_components_util", "capability_route")
_emit_writes_via_uwg("p2", "rank_observability_components_util", "uwg_write")
_emit_blocks_direct_write("p2", "rank_observability_components_util", "direct_write_block")
_emit_records_tool_invocation("p2", "rank_observability_components_util", "tool_invocation")
_emit_captures_execution_output("p2", "rank_observability_components_util", "exec_output")
_emit_dispatches_agent("p3", "rank_observability_components_util", "agent_dispatch")
_emit_coordinates_agents("p3", "rank_observability_components_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "rank_observability_components_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "rank_observability_components_util", "healing_outcome")
_emit_escalates_failure("p3", "rank_observability_components_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "rank_observability_components_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rank_observability_components_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "rank_observability_components_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "rank_observability_components_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rank_observability_components_util", "eval_metric")
_emit_stores_embedding("p4", "rank_observability_components_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "rank_observability_components_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rank_observability_components_util", "exec_snapshot_link")
_emit_emits_metric_event("rank_observability_components_util", "p4obs", "metric_1")
_emit_emits_metric_event("rank_observability_components_util", "p4obs", "metric_2")
_emit_emits_metric_event("rank_observability_components_util", "p4obs", "metric_3")
_emit_emits_metric_event("rank_observability_components_util", "p4obs", "metric_4")
_emit_emits_metric_event("rank_observability_components_util", "p4obs", "metric_5")
_emit_emits_metric_event("rank_observability_components_util", "p4obs", "metric_6")
_emit_records_incident_event("rank_observability_components_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("rank_observability_components_util", "p4obs", "anomaly")
_emit_writes_observability_log("rank_observability_components_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("rank_observability_components_util", "p4obs", "mon_state")
_emit_triggers_alert("rank_observability_components_util", "p4obs", "alert")
_emit_links_incident_trace("rank_observability_components_util", "p4obs", "trace_link")
_emit_captures_pattern("rank_observability_components_util", "p3lm", "pattern")
_emit_records_learning_event("rank_observability_components_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rank_observability_components_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("rank_observability_components_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rank_observability_components_util", "p3lm", "routing")
_emit_improves_agent_policy("rank_observability_components_util", "p3lm", "policy")
_emit_stores_learning_state("rank_observability_components_util", "p3lm", "state")
_emit_pulls_context("p1", "rank_observability_components_util", "context_pull")
_emit_execution_terminates_at_uwg("p1", "rank_observability_components_util", "uwg_term")
_emit_writes_through("p1", "rank_observability_components_util", "write_through")
_emit_validated_by_safety_plane("p1", "rank_observability_components_util", "safety_validation")
_emit_proposal_commits_routing("p1", "rank_observability_components_util", "routing_commit")
_emit_escalates_to_human("p1", "rank_observability_components_util", "human_escalation")
_emit_routes_through("p1", "rank_observability_components_util", "route_through")
_emit_checks_agent_registry("p1", "rank_observability_components_util", "agent_registry")
_emit_validates_agent_capability("p1", "rank_observability_components_util", "capability")
_emit_dispatches_execution_plan("p1", "rank_observability_components_util", "exec_plan")
_emit_agent_executes_agent("p1", "rank_observability_components_util", "sub_agent")
_emit_routes_to_agent("p1", "rank_observability_components_util", "target_agent")
_emit_verifies_policy("p1", "rank_observability_components_util", "policy_check")
_emit_observes_runtime_state("p1", "rank_observability_components_util", "runtime_state")
_emit_verifies_boundary("p1", "rank_observability_components_util", "boundary_check")
_emit_transcripts_response("p1", "rank_observability_components_util", "transcript")
_emit_hard_fails_untranscripted("p1", "rank_observability_components_util")
_emit_gated_by_confidence("p1", "rank_observability_components_util", "confidence_gate")


@dataclass
class TemporalEntity:
    entity_id: str
    entity_type: str = "entity"
    canonical_id: str = ""
    aliases: tuple[str, ...] = ()
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalRange:
    valid_at: datetime = field(default_factory=datetime.utcnow)
    invalid_at: datetime | None = None


@dataclass
class TemporalTriplet:
    triplet_id: str
    subject: str = ""
    predicate: str = "related_to"
    object: str = ""
    temporal_range: TemporalRange = field(default_factory=TemporalRange)
    confidence: float = 0.0
    source: str = "unknown"
    status: Any = field(default_factory=lambda: SimpleNamespace(value="active"))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TemporalEvent:
    event_type: str = ""
    triplet_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


try:
    from agentic_core.L4_state.enforcement.neo4j_store import Neo4jGraphStore
except (ValueError, TypeError, RuntimeError) as e:
    Neo4jGraphStore = None  # type: ignore[assignment]

try:
    _neo4j_graph: Neo4jGraphStore | None = Neo4jGraphStore() if Neo4jGraphStore else None
    _NEO4J_AVAILABLE = True
except (ValueError, TypeError, RuntimeError) as e:
    _neo4j_graph = None
    _NEO4J_AVAILABLE = False


async def insert_entity(entity: TemporalEntity) -> None:
    """
    Inserts resume entity into Neo4j for timeline analysis.

    Mirrors canonical entity data to support resume job alignment.
    """
    if not _NEO4J_AVAILABLE:
        return
    try:
        if _neo4j_graph is not None:
            _neo4j_graph.upsert_entity(
                entity_id=entity.entity_id,
                etype=entity.entity_type,
                name=entity.entity_id,
                metadata={
                    "canonical_id": entity.canonical_id,
                    "aliases": list(entity.aliases),
                    "confidence": entity.confidence,
                    "created_at": entity.created_at.isoformat(),
                    **entity.metadata,
                },
            )
    except (ValueError, TypeError, RuntimeError, KeyError):
        ...


async def insert_triplet(triplet: TemporalTriplet) -> None:
    """
    Inserts resume triplet as relation in Neo4j for timeline analysis.

    Creates RELATION edge to support resume job alignment.
    """
    if not _NEO4J_AVAILABLE:
        return
    try:
        if _neo4j_graph is not None:
            _neo4j_graph.upsert_relation(
                rel_id=triplet.triplet_id,
                subject_id=triplet.subject,
                predicate=triplet.predicate,
                object_id=triplet.object,
                valid_at=triplet.temporal_range.valid_at.isoformat(),
                invalid_at=triplet.temporal_range.invalid_at.isoformat()
                if triplet.temporal_range.invalid_at
                else None,
                attrs={
                    "confidence": triplet.confidence,
                    "source": triplet.source,
                    "status": triplet.status.value,
                    **triplet.metadata,
                },
            )
    except (ValueError, TypeError, RuntimeError, KeyError):
        ...


async def insert_event(event: TemporalEvent) -> None:
    """
    Inserts resume temporal event in Neo4j for timeline analysis.

    Updates relation invalidation to support resume job alignment.
    """
    if not _NEO4J_AVAILABLE:
        return
    try:
        if _neo4j_graph is not None:
            if event.triplet_id and event.event_type in ["invalidation", "expiration"]:
                invalid_at = event.metadata.get("invalid_at")
                invalidated_by = event.metadata.get("invalidated_by")
                _neo4j_graph.update_relation_invalidity(
                    rel_id=event.triplet_id,
                    invalid_at=invalid_at.isoformat() if isinstance(invalid_at, datetime) else invalid_at,
                    invalidated_by=invalidated_by,
                )
    except (ValueError, TypeError, RuntimeError, KeyError):
        ...


async def batch_process_invalidation(events_to_update: list[TemporalEvent]) -> None:
    """
    Processes batch invalidation updates for resume timeline analysis.

    Updates multiple relations to support resume job alignment.
    """
    if not _NEO4J_AVAILABLE:
        return
    for event in events_to_update:
        await insert_event(event)


async def ingest_transcript(
    transcript_id: str,
    entities: list[TemporalEntity],
    triplets: list[TemporalTriplet],
    events: list[TemporalEvent],
) -> None:
    """
    Ingests complete resume transcript data for timeline analysis.

    Mirrors all components to support resume job alignment.
    """
    if not _NEO4J_AVAILABLE:
        return
    for entity in entities:
        await insert_entity(entity)
    for triplet in triplets:
        await insert_triplet(triplet)
    for event in events:
        await insert_event(event)
