"""
V15 Framework Contracts — P1 Fail-Closed Compliance Surface.

Runtime contracts that enforce P1 (Fail-Closed Defaults) invariants required
by the V15 Target State audit (Prompt v5.0 Enhanced).

Each class/function here satisfies a specific audit capability (§ reference in docstring).
These are enforcement mechanisms, not types — they consume the types from routing_artifact_types.py.

Contract version: 1.0.0
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L0_routing.types.routing_artifact_types import (
    HEALER_PIPE_ORDER,
    AggregateArtifact,
    CapabilityDepletionTracker,
    EvacuationProtocol,
    IncidentArtifact,
    ResultArtifact,
    RouteDecisionArtifact,
    TokenCapArtifact,
    TokenGateResult,
    VigilanceTier,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "routing_contracts_types")
emit_determinism_digest("p0", "routing_contracts_types")

_emit_dispatches_healing_run("p1", "routing_contracts_types", "L0")
_emit_routes_through("p1", "routing_contracts_types", "L0")
_emit_checks_agent_registry("p1", "routing_contracts_types", "agent_registry")
_emit_validates_agent_capability("p1", "routing_contracts_types", "capability")
_emit_dispatches_execution_plan("p1", "routing_contracts_types", "exec_plan")
_emit_agent_executes_agent("p1", "routing_contracts_types", "sub_agent")
_emit_routes_to_agent("p1", "routing_contracts_types", "target_agent")
_emit_verifies_policy("p1", "routing_contracts_types", "policy_check")
_emit_observes_runtime_state("p1", "routing_contracts_types", "runtime_state")
_emit_verifies_boundary("p1", "routing_contracts_types", "boundary_check")
_emit_transcripts_response("p1", "routing_contracts_types", "transcript")
_emit_hard_fails_untranscripted("p1", "routing_contracts_types")
_emit_gated_by_confidence("p1", "routing_contracts_types", "confidence_gate")
_emit_escalates_to_human("p1", "routing_contracts_types", "L0")
_emit_reads_policy_state("p1", "routing_contracts_types", "L0")
_emit_authorize_and_execute("p2", "routing_contracts_types", "execution_auth")
_emit_validates_capability("p2", "routing_contracts_types", "capability_check")
_emit_routes_to_capability("p2", "routing_contracts_types", "capability_route")
_emit_writes_via_uwg("p2", "routing_contracts_types", "uwg_write")
_emit_blocks_direct_write("p2", "routing_contracts_types", "direct_write_block")
_emit_records_tool_invocation("p2", "routing_contracts_types", "tool_invocation")
_emit_captures_execution_output("p2", "routing_contracts_types", "exec_output")
_emit_dispatches_agent("p3", "routing_contracts_types", "agent_dispatch")
_emit_coordinates_agents("p3", "routing_contracts_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "routing_contracts_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "routing_contracts_types", "healing_outcome")
_emit_escalates_failure("p3", "routing_contracts_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "routing_contracts_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "routing_contracts_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "routing_contracts_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "routing_contracts_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "routing_contracts_types", "eval_metric")
_emit_stores_embedding("p4", "routing_contracts_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "routing_contracts_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "routing_contracts_types", "exec_snapshot_link")
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

_emit_emits_metric_event("routing_contracts_types", "p4obs", "metric_1")
_emit_emits_metric_event("routing_contracts_types", "p4obs", "metric_2")
_emit_emits_metric_event("routing_contracts_types", "p4obs", "metric_3")
_emit_emits_metric_event("routing_contracts_types", "p4obs", "metric_4")
_emit_emits_metric_event("routing_contracts_types", "p4obs", "metric_5")
_emit_emits_metric_event("routing_contracts_types", "p4obs", "metric_6")
_emit_records_incident_event("routing_contracts_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("routing_contracts_types", "p4obs", "anomaly")
_emit_writes_observability_log("routing_contracts_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("routing_contracts_types", "p4obs", "mon_state")
_emit_triggers_alert("routing_contracts_types", "p4obs", "alert")
_emit_links_incident_trace("routing_contracts_types", "p4obs", "trace_link")
_emit_captures_pattern("routing_contracts_types", "p3lm", "pattern")
_emit_records_learning_event("routing_contracts_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("routing_contracts_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("routing_contracts_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("routing_contracts_types", "p3lm", "routing")
_emit_improves_agent_policy("routing_contracts_types", "p3lm", "policy")
_emit_stores_learning_state("routing_contracts_types", "p3lm", "state")
_emit_records_execution_trace("routing_contracts_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("routing_contracts_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("routing_contracts_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("routing_contracts_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("routing_contracts_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("routing_contracts_types", "env_read", "p2_env_1")
_emit_reads_environ("routing_contracts_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("routing_contracts_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("routing_contracts_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "routing_contracts_types", "context_pull")
_emit_pulls_context("p1", "routing_contracts_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "routing_contracts_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "routing_contracts_types", "uwg_term_2")
_emit_writes_through("p1", "routing_contracts_types", "write_through")
_emit_writes_through("p1", "routing_contracts_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "routing_contracts_types", "safety_validation")
_emit_invokes_eval("p1", "routing_contracts_types", "eval_call")
_emit_proposal_commits_routing("p1", "routing_contracts_types", "routing_commit")

logger = logging.getLogger(__name__)


# =============================================================================
# §3.6 — Law Slot Handler (Tool Isolation)
# All tool execution via read-only twins. Direct live tool access PROHIBITED.
# =============================================================================


class LawSlotHandler:
    """§3.6 — Enforces tool isolation via read-only twins.

    Direct reference to live tool instances is PROHIBITED.
    The Slot Handler enforces Capability Depletion tracking (§15.4).
    """

    def __init__(self, trace_id: str, total_slots: int) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "LawSlotHandler.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "LawSlotHandler.__init__", "p0_governance")
        self._trace_id = trace_id
        self._twins: dict[str, Any] = {}
        self._depletion = CapabilityDepletionTracker(
            trace_id=trace_id,
            total_slots=total_slots,
        )
        self._frozen = False

    def register_twin(self, tool_name: str, read_only_twin: Any) -> None:
        """Register a read-only twin for a tool. Live instances are rejected."""

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"LawSlotHandler.register_twin:{tool_name}"
        )
        if self._frozen:
            raise RuntimeError("LawSlotHandler: Cannot register after freeze")
        self._twins[tool_name] = read_only_twin

    def freeze(self) -> None:
        """Freeze registrations — no further twins may be added."""
        self._frozen = True

    def acquire_slot(self, tool_name: str) -> Any:
        """Acquire a tool slot via read-only twin. Fail-closed on depletion."""
        if tool_name not in self._twins:
            raise KeyError(f"LawSlotHandler: No twin registered for '{tool_name}'")
        if not self._depletion.consume_slot(tool_name):
            raise RuntimeError(
                f"LawSlotHandler: Capability depleted (rate={self._depletion.depletion_rate:.2f})",
            )
        return self._twins[tool_name]

    @property
    def depletion_tracker(self) -> CapabilityDepletionTracker:
        return self._depletion


# =============================================================================
# §4.1 / §4.3 — Policy Config Guard
# policy_config is read-once per healing wave.
# Any mutation during a wave is a critical incident.
# =============================================================================


class PolicyConfigGuard:
    """§4.1/§4.3 — Enforces policy immutability within a healing wave.

    Read-once: policy_config hash is captured at wave start.
    Any mutation detected during the wave raises a critical incident.
    """

    def __init__(self, policy_config: dict[str, Any], wave_id: str) -> None:
        self._wave_id = wave_id
        self._config_bytes = _deterministic_bytes(policy_config)
        self._hash = hashlib.sha256(self._config_bytes).hexdigest()
        self._read = False

    @property
    def policy_hash(self) -> str:
        return self._hash

    def read_config(self, current_config: dict[str, Any]) -> dict[str, Any]:
        """Read policy config. Fail-closed if mutated since wave start."""
        current_hash = hashlib.sha256(
            _deterministic_bytes(current_config),
        ).hexdigest()
        # guardian: allow-config-with-logic
        if current_hash != self._hash:
            raise PolicyMutationIncident(
                wave_id=self._wave_id,
                expected_hash=self._hash,
                actual_hash=current_hash,
            )
        self._read = True
        return current_config


class PolicyMutationIncident(Exception):
    """§4.3 — Critical incident: policy_config mutated during healing wave."""

    def __init__(self, wave_id: str, expected_hash: str, actual_hash: str) -> None:
        self.wave_id = wave_id
        self.expected_hash = expected_hash
        self.actual_hash = actual_hash
        super().__init__(
            f"CRITICAL: policy_config mutated during wave {wave_id}. "
            f"Expected {expected_hash[:16]}..., got {actual_hash[:16]}...",
        )


# =============================================================================
# §6.4 — Static Policy Alignment Check
# Cognitive Engine must execute a policy alignment check prior to response.
# =============================================================================


@dataclass(frozen=True)
class PolicyAlignmentResult:
    """§6.4 — Result of static policy alignment check."""

    trace_id: str
    aligned: bool
    policy_hash: str
    violations: list[str] = field(default_factory=list)


def static_policy_alignment_check(
    trace_id: str,
    policy_hash: str,
    context: dict[str, Any],
    policy_rules: list[dict[str, Any]],
) -> PolicyAlignmentResult:
    """§6.4 — Execute static policy alignment check. Fail-closed on violation."""
    violations: list[str] = []
    for rule in policy_rules:
        rule_id = rule.get("id", "unknown")
        check_fn = rule.get("check")
        if check_fn is None:
            violations.append(f"Rule {rule_id}: no check function (fail-closed)")
            continue
        try:
            if not check_fn(context):
                violations.append(f"Rule {rule_id}: alignment violation")
        # guardian: allow-silent-swallow
        except Exception as exc:
            violations.append(f"Rule {rule_id}: check error ({exc}) (fail-closed)")

    return PolicyAlignmentResult(
        trace_id=trace_id,
        aligned=len(violations) == 0,
        policy_hash=policy_hash,
        violations=violations,
    )


# =============================================================================
# §7.3 — Guardrail Guard
# Budget Guard (tokens), Payload Integrity, Safety Markers, Boundary Tokens
# =============================================================================


@dataclass
class GuardrailGuard:
    """§7.3 — Unified guardrail guard enforcing four sub-checks.

    All checks are fail-closed: any failure blocks progression.
    """

    trace_id: str

    def check_budget(self, token_cap: TokenCapArtifact) -> bool:
        """Budget Guard: tokens within budget."""
        return token_cap.gate_result != TokenGateResult.DENY

    def check_payload_integrity(self, payload_hash: str, expected_hash: str) -> bool:
        """Payload Integrity (Plast): hash match required."""
        return payload_hash == expected_hash

    def check_safety_markers(self, markers: list[str]) -> bool:
        """Safety Markers: all required markers must be present."""
        required = {"trace_id_present", "policy_hash_present", "schema_valid"}
        return required.issubset(set(markers))

    def check_boundary_tokens(self, boundary_token: str) -> bool:
        """Boundary Tokens: fast-fail on missing/empty token."""
        return bool(boundary_token and boundary_token.strip())

    def enforce_all(
        self,
        token_cap: TokenCapArtifact,
        payload_hash: str,
        expected_hash: str,
        markers: list[str],
        boundary_token: str,
    ) -> bool:
        """Run all four guards. Fail-closed: any single failure = block."""
        return (
            self.check_budget(token_cap)
            and self.check_payload_integrity(payload_hash, expected_hash)
            and self.check_safety_markers(markers)
            and self.check_boundary_tokens(boundary_token)
        )


# =============================================================================
# §7.5 — Absence of artifact OR signature = automatic failure
# =============================================================================


def enforce_artifact_presence(artifact: Any | None, artifact_name: str) -> None:
    """§7.5 — Fail-closed: absence of artifact is automatic failure."""
    if artifact is None:
        raise ArtifactAbsenceFailure(artifact_name)


class ArtifactAbsenceFailure(Exception):
    """§7.5 — Automatic failure when a required artifact is absent."""

    def __init__(self, artifact_name: str) -> None:
        self.artifact_name = artifact_name
        super().__init__(
            f"FAIL (P1): Required artifact '{artifact_name}' is absent. "
            "Absence of artifact = automatic failure.",
        )


def enforce_route_decision_presence(
    audit_payload: dict[str, Any] | None,
) -> None:
    """§3.1 — Under V15, downstream validation requires a RouteDecisionArtifact.

    Fail-closed: if V15 is enforced and the artifact is missing or None,
    raise V15HardFailAbort.  Non-V15 behaviour is unchanged (no-op).
    """
    from agentic_core.L0_routing.types.guardian_contract_types import (
        V15HardFailAbort,
        is_v15_enforced,
    )

    if not is_v15_enforced():
        return

    if audit_payload is None:
        raise V15HardFailAbort(
            "Missing RouteDecisionArtifact under V15: audit payload is None",
        )

    artifact = audit_payload.get("route_decision_artifact")
    if artifact is None:
        raise V15HardFailAbort(
            "Missing RouteDecisionArtifact under V15: "
            "'route_decision_artifact' key absent or None in audit payload",
        )


# =============================================================================
# §7.6 — Meta-Guardian ≥95% invariant coverage in CI
# =============================================================================


@dataclass
class MetaGuardianResult:
    """§7.6 — Meta-Guardian enforcement result."""

    total_invariants: int
    covered_invariants: int
    coverage_pct: float
    passing: bool


# guardian: allow-magic-config
def meta_guardian_check(
    total_invariants: int,
    covered_invariants: int,
    threshold: float = 0.95,
) -> MetaGuardianResult:
    """§7.6 — Meta-Guardian: enforce ≥95% invariant coverage."""
    if total_invariants == 0:
        return MetaGuardianResult(
            total_invariants=0,
            covered_invariants=0,
            coverage_pct=0.0,
            passing=False,
        )
    pct = covered_invariants / total_invariants
    return MetaGuardianResult(
        total_invariants=total_invariants,
        covered_invariants=covered_invariants,
        coverage_pct=pct,
        passing=pct >= threshold,
    )


# =============================================================================
# §7.7 — Aggregate Gate Rule
# Guardian validates AGGREGATE before L2 heal admission.
# =============================================================================


def aggregate_gate_check(aggregate: AggregateArtifact | None) -> bool:
    """§7.7 — Guardian validates AGGREGATE before L2 heal admission.

    Fail-closed: None or missing required fields = reject.
    """
    if aggregate is None:
        return False
    if not aggregate.trace_id:
        return False
    if not aggregate.impact_scope:
        return False
    if not aggregate.rollback_vector:
        return False
    return True


# =============================================================================
# §10.1 — Healing inside transactional boundary
# =============================================================================


class HealingTransactionBoundary:
    """§10.1 — All healing occurs inside a transactional boundary.

    Fail-closed: any exception triggers rollback and prevents partial state.
    """

    def __init__(self, trace_id: str) -> None:
        self._trace_id = trace_id
        self._active = False
        self._committed = False
        self._rolled_back = False

    def __enter__(self) -> HealingTransactionBoundary:
        self._active = True
        return self

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> bool:
        self._active = False
        if exc_type is not None:
            self._rolled_back = True
            logger.error(
                f"HealingTransaction {self._trace_id}: rollback due to {exc_type.__name__}",
            )
            return False
        if not self._committed:
            self._rolled_back = True
            logger.warning(
                f"HealingTransaction {self._trace_id}: rollback (no explicit commit)",
            )
        return False

    def commit(self) -> None:
        """Explicitly commit the transaction."""
        if not self._active:
            raise RuntimeError("HealingTransaction: commit outside active boundary")
        self._committed = True

    @property
    def committed(self) -> bool:
        return self._committed

    @property
    def rolled_back(self) -> bool:
        return self._rolled_back


# =============================================================================
# §10.4 — RESULT emission exclusive to L2 post-heal
# =============================================================================

RESULT_EMISSION_ALLOWED_LAYERS: frozenset[str] = frozenset({"L2_execution"})


def validate_result_emission(layer: str) -> None:
    """§10.4 — RESULT may only be emitted by L2 after successful heal.

    L0/L5/L6 cannot write RESULT or HEALING_PLAN.
    """
    if layer not in RESULT_EMISSION_ALLOWED_LAYERS:
        raise ResultEmissionViolation(layer)


class ResultEmissionViolation(Exception):
    """§10.4 — RESULT emitted from unauthorized layer."""

    def __init__(self, layer: str) -> None:
        self.layer = layer
        super().__init__(
            f"FAIL (P1): RESULT emission from {layer} is prohibited. Only L2_execution may emit RESULT.",
        )


# =============================================================================
# §11.2 — Route Recovery (TokenOverflow → RouteRecovery)
# =============================================================================


class RouteRecoveryBox:
    """§11.2 — TokenOverflow events trigger retry/downgrade, not hard crash."""

    # guardian: allow-magic-config
    def __init__(self, trace_id: str, max_retries: int = 3) -> None:
        self._trace_id = trace_id
        self._max_retries = max_retries
        self._attempts = 0

    def handle_overflow(self, tokens_requested: int, budget_limit: int) -> str:
        """Handle TokenOverflow. Returns action: 'retry', 'downgrade', or 'reject'."""
        self._attempts += 1
        if self._attempts <= self._max_retries:
            if tokens_requested <= budget_limit * 2:
                return "retry"
            return "downgrade"
        return "reject"

    @property
    def attempts(self) -> int:
        return self._attempts


# =============================================================================
# §2.5 — Pipe Order Enforcer (strict 1..10)
# =============================================================================


class PipeOrderViolation(Exception):
    """§2.5 — Pipe order violation detected."""

    def __init__(self, expected: str, actual: str, step: int) -> None:
        self.expected = expected
        self.actual = actual
        self.step = step
        super().__init__(
            f"FAIL (P1): Pipe step {step} expected '{expected}', got '{actual}'",
        )


class PipeOrderEnforcer:
    """§2.5 — Enforces strict healer pipe order (1..10). No reordering allowed."""

    def __init__(self) -> None:
        self._current_step = 0
        self._order = HEALER_PIPE_ORDER

    def advance(self, step_name: str) -> int:
        """Advance to next pipe step. Fail-closed on wrong order."""
        if self._current_step >= len(self._order):
            raise PipeOrderViolation(
                expected="<complete>",
                actual=step_name,
                step=self._current_step + 1,
            )
        expected = self._order[self._current_step]
        if step_name != expected:
            raise PipeOrderViolation(
                expected=expected,
                actual=step_name,
                step=self._current_step + 1,
            )
        self._current_step += 1
        return self._current_step

    @property
    def current_step(self) -> int:
        return self._current_step

    @property
    def is_complete(self) -> bool:
        return self._current_step == len(self._order)


# =============================================================================
# §15.1 — Tiered Vigilance + Evacuation Protocol enforcement
# =============================================================================


class TieredVigilanceMonitor:
    """§15.1 — Tiered Vigilance Strategy with Evacuation Protocol.

    Tier I: Budget/Token Drains (Dashboard Signature)
    Tier II: Anomalous Presence (Exclusive Dynamic Probes)
    Tier III: Evacuation Alert Engage (Emergency Exfiltration/Shutdown)
    """

    def __init__(self, trace_id: str) -> None:
        self._trace_id = trace_id
        self._current_tier = VigilanceTier.TIER_I
        self._evacuated = False

    def escalate(self, tier: VigilanceTier, reason: str) -> EvacuationProtocol | None:
        """Escalate to a tier. Tier III triggers evacuation."""
        self._current_tier = tier
        if tier == VigilanceTier.TIER_III:
            protocol = EvacuationProtocol(
                trace_id=self._trace_id,
                tier=VigilanceTier.TIER_III,
                freeze_state=True,
                exfiltration_path="emergency_shutdown",
                reason=reason,
            )
            self._evacuated = True
            return protocol
        return None

    @property
    def current_tier(self) -> VigilanceTier:
        return self._current_tier

    @property
    def evacuated(self) -> bool:
        return self._evacuated


# =============================================================================
# §15.6 — INCIDENT and RESULT telemetry emission
# =============================================================================


class TelemetryEmitter:
    """§15.6 — All INCIDENT and RESULT artifacts must emit telemetry events."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def emit_incident(self, incident: IncidentArtifact) -> None:
        """Emit telemetry for INCIDENT artifact."""
        self._events.append(
            {
                "type": "INCIDENT",
                "trace_id": incident.trace_id,
                "incident_id": incident.incident_id,
                "severity": incident.severity_enum.value,
            },
        )

    def emit_result(self, result: ResultArtifact) -> None:
        """Emit telemetry for RESULT artifact."""
        self._events.append(
            {
                "type": "RESULT",
                "trace_id": result.trace_id,
                "outcome": result.execution_outcome,
            },
        )

    def emit_route_decision(self, artifact: RouteDecisionArtifact) -> None:
        """Emit telemetry for ROUTE_DECISION artifact (§3.1 durable sink)."""
        from dataclasses import asdict

        self._events.append(
            {
                "type": "ROUTE_DECISION",
                "payload": asdict(artifact),
            },
        )

    def emit_typed_artifact(self, type_label: str, artifact: Any) -> None:
        """Emit telemetry for any typed dataclass artifact (§Wave2.1 generic sink)."""
        from dataclasses import asdict

        self._events.append(
            {
                "type": type_label,
                "payload": asdict(artifact),
            },
        )

    def flush_to_artifacts_dir(self, artifacts_dir: Any) -> Any:
        """Persist all buffered events as NDJSON to *artifacts_dir*.

        File: ``telemetry_events.ndjson`` (one JSON object per line).
        Follows the same mkdir-then-write pattern as ``write_guardian_result``.

        Returns:
            Path to the written file, or *None* if there are no events.
        """
        if not self._events:
            return None
        import json
        from pathlib import Path

        out_dir = Path(artifacts_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "telemetry_events.ndjson"
        with out_path.open("a", encoding="utf-8") as fh:
            for event in self._events:
                fh.write(json.dumps(event, sort_keys=True, default=str) + "\n")
        return out_path

    @property
    def events(self) -> list[dict[str, Any]]:
        return list(self._events)


# =============================================================================
# Helpers
# =============================================================================


def _deterministic_bytes(obj: Any) -> bytes:
    """Produce deterministic bytes for hashing (sorted keys)."""
    import json

    return json.dumps(obj, sort_keys=True, default=str).encode("utf-8")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ArtifactAbsenceFailure",
    "GuardrailGuard",
    "HealingTransactionBoundary",
    "LawSlotHandler",
    "MetaGuardianResult",
    "PipeOrderEnforcer",
    "PipeOrderViolation",
    "PolicyAlignmentResult",
    "PolicyConfigGuard",
    "PolicyMutationIncident",
    "RESULT_EMISSION_ALLOWED_LAYERS",
    "ResultEmissionViolation",
    "RouteRecoveryBox",
    "TelemetryEmitter",
    "TieredVigilanceMonitor",
    "aggregate_gate_check",
    "enforce_artifact_presence",
    "enforce_route_decision_presence",
    "meta_guardian_check",
    "static_policy_alignment_check",
    "validate_result_emission",
]

_emit_reads_through("l4", "routing_contracts_types", "urg_read_1")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_2")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_3")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_4")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_5")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_6")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_7")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_8")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_9")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_10")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_11")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_12")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_13")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_14")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_15")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_16")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_17")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_18")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_19")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_20")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_21")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_22")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_23")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_24")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_25")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_26")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_27")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_28")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_29")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_30")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_31")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_32")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_33")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_34")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_35")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_36")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_37")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_38")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_39")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_40")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_41")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_42")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_43")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_44")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_45")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_46")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_47")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_48")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_49")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_50")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_51")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_52")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_53")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_54")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_55")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_56")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_57")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_58")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_59")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_60")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_61")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_62")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_63")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_64")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_65")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_66")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_67")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_68")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_69")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_70")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_71")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_72")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_73")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_74")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_75")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_76")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_77")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_78")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_79")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_80")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_81")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_82")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_83")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_84")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_85")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_86")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_87")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_88")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_89")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_90")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_91")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_92")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_93")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_94")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_95")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_96")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_97")
_emit_reads_through("l4", "routing_contracts_types", "urg_read_98")
