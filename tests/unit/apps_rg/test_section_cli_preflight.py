"""Unit tests for section CLI preflight (mock fast-fail, vLLM health gate)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from apps_rg.runtime.section_cli_defaults import (
    CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE,
    SectionCliConfigError,
    resolve_cli_lane_provider_with_source,
)
from apps_rg.runtime.section_cli_preflight import (
    require_qwen_vllm_cli_health,
    should_skip_qwen_vllm_health_gate,
)


def test_resolve_cli_rejects_mock_provider_fast() -> None:
    with pytest.raises(SectionCliConfigError, match="Invalid --provider 'mock'"):
        resolve_cli_lane_provider_with_source("mock")


def test_resolve_cli_accepts_qwen_vllm() -> None:
    prov, src = resolve_cli_lane_provider_with_source("qwen_vllm")
    assert prov == "qwen_vllm"
    assert src == CLI_PROVIDER_RESOLUTION_CLI_OVERRIDE


def test_health_gate_skipped_when_offline_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    assert should_skip_qwen_vllm_health_gate() is True
    require_qwen_vllm_cli_health(lane_provider="qwen_vllm", docker_restart_audit={})


def _clear_health_skip_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "APPS_RG_SKIP_QWEN_VLLM_HEALTH",
    ):
        monkeypatch.delenv(key, raising=False)


def test_health_gate_fails_when_docker_not_running(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_health_skip_env(monkeypatch)

    def _docker_fail(_container: str) -> tuple[bool, str]:
        return False, "container not running"

    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._docker_container_running",
        _docker_fail,
    )
    with pytest.raises(SectionCliConfigError, match="docker container health check failed"):
        require_qwen_vllm_cli_health(lane_provider="qwen_vllm")


def test_health_gate_fails_when_http_probe_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_health_skip_env(monkeypatch)

    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._docker_container_running",
        lambda _c: (True, ""),
    )

    def _http_fail() -> tuple[bool, str]:
        return False, "http_503"

    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._http_models_health_check",
        _http_fail,
    )
    with pytest.raises(SectionCliConfigError, match="HTTP /v1/models health check failed"):
        require_qwen_vllm_cli_health(lane_provider="qwen_vllm")


def test_health_gate_accepts_docker_restart_audit_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_health_skip_env(monkeypatch)
    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._docker_container_running",
        lambda _c: (True, ""),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._http_models_health_check",
        lambda: (True, ""),
    )
    require_qwen_vllm_cli_health(
        lane_provider="qwen_vllm",
        docker_restart_audit={"ready": True, "performed": True},
    )


def test_health_gate_fails_when_restart_not_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_health_skip_env(monkeypatch)
    with pytest.raises(SectionCliConfigError, match="readiness probe failed"):
        require_qwen_vllm_cli_health(
            lane_provider="qwen_vllm",
            docker_restart_audit={
                "performed": True,
                "ready": False,
                "probe_error": "probe_budget_exhausted",
            },
        )


def test_health_gate_auto_starts_container_when_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_health_skip_env(monkeypatch)
    monkeypatch.setenv("APPS_RG_VLLM_AUTO_START", "1")
    calls: list[str] = []

    def _docker_state(_container: str) -> tuple[bool, str]:
        calls.append("inspect")
        return len(calls) >= 2, ""

    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._docker_container_running",
        _docker_state,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._try_start_qwen_container",
        lambda _c: (True, ""),
    )
    monkeypatch.setattr(
        "apps_rg.runtime.section_cli_preflight._http_models_health_check",
        lambda: (True, ""),
    )
    require_qwen_vllm_cli_health(lane_provider="qwen_vllm")
    assert calls.count("inspect") >= 2
