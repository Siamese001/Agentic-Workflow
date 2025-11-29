#!/usr/bin/env python3
"""
Instructional Injection
Section 6: Prompt Governance - Instructional Injection v5
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class InjectionType(str, Enum):
    """Injection type enumeration"""
    CONTEXT = "context"
    INSTRUCTION = "instruction"
    CONSTRAINT = "constraint"
    EXAMPLE = "example"

@dataclass
class InstructionalInjector:
    """Instructional injection system for prompts"""
    injector_id: str
    injection_type: InjectionType
    template: str
    priority: int = 1
    
    def inject(self, base_prompt: str, context: Dict[str, Any]) -> str:
        """Inject instructional content into prompt"""
        try:
            injected_content = self.template.format(**context)
            return f"{base_prompt}\n\n{injected_content}"
        except KeyError as e:
            logger.error(f"Missing context for injection: {e}")
            return base_prompt

# Re-export components
__all__ = [
    'InstructionalInjector', 'InjectionType'
]
