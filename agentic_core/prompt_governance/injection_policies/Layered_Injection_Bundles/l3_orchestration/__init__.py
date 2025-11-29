#!/usr/bin/env python3
"""
L3 Orchestration Injection Bundles
Section 6: Prompt Governance - L3 Orchestration layer prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class OrchestrationPromptType(str, Enum):
    """Orchestration prompt injection type enumeration"""
    WORKFLOW_COORDINATION = "workflow_coordination"
    RESOURCE_MANAGEMENT = "resource_management"
    DEPENDENCY_RESOLUTION = "dependency_resolution"
    STATE_TRACKING = "state_tracking"

@dataclass
class L3OrchestrationBundle:
    """L3 Orchestration layer injection bundle"""
    bundle_id: str
    prompt_type: OrchestrationPromptType
    templates: List[str]
    metadata: Dict[str, Any]
    
    def inject_orchestration_guidance(self, base_prompt: str, orchestration_context: Dict[str, Any]) -> str:
        """Inject L3 orchestration guidance into prompt"""
        guidance = self._generate_orchestration_guidance(orchestration_context)
        return f"{base_prompt}\n\nOrchestration Guidance:\n{guidance}"
    
    def _generate_orchestration_guidance(self, context: Dict[str, Any]) -> str:
        """Generate orchestration-specific guidance"""
        if self.prompt_type == OrchestrationPromptType.WORKFLOW_COORDINATION:
            return f"Workflow Coordination: Coordinate {context.get('workflow_steps', 'multiple steps')} in proper sequence"
        elif self.prompt_type == OrchestrationPromptType.RESOURCE_MANAGEMENT:
            return f"Resource Management: Allocate and manage {context.get('resources', 'computational resources')}"
        elif self.prompt_type == OrchestrationPromptType.DEPENDENCY_RESOLUTION:
            return f"Dependency Resolution: Handle {context.get('dependencies', 'inter-component dependencies')}"
        elif self.prompt_type == OrchestrationPromptType.STATE_TRACKING:
            return f"State Tracking: Monitor and maintain {context.get('state_info', 'execution state')}"
        return ""

# Re-export components
__all__ = [
    'L3OrchestrationBundle', 'OrchestrationPromptType'
]
