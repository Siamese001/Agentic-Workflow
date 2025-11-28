"""
Execution layer for résumé processing workflow orchestration.

Provides technical execution functions that bridge planning to actual LLM execution for résumé enhancement operations.

Layer: L2 (Execution)
Responsibilities:
- Execute strategy, RAG, drafting, QA, safety tasks for résumé processing
- Invoke cognitive agents with proper context for résumé improvement
- Handle execution errors and retries in résumé enhancement workflows
- Return structured L2 results for comprehensive résumé operations

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
    run_l2,
    _execute_strategy,
    _execute_retrieval,
    _execute_drafting,
    _execute_qa,
    _execute_safety,
    _maybe_run_hyde_query,
)

# Re-export agents from l2.agents
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



