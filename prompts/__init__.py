"""
Prompts package for Canon Validator

Contains modularized prompts for global constraints and specialist agents.
"""
from .prompt_loader import (
    PromptLoader,
    get_global_constraints,
    get_specialist_prompt,
    load_prompt_for_agent,
)

__all__ = [
    'load_prompt_for_agent',
    'get_global_constraints',
    'get_specialist_prompt',
    'PromptLoader'
]
