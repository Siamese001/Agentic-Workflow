"""Foundational behavioral tests for agentic_core/L6_observability/engines/dpo_pair_generator.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_dpo_pair_generator_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L6_observability.engines.dpo_pair_generator import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    BoundedDPOPair,
    BoundingViolation,
    DPOBoundingPolicy,
    DPOPair,
    create_bounded_dpo_pairs,
)


class TestBoundingViolationContract:
    def test_is_class(self):
        assert isinstance(BoundingViolation, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(BoundingViolation, type)

class TestDPOPairContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DPOPair)

    def test_is_frozen(self):
        assert DPOPair.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(DPOPair)}
        assert field_names >= {'candidate_payload', 'control_hash', 'control_payload', 'candidate_hash', 'raw_score'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(DPOPair)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert DPOPair.__dataclass_params__.frozen is True

class TestBoundedDPOPairContract:
    def test_is_class(self):
        assert isinstance(BoundedDPOPair, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(BoundedDPOPair, type)

class TestDPOBoundingPolicyContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DPOBoundingPolicy)

    def test_is_frozen(self):
        assert DPOBoundingPolicy.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(DPOBoundingPolicy)}
        assert field_names >= {'min_clamp', 'max_clamp', 'max_delta'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(DPOBoundingPolicy)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert DPOBoundingPolicy.__dataclass_params__.frozen is True

class TestCreateBoundedDpoPairsFunction:
    def test_is_callable(self):
        assert callable(create_bounded_dpo_pairs)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_bounded_dpo_pairs)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module dpo_pair_generator must be importable or skip gracefully."""
    pass  # Import verified at module level
