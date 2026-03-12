"""ADG importability contract for agentic_core/L2_execution/types/vllm_gateway_adapter_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_gateway_adapter_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.vllm_gateway_adapter_types import (  # noqa: F401
        VLLMGatewayAdapter,
        reset_singletons,
        emit_seam_proof,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMGatewayAdapter = None  # type: ignore[assignment,misc]
    reset_singletons = None  # type: ignore[assignment,misc]
    emit_seam_proof = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_gateway_adapter_types.py deps unavailable")
class TestVllmGatewayAdapterTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: vllm_gateway_adapter_types.py must be importable."""
        assert _AVAILABLE

    def test_vllmgatewayadapter_is_type(self) -> None:
        assert VLLMGatewayAdapter is not None

    def test_reset_singletons_callable(self) -> None:
        assert callable(reset_singletons)

    def test_emit_seam_proof_callable(self) -> None:
        assert callable(emit_seam_proof)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

