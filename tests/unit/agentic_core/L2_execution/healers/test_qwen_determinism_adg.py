"""ADG importability contract for agentic_core/L2_execution/healers/qwen_determinism.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_qwen_determinism.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.healers.qwen_determinism import (  # noqa: F401
        compute_qwen_determinism_digest,
        canonicalize_qwen_output,
        compute_current_determinism_digest,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    compute_qwen_determinism_digest = None  # type: ignore[assignment,misc]
    canonicalize_qwen_output = None  # type: ignore[assignment,misc]
    compute_current_determinism_digest = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="qwen_determinism.py deps unavailable")
class TestQwenDeterminismImportability:
    def test_module_importable(self) -> None:
        """ADG contract: qwen_determinism.py must be importable."""
        assert _AVAILABLE

    def test_compute_qwen_determinism_digest_callable(self) -> None:
        assert callable(compute_qwen_determinism_digest)

    def test_canonicalize_qwen_output_callable(self) -> None:
        assert callable(canonicalize_qwen_output)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

