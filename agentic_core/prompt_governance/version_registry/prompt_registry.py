"""
Prompt Registry - Re-export from PromptRegistryAgent.

Provides backwards compatibility for snake_case imports.
"""
from agentic_core.prompt_governance.version_registry.PromptRegistryAgent import (
    PromptRegistryAgent,
    registers_prompt,
    get_prompt_registry,
)

# Alias for backwards compatibility
PromptRegistry = PromptRegistryAgent

__all__ = ["PromptRegistry", "PromptRegistryAgent", "registers_prompt", "get_prompt_registry"]
