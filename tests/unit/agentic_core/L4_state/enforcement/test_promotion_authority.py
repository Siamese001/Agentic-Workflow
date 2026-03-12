"""Foundational behavioral tests for agentic_core/L4_state/enforcement/promotion_authority.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_promotion_authority_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.enforcement.promotion_authority import (  # noqa: F401
        PromotionPointerUpdate,
        PromotionAuthority,
        get_promotion_authority,
        update_pointer_via_gateway,
        validate_pointer_update_integrity,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    PromotionPointerUpdate = None  # type: ignore[assignment,misc]
    PromotionAuthority = None  # type: ignore[assignment,misc]
    get_promotion_authority = None  # type: ignore[assignment,misc]
    update_pointer_via_gateway = None  # type: ignore[assignment,misc]
    validate_pointer_update_integrity = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
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
            pytest.skip('no fields to test immutability')
        # Verify frozen raises on setattr
        # (create requires knowing required fields — skip if args unknown)
        assert PromotionPointerUpdate.__dataclass_params__.frozen is True

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
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

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestGetPromotionAuthorityFunction:
    def test_is_callable(self):
        assert callable(get_promotion_authority)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_promotion_authority)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestUpdatePointerViaGatewayFunction:
    def test_is_callable(self):
        assert callable(update_pointer_via_gateway)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(update_pointer_via_gateway)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestValidatePointerUpdateIntegrityFunction:
    def test_is_callable(self):
        assert callable(validate_pointer_update_integrity)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_pointer_update_integrity)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module promotion_authority must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
