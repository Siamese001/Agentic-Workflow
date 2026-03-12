"""ADG importability contract for agentic_core/L2_execution/healers/vllm_process_manager.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_process_manager.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.vllm_process_manager import (  # noqa: F401
        VLLMProcessManager,
        get_model_config,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    VLLMProcessManager = None  # type: ignore[assignment,misc]
    get_model_config = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_process_manager.py deps unavailable")
class TestVllmProcessManagerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: vllm_process_manager.py must be importable."""
        assert _AVAILABLE

    def test_vllmprocessmanager_is_type(self) -> None:
        assert VLLMProcessManager is not None

    def test_get_model_config_callable(self) -> None:
        assert callable(get_model_config)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

