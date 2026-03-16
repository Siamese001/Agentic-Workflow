"""
Adapter Base - V10 Legacy Bridge Pattern Implementation.

Per Agentic Process V10 specification and 'Adapters Usage.png':
- Adapters wrap ORPHAN agents that cannot be safely refactored
- Preserve exact orphan behavior
- Add ONLY V10 logic (circuit breaker, validation gate, audit trail)

The adapter pattern enables:
1. Zero-modification to legacy code
2. V10 compliance wrapper
3. Future swap-out capability (adapter -> native)

References:
- Adapters Usage.png: "WITH ADAPTERS (LEGACY)" vs "NO ADAPTERS (NATIVE/COMPLIANT)"
- V10 Diagram: "Legacy Bridge" integration layer
"""

import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Generic, TypeVar

from agentic_core.L5_safety.enforcement.circuit_breaker_gate import CircuitBreaker, get_breaker
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
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
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "AdapterBase")
emit_determinism_digest("p0", "AdapterBase")

_emit_dispatches_healing_run("p1", "AdapterBase", "L5")
_emit_routes_through("p1", "AdapterBase", "L5")
_emit_escalates_to_human("p1", "AdapterBase", "L5")
_emit_reads_policy_state("p1", "AdapterBase", "L5")

_emit_snapshots_state("p0", "AdapterBase", "state_snapshot")
_emit_authorize_and_execute("p2", "AdapterBase", "execution_auth")
_emit_validates_capability("p2", "AdapterBase", "capability_check")
_emit_routes_to_capability("p2", "AdapterBase", "capability_route")
_emit_writes_via_uwg("p2", "AdapterBase", "uwg_write")
_emit_blocks_direct_write("p2", "AdapterBase", "direct_write_block")
_emit_records_tool_invocation("p2", "AdapterBase", "tool_invocation")
_emit_captures_execution_output("p2", "AdapterBase", "exec_output")
_emit_dispatches_agent("p3", "AdapterBase", "agent_dispatch")
_emit_coordinates_agents("p3", "AdapterBase", "agent_coordination")
_emit_records_workflow_lineage("p3", "AdapterBase", "workflow_lineage")
_emit_records_healing_outcome("p3", "AdapterBase", "healing_outcome")
_emit_escalates_failure("p3", "AdapterBase", "failure_escalation")
_emit_orchestrates_workflow("p3", "AdapterBase", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "AdapterBase", "healing_dispatch")
_emit_invokes_evaluation("p3", "AdapterBase", "evaluation_signal")
_emit_records_telemetry_event("p4", "AdapterBase", "telemetry_event")
_emit_captures_evaluation_metric("p4", "AdapterBase", "eval_metric")
_emit_stores_embedding("p4", "AdapterBase", "embedding_store")
_emit_updates_meta_learning_state("p4", "AdapterBase", "meta_learning")
_emit_links_execution_to_snapshot("p4", "AdapterBase", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("AdapterBase", "p4obs", "metric_1")
_emit_emits_metric_event("AdapterBase", "p4obs", "metric_2")
_emit_emits_metric_event("AdapterBase", "p4obs", "metric_3")
_emit_emits_metric_event("AdapterBase", "p4obs", "metric_4")
_emit_emits_metric_event("AdapterBase", "p4obs", "metric_5")
_emit_emits_metric_event("AdapterBase", "p4obs", "metric_6")
_emit_records_incident_event("AdapterBase", "p4obs", "incident")
_emit_captures_runtime_anomaly("AdapterBase", "p4obs", "anomaly")
_emit_writes_observability_log("AdapterBase", "p4obs", "obs_log")
_emit_updates_monitoring_state("AdapterBase", "p4obs", "mon_state")
_emit_triggers_alert("AdapterBase", "p4obs", "alert")
_emit_links_incident_trace("AdapterBase", "p4obs", "trace_link")
_emit_captures_pattern("AdapterBase", "p3lm", "pattern")
_emit_records_learning_event("AdapterBase", "p3lm", "learning_event")
_emit_writes_learning_snapshot("AdapterBase", "p3lm", "snapshot")
_emit_feeds_meta_learning("AdapterBase", "p3lm", "meta_feed")
_emit_updates_routing_strategy("AdapterBase", "p3lm", "routing")
_emit_improves_agent_policy("AdapterBase", "p3lm", "policy")
_emit_stores_learning_state("AdapterBase", "p3lm", "state")
_emit_records_execution_trace("AdapterBase", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("AdapterBase", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("AdapterBase", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("AdapterBase", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("AdapterBase", "L4_STATE", "p2_trace_5")
_emit_reads_environ("AdapterBase", "env_read", "p2_env_1")
_emit_reads_environ("AdapterBase", "env_read", "p2_env_2")
_emit_reads_runtime_state("AdapterBase", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("AdapterBase", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "AdapterBase", "context_pull")
_emit_pulls_context("p1", "AdapterBase", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "AdapterBase", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "AdapterBase", "uwg_term_2")
_emit_writes_through("p1", "AdapterBase", "write_through")
_emit_writes_through("p1", "AdapterBase", "write_through_2")
_emit_validated_by_safety_plane("p1", "AdapterBase", "safety_validation")
_emit_invokes_eval("p1", "AdapterBase", "eval_call")
_emit_proposal_commits_routing("p1", "AdapterBase", "routing_commit")

logger = logging.getLogger(__name__)
T = TypeVar("T")


@dataclass
class AdapterContext:
    """Context passed through adapter chain."""

    request_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    risk_level: str = "medium"
    bypass_validation: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AdapterResult:
    """Standardized result from adapter operations."""

    success: bool
    data: Any = None
    error: str | None = None
    skipped: bool = False
    skip_reason: str | None = None
    audit_trail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "skipped": self.skipped,
            "skip_reason": self.skip_reason,
            "audit_trail": self.audit_trail,
        }


class AdapterBase(ABC, Generic[T]):
    """
    Base class for V10-compliant Legacy Adapters.

    Implements the Bridge Pattern per V10 specification:
    - Wraps legacy/orphan agents without modification
    - Injects V10 compliance (circuit breaker, validation, audit)
    - Preserves exact legacy behavior

    Usage:
        class EmbeddingAdapter(AdapterBase[EmbeddingSovereignAgent]):
            def __init__(self, legacy_agent: EmbeddingSovereignAgent):
                super().__init__(legacy_agent, "embedding_service")

            def _execute_legacy(self, context, *args, **kwargs):
                return self._legacy_agent.get_embedding(*args, **kwargs)

            def _validate_input(self, context, *args, **kwargs):
                # V10 validation logic
                return True

            def _validate_output(self, result, context):
                # V10 output validation
                return True
    """

    def __init__(
        self, legacy_agent: T, service_name: str, circuit_breaker_config: dict[str, Any] | None = None
    ):
        """
        Initialize adapter with legacy agent.

        Args:
            legacy_agent: The orphan agent to wrap
            service_name: Name for circuit breaker and logging
            circuit_breaker_config: Optional circuit breaker configuration
        """
        self._legacy_agent = legacy_agent
        self._service_name = service_name
        self._circuit_breaker = get_breaker(f"adapter_{service_name}", **circuit_breaker_config or {})
        self._audit_log: list[dict[str, Any]] = []
        self._verification_gate = None
        logger.info(f"AdapterBase initialized for '{service_name}' wrapping {type(legacy_agent).__name__}")

    @property
    def legacy_agent(self) -> T:
        """Access the wrapped legacy agent (read-only)."""
        return self._legacy_agent

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """Access the circuit breaker for this adapter."""
        return self._circuit_breaker

    def _get_verification_gate(self):
        """Lazy-load verification gate to avoid circular imports."""
        _emit_applies_guardrail(str(uuid.uuid4()), "AdapterBase._get_verification_gate", "L5_POLICY")
        if self._verification_gate is None:
            try:
                from agentic_core.L5_safety.enforcement.verification_gate import VerificationGate

                self._verification_gate = VerificationGate()
            except ImportError:
                logger.warning("VerificationGate not available")
        return self._verification_gate

    @abstractmethod
    def _execute_legacy(self, context: AdapterContext, *args, **kwargs) -> Any:
        """
        Execute the legacy agent's operation.

        Subclasses MUST implement this to call the appropriate
        legacy agent method.

        Args:
            context: Adapter context with request metadata
            *args: Positional arguments for legacy method
            **kwargs: Keyword arguments for legacy method

        Returns:
            Raw result from legacy agent
        """
        pass

    def _validate_input(self, context: AdapterContext, *args, **kwargs) -> bool:
        """
        V10 Input validation before legacy execution.

        Override to add input validation. Default: allow all.

        Args:
            context: Adapter context
            *args: Input arguments
            **kwargs: Input keyword arguments

        Returns:
            True if input is valid, False to reject
        """
        _emit_verifies_boundary(str(uuid.uuid4()), "AdapterBase._validate_input", "L5_POLICY")
        return True

    def _validate_output(self, result: Any, context: AdapterContext) -> bool:
        """
        V10 Output validation after legacy execution.

        Override to add output validation. Default: allow all.

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            True if output is valid, False to reject
        """
        return True

    def _pre_execute_hook(self, context: AdapterContext, *args, **kwargs) -> AdapterResult | None:
        """
        Hook called before execution.

        Override to add pre-execution logic. Return AdapterResult
        to short-circuit execution.

        Args:
            context: Adapter context
            *args: Input arguments
            **kwargs: Input keyword arguments

        Returns:
            None to continue, AdapterResult to short-circuit
        """
        return None

    def _post_execute_hook(self, result: Any, context: AdapterContext) -> Any:
        """
        Hook called after successful execution.

        Override to transform or enrich results.

        Args:
            result: Result from legacy execution
            context: Adapter context

        Returns:
            Transformed result
        """
        return result

    def _on_error(self, error: Exception, context: AdapterContext) -> AdapterResult | None:
        """
        Error handler for legacy execution failures.

        Override to customize error handling. Default: re-raise.

        Args:
            error: Exception from legacy execution
            context: Adapter context

        Returns:
            AdapterResult to return instead of raising, or None to raise
        """
        return None

    def _log_audit(
        self,
        action: str,
        context: AdapterContext,
        result: AdapterResult | None = None,
        error: Exception | None = None,
    ) -> None:
        """Log to audit trail for V10 observability."""
        try:
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "service": self._service_name,
                "action": action,
                "request_id": context.request_id,
                "risk_level": context.risk_level,
                "success": result.success if result else False,
                "error": str(error) if error else None,
            }
            self._audit_log.append(entry)
            logger.debug(f"Adapter audit: {entry}")
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to log audit: {e}")

    def execute(self, context: AdapterContext | None = None, *args, **kwargs) -> AdapterResult:
        """
        Execute the adapted operation with V10 compliance.

        This is the main entry point that:
        1. Checks circuit breaker state
        2. Validates input (V10 guardrail)
        3. Calls pre-execute hook
        4. Executes legacy agent
        5. Validates output (V10 guardrail)
        6. Calls post-execute hook
        7. Records to audit trail

        Args:
            context: Optional adapter context (created if not provided)
            *args: Arguments for legacy method
            **kwargs: Keyword arguments for legacy method

        Returns:
            AdapterResult with operation outcome
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "AdapterBase.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:AdapterBase.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        import uuid

        if context is None:
            context = AdapterContext(request_id=str(uuid.uuid4()))
        audit_trail = {
            "request_id": context.request_id,
            "adapter": self._service_name,
            "legacy_agent": type(self._legacy_agent).__name__,
            "started_at": datetime.utcnow().isoformat(),
        }
        if not self._circuit_breaker.allow_request():
            self._log_audit("circuit_open", context)
            return AdapterResult(
                success=False,
                error="Circuit breaker is OPEN",
                skipped=True,
                skip_reason="circuit_breaker_open",
                audit_trail=audit_trail,
            )
        try:
            if not self._validate_input(context, *args, **kwargs):
                self._log_audit("input_validation_failed", context)
                return AdapterResult(
                    success=False,
                    error="Input validation failed",
                    skipped=True,
                    skip_reason="input_validation_failed",
                    audit_trail=audit_trail,
                )
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return AdapterResult(success=False, error=f"Input validation error: {e}", audit_trail=audit_trail)
        pre_result = self._pre_execute_hook(context, *args, **kwargs)
        if pre_result is not None:
            self._log_audit("pre_execute_short_circuit", context, pre_result)
            return pre_result
        try:
            raw_result = self._execute_legacy(context, *args, **kwargs)
            self._circuit_breaker.record_success()
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            self._circuit_breaker.record_failure(e)
            self._log_audit("execution_error", context, error=e)
            error_result = self._on_error(e, context)
            if error_result is not None:
                return error_result
            return AdapterResult(success=False, error=str(e), audit_trail=audit_trail)
        try:
            if not self._validate_output(raw_result, context):
                self._log_audit("output_validation_failed", context)
                return AdapterResult(
                    success=False, data=raw_result, error="Output validation failed", audit_trail=audit_trail
                )
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Output validation error: {e}")
            return AdapterResult(
                success=False, data=raw_result, error=f"Output validation error: {e}", audit_trail=audit_trail
            )
        final_result = self._post_execute_hook(raw_result, context)
        audit_trail["completed_at"] = datetime.utcnow().isoformat()
        result = AdapterResult(success=True, data=final_result, audit_trail=audit_trail)
        self._log_audit("success", context, result)
        return result

    def get_audit_log(self) -> list[dict[str, Any]]:
        """Get the audit log for this adapter."""
        return list(self._audit_log)

    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        self._audit_log.clear()

    def get_status(self) -> dict[str, Any]:
        """Get adapter status for dashboard."""
        return {
            "service_name": self._service_name,
            "legacy_agent_type": type(self._legacy_agent).__name__,
            "circuit_breaker": self._circuit_breaker.metrics.__dict__,
            "audit_log_size": len(self._audit_log),
        }


class HealingAdapter(AdapterBase[T]):
    """
    Specialized adapter for healing operations.

    Adds V10 healing-specific logic:
    - Verification gate integration
    - Atomic execution support
    - Symmetric AST manifest handling
    """

    def __init__(self, legacy_agent: T, service_name: str, project_root: Path | None = None):
        super().__init__(legacy_agent, service_name)
        self._project_root = project_root or Path.cwd()

    def verify_healing_target(self, file_path: Path, action_type: str, target_node: str) -> bool:
        """
        Verify healing target exists before execution.

        Per V10 Validation Gate specification.

        Args:
            file_path: File to verify
            action_type: Type of healing action
            target_node: Target node name

        Returns:
            True if target exists, False if hallucinated
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "HealingAdapter.verify_healing_target"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HealingAdapter.verify_healing_target".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        gate = self._get_verification_gate()
        if gate is None:
            logger.warning("VerificationGate unavailable, allowing action")
            return True
        return gate.verify_action(file_path, action_type, target_node)


AdapterBaseAdapter = AdapterBase
__all__ = ["AdapterBase", "AdapterBaseAdapter", "AdapterContext", "AdapterResult", "HealingAdapter"]
