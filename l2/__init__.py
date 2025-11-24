"""L2 - Execution Layer

This layer provides the main execution functions that invoke cognitive agents
and return structured results. It bridges L1 plans to actual LLM execution.

Layer: L2 (Execution)
Responsibilities:
- Execute strategy, RAG, drafting, QA, safety tasks
- Invoke cognitive agents with proper context
- Handle execution errors and retries
- Return structured L2 results

Non-responsibilities:
- Planning (L1)
- Orchestration/DAG (L3)
- State management (L4)
- Policy enforcement (L5)
"""

from __future__ import annotations

# Re-export execution functions from l2.execution
from .execution import (
    execute_workflow_plans,
)

# Re-export agents from l2.agents
from .agents import (
    StrategyLLMAgent,
    DraftingGuild,
    SemanticQAAgent,
    ConstitutionalSafetyAgent,
    HYDEQueryAgent,
)

__all__ = [
    # Execution functions
    'execute_workflow_plans',
    # Agents
    'StrategyLLMAgent',
    'DraftingGuild',
    'SemanticQAAgent',
    'ConstitutionalSafetyAgent',
    'HYDEQueryAgent',
]
