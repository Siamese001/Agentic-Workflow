"""Semantic Memory Types — ADG-backed embedding use-case types.

Frozen, deterministic dataclasses for the six embedding use-cases:
  1. IncidentBundle      — composite trace+violation+route+heal+policy object
  2. MutationDiffRecord  — RFC 6902 diff, state_diff, rollback context
  3. HealerOutcomeRecord — change packages V1→V2→V3, fix rationale, outcome
  4. PathDPreferencePair — DPO-style human patch + approve/reject reason
  5. GraphNeighborhood   — local ADG subgraph node with structural context
  6. PolicyGuardrailCase — blocked payload + remediation + drift annotation

All types are influence_class='C0_INFORMATIONAL'.
All hashing uses SHA-256 over canonical JSON (sort_keys, no whitespace).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Literal

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

_emit_applies_guardrail("p0", "semantic_memory_types", "p0_governance")
_emit_snapshots_state("p0", "semantic_memory_types", "state_snapshot")
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

_emit_emits_metric_event("semantic_memory_types", "p4obs", "metric_1")
_emit_emits_metric_event("semantic_memory_types", "p4obs", "metric_2")
_emit_emits_metric_event("semantic_memory_types", "p4obs", "metric_3")
_emit_emits_metric_event("semantic_memory_types", "p4obs", "metric_4")
_emit_emits_metric_event("semantic_memory_types", "p4obs", "metric_5")
_emit_emits_metric_event("semantic_memory_types", "p4obs", "metric_6")
_emit_records_incident_event("semantic_memory_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("semantic_memory_types", "p4obs", "anomaly")
_emit_writes_observability_log("semantic_memory_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("semantic_memory_types", "p4obs", "mon_state")
_emit_triggers_alert("semantic_memory_types", "p4obs", "alert")
_emit_links_incident_trace("semantic_memory_types", "p4obs", "trace_link")
_emit_captures_pattern("semantic_memory_types", "p3lm", "pattern")
_emit_records_learning_event("semantic_memory_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("semantic_memory_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("semantic_memory_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("semantic_memory_types", "p3lm", "routing")
_emit_improves_agent_policy("semantic_memory_types", "p3lm", "policy")
_emit_stores_learning_state("semantic_memory_types", "p3lm", "state")
_emit_records_execution_trace("semantic_memory_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("semantic_memory_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("semantic_memory_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("semantic_memory_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("semantic_memory_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("semantic_memory_types", "env_read", "p2_env_1")
_emit_reads_environ("semantic_memory_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("semantic_memory_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("semantic_memory_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "semantic_memory_types", "context_pull")
_emit_pulls_context("p1", "semantic_memory_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "semantic_memory_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "semantic_memory_types", "uwg_term_2")
_emit_writes_through("p1", "semantic_memory_types", "write_through")
_emit_writes_through("p1", "semantic_memory_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "semantic_memory_types", "safety_validation")
_emit_invokes_eval("p1", "semantic_memory_types", "eval_call")
_emit_proposal_commits_routing("p1", "semantic_memory_types", "routing_commit")
_emit_escalates_to_human("p1", "semantic_memory_types", "human_escalation")
_emit_routes_through("p1", "semantic_memory_types", "route_through")
_emit_checks_agent_registry("p1", "semantic_memory_types", "agent_registry")
_emit_validates_agent_capability("p1", "semantic_memory_types", "capability")
_emit_dispatches_execution_plan("p1", "semantic_memory_types", "exec_plan")
_emit_agent_executes_agent("p1", "semantic_memory_types", "sub_agent")
_emit_routes_to_agent("p1", "semantic_memory_types", "target_agent")
_emit_verifies_policy("p1", "semantic_memory_types", "policy_check")
_emit_observes_runtime_state("p1", "semantic_memory_types", "runtime_state")
_emit_verifies_boundary("p1", "semantic_memory_types", "boundary_check")
_emit_transcripts_response("p1", "semantic_memory_types", "transcript")
_emit_hard_fails_untranscripted("p1", "semantic_memory_types")
_emit_gated_by_confidence("p1", "semantic_memory_types", "confidence_gate")
emit_replay_key("p0", "semantic_memory_types")
emit_determinism_digest("p0", "semantic_memory_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "semantic_memory_types", "execution_auth")
_emit_validates_capability("p2", "semantic_memory_types", "capability_check")
_emit_routes_to_capability("p2", "semantic_memory_types", "capability_route")
_emit_writes_via_uwg("p2", "semantic_memory_types", "uwg_write")
_emit_blocks_direct_write("p2", "semantic_memory_types", "direct_write_block")
_emit_records_tool_invocation("p2", "semantic_memory_types", "tool_invocation")
_emit_captures_execution_output("p2", "semantic_memory_types", "exec_output")
_emit_dispatches_agent("p3", "semantic_memory_types", "agent_dispatch")
_emit_coordinates_agents("p3", "semantic_memory_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "semantic_memory_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "semantic_memory_types", "healing_outcome")
_emit_escalates_failure("p3", "semantic_memory_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "semantic_memory_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "semantic_memory_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "semantic_memory_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "semantic_memory_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "semantic_memory_types", "eval_metric")
_emit_stores_embedding("p4", "semantic_memory_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "semantic_memory_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "semantic_memory_types", "exec_snapshot_link")


def _sha256_json(obj: dict) -> str:
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 1. Incident Bundle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IncidentBundle:
    """Composite incident object for case-based reasoning retrieval.

    Embeds together: trace summary, violations, route path, tool/capability,
    state_diff summary, healer used, outcome, and policy hash so that
    nearest-neighbour search operates over the full execution context.

    influence_class is always C0_INFORMATIONAL.
    """

    trace_id: str
    trace_summary: str
    violations: tuple[str, ...]
    route_path: str
    tool_capability: str
    state_diff_summary: str
    healer_id: str
    outcome: Literal["success", "failure", "partial"]
    policy_hash: str
    timestamp_utc: int
    bundle_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("trace_id must not be empty")
        if self.outcome not in ("success", "failure", "partial"):
            raise ValueError(f"outcome must be success/failure/partial, got {self.outcome!r}")
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "bundle_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "healer_id": self.healer_id,
            "outcome": self.outcome,
            "policy_hash": self.policy_hash,
            "route_path": self.route_path,
            "state_diff_summary": self.state_diff_summary,
            "timestamp_utc": self.timestamp_utc,
            "tool_capability": self.tool_capability,
            "trace_id": self.trace_id,
            "trace_summary": self.trace_summary,
            "violations": sorted(self.violations),
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding — deterministic field order."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "IncidentBundle.to_embedding_text"
        )

        parts = [
            f"trace:{self.trace_summary}",
            f"violations:{' | '.join(sorted(self.violations))}",
            f"route:{self.route_path}",
            f"tool:{self.tool_capability}",
            f"diff:{self.state_diff_summary}",
            f"healer:{self.healer_id}",
            f"outcome:{self.outcome}",
            f"policy:{self.policy_hash}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 2. Mutation Diff Record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MutationDiffRecord:
    """RFC 6902-style diff packaged with rollback context for retrieval.

    Enables pre-commit nearest-neighbour checks, post-commit healing retrieval,
    and rollback refinement from similar failed mutations.
    """

    mutation_id: str
    target_resource: str
    operations: tuple[str, ...]
    state_diff_summary: str
    rollback_context: str
    commit_outcome: Literal["committed", "rolled_back", "pending"]
    trace_id: str
    policy_hash: str
    timestamp_utc: int
    diff_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.mutation_id:
            raise ValueError("mutation_id must not be empty")
        if self.commit_outcome not in ("committed", "rolled_back", "pending"):
            raise ValueError(
                f"commit_outcome must be committed/rolled_back/pending, got {self.commit_outcome!r}",
            )
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "diff_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "commit_outcome": self.commit_outcome,
            "mutation_id": self.mutation_id,
            "operations": sorted(self.operations),
            "policy_hash": self.policy_hash,
            "rollback_context": self.rollback_context,
            "state_diff_summary": self.state_diff_summary,
            "target_resource": self.target_resource,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "MutationDiffRecord.to_embedding_text"
        )

        parts = [
            f"mutation:{self.mutation_id}",
            f"resource:{self.target_resource}",
            f"ops:{' | '.join(sorted(self.operations))}",
            f"diff:{self.state_diff_summary}",
            f"rollback:{self.rollback_context}",
            f"outcome:{self.commit_outcome}",
            f"policy:{self.policy_hash}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 3. Healer Outcome Record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HealerOutcomeRecord:
    """Healer playbook record: change packages V1→V2→V3, rationale, outcome.

    High-quality training memory because the healer-validator architecture
    enforces lineage and replay validation on these cases.
    """

    healer_id: str
    failure_type: str
    violation_text: str
    fix_rationale: str
    change_summary: str
    package_version: str
    outcome: Literal["success", "failure", "partial"]
    tier: str
    trace_id: str
    timestamp_utc: int
    outcome_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.healer_id:
            raise ValueError("healer_id must not be empty")
        if not self.failure_type:
            raise ValueError("failure_type must not be empty")
        if self.outcome not in ("success", "failure", "partial"):
            raise ValueError(f"outcome must be success/failure/partial, got {self.outcome!r}")
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "outcome_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "change_summary": self.change_summary,
            "failure_type": self.failure_type,
            "fix_rationale": self.fix_rationale,
            "healer_id": self.healer_id,
            "outcome": self.outcome,
            "package_version": self.package_version,
            "tier": self.tier,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
            "violation_text": self.violation_text,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "HealerOutcomeRecord.to_embedding_text"
        )

        parts = [
            f"healer:{self.healer_id}",
            f"failure:{self.failure_type}",
            f"violation:{self.violation_text}",
            f"rationale:{self.fix_rationale}",
            f"change:{self.change_summary}",
            f"pkg:{self.package_version}",
            f"tier:{self.tier}",
            f"outcome:{self.outcome}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 4. Path D Preference Pair
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PathDPreferencePair:
    """DPO-style human preference pair from Path D HITL decisions.

    Embeds original plan, human patch, approve/reject reason, and resulting
    outcome to enable retrieval of human preference precedents.
    """

    decision_id: str
    original_plan: str
    human_patch: str
    decision: Literal["approved", "rejected", "modified"]
    reason: str
    resulting_outcome: str
    agent: str
    trace_id: str
    timestamp_utc: int
    pair_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("decision_id must not be empty")
        if self.decision not in ("approved", "rejected", "modified"):
            raise ValueError(f"decision must be approved/rejected/modified, got {self.decision!r}")
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "pair_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "agent": self.agent,
            "decision": self.decision,
            "decision_id": self.decision_id,
            "human_patch": self.human_patch,
            "original_plan": self.original_plan,
            "reason": self.reason,
            "resulting_outcome": self.resulting_outcome,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PathDPreferencePair.to_embedding_text"
        )

        parts = [
            f"plan:{self.original_plan}",
            f"patch:{self.human_patch}",
            f"decision:{self.decision}",
            f"reason:{self.reason}",
            f"outcome:{self.resulting_outcome}",
            f"agent:{self.agent}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 5. Graph Neighborhood
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GraphNeighborhood:
    """Local ADG subgraph around a node for architectural motif search.

    Encodes: node identity, layer, inbound/outbound relation types,
    governance edges, mutation/determinism edges, and ownership territory.
    Enables semantic search over architectural patterns.
    """

    node_id: str
    node_type: str
    layer: str
    inbound_relations: tuple[str, ...]
    outbound_relations: tuple[str, ...]
    governance_edges: tuple[str, ...]
    mutation_edges: tuple[str, ...]
    ownership_territory: str
    risk_label: str
    neighborhood_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.node_id:
            raise ValueError("node_id must not be empty")
        if not self.layer:
            raise ValueError("layer must not be empty")
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "neighborhood_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "governance_edges": sorted(self.governance_edges),
            "inbound_relations": sorted(self.inbound_relations),
            "layer": self.layer,
            "mutation_edges": sorted(self.mutation_edges),
            "node_id": self.node_id,
            "node_type": self.node_type,
            "outbound_relations": sorted(self.outbound_relations),
            "ownership_territory": self.ownership_territory,
            "risk_label": self.risk_label,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "GraphNeighborhood.to_embedding_text"
        )

        parts = [
            f"node:{self.node_id}",
            f"type:{self.node_type}",
            f"layer:{self.layer}",
            f"in:{' | '.join(sorted(self.inbound_relations))}",
            f"out:{' | '.join(sorted(self.outbound_relations))}",
            f"gov:{' | '.join(sorted(self.governance_edges))}",
            f"mut:{' | '.join(sorted(self.mutation_edges))}",
            f"territory:{self.ownership_territory}",
            f"risk:{self.risk_label}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 6. Policy Guardrail Case
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PolicyGuardrailCase:
    """Blocked payload case for guardrail drift retrieval.

    Captures blocked payloads, remediation text, false-positive/negative
    annotations, and policy hash to enable calibration of strictness via
    semantic retrieval of similar past blocks.
    """

    case_id: str
    blocked_payload_summary: str
    remediation_text: str
    policy_hash: str
    policy_root: str
    verdict: Literal["true_positive", "false_positive", "false_negative"]
    strictness_level: str
    trace_id: str
    timestamp_utc: int
    case_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        if not self.case_id:
            raise ValueError("case_id must not be empty")
        if self.verdict not in ("true_positive", "false_positive", "false_negative"):
            raise ValueError(
                f"verdict must be true_positive/false_positive/false_negative, got {self.verdict!r}",
            )
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "case_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "blocked_payload_summary": self.blocked_payload_summary,
            "case_id": self.case_id,
            "policy_hash": self.policy_hash,
            "policy_root": self.policy_root,
            "remediation_text": self.remediation_text,
            "strictness_level": self.strictness_level,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
            "verdict": self.verdict,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PolicyGuardrailCase.to_embedding_text"
        )

        parts = [
            f"payload:{self.blocked_payload_summary}",
            f"remediation:{self.remediation_text}",
            f"policy:{self.policy_hash}",
            f"root:{self.policy_root}",
            f"verdict:{self.verdict}",
            f"strictness:{self.strictness_level}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 7. Replay Failure Record (addendum §2.4)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReplayFailureRecord:
    """Determinism failure case for replay triage clustering.

    Captures nondeterminism type, mismatch explanation, affected subsystems,
    and attempted remediation so that nearest-neighbour search can cluster
    systemic determinism leaks and accelerate replay debugging.

    influence_class is always C0_INFORMATIONAL.
    replay_key and determinism_digest are metadata-only (not embedded in text).
    """

    failure_id: str
    failure_summary: str
    nondeterminism_type: str
    mismatch_explanation: str
    affected_subsystems: tuple[str, ...]
    attempted_remediation: str
    replay_key: str
    determinism_digest: str
    trace_id: str
    timestamp_utc: int
    failure_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(
        default="C0_INFORMATIONAL",
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.failure_id:
            raise ValueError("failure_id must not be empty")
        if not self.nondeterminism_type:
            raise ValueError("nondeterminism_type must not be empty")
        if not self.replay_key:
            raise ValueError("replay_key must not be empty")
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "failure_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "affected_subsystems": sorted(self.affected_subsystems),
            "attempted_remediation": self.attempted_remediation,
            "determinism_digest": self.determinism_digest,
            "failure_id": self.failure_id,
            "failure_summary": self.failure_summary,
            "mismatch_explanation": self.mismatch_explanation,
            "nondeterminism_type": self.nondeterminism_type,
            "replay_key": self.replay_key,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding.

        IDs (replay_key, determinism_digest, trace_id) are metadata only;
        they do NOT appear in the embedded text.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ReplayFailureRecord.to_embedding_text"
        )

        parts = [
            f"summary:{self.failure_summary}",
            f"nondeterminism:{self.nondeterminism_type}",
            f"mismatch:{self.mismatch_explanation}",
            f"subsystems:{' | '.join(sorted(self.affected_subsystems))}",
            f"remediation:{self.attempted_remediation}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 8. Prompt Outcome Embedding Record (addendum §2.5)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PromptOutcomeEmbeddingRecord:
    """Prompt construction + outcome for semantic memory.

    Encodes prompt slot summaries (S0/D0/I0/C0/U0), task description,
    answer summary, safety outcome, and retrieval grounding so that
    nearest-neighbour search can find successful prompt constructions
    and detect prompt drift.

    prompt_hash, template_id, route, model, policy_hash are metadata only.
    influence_class is always C0_INFORMATIONAL.
    """

    record_id: str
    slot_s0_summary: str
    slot_d0_summary: str
    slot_i0_summary: str
    slot_c0_summary: str
    slot_u0_summary: str
    task_description: str
    answer_summary: str
    safety_outcome: str
    retrieval_grounding_summary: str
    prompt_hash: str
    template_id: str
    route: str
    model: str
    policy_hash: str
    trace_id: str
    timestamp_utc: int
    record_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(
        default="C0_INFORMATIONAL",
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.record_id:
            raise ValueError("record_id must not be empty")
        if not self.task_description:
            raise ValueError("task_description must not be empty")
        if self.safety_outcome not in (
            "ALLOWED",
            "BLOCKED",
            "ESCALATED",
            "HEALED",
            "UNKNOWN",
        ):
            raise ValueError(
                f"safety_outcome must be ALLOWED/BLOCKED/ESCALATED/HEALED/UNKNOWN, "
                f"got {self.safety_outcome!r}",
            )
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "record_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "answer_summary": self.answer_summary,
            "model": self.model,
            "policy_hash": self.policy_hash,
            "prompt_hash": self.prompt_hash,
            "record_id": self.record_id,
            "retrieval_grounding_summary": self.retrieval_grounding_summary,
            "route": self.route,
            "safety_outcome": self.safety_outcome,
            "slot_c0_summary": self.slot_c0_summary,
            "slot_d0_summary": self.slot_d0_summary,
            "slot_i0_summary": self.slot_i0_summary,
            "slot_s0_summary": self.slot_s0_summary,
            "slot_u0_summary": self.slot_u0_summary,
            "task_description": self.task_description,
            "template_id": self.template_id,
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding.

        IDs (prompt_hash, template_id, route, model, policy_hash, trace_id)
        are metadata only; they do NOT appear in the embedded text.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "PromptOutcomeEmbeddingRecord.to_embedding_text"
        )

        parts = [
            f"s0:{self.slot_s0_summary}",
            f"d0:{self.slot_d0_summary}",
            f"i0:{self.slot_i0_summary}",
            f"c0:{self.slot_c0_summary}",
            f"u0:{self.slot_u0_summary}",
            f"task:{self.task_description}",
            f"answer:{self.answer_summary}",
            f"safety:{self.safety_outcome}",
            f"grounding:{self.retrieval_grounding_summary}",
        ]
        return " ## ".join(parts)


# ---------------------------------------------------------------------------
# 9. Retrieval Case Record (addendum §2.6)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RetrievalCaseRecord:
    """RAG retrieval quality case for retrieval policy learning.

    Encodes query summary, chunk summaries, support reasoning, and answer
    quality summary with quality signals (completeness_score, support_score,
    escalation_flag, healer_invoked, replay_pass) as metadata so that
    the meta-learning bus can adjust retrieval depth, chunk ranking, and
    corpus expansion strategies.

    query_id and chunk_ids are metadata only.
    influence_class is always C0_INFORMATIONAL.
    """

    case_id: str
    query_summary: str
    chunk_summaries: tuple[str, ...]
    support_reasoning: str
    answer_quality_summary: str
    query_id: str
    chunk_ids: tuple[str, ...]
    support_score: float
    completeness_score: float
    escalation_flag: bool
    healer_invoked: bool
    replay_pass: bool
    trace_id: str
    timestamp_utc: int
    case_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(
        default="C0_INFORMATIONAL",
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.case_id:
            raise ValueError("case_id must not be empty")
        if not self.query_summary:
            raise ValueError("query_summary must not be empty")
        if not (0.0 <= self.support_score <= 1.0):
            raise ValueError(
                f"support_score must be in [0.0, 1.0], got {self.support_score}",
            )
        if not (0.0 <= self.completeness_score <= 1.0):
            raise ValueError(
                f"completeness_score must be in [0.0, 1.0], got {self.completeness_score}",
            )
        h = _sha256_json(self._canonical_dict())
        object.__setattr__(self, "case_hash", h)

    def _canonical_dict(self) -> dict:
        return {
            "answer_quality_summary": self.answer_quality_summary,
            "case_id": self.case_id,
            "chunk_ids": sorted(self.chunk_ids),
            "chunk_summaries": sorted(self.chunk_summaries),
            "completeness_score": round(self.completeness_score, 6),
            "escalation_flag": self.escalation_flag,
            "healer_invoked": self.healer_invoked,
            "query_id": self.query_id,
            "query_summary": self.query_summary,
            "replay_pass": self.replay_pass,
            "support_reasoning": self.support_reasoning,
            "support_score": round(self.support_score, 6),
            "timestamp_utc": self.timestamp_utc,
            "trace_id": self.trace_id,
        }

    def to_embedding_text(self) -> str:
        """Canonical flat text for embedding.

        query_id and chunk_ids are metadata only; they do NOT appear in text.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalCaseRecord.to_embedding_text"
        )

        chunks_text = " | ".join(sorted(self.chunk_summaries))
        parts = [
            f"query:{self.query_summary}",
            f"chunks:{chunks_text}",
            f"support:{self.support_reasoning}",
            f"quality:{self.answer_quality_summary}",
        ]
        return " ## ".join(parts)


__all__ = [
    "GraphNeighborhood",
    "HealerOutcomeRecord",
    "IncidentBundle",
    "MutationDiffRecord",
    "PathDPreferencePair",
    "PolicyGuardrailCase",
    "PromptOutcomeEmbeddingRecord",
    "ReplayFailureRecord",
    "RetrievalCaseRecord",
]
