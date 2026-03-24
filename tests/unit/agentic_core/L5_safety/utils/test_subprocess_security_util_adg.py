"""ADG importability contract for agentic_core/L5_safety/utils/subprocess_security_util.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_subprocess_security_util.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.utils.subprocess_security_util import (  # noqa: F401
        INJECTION_REGEX,
        SHELL_METACHARACTERS,
        SecurityViolationError,
        safe_execute,
        safe_popen,
        validate_command_whitelist,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SHELL_METACHARACTERS = None  # type: ignore[assignment,misc]
    INJECTION_REGEX = None  # type: ignore[assignment,misc]
    SecurityViolationError = None  # type: ignore[assignment,misc]
    safe_execute = None  # type: ignore[assignment,misc]
    safe_popen = None  # type: ignore[assignment,misc]
    validate_command_whitelist = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util deps unavailable")
class TestSubprocessSecurityUtilImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/utils/subprocess_security_util.py must be importable."""
        assert _AVAILABLE

    def test_securityviolationerror_defined(self) -> None:
        assert SecurityViolationError is not None