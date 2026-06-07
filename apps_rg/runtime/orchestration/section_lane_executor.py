"""Isolated Phase-1 lane execution context (serial + parallel dispatcher)."""
from __future__ import annotations

import os
import threading
from dataclasses import dataclass, field
from typing import Any, Callable

from apps_rg.runtime.runtime_proof_layout import MODULAR_R4_SECTIONS_ROOT_ENV
from apps_rg.runtime.section_cli_defaults import CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE
from apps_rg.runtime.section_lane_temperature import default_temperature_for_section

# Held across the entire lane dispatch (not just the os.environ mutation) so the
# process-global MODULAR_R4_SECTIONS_ROOT overlay cannot be swapped out from under
# an in-flight lane. This intentionally serializes concurrent wave lanes -- a
# deliberate vLLM-safe throttle, not merely env protection. If true wave
# parallelism is wanted later, set the (constant) sections_root once before the
# wave and drop the per-lane overlay rather than widening this lock.
_ENV_OVERLAY_LOCK = threading.Lock()


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


def run_lane_in_context(
    ctx: LaneExecutionContext,
    lane: str,
    *,
    dispatch_fn: Callable[..., dict[str, Any]],
) -> LaneDispatchOutcome:
    """Run one lane dispatch with scoped MODULAR_R4_SECTIONS_ROOT."""
    with _ENV_OVERLAY_LOCK:
        saved = {k: os.environ.get(k) for k in ctx.env_overlay()}
        try:
            for k, v in ctx.env_overlay().items():
                if v is not None:
                    os.environ[k] = v
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
            return LaneDispatchOutcome(
                lane=lane,
                dispatch_result={"fault": "exception", "error": str(exc)},
                exec_status=f"error:{exc!s}",
                error=str(exc),
            )
        finally:
            for k, prev in saved.items():
                if prev is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = prev


__all__ = ["LaneExecutionContext", "LaneDispatchOutcome", "run_lane_in_context"]
