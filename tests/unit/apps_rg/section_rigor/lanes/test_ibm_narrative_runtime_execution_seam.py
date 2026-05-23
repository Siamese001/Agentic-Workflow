"""W3.1 — IBM narrative runtime/execution seam exposes single spine entry."""

from __future__ import annotations

import inspect


def test_ibm_narrative_single_execution_entry() -> None:
    from apps_rg.runtime.sections import ibm_narrative_lane

    assert hasattr(ibm_narrative_lane, "run_ibm_narrative_lane_execution")
    assert callable(ibm_narrative_lane.run_ibm_narrative_lane_execution)


def test_ibm_narrative_runtime_module_importable() -> None:
    from apps_rg.runtime.sections import ibm_narrative_lane_runtime

    assert inspect.ismodule(ibm_narrative_lane_runtime)
