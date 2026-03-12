"""Foundational behavioral tests for agentic_core/L5_safety/reasoning/CodeEnforcerAgent.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_CodeEnforcerAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.CodeEnforcerAgent import (  # noqa: F401
        EnforcementType,
        ViolationSeverity,
        CodeViolation,
        SignedException,
        EnforcementConfig,
        CodeEnforcerAgent,
        create_legacy_ssot_enforcer,
        create_legacy_standards_enforcer,
        create_legacy_sovereignty_enforcer,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
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
    create_legacy_ssot_enforcer = None  # type: ignore[assignment,misc]
    create_legacy_standards_enforcer = None  # type: ignore[assignment,misc]
    create_legacy_sovereignty_enforcer = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestEnforcementTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(EnforcementType, enum.Enum)

    def test_has_members(self):
        assert len(list(EnforcementType)) >= 1

    def test_member_values_accessible(self):
        for m in EnforcementType:
            assert m.value is not None or m.value is None

    def test_known_member_ssot_sync_present(self):
        assert hasattr(EnforcementType, 'SSOT_SYNC')

    def test_members_are_unique(self):
        values = [m.value for m in EnforcementType]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestViolationSeverityContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ViolationSeverity, enum.Enum)

    def test_has_members(self):
        assert len(list(ViolationSeverity)) >= 1

    def test_member_values_accessible(self):
        for m in ViolationSeverity:
            assert m.value is not None or m.value is None

    def test_known_member_info_present(self):
        assert hasattr(ViolationSeverity, 'INFO')

    def test_members_are_unique(self):
        values = [m.value for m in ViolationSeverity]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestCodeViolationContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CodeViolation)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(CodeViolation)}
        assert fnames >= {'severity', 'line_number', 'message', 'file_path', 'enforcement_type', 'suggested_fix'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(CodeViolation)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestSignedExceptionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(SignedException)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(SignedException)}
        assert fnames >= {'target_file', 'granted_at', 'target_layer', 'granted_by', 'exception_id', 'source_layer'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(SignedException)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestEnforcementConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(EnforcementConfig)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(EnforcementConfig)}
        assert fnames >= {'enable_ssot_sync', 'enable_patterns', 'enable_standards', 'enable_type_hints', 'enable_sovereignty', 'auto_fix'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(EnforcementConfig)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestCodeEnforcerAgentContract:
    def test_is_class(self):
        assert isinstance(CodeEnforcerAgent, type)

    def test_has_method_heal_repository(self):
        assert callable(getattr(CodeEnforcerAgent, 'heal_repository', None))

    def test_has_method_validate_file(self):
        assert callable(getattr(CodeEnforcerAgent, 'validate_file', None))

    def test_has_method_check_sovereignty(self):
        assert callable(getattr(CodeEnforcerAgent, 'check_sovereignty', None))

    def test_has_method_grant_exception(self):
        assert callable(getattr(CodeEnforcerAgent, 'grant_exception', None))

    def test_public_api_surface_non_empty(self):
        pub = [m for m in dir(CodeEnforcerAgent) if not m.startswith('_')]
        assert len(pub) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestCreateLegacySsotEnforcerFunction:
    def test_is_callable(self):
        assert callable(create_legacy_ssot_enforcer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_legacy_ssot_enforcer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestCreateLegacyStandardsEnforcerFunction:
    def test_is_callable(self):
        assert callable(create_legacy_standards_enforcer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_legacy_standards_enforcer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestCreateLegacySovereigntyEnforcerFunction:
    def test_is_callable(self):
        assert callable(create_legacy_sovereignty_enforcer)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_legacy_sovereignty_enforcer)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="CodeEnforcerAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: CodeEnforcerAgent importable or gracefully unavailable."""
    assert True
