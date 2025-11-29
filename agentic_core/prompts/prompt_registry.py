#!/usr/bin/env python3
"""
Prompt Registry
Section 6: Prompt Governance - Centralized prompt management
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PromptCategory(str, Enum):
    """Prompt category enumeration"""
    PLANNING = "planning"
    EXECUTION = "execution"
    ORCHESTRATION = "orchestration"
    MEMORY = "memory"
    SAFETY = "safety"
    GENERAL = "general"

class PromptVersion(str, Enum):
    """Prompt version enumeration"""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"
    V4 = "v4"
    V5 = "v5"

@dataclass
class PromptTemplate:
    """Prompt template definition"""
    template_id: str
    name: str
    category: PromptCategory
    version: PromptVersion
    template: str
    parameters: List[str]
    metadata: Dict[str, Any]

class PromptRegistry:
    """Centralized prompt management registry"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self.active_templates: Dict[str, PromptTemplate] = {}
    
    def register_template(self, template: PromptTemplate) -> bool:
        """Register a prompt template"""
        try:
            self.templates[template.template_id] = template
            self.active_templates[template.template_id] = template
            logger.info(f"Prompt template registered: {template.template_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register prompt template: {e}")
            return False
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get prompt template by ID"""
        return self.templates.get(template_id)
    
    def render_template(self, template_id: str, parameters: Dict[str, Any]) -> Optional[str]:
        """Render prompt template with parameters"""
        template = self.get_template(template_id)
        if not template:
            return None
        
        try:
            return template.template.format(**parameters)
        except KeyError as e:
            logger.error(f"Missing parameter for template {template_id}: {e}")
            return None

# Re-export components
__all__ = [
    'PromptRegistry', 'PromptTemplate', 'PromptCategory', 'PromptVersion'
]
