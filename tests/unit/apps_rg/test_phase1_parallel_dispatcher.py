"""Phase-1 parallel lane dispatcher (plan f2a8c4)."""
from __future__ import annotations

from collections.abc import Iterator
import os

import pytest

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
from apps_rg.runtime.runtime_proof_layout import MODULAR_R4_SECTIONS_ROOT_ENV


@pytest.fixture(autouse=True)
def _restore_modular_sections_root_env() -> Iterator[None]:
    prior = os.environ.get(MODULAR_R4_SECTIONS_ROOT_ENV)
    try:
        yield
    finally:
        if prior is None:
            os.environ.pop(MODULAR_R4_SECTIONS_ROOT_ENV, None)
        else:
            os.environ[MODULAR_R4_SECTIONS_ROOT_ENV] = prior


def test_build_phase1_waves_wave0_is_upstream_proof_bearing() -> None:
    # Dependency-ordered DAG: wave 0 holds the upstream proof-bearing sections
    # (competencies + bullets); executive_summary is downstream synthesis (later wave).
    waves = build_phase1_waves()
    assert waves
    wave0 = waves[0]
    assert set(wave0.lanes) == {
        "competencies",
        "unify_bullets",
        "ibm_bullets",
        "insurtech_bullets",
        "ey_bullets",
    }
    assert "executive_summary" not in wave0.lanes


def test_build_phase1_waves_exec_summary_is_downstream_solo() -> None:
    waves = build_phase1_waves()
    lane_wave = {lane: w.wave_id for w in waves for lane in w.lanes}
    es_wave = next(w for w in waves if "executive_summary" in w.lanes)
    assert es_wave.lanes == ("executive_summary",)
    assert es_wave.max_parallel == 1
    # exec_summary runs after every upstream proof-bearing + narrative lane.
    for upstream in ("competencies", "unify_bullets", "ibm_bullets", "unify_narrative", "ibm_narrative"):
        assert lane_wave[upstream] < lane_wave["executive_summary"]
    # headline is final positioning, strictly after exec_summary.
    assert lane_wave["executive_summary"] < lane_wave["headline"]


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
    # Narratives are never scheduled in the wave-0 (upstream proof-bearing) bucket.
    wave0_lanes = manifest["waves"][0].get("lanes") or []
    assert "ibm_narrative" not in wave0_lanes
    assert "unify_narrative" not in wave0_lanes


def test_build_phase1_waves_narratives_parallel_after_bullets() -> None:
    # Wave-1 narratives run parallel (max_parallel:4). The 4 narratives are mutually
    # independent — each depends only on its own bullets lane in wave 0 — and
    # run_lane_in_context is lock-free (section_lane_executor.py), so they parallelize
    # safely. This is the PR #325 parallel manifest (1.96x wall-clock: 704s vs 1383s);
    # the 2026-06-14 serial re-pin was a regression and has been reverted.
    waves = build_phase1_waves()
    nar_wave = next(w for w in waves if "unify_narrative" in w.lanes)
    assert set(nar_wave.lanes) == {
        "unify_narrative",
        "ibm_narrative",
        "insurtech_narrative",
        "ey_narrative",
    }
    # narratives parallel (4); throttle via APPS_RG_PHASE1_MAX_PARALLEL if needed.
    assert nar_wave.max_parallel == 4


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
    """A later wave must not run when an earlier wave sets should_skip_remaining_waves (fail-closed parity).

    Lanes are chosen to span two waves under build_phase1_waves(): unify_bullets is in
    wave 0, unify_narrative in wave 1. Aborting on the wave-0 lane must skip the wave-1 lane.
    """
    calls: list[str] = []
    aborted = False

    def _fn(**kwargs: object) -> dict[str, str]:
        lane = str(kwargs.get("section") or "")
        calls.append(lane)
        if lane == "unify_bullets":
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
        ("unify_bullets", "unify_narrative"),
        ctx,
        dispatch_fn=_fn,
        parallel=True,
        max_parallel=2,
        should_skip_remaining_waves=lambda: aborted,
    )
    assert "unify_narrative" not in calls
    assert out["unify_narrative"].exec_status.startswith("pre_run_blocked:")
    assert out["unify_narrative"].dispatch_result.get("prior_abort")
    # A skipped wave never ran, so it must not carry a generic dispatch exit_status:
    # that would let downstream status recompute mislabel it as LANE_DISPATCH_EXIT_ERROR
    # instead of preserving the PHASE1_PRIOR_LANE_FAILED blocker (see PR #251 review).
    assert out["unify_narrative"].dispatch_result.get("exit_status") is None
