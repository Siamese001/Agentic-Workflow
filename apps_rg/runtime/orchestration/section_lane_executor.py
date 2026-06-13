"""Isolated Phase-1 lane execution context (serial + parallel dispatcher)."""
from __future__ import annotations

import json
import os
import traceback as _tb
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from apps_rg.runtime.runtime_proof_layout import MODULAR_R4_SECTIONS_ROOT_ENV
from apps_rg.runtime.section_cli_defaults import CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE
from apps_rg.runtime.section_lane_temperature import default_temperature_for_section

# 2026-06-13: removed `_ENV_OVERLAY_LOCK` (a process-global lock formerly held across
# the ENTIRE lane dispatch as a "vLLM-safe throttle"). It serialized all wave lanes
# despite parallel=True/cap=N (measured: 23-min fully-serial baseline). Since
# MODULAR_R4_SECTIONS_ROOT is a run-level CONSTANT, run_lane_in_context now sets it
# idempotently and lock-free — true wave parallelism, validated at 704s vs 1383s
# (1.96x) with identical per-lane X3 outcomes. See memory
# apps-rg-parallel-orchestration-nonfunctional.


@dataclass
class LaneExecutionContext:
    """Per-lane env isolation for in-process Phase-1 dispatch."""

    sections_root: str
    target_company: str
    target_role: str
    job_description_ref: str
    job_description_text: str
    manual_brief: str
    lane_provider: str
    # str (same judges for every lane) OR Callable[[lane_id], str] for per-lane composite-judge
    # defaults (competencies -> gemini_pro, ibm_bullets -> anthropic_claude, else panel).
    lane_x1d_judges: Any
    lane_mock_judges: bool
    lane_allow_non_allow_exit_zero: bool = False
    generation_mode: str = "strategic_tailor"

    def env_overlay(self) -> dict[str, str | None]:
        return {MODULAR_R4_SECTIONS_ROOT_ENV: self.sections_root}

    def x1d_judges_for_lane(self, lane: str) -> Any:
        """Resolve the X1D judge CSV for ``lane`` (honors a per-lane callable)."""
        judges = self.lane_x1d_judges
        if callable(judges):
            return judges(lane)
        return judges


@dataclass
class LaneDispatchOutcome:
    lane: str
    dispatch_result: dict[str, Any] = field(default_factory=dict)
    exec_status: str = ""
    error: str | None = None


def _persist_exception_trace(
    ctx: LaneExecutionContext, lane: str, exc: BaseException
) -> dict[str, Any]:
    """Capture a failed lane dispatch traceback and best-effort persist it.

    Returns the structured trace fields (merged into the ``dispatch_result``) and writes
    ``section_exception_trace.json`` into the lane artifact dir, so a failed integrated
    run carries the exact module/line instead of only ``str(exc)``
    (apps_rg AIG E2E remediation, Wave 0 -- truthful instrumentation for E2E-05/E2E-11).
    """
    tb_str = "".join(_tb.format_exception(type(exc), exc, exc.__traceback__))
    frames = _tb.extract_tb(exc.__traceback__)
    last = frames[-1] if frames else None
    fields: dict[str, Any] = {
        "error_type": type(exc).__name__,
        "error_module": (last.filename if last else ""),
        "error_lineno": (last.lineno if last else 0),
        "traceback": tb_str,
    }
    payload = {
        "schema_version": "section_exception_trace_v1",
        "lane": lane,
        "error": str(exc),
        **fields,
    }
    try:
        lane_dir = Path(ctx.sections_root) / lane
        lane_dir.mkdir(parents=True, exist_ok=True)
        (lane_dir / "section_exception_trace.json").write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )
    except OSError:
        # Best-effort: trace persistence must never mask the original lane fault.
        pass
    return fields


def run_lane_in_context(
    ctx: LaneExecutionContext,
    lane: str,
    *,
    dispatch_fn: Callable[..., dict[str, Any]],
) -> LaneDispatchOutcome:
    """Run one lane dispatch with the run-constant MODULAR_R4_SECTIONS_ROOT.

    ``sections_root`` is identical for every lane in a run (see ``env_overlay`` — it
    sets only that one constant key). Set it idempotently and **lock-free** so lanes
    can execute concurrently. The prior implementation wrapped the ENTIRE lane (C0 +
    generation + X1D judges + X3) in ``_ENV_OVERLAY_LOCK`` and save/restored the env
    per-lane, which forced strict-serial execution despite ``parallel=True``/``cap=N``
    (measured: 23-min fully-serial baseline) AND was racy — one lane's per-lane restore
    could unset the root while a concurrent lane was still running. Because the value is
    a run-level constant, a lock-free idempotent set is correct; no per-lane restore is
    needed (the constant must persist for the run's lifetime). See memory
    ``apps-rg-parallel-orchestration-nonfunctional``.
    """
    for k, v in ctx.env_overlay().items():
        if v is not None and os.environ.get(k) != v:
            os.environ[k] = v
    try:
        result = dispatch_fn(
            target_company=ctx.target_company,
            target_role=ctx.target_role,
            jd="",
            job_description_ref=ctx.job_description_ref,
            job_description_text=ctx.job_description_text,
            manual_brief=ctx.manual_brief,
            resume_path="",
            source_resume_text="",
            generation_mode=ctx.generation_mode,
            artifact_dir="",
            section=lane,
            lane_provider=ctx.lane_provider,
            lane_provider_resolution_source=CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE,
            lane_temperature=default_temperature_for_section(lane),
            lane_x1d_judges=ctx.x1d_judges_for_lane(lane),
            lane_mock_judges=ctx.lane_mock_judges,
            lane_allow_non_allow_exit_zero=bool(ctx.lane_allow_non_allow_exit_zero),
        )
        dr = dict(result) if isinstance(result, dict) else {}
        return LaneDispatchOutcome(lane=lane, dispatch_result=dr, exec_status="ok")
    except Exception as exc:  # guardian: allow-broad-exception -- phase1 fail-soft boundary
        trace_fields = _persist_exception_trace(ctx, lane, exc)
        return LaneDispatchOutcome(
            lane=lane,
            dispatch_result={"fault": "exception", "error": str(exc), **trace_fields},
            exec_status=f"error:{exc!s}",
            error=str(exc),
        )


__all__ = ["LaneExecutionContext", "LaneDispatchOutcome", "run_lane_in_context"]
