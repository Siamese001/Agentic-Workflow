# Agent schema definitions
from .base import BaseSchema
from pydantic import BaseModel
from typing import List, Optional

class AgentSchema(BaseSchema):
    """Agent configuration schema"""
    type: str
    capabilities: List[str]
    config: Optional[Dict[str, Any]] = None
