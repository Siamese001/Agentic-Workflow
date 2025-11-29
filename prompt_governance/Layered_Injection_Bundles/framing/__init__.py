#!/usr/bin/env python3
"""
Framing Injection Bundles
Section 6: Prompt Governance - Framing and structure prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class FramingType(str, Enum):
    """Framing injection type enumeration"""
    PROBLEM = "problem"
    SOLUTION = "solution"
    CONSTRAINT = "constraint"
    OBJECTIVE = "objective"

@dataclass
class FramingBundle:
    """Framing injection bundle for prompt structure"""
    bundle_id: str
    framing_type: FramingType
    templates: List[str]
    metadata: Dict[str, Any]
    
    def apply_framing(self, base_prompt: str, framing_data: Dict[str, Any]) -> str:
        """Apply framing structure to base prompt"""
        frame = self._build_frame(framing_data)
        return f"{frame}\n\n{base_prompt}"
    
    def _build_frame(self, framing_data: Dict[str, Any]) -> str:
        """Build framing structure"""
        if self.framing_type == FramingType.PROBLEM:
            return f"Problem: {framing_data.get('description', '')}"
        elif self.framing_type == FramingType.SOLUTION:
            return f"Solution Approach: {framing_data.get('approach', '')}"
        elif self.framing_type == FramingType.CONSTRAINT:
            constraints = framing_data.get('constraints', [])
            return f"Constraints:\n" + "\n".join(f"- {c}" for c in constraints)
        elif self.framing_type == FramingType.OBJECTIVE:
            return f"Objective: {framing_data.get('objective', '')}"
        return ""

# Re-export components
__all__ = [
    'FramingBundle', 'FramingType'
]
