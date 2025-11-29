"""
Subatomic Execution Agents

Granular micro-agents for specialized execution tasks with enhanced v5 instructional prompts.
"""

from .content_enhancer import ContentEnhancerAgent, create_content_enhancer

__version__ = "1.0.0"
__all__ = [
    'ContentEnhancerAgent',
    'create_content_enhancer'
]
