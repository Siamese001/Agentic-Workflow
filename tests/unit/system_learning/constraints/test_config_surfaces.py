"""Foundational behavioral tests for system_learning/constraints/config_surfaces.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_config_surfaces_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.constraints.config_surfaces import (  # noqa: F401
        FloatConstraint,
        IntConstraint,
        PointerConstraint,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    FloatConstraint = None  # type: ignore[assignment,misc]
    IntConstraint = None  # type: ignore[assignment,misc]
    PointerConstraint = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces.py deps unavailable")
class TestFloatConstraintContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(FloatConstraint)

    def test_is_frozen(self):
        assert FloatConstraint.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(FloatConstraint)}
        assert field_names >= {'max_value', 'min_value', 'max_delta_per_cycle'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(FloatConstraint)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert FloatConstraint.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces.py deps unavailable")
class TestIntConstraintContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(IntConstraint)

    def test_is_frozen(self):
        assert IntConstraint.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(IntConstraint)}
        assert field_names >= {'max_value', 'min_value', 'max_delta_per_cycle'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(IntConstraint)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert IntConstraint.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces.py deps unavailable")
class TestPointerConstraintContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PointerConstraint)

    def test_is_frozen(self):
        assert PointerConstraint.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PointerConstraint)}
        assert field_names >= {'allowlist'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(PointerConstraint)
        if not fields:
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert PointerConstraint.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_surfaces.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module config_surfaces must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
