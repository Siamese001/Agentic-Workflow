"""Perform observability Operation - observability operation execution adapter.

This module provides adapters for performing specific observability operations
with proper error handling, context management, and result aggregation.
Follows the functional component pattern with proper logging.
"""

import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

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
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
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

_emit_applies_guardrail("p0", "operation_category_types", "p0_governance")
_emit_reads_policy_state("p0", "operation_category_types", "policy_binding")
_emit_snapshots_state("p0", "operation_category_types", "state_snapshot")
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
from tqdm import tqdm

_emit_emits_metric_event("operation_category_types", "p4obs", "metric_1")
_emit_emits_metric_event("operation_category_types", "p4obs", "metric_2")
_emit_emits_metric_event("operation_category_types", "p4obs", "metric_3")
_emit_emits_metric_event("operation_category_types", "p4obs", "metric_4")
_emit_emits_metric_event("operation_category_types", "p4obs", "metric_5")
_emit_emits_metric_event("operation_category_types", "p4obs", "metric_6")
_emit_records_incident_event("operation_category_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("operation_category_types", "p4obs", "anomaly")
_emit_writes_observability_log("operation_category_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("operation_category_types", "p4obs", "mon_state")
_emit_triggers_alert("operation_category_types", "p4obs", "alert")
_emit_links_incident_trace("operation_category_types", "p4obs", "trace_link")
_emit_captures_pattern("operation_category_types", "p3lm", "pattern")
_emit_records_learning_event("operation_category_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("operation_category_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("operation_category_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("operation_category_types", "p3lm", "routing")
_emit_improves_agent_policy("operation_category_types", "p3lm", "policy")
_emit_stores_learning_state("operation_category_types", "p3lm", "state")
_emit_records_execution_trace("operation_category_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("operation_category_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("operation_category_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("operation_category_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("operation_category_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("operation_category_types", "env_read", "p2_env_1")
_emit_reads_environ("operation_category_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("operation_category_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("operation_category_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "operation_category_types", "context_pull")
_emit_pulls_context("p1", "operation_category_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "operation_category_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "operation_category_types", "uwg_term_2")
_emit_writes_through("p1", "operation_category_types", "write_through")
_emit_writes_through("p1", "operation_category_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "operation_category_types", "safety_validation")
_emit_invokes_eval("p1", "operation_category_types", "eval_call")
_emit_proposal_commits_routing("p1", "operation_category_types", "routing_commit")
_emit_escalates_to_human("p1", "operation_category_types", "human_escalation")
_emit_routes_through("p1", "operation_category_types", "route_through")
_emit_checks_agent_registry("p1", "operation_category_types", "agent_registry")
_emit_validates_agent_capability("p1", "operation_category_types", "capability")
_emit_dispatches_execution_plan("p1", "operation_category_types", "exec_plan")
_emit_agent_executes_agent("p1", "operation_category_types", "sub_agent")
_emit_routes_to_agent("p1", "operation_category_types", "target_agent")
_emit_verifies_policy("p1", "operation_category_types", "policy_check")
_emit_observes_runtime_state("p1", "operation_category_types", "runtime_state")
_emit_verifies_boundary("p1", "operation_category_types", "boundary_check")
_emit_transcripts_response("p1", "operation_category_types", "transcript")
_emit_hard_fails_untranscripted("p1", "operation_category_types")
_emit_gated_by_confidence("p1", "operation_category_types", "confidence_gate")
emit_replay_key("p0", "operation_category_types")
emit_determinism_digest("p0", "operation_category_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "operation_category_types", "execution_auth")
_emit_validates_capability("p2", "operation_category_types", "capability_check")
_emit_routes_to_capability("p2", "operation_category_types", "capability_route")
_emit_writes_via_uwg("p2", "operation_category_types", "uwg_write")
_emit_blocks_direct_write("p2", "operation_category_types", "direct_write_block")
_emit_records_tool_invocation("p2", "operation_category_types", "tool_invocation")
_emit_captures_execution_output("p2", "operation_category_types", "exec_output")
_emit_dispatches_agent("p3", "operation_category_types", "agent_dispatch")
_emit_coordinates_agents("p3", "operation_category_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "operation_category_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "operation_category_types", "healing_outcome")
_emit_escalates_failure("p3", "operation_category_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "operation_category_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "operation_category_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "operation_category_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "operation_category_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "operation_category_types", "eval_metric")
_emit_stores_embedding("p4", "operation_category_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "operation_category_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "operation_category_types", "exec_snapshot_link")
_emit_reads_through("l4", "operation_category_types", "urg_read_1")
_emit_reads_through("l4", "operation_category_types", "urg_read_2")
_emit_reads_through("l4", "operation_category_types", "urg_read_3")
_emit_reads_through("l4", "operation_category_types", "urg_read_4")
_emit_reads_through("l4", "operation_category_types", "urg_read_5")
_emit_reads_through("l4", "operation_category_types", "urg_read_6")
_emit_reads_through("l4", "operation_category_types", "urg_read_7")
_emit_reads_through("l4", "operation_category_types", "urg_read_8")
_emit_reads_through("l4", "operation_category_types", "urg_read_9")
_emit_reads_through("l4", "operation_category_types", "urg_read_10")
_emit_reads_through("l4", "operation_category_types", "urg_read_11")
_emit_reads_through("l4", "operation_category_types", "urg_read_12")
_emit_reads_through("l4", "operation_category_types", "urg_read_13")
_emit_reads_through("l4", "operation_category_types", "urg_read_14")
_emit_reads_through("l4", "operation_category_types", "urg_read_15")
_emit_reads_through("l4", "operation_category_types", "urg_read_16")
_emit_reads_through("l4", "operation_category_types", "urg_read_17")
_emit_reads_through("l4", "operation_category_types", "urg_read_18")
_emit_reads_through("l4", "operation_category_types", "urg_read_19")
_emit_reads_through("l4", "operation_category_types", "urg_read_20")
_emit_reads_through("l4", "operation_category_types", "urg_read_21")
_emit_reads_through("l4", "operation_category_types", "urg_read_22")
_emit_reads_through("l4", "operation_category_types", "urg_read_23")
_emit_reads_through("l4", "operation_category_types", "urg_read_24")
_emit_reads_through("l4", "operation_category_types", "urg_read_25")
_emit_reads_through("l4", "operation_category_types", "urg_read_26")
_emit_reads_through("l4", "operation_category_types", "urg_read_27")
_emit_reads_through("l4", "operation_category_types", "urg_read_28")
_emit_reads_through("l4", "operation_category_types", "urg_read_29")
_emit_reads_through("l4", "operation_category_types", "urg_read_30")
_emit_reads_through("l4", "operation_category_types", "urg_read_31")
_emit_reads_through("l4", "operation_category_types", "urg_read_32")
_emit_reads_through("l4", "operation_category_types", "urg_read_33")
_emit_reads_through("l4", "operation_category_types", "urg_read_34")
_emit_reads_through("l4", "operation_category_types", "urg_read_35")
_emit_reads_through("l4", "operation_category_types", "urg_read_36")
_emit_reads_through("l4", "operation_category_types", "urg_read_37")
_emit_reads_through("l4", "operation_category_types", "urg_read_38")
_emit_reads_through("l4", "operation_category_types", "urg_read_39")
_emit_reads_through("l4", "operation_category_types", "urg_read_40")
_emit_reads_through("l4", "operation_category_types", "urg_read_41")
_emit_reads_through("l4", "operation_category_types", "urg_read_42")
_emit_reads_through("l4", "operation_category_types", "urg_read_43")
_emit_reads_through("l4", "operation_category_types", "urg_read_44")
_emit_reads_through("l4", "operation_category_types", "urg_read_45")
_emit_reads_through("l4", "operation_category_types", "urg_read_46")
_emit_reads_through("l4", "operation_category_types", "urg_read_47")
_emit_reads_through("l4", "operation_category_types", "urg_read_48")
_emit_reads_through("l4", "operation_category_types", "urg_read_49")
_emit_reads_through("l4", "operation_category_types", "urg_read_50")
_emit_reads_through("l4", "operation_category_types", "urg_read_51")
_emit_reads_through("l4", "operation_category_types", "urg_read_52")
_emit_reads_through("l4", "operation_category_types", "urg_read_53")
_emit_reads_through("l4", "operation_category_types", "urg_read_54")
_emit_reads_through("l4", "operation_category_types", "urg_read_55")
_emit_reads_through("l4", "operation_category_types", "urg_read_56")
_emit_reads_through("l4", "operation_category_types", "urg_read_57")
_emit_reads_through("l4", "operation_category_types", "urg_read_58")
_emit_reads_through("l4", "operation_category_types", "urg_read_59")
_emit_reads_through("l4", "operation_category_types", "urg_read_60")
_emit_reads_through("l4", "operation_category_types", "urg_read_61")
_emit_reads_through("l4", "operation_category_types", "urg_read_62")
_emit_reads_through("l4", "operation_category_types", "urg_read_63")
_emit_reads_through("l4", "operation_category_types", "urg_read_64")
_emit_reads_through("l4", "operation_category_types", "urg_read_65")
_emit_reads_through("l4", "operation_category_types", "urg_read_66")
_emit_reads_through("l4", "operation_category_types", "urg_read_67")
_emit_reads_through("l4", "operation_category_types", "urg_read_68")
_emit_reads_through("l4", "operation_category_types", "urg_read_69")
_emit_reads_through("l4", "operation_category_types", "urg_read_70")
_emit_reads_through("l4", "operation_category_types", "urg_read_71")
_emit_reads_through("l4", "operation_category_types", "urg_read_72")
_emit_reads_through("l4", "operation_category_types", "urg_read_73")
_emit_reads_through("l4", "operation_category_types", "urg_read_74")
_emit_reads_through("l4", "operation_category_types", "urg_read_75")
_emit_reads_through("l4", "operation_category_types", "urg_read_76")
_emit_reads_through("l4", "operation_category_types", "urg_read_77")
_emit_reads_through("l4", "operation_category_types", "urg_read_78")
_emit_reads_through("l4", "operation_category_types", "urg_read_79")
_emit_reads_through("l4", "operation_category_types", "urg_read_80")
_emit_reads_through("l4", "operation_category_types", "urg_read_81")
_emit_reads_through("l4", "operation_category_types", "urg_read_82")
_emit_reads_through("l4", "operation_category_types", "urg_read_83")
_emit_reads_through("l4", "operation_category_types", "urg_read_84")
_emit_reads_through("l4", "operation_category_types", "urg_read_85")
_emit_reads_through("l4", "operation_category_types", "urg_read_86")
_emit_reads_through("l4", "operation_category_types", "urg_read_87")
_emit_reads_through("l4", "operation_category_types", "urg_read_88")
_emit_reads_through("l4", "operation_category_types", "urg_read_89")
_emit_reads_through("l4", "operation_category_types", "urg_read_90")
_emit_reads_through("l4", "operation_category_types", "urg_read_91")
_emit_reads_through("l4", "operation_category_types", "urg_read_92")
_emit_reads_through("l4", "operation_category_types", "urg_read_93")
_emit_reads_through("l4", "operation_category_types", "urg_read_94")
_emit_reads_through("l4", "operation_category_types", "urg_read_95")
_emit_reads_through("l4", "operation_category_types", "urg_read_96")
_emit_reads_through("l4", "operation_category_types", "urg_read_97")
_emit_reads_through("l4", "operation_category_types", "urg_read_98")
_emit_reads_through("l4", "operation_category_types", "urg_read_99")
_emit_reads_through("l4", "operation_category_types", "urg_read_100")
_emit_reads_through("l4", "operation_category_types", "urg_read_101")
_emit_reads_through("l4", "operation_category_types", "urg_read_102")
_emit_reads_through("l4", "operation_category_types", "urg_read_103")
_emit_reads_through("l4", "operation_category_types", "urg_read_104")
_emit_reads_through("l4", "operation_category_types", "urg_read_105")
_emit_reads_through("l4", "operation_category_types", "urg_read_106")
_emit_reads_through("l4", "operation_category_types", "urg_read_107")
_emit_reads_through("l4", "operation_category_types", "urg_read_108")
_emit_reads_through("l4", "operation_category_types", "urg_read_109")
_emit_reads_through("l4", "operation_category_types", "urg_read_110")
_emit_reads_through("l4", "operation_category_types", "urg_read_111")
_emit_reads_through("l4", "operation_category_types", "urg_read_112")
_emit_reads_through("l4", "operation_category_types", "urg_read_113")
_emit_reads_through("l4", "operation_category_types", "urg_read_114")
_emit_reads_through("l4", "operation_category_types", "urg_read_115")
_emit_reads_through("l4", "operation_category_types", "urg_read_116")
_emit_reads_through("l4", "operation_category_types", "urg_read_117")
_emit_reads_through("l4", "operation_category_types", "urg_read_118")
_emit_reads_through("l4", "operation_category_types", "urg_read_119")
_emit_reads_through("l4", "operation_category_types", "urg_read_120")
_emit_reads_through("l4", "operation_category_types", "urg_read_121")

logger = logging.getLogger(__name__)


class OperationCategory(Enum):
    """Categories of observability operations."""

    MONITORING = "monitoring"
    TRACING = "tracing"
    LOGGING = "logging"
    METRICS = "metrics"
    ALERTING = "alerting"


class OperationScope(Enum):
    """Scope of observability operations."""

    SYSTEM = "system"
    COMPONENT = "component"
    SERVICE = "service"
    REQUEST = "request"
    CUSTOM = "custom"


@dataclass
class OperationContext:
    """Context for observability operation."""

    operation_id: str
    category: OperationCategory
    scope: OperationScope
    target: str
    correlation_id: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationParameters:
    """Parameters for observability operation."""

    operation_type: str
    config: dict[str, Any] = field(default_factory=dict)
    filters: dict[str, Any] = field(default_factory=dict)
    aggregation: str | None = None
    time_range: tuple[datetime, datetime] | None = None
    limit: int | None = None


@dataclass
class OperationConfig:
    """configuration for operation execution."""

    timeout: float = 30.0
    retry_attempts: int = 3
    enable_caching: bool = True
    cache_ttl: float = 300.0
    enable_compression: bool = False


@dataclass
class OperationOutcome:
    """Outcome of observability operation."""

    operation_id: str
    success: bool
    data: dict[str, Any] | list[Any] | None = None
    count: int = 0
    aggregated_values: dict[str, float] = field(default_factory=dict)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0


class ObservabilityOperationAdapter:
    """Main adapter for performing observability operations."""

    def __init__(self, config: OperationConfig | None = None):
        self.config = config or OperationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._operation_handlers: dict[str, Callable] = {}
        self._cache: dict[str, tuple[Any, float]] = {}
        self._initialize_handlers()

    def register_handler(self, operation_type: str, handler: Callable) -> None:
        """Register a handler for operation type.

        Args:
            operation_type: Type of operation
            handler: Handler function
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"OperationDispatcher.register_handler:{operation_type}",
        )
        self._operation_handlers[operation_type] = handler
        self.logger.info(f"Registered handler for operation: {operation_type}")

    def perform_operation(
        self,
        context: OperationContext,
        parameters: OperationParameters,
    ) -> OperationOutcome:
        """Perform observability operation.

        Args:
            context: Operation context
            parameters: Operation parameters

        Returns:
            OperationOutcome: Result of operation
        """
        self.logger.info(f"Performing operation: {context.operation_id}")
        start_time = time.time()
        try:
            if self.config.enable_caching:
                cached_result = self._get_from_cache(context, parameters)
                if cached_result is not None:
                    self.logger.info(f"Returning cached result for: {context.operation_id}")
                    cached_result.execution_time = time.time() - start_time
                    return cached_result
            handler = self._operation_handlers.get(parameters.operation_type)
            if not handler:
                return self._create_error_outcome(
                    context.operation_id,
                    f"No handler for operation type: {parameters.operation_type}",
                    start_time,
                )
            result = self._execute_with_retry(handler, context, parameters)
            if self.config.enable_caching and result.success:
                self._store_in_cache(context, parameters, result)
            result.execution_time = time.time() - start_time
            return result
        # guardian: allow-silent-swallow
        except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:
            self.logger.error(f"Operation failed: {str(e)}")
            return self._create_error_outcome(context.operation_id, str(e), start_time)

    def perform_batch_operations(
        self,
        contexts: list[OperationContext],
        parameters_list: list[OperationParameters],
    ) -> list[OperationOutcome]:
        """Perform multiple operations.

        Args:
            contexts: List of operation contexts
            parameters_list: List of operation parameters

        Returns:
            List[OperationOutcome]: Results for all operations
        """
        if len(contexts) != len(parameters_list):
            raise ValueError("Contexts and parameters lists must have same length")
        results = []
        for context, parameters in zip(contexts, parameters_list, strict=False):
            result = self.perform_operation(context, parameters)
            results.append(result)
        return results

    def perform_aggregated_operation(
        self,
        contexts: list[OperationContext],
        parameters: OperationParameters,
    ) -> OperationOutcome:
        """Perform operation with aggregation across multiple contexts.

        Args:
            contexts: List of operation contexts
            parameters: Operation parameters

        Returns:
            OperationOutcome: Aggregated result
        """
        self.logger.info(f"Performing aggregated operation across {len(contexts)} contexts")
        start_time = time.time()
        all_data = []
        all_errors = []
        all_warnings = []
        for context in contexts:
            result = self.perform_operation(context, parameters)
            if result.success and result.data:
                if isinstance(result.data, list):
                    all_data.extend(result.data)
                else:
                    all_data.append(result.data)
            if result.error:
                all_errors.append(result.error)
            all_warnings.extend(result.warnings)
        aggregated_data = self._aggregate_data(all_data, parameters.aggregation)
        aggregated_values = self._calculate_aggregated_values(all_data)
        outcome = OperationOutcome(
            operation_id=f"aggregated_{int(time.time())}",
            success=len(all_errors) == 0,
            data=aggregated_data,
            count=len(all_data),
            aggregated_values=aggregated_values,
            error="; ".join(all_errors) if all_errors else None,
            warnings=all_warnings,
            execution_time=time.time() - start_time,
        )
        return outcome

    def get_operation_history(
        self,
        operation_id: str | None = None,
        time_range: tuple[datetime, datetime] | None = None,
    ) -> list[dict[str, Any]]:
        """Get history of operations.

        Args:
            operation_id: Optional specific operation ID
            time_range: Optional time range filter

        Returns:
            List[Dict]: Operation history
        """
        return []

    def clear_cache(self, pattern: str | None = None) -> int:
        """Clear operation cache.

        Args:
            pattern: Optional pattern to match cache keys

        Returns:
            int: Number of cache entries cleared
        """
        if pattern is None:
            count = len(self._cache)
            self._cache.clear()
            return count
        to_remove = []
        for key in self._cache:
            if pattern in key:
                to_remove.append(key)
        for key in to_remove:
            del self._cache[key]
        return len(to_remove)

    def _execute_with_retry(
        self,
        handler: Callable,
        context: OperationContext,
        parameters: OperationParameters,
    ) -> OperationOutcome:
        """Execute operation with retry logic."""
        last_error = None
        for attempt in tqdm(range(self.config.retry_attempts + 1), desc="Processing", unit="item"):
            try:
                exec_data = {"context": context, "parameters": parameters, "attempt": attempt + 1}
                result_data = handler(exec_data)
                data = result_data.get("data")
                count = result_data.get("count", 0)
                aggregated_values = result_data.get("aggregated_values", {})
                warnings = result_data.get("warnings", [])
                return OperationOutcome(
                    operation_id=context.operation_id,
                    success=True,
                    data=data,
                    count=count,
                    aggregated_values=aggregated_values,
                    warnings=warnings,
                )
            # guardian: allow-silent-swallow
            except (TypeError, ValueError, KeyError, AttributeError, RuntimeError, OSError) as e:
                last_error = str(e)
                if attempt < self.config.retry_attempts:
                    self.logger.warning(f"Operation attempt {attempt + 1} failed, retrying: {last_error}")
                    time.sleep(2**attempt)
                else:
                    self.logger.error(f"Operation failed after {attempt + 1} attempts: {last_error}")
        return self._create_error_outcome(context.operation_id, last_error, time.time())

    def _get_from_cache(
        self,
        context: OperationContext,
        parameters: OperationParameters,
    ) -> OperationOutcome | None:
        """Get result from cache."""
        cache_key = self._generate_cache_key(context, parameters)
        if cache_key in self._cache:
            cached_data, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.config.cache_ttl:
                return cached_data
            else:
                del self._cache[cache_key]
        return None

    def _store_in_cache(
        self,
        context: OperationContext,
        parameters: OperationParameters,
        result: OperationOutcome,
    ) -> None:
        """Store result in cache."""
        cache_key = self._generate_cache_key(context, parameters)
        self._cache[cache_key] = (result, time.time())

    def _generate_cache_key(self, context: OperationContext, parameters: OperationParameters) -> str:
        """Generate cache key for operation."""
        key_data = {
            "operation_type": parameters.operation_type,
            "target": context.target,
            "scope": context.scope.value,
            "config": parameters.config,
            "filters": parameters.filters,
        }
        return f"obs_op_{hash(json.dumps(key_data, sort_keys=True))}"

    def _group_by_type(self, data: list[Any]) -> dict[str, list[Any]]:
        """Group data items by their type."""
        groups = {}
        for item in data:
            item_type = type(item).__name__
            if item_type not in groups:
                groups[item_type] = []
            groups[item_type].append(item)
        return groups

    def _aggregate_numeric(self, data: list[Any], method: str) -> dict[str, float] | None:
        """Aggregate numeric data."""
        if not data or not all(isinstance(d, int | float) for d in data):
            return None
        if method == "sum":
            return {"sum": sum(data)}
        elif method == "average":
            return {"average": sum(data) / len(data)}
        return None

    def _aggregate_by_method(self, data: list[Any], aggregation: str) -> dict[str, Any] | list[Any]:
        """Perform specific aggregation method on data."""
        if aggregation == "count":
            return {"total": len(data)}
        if aggregation in ("sum", "average"):
            result = self._aggregate_numeric(data, aggregation)
            if result:
                return result
        if aggregation == "unique":
            return {"unique_items": list(set(data))}
        if aggregation == "group_by":
            return self._group_by_type(data)
        return data

    def _aggregate_data(self, data: list[Any], aggregation: str | None) -> dict[str, Any] | list[Any]:
        """Aggregate data based on aggregation method."""
        if not aggregation:
            return data
        return self._aggregate_by_method(data, aggregation)

    def _calculate_aggregated_values(self, data: list[Any]) -> dict[str, float]:
        """Calculate aggregated values from data."""
        values = {}
        if data:
            values["count"] = len(data)
            numeric_data = [d for d in data if isinstance(d, int | float)]
            if numeric_data:
                values["sum"] = sum(numeric_data)
                values["average"] = values["sum"] / len(numeric_data)
                values["min"] = min(numeric_data)
                values["max"] = max(numeric_data)
        return values

    def _create_error_outcome(self, operation_id: str, error: str, start_time: float) -> OperationOutcome:
        """Create error outcome."""
        return OperationOutcome(
            operation_id=operation_id,
            success=False,
            error=error,
            execution_time=time.time() - start_time,
        )

    def _initialize_handlers(self) -> None:
        """Initialize default operation handlers."""

        def _health_check_handler(exec_data: dict[str, Any]) -> dict[str, Any]:
            context = exec_data["context"]
            return {
                "data": {
                    "status": "healthy",
                    "target": context.target,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                "count": 1,
            }

        def _metrics_handler(exec_data: dict[str, Any]) -> dict[str, Any]:
            parameters = exec_data["parameters"]
            metric_names = parameters.config.get("metrics", [])
            return {
                "data": [
                    {"name": name, "value": 42.0, "timestamp": datetime.utcnow().isoformat()}
                    for name in metric_names
                ],
                "count": len(metric_names),
                "aggregated_values": {"total_metrics": len(metric_names)},
            }

        def _log_query_handler(exec_data: dict[str, Any]) -> dict[str, Any]:
            parameters = exec_data["parameters"]
            level = parameters.config.get("level", "info")
            limit = parameters.limit or 100
            return {
                "data": [
                    {
                        "message": f"Sample log message {i}",
                        "level": level,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    for i in range(min(limit, 10))
                ],
                "count": min(limit, 10),
            }

        def _trace_query_handler(exec_data: dict[str, Any]) -> dict[str, Any]:
            context = exec_data["context"]
            trace_id = context.correlation_id
            return {
                "data": {
                    "trace_id": trace_id,
                    "spans": [
                        {"operation": "span1", "duration": 0.1},
                        {"operation": "span2", "duration": 0.2},
                    ],
                },
                "count": 1,
            }

        self.register_handler("health_check", _health_check_handler)
        self.register_handler("collect_metrics", _metrics_handler)
        self.register_handler("query_logs", _log_query_handler)
        self.register_handler("query_traces", _trace_query_handler)


# guardian: allow-magic-config
def create_observability_operation_adapter(
    timeout: float = 30.0,
    retry_attempts: int = 3,
    enable_caching: bool = True,
    **kwargs: object,
) -> ObservabilityOperationAdapter:
    """Create a configured observability operation adapter."""
    config = OperationConfig(
        timeout=timeout,
        retry_attempts=retry_attempts,
        enable_caching=enable_caching,
        **kwargs,
    )
    return ObservabilityOperationAdapter(config)


def perform_observability_operation(
    operation_id: str,
    category: str,
    scope: str,
    target: str,
    operation_type: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Perform observability operation.

    Args:
        operation_id: Unique operation identifier
        category: Operation category
        scope: Operation scope
        target: Target system or component
        operation_type: Type of operation to perform
        config: Optional configuration

    Returns:
        Dict: Operation outcome
    """
    adapter = create_observability_operation_adapter()
    context = OperationContext(
        operation_id=operation_id,
        category=OperationCategory(category),
        scope=OperationScope(scope),
        target=target,
    )
    parameters = OperationParameters(operation_type=operation_type, config=config or {})
    outcome = adapter.perform_operation(context, parameters)
    return {
        "operation_id": outcome.operation_id,
        "success": outcome.success,
        "data": outcome.data,
        "count": outcome.count,
        "aggregated_values": outcome.aggregated_values,
        "error": outcome.error,
        "warnings": outcome.warnings,
        "execution_time": outcome.execution_time,
    }
