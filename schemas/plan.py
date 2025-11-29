# Plan schema definitions
from .base import BaseSchema
from pydantic import BaseModel
from typing import List, Optional

class PlanSchema(BaseSchema):
    """Plan execution schema"""
    steps: List[str]
    dependencies: Optional[List[str]] = None
