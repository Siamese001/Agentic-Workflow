"""
L2 Execution Contracts Module

Canonical execution taxonomy and agent classification contracts.
"""

from agentic_core.L2_execution.types.agent_taxonomy_registry import (
    AGENT_TAXONOMY_MAP,
    AgentClassification,
    AgentStatus,
    AgentTaxonomyRegistry,
    get_taxonomy_registry,
)
from agentic_core.L2_execution.types.l2_execution_contract import (
    CanonicalAgentRole,
    L2ExecutionAgent,
    L2ExecutionContext,
    L2ExecutionContract,
    L2ExecutionPhase,
    L2PhaseResult,
)

__all__ = [
    # L2 Execution Contract
    "L2ExecutionPhase",
    "L2PhaseResult",
    "L2ExecutionContext",
    "L2ExecutionContract",
    "L2ExecutionAgent",
    "CanonicalAgentRole",
    # Taxonomy Registry
    "AgentClassification",
    "AgentStatus",
    "AgentTaxonomyRegistry",
    "AGENT_TAXONOMY_MAP",
    "get_taxonomy_registry",
]
