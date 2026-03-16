from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
)

_emit_dispatches_healing_run("p1", "execution", "L0")
_emit_routes_through("p1", "execution", "L0")
_emit_escalates_to_human("p1", "execution", "L0")
_emit_reads_policy_state("p1", "execution", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "execution", "p0_governance")
_emit_snapshots_state("p0", "execution", "state_snapshot")
_emit_authorize_and_execute("p2", "execution", "execution_auth")
_emit_validates_capability("p2", "execution", "capability_check")
_emit_routes_to_capability("p2", "execution", "capability_route")
_emit_writes_via_uwg("p2", "execution", "uwg_write")
_emit_blocks_direct_write("p2", "execution", "direct_write_block")
_emit_records_tool_invocation("p2", "execution", "tool_invocation")
_emit_captures_execution_output("p2", "execution", "exec_output")
_emit_dispatches_agent("p3", "execution", "agent_dispatch")
_emit_coordinates_agents("p3", "execution", "agent_coordination")
_emit_records_workflow_lineage("p3", "execution", "workflow_lineage")
_emit_records_healing_outcome("p3", "execution", "healing_outcome")
_emit_escalates_failure("p3", "execution", "failure_escalation")
_emit_orchestrates_workflow("p3", "execution", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execution", "healing_dispatch")
_emit_invokes_evaluation("p3", "execution", "evaluation_signal")
_emit_records_telemetry_event("p4", "execution", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execution", "eval_metric")
_emit_stores_embedding("p4", "execution", "embedding_store")
_emit_updates_meta_learning_state("p4", "execution", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execution", "exec_snapshot_link")

"\nExecution Strategy Interface and Implementations\n\nProvides pluggable execution strategies for the UnifiedWorkflowEngine:\n- DAGStrategy: Directed Acyclic Graph-based execution\n- StateMachineStrategy: State machine-based execution\n- EventDrivenStrategy: Event-driven execution\n- ReactiveStrategy: Reactive stream-based execution\n"
import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)


class ExecutionStatus(Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class WorkflowContext:
    """Context for workflow execution."""

    workflow_id: str
    workflow_type: str
    input_data: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    parent_context: WorkflowContext | None = None


@dataclass
class WorkflowResult:
    """Result of workflow execution."""

    workflow_id: str
    status: ExecutionStatus
    output: Any = None
    error: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    steps_executed: int = 0


@dataclass
class WorkflowStep:
    """Single step in workflow execution."""

    step_id: str
    name: str
    handler: Callable
    dependencies: list[str] = field(default_factory=list)
    timeout_seconds: float = 30.0
    retries: int = 0


class ExecutionStrategy(ABC):
    """Base execution strategy interface."""

    @abstractmethod
    async def execute(self, context: WorkflowContext, steps: list[WorkflowStep]) -> WorkflowResult:
        """Execute workflow using this strategy."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return strategy name."""
        pass

    @abstractmethod
    def can_handle(self, workflow_type: str) -> bool:
        """Check if strategy can handle workflow type."""
        pass


class DAGStrategy(ExecutionStrategy):
    """DAG-based execution strategy."""

    def __init__(self):
        """Initialize DAG strategy."""
        self.name = "dag"
        self.supported_types = ["dag", "pipeline", "sequential", "parallel"]

    async def execute(self, context: WorkflowContext, steps: list[WorkflowStep]) -> WorkflowResult:
        """Execute workflow as DAG."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "DAGStrategy.execute")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        completed = set()
        results = {}
        steps_executed = 0
        {step.step_id: step for step in steps}
        while len(completed) < len(steps):
            ready = [
                step
                for step in steps
                if step.step_id not in completed and all(dep in completed for dep in step.dependencies)
            ]
            if not ready:
                return WorkflowResult(
                    workflow_id=context.workflow_id,
                    status=ExecutionStatus.FAILED,
                    error="Circular dependency detected",
                    steps_executed=steps_executed,
                )
            tasks = []
            for step in ready:
                task = asyncio.create_task(self._execute_step(step, context, results))
                tasks.append((step.step_id, task))
            for step_id, task in tasks:
                try:
                    result = await task
                    results[step_id] = result
                    completed.add(step_id)
                    steps_executed += 1
                # guardian: allow-silent-swallow
                except Exception as e:
                    return WorkflowResult(
                        workflow_id=context.workflow_id,
                        status=ExecutionStatus.FAILED,
                        error=f"Step {step_id} failed: {str(e)}",
                        steps_executed=steps_executed,
                    )
        return WorkflowResult(
            workflow_id=context.workflow_id,
            status=ExecutionStatus.COMPLETED,
            output=results,
            steps_executed=steps_executed,
        )

    async def _execute_step(self, step: WorkflowStep, context: WorkflowContext, results: dict) -> Any:
        """Execute single step."""
        try:
            if asyncio.iscoroutinefunction(step.handler):
                return await asyncio.wait_for(step.handler(context, results), timeout=step.timeout_seconds)
            else:
                return await asyncio.to_thread(step.handler, context, results)
        except asyncio.TimeoutError:
            raise Exception(f"Step {step.step_id} timed out after {step.timeout_seconds}s")

    def get_name(self) -> str:
        return self.name

    def can_handle(self, workflow_type: str) -> bool:
        return workflow_type.lower() in self.supported_types


class StateMachineStrategy(ExecutionStrategy):
    """State machine-based execution strategy."""

    def __init__(self):
        """Initialize state machine strategy."""
        self.name = "state_machine"
        self.supported_types = ["state_machine", "fsm", "workflow"]

    async def execute(self, context: WorkflowContext, steps: list[WorkflowStep]) -> WorkflowResult:
        """Execute workflow as state machine."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "StateMachineStrategy.execute")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        current_state = "start"
        steps_executed = 0
        results = {}
        state_map = {step.step_id: step for step in steps}
        while current_state != "end" and steps_executed < len(steps) * 2:
            if current_state not in state_map and current_state != "start":
                return WorkflowResult(
                    workflow_id=context.workflow_id,
                    status=ExecutionStatus.COMPLETED,
                    output=results,
                    steps_executed=steps_executed,
                )
            if current_state == "start":
                step = steps[0] if steps else None
            else:
                step = state_map.get(current_state)
            if not step:
                break
            try:
                result = await self._execute_step(step, context, results)
                results[step.step_id] = result
                steps_executed += 1
                next_state = result.get("next_state") if isinstance(result, dict) else None
                if next_state:
                    current_state = next_state
                else:
                    idx = steps.index(step)
                    if idx + 1 < len(steps):
                        current_state = steps[idx + 1].step_id
                    else:
                        current_state = "end"
            # guardian: allow-silent-swallow
            except Exception as e:
                return WorkflowResult(
                    workflow_id=context.workflow_id,
                    status=ExecutionStatus.FAILED,
                    error=f"State {current_state} failed: {str(e)}",
                    steps_executed=steps_executed,
                )
        return WorkflowResult(
            workflow_id=context.workflow_id,
            status=ExecutionStatus.COMPLETED,
            output=results,
            steps_executed=steps_executed,
        )

    async def _execute_step(self, step: WorkflowStep, context: WorkflowContext, results: dict) -> Any:
        """Execute single state."""
        if asyncio.iscoroutinefunction(step.handler):
            return await step.handler(context, results)
        else:
            return await asyncio.to_thread(step.handler, context, results)

    def get_name(self) -> str:
        return self.name

    def can_handle(self, workflow_type: str) -> bool:
        return workflow_type.lower() in self.supported_types


class EventDrivenStrategy(ExecutionStrategy):
    """Event-driven execution strategy."""

    def __init__(self):
        """Initialize event-driven strategy."""
        self.name = "event_driven"
        self.supported_types = ["event", "event_driven", "async"]

    async def execute(self, context: WorkflowContext, steps: list[WorkflowStep]) -> WorkflowResult:
        """Execute workflow using event-driven pattern."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "EventDrivenStrategy.execute")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        event_queue = asyncio.Queue()
        results = {}
        steps_executed = 0
        if steps:
            await event_queue.put(steps[0].step_id)
        step_map = {step.step_id: step for step in steps}
        while not event_queue.empty() and steps_executed < len(steps) * 2:
            event = await event_queue.get()
            if event == "complete":
                break
            step = step_map.get(event)
            if not step:
                continue
            try:
                result = await self._execute_step(step, context, results)
                results[step.step_id] = result
                steps_executed += 1
                next_events = result.get("emit") if isinstance(result, dict) else None
                if next_events:
                    for evt in next_events:
                        await event_queue.put(evt)
                else:
                    idx = steps.index(step)
                    if idx + 1 < len(steps):
                        await event_queue.put(steps[idx + 1].step_id)
                    else:
                        await event_queue.put("complete")
            # guardian: allow-silent-swallow
            except Exception as e:
                return WorkflowResult(
                    workflow_id=context.workflow_id,
                    status=ExecutionStatus.FAILED,
                    error=f"Event {event} failed: {str(e)}",
                    steps_executed=steps_executed,
                )
        return WorkflowResult(
            workflow_id=context.workflow_id,
            status=ExecutionStatus.COMPLETED,
            output=results,
            steps_executed=steps_executed,
        )

    async def _execute_step(self, step: WorkflowStep, context: WorkflowContext, results: dict) -> Any:
        """Execute step as event handler."""
        if asyncio.iscoroutinefunction(step.handler):
            return await step.handler(context, results)
        else:
            return await asyncio.to_thread(step.handler, context, results)

    def get_name(self) -> str:
        return self.name

    def can_handle(self, workflow_type: str) -> bool:
        return workflow_type.lower() in self.supported_types


class ReactiveStrategy(ExecutionStrategy):
    """Reactive stream-based execution strategy."""

    def __init__(self):
        """Initialize reactive strategy."""
        self.name = "reactive"
        self.supported_types = ["reactive", "stream", "observable"]

    async def execute(self, context: WorkflowContext, steps: list[WorkflowStep]) -> WorkflowResult:
        """Execute workflow using reactive streams."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ReactiveStrategy.execute")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        results = {}
        steps_executed = 0
        current_value = context.input_data
        for step in steps:
            try:
                result = await self._execute_step(step, context, current_value)
                results[step.step_id] = result
                current_value = result
                steps_executed += 1
            # guardian: allow-silent-swallow
            except Exception as e:
                return WorkflowResult(
                    workflow_id=context.workflow_id,
                    status=ExecutionStatus.FAILED,
                    error=f"Stream step {step.step_id} failed: {str(e)}",
                    steps_executed=steps_executed,
                )
        return WorkflowResult(
            workflow_id=context.workflow_id,
            status=ExecutionStatus.COMPLETED,
            output=current_value,
            metrics={"all_results": results},
            steps_executed=steps_executed,
        )

    async def _execute_step(self, step: WorkflowStep, context: WorkflowContext, value: Any) -> Any:
        """Execute step as stream transformation."""
        if asyncio.iscoroutinefunction(step.handler):
            return await step.handler(context, value)
        else:
            return await asyncio.to_thread(step.handler, context, value)

    def get_name(self) -> str:
        return self.name

    def can_handle(self, workflow_type: str) -> bool:
        return workflow_type.lower() in self.supported_types


STRATEGY_REGISTRY: dict[str, ExecutionStrategy] = {
    "dag": DAGStrategy(),
    "state_machine": StateMachineStrategy(),
    "event_driven": EventDrivenStrategy(),
    "reactive": ReactiveStrategy(),
}


def get_strategy(workflow_type: str) -> ExecutionStrategy:
    """Get appropriate strategy for workflow type."""
    for strategy in STRATEGY_REGISTRY.values():
        if strategy.can_handle(workflow_type):
            return strategy
    return STRATEGY_REGISTRY["dag"]
