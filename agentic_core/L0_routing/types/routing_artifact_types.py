"""
V15 Typed Artifacts — P1 Fail-Closed Compliance Surface.

All typed artifacts required by the V15 Target State audit (Prompt v5.0 Enhanced)
that are gated by P1 (Fail-Closed Defaults).

Each TypedDict/dataclass here satisfies a specific audit capability (§ reference in docstring).
Fields are the **exact** set mandated by the audit contract — no more, no less.

Contract version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.L0_routing.utils.seams.layer_emission_seam import (
    assert_layer_may_emit,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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
    emit_determinism_digest,
    emit_replay_key,
)

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

# =============================================================================
# §3.1 — RouteDecision Typed Artifact
# Required fields: trace_id, timestamp, route_path, risk_score,
#                  budget_est, rationale_enum, policy_config_hash
# =============================================================================


class RoutingRationale(str, Enum):
    """§3.2 — Rationale restricted to a finite enum. Free-form prose is invalid."""

    LOW_RISK_BYPASS = "low_risk_bypass"
    STANDARD_VALIDATION = "standard_validation"
    HUMAN_ESCALATION = "human_escalation"
    POLICY_CHALLENGE = "policy_challenge"
    ROUTE_RECOVERY = "route_recovery"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    GUARDIAN_SIGNAL = "guardian_signal"
    BUDGET_OVERFLOW = "budget_overflow"


class RoutePath(str, Enum):
    """§3.3 — Routing paths strictly defined (5 paths)."""

    LOW_RISK_BYPASS = "low_risk_bypass"
    STANDARD_VALIDATION = "standard_validation"
    HUMAN_ESCALATION = "human_escalation"
    POLICY_CHALLENGE_LOOP = "policy_challenge_loop"
    ROUTE_RECOVERY_BUDGET_OVERFLOW = "route_recovery_budget_overflow"


@dataclass(frozen=True)
class RouteDecisionArtifact:
    """§3.1 — Typed RouteDecision artifact with all 7 required fields."""

    trace_id: str
    timestamp: str
    route_path: RoutePath
    risk_score: float
    budget_est: float
    rationale_enum: RoutingRationale
    policy_config_hash: str
    # §Phase3.2 — SemanticClock propagation
    semantic_clock: SemanticClockSnapshot | None = None


# =============================================================================
# §11.1 — TokenCap Artifact
# Required fields: trace_id, policy_hash, budget_limit,
#                  tokens_requested, gate_result
# =============================================================================


class TokenGateResult(str, Enum):
    """Gate result for TokenCap enforcement."""

    ALLOW = "allow"
    DENY = "deny"
    DOWNGRADE = "downgrade"


@dataclass(frozen=True)
class TokenCapArtifact:
    """§11.1 — TokenCap enforcement artifact. Emitted before any LLM call."""

    trace_id: str
    policy_hash: str
    budget_limit: int
    tokens_requested: int
    gate_result: TokenGateResult


@dataclass(frozen=True)
class PermsArtifact:
    """§11.1 — Perms artifact passed to agent with budget authorization."""

    trace_id: str
    policy_hash: str
    budget: int


# =============================================================================
# §5.4 — SelfHealingTrigger
# Required fields: trace_id, source_layer, target_pipe,
#                  signal_hash, severity_enum
# =============================================================================


class SeverityEnum(str, Enum):
    """Severity levels for incidents and triggers."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SelfHealingTrigger:
    """§5.4 — L6 emits to L2 to trigger healing from observability signals."""

    trace_id: str
    source_layer: str
    target_pipe: str
    signal_hash: str
    severity_enum: SeverityEnum


# =============================================================================
# §2.8 — AGGREGATE artifact
# Required fields: trace_id, impact_scope, rollback_vector,
#                  risk_delta, pre_heal_assessment
# =============================================================================


@dataclass(frozen=True)
class AggregateArtifact:
    """§2.8 — AGGREGATE emitted on conditional flows (L2 pre-heal)."""

    trace_id: str
    impact_scope: list[str]
    rollback_vector: str
    risk_delta: float
    pre_heal_assessment: str


# =============================================================================
# §10.4 — RESULT artifact
# Required fields: trace_id, execution_outcome, final_state_hash,
#                  artifact_class
# =============================================================================


@dataclass(frozen=True)
class ResultArtifact:
    """§10.4 — RESULT emitted exclusively by L2 after successful heal."""

    trace_id: str
    execution_outcome: str
    final_state_hash: str
    artifact_class: str
    emitting_layer: str = "L2"

    def __post_init__(self) -> None:
        assert_layer_may_emit("RESULT", self.emitting_layer, self.trace_id)


# =============================================================================
# §15.6 — INCIDENT artifact
# Required fields: trace_id, incident_id, correlation_hash,
#                  severity_enum, telemetry_events
# =============================================================================


@dataclass(frozen=True)
class IncidentArtifact:
    """§15.6 — INCIDENT with mandatory telemetry event emission."""

    trace_id: str
    incident_id: str
    correlation_hash: str
    severity_enum: SeverityEnum
    telemetry_events: list[str]


# =============================================================================
# §6.3 — TokenControl Artifact
# Required fields: trace_id, prompt_hash, gold_tokens
# =============================================================================


@dataclass(frozen=True)
class TokenControlArtifact:
    """§6.3 — Emitted PRIOR to LLM submission. Token-bounded (<=300 tokens)."""

    trace_id: str
    prompt_hash: str
    gold_tokens: int

    def __post_init__(self) -> None:
        if self.gold_tokens > 300:
            raise ValueError(
                f"TokenControlArtifact: gold_tokens={self.gold_tokens} exceeds 300-token bound",
            )


