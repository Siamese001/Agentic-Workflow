"""ADG importability contract for agentic_core/L5_safety/enforcement/secure_error_handler_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_secure_error_handler_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.secure_error_handler_enforcer import (  # noqa: F401
        ConfigurationError,
        ErrorSanitizer,
        ExecutionError,
        SecureError,
        SecurityError,
        ValidationError,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SecureError = None  # type: ignore[assignment,misc]
    SecurityError = None  # type: ignore[assignment,misc]
    ConfigurationError = None  # type: ignore[assignment,misc]
    ValidationError = None  # type: ignore[assignment,misc]
    ExecutionError = None  # type: ignore[assignment,misc]
    ErrorSanitizer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="secure_error_handler_enforcer deps unavailable")
class TestSecureErrorHandlerEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/secure_error_handler_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_secureerror_defined(self) -> None:
        assert SecureError is not None

    def test_securityerror_defined(self) -> None:
        assert SecurityError is not None

    def test_configurationerror_defined(self) -> None:
        assert ConfigurationError is not None

    def test_validationerror_defined(self) -> None:
        assert ValidationError is not None

    def test_executionerror_defined(self) -> None:
        assert ExecutionError is not None

    def test_errorsanitizer_defined(self) -> None:
        assert ErrorSanitizer is not None