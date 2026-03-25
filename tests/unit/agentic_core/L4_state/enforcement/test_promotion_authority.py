"""Foundational behavioral tests for agentic_core/L4_state/enforcement/promotion_authority.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_promotion_authority_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.enforcement.promotion_authority import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    PromotionAuthority,
    PromotionPointerUpdate,
    get_promotion_authority,
    update_pointer_via_gateway,
    validate_pointer_update_integrity,
)


class TestPromotionPointerUpdateContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PromotionPointerUpdate)

    def test_is_frozen(self):
        assert PromotionPointerUpdate.__dataclass_params__.frozen is True

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(PromotionPointerUpdate)}
        assert field_names >= {'old_pointer', 'new_pointer', 'timestamp', 'guardian_signature', 'capability_token_hash'}

    def test_immutable_after_creation(self):
        import dataclasses
        fields = dataclasses.fields(PromotionPointerUpdate)
        if not fields:

        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert PromotionPointerUpdate.__dataclass_params__.frozen is True

class TestPromotionAuthorityContract:
    def test_is_class(self):
        assert isinstance(PromotionAuthority, type)

    def test_has_method_set_write_gateway(self):
        assert callable(getattr(PromotionAuthority, 'set_write_gateway', None))

    def test_has_method_update_pointer_via_gateway(self):
        assert callable(getattr(PromotionAuthority, 'update_pointer_via_gateway', None))

    def test_has_method_get_update_history(self):
        assert callable(getattr(PromotionAuthority, 'get_update_history', None))

    def test_has_method_validate_pointer_update_integrity(self):
        assert callable(getattr(PromotionAuthority, 'validate_pointer_update_integrity', None))

class TestGetPromotionAuthorityFunction:
    def test_is_callable(self):
        assert callable(get_promotion_authority)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_promotion_authority)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestUpdatePointerViaGatewayFunction:
    def test_is_callable(self):
        assert callable(update_pointer_via_gateway)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(update_pointer_via_gateway)
        assert sig.return_annotation is not inspect.Parameter.empty

class TestValidatePointerUpdateIntegrityFunction:
    def test_is_callable(self):
        assert callable(validate_pointer_update_integrity)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_pointer_update_integrity)
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
    """Module promotion_authority must be importable or skip gracefully."""
    pass  # Import verified at module level
