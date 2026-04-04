"""Canonical apps_research knowledge base exports.

This module preserves the historical import surface:
`apps_research.config.knowledge_base`.
"""

from apps_research.types.PromptTemplate import (
    FROZEN_SNAPSHOT,
    ResearchGlobalRule,
    ResearchNodeEntry,
    ResearchPromptEntry,
    ResearchSovereignKnowledge,
    get_global_rule,
    get_node_config,
    get_prompt,
    get_prompt_entry,
    get_system_prompt,
    list_all_nodes,
    list_all_prompts,
)

__all__ = [
    "FROZEN_SNAPSHOT",
    "ResearchPromptEntry",
    "ResearchNodeEntry",
    "ResearchGlobalRule",
    "ResearchSovereignKnowledge",
    "get_prompt",
    "get_system_prompt",
    "get_prompt_entry",
    "get_node_config",
    "get_global_rule",
    "list_all_prompts",
    "list_all_nodes",
]
