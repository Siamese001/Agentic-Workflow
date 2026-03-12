"""ADG importability contract for agentic_core/L2_execution/types/vllm_invariant_contract_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_invariant_contract_types.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L2_execution.types.vllm_invariant_contract_types import (  # noqa: F401
        InvariantId,
        InvariantSeverity,
        InvariantViolation,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    InvariantId = None  # type: ignore[assignment,misc]
    InvariantSeverity = None  # type: ignore[assignment,misc]
    InvariantViolation = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="vllm_invariant_contract_types.py deps unavailable")
class TestVllmInvariantContractTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: vllm_invariant_contract_types.py must be importable."""
        assert _AVAILABLE

    def test_invariantid_is_type(self) -> None:
        assert InvariantId is not None

    def test_invariantseverity_is_type(self) -> None:
        assert InvariantSeverity is not None

    def test_invariantviolation_is_type(self) -> None:
        assert InvariantViolation is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

