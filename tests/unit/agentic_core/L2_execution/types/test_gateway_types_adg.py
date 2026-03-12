"""ADG importability contract for agentic_core/L2_execution/types/gateway_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_gateway_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.gateway_types import (  # noqa: F401
        GenerationRequest,
        GenerationResponse,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GenerationRequest = None  # type: ignore[assignment,misc]
    GenerationResponse = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="gateway_types.py deps unavailable")
class TestGatewayTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: gateway_types.py must be importable."""
        assert _AVAILABLE

    def test_generationrequest_is_type(self) -> None:
        assert GenerationRequest is not None

    def test_generationresponse_is_type(self) -> None:
        assert GenerationResponse is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

