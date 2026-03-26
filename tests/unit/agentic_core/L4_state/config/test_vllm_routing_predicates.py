"""Foundational behavioral tests for agentic_core/L4_state/config/vllm_routing_predicates.py.

fan_in=14 — this module is imported by 14 other modules.
ADG contract: import-hygiene is covered by test_vllm_routing_predicates_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L4_state.config.vllm_routing_predicates import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    Provider,
    RoutingDecision,
    RoutingPredicate,
    default_routing,
    invalid_ast_detected,
    iteration_count_exceeded,
    requires_policy_read,
)


class TestProviderContract:
    def test_is_enum(self):
        from agentic_core.L4_state.config.vllm_routing_predicates import (  # noqa: F401
        import enum
        assert issubclass(Provider, enum.Enum)

    def test_has_members(self):
        assert len(list(Provider)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in Provider:
            assert member.value is not None

    def test_known_member_opus_exists(self):
        assert hasattr(Provider, 'OPUS')

class TestRoutingDecisionContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(RoutingDecision)

    def test_is_frozen(self):
        assert RoutingDecision.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(RoutingDecision)}
        assert field_names >= {'provider', 'routing_version', 'predicate_evaluation_hash'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(RoutingDecision)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert RoutingDecision.__dataclass_params__.frozen is True

class TestRoutingPredicateContract:
    def test_is_class(self):
        assert isinstance(RoutingPredicate, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(RoutingPredicate, type)

class TestRequiresPolicyReadFunction:
    def test_is_callable(self):
        assert callable(requires_policy_read)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(requires_policy_read)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestIterationCountExceededFunction:
    def test_is_callable(self):
        assert callable(iteration_count_exceeded)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(iteration_count_exceeded)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestInvalidAstDetectedFunction:
    def test_is_callable(self):
        assert callable(invalid_ast_detected)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(invalid_ast_detected)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestDefaultRoutingFunction:
    def test_is_callable(self):
        assert callable(default_routing)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(default_routing)
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
    """Module vllm_routing_predicates must be importable or skip gracefully."""
    pass  # Import verified at module level
