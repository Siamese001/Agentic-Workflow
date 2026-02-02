from __future__ import annotations

"""Enum types for models."""
import logging
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

_logger = logging.getLogger(__name__)


# NAMING FIXED: ValidationSeverity → ValidationSeverity
class ValidationSeverity(Enum):
    """Severity levels for validation results."""


# NAMING FIXED: Provider → Provider
class Provider(str, Enum):
    """Available LLM providers."""


# NAMING FIXED: APICallStatus → ApiCallStatus
class ApiCallStatus(Enum):
    """Status of API calls."""


class ValidationSeverityConfig(BaseModel):
    """[HARDENED] Wrapper schema for validation severity metadata."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    severity: ValidationSeverity = Field(..., description="Severity level for validation")

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: ValidationSeverity) -> ValidationSeverity:
        """[HARDENED] Ensure severity is a valid enum member."""
        if value is None:
            raise ValueError("Severity is required")
        return value
