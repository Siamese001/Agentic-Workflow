"""Validation and Guard modules for execute_ssot - extracted during Wave 1 modularization.

This module contains PreFlightValidator and NonInteractiveGuard classes.
"""

from typing import Any


class PreFlightValidator:
    """Validates execution preconditions before starting workflow."""

    def __init__(self, args: Any, console: Any = None):
        self.args = args
        self.console = console
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> tuple[bool, list[str], list[str]]:
        """Run all pre-flight validations.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []

        # Validate args
        self._validate_args()

        # Validate environment
        self._validate_environment()

        # Validate registry
        self._validate_registry()

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_args(self) -> None:
        """Validate command line arguments."""
        if not self.args:
            self.errors.append("No arguments provided")
            return

        # Check required args
        if hasattr(self.args, 'targets') and not self.args.targets:
            self.warnings.append("No targets specified")

    def _validate_environment(self) -> None:
        """Validate execution environment."""
        # Environment checks
        pass

    def _validate_registry(self) -> None:
        """Validate agent registry state."""
        # Registry validation
        pass


class NonInteractiveGuard:
    """Guards for non-interactive execution mode."""

    def __init__(self, args: Any):
        self.args = args
        self.blocked_operations: list[str] = []

    def check_operation(self, operation: str) -> bool:
        """Check if an operation is allowed in non-interactive mode.

        Args:
            operation: Operation name to check

        Returns:
            True if operation is allowed

        Raises:
            ValueError: If args is None or operation is empty
        """
        if self.args is None:
            raise ValueError("Args cannot be None")
        if not operation:
            raise ValueError("Operation cannot be empty")
        # Check if non-interactive
        if hasattr(self.args, 'non_interactive') and self.args.non_interactive:
            blocked = ['prompt', 'confirm', 'interactive_config']
            if operation in blocked:
                self.blocked_operations.append(operation)
                return False
        return True

    def get_blocked_operations(self) -> list[str]:
        """Get list of operations blocked in current mode."""
        return self.blocked_operations.copy()
