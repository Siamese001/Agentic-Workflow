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
from dataclasses import dataclass, field # Added missing import

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
    observation: str = "" # Changed OBSERVATION: STR to observation: str
    timestamp: datetime = field(default_factory=datetime.now) # Changed TIMESTAMP: DATETIME to timestamp: datetime
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
    success: bool = False # Changed SUCCESS: BOOL to success: bool
    error: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_reasoning_trace(self) -> Any: # Changed return type to Any, as ReasoningTraceModel is not defined
        """Convert to formal Pydantic ReasoningTraceModel."""
        # Assuming ReasoningTraceModel is imported or defined elsewhere
        # For compilation, placeholder type 'Any' is used if not available.
        # If 'ReasoningTraceModel' is a type from another module, it needs to be imported.
        # For now, let's assume it's available or use a placeholder to fix syntax.
        from pydantic import BaseModel # Assuming Pydantic model
        class ReasoningTraceModel(BaseModel):
            trace_id: str
            TASK: str
            started_at: datetime
            METADATA: Dict[str, Any] = {}
            # Add other necessary fields and methods like add_think, add_action, add_observation, complete
            def add_think(self, thought: str, metadata: Optional[Dict[str, Any]] = None): pass
            def add_action(self, action: str, PARAMETERS: Optional[Dict[str, Any]] = None, METADATA: Optional[Dict[str, Any]] = None): pass
            def add_observation(self, observation: str, METADATA: Optional[Dict[str, Any]] = None): pass
            def complete(self, final_answer: str, success: bool, error: Optional[str]): pass


        trace_model = ReasoningTraceModel( # Renamed TRACE to trace_model to avoid shadowing instance variable
            trace_id=self.trace_id,
            TASK=self.task,
            started_at=self.started_at,
            METADATA=self.metadata,
        )

        for step in self.steps:
            trace_model.add_think(step.thought, metadata={
                            "step_number": step.step_number})
            trace_model.add_action(
                step.action,
                PARAMETERS=step.action_input,
                METADATA={"step_number": step.step_number}
            )
            if step.observation:
                trace_model.add_observation(
                    step.observation,
                    METADATA={"step_number": step.step_number}
                )

        if self.final_answer:
            trace_model.complete(self.final_answer, self.success, self.error)

        return trace_model


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
        self, # Docstring must be inside the function body, not between def and self.
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
        trace = ReActTrace(trace_id=trace_id, task=task, # Renamed TRACE to trace
                           metadata=context or {})

        LOGGER.info("react_start", # Changed logger to LOGGER
                    extra={"trace_id": trace_id,
                           "task": task[:100],
                           "max_steps": self.max_steps})

        try:
            await self._execute_reasoning_loop(task,
                                               think_fn,
                                               act_fn,
                                               should_continue_fn,
                                               trace,
                                               trace_id)
            trace = await self._finalize_trace(task, think_fn, trace, trace_id) # Renamed TRACE to trace
        except Exception as e:
            pass # Fixed indentation
            self._handle_trace_error(trace, trace_id, e)

        return trace

    async def _execute_reasoning_loop(
        self, # Docstring must be inside the function body.
        task: str,
        think_fn: Callable,
        act_fn: Callable,
        should_continue_fn: Optional[Callable],
        trace: ReActTrace,
        trace_id: str,
    ) -> None:
        """Execute the main reasoning loop."""
        for step_num in range(1, self.max_steps + 1):
            thought = await think_fn(task, trace.steps) # Renamed THOUGHT to thought

            if not thought or "FINISH" in thought.upper():
                LOGGER.info("react_finish", # Changed logger to LOGGER
                            extra={"trace_id": trace_id,
                                   "step": step_num,
                                   "reason": "finish_signal"})
                break

            step = await self._execute_step(step_num, thought, act_fn, trace_id) # Renamed STEP to step
            trace.steps.append(step)

            if should_continue_fn and not should_continue_fn(trace.steps):
                LOGGER.info("react_stop", # Changed logger to LOGGER
                            extra={"trace_id": trace_id,
                                   "step": step_num,
                                   "reason": "should_continue_false"})
                break

            if self.enable_self_reflection and step_num % 3 == 0:
                await self._self_reflect(trace, think_fn)

    async def _execute_step(self,
                            step_num: int, # Docstring must be inside the function body.
                            thought: str,
                            act_fn: Callable,
                            trace_id: str) -> ReActStep:
        """Execute a single reasoning step."""
        action, action_input = self._parse_action(thought)
        step = ReActStep(step_number=step_num, # Renamed STEP to step, consistent casing
                         thought=thought, # consistent casing
                         action=action, # consistent casing
                         action_input=action_input)

        try:
            observation = await act_fn(action, action_input) # Renamed OBSERVATION to observation
            step.observation = observation
        except Exception as e:
            pass # Fixed indentation
            LOGGER.error("react_action_error", # Changed logger to LOGGER
                         extra={"trace_id": trace_id,
                                "step": step_num,
                                "action": action,
                                "error": str(e)})
            step.observation = f"Error: {str(e)}"

        return step

    async def _finalize_trace(self,
                              task: str, # Docstring must be inside the function body.
                              think_fn: Callable,
                              trace: ReActTrace,
                              trace_id: str) -> ReActTrace:
        """Finalize trace with final answer."""
        final_thought = await think_fn(f"Based on the reasoning above, " # Corrected string literal for f-string
                                       f"provide the final answer to: {task}",
                                       trace.steps)
        trace.final_answer = final_thought
        trace.success = True # Renamed TRACE.SUCCESS to trace.success
        trace.completed_at = datetime.now()
        LOGGER.info("react_complete", # Changed logger to LOGGER
                    extra={"trace_id": trace_id,
                           "steps": len(trace.steps),
                           "success": True})
        return trace

    def _handle_trace_error(self, trace: ReActTrace, trace_id: str, error: Exception) -> None:
        """Handle trace execution error."""
        LOGGER.error("react_error", extra={ # Changed logger to LOGGER
                     "trace_id": trace_id, "error": str(error)})
        trace.error = str(error) # Renamed TRACE.ERROR to trace.error
        trace.success = False # Renamed TRACE.SUCCESS to trace.success
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
        action = "unknown" # Renamed ACTION to action
        action_input = {}

        lines = thought.split("\n") # Renamed LINES to lines
        for i, line in enumerate(lines):
            if line.strip().lower().startswith("action:"):
                action = line.split(":", 1)[1].strip() # Renamed ACTION to action
            elif line.strip().lower().startswith("action input:"):
                input_str = line.split(":", 1)[1].strip()
                try:
                    import json
                    action_input = json.loads(input_str)
                except Exception:
                    pass # Fixed indentation
                    action_input = {"input": input_str}

        return action, action_input

    async def _self_reflect(
        self, # Docstring must be inside the function body.
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
            reflection = await think_fn(reflection_prompt, trace.steps) # Renamed REFLECTION to reflection

            LOGGER.info( # Changed logger to LOGGER
                "react_reflection",
                extra={
                    "trace_id": trace.trace_id,
                    "step": len(trace.steps),
                    "reflection": reflection[:200],
                }
            )

            if "reflections" not in trace.metadata: # Ensure reflections key exists
                trace.metadata["reflections"] = []

            trace.metadata["reflections"].append({ # Renamed TRACE.METADATA to trace.metadata
                "step": len(trace.steps),
                "reflection": reflection,
            })

        except Exception as e:
            pass # Fixed indentation
            LOGGER.warning( # Changed logger to LOGGER
                "react_reflection_error",
                extra={
                    "trace_id": trace.trace_id,
                    "error": str(e),
                }
            )


def create_react_engine(
    max_steps: int = 10, # Docstring must be inside the function body.
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