"""Types and models for check_schema_policy."""

from enum import Enum
import logging


logger = logging.getLogger(__name__)
class CheckDataPolicyPlanType(Enum):
    """L5 Typed enumeration for deterministic behavior"""
    DEFAULT = 'default'
    CORE = 'core'
    SYSTEM = 'system'
