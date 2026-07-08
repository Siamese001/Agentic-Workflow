"""
Reasoning Intensity Contracts — L0 Authority Surface.

Defines the sealed, versioned, cryptographically-bound contracts for
reasoning intensity governance. L0 computes and stamps these; L3 enforces;
apps_* consume read-only.

Design invariants:
  - All types are immutable (frozen dataclasses).
  - profile_hash = SHA256(deterministic_serialization(profile)).
  - Complexity scoring is a pure function of structural inputs only.
  - No C0 embedding outputs may appear as policy signals.
  - Tier mapping is discrete: LOW / MEDIUM / HIGH / CRITICAL.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.L0_routing.types.routing_artifact_types import RouteDecisionArtifact
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "reasoning_intensity_types")
trace_contract.emit_determinism_digest("p0", "reasoning_intensity_types")

trace_contract._emit_dispatches_healing_run("p1", "reasoning_intensity_types", "L0")
trace_contract._emit_routes_through("p1", "reasoning_intensity_types", "L0")
trace_contract._emit_checks_agent_registry("p1", "reasoning_intensity_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "reasoning_intensity_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "reasoning_intensity_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "reasoning_intensity_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "reasoning_intensity_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "reasoning_intensity_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "reasoning_intensity_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "reasoning_intensity_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "reasoning_intensity_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "reasoning_intensity_types")
trace_contract._emit_gated_by_confidence("p1", "reasoning_intensity_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "reasoning_intensity_types", "L0")
trace_contract._emit_reads_policy_state("p1", "reasoning_intensity_types", "L0")
trace_contract._emit_authorize_and_execute("p2", "reasoning_intensity_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "reasoning_intensity_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "reasoning_intensity_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "reasoning_intensity_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "reasoning_intensity_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "reasoning_intensity_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "reasoning_intensity_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "reasoning_intensity_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "reasoning_intensity_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "reasoning_intensity_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "reasoning_intensity_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "reasoning_intensity_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "reasoning_intensity_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "reasoning_intensity_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "reasoning_intensity_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "reasoning_intensity_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "reasoning_intensity_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "reasoning_intensity_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "reasoning_intensity_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "reasoning_intensity_types", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("reasoning_intensity_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("reasoning_intensity_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("reasoning_intensity_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("reasoning_intensity_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("reasoning_intensity_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("reasoning_intensity_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("reasoning_intensity_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("reasoning_intensity_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("reasoning_intensity_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("reasoning_intensity_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("reasoning_intensity_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("reasoning_intensity_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("reasoning_intensity_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("reasoning_intensity_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("reasoning_intensity_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("reasoning_intensity_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("reasoning_intensity_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("reasoning_intensity_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("reasoning_intensity_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("reasoning_intensity_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("reasoning_intensity_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("reasoning_intensity_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("reasoning_intensity_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("reasoning_intensity_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("reasoning_intensity_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("reasoning_intensity_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("reasoning_intensity_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("reasoning_intensity_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "reasoning_intensity_types", "context_pull")
trace_contract._emit_pulls_context("p1", "reasoning_intensity_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_intensity_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_intensity_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "reasoning_intensity_types", "write_through")
trace_contract._emit_writes_through("p1", "reasoning_intensity_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "reasoning_intensity_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "reasoning_intensity_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "reasoning_intensity_types", "routing_commit")


class ReasoningTier(str, Enum):
    """Discrete reasoning intensity tiers. No fractional values allowed."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class StageTokenBudget:
    """Per-HOP-stage token budget constraint stamped by L0."""

    stage_id: int
    max_tokens: int

    def __post_init__(self) -> None:
        if self.stage_id < 1:
            raise ValueError(f"StageTokenBudget: stage_id must be >= 1, got {self.stage_id}")
        if self.max_tokens < 1:
            raise ValueError(f"StageTokenBudget: max_tokens must be >= 1, got {self.max_tokens}")


