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
from apps_rg.runtime.product_output_policy import PHASE1_PRIOR_LANE_FAILED_BLOCKER
from tools.progress_display import ProgressReporter

_WAVE_ABORT_EXEC_STATUS = f"pre_run_blocked:{PHASE1_PRIOR_LANE_FAILED_BLOCKER}"


def _skipped_prior_lane_abort(lane: str) -> LaneDispatchOutcome:
    # Skipped wave after a prior-lane fail-closed abort. The lane never ran, so it
    # carries no real dispatch exit_status -- the blocker lives in exec_status
    # (pre_run_blocked:...) and dispatch_result["prior_abort"]. Emitting a generic
    # exit_status="error" here would let downstream status recompute mislabel the
    # skip as LANE_DISPATCH_EXIT_ERROR instead of PHASE1_PRIOR_LANE_FAILED.
    return LaneDispatchOutcome(
        lane=lane,
        dispatch_result={"prior_abort": PHASE1_PRIOR_LANE_FAILED_BLOCKER},
        exec_status=_WAVE_ABORT_EXEC_STATUS,
    )


def dispatch_phase1_lanes_managed(
    lanes_in_order: tuple[str, ...],
    ctx: LaneExecutionContext,
    *,
    dispatch_fn: Callable[..., dict[str, Any]],
    parallel: bool,
    max_parallel: int = 2,
    should_skip_remaining_waves: Callable[[], bool] | None = None,
) -> dict[str, LaneDispatchOutcome]:
    """Dispatch lanes in DAG waves; serial fallback is one lane at a time."""
    outcomes: dict[str, LaneDispatchOutcome] = {}

    # §16 query-progress (constitutional): a Phase-1 dispatch runs N section lanes, each an
    # ~1-2 min LLM generation, so the loop is a multi-minute operation that MUST surface a
    # progress bar — the static check_query_progress_bar gate misses it because the loop body
    # is short and the function is not a scan_/query_-prefixed "heavy" name. The bar ticks on
    # lane COMPLETION from the MAIN thread only (the serial loops + the parallel as_completed
    # loop), never from a worker thread, so it is concurrency-safe under ThreadPoolExecutor.
    reporter = ProgressReporter(
        total=max(len(lanes_in_order), 1), label="apps_rg section lanes", unit="lane"
    )

    def _record(lane: str, outcome: LaneDispatchOutcome) -> None:
        outcomes[lane] = outcome
        reporter.update(label=f"{lane} [{str(getattr(outcome, 'exec_status', '') or 'done')}]")

    if not parallel:
        for lane in lanes_in_order:
            if should_skip_remaining_waves and should_skip_remaining_waves():
                _record(lane, _skipped_prior_lane_abort(lane))
                continue
            _record(lane, run_lane_in_context(ctx, lane, dispatch_fn=dispatch_fn))
        reporter.done()
        return outcomes

    waves = build_phase1_waves()
    for wave in waves:
        wave_lanes = [ln for ln in wave.lanes if ln in lanes_in_order]
        if not wave_lanes:
            continue
        if should_skip_remaining_waves and should_skip_remaining_waves():
            for lane in wave_lanes:
                _record(lane, _skipped_prior_lane_abort(lane))
            continue
        cap = min(wave.max_parallel, max_parallel, len(wave_lanes))
        if cap <= 1:
            for lane in wave_lanes:
                if should_skip_remaining_waves and should_skip_remaining_waves():
                    _record(lane, _skipped_prior_lane_abort(lane))
                    continue
                _record(lane, run_lane_in_context(ctx, lane, dispatch_fn=dispatch_fn))
            continue
        with ThreadPoolExecutor(max_workers=cap) as pool:
            futs = {
                pool.submit(run_lane_in_context, ctx, lane, dispatch_fn=dispatch_fn): lane
                for lane in wave_lanes
            }
            for fut in as_completed(futs):
                lane = futs[fut]
                _record(lane, fut.result())
    for lane in lanes_in_order:
        if lane not in outcomes:
            _record(
                lane,
                LaneDispatchOutcome(lane=lane, exec_status="skipped", dispatch_result={}),
            )
    reporter.done()
    return outcomes


__all__ = ["dispatch_phase1_lanes_managed", "LaneWave"]
