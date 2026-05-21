"""Narrow contract slice: apps_rg Qwen/vLLM transport reliability W0–W2.

Avoid broad ``-k competencies`` filters — this module is the tight proof surface for:
transport diagnostics, competencies HTTP models preflight, stub-disable semantics, docker opt-in.

Does not replace full apps_rg or competencies contract suites.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from apps_rg.runtime import qwen_transport_diag as qtd
from apps_rg.runtime.judges import executive_summary_x1d as es_x1d


def test_offline_contract_stub_disabled_at_runtime() -> None:
    """Product runs must not synthesize Qwen responses without vLLM HTTP."""
    from apps_rg.runtime.qwen_offline_contract_stub import (
        effective_offline_contract_stub_enabled,
        offline_contract_stub_enabled,
        synthetic_qwen_provider_result,
    )

    assert offline_contract_stub_enabled() is False
    assert effective_offline_contract_stub_enabled() is False
    with pytest.raises(RuntimeError, match="disabled"):
        synthetic_qwen_provider_result(raw_model_output="{}", requested_model="Qwen/Qwen2.5-32B-Instruct-AWQ")


def test_probe_failure_writes_diagnostic_with_base_url_and_category(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ad = tmp_path / "c"
    ad.mkdir()
    qtd.reset_transport_context_for_tests()
    monkeypatch.delenv("APPS_RG_QWEN_OFFLINE_CONTRACT_STUB", raising=False)
    monkeypatch.delenv("APPS_RG_QWEN_DISABLE_OFFLINE_STUB", raising=False)

    snap = {"probe_url": "http://127.0.0.1:9/v1/models", "status": "unhealthy", "error": "http_503"}

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
    qtd.merge_transport_context(artifact_dir=str(ad.resolve()), run_id="contract_r1", section_lane="competencies")

    ok, _, code = qtd.ensure_http_preflight_and_banner_for_slice(
        base_url="http://127.0.0.1:9/v1",
        timeout_seconds=1.0,
    )
    assert ok is False
    assert code == qtd.ERR_HTTP_MODELS_PROBE
    doc_path = ad / qtd.SIDECAR_NAME
    assert doc_path.is_file()
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    assert doc["effective_base_url"] == "http://127.0.0.1:9/v1"
    assert doc["error_category"] == qtd.ERR_HTTP_MODELS_PROBE
    assert doc["mock_or_stub_used"] is False


def test_diagnostic_sidecar_redacts_prompt_and_secrets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from apps_rg.runtime.providers import qwen_vllm_provider as qvp

    ad = tmp_path / "r"
    ad.mkdir()
    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(ad.resolve()))
    scary = "Bearer VERYSECRETTOKEN messages=[{\"content\":\"HEAVY_PROMPT_LEAK\"}] sk-abcdefghijklmnopqrstuvwxyz0123456789"

    def _boom(_req: object, timeout: object = None) -> object:  # noqa: ARG001
        raise ValueError(scary)

    monkeypatch.setattr(qvp.urllib.request, "urlopen", _boom)
    payload = {
        "model": qvp.DEFAULT_QWEN_MODEL,
        "messages": [{"role": "user", "content": "PROMPT_BODY"}],
        "temperature": 0.1,
        "max_tokens": 4,
        "timeout_seconds": 2,
        "response_format": {"type": "json_object"},
    }
    _ = qvp.call_qwen_vllm(payload, base_url="http://127.0.0.1:9/v1")
    raw = (ad / qtd.SIDECAR_NAME).read_text(encoding="utf-8").lower()
    assert "heavy_prompt_leak" not in raw
    assert "prompt_body" not in raw
    assert "verysecrettoken" not in raw


def test_docker_restart_is_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPS_RG_QWEN_VLLM_DOCKER_RESTART", raising=False)
    audit = None
    assert qtd.docker_restart_banner_label(audit) == "disabled"


def test_competencies_gate_uses_http_models_preflight_not_tcp_only() -> None:
    from apps_rg.runtime.providers import competencies_live_provider_gate as gate

    src = Path(gate.__file__).read_text(encoding="utf-8")
    assert "run_http_models_preflight" in src
    assert "def qwen_vllm_http_models_preflight" in src
    assert "preflight_transport" in src
    assert "http_v1_models" in src


def test_judge_openai_https_blocked_under_pytest_without_network_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """Regression: unify_narrative (and other lanes) must not hang on live OpenAI during pytest."""
    monkeypatch.delenv("APPS_RG_ENABLE_NETWORK_TESTS", raising=False)
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "contract/test_fake.py::test_x")

    out = es_x1d._call_openai(
        api_key="sk-test-not-used",
        prompt="hi",
        model="gpt-4.1",
        input_hash="abc",
        provider_key="openai_chatgpt",
    )
    assert out.provider_blocked is True
    assert out.provider_status == "NETWORK_TESTS_NOT_ENABLED"
    assert "APPS_RG_ENABLE_NETWORK_TESTS" in (out.exact_provider_error or "")

    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
