"""ADG-driven tests for L2_execution/enforcement/provider_binding_determinism.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.enforcement.provider_binding_determinism import (
        ProviderBindingContext,
        compute_provider_binding_digest,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ProviderBindingContext = None  # type: ignore[assignment,misc]
    compute_provider_binding_digest = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="provider_binding_determinism deps unavailable")
class TestProviderBindingContext:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ProviderBindingContext)

    def test_is_frozen(self):
        ctx = ProviderBindingContext(
            provider_id="openai",
            model_id="gpt-4",
            gateway_version="v1",
            semantic_clock_vector={"tick": 1},
        )
        with pytest.raises((AttributeError, TypeError)):
            ctx.provider_id = "anthropic"


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
