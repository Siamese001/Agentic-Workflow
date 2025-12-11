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

# Re-export agents from l2.agents

# Re-export retrieval and observability for test compatibility
from archives.legacy_resume_gen.Agentic_Workflow-10_10.l2.execution import run_rag_retrieval
from archives.legacy_resume_gen.Agentic_Workflow-10_10.tests.sandbox.test_sandbox_observability import start_span, end_span

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



