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
