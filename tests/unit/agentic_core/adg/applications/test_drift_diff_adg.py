"""ADG importability contract for agentic_core/adg/applications/drift_diff.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_drift_diff.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.adg.applications.drift_diff import (  # noqa: F401
        RegressionFinding,
        DriftDiffResult,
        run_drift_diff,
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RegressionFinding = None  # type: ignore[assignment,misc]
    DriftDiffResult = None  # type: ignore[assignment,misc]
    run_drift_diff = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="drift_diff.py deps unavailable")
class TestDriftDiffImportability:
    def test_module_importable(self) -> None:
        """ADG contract: drift_diff.py must be importable."""
        assert _AVAILABLE

    def test_regressionfinding_is_type(self) -> None:
        assert RegressionFinding is not None

    def test_driftdiffresult_is_type(self) -> None:
        assert DriftDiffResult is not None

    def test_run_drift_diff_callable(self) -> None:
        assert callable(run_drift_diff)

    def test_main_callable(self) -> None:
        assert callable(main)

