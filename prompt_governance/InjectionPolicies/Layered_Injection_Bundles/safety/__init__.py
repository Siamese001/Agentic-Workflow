#!/usr/bin/env python3
"""
Safety Injection Bundles
Section 6: Prompt Governance - Safety and compliance prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class SafetyPromptType(str, Enum):
    """Safety prompt injection type enumeration"""
    HARM_PREVENTION = "harm_prevention"
    BIAS_DETECTION = "bias_detection"
    CONTENT_MODERATION = "content_moderation"
    COMPLIANCE_CHECK = "compliance_check"

@dataclass
class SafetyBundle:
    """Safety injection bundle"""
    bundle_id: str
    prompt_type: SafetyPromptType
    templates: List[str]
    metadata: Dict[str, Any]

    def inject_safety_protocols(self, base_prompt: str, safety_context: Dict[str, Any]) -> str:
        """Inject safety protocols into prompt"""
        protocols = self._generate_safety_protocols(safety_context)
        return f"{base_prompt}\n\nSafety Protocols:\n{protocols}"

    def _generate_safety_protocols(self, context: Dict[str, Any]) -> str:
        """Generate safety-specific protocols"""
        if self.prompt_type == SafetyPromptType.HARM_PREVENTION:
            return f"Harm Prevention: Ensure no {context.get('harm_types', 'potential harm')} in generated content"
        elif self.prompt_type == SafetyPromptType.BIAS_DETECTION:
            return f"Bias Detection: Check for and mitigate {context.get('bias_types', 'unconscious biases')}"
        elif self.prompt_type == SafetyPromptType.CONTENT_MODERATION:
            return f"Content Moderation: Apply {context.get('moderation_rules', 'content standards')} consistently"
        elif self.prompt_type == SafetyPromptType.COMPLIANCE_CHECK:
            return f"Compliance Check: Verify adherence to {context.get('compliance_standards', 'regulatory requirements')}"
        return ""

# Re-export components
__all__ = [
    'SafetyBundle', 'SafetyPromptType'
]





