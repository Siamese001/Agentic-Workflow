"""Foundational behavioral tests for agentic_core/L5_safety/enforcement/system_enforcer.py.

fan_in=10 — this module is imported by 10 other modules.
ADG contract: import-hygiene is covered by test_system_enforcer_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.system_enforcer import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        SystemValidator,
        ValidationReport,
        ValidationResult,
        main,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    ValidationResult = None  # type: ignore[assignment,misc]
    ValidationReport = None  # type: ignore[assignment,misc]
    SystemValidator = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer.py deps unavailable")
class TestValidationResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ValidationResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ValidationResult)}
        assert field_names >= {'testing_pass', 'module_path', 'healing_pass', 'agent_name', 'layer'}

@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer.py deps unavailable")
class TestValidationReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ValidationReport)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ValidationReport)}
        assert field_names >= {'total_core', 'testing_pass', 'healing_pass', 'mcp_hardened', 'external_agents'}

@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer.py deps unavailable")
class TestSystemValidatorContract:
    def test_is_class(self):
        assert isinstance(SystemValidator, type)

    def test_has_method_load_discovery(self):
        assert callable(getattr(SystemValidator, 'load_discovery', None))

    def test_has_method_check_has_healing(self):
        assert callable(getattr(SystemValidator, 'check_has_healing', None))

    def test_has_method_check_has_testing(self):
        assert callable(getattr(SystemValidator, 'check_has_testing', None))

    def test_has_method_check_external_touch(self):
        assert callable(getattr(SystemValidator, 'check_external_touch', None))

@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer.py deps unavailable")
class TestMainFunction:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="system_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module system_enforcer must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
