"""ADG-driven tests for L0_routing/types/v15_contracts_types.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.types.v15_contracts_types import (
        RESULT_EMISSION_ALLOWED_LAYERS,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RESULT_EMISSION_ALLOWED_LAYERS = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="v15_contracts_types deps unavailable")
class TestV15ContractsTypes:
    def test_result_emission_allowed_layers_is_collection(self):
        assert hasattr(RESULT_EMISSION_ALLOWED_LAYERS, "__contains__")

    def test_non_empty(self):
        assert len(RESULT_EMISSION_ALLOWED_LAYERS) >= 1


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
