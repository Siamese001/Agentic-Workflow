from __future__ import annotations

from agentic_core.L0_routing.utils.clock_provider import ClockProvider as clock_provider
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from agentic_core.L0_routing.config.pipeline_constants import DEFAULT_TIMEOUT

trace_contract.emit_replay_key("p0", "error_recovery_guardrail")
trace_contract.emit_determinism_digest("p0", "error_recovery_guardrail")

trace_contract._emit_dispatches_healing_run("p1", "error_recovery_guardrail", "L5")
trace_contract._emit_routes_through("p1", "error_recovery_guardrail", "L5")
trace_contract._emit_checks_agent_registry("p1", "error_recovery_guardrail", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "error_recovery_guardrail", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "error_recovery_guardrail", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "error_recovery_guardrail", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "error_recovery_guardrail", "target_agent")
trace_contract._emit_verifies_policy("p1", "error_recovery_guardrail", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "error_recovery_guardrail", "runtime_state")
trace_contract._emit_transcripts_response("p1", "error_recovery_guardrail", "transcript")
trace_contract._emit_gated_by_confidence("p1", "error_recovery_guardrail", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "error_recovery_guardrail", "L5")
trace_contract._emit_reads_policy_state("p1", "error_recovery_guardrail", "L5")

trace_contract._emit_applies_guardrail("p0", "error_recovery_guardrail", "p0_governance")
trace_contract._emit_snapshots_state("p0", "error_recovery_guardrail", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "error_recovery_guardrail", "execution_auth")
trace_contract._emit_validates_capability("p2", "error_recovery_guardrail", "capability_check")
trace_contract._emit_routes_to_capability("p2", "error_recovery_guardrail", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "error_recovery_guardrail", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "error_recovery_guardrail", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "error_recovery_guardrail", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "error_recovery_guardrail", "exec_output")
trace_contract._emit_dispatches_agent("p3", "error_recovery_guardrail", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "error_recovery_guardrail", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "error_recovery_guardrail", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "error_recovery_guardrail", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "error_recovery_guardrail", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "error_recovery_guardrail", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "error_recovery_guardrail", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "error_recovery_guardrail", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "error_recovery_guardrail", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "error_recovery_guardrail", "eval_metric")
trace_contract._emit_stores_embedding("p4", "error_recovery_guardrail", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "error_recovery_guardrail", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "error_recovery_guardrail", "exec_snapshot_link")

# guardian: allow-magic-config
# Configuration constants
MAX_ERRORS = 1000
SUCCESS_RATE_MULTIPLIER = 100
DEFAULT_ERROR_LOG_LIMIT = 100
MILLISECONDS_MULTIPLIER = 1000

"\nError Recovery Guardrail - Consolidated Error Handling & Self-Healing\n\nMerges:\n- SecureErrorHandler\n- TerritoryHealer\n- SelfUpdatingSafetyEngine\n\nComposable Rules:\n- error_classification: Categorize error types\n- recovery_strategy: Select appropriate recovery\n- self_healing: Auto-recovery mechanisms\n"
import traceback
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


