#!/usr/bin/env python3
"""
Reasoning Injection Bundles
Section 6: Prompt Governance - Reasoning and logic prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ReasoningPromptType(str, Enum):
    """Reasoning prompt injection type enumeration"""
    LOGICAL_INFERENCE = "logical_inference"
    CAUSAL_REASONING = "causal_reasoning"
    ANALOGICAL_REASONING = "analogical_reasoning"
    DEDUCTIVE_REASONING = "deductive_reasoning"

@dataclass
class ReasoningBundle:
    """Reasoning injection bundle"""
    bundle_id: str
    prompt_type: ReasoningPromptType
    templates: List[str]
    metadata: Dict[str, Any]
    
    def inject_reasoning_guidance(self, base_prompt: str, reasoning_context: Dict[str, Any]) -> str:
        """Inject reasoning guidance into prompt"""
        guidance = self._generate_reasoning_guidance(reasoning_context)
        return f"{base_prompt}\n\nReasoning Approach:\n{guidance}"
    
    def _generate_reasoning_guidance(self, context: Dict[str, Any]) -> str:
        """Generate reasoning-specific guidance"""
        if self.prompt_type == ReasoningPromptType.LOGICAL_INFERENCE:
            return f"Logical Inference: Apply {context.get('logic_rules', 'formal logical principles')} to derive conclusions"
        elif self.prompt_type == ReasoningPromptType.CAUSAL_REASONING:
            return f"Causal Reasoning: Analyze {context.get('causal_factors', 'cause-effect relationships')} systematically"
        elif self.prompt_type == ReasoningPromptType.ANALOGICAL_REASONING:
            return f"Analogical Reasoning: Use {context.get('analogies', 'relevant analogies')} to understand complex concepts"
        elif self.prompt_type == ReasoningPromptType.DEDUCTIVE_REASONING:
            return f"Deductive Reasoning: Apply {context.get('premises', 'given premises')} to reach logical conclusions"
        return ""

# Re-export components
__all__ = [
    'ReasoningBundle', 'ReasoningPromptType'
]
