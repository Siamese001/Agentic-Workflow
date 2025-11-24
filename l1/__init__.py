"""
L1 - Pure Planning and Reasoning Layer

This layer contains only pure reasoning and planning components with no side effects.
No tool calls, state writes, or orchestration logic is allowed here.
"""
from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum

class ReasoningMode(str, Enum):
    """Supported reasoning modes for L1 components."""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    REACT = "react"
    REFLEXION = "reflexion"

@dataclass
class ReasoningContext:
    """Context for reasoning operations."""
    mode: ReasoningMode = ReasoningMode.CHAIN_OF_THOUGHT
    max_steps: int = 10
    temperature: float = 0.7

class BaseReasoner:
    """Base class for all L1 reasoning components."""
    
    def reason(self, prompt: str, context: Optional[ReasoningContext] = None) -> str:
        """Pure reasoning operation with no side effects."""
        raise NotImplementedError()

# Re-export public interfaces
__all__ = [
    'ReasoningMode',
    'ReasoningContext',
    'BaseReasoner',
]
