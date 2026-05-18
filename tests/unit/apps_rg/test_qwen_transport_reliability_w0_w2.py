"""W0–W2: Qwen vLLM transport diagnostics, probe-before-chat, stub disable, redaction."""
from __future__ import annotations

import http.client
import io
import json
import urllib.error
from pathlib import Path

import pytest

from apps_rg.runtime import qwen_transport_diag as qtd
from apps_rg.runtime.providers import qwen_vllm_provider as qvp
from apps_rg.runtime.providers.section_qwen_slice import call_qwen_vllm, tag_reasoning_lane
from apps_rg.runtime.qwen_offline_contract_stub import (
    effective_offline_contract_stub_enabled,
    offline_contract_stub_enabled,
)


def test_probe_failure_writes_diagnostic_sidecar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ad = tmp_path / "probe_fail"
    ad.mkdir()
    qtd.reset_transport_context_for_tests()
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_QWEN_DISABLE_OFFLINE_STUB", raising=False)

    snap = {
        "probe_url": "http://127.0.0.1:9/v1/models",
        "status": "unhealthy",
        "error": "http_503",
        "model_id": "",
    }

    def _fail(
        *,
        base_url: str,
        timeout_s: float,
        force_refresh: bool = True,  # noqa: ARG001
    ) -> tuple[bool, dict[str, object], str | None]:
        _ = force_refresh
        _ = timeout_s
        _ = base_url
        return False, snap, qtd.ERR_HTTP_MODELS_PROBE

    monkeypatch.setattr(qtd, "run_http_models_preflight", _fail)
    qtd.merge_transport_context(artifact_dir=str(ad.resolve()), run_id="run_probe_x", section_lane="executive_summary")

    ok, out_snap, code = qtd.ensure_http_preflight_and_banner_for_slice(
        base_url="http://127.0.0.1:9/v1",
        timeout_seconds=1.0,
    )
    assert ok is False
    assert code == qtd.ERR_HTTP_MODELS_PROBE
    assert isinstance(out_snap, dict)

    sc = ad / qtd.SIDECAR_NAME
    assert sc.is_file(), "failed /v1/models probe must persist qwen_transport_diagnostic.json"
    body = json.loads(sc.read_text(encoding="utf-8"))
    assert body["effective_base_url"] == "http://127.0.0.1:9/v1"
    assert body["error_category"] == qtd.ERR_HTTP_MODELS_PROBE
    assert body["mock_or_stub_used"] is False
    assert body["run_id"] == "run_probe_x"
    assert body["retry_reasons"] == []


def test_failed_chat_writes_sidecar_not_stub_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ad = tmp_path / "chat_fail"
    ad.mkdir()
    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(ad.resolve()), run_id="run_chat_y")

    def _boom(req: object, timeout: int | float | None = None) -> object:  # noqa: ARG001
        url = getattr(req, "full_url", "http://mock/v1/chat/completions")
        hdrs = http.client.HTTPMessage()
        raise urllib.error.HTTPError(url, 502, "Bad Gateway", hdrs, fp=io.BytesIO(b'{"detail":"upstream"}'))

    monkeypatch.setattr(qvp.urllib.request, "urlopen", _boom)

    payload = {
        "model": qvp.DEFAULT_QWEN_MODEL,
        "messages": [{"role": "user", "content": "{}"}],
        "temperature": 0.2,
        "max_tokens": 8,
        "timeout_seconds": 2,
        "response_format": {"type": "json_object"},
    }
    result = qvp.call_qwen_vllm(payload, base_url="http://127.0.0.1:9/v1")
    assert result.runtime_generation_status == "BLOCKED"
    assert result.provider_available is False

    sc = ad / qtd.SIDECAR_NAME
    assert sc.is_file(), "missing diagnostic artifact on failed live Qwen call"
    doc = json.loads(sc.read_text(encoding="utf-8"))
    assert doc["error_category"] == qtd.ERR_CHAT_5XX
    assert doc["mock_or_stub_used"] is False
    assert doc["http_status"] == 502
    assert doc["effective_base_url"] == "http://127.0.0.1:9/v1"


