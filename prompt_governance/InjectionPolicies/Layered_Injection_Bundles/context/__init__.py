#!/usr/bin/env python3
"""
Context Injection Bundles
Section 6: Prompt Governance - Context-aware prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ContextType(str, Enum):
    """Context injection type enumeration"""
    DOMAIN = "domain"
    TASK = "task"
    HISTORY = "history"
    ENVIRONMENT = "environment"

@dataclass
class ContextBundle:
    """Context injection bundle for prompt enhancement"""
    bundle_id: str
    context_type: ContextType
    templates: List[str]
    metadata: Dict[str, Any]

    def inject_context(self, base_prompt: str, context_data: Dict[str, Any]) -> str:
        """Inject context into base prompt"""
        context_str = self._format_context(context_data)
        return f"{base_prompt}\n\nContext: {context_str}"

    def _format_context(self, context_data: Dict[str, Any]) -> str:
        """Format context data for injection"""
        formatted_items = []
        for key, value in context_data.items():
            formatted_items.append(f"{key}: {value}")
        return "\n".join(formatted_items)

# Re-export components
__all__ = [
    'ContextBundle', 'ContextType'
]





