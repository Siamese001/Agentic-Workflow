"""W3: bounded transient-only retries for live Qwen/vLLM chat/completions transport."""
from __future__ import annotations

import http.client
import io
import json
from pathlib import Path

import pytest
import urllib.error

from apps_rg.runtime import qwen_transport_diag as qtd
from apps_rg.runtime.providers import qwen_vllm_provider as qvp


def _ok_body() -> bytes:
    return json.dumps(
        {
            "model": "Qwen/Qwen2.5-32B-Instruct-AWQ",
            "choices": [{"message": {"content": "{}"}}],
        }
    ).encode()


class _FakeResp:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResp:
        return self

    def __exit__(self, *_a: object) -> bool:
        return False


def test_transient_timeout_then_success_retries(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(tmp_path))
    monkeypatch.setenv("APPS_RG_QWEN_TRANSPORT_MAX_ATTEMPTS", "3")
    monkeypatch.setattr(qvp.time, "sleep", lambda *a, **k: None)

    calls: list[int] = []

    def _urlopen(req: object, timeout: object = None) -> object:  # noqa: ARG001
        calls.append(1)
        if len(calls) == 1:
            raise TimeoutError("unit_simulated")
        return _FakeResp(_ok_body())

    monkeypatch.setattr(qvp.urllib.request, "urlopen", _urlopen)

    payload = {
        "model": qvp.DEFAULT_QWEN_MODEL,
        "messages": [{"role": "user", "content": "{}"}],
        "temperature": 0.1,
        "max_tokens": 8,
        "timeout_seconds": 5,
        "response_format": {"type": "json_object"},
    }
    result = qvp.call_qwen_vllm(payload, base_url="http://127.0.0.1:9/v1")
    assert result.runtime_generation_status == "REAL_LLM"
    assert len(calls) == 2
    doc_path = tmp_path / qtd.SIDECAR_NAME
    assert doc_path.is_file()
    doc = json.loads(doc_path.read_text(encoding="utf-8"))
    assert doc["attempt_count"] == 2
    assert doc["retried"] is True
    assert doc["final_error_category"] == qtd.ERR_TRANSPORT_RECOVERED
    assert doc["retry_reasons"] == ["timeout"]
    assert len(doc["attempts"]) == 1
    assert doc["runtime_generation_status"] == "REAL_LLM"
    assert doc["effective_base_url"] == "http://127.0.0.1:9/v1"
    assert doc["model"] == qvp.DEFAULT_QWEN_MODEL


def test_http_401_no_retry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(tmp_path))
    monkeypatch.setattr(qvp.time, "sleep", lambda *a, **k: None)

    calls: list[int] = []

    def _urlopen(req: object, timeout: object = None) -> object:  # noqa: ARG001
        calls.append(1)
        url = getattr(req, "full_url", "http://x/v1/chat/completions")
        hdrs = http.client.HTTPMessage()
        raise urllib.error.HTTPError(url, 401, "Unauthorized", hdrs, io.BytesIO(b"no"))

    monkeypatch.setattr(qvp.urllib.request, "urlopen", _urlopen)

    payload = {
        "model": qvp.DEFAULT_QWEN_MODEL,
        "messages": [{"role": "user", "content": "{}"}],
        "temperature": 0.1,
        "max_tokens": 8,
        "timeout_seconds": 5,
        "response_format": {"type": "json_object"},
    }
    result = qvp.call_qwen_vllm(payload, base_url="http://127.0.0.1:9/v1")
    assert result.runtime_generation_status == "BLOCKED"
    assert len(calls) == 1


def test_wrong_model_id_no_transport_retry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(tmp_path))

    def _urlopen(req: object, timeout: object = None) -> object:  # noqa: ARG001
        body = json.dumps(
            {
                "model": "SomeOther/Model-Id",
                "choices": [{"message": {"content": "{}"}}],
            }
        ).encode()
        return _FakeResp(body)

    monkeypatch.setattr(qvp.urllib.request, "urlopen", _urlopen)

    payload = {
        "model": qvp.DEFAULT_QWEN_MODEL,
        "messages": [{"role": "user", "content": "{}"}],
        "temperature": 0.1,
        "max_tokens": 8,
        "timeout_seconds": 5,
        "response_format": {"type": "json_object"},
    }
    result = qvp.call_qwen_vllm(payload, base_url="http://127.0.0.1:9/v1")
    assert result.runtime_generation_status == "STUBBED"
    assert result.stub is True


