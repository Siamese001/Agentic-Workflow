# Base schema classes
from pydantic import BaseModel
from typing import Dict, Any, Optional

class BaseSchema(BaseModel):
    """Base schema for all components"""
    name: str
    version: str = "1.0.0"
    metadata: Optional[Dict[str, Any]] = None
