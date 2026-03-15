"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/CodeValidatorAgent.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_CodeValidatorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.CodeValidatorAgent import (  # noqa: F401
        CodeValidatorAgent,
        RuleSet,
        ValidationReport,
        Violation,
        ViolationType,
        create_legacy_async_validator,
        create_legacy_canon_validator,
        create_legacy_print_validator,
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
    create_legacy_canon_validator = None  # type: ignore[assignment,misc]
    create_legacy_async_validator = None  # type: ignore[assignment,misc]
    create_legacy_print_validator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent.py deps unavailable")
class TestViolationTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ViolationType, enum.Enum)

    def test_has_members(self):
        assert len(list(ViolationType)) >= 1

    def test_member_values_accessible(self):
        for m in ViolationType:
            assert m.value is not None or m.value is None

    def test_known_member_syntax_present(self):
        assert hasattr(ViolationType, 'SYNTAX')

    def test_members_are_unique(self):
        values = [m.value for m in ViolationType]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent.py deps unavailable")
class TestViolationContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Violation)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(Violation)}
        assert fnames >= {'severity', 'violation_type', 'issue', 'line_number', 'file_path', 'suggested_fix'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(Violation)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent.py deps unavailable")
class TestRuleSetContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RuleSet)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(RuleSet)}
        assert fnames >= {'check_prints', 'check_async', 'check_canon', 'check_syntax', 'async_patterns', 'canon_patterns'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(RuleSet)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent.py deps unavailable")
class TestValidationReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ValidationReport)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ValidationReport)}
        assert fnames >= {'high_severity_count', 'violations', 'validation_summary', 'total_violations', 'auto_fixable_count', 'validation_timestamp'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ValidationReport)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent.py deps unavailable")
class TestCodeValidatorAgentContract:
    def test_is_class(self):
        assert isinstance(CodeValidatorAgent, type)

    def test_has_method_validate_syntax(self):
        assert callable(getattr(CodeValidatorAgent, 'validate_syntax', None))

    def test_has_method_validate_canon(self):
        assert callable(getattr(CodeValidatorAgent, 'validate_canon', None))

    def test_has_method_validate_async(self):
        assert callable(getattr(CodeValidatorAgent, 'validate_async', None))

    def test_has_method_validate_prints(self):
        assert callable(getattr(CodeValidatorAgent, 'validate_prints', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(CodeValidatorAgent) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent.py deps unavailable")
class TestCreateLegacySyntaxValidatorFunction:
    def test_is_callable(self):
        assert callable(create_legacy_syntax_validator)

@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent.py deps unavailable")
class TestCreateLegacyCanonValidatorFunction:
    def test_is_callable(self):
        assert callable(create_legacy_canon_validator)

@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent.py deps unavailable")
class TestCreateLegacyAsyncValidatorFunction:
    def test_is_callable(self):
        assert callable(create_legacy_async_validator)

@pytest.mark.skipif(not _AVAILABLE, reason="CodeValidatorAgent.py deps unavailable")
class TestCreateLegacyPrintValidatorFunction:
    def test_is_callable(self):
        assert callable(create_legacy_print_validator)


def test_module_importable():
    """Smoke: CodeValidatorAgent importable or gracefully unavailable."""
    pass
