"""
Knowledge consolidation for Agentic Workflow
L5 Consolidated Knowledge combining MEMemory and Pinecone access
"""

from .l5_consolidated import (
    KnowledgeResult,
    L5ConsolidatedKnowledge,
    get_consolidated_knowledge,
    search_profile_and_template,
)

__all__ = [
    "L5ConsolidatedKnowledge",
    "KnowledgeResult",
    "get_consolidated_knowledge",
    "search_profile_and_template"
]
