"""
ReAct Engine Implementation for Orchestration
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ReActStep(Enum):
    """ReAct execution steps"""
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"


@dataclass
class ReActState:
    """State of ReAct execution"""
    current_step: ReActStep
    thought: str
    action: str
    observation: str
    context: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ReactEngine:
    """ReAct (Reasoning and Acting) orchestration engine"""
    
    def __init__(self, max_iterations: int = 10):
        self.max_iterations = max_iterations
        self.execution_history: List[ReActState] = []
        self.action_handlers: Dict[str, Callable] = {}
        self.context: Dict[str, Any] = {}
        self.current_iteration = 0
    
    def add_action_handler(self, action_name: str, handler: Callable):
        """Add a handler for a specific action"""
        self.action_handlers[action_name] = handler
    
    def think(self, context: Dict[str, Any], goal: str) -> str:
        """Generate a thought based on context and goal"""
        # Mock implementation - in real system this would use LLM
        thought = f"Based on current context: {list(context.keys())}, I need to achieve: {goal}"
        return thought
    
    def act(self, thought: str, context: Dict[str, Any]) -> str:
        """Generate an action based on thought and context"""
        # Mock implementation - in real system this would use LLM
        if "search" in thought.lower():
            return "search_web"
        elif "process" in thought.lower():
            return "process_data"
        else:
            return "default_action"
    
    def observe(self, action: str, context: Dict[str, Any]) -> str:
        """Execute action and return observation"""
        if action in self.action_handlers:
            try:
                result = self.action_handlers[action](context)
                observation = f"Action '{action}' executed successfully: {result}"
            except Exception as e:
                observation = f"Action '{action}' failed: {str(e)}"
        else:
            observation = f"Unknown action '{action}', no handler available"
        
        return observation
    
    def execute_step(self, goal: str) -> ReActState:
        """Execute one ReAct step (thought -> action -> observation)"""
        # Thought step
        thought = self.think(self.context, goal)
        thought_state = ReActState(
            current_step=ReActStep.THOUGHT,
            thought=thought,
            action="",
            observation="",
            context=self.context.copy()
        )
        self.execution_history.append(thought_state)
        
        # Action step
        action = self.act(thought, self.context)
        action_state = ReActState(
            current_step=ReActStep.ACTION,
            thought=thought,
            action=action,
            observation="",
            context=self.context.copy()
        )
        self.execution_history.append(action_state)
        
        # Observation step
        observation = self.observe(action, self.context)
        observation_state = ReActState(
            current_step=ReActStep.OBSERVATION,
            thought=thought,
            action=action,
            observation=observation,
            context=self.context.copy()
        )
        self.execution_history.append(observation_state)
        
        return observation_state
    
    def run(self, goal: str, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run ReAct loop until goal is achieved or max iterations reached"""
        if initial_context:
            self.context = initial_context.copy()
        
        self.current_iteration = 0
        final_observation = ""
        
        while self.current_iteration < self.max_iterations:
            state = self.execute_step(goal)
            final_observation = state.observation
            self.current_iteration += 1
            
            # Check if goal is achieved (mock logic)
            if "success" in final_observation.lower() or "completed" in final_observation.lower():
                break
        
        return {
            "goal": goal,
            "iterations": self.current_iteration,
            "final_observation": final_observation,
            "execution_history": [state.__dict__ for state in self.execution_history],
            "context": self.context.copy(),
            "completed": self.current_iteration < self.max_iterations
        }
    
    def reset(self):
        """Reset the engine state"""
        self.execution_history.clear()
        self.context.clear()
        self.current_iteration = 0
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution"""
        if not self.execution_history:
            return {"status": "not_executed"}
        
        thoughts = [s for s in self.execution_history if s.current_step == ReActStep.THOUGHT]
        actions = [s for s in self.execution_history if s.current_step == ReActStep.ACTION]
        observations = [s for s in self.execution_history if s.current_step == ReActStep.OBSERVATION]
        
        return {
            "total_steps": len(self.execution_history),
            "thoughts": len(thoughts),
            "actions": len(actions),
            "observations": len(observations),
            "iterations": self.current_iteration,
            "context_size": len(self.context),
            "available_actions": list(self.action_handlers.keys())
        }
    
    def set_context(self, key: str, value: Any):
        """Set a context variable"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context variable"""
        return self.context.get(key, default)
    
    def __str__(self):
        return f"ReactEngine(max_iterations={self.max_iterations}, current_iteration={self.current_iteration})"
    
    def __repr__(self):
        return self.__str__()
