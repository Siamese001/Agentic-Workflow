"""
Core Stub Package - Semantic Validation

PURPOSE:
    Provides stub implementations for core semantic validation components.
    Used for testing semantic gatekeeper and validation logic.

STATUS: Active - Used for testing L1 Cognition layer
CLASSES:
    - SemanticGatekeeper: Validates semantic integrity of content
"""
from .semantic_gatekeeper import SemanticGatekeeper

__all__ = ["SemanticGatekeeper"]
