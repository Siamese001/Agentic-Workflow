"""Split module 2 for exceptions_impl."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class ValidationError(AgenticWorkflowError):
    """Validation rule failed."""
    pass

class APIError(AgenticWorkflowError):
    """External API call failed."""
    pass

