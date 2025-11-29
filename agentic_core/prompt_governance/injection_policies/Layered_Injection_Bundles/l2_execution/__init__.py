#!/usr/bin/env python3
"""
L2 Execution Injection Bundles
Section 6: Prompt Governance - L2 Execution layer prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ExecutionPromptType(str, Enum):
    """Execution prompt injection type enumeration"""
    TOOL_SELECTION = "tool_selection"
    PARAMETER_BINDING = "parameter_binding"
    ERROR_HANDLING = "error_handling"
    OUTPUT_FORMATTING = "output_formatting"

@dataclass
class L2ExecutionBundle:
    """L2 Execution layer injection bundle"""
    bundle_id: str
    prompt_type: ExecutionPromptType
    templates: List[str]
    metadata: Dict[str, Any]
    
    def inject_execution_guidance(self, base_prompt: str, execution_context: Dict[str, Any]) -> str:
        """Inject L2 execution guidance into prompt"""
        guidance = self._generate_execution_guidance(execution_context)
        return f"{base_prompt}\n\nExecution Guidance:\n{guidance}"
    
    def _generate_execution_guidance(self, context: Dict[str, Any]) -> str:
        """Generate execution-specific guidance"""
        if self.prompt_type == ExecutionPromptType.TOOL_SELECTION:
            return f"Tool Selection: Choose appropriate tools from {context.get('available_tools', 'standard toolkit')}"
        elif self.prompt_type == ExecutionPromptType.PARAMETER_BINDING:
            return f"Parameter Binding: Map inputs to tool parameters with proper validation"
        elif self.prompt_type == ExecutionPromptType.ERROR_HANDLING:
            return f"Error Handling: Implement robust error handling and fallback mechanisms"
        elif self.prompt_type == ExecutionPromptType.OUTPUT_FORMATTING:
            return f"Output Formatting: Structure output according to {context.get('format_spec', 'standard schema')}"
        return ""

# Re-export components
__all__ = [
    'L2ExecutionBundle', 'ExecutionPromptType'
]