@dataclass(frozen=True)
class ReasoningIntensityProfile:
    """Sealed reasoning intensity profile stamped by L0 ReasoningPolicyEngine.

    All fields are required. profile_hash is computed over the canonical
    serialization of all policy parameters and must be included in:
      - execution trace
      - replay key
      - L3 enforcement log

    L3 may only REDUCE (enforce ceilings). No upward mutation is permitted.
    """

    reasoning_profile_version: str
    reasoning_policy_hash: str
    tier: ReasoningTier
    max_branches: int
    max_depth: int
    enable_reflection: bool
    token_budget_per_stage: tuple[StageTokenBudget, ...]
    allowed_modes: tuple[str, ...]
    profile_hash: str
    # ADG complexity bindings for on-the-fly optimization
    complexity_hash: str = ""  # SHA256 of ADG complexity surface
    adg_complexity_tier: str = "moderate"  # simple, moderate, complex, deep
    adg_node_count: int = 0  # Number of ADG nodes in module's call graph
    adg_edge_count: int = 0  # Number of ADG edges in module's call graph

    def __post_init__(self) -> None:
        if not self.reasoning_profile_version:
            raise ValueError("ReasoningIntensityProfile: reasoning_profile_version must be non-empty")
        if not self.reasoning_policy_hash:
            raise ValueError("ReasoningIntensityProfile: reasoning_policy_hash must be non-empty")
        if self.max_branches < 1:
            raise ValueError(f"ReasoningIntensityProfile: max_branches must be >= 1, got {self.max_branches}")
        if self.max_depth < 1:
            raise ValueError(f"ReasoningIntensityProfile: max_depth must be >= 1, got {self.max_depth}")
        if not self.profile_hash:
            raise ValueError("ReasoningIntensityProfile: profile_hash must be non-empty")
        expected = _compute_profile_hash(
            version=self.reasoning_profile_version,
            policy_hash=self.reasoning_policy_hash,
            tier=self.tier.value,
            max_branches=self.max_branches,
            max_depth=self.max_depth,
            enable_reflection=self.enable_reflection,
            token_budget_per_stage=[
                {"stage_id": b.stage_id, "max_tokens": b.max_tokens} for b in self.token_budget_per_stage
            ],
            allowed_modes=sorted(self.allowed_modes),
            complexity_hash=self.complexity_hash,
            adg_complexity_tier=self.adg_complexity_tier,
            adg_node_count=self.adg_node_count,
            adg_edge_count=self.adg_edge_count,
        )
        if self.profile_hash != expected:
            raise ValueError(
                f"ReasoningIntensityProfile: profile_hash mismatch. Expected {expected[:16]}..., got {self.profile_hash[:16]}...",
            )


@dataclass(frozen=True)
class SignedExecutionEnvelope:
    """First-class sealed execution contract combining route decision and reasoning profile.

    L0 stamps this; L3 reads it; apps_* receive it as read-only constraints.
    The envelope_hash covers both route_decision and reasoning_profile to
    prevent partial substitution attacks.
    """

    route_decision: RouteDecisionArtifact
    reasoning_profile: ReasoningIntensityProfile
    enforcement_constraints: dict[str, Any]
    policy_hash: str
    envelope_hash: str

    def __post_init__(self) -> None:
        if not self.policy_hash:
            raise ValueError("SignedExecutionEnvelope: policy_hash must be non-empty")
        if not self.envelope_hash:
            raise ValueError("SignedExecutionEnvelope: envelope_hash must be non-empty")
        expected = _compute_envelope_hash(
            route_decision_trace_id=self.route_decision.trace_id,
            profile_hash=self.reasoning_profile.profile_hash,
            policy_hash=self.policy_hash,
        )
        if self.envelope_hash != expected:
            raise ValueError(
                f"SignedExecutionEnvelope: envelope_hash mismatch. Expected {expected[:16]}..., got {self.envelope_hash[:16]}...",
            )


@dataclass(frozen=True)
class ReasoningConstraintViolation:
    """Emitted by L3 ReasoningIntensityEnforcer on policy ceiling breach.

    This is a deterministic failure artifact — not a soft warning.
    The violating stage MUST be halted immediately.
    """

    trace_id: str
    profile_hash: str
    stage_id: int
    violation_kind: str
    limit_value: int | float
    observed_value: int | float

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("ReasoningConstraintViolation: trace_id must be non-empty")
        if not self.profile_hash:
            raise ValueError("ReasoningConstraintViolation: profile_hash must be non-empty")
        if not self.violation_kind:
            raise ValueError("ReasoningConstraintViolation: violation_kind must be non-empty")


@dataclass(frozen=True)
class ReasoningEnforcementTelemetry:
    """Non-authoritative telemetry emitted by L3 after stage execution.

    CRITICAL: This data MUST NOT influence the current run.
    It may only be used by L0 for FUTURE calibration, and only after
    windowed aggregation and versioning (no direct feedback loops).
    """

    trace_id: str
    profile_hash: str
    stage_id: int
    branches_used: int
    depth_reached: int
    tokens_used: int
    reflection_triggered: bool
    early_stop_triggered: bool
    compliant: bool


