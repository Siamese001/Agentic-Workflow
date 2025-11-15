"""v10.8 agent stack shims that delegate to the existing v10.7 agents."""

from .rag_execution_stack import RAGExecutionStack
from .qa_validation_stack import QAValidationStack
from .drafting_execution_stack import DraftingExecutionStack
from .bullet_execution_stack import BulletExecutionStack
from .strategy_stack import StrategyStackV10_8
from .safety_stack import SafetyStackV10_8
from .hil_stack import HILStackV10_8
from .state_adapter_stack import StateAdapterStack

__all__ = [
    "RAGExecutionStack",
    "QAValidationStack",
    "DraftingExecutionStack",
    "BulletExecutionStack",
    "StrategyStackV10_8",
    "SafetyStackV10_8",
    "HILStackV10_8",
    "StateAdapterStack",
]
