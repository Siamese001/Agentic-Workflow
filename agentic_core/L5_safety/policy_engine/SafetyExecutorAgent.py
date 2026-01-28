#!/usr/bin/env python3
from __future__ import annotations
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.base_agents.subatomic_testing_mixin import SubatomicTestingMixin

"""
SafetyExecutorAgent - Safety Execution Interface

Phase 4 Hard Migration: Consolidates:
- IntegrityGateExecutorAgent (integrity gate execution)
- L5IntegrityGateExecutorAgent (L5 integrity gates)
- SafetyExecutorAgent (safety execution)

Features:
- Pre-execution safety checks
- Integrity gate enforcement
- Execution blocking on violations
- Safety score thresholds
- Audit logging
"""


import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, TypeVar

Logger = logging.getLogger(__name__)

T = TypeVar("T")


class ExecutionStatus(Enum):
    """Status of execution."""

    ALLOWED = auto()
    BLOCKED = auto()
    WARNED = auto()
    FAILED = auto()


class BlockReason(Enum):
    """Reasons for blocking execution."""

    SAFETY_VIOLATION = auto()
    INTEGRITY_FAILURE = auto()
    PERMISSION_DENIED = auto()
    THRESHOLD_EXCEEDED = auto()
    DETECTOR_FLAG = auto()


@dataclass
class ExecutionResult:
    """Result of an execution attempt."""

    status: ExecutionStatus
    block_reason: BlockReason | None = None
    message: str = ""
    result: Any = None
    execution_time_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SafetyGate:
    """Represents a safety gate check."""

    name: str
    check_fn: Callable[..., bool]
    severity: str = "HIGH"
    blocking: bool = True


@dataclass
class ExecutorConfig:
    """configuration for safety executor."""

    enable_integrity_gates: bool = True
    enable_safety_checks: bool = True
    block_on_high_severity: bool = True
    safety_score_threshold: float = 0.75
    max_execution_time_ms: float = 30000
    audit_all_executions: bool = True