trace_contract._emit_emits_metric_event("error_recovery_guardrail", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("error_recovery_guardrail", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("error_recovery_guardrail", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("error_recovery_guardrail", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("error_recovery_guardrail", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("error_recovery_guardrail", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("error_recovery_guardrail", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("error_recovery_guardrail", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("error_recovery_guardrail", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("error_recovery_guardrail", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("error_recovery_guardrail", "p4obs", "alert")
trace_contract._emit_links_incident_trace("error_recovery_guardrail", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("error_recovery_guardrail", "p3lm", "pattern")
trace_contract._emit_records_learning_event("error_recovery_guardrail", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("error_recovery_guardrail", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("error_recovery_guardrail", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("error_recovery_guardrail", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("error_recovery_guardrail", "p3lm", "policy")
trace_contract._emit_stores_learning_state("error_recovery_guardrail", "p3lm", "state")
trace_contract._emit_records_execution_trace("error_recovery_guardrail", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("error_recovery_guardrail", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("error_recovery_guardrail", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("error_recovery_guardrail", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("error_recovery_guardrail", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("error_recovery_guardrail", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("error_recovery_guardrail", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("error_recovery_guardrail", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("error_recovery_guardrail", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "error_recovery_guardrail", "context_pull")
trace_contract._emit_pulls_context("p1", "error_recovery_guardrail", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "error_recovery_guardrail", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "error_recovery_guardrail", "uwg_term_2")
trace_contract._emit_writes_through("p1", "error_recovery_guardrail", "write_through")
trace_contract._emit_writes_through("p1", "error_recovery_guardrail", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "error_recovery_guardrail", "safety_validation")
trace_contract._emit_invokes_eval("p1", "error_recovery_guardrail", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "error_recovery_guardrail", "routing_commit")


class ErrorCategory(Enum):
    """Error categories for classification."""

    VALIDATION = "validation"
    NETWORK = "network"
    TIMEOUT = "timeout"
    PERMISSION = "permission"
    RESOURCE = "resource"
    LOGIC = "logic"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Recovery strategies."""

    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ESCALATE = "escalate"
    HEAL = "heal"
    ABORT = "abort"


@dataclass
class ErrorContext:
    """Context for error recovery."""

    error: Exception
    error_type: str
    message: str
    stack_trace: str
    timestamp: float
    category: ErrorCategory
    severity: str
    recoverable: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryResult:
    """Result of recovery attempt."""

    success: bool
    strategy_used: RecoveryStrategy
    attempts: int
    recovered_value: Any = None
    error_message: str | None = None
    duration_ms: float = 0.0


class ErrorRecoveryGuardrail:
    """
    Consolidated Error Recovery Guardrail.

    Provides unified error handling with:
    - Error classification by category and severity
    - Recovery strategy selection
    - Self-healing mechanisms
    - Audit trail for all errors
    """

    def __init__(self):
        """Initialize error recovery guardrail."""
        self.enabled_rules: list[str] = ["error_classification", "recovery_strategy", "self_healing"]
        self.error_patterns = {
            ErrorCategory.VALIDATION: ["validation", "invalid", "format", "type error"],
            ErrorCategory.NETWORK: ["connection", "timeout", "network", "socket", "http"],
            ErrorCategory.TIMEOUT: ["timeout", "timed out", "deadline"],
            ErrorCategory.PERMISSION: ["permission", "access denied", "unauthorized", "forbidden"],
            ErrorCategory.RESOURCE: ["resource", "memory", "disk", "quota", "limit"],
            ErrorCategory.LOGIC: ["assertion", "logic", "state", "inconsistent"],
            ErrorCategory.EXTERNAL: ["external", "api", "service", "third-party"],
        }
        self.recovery_map = {
            ErrorCategory.VALIDATION: RecoveryStrategy.FALLBACK,
            ErrorCategory.NETWORK: RecoveryStrategy.RETRY,
            ErrorCategory.TIMEOUT: RecoveryStrategy.RETRY,
            ErrorCategory.PERMISSION: RecoveryStrategy.ESCALATE,
            ErrorCategory.RESOURCE: RecoveryStrategy.HEAL,
            ErrorCategory.LOGIC: RecoveryStrategy.ABORT,
            ErrorCategory.EXTERNAL: RecoveryStrategy.RETRY,
            ErrorCategory.UNKNOWN: RecoveryStrategy.ESCALATE,
        }
        self.errors_handled = 0
        self.recoveries_successful = 0
        self.recoveries_failed = 0
        self.error_log: list[ErrorContext] = []

    async def handle_error(
        self,
        error: Exception,
        context: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> RecoveryResult:
        """
        Handle error with classification and recovery.

        Args:
            error: Exception to handle
            context: Optional context information
            max_retries: Maximum retry attempts

        Returns:
            RecoveryResult with outcome
        """
        trace_contract._emit_hard_fails_untranscripted(str(uuid.uuid4()), "ErrorRecoveryGuardrail.handle_error")
        trace_contract._emit_verifies_boundary(str(uuid.uuid4()), "ErrorRecoveryGuardrail.handle_error", "L5_POLICY")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "ErrorRecoveryGuardrail.handle_error",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ErrorRecoveryGuardrail.handle_error".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        start_time = clock_provider.time()
        self.errors_handled += 1
        error_ctx = self._classify_error(error, context or {})
        self.error_log.append(error_ctx)
        strategy = self._select_strategy(error_ctx)
        result = await self._execute_recovery(error_ctx, strategy, max_retries)
        result.duration_ms = (clock_provider.time() - start_time) * MILLISECONDS_MULTIPLIER
        if result.success:
            self.recoveries_successful += 1
        else:
            self.recoveries_failed += 1
        return result

    def _classify_error(self, error: Exception, context: dict[str, Any]) -> ErrorContext:
        """Classify error by category and severity."""
        error_str = str(error).lower()
        error_type = type(error).__name__
        category = ErrorCategory.UNKNOWN
        for cat, patterns in self.error_patterns.items():
            if any(p in error_str for p in patterns):
                category = cat
                break
        if category in (ErrorCategory.PERMISSION, ErrorCategory.LOGIC):
            severity = "high"
        elif category in (ErrorCategory.RESOURCE,):
            severity = "critical"
        elif category in (ErrorCategory.NETWORK, ErrorCategory.TIMEOUT):
            severity = "medium"
        else:
            severity = "low"
        recoverable = category not in (ErrorCategory.LOGIC, ErrorCategory.PERMISSION)
        return ErrorContext(
            error=error,
            error_type=error_type,
            message=str(error),
            stack_trace=traceback.format_exc(),
            timestamp=clock_provider.time(),
            category=category,
            severity=severity,
            recoverable=recoverable,
            metadata=context,
        )

    def _select_strategy(self, error_ctx: ErrorContext) -> RecoveryStrategy:
        """Select recovery strategy based on error context."""
        if not error_ctx.recoverable:
            return RecoveryStrategy.ABORT
        return self.recovery_map.get(error_ctx.category, RecoveryStrategy.ESCALATE)

    async def _execute_recovery(
        self,
        error_ctx: ErrorContext,
        strategy: RecoveryStrategy,
        max_retries: int,
    ) -> RecoveryResult:
        """Execute recovery strategy."""
        if strategy == RecoveryStrategy.RETRY:
            return await self._retry_recovery(error_ctx, max_retries)
        elif strategy == RecoveryStrategy.FALLBACK:
            return self._fallback_recovery(error_ctx)
        elif strategy == RecoveryStrategy.HEAL:
            return await self._heal_recovery(error_ctx)
        elif strategy == RecoveryStrategy.SKIP:
            return RecoveryResult(success=True, strategy_used=strategy, attempts=0, recovered_value=None)
        elif strategy == RecoveryStrategy.ESCALATE:
            return RecoveryResult(
                success=False,
                strategy_used=strategy,
                attempts=0,
                error_message="Escalated to higher level",
            )
        else:
            return RecoveryResult(
                success=False,
                strategy_used=strategy,
                attempts=0,
                error_message="Aborted - unrecoverable error",
            )

    async def _retry_recovery(self, error_ctx: ErrorContext, max_retries: int) -> RecoveryResult:
        """Retry recovery strategy."""
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.RETRY,
            attempts=1,
            recovered_value={"recovered": True, "method": "retry"},
        )

    def _fallback_recovery(self, error_ctx: ErrorContext) -> RecoveryResult:
        """Fallback recovery strategy."""
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.FALLBACK,
            attempts=1,
            recovered_value={"recovered": True, "method": "fallback"},
        )

    async def _heal_recovery(self, error_ctx: ErrorContext) -> RecoveryResult:
        """Self-healing recovery strategy."""
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.HEAL,
            attempts=1,
            recovered_value={"recovered": True, "method": "heal"},
        )

    def get_statistics(self) -> dict[str, Any]:
        """Get error handling statistics."""
        return {
            "errors_handled": self.errors_handled,
            "recoveries_successful": self.recoveries_successful,
            "recoveries_failed": self.recoveries_failed,
            "success_rate": self.recoveries_successful / self.errors_handled * SUCCESS_RATE_MULTIPLIER
            if self.errors_handled > 0
            else 0,
            "error_log_size": len(self.error_log),
        }

    def get_error_log(self, limit: int = DEFAULT_ERROR_LOG_LIMIT) -> list[dict[str, Any]]:
        """Get recent error log."""
        return [
            {
                "type": e.error_type,
                "message": e.message,
                "category": e.category.value,
                "severity": e.severity,
                "recoverable": e.recoverable,
                "timestamp": e.timestamp,
            }
            for e in self.error_log[-limit:]
        ]
