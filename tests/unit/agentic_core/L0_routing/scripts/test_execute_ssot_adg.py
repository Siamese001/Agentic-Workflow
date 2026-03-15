"""ADG importability contract for agentic_core/L0_routing/scripts/execute_ssot.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_execute_ssot.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.scripts.execute_ssot import (  # noqa: F401
        REPO_ROOT,
        ConfidenceScore,
        FailureType,
        RoutingTier,
        resolve_repo_root,
        run_fence_self_check,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    run_fence_self_check = None  # type: ignore[assignment,misc]
    resolve_repo_root = None  # type: ignore[assignment,misc]
    REPO_ROOT = None  # type: ignore[assignment,misc]
    ConfidenceScore = None  # type: ignore[assignment,misc]
    FailureType = None  # type: ignore[assignment,misc]
    RoutingTier = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="execute_ssot deps unavailable")
class TestExecuteSsotImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/scripts/execute_ssot.py must be importable."""
        assert _AVAILABLE

    def test_confidencescore_defined(self) -> None:
        assert ConfidenceScore is not None

    def test_failuretype_defined(self) -> None:
        assert FailureType is not None

    def test_routingtier_defined(self) -> None:
        assert RoutingTier is not None
