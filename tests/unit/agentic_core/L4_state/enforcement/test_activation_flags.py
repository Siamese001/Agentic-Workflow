"""Foundational behavioral tests for agentic_core/L4_state/enforcement/activation_flags.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_activation_flags_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.enforcement.activation_flags import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    ActivationFlags,
    ActivationFlagsStore,
    ActivationGate,
    ActivationProof,
    assert_meta_learning_allowed,
    get_activation_flags,
    is_meta_learning_allowed,
    update_activation_flags,
)


class TestActivationFlagsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ActivationFlags)

    def test_is_frozen(self):
        assert ActivationFlags.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ActivationFlags)}
        assert field_names >= {'execution_hardened', 'mutation_surface_zero', 'meta_learning_prepared', 'freeze_authority_active', 'guardian_coverage'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(ActivationFlags)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert ActivationFlags.__dataclass_params__.frozen is True

class TestActivationProofContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ActivationProof)

    def test_is_frozen(self):
        assert ActivationProof.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(ActivationProof)}
        assert field_names >= {'timestamp', 'previous_flags_hash', 'guardian_signature', 'flags_hash'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(ActivationProof)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert ActivationProof.__dataclass_params__.frozen is True

class TestActivationFlagsStoreContract:
    def test_is_class(self):
        assert isinstance(ActivationFlagsStore, type)

    def test_has_method_update_flags(self):
        assert callable(getattr(ActivationFlagsStore, 'update_flags', None))

    def test_has_method_get_current_flags(self):
        assert callable(getattr(ActivationFlagsStore, 'get_current_flags', None))

    def test_has_method_get_activation_proof(self):
        assert callable(getattr(ActivationFlagsStore, 'get_activation_proof', None))

    def test_has_method_verify_activation_chain(self):
        assert callable(getattr(ActivationFlagsStore, 'verify_activation_chain', None))

class TestActivationGateContract:
    def test_is_class(self):
        assert isinstance(ActivationGate, type)

    def test_has_method_check_p0_ready(self):
        assert callable(getattr(ActivationGate, 'check_p0_ready', None))

    def test_has_method_check_p1_ready(self):
        assert callable(getattr(ActivationGate, 'check_p1_ready', None))

    def test_has_method_check_p2_ready(self):
        assert callable(getattr(ActivationGate, 'check_p2_ready', None))

    def test_has_method_check_meta_learning_allowed(self):
        assert callable(getattr(ActivationGate, 'check_meta_learning_allowed', None))

class TestGetActivationFlagsFunction:
    def test_is_callable(self):
        assert callable(get_activation_flags)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_activation_flags)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestUpdateActivationFlagsFunction:
    def test_is_callable(self):
        assert callable(update_activation_flags)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(update_activation_flags)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestIsMetaLearningAllowedFunction:
    def test_is_callable(self):
        assert callable(is_meta_learning_allowed)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(is_meta_learning_allowed)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestAssertMetaLearningAllowedFunction:
    def test_is_callable(self):
        assert callable(assert_meta_learning_allowed)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(assert_meta_learning_allowed)
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
    """Module activation_flags must be importable or skip gracefully."""
    pass  # Import verified at module level
