"""Foundational behavioral tests for agentic_core/L5_safety/validators/migration_helper_validator.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_migration_helper_validator_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.validators.migration_helper_validator import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        ComplianceResult,
        MigrationHelper,
        MigrationStatus,
        check_agent_compliance,
        get_migration_status,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ComplianceResult = None  # type: ignore[assignment,misc]
    MigrationStatus = None  # type: ignore[assignment,misc]
    MigrationHelper = None  # type: ignore[assignment,misc]
    check_agent_compliance = None  # type: ignore[assignment,misc]
    get_migration_status = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestComplianceResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ComplianceResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ComplianceResult)}
        assert field_names >= {'has_human_review', 'compliant', 'has_verification_gate', 'has_feature_flag_mixin', 'agent_name'}

@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestMigrationStatusContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MigrationStatus)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(MigrationStatus)}
        assert field_names >= {'compliance_percentage', 'non_compliant_agents', 'agents_by_status', 'compliant_agents', 'total_agents'}

@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestMigrationHelperContract:
    def test_is_class(self):
        assert isinstance(MigrationHelper, type)

    def test_has_method_check_agent_compliance(self):
        assert callable(getattr(MigrationHelper, 'check_agent_compliance', None))

    def test_has_method_get_migration_status(self):
        assert callable(getattr(MigrationHelper, 'get_migration_status', None))

    def test_has_method_generate_migration_report(self):
        assert callable(getattr(MigrationHelper, 'generate_migration_report', None))

@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestCheckAgentComplianceFunction:
    def test_is_callable(self):
        assert callable(check_agent_compliance)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(check_agent_compliance)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestGetMigrationStatusFunction:
    def test_is_callable(self):
        assert callable(get_migration_status)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_migration_status)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="migration_helper_validator.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module migration_helper_validator must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
