# Plan schema definitions
from .base import BaseSchema
from typing import List, Optional

class PlanSchema(BaseSchema):
    """Plan execution schema"""
    steps: List[str]
    dependencies: Optional[List[str]] = None
