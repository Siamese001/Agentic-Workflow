"""Canonical apps_rfp knowledge base exports.

This module preserves the historical import surface:
`apps_rfp.config.knowledge_base`.
"""

from apps_rfp.types.PromptTemplate import (
    FROZEN_SNAPSHOT,
    RfpPromptEntry,
    RfpNodeEntry,
    RfpGlobalRule,
    RfpSovereignKnowledge,
    get_prompt,
    get_system_prompt,
    get_prompt_entry,
    get_node_config,
    get_global_rule,
    list_all_prompts,
    list_all_nodes,
)

__all__ = [
    "FROZEN_SNAPSHOT",
    "RfpPromptEntry",
    "RfpNodeEntry",
    "RfpGlobalRule",
    "RfpSovereignKnowledge",
    "get_prompt",
    "get_system_prompt",
    "get_prompt_entry",
    "get_node_config",
    "get_global_rule",
    "list_all_prompts",
    "list_all_nodes",
]
