"""W0 unit test for per-lane exception-trace persistence.

When a lane dispatch raises, ``run_lane_in_context`` must capture the traceback
(module + line) into the returned ``dispatch_result`` AND persist
``section_exception_trace.json`` into the lane artifact dir, so a failed integrated
run carries the exact origin instead of only ``str(exc)``
(apps_rg AIG E2E remediation, Wave 0 -- truthful instrumentation).
"""
from __future__ import annotations

import json

from apps_rg.runtime.orchestration.section_lane_executor import (
    LaneExecutionContext,
    run_lane_in_context,
)


def _ctx(sections_root) -> LaneExecutionContext:
    return LaneExecutionContext(
        sections_root=str(sections_root),
        target_company="AIG",
        target_role="VP Global Head of Agentic AI Solutions",
        job_description_ref="",
        job_description_text="",
        manual_brief="",
        lane_provider="external_claude",
        lane_x1d_judges="",
        lane_mock_judges=False,
    )


def test_exception_trace_persisted(tmp_path):
    def boom(**_kwargs):
        raise RuntimeError("kaboom-from-test")

    outcome = run_lane_in_context(_ctx(tmp_path), "ibm_bullets", dispatch_fn=boom)

    # The fault is still surfaced (control flow unchanged) ...
    assert outcome.error and "kaboom-from-test" in outcome.error
    dr = outcome.dispatch_result
    assert dr["fault"] == "exception"
    # ... and now enriched with structured trace fields.
    assert dr["error_type"] == "RuntimeError"
    assert dr["error_module"].endswith(".py")
    assert isinstance(dr["error_lineno"], int) and dr["error_lineno"] > 0
    assert "kaboom-from-test" in dr["traceback"]

    trace_file = tmp_path / "ibm_bullets" / "section_exception_trace.json"
    assert trace_file.is_file()
    payload = json.loads(trace_file.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "section_exception_trace_v1"
    assert payload["lane"] == "ibm_bullets"
    assert payload["error_lineno"] > 0
    assert payload["error_module"].endswith(".py")
    assert "kaboom-from-test" in payload["traceback"]


def test_successful_dispatch_writes_no_trace(tmp_path):
    def ok(**_kwargs):
        return {"exit_status": "ok", "x3_disposition": "X3_ALLOW"}

    outcome = run_lane_in_context(_ctx(tmp_path), "competencies", dispatch_fn=ok)
    assert outcome.exec_status == "ok"
    assert outcome.error is None
    assert not (tmp_path / "competencies" / "section_exception_trace.json").exists()
