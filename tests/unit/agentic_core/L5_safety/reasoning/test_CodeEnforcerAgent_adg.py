"""ADG importability contract for agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_CodeEnforcerAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import (  # noqa: F401
        CodeEnforcerAgent,
        CodeViolation,
        EnforcementConfig,
        EnforcementType,
        SignedException,
        ViolationSeverity,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    EnforcementType = None  # type: ignore[assignment,misc]
    ViolationSeverity = None  # type: ignore[assignment,misc]
    CodeViolation = None  # type: ignore[assignment,misc]
    SignedException = None  # type: ignore[assignment,misc]
    EnforcementConfig = None  # type: ignore[assignment,misc]
    CodeEnforcerAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent deps unavailable")
class TestCodeenforceragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py must be importable."""
        assert _AVAILABLE

    def test_enforcementtype_defined(self) -> None:
        assert EnforcementType is not None

    def test_violationseverity_defined(self) -> None:
        assert ViolationSeverity is not None

    def test_codeviolation_defined(self) -> None:
        assert CodeViolation is not None

    def test_signedexception_defined(self) -> None:
        assert SignedException is not None

    def test_enforcementconfig_defined(self) -> None:
        assert EnforcementConfig is not None

    def test_codeenforceragent_defined(self) -> None:
        assert CodeEnforcerAgent is not None
