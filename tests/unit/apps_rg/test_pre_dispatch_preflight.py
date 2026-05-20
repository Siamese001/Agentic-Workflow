"""Unit tests for centralized pre-dispatch preflight."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.pre_dispatch_preflight import (
    evaluate_jd_cli_input,
    evaluate_manual_brief_cli_input,
    run_pre_dispatch_preflight,
    targeting_override_allowed,
)
from apps_rg.runtime.section_cli_defaults import CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM

REPO = Path(__file__).resolve().parents[3]
_FRESH_JD = REPO / "tests" / "_fixtures" / "ci-probe-jd.txt"
_DEFAULT_JD = REPO / "apps_rg" / "config" / "default_jd_targeting.txt"


def test_fresh_jd_fixture_passes() -> None:
    status, _ = evaluate_jd_cli_input(str(_FRESH_JD))
    assert status == "PASS"


def test_default_jd_path_blocked_without_override() -> None:
    status, _ = evaluate_jd_cli_input(str(_DEFAULT_JD))
    assert status == "DEFAULT_BLOCKED"


def test_default_jd_path_allowed_with_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_ALLOW_STALE_TARGETING_SSOT", "1")
    assert targeting_override_allowed()
    status, _ = evaluate_jd_cli_input(str(_DEFAULT_JD))
    assert status == "PASS"


def test_run_preflight_dispatch_false_when_jd_missing() -> None:
    result = run_pre_dispatch_preflight(
        section="competencies",
        jd="",
        manual_brief="Updated briefing for unit test lane validation.",
        lane_provider="qwen_vllm",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
    )
    assert result.dispatch_started is False
    assert result.jd_status == "MISSING"
    assert "targeting" in result.decisive_reason.lower()


def test_stub_skips_qwen_gate() -> None:
    import os

    prev = os.environ.get("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB")
    os.environ["APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"] = "1"
    try:
        result = run_pre_dispatch_preflight(
            section="headline",
            jd=str(_FRESH_JD),
            manual_brief="Lane briefing with non-default digest for pytest unit scope.",
            lane_provider="qwen_vllm",
            provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
        )
        assert result.dispatch_started is True
        assert result.qwen_health_status == "SKIPPED"
        assert result.qwen_model_ready_status == "SKIPPED"
    finally:
        if prev is None:
            os.environ.pop("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", None)
        else:
            os.environ["APPS_RG_QWEN_OFFLINE_CONTRACT_STUB"] = prev