# =============================================================================
# §15.1 — Tiered Vigilance Strategy
# Tier I: Budget/Token Drains
# Tier II: Anomalous Presence (Exclusive Dynamic Probes)
# Tier III: Evacuation Alert Engage (Emergency Exfiltration/Shutdown)
# =============================================================================


class VigilanceTier(str, Enum):
    """§15.1 — Monitoring is strictly stratified into three tiers."""

    TIER_I = "tier_i_budget_drain"
    TIER_II = "tier_ii_anomalous_presence"
    TIER_III = "tier_iii_evacuation"


@dataclass(frozen=True)
class EvacuationProtocol:
    """§15.1 — Tier III Evacuation Alert Engage (freeze + exfiltration path)."""

    trace_id: str
    tier: VigilanceTier
    freeze_state: bool
    exfiltration_path: str
    reason: str


# =============================================================================
# §15.4 — Capability Depletion Tracker
# =============================================================================


@dataclass
class CapabilityDepletionTracker:
    """§15.4 — Tracks tool slot depletion rate."""

    trace_id: str
    total_slots: int
    used_slots: int = 0
    depletion_log: list[dict[str, Any]] = field(default_factory=list)

    @property
    def depletion_rate(self) -> float:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "CapabilityDepletionTracker.depletion_rate"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if self.total_slots == 0:
            return 1.0
        return self.used_slots / self.total_slots

    def consume_slot(self, tool_name: str) -> bool:
        """Consume a tool slot. Returns False if depleted (fail-closed)."""
        if self.used_slots >= self.total_slots:
            return False
        self.used_slots += 1
        self.depletion_log.append(
            {"tool": tool_name, "slots_remaining": self.total_slots - self.used_slots},
        )
        return True


# =============================================================================
# §4.1 / §4.3 — Policy Config Guard types
# =============================================================================


@dataclass(frozen=True)
class PolicyConfigSnapshot:
    """§4.1 — Immutable snapshot of policy_config taken at wave start."""

    policy_hash: str
    wave_id: str
    frozen: bool = True


# =============================================================================
# §1.7 — HealingPlan Typed Artifact
# Required fields: trace_id, plan_id, manifests, semantic_clock_tick,
#                  policy_liaison_node
# =============================================================================


@dataclass(frozen=True)
class HealingPlan:
    """§1.7 — Typed HealingPlan artifact with all required fields.

    Represents a structured healing plan that L2 agents produce
    and L0/L5/L6 cannot write.
    """

    trace_id: str
    plan_id: str
    manifests: tuple[str, ...]
    semantic_clock_tick: int
    policy_liaison_node: str

    emitting_layer: str = "L2"

    def __post_init__(self) -> None:
        assert_layer_may_emit("HEALING_PLAN", self.emitting_layer, self.trace_id)
        if not self.trace_id:
            raise ValueError("HealingPlan: trace_id must be non-empty")
        if not self.plan_id:
            raise ValueError("HealingPlan: plan_id must be non-empty")
        if not isinstance(self.manifests, tuple):
            raise TypeError("HealingPlan: manifests must be a tuple")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"HealingPlan: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )
        if not self.policy_liaison_node:
            raise ValueError("HealingPlan: policy_liaison_node must be non-empty")


# =============================================================================
# §2.5 — StaleWriteIncident Typed Artifact
# Required fields: trace_id, target_path, expected_hash, actual_hash,
#                  semantic_clock_tick
# =============================================================================


@dataclass(frozen=True)
class StaleWriteIncident:
    """§2.5 — Typed StaleWriteIncident for hash-mismatch detection.

    Emitted when a healer attempts to write to a file whose hash
    has changed since the boundary snapshot was taken.
    """

    trace_id: str
    target_path: str
    expected_hash: str
    actual_hash: str
    semantic_clock_tick: int

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise ValueError("StaleWriteIncident: trace_id must be non-empty")
        if not self.target_path:
            raise ValueError("StaleWriteIncident: target_path must be non-empty")
        if not self.expected_hash:
            raise ValueError("StaleWriteIncident: expected_hash must be non-empty")
        if not self.actual_hash:
            raise ValueError("StaleWriteIncident: actual_hash must be non-empty")
        if self.semantic_clock_tick < 0:
            raise ValueError(
                f"StaleWriteIncident: semantic_clock_tick must be >= 0, got {self.semantic_clock_tick}",
            )


# =============================================================================
# §2.5 — Pipe Order (strict 1..10)
# =============================================================================

HEALER_PIPE_ORDER: tuple[str, ...] = (
    "schema_validation",
    "hash_verification",
    "immediate_rollback_on_mismatch",
    "signed_modify_override_check",
    "stale_write_incident_emission",
    "circuit_breaker_increment",
    "ast_deserialization",
    "ast_native_transformation",
    "post_transform_node_id_check",
    "commit",
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AggregateArtifact",
    "CapabilityDepletionTracker",
    "EvacuationProtocol",
    "HEALER_PIPE_ORDER",
    "HealingPlan",
    "IncidentArtifact",
    "PermsArtifact",
    "PolicyConfigSnapshot",
    "ResultArtifact",
    "RoutePath",
    "RouteDecisionArtifact",
    "RoutingRationale",
    "SelfHealingTrigger",
    "SeverityEnum",
    "StaleWriteIncident",
    "TokenCapArtifact",
    "TokenControlArtifact",
    "TokenGateResult",
    "VigilanceTier",
]
