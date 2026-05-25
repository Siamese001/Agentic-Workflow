"""Managed wave-based Phase-1 lane dispatcher (vLLM-safe parallelism)."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable

from apps_rg.runtime.orchestration.section_lane_concurrency import LaneWave, build_phase1_waves
from apps_rg.runtime.orchestration.section_lane_executor import (
    LaneDispatchOutcome,
    LaneExecutionContext,
    run_lane_in_context,
)


def dispatch_phase1_lanes_managed(
    lanes_in_order: tuple[str, ...],
    ctx: LaneExecutionContext,
    *,
    dispatch_fn: Callable[..., dict[str, Any]],
    parallel: bool,
    max_parallel: int = 2,
) -> dict[str, LaneDispatchOutcome]:
    """Dispatch lanes in DAG waves; serial fallback is one lane at a time."""
    outcomes: dict[str, LaneDispatchOutcome] = {}

    if not parallel:
        for lane in lanes_in_order:
            outcomes[lane] = run_lane_in_context(ctx, lane, dispatch_fn=dispatch_fn)
        return outcomes

    waves = build_phase1_waves()
    for wave in waves:
        wave_lanes = [ln for ln in wave.lanes if ln in lanes_in_order]
        if not wave_lanes:
            continue
        cap = min(wave.max_parallel, max_parallel, len(wave_lanes))
        if cap <= 1:
            for lane in wave_lanes:
                outcomes[lane] = run_lane_in_context(ctx, lane, dispatch_fn=dispatch_fn)
            continue
        with ThreadPoolExecutor(max_workers=cap) as pool:
            futs = {
                pool.submit(run_lane_in_context, ctx, lane, dispatch_fn=dispatch_fn): lane
                for lane in wave_lanes
            }
            for fut in as_completed(futs):
                lane = futs[fut]
                outcomes[lane] = fut.result()
    for lane in lanes_in_order:
        outcomes.setdefault(
            lane,
            LaneDispatchOutcome(lane=lane, exec_status="skipped", dispatch_result={}),
        )
    return outcomes


__all__ = ["dispatch_phase1_lanes_managed", "LaneWave"]
