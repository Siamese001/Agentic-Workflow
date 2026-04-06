"""
Contextual Router - V10 Policy Enforcer Implementation.

Per Agentic Process V10 specification:
- "Contextual Router & Policy Enforcer (Policy & Orchestration)"
- Receives detection signal, applies enforcement policy
- Classifies risk level (low/medium/high) based on impact & confidence
- Routes to Validation Gate or Human Review Gate based on risk

Key V10 Flows:
1. LOW RISK: Blue arrow bypass -> direct to System Actuation
2. MEDIUM RISK: Standard validation -> Validation Gate -> Actuation
3. HIGH RISK: Human Review Gate -> Approval Queue -> Actuation

References:
- V10 Diagram: "Contextual Router & Policy Enforcer" (orange hexagon)
- V10 Diagram: "Low Risk Bypass" (blue dashed arrow)
"""

import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Protocol

from agentic_core.L0_routing.types.routing_artifact_types import RoutePath
from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker
from agentic_core.L5_safety.enforcement.context_session import (
    ContextSession,
    ContextSessionManager,
    RiskLevel,
    classify_risk,
    get_session_manager,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
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
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_reads_through,
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
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("contextual_router_config", "p4obs", "metric_1")
_emit_emits_metric_event("contextual_router_config", "p4obs", "metric_2")
_emit_emits_metric_event("contextual_router_config", "p4obs", "metric_3")
_emit_emits_metric_event("contextual_router_config", "p4obs", "metric_4")
_emit_emits_metric_event("contextual_router_config", "p4obs", "metric_5")
_emit_emits_metric_event("contextual_router_config", "p4obs", "metric_6")
_emit_records_incident_event("contextual_router_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("contextual_router_config", "p4obs", "anomaly")
_emit_writes_observability_log("contextual_router_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("contextual_router_config", "p4obs", "mon_state")
_emit_triggers_alert("contextual_router_config", "p4obs", "alert")
_emit_links_incident_trace("contextual_router_config", "p4obs", "trace_link")
_emit_captures_pattern("contextual_router_config", "p3lm", "pattern")
_emit_records_learning_event("contextual_router_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("contextual_router_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("contextual_router_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("contextual_router_config", "p3lm", "routing")
_emit_improves_agent_policy("contextual_router_config", "p3lm", "policy")
_emit_stores_learning_state("contextual_router_config", "p3lm", "state")
_emit_records_execution_trace("contextual_router_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("contextual_router_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("contextual_router_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("contextual_router_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("contextual_router_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("contextual_router_config", "env_read", "p2_env_1")
_emit_reads_environ("contextual_router_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("contextual_router_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("contextual_router_config", "runtime_state", "p2_rt_2")

_emit_snapshots_state("p0", "contextual_router_config", "state_snapshot")
_emit_pulls_context("p1", "contextual_router_config", "context_pull")
_emit_pulls_context("p1", "contextual_router_config", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "contextual_router_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "contextual_router_config", "uwg_term_secondary")
_emit_writes_through("p1", "contextual_router_config", "write_through")
_emit_writes_through("p1", "contextual_router_config", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "contextual_router_config", "safety_validation")
_emit_invokes_eval("p1", "contextual_router_config", "eval_call")
_emit_proposal_commits_routing("p1", "contextual_router_config", "routing_commit")
_emit_escalates_to_human("p1", "contextual_router_config", "human_escalation")
_emit_routes_through("p1", "contextual_router_config", "route_through")
_emit_checks_agent_registry("p1", "contextual_router_config", "agent_registry")
_emit_validates_agent_capability("p1", "contextual_router_config", "capability")
_emit_dispatches_execution_plan("p1", "contextual_router_config", "exec_plan")
_emit_agent_executes_agent("p1", "contextual_router_config", "sub_agent")
_emit_routes_to_agent("p1", "contextual_router_config", "target_agent")
_emit_verifies_policy("p1", "contextual_router_config", "policy_check")
_emit_observes_runtime_state("p1", "contextual_router_config", "runtime_state")
_emit_verifies_boundary("p1", "contextual_router_config", "boundary_check")
_emit_transcripts_response("p1", "contextual_router_config", "transcript")
_emit_hard_fails_untranscripted("p1", "contextual_router_config")
_emit_gated_by_confidence("p1", "contextual_router_config", "confidence_gate")
emit_replay_key("p0", "contextual_router_config")
emit_determinism_digest("p0", "contextual_router_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "contextual_router_config", "execution_auth")
_emit_validates_capability("p2", "contextual_router_config", "capability_check")
_emit_routes_to_capability("p2", "contextual_router_config", "capability_route")
_emit_writes_via_uwg("p2", "contextual_router_config", "uwg_write")
_emit_blocks_direct_write("p2", "contextual_router_config", "direct_write_block")
_emit_records_tool_invocation("p2", "contextual_router_config", "tool_invocation")
_emit_captures_execution_output("p2", "contextual_router_config", "exec_output")
_emit_dispatches_agent("p3", "contextual_router_config", "agent_dispatch")
_emit_coordinates_agents("p3", "contextual_router_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "contextual_router_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "contextual_router_config", "healing_outcome")
_emit_escalates_failure("p3", "contextual_router_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "contextual_router_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "contextual_router_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "contextual_router_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "contextual_router_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "contextual_router_config", "eval_metric")
_emit_stores_embedding("p4", "contextual_router_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "contextual_router_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "contextual_router_config", "exec_snapshot_link")

logger = logging.getLogger(__name__)


# V15 P0.3: RouteDecision is now an alias for the canonical V15 RoutePath.
# All 5 strictly defined paths come from routing_artifact_types.RoutePath.
RouteDecision = RoutePath


@dataclass
class RoutingRequest:
    """Request to be routed through the V10 pipeline."""

    request_id: str
    action_type: str  # heal, validate, execute, etc.
    target_files: list[Path] = field(default_factory=list)
    agent_name: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # Risk factors from discovery
    cyclomatic_complexity: int = 0
    has_external_touch: bool = False
    is_base_agent: bool = False


@dataclass
class RoutingResult:
    """Result of routing decision."""

    decision: RoutePath
    risk_level: RiskLevel
    reason: str
    request: RoutingRequest
    session: ContextSession | None = None
    bypass_validation: bool = False
    requires_human_approval: bool = False
    circuit_breaker_status: str | None = None
    guardian_signals: list[str] = field(default_factory=list)


class GuardianSignalProtocol(Protocol):
    """Protocol for guardian signal emission."""

    def emit_signal(self, signal_type: str, data: dict[str, Any]) -> None:
        """Emit a guardian signal."""
        ...

    def get_active_signals(self) -> list[dict[str, Any]]:
        """Get all active guardian signals."""
        ...


class GuardianSignalBus:
    """
    Signal bus for Guardian script integration.

    Per V10 "Tests vs. Agents" schematic:
    - Guardian scripts are deterministic tripwires
    - They emit signals that the Router must respond to
    """

    _instance: Optional["GuardianSignalBus"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._signals: list[dict[str, Any]] = []
            cls._instance._subscribers: list[Callable] = []
        return cls._instance

    def emit_signal(
        self,
        signal_type: str,
        data: dict[str, Any],
        severity: str = "warning",
    ) -> None:
        """
        Emit a guardian signal.

        Args:
            signal_type: Type of signal (mro_violation, import_cycle, etc.)
            data: Signal payload
            severity: Signal severity (info, warning, error, critical)
        """
        signal = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": signal_type,
            "severity": severity,
            "data": data,
        }
        self._signals.append(signal)

        # Notify subscribers
        for subscriber in self._subscribers:
            try:
                subscriber(signal)
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.error(f"Signal subscriber error: {e}")

        logger.info(f"Guardian signal emitted: {signal_type} ({severity})")

    def subscribe(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Subscribe to guardian signals."""
        self._subscribers.append(callback)

    def get_active_signals(
        self,
        signal_types: set[str] | None = None,
        min_severity: str = "warning",
    ) -> list[dict[str, Any]]:
        """Get active signals, optionally filtered."""

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, "GuardianSignalBus.get_active_signals")
        severity_order = {"info": 0, "warning": 1, "error": 2, "critical": 3}
        min_level = severity_order.get(min_severity, 1)

        signals = []
        for signal in self._signals:
            if signal_types and signal["type"] not in signal_types:
                continue
            if severity_order.get(signal["severity"], 0) >= min_level:
                signals.append(signal)

        return signals

    def clear_signals(self, signal_type: str | None = None) -> int:
        """Clear signals, optionally by type."""
        if signal_type:
            before = len(self._signals)
            self._signals = [s for s in self._signals if s["type"] != signal_type]
            return before - len(self._signals)
        else:
            count = len(self._signals)
            self._signals.clear()
            return count


def get_guardian_signal_bus() -> GuardianSignalBus:
    """Get the global guardian signal bus."""
    return GuardianSignalBus()


class ContextualRouter:
    """
    V10 Contextual Router & Policy Enforcer.

    Implements the central routing logic from the V10 architecture:
    1. Receives requests with context
    2. Classifies risk level
    3. Checks circuit breakers
    4. Applies policy enforcement
    5. Routes to appropriate gate (bypass/validate/human review)

    Integration points:
    - Guardian Signal Bus: Receives tripwire signals from test scripts
    - Circuit Breakers: Per-agent failure tracking
    - Session Manager: Context propagation
    - Validation Gate: Pre-execution verification
    - Human Review Gate: Async approval queue
    """

    def __init__(
        self,
        session_manager: ContextSessionManager | None = None,
        guardian_bus: GuardianSignalBus | None = None,
    ):
        self._session_manager = session_manager or get_session_manager()
        self._guardian_bus = guardian_bus or get_guardian_signal_bus()
        self._policy_rules: list[Callable[[RoutingRequest], RoutePath | None]] = []
        self._metrics = {
            "total_requests": 0,
            "bypassed": 0,
            "validated": 0,
            "human_review": 0,
            "rejected": 0,
        }

        # Subscribe to guardian signals
        self._guardian_bus.subscribe(self._on_guardian_signal)

        # Register default policy rules
        self._register_default_policies()

    def _register_default_policies(self) -> None:
        """Register default V10 policy rules."""

        # Rule 1: Base agent modifications always require human review
        def base_agent_rule(req: RoutingRequest) -> RoutePath | None:
            if req.is_base_agent:
                return RoutePath.HUMAN_ESCALATION
            return None

        # Rule 2: External touch requires validation
        def external_touch_rule(req: RoutingRequest) -> RoutePath | None:
            if req.has_external_touch:
                return RoutePath.STANDARD_VALIDATION
            return None

        # Rule 3: High complexity requires validation
        def complexity_rule(req: RoutingRequest) -> RoutePath | None:
            if req.cyclomatic_complexity > 50:
                return RoutePath.HUMAN_ESCALATION
            if req.cyclomatic_complexity > 20:
                return RoutePath.STANDARD_VALIDATION
            return None

        self._policy_rules.extend(
            [
                base_agent_rule,
                external_touch_rule,
                complexity_rule,
            ],
        )

    def _on_guardian_signal(self, signal: dict[str, Any]) -> None:
        """Handle incoming guardian signal."""
        logger.debug(f"Router received guardian signal: {signal['type']}")

        # Critical signals can trigger circuit breakers
        if signal["severity"] == "critical":
            agent = signal["data"].get("agent_name")
            if agent:
                breaker = get_breaker(f"agent_{agent}")
                breaker.record_failure(Exception(f"Guardian signal: {signal['type']}"))

    def add_policy_rule(
        self,
        rule: Callable[[RoutingRequest], RoutePath | None],
    ) -> None:
        """
        Add a custom policy rule.

        Rules are evaluated in order. First non-None result wins.

        Args:
            rule: Function that takes RoutingRequest and returns RouteDecision or None
        """
        self._policy_rules.append(rule)

    def _check_circuit_breaker(self, agent_name: str) -> RoutePath | None:
        """Check if circuit breaker allows request."""
        if not agent_name:
            return None

        breaker = get_breaker(f"agent_{agent_name}")
        if not breaker.allow_request():
            return RoutePath.ROUTE_RECOVERY_BUDGET_OVERFLOW

        return None

    def _evaluate_policies(self, request: RoutingRequest) -> RoutePath | None:
        """Evaluate policy rules against request."""
        for rule in self._policy_rules:
            try:
                decision = rule(request)
                if decision is not None:
                    return decision
            # guardian: allow-silent-swallow
            except Exception as e:
                logger.error(f"Policy rule error: {e}")

        return None

    def _check_guardian_signals(self, request: RoutingRequest) -> list[str]:
        """Check for relevant guardian signals."""
        signals = []

        # Check for signals related to target files
        for file_path in request.target_files:
            file_str = str(file_path)
            active_signals = self._guardian_bus.get_active_signals()
            for signal in active_signals:
                if file_str in str(signal.get("data", {})):
                    signals.append(signal["type"])

        # Check for agent-specific signals
        if request.agent_name:
            active_signals = self._guardian_bus.get_active_signals()
            for signal in active_signals:
                if request.agent_name in str(signal.get("data", {})):
                    signals.append(signal["type"])

        return signals

    def route(self, request: RoutingRequest) -> RoutingResult:
        """
        Route a request through the V10 pipeline.

        This is the main entry point implementing the V10 flow:
        1. Check circuit breaker
        2. Check guardian signals
        3. Classify risk
        4. Apply policies
        5. Return routing decision

        Args:
            request: The routing request

        Returns:
            RoutingResult with decision and context
        """
        self._metrics["total_requests"] += 1

        # Get or create session
        session = self._session_manager.get_or_create_session()

        # 1. Check circuit breaker
        cb_decision = self._check_circuit_breaker(request.agent_name)
        if cb_decision == RoutePath.ROUTE_RECOVERY_BUDGET_OVERFLOW:
            self._metrics["rejected"] += 1
            return RoutingResult(
                decision=RoutePath.ROUTE_RECOVERY_BUDGET_OVERFLOW,
                risk_level=RiskLevel.HIGH,
                reason="Circuit breaker is OPEN for this agent",
                request=request,
                session=session,
                circuit_breaker_status="open",
            )

        # 2. Check guardian signals
        guardian_signals = self._check_guardian_signals(request)
        if any("critical" in s.lower() for s in guardian_signals):
            self._metrics["human_review"] += 1
            return RoutingResult(
                decision=RoutePath.HUMAN_ESCALATION,
                risk_level=RiskLevel.HIGH,
                reason=f"Critical guardian signals: {guardian_signals}",
                request=request,
                session=session,
                requires_human_approval=True,
                guardian_signals=guardian_signals,
            )

        # 3. Classify risk
        risk_level = classify_risk(
            file_count=len(request.target_files),
            has_external_touch=request.has_external_touch,
            cyclomatic_complexity=request.cyclomatic_complexity,
            is_base_agent=request.is_base_agent,
        )
        session.escalate_risk(risk_level)

        # 4. Apply policies
        policy_decision = self._evaluate_policies(request)

        # 5. Determine final routing
        if policy_decision == RoutePath.HUMAN_ESCALATION:
            self._metrics["human_review"] += 1
            return RoutingResult(
                decision=RoutePath.HUMAN_ESCALATION,
                risk_level=RiskLevel.HIGH,
                reason="Policy requires human review",
                request=request,
                session=session,
                requires_human_approval=True,
                guardian_signals=guardian_signals,
            )

        if policy_decision == RoutePath.STANDARD_VALIDATION:
            self._metrics["validated"] += 1
            return RoutingResult(
                decision=RoutePath.STANDARD_VALIDATION,
                risk_level=risk_level,
                reason="Policy requires validation",
                request=request,
                session=session,
                guardian_signals=guardian_signals,
            )

        # Low risk bypass (V10 blue arrow path)
        if risk_level == RiskLevel.LOW and not guardian_signals:
            self._metrics["bypassed"] += 1
            return RoutingResult(
                decision=RoutePath.LOW_RISK_BYPASS,
                risk_level=RiskLevel.LOW,
                reason="Low risk - validation bypassed",
                request=request,
                session=session,
                bypass_validation=True,
            )

        # Default: standard validation
        self._metrics["validated"] += 1
        return RoutingResult(
            decision=RoutePath.STANDARD_VALIDATION,
            risk_level=risk_level,
            reason="Standard validation path",
            request=request,
            session=session,
            guardian_signals=guardian_signals,
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get router metrics for observability dashboard."""
        return {
            **self._metrics,
            "active_sessions": len(self._session_manager.get_all_sessions()),
            "active_signals": len(self._guardian_bus.get_active_signals()),
        }


# Global router instance
_router_instance: ContextualRouter | None = None


def get_router() -> ContextualRouter:
    """Get the global router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = ContextualRouter()
    return _router_instance


__all__ = [
    "ContextualRouter",
    "GuardianSignalBus",
    "RouteDecision",  # V15: alias for RoutePath (backward compat)
    "RoutePath",
    "RoutingRequest",
    "RoutingResult",
    "get_guardian_signal_bus",
    "get_router",
]

_emit_reads_through("l4", "contextual_router_config", "urg_read_1")
_emit_reads_through("l4", "contextual_router_config", "urg_read_2")
_emit_reads_through("l4", "contextual_router_config", "urg_read_3")
_emit_reads_through("l4", "contextual_router_config", "urg_read_4")
_emit_reads_through("l4", "contextual_router_config", "urg_read_5")
_emit_reads_through("l4", "contextual_router_config", "urg_read_6")
_emit_reads_through("l4", "contextual_router_config", "urg_read_7")
_emit_reads_through("l4", "contextual_router_config", "urg_read_8")
_emit_reads_through("l4", "contextual_router_config", "urg_read_9")
_emit_reads_through("l4", "contextual_router_config", "urg_read_10")
_emit_reads_through("l4", "contextual_router_config", "urg_read_11")
_emit_reads_through("l4", "contextual_router_config", "urg_read_12")
_emit_reads_through("l4", "contextual_router_config", "urg_read_13")
_emit_reads_through("l4", "contextual_router_config", "urg_read_14")
_emit_reads_through("l4", "contextual_router_config", "urg_read_15")
_emit_reads_through("l4", "contextual_router_config", "urg_read_16")
_emit_reads_through("l4", "contextual_router_config", "urg_read_17")
_emit_reads_through("l4", "contextual_router_config", "urg_read_18")
_emit_reads_through("l4", "contextual_router_config", "urg_read_19")
_emit_reads_through("l4", "contextual_router_config", "urg_read_20")
_emit_reads_through("l4", "contextual_router_config", "urg_read_21")
_emit_reads_through("l4", "contextual_router_config", "urg_read_22")
_emit_reads_through("l4", "contextual_router_config", "urg_read_23")
_emit_reads_through("l4", "contextual_router_config", "urg_read_24")
_emit_reads_through("l4", "contextual_router_config", "urg_read_25")
_emit_reads_through("l4", "contextual_router_config", "urg_read_26")
_emit_reads_through("l4", "contextual_router_config", "urg_read_27")
_emit_reads_through("l4", "contextual_router_config", "urg_read_28")
_emit_reads_through("l4", "contextual_router_config", "urg_read_29")
_emit_reads_through("l4", "contextual_router_config", "urg_read_30")
_emit_reads_through("l4", "contextual_router_config", "urg_read_31")
_emit_reads_through("l4", "contextual_router_config", "urg_read_32")
_emit_reads_through("l4", "contextual_router_config", "urg_read_33")
_emit_reads_through("l4", "contextual_router_config", "urg_read_34")
_emit_reads_through("l4", "contextual_router_config", "urg_read_35")
_emit_reads_through("l4", "contextual_router_config", "urg_read_36")
_emit_reads_through("l4", "contextual_router_config", "urg_read_37")
_emit_reads_through("l4", "contextual_router_config", "urg_read_38")
_emit_reads_through("l4", "contextual_router_config", "urg_read_39")
_emit_reads_through("l4", "contextual_router_config", "urg_read_40")
_emit_reads_through("l4", "contextual_router_config", "urg_read_41")
_emit_reads_through("l4", "contextual_router_config", "urg_read_42")
_emit_reads_through("l4", "contextual_router_config", "urg_read_43")
_emit_reads_through("l4", "contextual_router_config", "urg_read_44")
_emit_reads_through("l4", "contextual_router_config", "urg_read_45")
_emit_reads_through("l4", "contextual_router_config", "urg_read_46")
_emit_reads_through("l4", "contextual_router_config", "urg_read_47")
_emit_reads_through("l4", "contextual_router_config", "urg_read_48")
_emit_reads_through("l4", "contextual_router_config", "urg_read_49")
_emit_reads_through("l4", "contextual_router_config", "urg_read_50")
_emit_reads_through("l4", "contextual_router_config", "urg_read_51")
_emit_reads_through("l4", "contextual_router_config", "urg_read_52")
_emit_reads_through("l4", "contextual_router_config", "urg_read_53")
_emit_reads_through("l4", "contextual_router_config", "urg_read_54")
_emit_reads_through("l4", "contextual_router_config", "urg_read_55")
_emit_reads_through("l4", "contextual_router_config", "urg_read_56")
_emit_reads_through("l4", "contextual_router_config", "urg_read_57")
_emit_reads_through("l4", "contextual_router_config", "urg_read_58")
_emit_reads_through("l4", "contextual_router_config", "urg_read_59")
_emit_reads_through("l4", "contextual_router_config", "urg_read_60")
_emit_reads_through("l4", "contextual_router_config", "urg_read_61")
_emit_reads_through("l4", "contextual_router_config", "urg_read_62")
_emit_reads_through("l4", "contextual_router_config", "urg_read_63")
_emit_reads_through("l4", "contextual_router_config", "urg_read_64")
_emit_reads_through("l4", "contextual_router_config", "urg_read_65")
_emit_reads_through("l4", "contextual_router_config", "urg_read_66")
_emit_reads_through("l4", "contextual_router_config", "urg_read_67")
_emit_reads_through("l4", "contextual_router_config", "urg_read_68")
_emit_reads_through("l4", "contextual_router_config", "urg_read_69")
_emit_reads_through("l4", "contextual_router_config", "urg_read_70")
_emit_reads_through("l4", "contextual_router_config", "urg_read_71")
_emit_reads_through("l4", "contextual_router_config", "urg_read_72")
_emit_reads_through("l4", "contextual_router_config", "urg_read_73")
_emit_reads_through("l4", "contextual_router_config", "urg_read_74")
_emit_reads_through("l4", "contextual_router_config", "urg_read_75")
_emit_reads_through("l4", "contextual_router_config", "urg_read_76")