def test_malformed_json_body_no_transport_retry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(tmp_path))

    calls: list[int] = []

    def _urlopen(req: object, timeout: object = None) -> object:  # noqa: ARG001
        calls.append(1)
        return _FakeResp(b"not-json{")

    monkeypatch.setattr(qvp.urllib.request, "urlopen", _urlopen)

    payload = {
        "model": qvp.DEFAULT_QWEN_MODEL,
        "messages": [{"role": "user", "content": "{}"}],
        "temperature": 0.1,
        "max_tokens": 8,
        "timeout_seconds": 5,
        "response_format": {"type": "json_object"},
    }
    result = qvp.call_qwen_vllm(payload, base_url="http://127.0.0.1:9/v1")
    assert result.runtime_generation_status == "BLOCKED"
    assert len(calls) == 1
    doc = json.loads((tmp_path / qtd.SIDECAR_NAME).read_text(encoding="utf-8"))
    assert doc["final_error_category"] == qtd.ERR_MALFORMED_RESPONSE
    assert doc["attempt_count"] == 1
    assert doc["retried"] is False


def test_repeated_transient_503_writes_full_attempt_trace(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(tmp_path))
    monkeypatch.setenv("APPS_RG_QWEN_TRANSPORT_MAX_ATTEMPTS", "3")
    monkeypatch.setattr(qvp.time, "sleep", lambda *a, **k: None)

    def _urlopen(req: object, timeout: object = None) -> object:  # noqa: ARG001
        url = getattr(req, "full_url", "http://x/v1/chat/completions")
        hdrs = http.client.HTTPMessage()
        raise urllib.error.HTTPError(url, 503, "Service Unavailable", hdrs, io.BytesIO(b"busy"))

    monkeypatch.setattr(qvp.urllib.request, "urlopen", _urlopen)

    payload = {
        "model": qvp.DEFAULT_QWEN_MODEL,
        "messages": [{"role": "user", "content": "{}"}],
        "temperature": 0.1,
        "max_tokens": 8,
        "timeout_seconds": 5,
        "response_format": {"type": "json_object"},
    }
    result = qvp.call_qwen_vllm(payload, base_url="http://127.0.0.1:9/v1")
    assert result.runtime_generation_status == "BLOCKED"
    doc = json.loads((tmp_path / qtd.SIDECAR_NAME).read_text(encoding="utf-8"))
    assert doc["schema"] == "apps_rg.qwen_transport_diagnostic.v2"
    assert doc["attempt_count"] == 3
    assert len(doc["attempts"]) == 3
    assert doc["retried"] is True
    assert doc["retry_policy_name"] == qtd.RETRY_POLICY_NAME
    assert doc["retry_policy_version"] == qtd.RETRY_POLICY_VERSION
    assert doc["final_error_category"] == qtd.ERR_CHAT_5XX
    assert doc["model"] == qvp.DEFAULT_QWEN_MODEL
    assert doc["effective_base_url"] == "http://127.0.0.1:9/v1"


def test_max_attempts_env_bounds_retries(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(tmp_path))
    monkeypatch.setenv("APPS_RG_QWEN_TRANSPORT_MAX_ATTEMPTS", "2")
    monkeypatch.setattr(qvp.time, "sleep", lambda *a, **k: None)

    calls: list[int] = []

    def _urlopen(req: object, timeout: object = None) -> object:  # noqa: ARG001
        calls.append(1)
        url = getattr(req, "full_url", "http://x/v1/chat/completions")
        hdrs = http.client.HTTPMessage()
        raise urllib.error.HTTPError(url, 503, "Service Unavailable", hdrs, io.BytesIO(b"busy"))

    monkeypatch.setattr(qvp.urllib.request, "urlopen", _urlopen)

    payload = {
        "model": qvp.DEFAULT_QWEN_MODEL,
        "messages": [{"role": "user", "content": "{}"}],
        "temperature": 0.1,
        "max_tokens": 8,
        "timeout_seconds": 5,
        "response_format": {"type": "json_object"},
    }
    _ = qvp.call_qwen_vllm(payload, base_url="http://127.0.0.1:9/v1")
    assert len(calls) == 2


def test_persist_skips_offline_stub_runtime(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Retry path must not treat OFFLINE_CONTRACT_STUB as a transport failure to persist (live proof)."""
    from apps_rg.runtime.qwen_offline_contract_stub import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS

    qtd.reset_transport_context_for_tests()
    qtd.merge_transport_context(artifact_dir=str(tmp_path))

    result = qvp.ProviderResult(
        provider_requested="qwen_vllm",
        provider_attempted=True,
        provider_available=True,
        exact_provider_error=None,
        runtime_generation_status=OFFLINE_CONTRACT_STUB_RUNTIME_STATUS,
        model=qvp.DEFAULT_QWEN_MODEL,
        raw_model_output="{}",
        provider_response={},
        stub=True,
    )
    qtd.persist_failure_for_provider_result(
        result=result,
        base_url="http://x/v1",
        timeout_seconds=5,
        exception=None,
        http_status=None,
        body_fragment="",
        error_category=qtd.ERR_UNKNOWN,
        probe_snapshot=None,
        attempt_count=2,
        retry_reasons=["would_not_run"],
        attempts=[{"attempt_index": 1}],
    )
    assert not (tmp_path / qtd.SIDECAR_NAME).exists()
