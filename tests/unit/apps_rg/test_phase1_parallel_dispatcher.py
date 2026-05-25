"""Phase-1 parallel lane dispatcher (plan f2a8c4)."""
from __future__ import annotations

import pytest

from apps_rg.runtime.orchestration.managed_section_lane_dispatcher import (
    dispatch_phase1_lanes_managed,
)
from apps_rg.runtime.orchestration.section_lane_concurrency import (
    build_phase1_waves,
    phase1_parallel_enabled,
)
from apps_rg.runtime.orchestration.section_lane_executor import LaneExecutionContext


@pytest.fixture(autouse=True)
def _stable_lane_temperature(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "apps_rg.runtime.orchestration.section_lane_executor.default_temperature_for_section",
        lambda _lane: 0.4,
    )


def test_build_phase1_waves_includes_exec_solo_wave() -> None:
    waves = build_phase1_waves()
    assert waves
    wave0 = waves[0]
    assert "executive_summary" in wave0.lanes


def test_dispatch_serial_mock() -> None:
    calls: list[str] = []

    def _fn(**kwargs: object) -> dict[str, str]:
        lane = str(kwargs.get("section") or "")
        calls.append(lane)
        return {"section": lane, "exit_status": "ok"}

    ctx = LaneExecutionContext(
        sections_root="/tmp/sections",
        target_company="Acme",
        target_role="VP",
        job_description_ref="",
        job_description_text="",
        manual_brief="",
        lane_provider="mock",
        lane_x1d_judges=(),
        lane_mock_judges=True,
    )
    lanes = ("headline", "competencies")
    out = dispatch_phase1_lanes_managed(
        lanes,
        ctx,
        dispatch_fn=_fn,
        parallel=False,
    )
    assert set(out) == set(lanes)
    assert calls == ["headline", "competencies"]


def test_phase1_parallel_env_default_off(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_PARALLEL_PHASE1_LANES", raising=False)
    assert phase1_parallel_enabled(profile_flag=False) is False
    monkeypatch.setenv("APPS_RG_PARALLEL_PHASE1_LANES", "1")
    assert phase1_parallel_enabled(profile_flag=False) is True


def test_resolve_max_parallel_clamps(monkeypatch) -> None:
    from apps_rg.runtime.orchestration.section_lane_concurrency import resolve_max_parallel

    monkeypatch.setenv("APPS_RG_PHASE1_MAX_PARALLEL", "99")
    assert resolve_max_parallel(default=2) == 7
    monkeypatch.setenv("APPS_RG_PHASE1_MAX_PARALLEL", "0")
    assert resolve_max_parallel(default=2) == 1
    monkeypatch.delenv("APPS_RG_PHASE1_MAX_PARALLEL", raising=False)
    assert resolve_max_parallel(default=4) == 4


def test_dispatch_parallel_invokes_all_lanes_in_wave() -> None:
    import threading

    calls: list[str] = []
    lock = threading.Lock()

    def _fn(**kwargs: object) -> dict[str, str]:
        lane = str(kwargs.get("section") or "")
        with lock:
            calls.append(lane)
        return {"section": lane, "exit_status": "ok"}

    ctx = LaneExecutionContext(
        sections_root="/tmp/sections",
        target_company="Acme",
        target_role="VP",
        job_description_ref="",
        job_description_text="",
        manual_brief="",
        lane_provider="mock",
        lane_x1d_judges=(),
        lane_mock_judges=True,
    )
    lanes = ("headline", "unify_bullets")
    out = dispatch_phase1_lanes_managed(
        lanes,
        ctx,
        dispatch_fn=_fn,
        parallel=True,
        max_parallel=2,
    )
    assert set(out) == set(lanes)
    assert set(calls) == set(lanes)
