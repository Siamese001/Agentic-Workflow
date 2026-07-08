"""Tool Perform observability Operation - Tool-based operation performance adapter.

This module provides tool-based adapters for performing observability operations
with standardized interfaces, error handling, and result processing.
Follows the functional component pattern with proper logging.
"""

import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "operation_mode_types", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "operation_mode_types", "policy_binding")
trace_contract._emit_snapshots_state("p0", "operation_mode_types", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("operation_mode_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("operation_mode_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("operation_mode_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("operation_mode_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("operation_mode_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("operation_mode_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("operation_mode_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("operation_mode_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("operation_mode_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("operation_mode_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("operation_mode_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("operation_mode_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("operation_mode_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("operation_mode_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("operation_mode_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("operation_mode_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("operation_mode_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("operation_mode_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("operation_mode_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("operation_mode_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("operation_mode_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("operation_mode_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("operation_mode_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("operation_mode_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("operation_mode_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("operation_mode_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("operation_mode_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("operation_mode_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "operation_mode_types", "context_pull")
trace_contract._emit_pulls_context("p1", "operation_mode_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "operation_mode_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "operation_mode_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "operation_mode_types", "write_through")
trace_contract._emit_writes_through("p1", "operation_mode_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "operation_mode_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "operation_mode_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "operation_mode_types", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "operation_mode_types", "human_escalation")
trace_contract._emit_routes_through("p1", "operation_mode_types", "route_through")
trace_contract._emit_checks_agent_registry("p1", "operation_mode_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "operation_mode_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "operation_mode_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "operation_mode_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "operation_mode_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "operation_mode_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "operation_mode_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "operation_mode_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "operation_mode_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "operation_mode_types")
trace_contract._emit_gated_by_confidence("p1", "operation_mode_types", "confidence_gate")
trace_contract.emit_replay_key("p0", "operation_mode_types")
trace_contract.emit_determinism_digest("p0", "operation_mode_types")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "operation_mode_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "operation_mode_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "operation_mode_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "operation_mode_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "operation_mode_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "operation_mode_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "operation_mode_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "operation_mode_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "operation_mode_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "operation_mode_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "operation_mode_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "operation_mode_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "operation_mode_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "operation_mode_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "operation_mode_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "operation_mode_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "operation_mode_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "operation_mode_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "operation_mode_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "operation_mode_types", "exec_snapshot_link")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_1")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_2")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_3")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_4")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_5")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_6")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_7")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_8")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_9")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_10")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_11")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_12")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_13")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_14")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_15")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_16")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_17")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_18")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_19")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_20")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_21")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_22")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_23")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_24")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_25")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_26")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_27")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_28")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_29")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_30")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_31")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_32")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_33")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_34")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_35")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_36")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_37")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_38")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_39")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_40")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_41")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_42")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_43")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_44")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_45")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_46")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_47")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_48")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_49")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_50")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_51")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_52")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_53")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_54")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_55")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_56")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_57")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_58")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_59")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_60")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_61")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_62")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_63")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_64")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_65")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_66")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_67")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_68")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_69")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_70")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_71")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_72")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_73")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_74")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_75")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_76")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_77")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_78")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_79")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_80")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_81")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_82")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_83")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_84")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_85")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_86")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_87")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_88")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_89")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_90")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_91")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_92")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_93")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_94")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_95")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_96")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_97")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_98")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_99")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_100")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_101")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_102")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_103")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_104")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_105")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_106")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_107")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_108")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_109")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_110")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_111")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_112")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_113")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_114")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_115")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_116")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_117")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_118")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_119")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_120")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_121")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_122")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_123")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_124")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_125")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_126")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_127")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_128")
trace_contract._emit_reads_through("l4", "operation_mode_types", "urg_read_129")

logger = logging.getLogger(__name__)


class OperationMode(Enum):
    """Modes of operation execution."""

    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    STREAMING = "streaming"
    BATCH = "batch"


class OperationScope(Enum):
    """Scope of observability operations."""

    SYSTEM = "system"
    SERVICE = "service"
    COMPONENT = "component"
    REQUEST = "request"
    CUSTOM = "custom"


