"""
Shared Prompts - Instructional Injection v5 Framework

Complete 30-point instructional framework for subatomic agents.
"""

from .framing_layer import FramingLayer
from .context_layer import ContextLayer
from .reasoning_layer import ReasoningLayer
from .tooling_layer import ToolingLayer
from .safety_layer import SafetyLayer
from .output_layer import OutputLayer
from .prompt_composer import (
    PromptComposer,
    AgentProfile,
    create_content_enhancer_profile,
    create_structure_optimizer_profile,
    create_quality_validator_profile
)

__version__ = "1.0.0"
__all__ = [
    'FramingLayer',
    'ContextLayer', 
    'ReasoningLayer',
    'ToolingLayer',
    'SafetyLayer',
    'OutputLayer',
    'PromptComposer',
    'AgentProfile',
    'create_content_enhancer_profile',
    'create_structure_optimizer_profile',
    'create_quality_validator_profile'
]