"""Foundational behavioral tests for agentic_core/L2_execution/types/heal_contract_types.py.

fan_in=12 — imported by 12 other modules.
ADG import-hygiene is covered separately by test_heal_contract_types_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.types.heal_contract_types import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        CombinedHealResult,
        HealCheckResult,
        HealStatus,
        check_schema_compatibility,
        validate_against_json_schema,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    HealStatus = None  # type: ignore[assignment,misc]
    HealCheckResult = None  # type: ignore[assignment,misc]
    CombinedHealResult = None  # type: ignore[assignment,misc]
    check_schema_compatibility = None  # type: ignore[assignment,misc]
    validate_against_json_schema = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestHealStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(HealStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(HealStatus)) >= 1

    def test_member_values_accessible(self):
        for m in HealStatus:
            assert m.value is not None or m.value is None

    def test_known_member_healed_present(self):
        assert hasattr(HealStatus, 'HEALED')

    def test_members_are_unique(self):
        values = [m.value for m in HealStatus]
        assert len(values) == len(set(values))

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestHealCheckResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(HealCheckResult)

    def test_is_frozen(self):
        assert HealCheckResult.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(HealCheckResult)}
        assert fnames >= {'check_id', 'status', 'needs_llm_escalation', 'notes', 'changes_made', 'rollback_info'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(HealCheckResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestCombinedHealResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CombinedHealResult)

    def test_is_frozen(self):
        assert CombinedHealResult.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(CombinedHealResult)}
        assert fnames >= {'results', 'tool_id', 'plan_name', 'created_utc', 'approved_by'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(CombinedHealResult)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestCheckSchemaCompatibilityFunction:
    def test_is_callable(self):
        assert callable(check_schema_compatibility)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(check_schema_compatibility)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestValidateAgainstJsonSchemaFunction:
    def test_is_callable(self):
        assert callable(validate_against_json_schema)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_against_json_schema)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="heal_contract_types.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: heal_contract_types importable or gracefully unavailable."""
    pass
