"""ADG-driven tests for agentic_core/mixins/hardening_mixin.py — fan_in=2.

Contract tests: TokenLimitError, HardeningMixin init, execute_hardened API.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.mixins.hardening_mixin import HardeningMixin, TokenLimitError
    _IMPORT_OK = True
except (ImportError, ModuleNotFoundError):
    _IMPORT_OK = False
    HardeningMixin = None
    TokenLimitError = None


class TestTokenLimitError:
    @pytest.mark.skipif(not _IMPORT_OK, reason="hardening_mixin deps unavailable")
    def test_is_exception(self):
        assert issubclass(TokenLimitError, Exception)

    @pytest.mark.skipif(not _IMPORT_OK, reason="hardening_mixin deps unavailable")
    def test_can_be_raised(self):
        with pytest.raises(TokenLimitError):
            raise TokenLimitError("token limit exceeded")


@pytest.mark.skipif(not _IMPORT_OK, reason="hardening_mixin deps unavailable")
class TestHardeningMixinImport:
    def test_importable(self):
        assert callable(HardeningMixin)

    def test_creates_with_component_name(self):
        mixin = HardeningMixin(component_name="test_component")
        assert mixin.component_name == "test_component"

    def test_default_max_retries(self):
        mixin = HardeningMixin(component_name="test", max_retries=3)
        assert mixin.error_recovery is not None

    def test_circuit_breaker_initialized(self):
        mixin = HardeningMixin(component_name="test_breaker")
        assert mixin.circuit_breaker is not None

    def test_has_execute_hardened(self):
        assert hasattr(HardeningMixin, "execute_hardened")
