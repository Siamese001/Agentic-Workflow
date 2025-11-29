#!/usr/bin/env python3
"""
L1 Planning Injection Bundles
Section 6: Prompt Governance - L1 Planning layer prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class PlanningPromptType(str, Enum):
    """Planning prompt injection type enumeration"""
    STRATEGY = "strategy"
    WORKFLOW = "workflow"
    RESEARCH = "research"
    COMPLEXITY = "complexity"

@dataclass
class L1PlanningBundle:
    """L1 Planning layer injection bundle"""
    bundle_id: str
    prompt_type: PlanningPromptType
    templates: List[str]
    metadata: Dict[str, Any]
    
    def inject_planning_guidance(self, base_prompt: str, planning_context: Dict[str, Any]) -> str:
        """Inject L1 planning guidance into prompt"""
        guidance = self._generate_planning_guidance(planning_context)
        return f"{base_prompt}\n\nPlanning Guidance:\n{guidance}"
    
    def _generate_planning_guidance(self, context: Dict[str, Any]) -> str:
        """Generate planning-specific guidance"""
        if self.prompt_type == PlanningPromptType.STRATEGY:
            return f"Strategic Approach: {context.get('strategy', 'Develop comprehensive strategy')}"
        elif self.prompt_type == PlanningPromptType.WORKFLOW:
            return f"Workflow Steps: {context.get('workflow', 'Define sequential workflow')}"
        elif self.prompt_type == PlanningPromptType.RESEARCH:
            return f"Research Focus: {context.get('research_area', 'Conduct thorough research')}"
        elif self.prompt_type == PlanningPromptType.COMPLEXITY:
            complexity = context.get('complexity', 'medium')
            return f"Complexity Level: {complexity} - Adjust approach accordingly"
        return ""

# Re-export components
__all__ = [
    'L1PlanningBundle', 'PlanningPromptType'
]
