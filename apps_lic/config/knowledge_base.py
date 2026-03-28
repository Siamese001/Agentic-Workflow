"""Canonical apps_lic knowledge base exports.

This module preserves the historical import surface:
`apps_lic.config.knowledge_base`.
"""

from apps_lic.types.PromptTemplate import (
    FROZEN_SNAPSHOT,
    LicPromptEntry,
    LicNodeEntry,
    LicGlobalRule,
    LicSovereignKnowledge,
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
    "LicPromptEntry",
    "LicNodeEntry",
    "LicGlobalRule",
    "LicSovereignKnowledge",
    "get_prompt",
    "get_system_prompt",
    "get_prompt_entry",
    "get_node_config",
    "get_global_rule",
    "list_all_prompts",
    "list_all_nodes",
]
