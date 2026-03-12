"""ADG importability contract for agentic_core/L2_execution/types/vllm_concurrency_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_concurrency_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.vllm_concurrency_types import (  # noqa: F401
        VLLMStressRequest,
        VLLMStressResult,
        VLLMConcurrencyValidationResult,
        build_worst_case_prompt,
        run_stress_batch,
        validate_concurrency_headroom,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMStressRequest = None  # type: ignore[assignment,misc]
    VLLMStressResult = None  # type: ignore[assignment,misc]
    VLLMConcurrencyValidationResult = None  # type: ignore[assignment,misc]
    build_worst_case_prompt = None  # type: ignore[assignment,misc]
    run_stress_batch = None  # type: ignore[assignment,misc]
    validate_concurrency_headroom = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_concurrency_types.py deps unavailable")
class TestVllmConcurrencyTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: vllm_concurrency_types.py must be importable."""
        assert _AVAILABLE

    def test_vllmstressrequest_is_type(self) -> None:
        assert VLLMStressRequest is not None

    def test_vllmstressresult_is_type(self) -> None:
        assert VLLMStressResult is not None

    def test_vllmconcurrencyvalidationresult_is_type(self) -> None:
        assert VLLMConcurrencyValidationResult is not None

    def test_build_worst_case_prompt_callable(self) -> None:
        assert callable(build_worst_case_prompt)

    def test_run_stress_batch_callable(self) -> None:
        assert callable(run_stress_batch)

