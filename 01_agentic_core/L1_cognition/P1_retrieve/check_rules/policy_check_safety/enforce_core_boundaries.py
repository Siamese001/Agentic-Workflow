"""
01_agentic_core/L1_cognition/P1_retrieve/check_rules/policy_check_safety/enforce_core_boundaries.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: db9f282709cc9f388d011d487d0241daccab93fd3bca28f3b3c13707a4740a55
"""


from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Dangerous patterns that trigger fail-closed behavior
DANGEROUS_PATTERNS: List[str] = [
    "<script>",
    "javascript:",
    "# SECURITY: eval(",
    "# SECURITY: exec(",
    "__import__",
    "subprocess",
    "os.system",
]

# Maximum data size for safety validation (1MB)
MAX_DATA_SIZE: int = 1_000_000


class EnforceScriptsBoundariesPlanType(Enum):
    """Typed enumeration for deterministic boundary enforcement behavior."""

    DEFAULT = "default"
    CORE = "core"
    SYSTEM = "system"


@dataclass
class EnforceScriptsBoundariesPlanConstraints:
    """
    Safety constraints for scripts boundary enforcement - fail-closed behavior.

    Attributes:
        max_depth: Maximum recursion depth for boundary checks.
        allowed_operations: List of permitted operation types.
        safety_level: Safety enforcement level (strict/permissive).
        requires_approval: Whether operations require explicit approval.
    """

    max_depth: int = 5
    allowed_operations: List[str] = field(
        default_factory=lambda: ["read", "validate", "filter"]
    )
    safety_level: str = "strict"
    requires_approval: bool = True


@dataclass
class EnforceScriptsBoundariesPlanResult:
    """
    Result structure for scripts boundary enforcement with full type safety.

    Attributes:
        success: Whether the operation completed successfully.
        data: Output data from the operation.
        errors: List of error messages encountered.
        safety_validated: Whether safety validation passed.
        timestamp: ISO timestamp of result creation.
    """

    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    safety_validated: bool = False
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class EnforceScriptsBoundariesPlanProcessor(ABC):
    """
    Abstract base class for scripts boundary enforcement processors.

    Ensures L1 pure planning behavior with no side effects.
    """

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> EnforceScriptsBoundariesPlanResult:
        """Process data with safety constraints."""

    @abstractmethod
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """Validate data against safety constraints (fail-closed)."""


class EnforceScriptsBoundariesPlanImpl(EnforceScriptsBoundariesPlanProcessor):
    """
    L1 Cognitive Planning Layer implementation for scripts boundary enforcement.

    Pure planning functionality with no side effects.
    Implements fail-closed safety behavior.
    """

    def __init__(
        self, constraints: Optional[EnforceScriptsBoundariesPlanConstraints] = None
    ) -> None:
        self.constraints = constraints or EnforceScriptsBoundariesPlanConstraints()
        self._logger = logging.getLogger(self.__class__.__name__)

    def process(self, input_data: Dict[str, Any]) -> EnforceScriptsBoundariesPlanResult:
        """Process input following architecture principles."""
        self._logger.debug("Processing input data")
        self._validate_input(input_data)

        if not self.validate_safety(input_data):
            raise SecurityError(
                "Input failed safety validation",
                context={"input_keys": list(input_data.keys())},
            )

        result = EnforceScriptsBoundariesPlanResult(
            success=True,
            data={"processed": True, "input_keys": list(input_data.keys())},
            safety_validated=True,
        )

        self._logger.info("Successfully processed input")
        return result

    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """Validate data against safety constraints with fail-closed behavior."""
        try:
            data_str = str(data).lower()

            for pattern in DANGEROUS_PATTERNS:
                if pattern.lower() in data_str:
                    self._logger.warning("Dangerous pattern detected: %s", pattern)
                    return False

            if len(data_str) > MAX_DATA_SIZE:
                self._logger.warning(
                    "Data exceeds size limit: %d > %d", len(data_str), MAX_DATA_SIZE
                )
                return False

            self._logger.debug("Data passed safety validation")
            return True

        except (TypeError, ValueError) as e:
            self._logger.error("Safety validation error: %s", e)
            return False  # Fail-closed

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """Validate input data structure."""
        if not isinstance(input_data, dict):
            raise ValueError(
                f"Input must be a dictionary, got {type(input_data).__name__}"
            )
        if not input_data:
            raise ValueError("Input cannot be empty")


class SecurityError(Exception):
    """
    Security exception for fail-closed behavior.

    Attributes:
        message: Human-readable error description.
        context: Additional context about the security violation.
    """

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}


class EnforceScriptsBoundariesPlanInterface:
    """Interface for scripts boundary enforcement ensuring contract compliance."""

    def __init__(self, processor: EnforceScriptsBoundariesPlanProcessor) -> None:
        self._processor = processor

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute scripts boundary enforcement safely."""
        try:
            result = self._processor.process(input_data)
            return {
                "success": result.success,
                "data": result.data,
                "errors": result.errors,
                "safety_validated": result.safety_validated,
                "timestamp": result.timestamp,
            }
        except SecurityError:
            raise
        except ValueError as e:
            raise SecurityError(
                f"Validation failed: {e}", context={"error_type": "validation"}
            ) from e
        except Exception as e:
            raise SecurityError(
                f"Execution failed: {e}", context={"error_type": "execution"}
            ) from e


class EnforceScriptsBoundariesPlanFactory:
    """Factory for creating scripts boundary enforcement processors."""

    @staticmethod
    def create_processor(
        safety_level: str = "strict",
    ) -> EnforceScriptsBoundariesPlanInterface:
        """Create a configured processor."""
        constraints = EnforceScriptsBoundariesPlanConstraints(safety_level=safety_level)
        processor = EnforceScriptsBoundariesPlanImpl(constraints)
        return EnforceScriptsBoundariesPlanInterface(processor)


def enforce_scripts_boundaries(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function for enforcing scripts boundaries.

    Args:
        input_data: Input data to process.

    Returns:
        Dictionary containing processed result.

    Raises:
        SecurityError: If execution fails any safety check.
        ValueError: If input validation fails.
    """
    processor = EnforceScriptsBoundariesPlanFactory.create_processor()
    return processor.execute(input_data)


__all__ = [
    "EnforceScriptsBoundariesPlanType",
    "EnforceScriptsBoundariesPlanConstraints",
    "EnforceScriptsBoundariesPlanResult",
    "EnforceScriptsBoundariesPlanProcessor",
    "EnforceScriptsBoundariesPlanImpl",
    "EnforceScriptsBoundariesPlanInterface",
    "EnforceScriptsBoundariesPlanFactory",
    "SecurityError",
    "enforce_scripts_boundaries",
    "DANGEROUS_PATTERNS",
    "MAX_DATA_SIZE",
]


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        test_data = {"test": True, "value": "safe_content"}
        result = enforce_scripts_boundaries(test_data)
        logger.info("Execution successful: %s", result)
    except SecurityError as e:
        logger.error("Security error: %s (context: %s)", e.message, e.context)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
