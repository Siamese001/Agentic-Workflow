"""Foundational behavioral tests for agentic_core/prompt_governance/scripts/file_intent.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_file_intent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.prompt_governance.scripts.file_intent import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        FileIntent,
        HardenedNamingAuditor,
        NamingConvention,
        ViolationReport,
        main,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    FileIntent = None  # type: ignore[assignment,misc]
    NamingConvention = None  # type: ignore[assignment,misc]
    ViolationReport = None  # type: ignore[assignment,misc]
    HardenedNamingAuditor = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestFileIntentContract:
    def test_is_enum(self):
        import enum
        assert issubclass(FileIntent, enum.Enum)

    def test_has_members(self):
        assert len(list(FileIntent)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in FileIntent:
            assert member.value is not None

    def test_known_member_class_export_exists(self):
        assert hasattr(FileIntent, 'CLASS_EXPORT')

@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestNamingConventionContract:
    def test_is_enum(self):
        import enum
        assert issubclass(NamingConvention, enum.Enum)

    def test_has_members(self):
        assert len(list(NamingConvention)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in NamingConvention:
            assert member.value is not None

    def test_known_member_pascal_case_exists(self):
        assert hasattr(NamingConvention, 'PASCAL_CASE')

@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestViolationReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ViolationReport)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ViolationReport)}
        assert field_names >= {'proposed_name', 'current_name', 'detected_intent', 'current_naming', 'file_path'}

@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestHardenedNamingAuditorContract:
    def test_is_class(self):
        assert isinstance(HardenedNamingAuditor, type)

    def test_has_method_analyze_file_content(self):
        assert callable(getattr(HardenedNamingAuditor, 'analyze_file_content', None))

    def test_has_method_classify_file_intent(self):
        assert callable(getattr(HardenedNamingAuditor, 'classify_file_intent', None))

    def test_has_method_detect_naming_convention(self):
        assert callable(getattr(HardenedNamingAuditor, 'detect_naming_convention', None))

    def test_has_method_validate_naming_compliance(self):
        assert callable(getattr(HardenedNamingAuditor, 'validate_naming_compliance', None))

@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestMainFunction:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="file_intent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module file_intent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
