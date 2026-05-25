"""Unit tests for optional Qwen vLLM Docker pre-run restart (apps_rg-local, W4 readiness)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L2_execution.healers.vllm_health_probe import VLLMHealth

from apps_rg.runtime import qwen_transport_diag as qtd


@pytest.fixture
def clean_restart_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in (
        "APPS_RG_QWEN_VLLM_DOCKER_RESTART",
        "APPS_RG_QWEN_OFFLINE_CONTRACT_STUB",
        "APPS_RG_QWEN_DISABLE_OFFLINE_STUB",
        "APPS_RG_L2_FORCE_STUB",
        "APPS_RG_L2_PROVIDER_MODE",
        "APPS_RG_MODULAR_LANE_PROVIDER",
        "APPS_RG_QWEN_VLLM_DOCKER_RESTART_MODE",
        "APPS_RG_QWEN_VLLM_CONTAINER_NAME",
        "APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING",
        "APPS_RG_QWEN_VLLM_MODEL_READY_SUBSTRING",
    ):
        monkeypatch.delenv(k, raising=False)


def test_restart_not_configured_skips(clean_restart_env: None) -> None:
    from apps_rg.runtime.qwen_vllm_docker_restart import maybe_restart_qwen_vllm_for_apps_rg_run

    audit = maybe_restart_qwen_vllm_for_apps_rg_run(
        running_section_lane=False,
        cli_provider=None,
    )
    assert audit["skipped"] is True
    assert audit["reason"] == "not_configured"
    assert audit.get("performed") is False
    assert audit["readiness_status"] == qtd.READINESS_RESTART_DISABLED
    assert audit["restart_requested"] is False
    assert audit["attempt_count"] == 0


def test_restart_disabled_no_docker_subprocess(
    clean_restart_env: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    mock_run = MagicMock()
    monkeypatch.setattr(mod.subprocess, "run", mock_run)
    audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
        running_section_lane=False,
        cli_provider=None,
    )
    assert audit["readiness_status"] == qtd.READINESS_RESTART_DISABLED
    mock_run.assert_not_called()


def test_restart_stub_env_does_not_skip_when_probe_healthy(
    monkeypatch: pytest.MonkeyPatch, clean_restart_env: None
) -> None:
    """Offline stub flag alone no longer skips docker restart (live-qwen-only policy)."""
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    healthy = VLLMHealth(
        status="healthy",
        model_id="Qwen/Qwen2.5-32B-Instruct-AWQ",
        latency_ms=1.0,
        checked_at=0.0,
    )
    with (
        patch.object(mod, "probe", return_value=healthy),
        patch.object(
            mod,
            "fetch_openai_compatible_model_ids",
            return_value=(200, ["Qwen/Qwen2.5-32B-Instruct-AWQ"], None),
        ),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    assert audit["skipped"] is True
    assert audit["reason"] == "already_healthy"


def test_if_unhealthy_skips_when_probe_healthy(monkeypatch: pytest.MonkeyPatch, clean_restart_env: None) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    healthy = VLLMHealth(
        status="healthy",
        model_id="Qwen/Qwen2.5-32B-Instruct-AWQ",
        latency_ms=1.0,
        checked_at=0.0,
    )
    with (
        patch.object(mod, "probe", return_value=healthy),
        patch.object(
            mod,
            "fetch_openai_compatible_model_ids",
            return_value=(200, ["Qwen/Qwen2.5-32B-Instruct-AWQ"], None),
        ),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    assert audit["skipped"] is True
    assert audit["reason"] == "already_healthy"
    assert audit.get("performed") is False
    assert audit["readiness_status"] == qtd.READINESS_RESTART_NOT_REQUESTED
    assert audit["ready"] is True
    assert "Qwen" in audit["observed_model_ids"][0]


def test_if_unhealthy_restarts_when_unhealthy(monkeypatch: pytest.MonkeyPatch, clean_restart_env: None) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_CONTAINER_NAME", "test-qwen")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    bad = VLLMHealth(status="unhealthy", model_id="", latency_ms=1.0, checked_at=0.0, error="conn")
    proc = MagicMock()
    proc.returncode = 0
    proc.stderr = ""
    proc.stdout = ""
    with (
        patch.object(mod, "probe", return_value=bad),
        patch.object(
            mod,
            "fetch_openai_compatible_model_ids",
            return_value=(200, ["Qwen/Qwen2.5-32B-Instruct-AWQ"], None),
        ),
        patch.object(mod.shutil, "which", return_value="/bin/docker"),
        patch.object(mod.subprocess, "run", return_value=proc) as mock_run,
        patch.object(mod.time, "sleep", lambda *a, **k: None),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    mock_run.assert_called_once()
    assert mock_run.call_args[0][0] == ["docker", "restart", "test-qwen"]
    assert audit["performed"] is True
    assert audit["ready"] is True
    assert audit["readiness_status"] == qtd.READINESS_READY


def test_restart_enabled_docker_fails_not_ready(
    monkeypatch: pytest.MonkeyPatch, clean_restart_env: None
) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART_MODE", "always")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    proc = MagicMock()
    proc.returncode = 1
    proc.stderr = "no such container"
    proc.stdout = ""
    with (
        patch.object(
            mod,
            "probe",
            return_value=VLLMHealth(
                status="healthy",
                model_id="Qwen/x",
                latency_ms=1.0,
                checked_at=0.0,
            ),
        ),
        patch.object(mod.shutil, "which", return_value="/bin/docker"),
        patch.object(mod.subprocess, "run", return_value=proc),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    assert audit["readiness_status"] == qtd.READINESS_RESTART_FAILED
    assert audit["ready"] is False
    assert audit["restart_outcome"] == "failed"
    assert audit["performed"] is False


def test_restart_succeeds_models_probe_fails_not_ready(
    monkeypatch: pytest.MonkeyPatch, clean_restart_env: None
) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_READY_WAIT_SECONDS", "10")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    bad = VLLMHealth(status="unhealthy", model_id="", latency_ms=1.0, checked_at=0.0, error="x")
    proc = MagicMock()
    proc.returncode = 0
    proc.stderr = ""
    proc.stdout = ""
    with (
        patch.object(mod, "probe", return_value=bad),
        patch.object(mod, "fetch_openai_compatible_model_ids", return_value=(None, [], "url_error:refused")),
        patch.object(mod.shutil, "which", return_value="/bin/docker"),
        patch.object(mod.subprocess, "run", return_value=proc),
        patch.object(mod.time, "sleep", lambda *a, **k: None),
        patch.object(mod.time, "monotonic", side_effect=[0.0, 5.0, 15.0]),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    assert audit["performed"] is True
    assert audit["ready"] is False
    assert audit["readiness_status"] == qtd.READINESS_PROBE_FAILED


def test_http_up_wrong_model_not_ready(
    monkeypatch: pytest.MonkeyPatch, clean_restart_env: None
) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    healthy = VLLMHealth(
        status="healthy",
        model_id="meta-llama/Llama-3-8B",
        latency_ms=1.0,
        checked_at=0.0,
    )
    with (
        patch.object(mod, "probe", return_value=healthy),
        patch.object(
            mod,
            "fetch_openai_compatible_model_ids",
            return_value=(200, ["meta-llama/Llama-3-8B"], None),
        ),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    assert audit["reason"] == "model_readiness_failed"
    assert audit["readiness_status"] == qtd.READINESS_MODEL_MISMATCH
    assert audit["ready"] is False


def test_http_up_qwen_model_ready(
    monkeypatch: pytest.MonkeyPatch, clean_restart_env: None
) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    healthy = VLLMHealth(
        status="healthy",
        model_id="Qwen/Qwen2.5-32B-Instruct-AWQ",
        latency_ms=1.0,
        checked_at=0.0,
    )
    with (
        patch.object(mod, "probe", return_value=healthy),
        patch.object(
            mod,
            "fetch_openai_compatible_model_ids",
            return_value=(200, ["Qwen/Qwen2.5-32B-Instruct-AWQ"], None),
        ),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    assert audit["readiness_status"] == qtd.READINESS_RESTART_NOT_REQUESTED
    assert audit["ready"] is True


def test_custom_expected_substring_honored(
    monkeypatch: pytest.MonkeyPatch, clean_restart_env: None
) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    monkeypatch.setenv("APPS_RG_QWEN_EXPECTED_MODEL_SUBSTRING", "CustomZephyr")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    healthy = VLLMHealth(status="healthy", model_id="x", latency_ms=1.0, checked_at=0.0)
    with (
        patch.object(mod, "probe", return_value=healthy),
        patch.object(
            mod,
            "fetch_openai_compatible_model_ids",
            return_value=(200, ["org/CustomZephyr-7B"], None),
        ),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    assert audit["expected_model_substring"] == "CustomZephyr"
    assert audit["ready"] is True


def test_readiness_artifact_redacts_decisive_reason(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, clean_restart_env: None
) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    healthy = VLLMHealth(status="healthy", model_id="x", latency_ms=1.0, checked_at=0.0)
    with (
        patch.object(mod, "probe", return_value=healthy),
        patch.object(
            mod,
            "fetch_openai_compatible_model_ids",
            return_value=(200, ["meta/x"], None),
        ),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    audit["decisive_reason"] = "upstream said Bearer VERYSECRETTOKEN for model"

    path = qtd.persist_docker_restart_readiness_artifact(tmp_path, audit)
    assert path is not None
    raw = path.read_text(encoding="utf-8").lower()
    assert "verysecrettoken" not in raw
    assert "redacted" in raw or "[redacted]" in raw


def test_empty_models_list_not_ready(
    monkeypatch: pytest.MonkeyPatch, clean_restart_env: None
) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    from apps_rg.runtime import qwen_vllm_docker_restart as mod

    healthy = VLLMHealth(status="healthy", model_id="", latency_ms=1.0, checked_at=0.0)
    with (
        patch.object(mod, "probe", return_value=healthy),
        patch.object(mod, "fetch_openai_compatible_model_ids", return_value=(200, [], None)),
    ):
        audit = mod.maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=False,
            cli_provider=None,
        )
    assert audit["readiness_status"] == qtd.READINESS_MODEL_MISSING
    assert audit["ready"] is False


def test_section_lane_mock_skips(monkeypatch: pytest.MonkeyPatch, clean_restart_env: None) -> None:
    monkeypatch.setenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", "1")
    from apps_rg.runtime.qwen_vllm_docker_restart import maybe_restart_qwen_vllm_for_apps_rg_run

    with patch(
        "apps_rg.runtime.section_cli_defaults.resolve_cli_lane_provider_with_source",
        return_value=("mock", "unit_test"),
    ):
        audit = maybe_restart_qwen_vllm_for_apps_rg_run(
            running_section_lane=True,
            cli_provider="mock",
        )
    assert audit["skipped"] is True
    assert audit["reason"] == "section_lane_provider_mock"
