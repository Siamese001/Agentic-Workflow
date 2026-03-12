"""
Chain of Thought (CoT) Helpers.

Provides utility functions to expand simple prompts into multi-step
reasoning chains without requiring full agent instantiation.
"""
from __future__ import annotations
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def expand_thought_process(prompt: str, steps: int=3) -> list[str]:
    """
    Expands a single prompt into a sequence of reasoning steps.

    Args:
        prompt (str): The core objective or question.
        steps (int): Number of reasoning steps to generate.
                     Must be between 1 and 10.

    Returns:
        List[str]: A list of strings representing step-by-step headers.

    Raises:
        ValueError: If steps is out of bounds.
    """
    if not 1 <= steps <= 10:
        raise ValueError(f'Steps must be between 1 and 10. Got {steps}.')
    if not prompt or not prompt.strip():
        return ['Step 1: Analyze empty request']
    base_steps = [f'Step {i + 1}: {action}' for i, action in enumerate(_generate_generic_steps(steps))]
    base_steps[0] = f"Step 1: Analyze context for '{prompt}'"
    return base_steps

def _generate_generic_steps(count: int) -> list[str]:
    """Generates generic reasoning placeholders."""
    templates = ['Analyze context and constraints', 'Identify key entities and relationships', 'Formulate hypothesis or draft content', 'Review against safety guidelines', 'Refine and finalize output', 'Verification pass 1', 'Verification pass 2', 'Final formatting', 'Pre-flight check', 'Commit result']
    return [templates[i % len(templates)] for i in range(count)]
