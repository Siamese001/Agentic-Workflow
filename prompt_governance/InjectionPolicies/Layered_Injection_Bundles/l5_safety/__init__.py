#!/usr/bin/env python3
"""
L5 Safety Injection Bundles
Section 6: Prompt Governance - L5 Safety layer prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class SafetyPromptType(str, Enum):
    """Safety prompt injection type enumeration"""
    CONTENT_FILTERING = "content_filtering"
    PRIVACY_PROTECTION = "privacy_protection"
    ETHICAL_GUIDELINES = "ethical_guidelines"
    SECURITY_CONSTRAINTS = "security_constraints"

@dataclass
class L5SafetyBundle:
    """L5 Safety layer injection bundle"""
    bundle_id: str
    prompt_type: SafetyPromptType
    templates: List[str]
    metadata: Dict[str, Any]

    def inject_safety_guidance(self, base_prompt: str, safety_context: Dict[str, Any]) -> str:
        """Inject L5 safety guidance into prompt"""
        guidance = self._generate_safety_guidance(safety_context)
        return f"{base_prompt}\n\nSafety Guidelines:\n{guidance}"

    def _generate_safety_guidance(self, context: Dict[str, Any]) -> str:
        """Generate safety-specific guidance"""
        if self.prompt_type == SafetyPromptType.CONTENT_FILTERING:
            return f"Content Filtering: Ensure content complies with {context.get('content_policy', 'acceptable content standards')}"
        elif self.prompt_type == SafetyPromptType.PRIVACY_PROTECTION:
            return f"Privacy Protection: Protect {context.get('sensitive_data', 'personal and confidential information')}"
        elif self.prompt_type == SafetyPromptType.ETHICAL_GUIDELINES:
            return f"Ethical Guidelines: Follow {context.get('ethical_standards', 'established ethical principles')}"
        elif self.prompt_type == SafetyPromptType.SECURITY_CONSTRAINTS:
            return f"Security Constraints: Adhere to {context.get('security_requirements', 'security protocols and constraints')}"
        return ""

# Re-export components
__all__ = [
    'L5SafetyBundle', 'SafetyPromptType'
]





