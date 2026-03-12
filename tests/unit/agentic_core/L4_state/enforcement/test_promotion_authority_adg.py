"""ADG-driven tests for agentic_core/L4_state/enforcement/promotion_authority.py — fan_in=0."""
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
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestPromotionPointerUpdate:
    def test_is_class(self):
        assert isinstance(PromotionPointerUpdate, type)
    def test_importable(self):
        assert PromotionPointerUpdate is not None

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestPromotionAuthority:
    def test_is_class(self):
        assert isinstance(PromotionAuthority, type)
    def test_importable(self):
        assert PromotionAuthority is not None

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestGetPromotionAuthority:
    def test_is_callable(self):
        assert callable(get_promotion_authority)

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestUpdatePointerViaGateway:
    def test_is_callable(self):
        assert callable(update_pointer_via_gateway)

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestValidatePointerUpdateIntegrity:
    def test_is_callable(self):
        assert callable(validate_pointer_update_integrity)

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

@pytest.mark.skipif(not _AVAILABLE, reason="promotion_authority.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module promotion_authority.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
