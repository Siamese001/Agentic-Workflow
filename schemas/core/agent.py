# Agent schema definitions
from .base import BaseSchema
from typing import List, Optional, Dict, Any

class AgentSchema(BaseSchema):
    """Agent configuration schema"""
    type: str
    capabilities: List[str]
    config: Optional[Dict[str, Any]] = None
