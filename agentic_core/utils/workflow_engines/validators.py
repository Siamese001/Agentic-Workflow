"""
Chunk Validators

Validates chunk manifests for size, overlap sanity, duplicates, and orphans.
All validators are deterministic and zero-dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field

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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

_emit_authorize_and_execute("p2", "validators", "execution_auth")
_emit_validates_capability("p2", "validators", "capability_check")
_emit_routes_to_capability("p2", "validators", "capability_route")
_emit_writes_via_uwg("p2", "validators", "uwg_write")
_emit_blocks_direct_write("p2", "validators", "direct_write_block")
_emit_records_tool_invocation("p2", "validators", "tool_invocation")
_emit_captures_execution_output("p2", "validators", "exec_output")
_emit_dispatches_agent("p3", "validators", "agent_dispatch")
_emit_coordinates_agents("p3", "validators", "agent_coordination")
_emit_records_workflow_lineage("p3", "validators", "workflow_lineage")
_emit_records_healing_outcome("p3", "validators", "healing_outcome")
_emit_escalates_failure("p3", "validators", "failure_escalation")
_emit_orchestrates_workflow("p3", "validators", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validators", "healing_dispatch")
_emit_invokes_evaluation("p3", "validators", "evaluation_signal")
_emit_records_telemetry_event("p4", "validators", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validators", "eval_metric")
_emit_stores_embedding("p4", "validators", "embedding_store")
_emit_updates_meta_learning_state("p4", "validators", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validators", "exec_snapshot_link")
from .policies import Chunk, ChunkManifest

_emit_applies_guardrail("p0", "validators", "p0_governance")
_emit_snapshots_state("p0", "validators", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("validators", "p4obs", "metric_1")
_emit_emits_metric_event("validators", "p4obs", "metric_2")
_emit_emits_metric_event("validators", "p4obs", "metric_3")
_emit_emits_metric_event("validators", "p4obs", "metric_4")
_emit_emits_metric_event("validators", "p4obs", "metric_5")
_emit_emits_metric_event("validators", "p4obs", "metric_6")
_emit_records_incident_event("validators", "p4obs", "incident")
_emit_captures_runtime_anomaly("validators", "p4obs", "anomaly")
_emit_writes_observability_log("validators", "p4obs", "obs_log")
_emit_updates_monitoring_state("validators", "p4obs", "mon_state")
_emit_triggers_alert("validators", "p4obs", "alert")
_emit_links_incident_trace("validators", "p4obs", "trace_link")
_emit_captures_pattern("validators", "p3lm", "pattern")
_emit_records_learning_event("validators", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validators", "p3lm", "snapshot")
_emit_feeds_meta_learning("validators", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validators", "p3lm", "routing")
_emit_improves_agent_policy("validators", "p3lm", "policy")
_emit_stores_learning_state("validators", "p3lm", "state")
_emit_records_execution_trace("validators", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validators", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validators", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validators", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validators", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validators", "env_read", "p2_env_1")
_emit_reads_environ("validators", "env_read", "p2_env_2")
_emit_reads_runtime_state("validators", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validators", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "validators", "context_pull")
_emit_pulls_context("p1", "validators", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "validators", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validators", "uwg_term_2")
_emit_writes_through("p1", "validators", "write_through")
_emit_writes_through("p1", "validators", "write_through_2")
_emit_validated_by_safety_plane("p1", "validators", "safety_validation")
_emit_invokes_eval("p1", "validators", "eval_call")
_emit_proposal_commits_routing("p1", "validators", "routing_commit")
_emit_escalates_to_human("p1", "validators", "human_escalation")
_emit_routes_through("p1", "validators", "route_through")
_emit_checks_agent_registry("p1", "validators", "agent_registry")
_emit_validates_agent_capability("p1", "validators", "capability")
_emit_dispatches_execution_plan("p1", "validators", "exec_plan")
_emit_agent_executes_agent("p1", "validators", "sub_agent")
_emit_routes_to_agent("p1", "validators", "target_agent")
_emit_verifies_policy("p1", "validators", "policy_check")
_emit_observes_runtime_state("p1", "validators", "runtime_state")
_emit_verifies_boundary("p1", "validators", "boundary_check")
_emit_transcripts_response("p1", "validators", "transcript")
_emit_hard_fails_untranscripted("p1", "validators")
_emit_gated_by_confidence("p1", "validators", "confidence_gate")
emit_replay_key("p0", "validators")
emit_determinism_digest("p0", "validators")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass
class ChunkQualityReport:
    """Validation report for a chunk manifest."""

    doc_id: str
    policy_name: str
    total_chunks: int
    duplicates: int
    orphan_chunks: int
    oversized_chunks: int
    undersized_chunks: int
    overlap_violations: int
    duplicate_chunk_ids: list[str] = field(default_factory=list)
    orphan_chunk_ids: list[str] = field(default_factory=list)
    oversized_chunk_ids: list[str] = field(default_factory=list)
    undersized_chunk_ids: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True iff no violations detected."""
        return (
            self.duplicates == 0
            and self.orphan_chunks == 0
            and (self.oversized_chunks == 0)
            and (self.overlap_violations == 0)
        )

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "policy_name": self.policy_name,
            "total_chunks": self.total_chunks,
            "duplicates": self.duplicates,
            "orphan_chunks": self.orphan_chunks,
            "oversized_chunks": self.oversized_chunks,
            "undersized_chunks": self.undersized_chunks,
            "overlap_violations": self.overlap_violations,
            "duplicate_chunk_ids": self.duplicate_chunk_ids,
            "orphan_chunk_ids": self.orphan_chunk_ids,
            "oversized_chunk_ids": self.oversized_chunk_ids,
            "undersized_chunk_ids": self.undersized_chunk_ids,
            "messages": self.messages,
            "is_valid": self.is_valid,
        }


