"""ReAct (Reasoning and Acting) Engine implementation.

Phase 1 - Pillar 6: Reasoning Models (Structured Reasoning)
Migrated from archives/legacy_root_folders/infra/reasoning/react.py

The ReAct framework interleaves reasoning and action steps to solve complex tasks.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

from .trace_models import ReasoningTraceModel

logger = logging.getLogger(__name__)


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
    observation: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
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
    success: bool = False
    error: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_reasoning_trace(self) -> ReasoningTraceModel:
        """Convert to formal Pydantic ReasoningTraceModel."""
        trace = ReasoningTraceModel(
            trace_id=self.trace_id,
            task=self.task,
            started_at=self.started_at,
            metadata=self.metadata,
        )
        
        for step in self.steps:
            trace.add_think(step.thought, metadata={"step_number": step.step_number})
            trace.add_action(
                step.action,
                parameters=step.action_input,
                metadata={"step_number": step.step_number}
            )
            if step.observation:
                trace.add_observation(
                    step.observation,
                    metadata={"step_number": step.step_number}
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
        trace = ReActTrace(
            trace_id=trace_id,
            task=task,
            metadata=context or {},
        )
        
        logger.info(
            "react_start",
            extra={
                "trace_id": trace_id,
                "task": task[:100],
                "max_steps": self.max_steps,
            }
        )
        
        try:
            for step_num in range(1, self.max_steps + 1):
                thought = await think_fn(task, trace.steps)
                
                if not thought or "FINISH" in thought.upper():
                    logger.info(
                        "react_finish",
                        extra={
                            "trace_id": trace_id,
                            "step": step_num,
                            "reason": "finish_signal",
                        }
                    )
                    break
                
                action, action_input = self._parse_action(thought)
                
                step = ReActStep(
                    step_number=step_num,
                    thought=thought,
                    action=action,
                    action_input=action_input,
                )
                
                try:
                    observation = await act_fn(action, action_input)
                    step.observation = observation
                    
                except Exception as e:
                    logger.error(
                        "react_action_error",
                        extra={
                            "trace_id": trace_id,
                            "step": step_num,
                            "action": action,
                            "error": str(e),
                        }
                    )
                    step.observation = f"Error: {str(e)}"
                
                trace.steps.append(step)
                
                if should_continue_fn and not should_continue_fn(trace.steps):
                    logger.info(
                        "react_stop",
                        extra={
                            "trace_id": trace_id,
                            "step": step_num,
                            "reason": "should_continue_false",
                        }
                    )
                    break
                
                if self.enable_self_reflection and step_num % 3 == 0:
                    await self._self_reflect(trace, think_fn)
            
            final_thought = await think_fn(
                f"Based on the reasoning above, provide the final answer to: {task}",
                trace.steps
            )
            
            trace.final_answer = final_thought
            trace.success = True
            trace.completed_at = datetime.now()
            
            logger.info(
                "react_complete",
                extra={
                    "trace_id": trace_id,
                    "steps": len(trace.steps),
                    "success": True,
                }
            )
            
        except Exception as e:
            logger.error(
                "react_error",
                extra={
                    "trace_id": trace_id,
                    "error": str(e),
                }
            )
            trace.error = str(e)
            trace.success = False
            trace.completed_at = datetime.now()
        
        return trace
    
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
        action = "unknown"
        action_input = {}
        
        lines = thought.split("\n")
        for i, line in enumerate(lines):
            if line.strip().lower().startswith("action:"):
                action = line.split(":", 1)[1].strip()
            elif line.strip().lower().startswith("action input:"):
                input_str = line.split(":", 1)[1].strip()
                try:
                    import json
                    action_input = json.loads(input_str)
                except:
                    action_input = {"input": input_str}
        
        return action, action_input
    
    async def _self_reflect(
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
            reflection = await think_fn(reflection_prompt, trace.steps)
            
            logger.info(
                "react_reflection",
                extra={
                    "trace_id": trace.trace_id,
                    "step": len(trace.steps),
                    "reflection": reflection[:200],
                }
            )
            
            trace.metadata["reflections"] = trace.metadata.get("reflections", [])
            trace.metadata["reflections"].append({
                "step": len(trace.steps),
                "reflection": reflection,
            })
            
        except Exception as e:
            logger.warning(
                "react_reflection_error",
                extra={
                    "trace_id": trace.trace_id,
                    "error": str(e),
                }
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
