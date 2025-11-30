"""
Shared Schemas
LEVEL 5 - Common Pydantic models and data structures shared across engines
"""

from .base_models import *
from .profile_models import *

# Re-export validation models from utils for convenience
from ..utils.validation import ValidationResult, ValidationReport, ValidationLevel

__all__ = [
    # Base models
    "BaseModel",
    "TimestampedModel",
    "IdentifiableModel",
    
    # Profile models
    "UserProfile",
    "ContactInfo",
    "ExperienceEntry",
    "EducationEntry",
    "SkillEntry",
    "SkillsByCategory",
    
    # Validation models (re-exported from utils)
    "ValidationError",
    "ValidationResult",
    "ValidationReport",
    "ValidationLevel"
]