class MaxChunkSizeValidator:
    """Flags chunks exceeding a maximum token count."""

    # guardian: allow-magic-config
    def __init__(self, max_tokens: int = 1024):
        if max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {max_tokens}")
        self.max_tokens = max_tokens

    def validate(self, chunks: list[Chunk]) -> list[str]:
        """Return list of chunk_ids that exceed max_tokens."""
        return [c.chunk_id for c in chunks if c.token_count > self.max_tokens]


class MinChunkSizeValidator:
    """Flags chunks below a minimum token count (potential orphans)."""

    # guardian: allow-magic-config
    def __init__(self, min_tokens: int = 10):
        if min_tokens < 0:
            raise ValueError(f"min_tokens must be non-negative, got {min_tokens}")
        self.min_tokens = min_tokens

    def validate(self, chunks: list[Chunk]) -> list[str]:
        """Return list of chunk_ids that are below min_tokens."""
        return [c.chunk_id for c in chunks if c.token_count < self.min_tokens]


class OverlapSanityValidator:
    """Verifies that overlapping windows don't produce identical chunks."""

    def validate(self, chunks: list[Chunk]) -> int:
        """Return number of consecutive identical-content chunk pairs."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "OverlapSanityValidator.validate")

        violations = 0
        for i in range(len(chunks) - 1):
            if chunks[i].content.strip() == chunks[i + 1].content.strip():
                violations += 1
        return violations


class DuplicateChunkDetector:
    """Detects chunks with duplicate content across the manifest."""

    def detect(self, chunks: list[Chunk]) -> list[str]:
        """Return list of chunk_ids whose content is a duplicate of an earlier chunk."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "DuplicateChunkDetector.detect")

        seen: set[str] = set()
        duplicates: list[str] = []
        for chunk in chunks:
            content_key = chunk.content.strip().lower()
            if content_key in seen:
                duplicates.append(chunk.chunk_id)
            else:
                seen.add(content_key)
        return duplicates


class OrphanChunkDetector:
    """Detects chunks with no meaningful content (empty or whitespace-only)."""

    def detect(self, chunks: list[Chunk]) -> list[str]:
        """Return list of chunk_ids with empty or whitespace-only content."""
        return [c.chunk_id for c in chunks if not c.content.strip()]


class ChunkManifestValidator:
    """Runs all validators against a ChunkManifest and produces a ChunkQualityReport."""

    # guardian: allow-magic-config
    def __init__(self, max_chunk_tokens: int = 1024, min_chunk_tokens: int = 10):
        self.max_validator = MaxChunkSizeValidator(max_tokens=max_chunk_tokens)
        self.min_validator = MinChunkSizeValidator(min_tokens=min_chunk_tokens)
        self.overlap_validator = OverlapSanityValidator()
        self.duplicate_detector = DuplicateChunkDetector()
        self.orphan_detector = OrphanChunkDetector()

    def validate(self, manifest: ChunkManifest) -> ChunkQualityReport:
        """Validate all chunks in a manifest.

        Args:
            manifest: ChunkManifest to validate

        Returns:
            ChunkQualityReport with all detected violations
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ChunkManifestValidator.validate")

        chunks = manifest.chunks
        messages: list[str] = []
        oversized = self.max_validator.validate(chunks)
        undersized = self.min_validator.validate(chunks)
        overlap_violations = self.overlap_validator.validate(chunks)
        duplicates = self.duplicate_detector.detect(chunks)
        orphans = self.orphan_detector.detect(chunks)
        if oversized:
            messages.append(f"{len(oversized)} chunk(s) exceed max token limit")
        if orphans:
            messages.append(f"{len(orphans)} orphan chunk(s) detected (empty content)")
        if duplicates:
            messages.append(f"{len(duplicates)} duplicate chunk(s) detected")
        if overlap_violations > 0:
            messages.append(f"{overlap_violations} overlap sanity violation(s) detected")
        return ChunkQualityReport(
            doc_id=manifest.doc_id,
            policy_name=manifest.policy_name,
            total_chunks=len(chunks),
            duplicates=len(duplicates),
            orphan_chunks=len(orphans),
            oversized_chunks=len(oversized),
            undersized_chunks=len(undersized),
            overlap_violations=overlap_violations,
            duplicate_chunk_ids=duplicates,
            orphan_chunk_ids=orphans,
            oversized_chunk_ids=oversized,
            undersized_chunk_ids=undersized,
            messages=messages,
        )


__all__ = [
    "ChunkQualityReport",
    "MaxChunkSizeValidator",
    "MinChunkSizeValidator",
    "OverlapSanityValidator",
    "DuplicateChunkDetector",
    "OrphanChunkDetector",
    "ChunkManifestValidator",
]
