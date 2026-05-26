"""Contract: mandatory pre-dispatch fail-closed gates for all ``python -m apps_rg --section`` lanes."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from apps_rg.runtime.pre_dispatch_preflight import (
    enforce_pre_dispatch_preflight,
    evaluate_jd_cli_input,
    evaluate_manual_brief_cli_input,
    evaluate_qwen_readiness,
    run_pre_dispatch_preflight,
)
from apps_rg.runtime.section_cli_defaults import (
    CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
    SectionCliConfigError,
)

REPO = Path(__file__).resolve().parents[2]
_FRESH_JD = REPO / "tests" / "_fixtures" / "ci-probe-jd.txt"
_FRESH_BRIEF = REPO / "tests" / "_fixtures" / "ci-probe-briefing.txt"
_DEFAULT_JD = REPO / "apps_rg" / "config" / "default_jd_targeting.txt"
_DEFAULT_BRIEF = REPO / "apps_rg" / "config" / "default_targeting_briefing.txt"

_STRIP_KEYS = frozenset(
    {
        "APPS_RG_MODULAR_LANE_PROVIDER",
        "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "APPS_RG_SKIP_QWEN_VLLM_HEALTH",
        "APPS_RG_ALLOW_STALE_TARGETING_SSOT",
        "APPS_RG_ALLOW_DEFAULT_TARGETING_PATHS",
        "VLLM_BASE_URL",
    }
)


def _subprocess_env(**extra: str) -> dict[str, str]:
    import os

    env = {k: v for k, v in os.environ.items() if k not in _STRIP_KEYS}
    env.update(extra)
    return env


def _run_cli(argv_tail: list[str], *, env_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = _subprocess_env(**(env_extra or {}))
    return subprocess.run(
        [sys.executable, "-m", "apps_rg", *argv_tail],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def _headline_base_argv() -> list[str]:
    return [
        "--section",
        "headline",
        "--target-company",
        "CI-Probe-Co",
        "--target-role",
        "Software Engineer",
    ]


@pytest.mark.parametrize("section", ["headline", "competencies", "ibm_bullets"])
def test_section_cli_blocks_missing_jd_before_dispatch(section: str) -> None:
    result = run_pre_dispatch_preflight(
        section=section,
        jd="",
        manual_brief=str(_FRESH_BRIEF),
        lane_provider="qwen_vllm",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
    )
    assert result.dispatch_started is False
    assert result.jd_status == "MISSING"
    with pytest.raises(SectionCliConfigError):
        enforce_pre_dispatch_preflight(
            section=section,
            jd="",
            manual_brief=str(_FRESH_BRIEF),
            lane_provider="qwen_vllm",
            provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
            artifact_dir=str(REPO / "artifacts" / "contract_preflight_smoke"),
        )


@pytest.mark.parametrize("section", ["headline", "unify_narrative"])
def test_section_cli_blocks_missing_briefing_before_dispatch(section: str) -> None:
    result = run_pre_dispatch_preflight(
        section=section,
        jd=str(_FRESH_JD),
        manual_brief="",
        lane_provider="qwen_vllm",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
    )
    assert result.dispatch_started is False
    assert result.manual_brief_status == "MISSING"


def test_section_cli_blocks_stale_default_jd_path_before_dispatch() -> None:
    result = run_pre_dispatch_preflight(
        section="headline",
        jd=str(_DEFAULT_JD),
        manual_brief=str(_FRESH_BRIEF),
        lane_provider="qwen_vllm",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
    )
    assert result.dispatch_started is False
    err = result.decisive_reason.lower()
    assert "default" in err or "stale" in err or "not updated" in err or "placeholder" in err


def test_section_cli_blocks_stale_default_briefing_path_before_dispatch() -> None:
    result = run_pre_dispatch_preflight(
        section="headline",
        jd=str(_FRESH_JD),
        manual_brief=str(_DEFAULT_BRIEF),
        lane_provider="qwen_vllm",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
    )
    assert result.dispatch_started is False
    err = result.decisive_reason.lower()
    assert "default" in err or "stale" in err or "briefing" in err


@pytest.mark.contract_harness_live
def test_default_paths_allowed_with_explicit_override_env() -> None:
    r = _run_cli(
        [
            *_headline_base_argv(),
            "--jd",
            str(_DEFAULT_JD),
            "--manual-brief",
            str(_DEFAULT_BRIEF),
            "--dry-run",
        ],
        env_extra={
            "APPS_RG_ALLOW_STALE_TARGETING_SSOT": "1",
            "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB": "1",
        },
    )
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "pre-dispatch" in (r.stdout or "").lower()


def test_qwen_down_blocks_before_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VLLM_BASE_URL", "http://127.0.0.1:9/")
    monkeypatch.setenv("APPS_RG_QWEN_DISABLE_OFFLINE_STUB", "1")
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_SKIP_QWEN_VLLM_HEALTH", raising=False)
    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._docker_container_running",
        lambda _c: (True, ""),
    )

    from apps_rg.__main__ import main

    rc = main(
        [
            *_headline_base_argv(),
            "--jd",
            str(_FRESH_JD),
            "--manual-brief",
            str(_FRESH_BRIEF),
        ]
    )
    assert rc == 2


def test_qwen_model_mismatch_blocks_before_dispatch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_SKIP_QWEN_VLLM_HEALTH", raising=False)
    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._docker_container_running",
        lambda _c: (True, ""),
    )

    def _http_model_mismatch() -> tuple[bool, str]:
        return False, "wrong_or_missing_model_id: expected Qwen substring missing"

    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._http_models_health_check",
        _http_model_mismatch,
    )

    health, model, detail = evaluate_qwen_readiness(lane_provider="qwen_vllm")
    assert health == "PASS"
    assert model == "FAIL"
    assert detail

    result = run_pre_dispatch_preflight(
        section="headline",
        jd=str(_FRESH_JD),
        manual_brief=str(_FRESH_BRIEF),
        lane_provider="qwen_vllm",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
    )
    assert result.dispatch_started is False
    assert "model" in result.decisive_reason.lower()


def test_no_dev_default_mock_when_qwen_required(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_rg.runtime.section_cli_defaults import resolve_cli_lane_provider_with_source

    monkeypatch.delenv("APPS_RG_MODULAR_LANE_PROVIDER", raising=False)
    prov, src = resolve_cli_lane_provider_with_source(None)
    assert prov == "qwen_vllm"
    assert src == CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM
    assert src != "mock"


@pytest.mark.contract_harness_live
def test_fresh_inputs_and_stub_allow_dry_run_dispatch_path() -> None:
    r = _run_cli(
        [
            *_headline_base_argv(),
            "--jd",
            str(_FRESH_JD),
            "--manual-brief",
            str(_FRESH_BRIEF),
            "--dry-run",
        ],
        env_extra={"APPS_RG_QWEN_OFFLINE_CONTRACT_STUB": "1"},
    )
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "dispatch_started=true" in (r.stdout or "").lower() or "pre_dispatch_preflight" in (
        r.stdout or ""
    ).lower()


def test_preflight_receipt_records_dispatch_not_started_on_block(tmp_path: Path) -> None:
    from apps_rg.runtime.pre_dispatch_preflight import (
        enforce_pre_dispatch_preflight,
        write_pre_dispatch_preflight_receipt,
    )

    result = run_pre_dispatch_preflight(
        section="headline",
        jd="",
        manual_brief=str(_FRESH_BRIEF),
        lane_provider="qwen_vllm",
        provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
    )
    path = tmp_path / "apps_rg_pre_dispatch_preflight.json"
    write_pre_dispatch_preflight_receipt(path, result)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["dispatch_started"] is False
    assert data["jd_status"] == "MISSING"
    assert data["manual_brief_status"] == "PASS"

    with pytest.raises(SectionCliConfigError):
        enforce_pre_dispatch_preflight(
            section="headline",
            jd="",
            manual_brief=str(_FRESH_BRIEF),
            lane_provider="qwen_vllm",
            provider_resolution_source=CLI_PROVIDER_RESOLUTION_DEV_DEFAULT_QWEN_VLLM,
            artifact_dir=str(tmp_path),
        )


def test_evaluate_jd_empty_file(tmp_path: Path) -> None:
    empty = tmp_path / "empty_jd.txt"
    empty.write_text("   \n", encoding="utf-8")
    status, path = evaluate_jd_cli_input(str(empty))
    assert status == "EMPTY"
    assert path


def test_evaluate_brief_missing_path() -> None:
    status, _ = evaluate_manual_brief_cli_input("artifacts/does_not_exist_brief.txt")
    assert status == "MISSING"
