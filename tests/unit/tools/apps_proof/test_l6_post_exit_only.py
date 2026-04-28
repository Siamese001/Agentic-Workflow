"""Any L6 span's started_at must be >= runtime_boundary_ts."""

from __future__ import annotations

from pathlib import Path


def test_no_l6_span_before_runtime_boundary(
    run_manifest: dict, otel_trace: list[dict]
) -> None:
    boundary = run_manifest.get("runtime_boundary_ts")
    if not boundary:
        # No boundary recorded means no Exit reached — irrelevant for this test.
        return
    bad = []
    for s in otel_trace:
        if not isinstance(s, dict):
            continue
        if s.get("layer") != "L6":
            continue
        started = s.get("started_at")
        if started and started < boundary:
            bad.append({"span_id": s.get("span_id"), "started_at": started, "boundary": boundary})
    assert not bad, f"L6 spans before runtime boundary: {bad}"
