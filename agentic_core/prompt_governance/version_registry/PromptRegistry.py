from __future__ import annotations
"""Compatibility module - re-exports from PromptRegistryAgent.

This module provides backward compatibility for PascalCase imports.
"""
from agentic_core.prompt_governance.PromptRegistryAgent import (
    PromptRegistryAgent,
    registers_prompt,
    get_prompt_registry,
)

# Alias for backwards compatibility
PromptRegistry = PromptRegistryAgent

__all__ = ["PromptRegistry", "PromptRegistryAgent", "registers_prompt", "get_prompt_registry"]
