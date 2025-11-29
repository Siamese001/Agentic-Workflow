#!/usr/bin/env python3
"""
Tooling Injection Bundles
Section 6: Prompt Governance - Tool selection and usage prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class ToolingPromptType(str, Enum):
    """Tooling prompt injection type enumeration"""
    TOOL_SELECTION = "tool_selection"
    TOOL_CONFIGURATION = "tool_configuration"
    TOOL_CHAINING = "tool_chaining"
    TOOL_OPTIMIZATION = "tool_optimization"

@dataclass
class ToolingBundle:
    """Tooling injection bundle"""
    bundle_id: str
    prompt_type: ToolingPromptType
    templates: List[str]
    metadata: Dict[str, Any]
    
    def inject_tooling_guidance(self, base_prompt: str, tooling_context: Dict[str, Any]) -> str:
        """Inject tooling guidance into prompt"""
        guidance = self._generate_tooling_guidance(tooling_context)
        return f"{base_prompt}\n\nTooling Guidance:\n{guidance}"
    
    def _generate_tooling_guidance(self, context: Dict[str, Any]) -> str:
        """Generate tooling-specific guidance"""
        if self.prompt_type == ToolingPromptType.TOOL_SELECTION:
            return f"Tool Selection: Choose optimal tools from {context.get('available_tools', 'tool ecosystem')}"
        elif self.prompt_type == ToolingPromptType.TOOL_CONFIGURATION:
            return f"Tool Configuration: Configure tools with {context.get('config_params', 'appropriate parameters')}"
        elif self.prompt_type == ToolingPromptType.TOOL_CHAINING:
            return f"Tool Chaining: Chain {context.get('tool_sequence', 'tools in logical sequence')}"
        elif self.prompt_type == ToolingPromptType.TOOL_OPTIMIZATION:
            return f"Tool Optimization: Optimize {context.get('optimization_target', 'tool performance and efficiency')}"
        return ""

# Re-export components
__all__ = [
    'ToolingBundle', 'ToolingPromptType'
]





