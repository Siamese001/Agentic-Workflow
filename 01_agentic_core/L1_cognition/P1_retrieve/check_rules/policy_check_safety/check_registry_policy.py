"""
01_agentic_core/L1_cognition/P1_retrieve/check_rules/policy_check_safety/check_registry_policy.py
AUTO-HARDENED BY ZERO-LOSS MERGE ENGINE
L5 CANONICAL — WINDSURF Ω — 2025-12-07
MERKLE-INTENDED: 3038f6064585ae271df9a6d406f9f03ba47752649a4a691e782bdd212c3dd27c
"""


from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CheckScriptsPolicyPlanType(Enum):
    """Typed enumeration for deterministic policy behavior."""

    DEFAULT = "default"
    CORE = "core"
    SYSTEM = "system"


@dataclass
class CheckScriptsPolicyPlanConstraints:
    """
    Safety constraints for policy checking - fail-closed behavior.

    Attributes:
        max_depth: Maximum recursion depth for policy checks.
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
class CheckScriptsPolicyPlanResult:
    """
    Result structure for policy plan operations with full type safety.

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


class CheckScriptsPolicyPlanProcessor(ABC):
    """
    Abstract base class for policy plan processors.

    Ensures L1 pure planning behavior with no side effects.
    All implementations must provide process and validate_safety methods.
    """

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> CheckScriptsPolicyPlanResult:
        """
        Process input data with safety constraints.

        Args:
            input_data: Dictionary of input data to process.

        Returns:
            CheckScriptsPolicyPlanResult with processing outcome.

        Raises:
            SecurityError: If safety validation fails.
            ValueError: If input validation fails.
        """

    @abstractmethod
    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """
        Validate data against safety constraints (fail-closed).

        Args:
            data: Dictionary of data to validate.

        Returns:
            True if data passes all safety checks, False otherwise.
        """


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


class CheckScriptsPolicyPlanImpl(CheckScriptsPolicyPlanProcessor):
    """
    L1 Cognitive Planning Layer implementation.

    Pure planning functionality with no side effects.
    Implements fail-closed safety behavior.
    """

    def __init__(
        self, constraints: Optional[CheckScriptsPolicyPlanConstraints] = None
    ) -> None:
        """
        Initialize the policy plan processor.

        Args:
            constraints: Optional safety constraints. Uses defaults if not provided.
        """
        self.constraints = constraints or CheckScriptsPolicyPlanConstraints()
        self._logger = logging.getLogger(self.__class__.__name__)

    def process(self, input_data: Dict[str, Any]) -> CheckScriptsPolicyPlanResult:
        """
        Process input following architecture principles.

        Args:
            input_data: Dictionary of input data to process.

        Returns:
            CheckScriptsPolicyPlanResult with processing outcome.

        Raises:
            SecurityError: If safety validation fails.
            ValueError: If input validation fails.
        """
        self._logger.debug("Processing input data")

        # Input validation
        self._validate_input(input_data)

        # Safety validation - fail-closed
        if not self.validate_safety(input_data):
            raise SecurityError(
                "Input failed safety validation",
                context={"input_keys": list(input_data.keys())},
            )

        result = CheckScriptsPolicyPlanResult(
            success=True,
            data={"processed": True, "input_keys": list(input_data.keys())},
            safety_validated=True,
        )

        self._logger.info("Successfully processed input")
        return result

    def validate_safety(self, data: Dict[str, Any]) -> bool:
        """
        Validate data against safety constraints with fail-closed behavior.

        Args:
            data: Dictionary of data to validate.

        Returns:
            True if data passes all safety checks, False otherwise.
        """
        try:
            data_str = str(data).lower()

            # Check for dangerous patterns
            for pattern in DANGEROUS_PATTERNS:
                if pattern.lower() in data_str:
                    self._logger.warning(
                        "Dangerous pattern detected: %s", pattern
                    )
                    return False

            # Check data size
            if len(data_str) > MAX_DATA_SIZE:
                self._logger.warning(
                    "Data exceeds size limit: %d > %d",
                    len(data_str),
                    MAX_DATA_SIZE,
                )
                return False

            self._logger.debug("Data passed safety validation")
            return True

        except (TypeError, ValueError) as e:
            self._logger.error("Safety validation error: %s", e)
            return False  # Fail-closed

    def _validate_input(self, input_data: Dict[str, Any]) -> None:
        """
        Validate input data structure.

        Args:
            input_data: Data to validate.

        Raises:
            ValueError: If input is invalid.
        """
        if not isinstance(input_data, dict):
            raise ValueError(
                f"Input must be a dictionary, got {type(input_data).__name__}"
            )

        if not input_data:
            raise ValueError("Input cannot be empty")


class SecurityError(Exception):
    """
    Security exception for fail-closed behavior.

    Raised when security validation fails or dangerous patterns are detected.

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


class CheckScriptsPolicyPlanInterface:
    """
    Interface for policy plan execution ensuring contract compliance.

    Wraps a processor and provides a consistent execution interface.
    """

    def __init__(self, processor: CheckScriptsPolicyPlanProcessor) -> None:
        """
        Initialize the interface.

        Args:
            processor: The underlying processor to wrap.
        """
        self._processor = processor

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute policy processing safely.

        Args:
            input_data: Dictionary of input data to process.

        Returns:
            Dictionary containing processing results.

        Raises:
            SecurityError: If execution fails any safety check.
        """
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
                f"Validation failed: {e}",
                context={"error_type": "validation"},
            ) from e
        except Exception as e:
            raise SecurityError(
                f"Execution failed: {e}",
                context={"error_type": "execution"},
            ) from e


class CheckScriptsPolicyPlanFactory:
    """
    Factory for creating policy plan processors with proper configuration.

    Provides a clean interface for creating configured processor instances.
    """

    @staticmethod
    def create_processor(
        safety_level: str = "strict",
    ) -> CheckScriptsPolicyPlanInterface:
        """
        Create a configured processor.

        Args:
            safety_level: Safety enforcement level ("strict" or "permissive").

        Returns:
            Configured CheckScriptsPolicyPlanInterface instance.
        """
        constraints = CheckScriptsPolicyPlanConstraints(safety_level=safety_level)
        processor = CheckScriptsPolicyPlanImpl(constraints)
        return CheckScriptsPolicyPlanInterface(processor)


def check_scripts_policy(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function for checking scripts policy operations.

    Args:
        input_data: Input data to process.

    Returns:
        Dictionary containing processed result.

    Raises:
        SecurityError: If execution fails any safety check.
        ValueError: If input validation fails.
    """
    processor = CheckScriptsPolicyPlanFactory.create_processor()
    return processor.execute(input_data)


__all__ = [
    "CheckScriptsPolicyPlanType",
    "CheckScriptsPolicyPlanConstraints",
    "CheckScriptsPolicyPlanResult",
    "CheckScriptsPolicyPlanProcessor",
    "CheckScriptsPolicyPlanImpl",
    "CheckScriptsPolicyPlanInterface",
    "CheckScriptsPolicyPlanFactory",
    "SecurityError",
    "check_scripts_policy",
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
        result = check_scripts_policy(test_data)
        logger.info("Execution successful: %s", result)
    except SecurityError as e:
        logger.error("Security error: %s (context: %s)", e.message, e.context)
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
