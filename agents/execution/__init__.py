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

# Re-export execution functions from agents.execution.execution
from .execution import (
    execute_workflow_plans,
    run_l2,
    _execute_strategy,
    _execute_retrieval,
    _execute_drafting,
    _execute_qa,
    _execute_safety,
    _maybe_run_hyde_query,
)

# Re-export agents from agents.execution.agents
from .agents import (
    LLMBaseAgent,
    StrategyLLMAgent,
    DraftingGuild,
    SemanticQAAgent,
    ConstitutionalSafetyAgent,
    HYDEQueryAgent,
    QACouncilAgent,
)

# Re-export retrieval and observability for test compatibility
from .execution import run_rag_retrieval
from runtime.observability import start_span, end_span

__all__ = [
    # Execution functions
    'execute_workflow_plans',
    'run_l2',
    '_execute_strategy',
    '_execute_retrieval',
    '_execute_drafting',
    '_execute_qa',
    '_execute_safety',
    '_maybe_run_hyde_query',
    # Agents
    'LLMBaseAgent',
    'StrategyLLMAgent',
    'DraftingGuild',
    'SemanticQAAgent',
    'ConstitutionalSafetyAgent',
    'HYDEQueryAgent',
    'QACouncilAgent',
    # Re-exports for test compatibility
    'run_rag_retrieval',
    'start_span',
    'end_span',
]



