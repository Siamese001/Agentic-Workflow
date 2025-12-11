# File: validation/__init__.py
# Validation Package - V18 Architecture
# Version: 18.00
# Exports all validation components for easy import

from archives.legacy_resume_gen.Older Microservices Models.v2.engine import ValidationEngine, ValidationRule, ConstraintFailureClassifier
# from archives.legacy_resume_gen.Agentic-Workflow-10_7_main.context import ValidationContext  # INVALID: Cannot import from path with hyphens
from archives.legacy_resume_gen.Older Microservices Models.v2.external import JDEnforcementValidator, AppTrackerQAValidator

__all__ = [
    'ValidationEngine',
    'ValidationRule', 
    'ConstraintFailureClassifier',
    'ValidationContext',
    'JDEnforcementValidator',
    'AppTrackerQAValidator'
]
