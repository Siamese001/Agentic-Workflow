from __future__ import annotations

"""
Execution Strategy Interface and Implementations

Provides pluggable execution strategies for the UnifiedWorkflowEngine:
- DAGStrategy: Directed Acyclic Graph-based execution
- StateMachineStrategy: State machine-based execution
- EventDrivenStrategy: Event-driven execution
- ReactiveStrategy: Reactive stream-based execution
"""


import asyncio
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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
        completed = set()
        results = {}
        steps_executed = 0

        # Build dependency graph
        {step.step_id: step for step in steps}

        while len(completed) < len(steps):
            # Find ready steps (all dependencies completed)
            ready = [
                step
                for step in steps
                if step.step_id not in completed and all(dep in completed for dep in step.dependencies)
            ]

            if not ready:
                # Deadlock or circular dependency
                return WorkflowResult(
                    workflow_id=context.workflow_id,
                    status=ExecutionStatus.FAILED,
                    error="Circular dependency detected",
                    steps_executed=steps_executed,
                )

            # Execute ready steps in parallel
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
        current_state = "start"
        steps_executed = 0
        results = {}

        # Build state transition map
        state_map = {step.step_id: step for step in steps}

        while current_state != "end" and steps_executed < len(steps) * 2:
            if current_state not in state_map and current_state != "start":
                return WorkflowResult(
                    workflow_id=context.workflow_id,
                    status=ExecutionStatus.COMPLETED,
                    output=results,
                    steps_executed=steps_executed,
                )

            # Get current step
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

                # Transition to next state
                next_state = result.get("next_state") if isinstance(result, dict) else None
                if next_state:
                    current_state = next_state
                else:
                    # Linear progression
                    idx = steps.index(step)
                    if idx + 1 < len(steps):
                        current_state = steps[idx + 1].step_id
                    else:
                        current_state = "end"

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
        event_queue = asyncio.Queue()
        results = {}
        steps_executed = 0

        # Initialize with first step
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

                # Emit next events
                next_events = result.get("emit") if isinstance(result, dict) else None
                if next_events:
                    for evt in next_events:
                        await event_queue.put(evt)
                else:
                    # Auto-emit next step
                    idx = steps.index(step)
                    if idx + 1 < len(steps):
                        await event_queue.put(steps[idx + 1].step_id)
                    else:
                        await event_queue.put("complete")

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
        results = {}
        steps_executed = 0

        # Create pipeline of steps
        current_value = context.input_data

        for step in steps:
            try:
                # Each step transforms the value
                result = await self._execute_step(step, context, current_value)
                results[step.step_id] = result
                current_value = result
                steps_executed += 1
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


# Strategy registry
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
    return STRATEGY_REGISTRY["dag"]  # Default
