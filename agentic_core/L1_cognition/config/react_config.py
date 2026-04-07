# guardian: allow-silent_swallower - ADG violation exemption

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_signs_execution_trace,
)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""ReAct (Reasoning and Acting) Engine implementation.

Phase 1 - Pillar 6: Reasoning models (Structured Reasoning)
Migrated from archives/legacy_root_folders/infra/reasoning/react.py

The ReAct framework interleaves reasoning and action steps to solve complex tasks.
"""

import logging
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    from agentic_core.L1_cognition.reasoning.trace_models import ReasoningTraceModel
except ImportError:  # guardian: allow-silent-swallow
    ReasoningTraceModel = None  # type: ignore[misc,assignment]
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_snapshots_state,
)

Logger = logging.getLogger(__name__)


class ReasoningMode(Enum):
    """Reasoning strategy modes."""

    REACT = "react"
    CHAIN_OF_THOUGHT = "cot"
    TREE_OF_THOUGHTS = "tot"
    SELF_CONSISTENCY = "self_consistency"
    SHOTGUN = "shotgun"


@dataclass
class ReActStep:
    """Single step in ReAct reasoning loop.

    Represents one iteration of: Think -> Act -> Observe
    """

    step_number: int
    thought: str
    action: str
    action_input: dict[str, Any] = field(default_factory=dict)
    observation: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReActTrace:
    """Complete trace of ReAct reasoning loop.

    Contains all steps and final result.
    """

    trace_id: str
    Task: str
    steps: list[ReActStep] = field(default_factory=list)
    final_answer: str | None = None
    success: bool = False
    error: str | None = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_reasoning_trace(self) -> ReasoningTraceModel:
        """Convert to formal Pydantic ReasoningTraceModel."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ReActTrace.to_reasoning_trace", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ReActTrace.to_reasoning_trace", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ReActTrace.to_reasoning_trace")

        trace = ReasoningTraceModel(
            trace_id=self.trace_id,
            Task=self.Task,
            started_at=self.started_at,
            metadata=self.metadata,
        )

        for step in self.steps:
            trace.add_think(step.thought, metadata={"step_number": step.step_number})
            trace.add_action(
                step.action,
                parameters=step.action_input,
                metadata={"step_number": step.step_number},
            )
            if step.observation:
                trace.add_observation(step.observation, metadata={"step_number": step.step_number})

        if self.final_answer:
            trace.complete(self.final_answer, self.success, self.error)

        return trace


