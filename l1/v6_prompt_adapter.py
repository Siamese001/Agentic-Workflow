"""
V6 Prompt Adapter for strategy planning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class V6PromptConfig:
    """Configuration for V6 prompt building."""
    max_context_length: int = 4000
    include_safety_checks: bool = True
    include_examples: bool = True


class ExecutionContext:
    """Mock execution context for compatibility."""
    pass


def build_v6_strategy_prompt(
    ctx: ExecutionContext,
    strategy_input: Dict[str, Any],
    config: Optional[V6PromptConfig] = None,
) -> str:
    """Build V6 strategy prompt from input data."""
    if config is None:
        config = V6PromptConfig()
    
    sections = ["# STRATEGY PLANNING", ""]
    
    # Add input data
    if strategy_input:
        sections.append("## INPUT DATA")
        sections.append(f"Strategy: {strategy_input.get('strategy', 'Unknown')}")
        sections.append("")
    
    # Add task
    sections.append("## YOUR TASK")
    sections.append("Create a comprehensive strategy plan.")
    sections.append("")
    
    return "\n".join(sections)


def _build_safety_context_section(
    ctx: ExecutionContext,
    safety_plan: Any,
    draft_result: Any,
) -> str:
    """Build context section for safety planning."""
    
    sections = ["## CURRENT CONTEXT", ""]
    
    # Draft sections to check
    if draft_result:
        sections_count = len(getattr(draft_result, "sections", []))
        sections.append(f"**Draft Sections:** {sections_count}")
        sections.append("")
    
    sections.append("## YOUR TASK")
    sections.append("")
    sections.append("Create a safety review plan to detect and prevent problematic content.")
    
    return "\n".join(sections)
