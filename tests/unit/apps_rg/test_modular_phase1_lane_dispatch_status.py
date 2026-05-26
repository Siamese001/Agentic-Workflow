"""Edge cases for phase-1 lane dispatch status summarization."""

from __future__ import annotations

from apps_rg.l2_recipe.modular_resume_generation import _phase1_lane_dispatch_status


def test_phase1_lane_dispatch_status_ok_on_success() -> None:
    assert _phase1_lane_dispatch_status({"exit_status": "success", "fault": ""}) == "ok"


def test_phase1_lane_dispatch_status_lane_exit_error() -> None:
    assert (
        _phase1_lane_dispatch_status({"exit_status": "error", "fault": ""})
        == "dispatch_error:lane_exit_error"
    )


def test_phase1_lane_dispatch_status_temperature_fault() -> None:
    assert (
        _phase1_lane_dispatch_status({"exit_status": "error", "fault": "temperature_range"})
        == "exit_2"
    )


def test_phase1_lane_dispatch_status_named_fault() -> None:
    assert (
        _phase1_lane_dispatch_status({"exit_status": "success", "fault": "provider_timeout"})
        == "dispatch_error:provider_timeout"
    )


def test_phase1_lane_dispatch_status_empty_result() -> None:
    assert _phase1_lane_dispatch_status(None) == "dispatch_status:unknown"
    assert _phase1_lane_dispatch_status({}) == "dispatch_status:unknown"
