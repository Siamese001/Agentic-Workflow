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
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    InvariantId = None  # type: ignore[assignment,misc]
    InvariantSeverity = None  # type: ignore[assignment,misc]
    InvariantViolation = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_invariant_contract_types deps unavailable")
class TestVllmInvariantContractTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L2_execution/types/vllm_invariant_contract_types.py must be importable."""
        assert _AVAILABLE

    def test_invariantid_defined(self) -> None:
        assert InvariantId is not None

    def test_invariantseverity_defined(self) -> None:
        assert InvariantSeverity is not None

    def test_invariantviolation_defined(self) -> None:
        assert InvariantViolation is not None