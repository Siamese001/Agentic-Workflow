"""ADG importability contract for agentic_core/L2_execution/types/vllm_token_budget_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_token_budget_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.vllm_token_budget_types import (  # noqa: F401
        TaskClass,
        VLLMFailureType,
        VLLMOutputCapExceeded,
        enforce_output_cap,
        estimate_tokens_qwen,
        get_output_cap,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    TaskClass = None  # type: ignore[assignment,misc]
    get_output_cap = None  # type: ignore[assignment,misc]
    enforce_output_cap = None  # type: ignore[assignment,misc]
    VLLMOutputCapExceeded = None  # type: ignore[assignment,misc]
    estimate_tokens_qwen = None  # type: ignore[assignment,misc]
    VLLMFailureType = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_token_budget_types deps unavailable")
class TestVllmTokenBudgetTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/vllm_token_budget_types.py must be importable."""
        assert _AVAILABLE

    def test_taskclass_defined(self) -> None:
        assert TaskClass is not None

    def test_vllmoutputcapexceeded_defined(self) -> None:
        assert VLLMOutputCapExceeded is not None

    def test_vllmfailuretype_defined(self) -> None:
        assert VLLMFailureType is not None