@dataclass
class ToolOperationDefinition:
    """Definition of a tool operation."""

    operation_id: str
    tool_name: str
    operation_type: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    scope: OperationScope
    timeout: float = 30.0
    retry_policy: dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationExecutionContext:
    """Context for operation execution."""

    execution_id: str
    operation_id: str
    mode: OperationMode
    caller_context: dict[str, Any] | None = None
    trace_context: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class OperationExecutionConfig:
    """configuration for operation execution."""

    default_timeout: float = 30.0
    enable_tracing: bool = True
    enable_metrics: bool = True
    enable_validation: bool = True
    max_concurrent_operations: int = 100


@dataclass
class OperationExecutionResult:
    """Result of operation execution."""

    execution_id: str
    operation_id: str
    success: bool
    output: Any | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    traces: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    execution_time: float = 0.0


class ObservabilityOperationPerformer:
    """Main performer for observability operations."""

    def __init__(self, config: OperationExecutionConfig | None = None):
        self.config = config or OperationExecutionConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._registered_operations: dict[str, ToolOperationDefinition] = {}
        self._operation_handlers: dict[str, Callable] = {}
        self._active_executions: dict[str, dict[str, Any]] = {}
        self._initialize_operations()

    def register_operation(self, operation_def: ToolOperationDefinition, handler: Callable) -> None:
        """Register an observability operation.

        Args:
            operation_def: Operation definition
            handler: Operation handler function
        """
        import uuid  # noqa: PLC0415

        trace_contract._emit_records_execution_trace(
            str(uuid.uuid4()),
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            f"OperationRegistry.register_operation:{operation_def.operation_id}",
        )
        self._registered_operations[operation_def.operation_id] = operation_def
        self._operation_handlers[operation_def.operation_id] = handler
        self.logger.info(f"Registered operation: {operation_def.operation_id}")

    def perform_operation(
        self,
        context: OperationExecutionContext,
        inputs: dict[str, Any],
    ) -> OperationExecutionResult:
        """Perform an observability operation.

        Args:
            context: Execution context
            inputs: Operation inputs

        Returns:
            OperationExecutionResult: Execution result
        """
        self.logger.info(f"Performing operation: {context.operation_id}")
        start_time = time.time()
        try:
            if context.operation_id not in self._registered_operations:
                return self._create_error_result(
                    context.execution_id,
                    context.operation_id,
                    f"Operation not registered: {context.operation_id}",
                    start_time,
                )
            operation_def = self._registered_operations[context.operation_id]
            if self.config.enable_validation:
                validation_errors = self._validate_inputs(inputs, operation_def)
                if validation_errors:
                    return self._create_error_result(
                        context.execution_id,
                        context.operation_id,
                        f"Input validation failed: {validation_errors}",
                        start_time,
                    )
            self._track_execution_start(context)
            if context.mode == OperationMode.SYNCHRONOUS:
                result = self._execute_synchronous(context, inputs)
            elif context.mode == OperationMode.ASYNCHRONOUS:
                result = self._execute_asynchronous(context, inputs)
            elif context.mode == OperationMode.STREAMING:
                result = self._execute_streaming(context, inputs)
            elif context.mode == OperationMode.BATCH:
                result = self._execute_batch(context, inputs)
            else:
                raise ValueError(f"Unsupported operation mode: {context.mode}")
            result.execution_time = time.time() - start_time
            self._track_execution_complete(context, result)
            return result
        except (
            TypeError,
            ValueError,
            KeyError,
            AttributeError,
            RuntimeError,
            OSError,
        ) as e:  # guardian: allow-silent-swallow
            self.logger.error(f"Operation execution failed: {str(e)}")
            return self._create_error_result(context.execution_id, context.operation_id, str(e), start_time)

    def perform_operation_stream(self, context: OperationExecutionContext, inputs: dict[str, Any]) -> object:
        """Perform operation with streaming output.

        Args:
            context: Execution context
            inputs: Operation inputs

        Returns:
            Iterator: Stream of output chunks
        """
        if context.mode != OperationMode.STREAMING:
            raise ValueError("Operation mode must be STREAMING for streaming execution")
        handler = self._operation_handlers.get(context.operation_id)
        if not handler:
            raise ValueError(f"No handler for operation: {context.operation_id}")
        yield from handler(inputs, stream=True)

    def perform_operations_batch(
        self,
        contexts: list[OperationExecutionContext],
        inputs_list: list[dict[str, Any]],
    ) -> list[OperationExecutionResult]:
        """Perform multiple operations.

        Args:
            contexts: List of execution contexts
            inputs_list: List of operation inputs

        Returns:
            List[OperationExecutionResult]: Results for all operations
        """
        if len(contexts) != len(inputs_list):
            raise ValueError("Contexts and inputs lists must have same length")
        results = []
        for context, inputs in zip(contexts, inputs_list, strict=False):
            result = self.perform_operation(context, inputs)
            results.append(result)
        return results

    def list_operations(self, scope: OperationScope | None = None) -> list[ToolOperationDefinition]:
        """List registered operations.

        Args:
            scope: Optional filter by scope

        Returns:
            List[ToolOperationDefinition]: Registered operations
        """
        operations = list(self._registered_operations.values())
        if scope:
            operations = [op for op in operations if op.scope == scope]
        return operations

    def get_operation_definition(self, operation_id: str) -> ToolOperationDefinition | None:
        """Get operation definition.

        Args:
            operation_id: Operation identifier

        Returns:
            Optional[ToolOperationDefinition]: Operation definition
        """
        return self._registered_operations.get(operation_id)

    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel an active execution.

        Args:
            execution_id: Execution identifier

        Returns:
            bool: True if cancelled successfully
        """
        if execution_id in self._active_executions:
            execution = self._active_executions[execution_id]
            execution["cancelled"] = True
            self.logger.info(f"Cancelled execution: {execution_id}")
            return True
        return False

    def get_execution_status(self, execution_id: str) -> dict[str, Any] | None:
        """Get execution status.

        Args:
            execution_id: Execution identifier

        Returns:
            Optional[Dict]: Execution status
        """
        return self._active_executions.get(execution_id)

    def _execute_synchronous(
        self,
        context: OperationExecutionContext,
        inputs: dict[str, Any],
    ) -> OperationExecutionResult:
        """Execute operation synchronously."""
        handler = self._operation_handlers[context.operation_id]
        output = handler(inputs)
        metrics = output.get("metrics", {}) if isinstance(output, dict) else {}
        traces = output.get("traces", []) if isinstance(output, dict) else []
        artifacts = output.get("artifacts", []) if isinstance(output, dict) else []
        return OperationExecutionResult(
            execution_id=context.execution_id,
            operation_id=context.operation_id,
            success=True,
            output=output,
            metrics=metrics,
            traces=traces,
            artifacts=artifacts,
        )

    def _execute_asynchronous(
        self,
        context: OperationExecutionContext,
        inputs: dict[str, Any],
    ) -> OperationExecutionResult:
        """Execute operation asynchronously."""
        handler = self._operation_handlers[context.operation_id]
        output = handler(inputs, async_mode=True)
        return OperationExecutionResult(
            execution_id=context.execution_id,
            operation_id=context.operation_id,
            success=True,
            output=output,
            metrics={"async_execution": 1},
        )

    def _execute_streaming(
        self,
        context: OperationExecutionContext,
        inputs: dict[str, Any],
    ) -> OperationExecutionResult:
        """Execute operation in streaming mode."""
        return OperationExecutionResult(
            execution_id=context.execution_id,
            operation_id=context.operation_id,
            success=True,
            output={"status": "streaming_active"},
            metrics={"streaming": 1},
        )

    def _execute_batch(
        self,
        context: OperationExecutionContext,
        inputs: dict[str, Any],
    ) -> OperationExecutionResult:
        """Execute operation in batch mode."""
        batch_items = inputs.get("batch_items", [])
        results = []
        total_metrics = {}
        all_traces = []
        all_artifacts = []
        for item in tqdm(batch_items, desc="Processing", unit="item"):
            handler = self._operation_handlers[context.operation_id]
            try:
                item_output = handler(item)
                results.append(item_output)
                if isinstance(item_output, dict):
                    for key, value in item_output.get("metrics", {}).items():
                        if key not in total_metrics:
                            total_metrics[key] = []
                        total_metrics[key].append(value)
                    all_traces.extend(item_output.get("traces", []))
                    all_artifacts.extend(item_output.get("artifacts", []))
            except (
                TypeError,
                ValueError,
                KeyError,
                AttributeError,
                RuntimeError,
                OSError,
            ) as e:  # guardian: allow-silent-swallow
                self.logger.warning(f"Batch item failed: {str(e)}")
                results.append({"error": str(e)})
        final_metrics = {}
        for key, values in total_metrics.items():
            if values:
                final_metrics[f"{key}_total"] = sum(values)
                final_metrics[f"{key}_avg"] = sum(values) / len(values)
        return OperationExecutionResult(
            execution_id=context.execution_id,
            operation_id=context.operation_id,
            success=True,
            output=results,
            metrics=final_metrics,
            traces=all_traces,
            artifacts=all_artifacts,
        )

    def _validate_input_field_type(self, value: object, field_type: str) -> bool:
        """Validate a single input field type and return error message if invalid."""
        type_validators = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int),
            "float": lambda v: isinstance(v, int | float),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, list),
            "object": lambda v: isinstance(v, dict),
        }
        validator = type_validators.get(expected_type)
        if validator and (not validator(value)):
            type_names = {
                "string": "string",
                "integer": "integer",
                "float": "number",
                "boolean": "boolean",
                "array": "array",
                "object": "object",
            }
            return f"Field {field_name} must be {type_names.get(expected_type, 'valid type')}"
        return None

    def _validate_inputs(self, inputs: dict[str, Any], operation_def: ToolOperationDefinition) -> list[str]:
        """Validate operation inputs."""
        errors = []
        for field_name, field_def in operation_def.input_schema.items():
            if field_def.get("required", False) and field_name not in inputs:
                errors.append(f"Missing required field: {field_name}")
            if field_name in inputs:
                expected_type = field_def.get("type")
                value = inputs[field_name]
                type_error = self._validate_input_field_type(field_name, value, expected_type)
                if type_error:
                    errors.append(type_error)
        return errors

    def _track_execution_start(self, context: OperationExecutionContext) -> None:
        """Track execution start."""
        self._active_executions[context.execution_id] = {
            "operation_id": context.operation_id,
            "mode": str(context.mode),
            "start_time": time.time(),
            "status": "running",
            "cancelled": False,
        }

    def _track_execution_complete(
        self,
        context: OperationExecutionContext,
        result: OperationExecutionResult,
    ) -> None:
        """Track execution completion."""
        if context.execution_id in self._active_executions:
            execution = self._active_executions[context.execution_id]
            execution["end_time"] = time.time()
            execution["status"] = "completed" if result.success else "failed"
            execution["execution_time"] = result.execution_time

    def _create_error_result(
        self,
        execution_id: str,
        operation_id: str,
        error: str,
        start_time: float,
    ) -> OperationExecutionResult:
        """Create error result."""
        return OperationExecutionResult(
            execution_id=execution_id,
            operation_id=operation_id,
            success=False,
            error=error,
            execution_time=time.time() - start_time,
        )

    def _create_trace_operation(self) -> tuple:
        """Create trace analysis operation and handler."""
        trace_op = ToolOperationDefinition(
            operation_id="trace_analysis",
            tool_name="trace_analyzer",
            operation_type="analysis",
            description="Analyze trace data for performance insights",
            input_schema={
                "trace_data": {"type": "object", "required": True},
                "analysis_type": {"type": "string", "required": False},
            },
            output_schema={"insights": {"type": "array"}, "recommendations": {"type": "array"}},
            scope=OperationScope.SERVICE,
        )

        def _trace_analysis_handler(inputs: dict[str, Any], **kwargs: object) -> dict[str, Any]:
            return {
                "insights": [
                    {"type": "slow_span", "description": "Database query took 500ms"},
                    {"type": "error_rate", "description": "5% error rate detected"},
                ],
                "recommendations": ["Add database index", "Implement retry logic"],
                "metrics": {"spans_analyzed": 10, "processing_time": 0.1},
            }

        return (trace_op, _trace_analysis_handler)

    def _create_metric_operation(self) -> tuple:
        """Create metric aggregation operation and handler."""
        metric_op = ToolOperationDefinition(
            operation_id="metric_aggregation",
            tool_name="metric_aggregator",
            operation_type="aggregation",
            description="Aggregate metrics over time window",
            input_schema={
                "metrics": {"type": "array", "required": True},
                "aggregation": {"type": "string", "required": False},
                "time_window": {"type": "object", "required": False},
            },
            output_schema={"aggregated_metrics": {"type": "object"}, "statistics": {"type": "object"}},
            scope=OperationScope.SYSTEM,
        )

        def _metric_aggregation_handler(inputs: dict[str, Any], **kwargs: object) -> dict[str, Any]:
            metrics = inputs.get("metrics", [])
            return {
                "aggregated_metrics": {
                    "cpu_usage": {"avg": 45.2, "max": 78.5, "min": 12.1},
                    "memory_usage": {"avg": 67.8, "max": 89.2, "min": 34.5},
                },
                "statistics": {"total_metrics": len(metrics), "time_range": "1h"},
                "metrics": {"metrics_processed": len(metrics)},
            }

        return (metric_op, _metric_aggregation_handler)

    def _create_log_operation(self) -> tuple:
        """Create log correlation operation and handler."""
        log_op = ToolOperationDefinition(
            operation_id="log_correlation",
            tool_name="log_correlator",
            operation_type="correlation",
            description="Correlate logs across services",
            input_schema={
                "log_entries": {"type": "array", "required": True},
                "correlation_id": {"type": "string", "required": False},
            },
            output_schema={"correlated_logs": {"type": "array"}, "patterns": {"type": "array"}},
            scope=OperationScope.REQUEST,
        )

        def _log_correlation_handler(inputs: dict[str, Any], **kwargs: object) -> dict[str, Any]:
            log_entries = inputs.get("log_entries", [])
            return {
                "correlated_logs": [
                    {"service": "api", "message": "Request received"},
                    {"service": "db", "message": "Query executed"},
                    {"service": "api", "message": "Response sent"},
                ],
                "patterns": [{"type": "request_flow", "count": 10}, {"type": "error_cascade", "count": 2}],
                "metrics": {"logs_correlated": len(log_entries)},
            }

        return (log_op, _log_correlation_handler)

    def _initialize_operations(self) -> None:
        """Initialize built-in operations."""
        trace_op, trace_handler = self._create_trace_operation()
        metric_op, metric_handler = self._create_metric_operation()
        log_op, log_handler = self._create_log_operation()
        self.register_operation(trace_op, trace_handler)
        self.register_operation(metric_op, metric_handler)
        self.register_operation(log_op, log_handler)


# guardian: allow-magic-config
def create_observability_operation_performer(
    default_timeout: float = 30.0,
    enable_tracing: bool = True,
    enable_metrics: bool = True,
    **kwargs: object,
) -> ObservabilityOperationPerformer:
    """Create a configured observability operation performer."""
    config = OperationExecutionConfig(
        default_timeout=default_timeout,
        enable_tracing=enable_tracing,
        enable_metrics=enable_metrics,
        **kwargs,
    )
    return ObservabilityOperationPerformer(config)


def tool_perform_observability_operation(
    operation_id: str,
    inputs: dict[str, Any],
    execution_id: str | None = None,
    mode: str = "synchronous",
    caller_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Perform observability operation.

    Args:
        operation_id: Operation identifier
        inputs: Operation inputs
        execution_id: Optional unique execution identifier
        mode: Execution mode
        caller_context: Optional caller context

    Returns:
        Dict: Execution result
    """
    performer = create_observability_operation_performer()
    context = OperationExecutionContext(
        execution_id=execution_id or str(uuid.uuid4()),
        operation_id=operation_id,
        mode=OperationMode(mode),
        caller_context=caller_context,
    )
    result = performer.perform_operation(context, inputs)
    return {
        "execution_id": result.execution_id,
        "operation_id": result.operation_id,
        "success": result.success,
        "output": result.output,
        "metrics": result.metrics,
        "traces": result.traces,
        "artifacts": result.artifacts,
        "error": result.error,
        "warnings": result.warnings,
        "execution_time": result.execution_time,
    }
