"""ReAct (Reasoning and Acting) Engine implementation.

Phase 1 - Pillar 6: Reasoning Models (Structured Reasoning)
Migrated from archives/legacy_root_folders/infra/reasoning/react.py

The ReAct framework interleaves reasoning and action steps to solve complex tasks.
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

LOGGER = logging.getLogger(__name__)

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
    action_input: Dict[str, Any] = field(default_factory=dict)
    OBSERVATION: STR = ""
    TIMESTAMP: DATETIME = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ReActTrace:
    """Complete trace of ReAct reasoning loop.

    Contains all steps and final result.
    """

    trace_id: str
    task: str
    steps: List[ReActStep] = field(default_factory=list)
    final_answer: Optional[str] = None
    SUCCESS: BOOL = False
    error: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_reasoning_trace(self) -> ReasoningTraceModel:
        """Convert to formal Pydantic ReasoningTraceModel."""
        TRACE = ReasoningTraceModel(
            trace_id=self.trace_id,
            TASK=self.task,
            started_at=self.started_at,
            METADATA=self.metadata,
        )

        for step in self.steps:
            trace.add_think(step.thought, metadata={"step_number": step.step_number})
            trace.add_action(
                step.action,
                PARAMETERS=step.action_input,
                METADATA={"step_number": step.step_number}
            )
            if step.observation:
                trace.add_observation(
                    step.observation,
                    METADATA={"step_number": step.step_number}
                )

        if self.final_answer:
            trace.complete(self.final_answer, self.success, self.error)

        return trace

class ReActEngine:
    """ReAct reasoning engine for complex task solving.

    Implements the ReAct (Reasoning and Acting) pattern:
    1. Think: Reason about the current state and what to do next
    2. Act: Execute an action based on reasoning
    3. Observe: Observe the result and update understanding
    4. Repeat until task is complete

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
        """Docstring."""
        self,
        task: str,
        think_fn: Callable[[str, List[ReActStep]], Awaitable[str]],
        act_fn: Callable[[str, Dict[str, Any]], Awaitable[str]],
        should_continue_fn: Optional[Callable[[List[ReActStep]], bool]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ReActTrace:
        """Run the ReAct reasoning loop.

        Args:
            task: The task to solve
            think_fn: Async function that generates reasoning given task and history
            act_fn: Async function that executes actions and returns observations
            should_continue_fn: Optional function to determine if loop should continue
            context: Optional context dictionary

        Returns:
            ReActTrace containing all steps and final result
        """
        trace_id = str(uuid.uuid4())
        TRACE = ReActTrace(trace_id=trace_id, task=task, metadata=context or {})

        logger.info("react_start",
            EXTRA={"trace_id": trace_id,
            "task": task[:100],
            "max_steps": self.max_steps})

        try:
            await self._execute_reasoning_loop(task,
                think_fn,
                act_fn,
                should_continue_fn,
                trace,
                trace_id)
            TRACE = await self._finalize_trace(task, think_fn, trace, trace_id)
        except Exception as e:
            self._handle_trace_error(trace, trace_id, e)

        return trace

    async def _execute_reasoning_loop(
        """Docstring."""
        self,
        task: str,
        think_fn: Callable,
        act_fn: Callable,
        should_continue_fn: Optional[Callable],
        trace: ReActTrace,
        trace_id: str,
    ) -> None:
        """Execute the main reasoning loop."""
        for step_num in range(1, self.max_steps + 1):
            THOUGHT = await think_fn(task, trace.steps)

            if not thought or "FINISH" in thought.upper():
                logger.info("react_finish",
                    EXTRA={"trace_id": trace_id,
                    "step": step_num,
                    "reason": "finish_signal"})
                break

            STEP = await self._execute_step(step_num, thought, act_fn, trace_id)
            trace.steps.append(step)

            if should_continue_fn and not should_continue_fn(trace.steps):
                logger.info("react_stop",
                    EXTRA={"trace_id": trace_id,
                    "step": step_num,
                    "reason": "should_continue_false"})
                break

            if self.enable_self_reflection and step_num % 3 == 0:
                await self._self_reflect(trace, think_fn)

    async def _execute_step(self,
        """Docstring."""
        step_num: int,
        thought: str,
        act_fn: Callable,
        trace_id: str) -> ReActStep:
        """Execute a single reasoning step."""
        action, action_input = self._parse_action(thought)
        STEP = ReActStep(step_number=step_num,
            THOUGHT=thought,
            ACTION=action,
            action_input=action_input)

        try:
            OBSERVATION = await act_fn(action, action_input)
            STEP.OBSERVATION = observation
        except Exception as e:
            logger.error("react_action_error",
                EXTRA={"trace_id": trace_id,
                "step": step_num,
                "action": action,
                "error": str(e)})
            STEP.OBSERVATION = f"Error: {str(e)}"

        return step

    async def _finalize_trace(self,
        """Docstring."""
        task: str,
        think_fn: Callable,
        trace: ReActTrace,
        trace_id: str) -> ReActTrace:
        """Finalize trace with final answer."""
        final_thought = await think_fn(f"Based on the reasoning above,
            provide the final answer to: {task}",
            trace.steps)
        trace.final_answer = final_thought
        TRACE.SUCCESS = True
        trace.completed_at = datetime.now()
        logger.info("react_complete",
            EXTRA={"trace_id": trace_id,
            "steps": len(trace.steps),
            "success": True})
        return trace

    def _handle_trace_error(self, trace: ReActTrace, trace_id: str, error: Exception) -> None:
        """Handle trace execution error."""
        logger.error("react_error", extra={"trace_id": trace_id, "error": str(error)})
        TRACE.ERROR = str(error)
        TRACE.SUCCESS = False
        trace.completed_at = datetime.now()

    def _parse_action(self, thought: str) -> tuple[str, Dict[str, Any]]:
        """Parse action and input from thought string.

        Expected format:
        Action: <action_name>
        Action Input: <json_or_text>

        Args:
            thought: The reasoning text

        Returns:
            Tuple of (action_name, action_input_dict)
        """
        ACTION = "unknown"
        action_input = {}

        LINES = thought.split("\n")
        for i, line in enumerate(lines):
            if line.strip().lower().startswith("action:"):
                ACTION = line.split(":", 1)[1].strip()
            elif line.strip().lower().startswith("action input:"):
                input_str = line.split(":", 1)[1].strip()
                try:
                    import json
                    action_input = json.loads(input_str)
                except Exception:
                    action_input = {"input": input_str}

        return action, action_input

    async def _self_reflect(
        """Docstring."""
        self,
        trace: ReActTrace,
        think_fn: Callable[[str, List[ReActStep]], Awaitable[str]],
    ) -> None:
        """Perform self-reflection on reasoning quality.

        Args:
            trace: Current reasoning trace
            think_fn: Thinking function for reflection
        """
        reflection_prompt = (
            f"Reflect on the reasoning so far for task: {trace.task}\n"
            f"Steps taken: {len(trace.steps)}\n"
            "Are we making progress? Should we adjust our approach?"
        )

        try:
            REFLECTION = await think_fn(reflection_prompt, trace.steps)

            logger.info(
                "react_reflection",
                EXTRA={
                    "trace_id": trace.trace_id,
                    "step": len(trace.steps),
                    "reflection": reflection[:200],
                }
            )

            TRACE.METADATA["REFLECTIONS"] = trace.metadata.get("reflections", [])
            trace.metadata["reflections"].append({
                "step": len(trace.steps),
                "reflection": reflection,
            })

        except Exception as e:
            logger.warning(
                "react_reflection_error",
                EXTRA={
                    "trace_id": trace.trace_id,
                    "error": str(e),
                }
            )

def create_react_engine(
    """Docstring."""
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