def test_live_banner_greppable(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    qtd.reset_transport_context_for_tests()
    monkeypatch.delenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", raising=False)
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_QWEN_DISABLE_OFFLINE_STUB", raising=False)

    def _ok(
        *,
        base_url: str,
        timeout_s: float,
        force_refresh: bool = True,  # noqa: ARG001
    ) -> tuple[bool, dict[str, object], str | None]:
        _ = force_refresh
        _ = timeout_s
        _ = base_url
        return True, {"status": "healthy", "model_id": "Qwen/x"}, None

    monkeypatch.setattr(qtd, "run_http_models_preflight", _ok)
    qtd.merge_transport_context(artifact_dir="/tmp/art", section_lane="executive_summary")
    ok, _, _ = qtd.ensure_http_preflight_and_banner_for_slice(
        base_url="http://127.0.0.1:8000/v1",
        timeout_seconds=1.0,
    )
    assert ok is True
    out = capsys.readouterr().out
    assert "APPS_RG_QWEN_LIVE" in out
    assert "provider=qwen_vllm" in out
    assert "probe=pass" in out


def test_diagnostics_redact_secrets_and_no_prompt_payload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ad = tmp_path / "redact"
    ad.mkdir()
    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(ad.resolve()))

    scary = (
        'Bearer abcdefghi messages=[{"role":"user","content":"SECRET_PROMPT_FULL_TEXT"}] '
        "api_key=supersecret sk-abcdefghijklmnopqrstuvwxyz0123456789"
    )

    def _boom(req: object, timeout: int | float | None = None) -> object:  # noqa: ARG001
        raise ValueError(scary)

    monkeypatch.setattr(qvp.urllib.request, "urlopen", _boom)

    payload = {
        "model": qvp.DEFAULT_QWEN_MODEL,
        "messages": [{"role": "user", "content": "LEAK_ME"}],
        "temperature": 0.1,
        "max_tokens": 4,
        "timeout_seconds": 2,
        "response_format": {"type": "json_object"},
    }
    _ = qvp.call_qwen_vllm(payload, base_url="http://127.0.0.1:9/v1")
    raw = (ad / qtd.SIDECAR_NAME).read_text(encoding="utf-8")
    lowered = raw.lower()
    assert "secret_prompt" not in lowered
    assert "leak_me" not in lowered
    assert "supersecret" not in lowered
    assert "abcdefghi" not in raw
    assert "sk-abcdefghijklmnopqrstuvwxyz0123456789" not in raw


def test_disable_offline_stub_forces_live_preflight_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """APPS_RG_QWEN_DISABLE_OFFLINE_STUB must not skip HTTP probe like offline stub."""
    ad = tmp_path / "stub_off"
    ad.mkdir()
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    monkeypatch.setenv("APPS_RG_QWEN_DISABLE_OFFLINE_STUB", "1")
    assert offline_contract_stub_enabled() is True
    assert effective_offline_contract_stub_enabled() is False

    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(ad.resolve()), run_id="r", section_lane="competencies")

    probes = {"n": 0}

    def _track(
        *,
        base_url: str,
        timeout_s: float,
        force_refresh: bool = True,  # noqa: ARG001
    ) -> tuple[bool, dict[str, object], str | None]:
        _ = force_refresh
        _ = timeout_s
        _ = base_url
        probes["n"] += 1
        return False, {"error": "unit_probe", "status": "unhealthy"}, qtd.ERR_HTTP_MODELS_PROBE

    monkeypatch.setattr(qtd, "run_http_models_preflight", _track)

    _, pl = qvp.build_qwen_request(
        messages=[{"role": "user", "content": "{}"}],
        prompt_hash="ph",
        input_payload_hash="ih",
        max_tokens=16,
        temperature=0.3,
    )
    lane_payload = tag_reasoning_lane(pl, "competencies")
    result = call_qwen_vllm(lane_payload, artifact_dir=ad, run_id="r")
    assert probes["n"] == 1
    assert result.apps_rg_qwen_preflight_blocked is True
    assert (ad / qtd.SIDECAR_NAME).is_file()


def test_offline_stub_without_disable_skips_http_probe(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ad = tmp_path / "stub_on"
    ad.mkdir()
    monkeypatch.setenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", "1")
    monkeypatch.delenv("APPS_RG_QWEN_DISABLE_OFFLINE_STUB", raising=False)
    assert effective_offline_contract_stub_enabled() is True

    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(ad.resolve()), run_id="r2", section_lane="competencies")

    probes = {"n": 0}

    def _track(
        *,
        base_url: str,
        timeout_s: float,
        force_refresh: bool = True,  # noqa: ARG001
    ) -> tuple[bool, dict[str, object], str | None]:
        _ = force_refresh
        _ = timeout_s
        _ = base_url
        probes["n"] += 1
        return True, {}, None

    monkeypatch.setattr(qtd, "run_http_models_preflight", _track)

    def _fake_chat(_payload: dict[str, object], *, base_url: str = "") -> qvp.ProviderResult:
        _ = base_url
        return qvp.ProviderResult(
            provider_requested="qwen_vllm",
            provider_attempted=True,
            provider_available=False,
            exact_provider_error="unit_stub_shortcut",
            runtime_generation_status="BLOCKED",
            model=qvp.DEFAULT_QWEN_MODEL,
            raw_model_output="",
            provider_response=None,
        )

    monkeypatch.setattr(
        "apps_rg.runtime.providers.section_qwen_slice.qwen_vllm_provider.call_qwen_vllm",
        _fake_chat,
    )

    _, pl = qvp.build_qwen_request(
        messages=[{"role": "user", "content": "{}"}],
        prompt_hash="ph",
        input_payload_hash="ih",
        max_tokens=16,
        temperature=0.3,
    )
    lane_payload = tag_reasoning_lane(pl, "competencies")
    result = call_qwen_vllm(lane_payload, artifact_dir=ad, run_id="r2")
    assert probes["n"] == 0
    assert result.apps_rg_qwen_preflight_blocked is False
    assert result.exact_provider_error == "unit_stub_shortcut"
