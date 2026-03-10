"""
Security Validation Suite - Phase 2 Red Team Integration

Provides a unified interface for running all security validators:
- Adversarial probing
- Boundary testing
- Prompt injection detection (future)

This module creates a RedTeamValidationSuite that orchestrates
security testing across multiple validators.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

Logger = logging.getLogger(__name__)


@dataclass
class SecurityValidationResult:
    """Result from a security validation run."""

    validator_name: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SecuritySuiteResult:
    """Aggregated result from running the full security suite."""

    overall_valid: bool
    validators_run: int
    validators_passed: int
    validators_failed: int
    results: list[SecurityValidationResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    execution_time_ms: float = 0.0


class RedTeamValidationSuite:
    """
    Orchestrates security validation across multiple red team validators.

    Usage:
        suite = RedTeamValidationSuite()
        result = suite.run_all(content={"test": "data"})
        if not result.overall_valid:
            print(f"Security issues found: {result.validators_failed} validators failed")
    """

    def __init__(self) -> None:
        """Initialize the security validation suite."""
        self._validators: dict[str, Any] = {}
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization of validators."""
        if self._initialized:
            return

        try:
            from agentic_core.L5_safety.validators.red_team_integration_types import (
                get_adversarial_validator,
                get_boundary_validator,
            )

            self._validators["adversarial_probe"] = get_adversarial_validator()
            self._validators["boundary_testing"] = get_boundary_validator()
            self._initialized = True
            Logger.info(f"[SecuritySuite] Initialized with {len(self._validators)} validators")
        except ImportError as e:
            Logger.warning(f"[SecuritySuite] Could not import validators: {e}")
            self._initialized = True

    def run_validator(
        self,
        validator_name: str,
        content: Any,
        context: dict | None = None,
    ) -> SecurityValidationResult:
        """
        Run a specific validator.

        Args:
            validator_name: Name of the validator to run
            content: Content to validate
            context: Optional validation context

        Returns:
            SecurityValidationResult with validation details
        """
        self._ensure_initialized()
        context = context or {}

        if validator_name not in self._validators:
            return SecurityValidationResult(
                validator_name=validator_name,
                valid=False,
                errors=[f"Validator '{validator_name}' not found"],
            )

        try:
            validator = self._validators[validator_name]
            result = validator.validate(content, context)

            return SecurityValidationResult(
                validator_name=validator_name,
                valid=result.get("valid", False),
                errors=result.get("errors", []),
                warnings=result.get("warnings", []),
                metadata={k: v for k, v in result.items() if k not in ("valid", "errors", "warnings")},
            )

        except Exception as e:
            Logger.error(f"[SecuritySuite] Validator {validator_name} failed: {e}")
            return SecurityValidationResult(
                validator_name=validator_name,
                valid=False,
                errors=[f"Validator error: {str(e)}"],
            )

    def run_all(self, content: Any, context: dict | None = None) -> SecuritySuiteResult:
        """
        Run all registered security validators.

        Args:
            content: Content to validate
            context: Optional validation context

        Returns:
            SecuritySuiteResult with aggregated results
        """
        import time

        self._ensure_initialized()
        context = context or {}

        start_time = time.time()
        results: list[SecurityValidationResult] = []

        for validator_name in self._validators:
            result = self.run_validator(validator_name, content, context)
            results.append(result)

        execution_time = (time.time() - start_time) * 1000

        passed = sum(1 for r in results if r.valid)
        failed = len(results) - passed

        return SecuritySuiteResult(
            overall_valid=failed == 0,
            validators_run=len(results),
            validators_passed=passed,
            validators_failed=failed,
            results=results,
            execution_time_ms=execution_time,
        )

    def get_available_validators(self) -> list[str]:
        """Get list of available validator names."""
        self._ensure_initialized()
        return list(self._validators.keys())

    def get_status(self) -> dict[str, Any]:
        """Get current status of the security suite."""
        self._ensure_initialized()
        return {
            "initialized": self._initialized,
            "validators_available": list(self._validators.keys()),
            "validator_count": len(self._validators),
        }


# Global suite instance
_security_suite: RedTeamValidationSuite | None = None


def get_security_suite() -> RedTeamValidationSuite:
    """Get or create the global security validation suite."""
    global _security_suite
    if _security_suite is None:
        _security_suite = RedTeamValidationSuite()
    return _security_suite


def run_security_validation(content: Any, context: dict | None = None) -> SecuritySuiteResult:
    """
    Convenience function to run full security validation.

    Args:
        content: Content to validate
        context: Optional validation context

    Returns:
        SecuritySuiteResult with all validation results
    """
    suite = get_security_suite()
    return suite.run_all(content, context)
