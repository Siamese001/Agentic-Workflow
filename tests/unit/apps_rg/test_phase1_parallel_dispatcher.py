"""Phase-1 parallel lane dispatcher (plan f2a8c4)."""
from __future__ import annotations

from apps_rg.runtime.orchestration.managed_section_lane_dispatcher import (
    dispatch_phase1_lanes_managed,
)
from apps_rg.runtime.orchestration.section_lane_concurrency import (
    assert_section_dag_wave_order,
    build_phase1_waves,
    load_section_dag_manifest,
    phase1_parallel_enabled,
)
from apps_rg.runtime.orchestration.section_lane_executor import LaneExecutionContext


def test_build_phase1_waves_includes_exec_solo_wave() -> None:
    waves = build_phase1_waves()
    assert waves
    wave0 = waves[0]
    assert "executive_summary" in wave0.lanes


def test_section_dag_narrative_never_precedes_companion_bullets() -> None:
    """Plan f2a8c4: unify_narrative / ibm_narrative must schedule after bullets lanes."""
    manifest = load_section_dag_manifest()
    assert_section_dag_wave_order(manifest)

    lane_wave: dict[str, int] = {}
    for wave in manifest.get("waves") or []:
        wid = int(wave["id"])
        for lane in wave.get("lanes") or []:
            lane_wave[str(lane)] = wid

    assert lane_wave["unify_narrative"] > lane_wave["unify_bullets"]
    assert lane_wave["ibm_narrative"] > lane_wave["ibm_bullets"]
    assert "ibm_narrative" not in (manifest["waves"][1].get("lanes") or [])


def test_build_phase1_waves_wave2_serial_narratives() -> None:
    waves = build_phase1_waves()
    wave2 = next(w for w in waves if w.wave_id == 2)
    assert wave2.lanes == ("unify_narrative", "ibm_narrative")
    assert wave2.max_parallel == 1


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


def test_parallel_dispatch_skips_later_waves_after_abort() -> None:
    """Wave 2 must not run when wave 1 sets should_skip_remaining_waves (fail-closed parity)."""
    calls: list[str] = []
    aborted = False

    def _fn(**kwargs: object) -> dict[str, str]:
        lane = str(kwargs.get("section") or "")
        calls.append(lane)
        if lane == "headline":
            nonlocal aborted
            aborted = True
            return {"section": lane, "exit_status": "error", "fault": "dispatch_failed"}
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
    out = dispatch_phase1_lanes_managed(
        ("executive_summary", "headline", "unify_narrative"),
        ctx,
        dispatch_fn=_fn,
        parallel=True,
        max_parallel=2,
        should_skip_remaining_waves=lambda: aborted,
    )
    assert "unify_narrative" not in calls
    assert out["unify_narrative"].exec_status.startswith("pre_run_blocked:")
    assert out["unify_narrative"].dispatch_result.get("prior_abort")