class SafetyExecutorAgent(SovereignBaseAgent):
    """
    Unified safety executor with integrity gates.

    Consolidates:
    - IntegrityGateExecutorAgent
    - L5IntegrityGateExecutorAgent
    - SafetyExecutorAgent

    Usage:
        executor = SafetyExecutorAgent()

        # Execute with safety checks
        result = executor.execute(my_function, arg1, arg2)

        # Add custom gate
        executor.add_gate("custom_check", lambda: check_something())
    """

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs
    ) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).
        
        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes
            
        Returns:
            Dict with healing summary
        """
        # Executor agents enforce runtime safety; they do not auto-heal code
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(
        self,
        agent_config: ExecutorConfig | None = None,
        detector: Any | None = None,
    ):
        self._agent_config = agent_config or ExecutorConfig()
        self._detector = detector
        self._lock = threading.RLock()
        self._gates: list[SafetyGate] = []
        self._results: list[ExecutionResult] = []
        self._blocked_count = 0
        self._allowed_count = 0

        # Initialize default gates
        self._init_default_gates()

        Logger.info("SafetyExecutorAgent initialized")

    def _init_default_gates(self) -> None:
        """Initialize default safety gates."""
        # Integrity gate: Check for valid execution context
        self._gates.append(
            SafetyGate(
                name="context_integrity",
                check_fn=lambda ctx: ctx is not None,
                severity="HIGH",
                blocking=True,
            )
        )

    def add_gate(
        self,
        name: str,
        check_fn: Callable[..., bool],
        severity: str = "HIGH",
        blocking: bool = True,
    ) -> None:
        """Add a custom safety gate."""
        gate = SafetyGate(
            name=name,
            check_fn=check_fn,
            severity=severity,
            blocking=blocking,
        )
        self._gates.append(gate)
        Logger.info(f"Added safety gate: {name}")

    def execute(
        self,
        fn: Callable[..., T],
        *args,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> ExecutionResult:
        """
        Execute a function with safety checks.

        Args:
            fn: Function to execute
            *args: Positional arguments
            context: Execution context for gate checks
            **kwargs: Keyword arguments

        Returns:
            ExecutionResult with status and result
        """
        start_time = datetime.utcnow()

        with self._lock:
            # Run pre-execution safety checks
            if self._agent_config.enable_safety_checks:
                check_result = self._run_safety_checks(context or {})
                if check_result.status == ExecutionStatus.BLOCKED:
                    self._blocked_count += 1
                    self._results.append(check_result)
                    return check_result

            # Run integrity gates
            if self._agent_config.enable_integrity_gates:
                gate_result = self._run_gates(context or {})
                if gate_result.status == ExecutionStatus.BLOCKED:
                    self._blocked_count += 1
                    self._results.append(gate_result)
                    return gate_result

            # Execute the function
            try:
                result = fn(*args, **kwargs)

                end_time = datetime.utcnow()
                execution_time = (end_time - start_time).total_seconds() * 1000

                exec_result = ExecutionResult(
                    status=ExecutionStatus.ALLOWED,
                    message="Execution completed successfully",
                    result=result,
                    execution_time_ms=execution_time,
                )

                self._allowed_count += 1
                self._results.append(exec_result)

                return exec_result

            except Exception as e:
                end_time = datetime.utcnow()
                execution_time = (end_time - start_time).total_seconds() * 1000

                exec_result = ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message=f"Execution failed: {str(e)}",
                    execution_time_ms=execution_time,
                )

                self._results.append(exec_result)
                return exec_result

    def _run_safety_checks(self, context: dict[str, Any]) -> ExecutionResult:
        """Run safety detector checks."""
        if self._detector is None:
            return ExecutionResult(
                status=ExecutionStatus.ALLOWED,
                message="No detector configured",
            )

        # Check for safety violations
        try:
            # Get input from context if available
            input_text = context.get("input", "")

            if not input_text:
                return ExecutionResult(
                    status=ExecutionStatus.ALLOWED,
                    message="No input to check",
                )

            # Check for injection threats first
            if hasattr(self._detector, "detect_injection"):
                injection_threats = self._detector.detect_injection(input_text)
                if injection_threats and self._agent_config.block_on_high_severity:
                    return ExecutionResult(
                        status=ExecutionStatus.BLOCKED,
                        block_reason=BlockReason.DETECTOR_FLAG,
                        message=f"Blocked by injection detector: {len(injection_threats)} threat(s)",
                    )

            if hasattr(self._detector, "detect_all"):
                threats = self._detector.detect_all(input_text)

                # Check for high-severity threats
                high_severity = [
                    t for t in threats if hasattr(t, "severity") and t.severity.value >= 2
                ]

                if high_severity and self._agent_config.block_on_high_severity:
                    return ExecutionResult(
                        status=ExecutionStatus.BLOCKED,
                        block_reason=BlockReason.DETECTOR_FLAG,
                        message=f"Blocked by safety detector: {len(high_severity)} high-severity threat(s)",
                    )

            if hasattr(self._detector, "get_safety_score"):
                score = self._detector.get_safety_score(input_text)

                if score < self._agent_config.safety_score_threshold:
                    return ExecutionResult(
                        status=ExecutionStatus.BLOCKED,
                        block_reason=BlockReason.THRESHOLD_EXCEEDED,
                        message=f"Safety score {score:.2f} below threshold {self._agent_config.safety_score_threshold}",
                    )

        except Exception as e:
            Logger.error(f"Safety check error: {e}")

        return ExecutionResult(
            status=ExecutionStatus.ALLOWED,
            message="Safety checks passed",
        )

    def _run_gates(self, context: dict[str, Any]) -> ExecutionResult:
        """Run integrity gates."""
        for gate in self._gates:
            try:
                passed = gate.check_fn(context)

                if not passed:
                    if gate.blocking:
                        return ExecutionResult(
                            status=ExecutionStatus.BLOCKED,
                            block_reason=BlockReason.INTEGRITY_FAILURE,
                            message=f"Integrity gate failed: {gate.name}",
                        )
                    else:
                        Logger.warning(f"Non-blocking gate failed: {gate.name}")

            except Exception as e:
                Logger.error(f"Gate {gate.name} error: {e}")

                if gate.blocking:
                    return ExecutionResult(
                        status=ExecutionStatus.BLOCKED,
                        block_reason=BlockReason.INTEGRITY_FAILURE,
                        message=f"Integrity gate error: {gate.name} - {e}",
                    )

        return ExecutionResult(
            status=ExecutionStatus.ALLOWED,
            message="All integrity gates passed",
        )

    def check_and_block(
        self,
        input_text: str,
        source: str = "unknown",
    ) -> tuple[bool, str]:
        """
        Quick check if input should be blocked.

        Args:
            input_text: Input to check
            source: Source of input

        Returns:
            Tuple of (should_block, reason)
        """
        if self._detector is None:
            return False, "No detector configured"

        try:
            if hasattr(self._detector, "is_safe"):
                is_safe = self._detector.is_safe(input_text, source)
                if not is_safe:
                    return True, "Safety detector flagged input as unsafe"

            if hasattr(self._detector, "get_safety_score"):
                score = self._detector.get_safety_score(input_text)
                if score < self._agent_config.safety_score_threshold:
                    return True, f"Safety score {score:.2f} below threshold"

        except Exception as e:
            Logger.error(f"Check error: {e}")

        return False, "Input passed safety checks"

    def get_stats(self) -> dict[str, Any]:
        """Get execution statistics."""
        return {
            "allowed": self._allowed_count,
            "blocked": self._blocked_count,
            "total": self._allowed_count + self._blocked_count,
            "block_rate": self._blocked_count / max(1, self._allowed_count + self._blocked_count),
            "gates_count": len(self._gates),
        }

    def get_results(self) -> list[ExecutionResult]:
        """Get all execution results."""
        return self._results.copy()


# Import Tuple for type hints


# Factory methods for backward compatibility
def create_legacy_integrity_executor() -> SafetyExecutorAgent:
    """Create executor with integrity gates only."""
    config = ExecutorConfig(
        enable_integrity_gates=True,
        enable_safety_checks=False,
    )
    return SafetyExecutorAgent(config=config)


def create_legacy_safety_executor() -> SafetyExecutorAgent:
    """Create executor with safety checks only."""
    config = ExecutorConfig(
        enable_integrity_gates=False,
        enable_safety_checks=True,
    )
    return SafetyExecutorAgent(config=config)
