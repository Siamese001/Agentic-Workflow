#!/usr/bin/env python3
"""
Output Injection Bundles
Section 6: Prompt Governance - Output formatting and structure prompt injection bundles
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class OutputPromptType(str, Enum):
    """Output prompt injection type enumeration"""
    STRUCTURED_FORMAT = "structured_format"
    JSON_SCHEMA = "json_schema"
    MARKDOWN_FORMAT = "markdown_format"
    CUSTOM_TEMPLATE = "custom_template"

@dataclass
class OutputBundle:
    """Output formatting injection bundle"""
    bundle_id: str
    prompt_type: OutputPromptType
    templates: List[str]
    metadata: Dict[str, Any]
    
    def inject_output_guidance(self, base_prompt: str, output_context: Dict[str, Any]) -> str:
        """Inject output formatting guidance into prompt"""
        guidance = self._generate_output_guidance(output_context)
        return f"{base_prompt}\n\nOutput Format Requirements:\n{guidance}"
    
    def _generate_output_guidance(self, context: Dict[str, Any]) -> str:
        """Generate output-specific guidance"""
        if self.prompt_type == OutputPromptType.STRUCTURED_FORMAT:
            return f"Structured Format: Provide output in {context.get('structure', 'well-organized structure')}"
        elif self.prompt_type == OutputPromptType.JSON_SCHEMA:
            return f"JSON Schema: Follow {context.get('schema', 'specified JSON schema')} exactly"
        elif self.prompt_type == OutputPromptType.MARKDOWN_FORMAT:
            return f"Markdown Format: Use {context.get('markdown_style', 'standard markdown formatting')}"
        elif self.prompt_type == OutputPromptType.CUSTOM_TEMPLATE:
            return f"Custom Template: Follow {context.get('template', 'specified template format')}"
        return ""

# Re-export components
__all__ = [
    'OutputBundle', 'OutputPromptType'
]