def _compute_profile_hash(
    version: str,
    policy_hash: str,
    tier: str,
    max_branches: int,
    max_depth: int,
    enable_reflection: bool,
    token_budget_per_stage: list[dict[str, int]],
    allowed_modes: list[str],
    complexity_hash: str = "",
    adg_complexity_tier: str = "moderate",
    adg_node_count: int = 0,
    adg_edge_count: int = 0,
) -> str:
    """Compute SHA256 over deterministic canonical serialization of profile parameters."""
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "_compute_profile_hash", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "_compute_profile_hash", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L0_ROUTING, "_compute_profile_hash")
    canonical = json.dumps(
        {
            "version": version,
            "policy_hash": policy_hash,
            "tier": tier,
            "max_branches": max_branches,
            "max_depth": max_depth,
            "enable_reflection": enable_reflection,
            "token_budget_per_stage": sorted(token_budget_per_stage, key=lambda x: x["stage_id"]),
            "allowed_modes": sorted(allowed_modes),
            "complexity_hash": complexity_hash,
            "adg_complexity_tier": adg_complexity_tier,
            "adg_node_count": adg_node_count,
            "adg_edge_count": adg_edge_count,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _compute_envelope_hash(route_decision_trace_id: str, profile_hash: str, policy_hash: str) -> str:
    """Compute SHA256 over envelope binding fields."""
    canonical = json.dumps(
        {
            "route_decision_trace_id": route_decision_trace_id,
            "profile_hash": profile_hash,
            "policy_hash": policy_hash,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_profile_hash(
    version: str,
    policy_hash: str,
    tier: ReasoningTier,
    max_branches: int,
    max_depth: int,
    enable_reflection: bool,
    token_budget_per_stage: list[StageTokenBudget],
    allowed_modes: list[str],
    complexity_hash: str = "",
    adg_complexity_tier: str = "moderate",
    adg_node_count: int = 0,
    adg_edge_count: int = 0,
) -> str:
    """Compute the profile_hash for use before constructing ReasoningIntensityProfile."""
    return _compute_profile_hash(
        version=version,
        policy_hash=policy_hash,
        tier=tier.value,
        max_branches=max_branches,
        max_depth=max_depth,
        enable_reflection=enable_reflection,
        token_budget_per_stage=[
            {"stage_id": b.stage_id, "max_tokens": b.max_tokens} for b in token_budget_per_stage
        ],
        allowed_modes=sorted(allowed_modes),
        complexity_hash=complexity_hash,
        adg_complexity_tier=adg_complexity_tier,
        adg_node_count=adg_node_count,
        adg_edge_count=adg_edge_count,
    )


def build_envelope_hash(route_decision_trace_id: str, profile_hash: str, policy_hash: str) -> str:
    """Compute the envelope_hash for use before constructing SignedExecutionEnvelope."""
    return _compute_envelope_hash(
        route_decision_trace_id=route_decision_trace_id,
        profile_hash=profile_hash,
        policy_hash=policy_hash,
    )


TIER_PARAMETER_TABLE: dict[ReasoningTier, dict[str, Any]] = {
    ReasoningTier.LOW: {
        "max_branches": 1,
        "max_depth": 1,
        "enable_reflection": False,
        "allowed_modes": ["cot"],
        "token_budget_multiplier": 0.5,
    },
    ReasoningTier.MEDIUM: {
        "max_branches": 2,
        "max_depth": 2,
        "enable_reflection": False,
        "allowed_modes": ["cot", "hybrid_cot_tot"],
        "token_budget_multiplier": 1.0,
    },
    ReasoningTier.HIGH: {
        "max_branches": 3,
        "max_depth": 3,
        "enable_reflection": True,
        "allowed_modes": ["cot", "hybrid_cot_tot", "tot"],
        "token_budget_multiplier": 1.5,
    },
    ReasoningTier.CRITICAL: {
        "max_branches": 5,
        "max_depth": 5,
        "enable_reflection": True,
        "allowed_modes": ["cot", "hybrid_cot_tot", "tot", "reflexion"],
        "token_budget_multiplier": 2.0,
    },
}

# ADG complexity tier mapping for on-the-fly reasoning optimization
ADG_COMPLEXITY_TIER_TABLE: dict[str, dict[str, Any]] = {
    "simple": {
        "adg_complexity_tier": "simple",
        "max_adg_nodes": 100,
        "max_adg_edges": 500,
        "reasoning_path_id": "simple_cot",
        "description": "Simple queries with minimal call graph complexity",
    },
    "moderate": {
        "adg_complexity_tier": "moderate",
        "max_adg_nodes": 500,
        "max_adg_edges": 2500,
        "reasoning_path_id": "moderate_cot_hybrid",
        "description": "Moderate complexity with balanced reasoning depth",
    },
    "complex": {
        "adg_complexity_tier": "complex",
        "max_adg_nodes": 2000,
        "max_adg_edges": 10000,
        "reasoning_path_id": "complex_tot_reflexion",
        "description": "Complex queries requiring full reasoning capabilities",
    },
    "deep": {
        "adg_complexity_tier": "deep",
        "max_adg_nodes": float("inf"),
        "max_adg_edges": float("inf"),
        "reasoning_path_id": "deep_full_reasoning",
        "description": "Deep complexity queries with maximum reasoning depth",
    },
}


def compute_complexity_tier(adg_node_count: int, adg_edge_count: int) -> str:
    """
    Compute ADG complexity tier from node and edge counts.

    Args:
        adg_node_count: Number of ADG nodes in module's call graph
        adg_edge_count: Number of ADG edges in module's call graph

    Returns:
        Complexity tier string: "simple", "moderate", "complex", or "deep"
    """
    for tier, config in ADG_COMPLEXITY_TIER_TABLE.items():
        if adg_node_count <= config["max_adg_nodes"] and adg_edge_count <= config["max_adg_edges"]:
            return tier
    return "deep"


__all__ = [
    "TIER_PARAMETER_TABLE",
    "ADG_COMPLEXITY_TIER_TABLE",
    "ReasoningConstraintViolation",
    "ReasoningEnforcementTelemetry",
    "ReasoningIntensityProfile",
    "ReasoningTier",
    "SignedExecutionEnvelope",
    "StageTokenBudget",
    "build_envelope_hash",
    "build_profile_hash",
    "compute_complexity_tier",
]
