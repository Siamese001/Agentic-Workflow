"""
Prompt Assembler - Re-export from rendering module.

Provides backwards compatibility for old import paths.
"""
from agentic_core.prompt_governance.rendering.prompt_assembler import (
    PromptAssembler,
    PromptComponents,
    PromptTemplate,
)

__all__ = ["PromptAssembler", "PromptComponents", "PromptTemplate"]
