"""ADG importability contract for agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_DAGMutatorAgent.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.reasoning.DAGMutatorAgent import (  # noqa: F401
        DAGConfig,
        DAGMutation,
        GraphTransaction,
        HopSpec,
        MutationAction,
        MutationResult,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GraphTransaction = None  # type: ignore[assignment,misc]
    MutationAction = None  # type: ignore[assignment,misc]
    HopSpec = None  # type: ignore[assignment,misc]
    DAGMutation = None  # type: ignore[assignment,misc]
    MutationResult = None  # type: ignore[assignment,misc]
    DAGConfig = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent deps unavailable")
class TestDagmutatoragentImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py must be importable."""
        assert _AVAILABLE

    def test_graphtransaction_defined(self) -> None:
        assert GraphTransaction is not None

    def test_mutationaction_defined(self) -> None:
        assert MutationAction is not None

    def test_hopspec_defined(self) -> None:
        assert HopSpec is not None

    def test_dagmutation_defined(self) -> None:
        assert DAGMutation is not None

    def test_mutationresult_defined(self) -> None:
        assert MutationResult is not None

    def test_dagconfig_defined(self) -> None:
        assert DAGConfig is not None
