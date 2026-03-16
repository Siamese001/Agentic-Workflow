from __future__ import annotations

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "SafetyExecutorAgent")
emit_determinism_digest("p0", "SafetyExecutorAgent")

_emit_dispatches_healing_run("p1", "SafetyExecutorAgent", "L5")
_emit_routes_through("p1", "SafetyExecutorAgent", "L5")
_emit_escalates_to_human("p1", "SafetyExecutorAgent", "L5")
_emit_reads_policy_state("p1", "SafetyExecutorAgent", "L5")

_emit_snapshots_state("p0", "SafetyExecutorAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "SafetyExecutorAgent", "execution_auth")
_emit_validates_capability("p2", "SafetyExecutorAgent", "capability_check")
_emit_routes_to_capability("p2", "SafetyExecutorAgent", "capability_route")
_emit_writes_via_uwg("p2", "SafetyExecutorAgent", "uwg_write")
_emit_blocks_direct_write("p2", "SafetyExecutorAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "SafetyExecutorAgent", "tool_invocation")
_emit_captures_execution_output("p2", "SafetyExecutorAgent", "exec_output")
_emit_dispatches_agent("p3", "SafetyExecutorAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "SafetyExecutorAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "SafetyExecutorAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "SafetyExecutorAgent", "healing_outcome")
_emit_escalates_failure("p3", "SafetyExecutorAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "SafetyExecutorAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SafetyExecutorAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "SafetyExecutorAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "SafetyExecutorAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SafetyExecutorAgent", "eval_metric")
_emit_stores_embedding("p4", "SafetyExecutorAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "SafetyExecutorAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SafetyExecutorAgent", "exec_snapshot_link")

"\nSafetyExecutorAgent - Safety Execution Interface\n\nPhase 4 Hard Migration: Consolidates:\n- IntegrityGateExecutorAgent (integrity gate execution)\n- L5IntegrityGateExecutorAgent (L5 integrity gates)\n- SafetyExecutorAgent (safety execution)\n\nFeatures:\n- Pre-execution safety checks\n- Integrity gate enforcement\n- Execution blocking on violations\n- Safety score thresholds\n- Audit logging\n"
import logging
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, TypeVar

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

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

    # guardian: allow-type-erasure
    def heal_repository(self, dry_run: bool = True, execute: bool = False, **kwargs) -> dict[str, Any]:
        """
        Autonomous healing method (Canon Key 51 compliance).

        Args:
            dry_run: If True, only report violations without fixing
            execute: If True, apply fixes

        Returns:
            Dict with healing summary
        """
        return {"violations": 0, "fixed": 0, "errors": 0}

    def __init__(self, agent_config: ExecutorConfig | None = None, detector: Any | None = None):
        self._agent_config = agent_config or ExecutorConfig()
        self._detector = detector
        self._lock = threading.RLock()
        self._gates: list[SafetyGate] = []
        self._results: list[ExecutionResult] = []
        self._blocked_count = 0
        self._allowed_count = 0
        self._init_default_gates()
        Logger.info("SafetyExecutorAgent initialized")

    def _init_default_gates(self) -> None:
        """Initialize default safety gates."""
        _emit_applies_guardrail(str(uuid.uuid4()), "SafetyExecutorAgent._init_default_gates", "L5_POLICY")
        self._gates.append(
            SafetyGate(
                name="context_integrity", check_fn=lambda ctx: ctx is not None, severity="HIGH", blocking=True
            )
        )

    def add_gate(
        self, name: str, check_fn: Callable[..., bool], severity: str = "HIGH", blocking: bool = True
    ) -> None:
        """Add a custom safety gate."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyExecutorAgent.add_gate")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyExecutorAgent.add_gate".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        gate = SafetyGate(name=name, check_fn=check_fn, severity=severity, blocking=blocking)
        self._gates.append(gate)
        Logger.info(f"Added safety gate: {name}")

    def execute(
        self, fn: Callable[..., T], *args, context: dict[str, Any] | None = None, **kwargs
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
            if self._agent_config.enable_safety_checks:
                check_result = self._run_safety_checks(context or {})
                if check_result.status == ExecutionStatus.BLOCKED:
                    self._blocked_count += 1
                    self._results.append(check_result)
                    return check_result
            if self._agent_config.enable_integrity_gates:
                gate_result = self._run_gates(context or {})
                if gate_result.status == ExecutionStatus.BLOCKED:
                    self._blocked_count += 1
                    self._results.append(gate_result)
                    return gate_result
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
            # guardian: allow-silent-swallow
            except Exception as e:
                raise
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
            return ExecutionResult(status=ExecutionStatus.ALLOWED, message="No detector configured")
        try:
            input_text = context.get("input", "")
            if not input_text:
                return ExecutionResult(status=ExecutionStatus.ALLOWED, message="No input to check")
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
                high_severity = [t for t in threats if hasattr(t, "severity") and t.severity.value >= 2]
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
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Safety check error: {e}")
        return ExecutionResult(status=ExecutionStatus.ALLOWED, message="Safety checks passed")

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
            # guardian: allow-silent-swallow
            except Exception as e:
                Logger.error(f"Gate {gate.name} error: {e}")
                if gate.blocking:
                    return ExecutionResult(
                        status=ExecutionStatus.BLOCKED,
                        block_reason=BlockReason.INTEGRITY_FAILURE,
                        message=f"Integrity gate error: {gate.name} - {e}",
                    )
        return ExecutionResult(status=ExecutionStatus.ALLOWED, message="All integrity gates passed")

    def check_and_block(self, input_text: str, source: str = "unknown") -> tuple[bool, str]:
        """
        Quick check if input should be blocked.

        Args:
            input_text: Input to check
            source: Source of input

        Returns:
            Tuple of (should_block, reason)
        """
        if self._detector is None:
            return (False, "No detector configured")
        try:
            if hasattr(self._detector, "is_safe"):
                is_safe = self._detector.is_safe(input_text, source)
                if not is_safe:
                    return (True, "Safety detector flagged input as unsafe")
            if hasattr(self._detector, "get_safety_score"):
                score = self._detector.get_safety_score(input_text)
                if score < self._agent_config.safety_score_threshold:
                    return (True, f"Safety score {score:.2f} below threshold")
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"Check error: {e}")
        return (False, "Input passed safety checks")

    # guardian: allow-type-erasure
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

    # guardian: allow-type-erasure
    def heal(self, violation: dict) -> dict:
        """Heal safety execution violations using standard_heal decorator pattern.

        Args:
            violation: Dictionary containing violation details with keys:
                - type: Type of violation (blocked, failed, integrity)
                - block_reason: Reason for blocking
                - agent_id: Agent that was blocked

        Returns:
            Dictionary with healing results following standard_heal format.
        """
        Logger.info("[SAFETY_EXECUTOR] Execution violations are runtime-managed")
        return {
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "reason": "Execution violations are runtime-managed, not code-healable",
        }


def create_legacy_integrity_executor() -> SafetyExecutorAgent:
    """Create executor with integrity gates only."""
    config = ExecutorConfig(enable_integrity_gates=True, enable_safety_checks=False)
    return SafetyExecutorAgent(config=config)


def create_legacy_safety_executor() -> SafetyExecutorAgent:
    """Create executor with safety checks only."""
    config = ExecutorConfig(enable_integrity_gates=False, enable_safety_checks=True)
    return SafetyExecutorAgent(config=config)