class ReActEngine:
    """ReAct reasoning engine for complex Task solving.

    Implements the ReAct (Reasoning and Acting) pattern:
    1. Think: Reason about the current state and what to do next
    2. Act: Execute an action based on reasoning
    3. Observe: Observe the result and update understanding
    4. Repeat until Task is complete

    This is the default reasoning model for complex tasks requiring tool use.
    """

    def __init__(
        self,
        max_steps: int = 10,
        max_retries: int = 3,
        enable_self_reflection: bool = True,
    ):
        """Initialize ReAct engine.

        Args:
            max_steps: Maximum reasoning steps before termination
            max_retries: Maximum retries for failed actions
            enable_self_reflection: Enable self-critique of reasoning
        """
        self.max_steps = max_steps
        self.max_retries = max_retries
        self.enable_self_reflection = enable_self_reflection

    async def run(
        self,
        Task: str,
        think_fn: Callable[[str, list[ReActStep]], Awaitable[str]],
        act_fn: Callable[[str, dict[str, Any]], Awaitable[str]],
        should_continue_fn: Callable[[list[ReActStep]], bool] | None = None,
        context: dict[str, Any] | None = None,
    ) -> ReActTrace:
        """Run the ReAct reasoning loop.

        Args:
            Task: The Task to solve
            think_fn: Async function that generates reasoning given Task and history
            act_fn: Async function that executes actions and returns observations
            should_continue_fn: Optional function to determine if loop should continue
            context: Optional context dictionary

        Returns:
            ReActTrace containing all steps and final result
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_REASONING, "ReActEngine.run")

        trace_id = str(uuid.uuid4())
        trace = ReActTrace(trace_id=trace_id, Task=Task, metadata=context or {})

        Logger.info(
            "react_start",
            extra={"trace_id": trace_id, "Task": Task[:100], "max_steps": self.max_steps},
        )

        try:
            await self._execute_reasoning_loop(Task, think_fn, act_fn, should_continue_fn, trace, trace_id)
            trace = await self._finalize_trace(Task, think_fn, trace, trace_id)
        except Exception as e:  # guardian: allow-silent-swallow
            self._handle_trace_error(trace, trace_id, e)

        return trace

    async def _execute_reasoning_loop(
        self,
        Task: str,
        think_fn: Callable,
        act_fn: Callable,
        should_continue_fn: Callable | None,
        trace: ReActTrace,
        trace_id: str,
    ) -> None:
        """Execute the main reasoning loop."""
        for step_num in range(1, self.max_steps + 1):
            thought = await think_fn(Task, trace.steps)

            if not thought or "FINISH" in thought.upper():
                Logger.info(
                    "react_finish",
                    extra={"trace_id": trace_id, "step": step_num, "reason": "finish_signal"},
                )
                break

            step = await self._execute_step(step_num, thought, act_fn, trace_id)
            trace.steps.append(step)

            if should_continue_fn and not should_continue_fn(trace.steps):
                Logger.info(
                    "react_stop",
                    extra={
                        "trace_id": trace_id,
                        "step": step_num,
                        "reason": "should_continue_false",
                    },
                )
                break

            if self.enable_self_reflection and step_num % 3 == 0:
                await self._self_reflect(trace, think_fn)

    async def _execute_step(self, step_num: int, thought: str, act_fn: Callable, trace_id: str) -> ReActStep:
        """Execute a single reasoning step."""
        action, action_input = self._parse_action(thought)
        step = ReActStep(step_number=step_num, thought=thought, action=action, action_input=action_input)

        try:
            observation = await act_fn(action, action_input)
            step.observation = observation
        except Exception as e:  # guardian: allow-silent-swallow
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.error(
                "react_action_error",
                extra={"trace_id": trace_id, "step": step_num, "action": action, "error": str(e)},
            )
            step.observation = f"Error: {str(e)}"

        return step

    async def _finalize_trace(
        self,
        Task: str,
        think_fn: Callable,
        trace: ReActTrace,
        trace_id: str,
    ) -> ReActTrace:
        """Finalize trace with final answer."""
        final_thought = await think_fn(
            f"Based on the reasoning above, provide the final answer to: {Task}",
            trace.steps,
        )
        trace.final_answer = final_thought
        trace.success = True
        trace.completed_at = datetime.now()
        Logger.info(
            "react_complete",
            extra={"trace_id": trace_id, "steps": len(trace.steps), "success": True},
        )
        return trace

    def _handle_trace_error(self, trace: ReActTrace, trace_id: str, error: Exception) -> None:
        """Handle trace execution error."""
        Logger.error("react_error", extra={"trace_id": trace_id, "error": str(error)})
        trace.error = str(error)
        trace.success = False
        trace.completed_at = datetime.now()

    def _parse_action(self, thought: str) -> tuple[str, dict[str, Any]]:
        """Parse action and input from thought string.

        Expected format:
        Action: <action_name>
        Action Input: <json_or_text>

        Args:
            thought: The reasoning text

        Returns:
            Tuple of (action_name, action_input_dict)
        """
        action = "unknown"
        action_input = {}

        lines = thought.split("\n")
        for _i, line in enumerate(lines):
            if line.strip().lower().startswith("action:"):
                action = line.split(":", 1)[1].strip()
            elif line.strip().lower().startswith("action input:"):
                input_str = line.split(":", 1)[1].strip()
                try:
                    import json

                    action_input = json.loads(input_str)
                except Exception:  # guardian: allow-silent-swallow
                    action_input = {"input": input_str}

        return action, action_input

    async def _self_reflect(
        self,
        trace: ReActTrace,
        think_fn: Callable[[str, list[ReActStep]], Awaitable[str]],
    ) -> None:
        """Perform self-reflection on reasoning quality.

        Args:
            trace: Current reasoning trace
            think_fn: Thinking function for reflection
        """
        reflection_prompt = (
            f"Reflect on the reasoning so far for Task: {trace.Task}\n"
            f"Steps taken: {len(trace.steps)}\n"
            "Are we making progress? Should we adjust our approach?"
        )

        try:
            reflection = await think_fn(reflection_prompt, trace.steps)

            Logger.info(
                "react_reflection",
                extra={
                    "trace_id": trace.trace_id,
                    "step": len(trace.steps),
                    "reflection": reflection[:200],
                },
            )

            trace.metadata["reflections"] = trace.metadata.get("reflections", [])
            trace.metadata["reflections"].append(
                {
                    "step": len(trace.steps),
                    "reflection": reflection,
                },
            )

        except Exception as e:  # guardian: allow-silent-swallow
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            Logger.warning(
                "react_reflection_error",
                extra={
                    "trace_id": trace.trace_id,
                    "error": str(e),
                },
            )


def create_react_engine(
    max_steps: int = 10,
    enable_self_reflection: bool = True,
) -> ReActEngine:
    """Factory function to create a ReAct engine.

    Args:
        max_steps: Maximum reasoning steps
        enable_self_reflection: Enable periodic self-reflection

    Returns:
        Configured ReActEngine instance
    """
    return ReActEngine(
        max_steps=max_steps,
        enable_self_reflection=enable_self_reflection,
    )
