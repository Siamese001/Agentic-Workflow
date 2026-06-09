"""Compatibility-fenced apps_lic knowledge base exports.

This module preserves the historical import surface:
`apps_lic.config.knowledge_base`.

It is not runtime prompt authority. Active prompt assembly is governed by
`apps_lic/config/prompt_registry.yaml`, `apps_lic/prompt_assembly/prompt_bom.yaml`,
`apps_lic/config/domain_contract/prompt_slot_registry.v1.yaml`, and
`apps_lic/config/domain_contract/output_schema.yaml`.
"""

from apps_lic.types.PromptTemplate import (
    CANONICAL_OUTPUT_SCHEMA_REF,
    CANONICAL_PROMPT_BOM_REF,
    CANONICAL_PROMPT_REGISTRY_REF,
    CANONICAL_PROMPT_SLOT_REGISTRY_REF,
    FROZEN_SNAPSHOT,
    LEGACY_PROMPT_TEMPLATE_AUTHORITY,
    LEGACY_PROMPT_TEMPLATE_RUNTIME_AUTHORITY,
    LEGACY_PROMPT_TEMPLATE_STATUS,
    LicGlobalRule,
    LicNodeEntry,
    LicPromptEntry,
    LicSovereignKnowledge,
    get_global_rule,
    get_node_config,
    get_prompt,
    get_prompt_entry,
    get_system_prompt,
    legacy_prompt_template_fence_receipt,
    list_all_nodes,
    list_all_prompts,
)

__all__ = [
    "LEGACY_PROMPT_TEMPLATE_STATUS",
    "LEGACY_PROMPT_TEMPLATE_RUNTIME_AUTHORITY",
    "LEGACY_PROMPT_TEMPLATE_AUTHORITY",
    "CANONICAL_PROMPT_REGISTRY_REF",
    "CANONICAL_PROMPT_BOM_REF",
    "CANONICAL_PROMPT_SLOT_REGISTRY_REF",
    "CANONICAL_OUTPUT_SCHEMA_REF",
    "FROZEN_SNAPSHOT",
    "LicPromptEntry",
    "LicNodeEntry",
    "LicGlobalRule",
    "LicSovereignKnowledge",
    "legacy_prompt_template_fence_receipt",
    "get_prompt",
    "get_system_prompt",
    "get_prompt_entry",
    "get_node_config",
    "get_global_rule",
    "list_all_prompts",
    "list_all_nodes",
]
