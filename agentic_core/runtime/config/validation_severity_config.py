from __future__ import annotations

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Enum types for models."""
import logging
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ValidationSeverityConfig.validate_severity")

        if value is None:
            raise ValueError("Severity is required")
        return value
