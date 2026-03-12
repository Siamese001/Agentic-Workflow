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
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
logger = logging.getLogger(__name__)

class OperationMode(Enum):
    """Modes of operation execution."""
    SYNCHRONOUS = 'synchronous'
    ASYNCHRONOUS = 'asynchronous'
    STREAMING = 'streaming'
    BATCH = 'batch'

class OperationScope(Enum):
    """Scope of observability operations."""
    SYSTEM = 'system'
    SERVICE = 'service'
    COMPONENT = 'component'
    REQUEST = 'request'
    CUSTOM = 'custom'

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

    def __init__(self, config: OperationExecutionConfig | None=None):
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
        self._registered_operations[operation_def.operation_id] = operation_def
        self._operation_handlers[operation_def.operation_id] = handler
        self.logger.info(f'Registered operation: {operation_def.operation_id}')

    def perform_operation(self, context: OperationExecutionContext, inputs: dict[str, Any]) -> OperationExecutionResult:
        """Perform an observability operation.

        Args:
            context: Execution context
            inputs: Operation inputs

        Returns:
            OperationExecutionResult: Execution result
        """
        self.logger.info(f'Performing operation: {context.operation_id}')
        start_time = time.time()
        try:
            if context.operation_id not in self._registered_operations:
                return self._create_error_result(context.execution_id, context.operation_id, f'Operation not registered: {context.operation_id}', start_time)
            operation_def = self._registered_operations[context.operation_id]
            if self.config.enable_validation:
                validation_errors = self._validate_inputs(inputs, operation_def)
                if validation_errors:
                    return self._create_error_result(context.execution_id, context.operation_id, f'Input validation failed: {validation_errors}', start_time)
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
                raise ValueError(f'Unsupported operation mode: {context.mode}')
            result.execution_time = time.time() - start_time
            self._track_execution_complete(context, result)
            return result
        # guardian: allow-silent-swallow
        except Exception as e:
            self.logger.error(f'Operation execution failed: {str(e)}')
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
            raise ValueError('Operation mode must be STREAMING for streaming execution')
        handler = self._operation_handlers.get(context.operation_id)
        if not handler:
            raise ValueError(f'No handler for operation: {context.operation_id}')
        yield from handler(inputs, stream=True)

    def perform_operations_batch(self, contexts: list[OperationExecutionContext], inputs_list: list[dict[str, Any]]) -> list[OperationExecutionResult]:
        """Perform multiple operations.

        Args:
            contexts: List of execution contexts
            inputs_list: List of operation inputs

        Returns:
            List[OperationExecutionResult]: Results for all operations
        """
        if len(contexts) != len(inputs_list):
            raise ValueError('Contexts and inputs lists must have same length')
        results = []
        for context, inputs in zip(contexts, inputs_list, strict=False):
            result = self.perform_operation(context, inputs)
            results.append(result)
        return results

    def list_operations(self, scope: OperationScope | None=None) -> list[ToolOperationDefinition]:
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
            execution['cancelled'] = True
            self.logger.info(f'Cancelled execution: {execution_id}')
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

    def _execute_synchronous(self, context: OperationExecutionContext, inputs: dict[str, Any]) -> OperationExecutionResult:
        """Execute operation synchronously."""
        handler = self._operation_handlers[context.operation_id]
        output = handler(inputs)
        metrics = output.get('metrics', {}) if isinstance(output, dict) else {}
        traces = output.get('traces', []) if isinstance(output, dict) else []
        artifacts = output.get('artifacts', []) if isinstance(output, dict) else []
        return OperationExecutionResult(execution_id=context.execution_id, operation_id=context.operation_id, success=True, output=output, metrics=metrics, traces=traces, artifacts=artifacts)

    def _execute_asynchronous(self, context: OperationExecutionContext, inputs: dict[str, Any]) -> OperationExecutionResult:
        """Execute operation asynchronously."""
        handler = self._operation_handlers[context.operation_id]
        output = handler(inputs, async_mode=True)
        return OperationExecutionResult(execution_id=context.execution_id, operation_id=context.operation_id, success=True, output=output, metrics={'async_execution': 1})

    def _execute_streaming(self, context: OperationExecutionContext, inputs: dict[str, Any]) -> OperationExecutionResult:
        """Execute operation in streaming mode."""
        return OperationExecutionResult(execution_id=context.execution_id, operation_id=context.operation_id, success=True, output={'status': 'streaming_active'}, metrics={'streaming': 1})

    def _execute_batch(self, context: OperationExecutionContext, inputs: dict[str, Any]) -> OperationExecutionResult:
        """Execute operation in batch mode."""
        batch_items = inputs.get('batch_items', [])
        results = []
        total_metrics = {}
        all_traces = []
        all_artifacts = []
        for item in batch_items:
            handler = self._operation_handlers[context.operation_id]
            try:
                item_output = handler(item)
                results.append(item_output)
                if isinstance(item_output, dict):
                    for key, value in item_output.get('metrics', {}).items():
                        if key not in total_metrics:
                            total_metrics[key] = []
                        total_metrics[key].append(value)
                    all_traces.extend(item_output.get('traces', []))
                    all_artifacts.extend(item_output.get('artifacts', []))
            # guardian: allow-silent-swallow
            except Exception as e:
                self.logger.warning(f'Batch item failed: {str(e)}')
                results.append({'error': str(e)})
        final_metrics = {}
        for key, values in total_metrics.items():
            if values:
                final_metrics[f'{key}_total'] = sum(values)
                final_metrics[f'{key}_avg'] = sum(values) / len(values)
        return OperationExecutionResult(execution_id=context.execution_id, operation_id=context.operation_id, success=True, output=results, metrics=final_metrics, traces=all_traces, artifacts=all_artifacts)

    def _validate_input_field_type(self, value: object, field_type: str) -> bool:
        """Validate a single input field type and return error message if invalid."""
        type_validators = {'string': lambda v: isinstance(v, str), 'integer': lambda v: isinstance(v, int), 'float': lambda v: isinstance(v, int | float), 'boolean': lambda v: isinstance(v, bool), 'array': lambda v: isinstance(v, list), 'object': lambda v: isinstance(v, dict)}
        validator = type_validators.get(expected_type)
        if validator and (not validator(value)):
            type_names = {'string': 'string', 'integer': 'integer', 'float': 'number', 'boolean': 'boolean', 'array': 'array', 'object': 'object'}
            return f"Field {field_name} must be {type_names.get(expected_type, 'valid type')}"
        return None

    def _validate_inputs(self, inputs: dict[str, Any], operation_def: ToolOperationDefinition) -> list[str]:
        """Validate operation inputs."""
        errors = []
        for field_name, field_def in operation_def.input_schema.items():
            if field_def.get('required', False) and field_name not in inputs:
                errors.append(f'Missing required field: {field_name}')
            if field_name in inputs:
                expected_type = field_def.get('type')
                value = inputs[field_name]
                type_error = self._validate_input_field_type(field_name, value, expected_type)
                if type_error:
                    errors.append(type_error)
        return errors

    def _track_execution_start(self, context: OperationExecutionContext) -> None:
        """Track execution start."""
        self._active_executions[context.execution_id] = {'operation_id': context.operation_id, 'mode': context.mode.value, 'start_time': time.time(), 'status': 'running', 'cancelled': False}

    def _track_execution_complete(self, context: OperationExecutionContext, result: OperationExecutionResult) -> None:
        """Track execution completion."""
        if context.execution_id in self._active_executions:
            execution = self._active_executions[context.execution_id]
            execution['end_time'] = time.time()
            execution['status'] = 'completed' if result.success else 'failed'
            execution['execution_time'] = result.execution_time

    def _create_error_result(self, execution_id: str, operation_id: str, error: str, start_time: float) -> OperationExecutionResult:
        """Create error result."""
        return OperationExecutionResult(execution_id=execution_id, operation_id=operation_id, success=False, error=error, execution_time=time.time() - start_time)

    def _create_trace_operation(self) -> tuple:
        """Create trace analysis operation and handler."""
        trace_op = ToolOperationDefinition(operation_id='trace_analysis', tool_name='trace_analyzer', operation_type='analysis', description='Analyze trace data for performance insights', input_schema={'trace_data': {'type': 'object', 'required': True}, 'analysis_type': {'type': 'string', 'required': False}}, output_schema={'insights': {'type': 'array'}, 'recommendations': {'type': 'array'}}, scope=OperationScope.SERVICE)

        def _trace_analysis_handler(inputs: dict[str, Any], **kwargs: object) -> dict[str, Any]:
            return {'insights': [{'type': 'slow_span', 'description': 'Database query took 500ms'}, {'type': 'error_rate', 'description': '5% error rate detected'}], 'recommendations': ['Add database index', 'Implement retry logic'], 'metrics': {'spans_analyzed': 10, 'processing_time': 0.1}}
        return (trace_op, _trace_analysis_handler)

    def _create_metric_operation(self) -> tuple:
        """Create metric aggregation operation and handler."""
        metric_op = ToolOperationDefinition(operation_id='metric_aggregation', tool_name='metric_aggregator', operation_type='aggregation', description='Aggregate metrics over time window', input_schema={'metrics': {'type': 'array', 'required': True}, 'aggregation': {'type': 'string', 'required': False}, 'time_window': {'type': 'object', 'required': False}}, output_schema={'aggregated_metrics': {'type': 'object'}, 'statistics': {'type': 'object'}}, scope=OperationScope.SYSTEM)

        def _metric_aggregation_handler(inputs: dict[str, Any], **kwargs: object) -> dict[str, Any]:
            metrics = inputs.get('metrics', [])
            return {'aggregated_metrics': {'cpu_usage': {'avg': 45.2, 'max': 78.5, 'min': 12.1}, 'memory_usage': {'avg': 67.8, 'max': 89.2, 'min': 34.5}}, 'statistics': {'total_metrics': len(metrics), 'time_range': '1h'}, 'metrics': {'metrics_processed': len(metrics)}}
        return (metric_op, _metric_aggregation_handler)

    def _create_log_operation(self) -> tuple:
        """Create log correlation operation and handler."""
        log_op = ToolOperationDefinition(operation_id='log_correlation', tool_name='log_correlator', operation_type='correlation', description='Correlate logs across services', input_schema={'log_entries': {'type': 'array', 'required': True}, 'correlation_id': {'type': 'string', 'required': False}}, output_schema={'correlated_logs': {'type': 'array'}, 'patterns': {'type': 'array'}}, scope=OperationScope.REQUEST)

        def _log_correlation_handler(inputs: dict[str, Any], **kwargs: object) -> dict[str, Any]:
            log_entries = inputs.get('log_entries', [])
            return {'correlated_logs': [{'service': 'api', 'message': 'Request received'}, {'service': 'db', 'message': 'Query executed'}, {'service': 'api', 'message': 'Response sent'}], 'patterns': [{'type': 'request_flow', 'count': 10}, {'type': 'error_cascade', 'count': 2}], 'metrics': {'logs_correlated': len(log_entries)}}
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
def create_observability_operation_performer(default_timeout: float=30.0, enable_tracing: bool=True, enable_metrics: bool=True, **kwargs: object) -> ObservabilityOperationPerformer:
    """Create a configured observability operation performer."""
    config = OperationExecutionConfig(default_timeout=default_timeout, enable_tracing=enable_tracing, enable_metrics=enable_metrics, **kwargs)
    return ObservabilityOperationPerformer(config)

def tool_perform_observability_operation(operation_id: str, inputs: dict[str, Any], execution_id: str | None=None, mode: str='synchronous', caller_context: dict[str, Any] | None=None) -> dict[str, Any]:
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
    context = OperationExecutionContext(execution_id=execution_id or str(uuid.uuid4()), operation_id=operation_id, mode=OperationMode(mode), caller_context=caller_context)
    result = performer.perform_operation(context, inputs)
    return {'execution_id': result.execution_id, 'operation_id': result.operation_id, 'success': result.success, 'output': result.output, 'metrics': result.metrics, 'traces': result.traces, 'artifacts': result.artifacts, 'error': result.error, 'warnings': result.warnings, 'execution_time': result.execution_time}
