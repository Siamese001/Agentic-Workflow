"""
apps_rg.domain - Domain models and knowledge base for Resume Generation
"""

from apps_rg.domain.knowledge_base import (
    FROZEN_SNAPSHOT,
    get_prompt,
    get_node_config,
    PromptTemplate,
    ThresholdConfig,
    KNodeDefinition,
    SovereignKnowledge,
)

__all__ = [
    "FROZEN_SNAPSHOT",
    "get_prompt",
    "get_node_config",
    "PromptTemplate",
    "ThresholdConfig",
    "KNodeDefinition",
    "SovereignKnowledge",
]
