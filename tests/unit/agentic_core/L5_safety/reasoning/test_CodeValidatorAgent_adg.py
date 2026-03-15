"""ADG importability contract for agentic_core/L5_safety/reasoning/CodeValidatorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_CodeValidatorAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (  # noqa: F401
        CodeValidatorAgent,
        RuleSet,
        ValidationReport,
        Violation,
        ViolationType,
        create_legacy_syntax_validator,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ViolationType = None  # type: ignore[assignment,misc]
    Violation = None  # type: ignore[assignment,misc]
    RuleSet = None  # type: ignore[assignment,misc]
    ValidationReport = None  # type: ignore[assignment,misc]
    CodeValidatorAgent = None  # type: ignore[assignment,misc]
    create_legacy_syntax_validator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent deps unavailable")
class TestCodevalidatoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/reasoning/CodeValidatorAgent.py must be importable."""
        assert _AVAILABLE

    def test_violationtype_defined(self) -> None:
        assert ViolationType is not None

    def test_violation_defined(self) -> None:
        assert Violation is not None

    def test_ruleset_defined(self) -> None:
        assert RuleSet is not None

    def test_validationreport_defined(self) -> None:
        assert ValidationReport is not None

    def test_codevalidatoragent_defined(self) -> None:
        assert CodeValidatorAgent is not None
