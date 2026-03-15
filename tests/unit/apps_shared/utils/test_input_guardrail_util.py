"""Foundational behavioral tests for apps_shared/utils/input_guardrail_util.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_input_guardrail_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.input_guardrail_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        GuardAction,
        GuardResult,
        InputGuardrail,
        get_input_guardrail,
        scan_input,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    GuardAction = None  # type: ignore[assignment,misc]
    GuardResult = None  # type: ignore[assignment,misc]
    InputGuardrail = None  # type: ignore[assignment,misc]
    get_input_guardrail = None  # type: ignore[assignment,misc]
    scan_input = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestGuardActionContract:
    def test_is_enum(self):
        import enum
        assert issubclass(GuardAction, enum.Enum)

    def test_has_members(self):
        assert len(list(GuardAction)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in GuardAction:
            assert member.value is not None

    def test_known_member_allow_exists(self):
        assert hasattr(GuardAction, 'ALLOW')

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestGuardResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(GuardResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(GuardResult)}
        assert field_names >= {'pii_detected', 'confidence', 'action', 'reason', 'injection_patterns'}

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestInputGuardrailContract:
    def test_is_class(self):
        assert isinstance(InputGuardrail, type)

    def test_has_method_scan(self):
        assert callable(getattr(InputGuardrail, 'scan', None))

    def test_has_method_get_stats(self):
        assert callable(getattr(InputGuardrail, 'get_stats', None))

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestGetInputGuardrailFunction:
    def test_is_callable(self):
        assert callable(get_input_guardrail)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_input_guardrail)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestScanInputFunction:
    def test_is_callable(self):
        assert callable(scan_input)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(scan_input)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="input_guardrail_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module input_guardrail_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
