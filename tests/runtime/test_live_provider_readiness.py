"""W2b Phase P7 — tests for probe_live_provider_readiness.

Unit tests with no live network calls. The probe is exercised end-to-end
via the public ``run_readiness_probe()`` entry point with provider helpers
monkey-patched. Integration tests that hit the real vLLM / Anthropic endpoint
live behind ``pytest.mark.integration`` (T1, T2 of the W2b test matrix).

Plan: .windsurf/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md § 7
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.evidence import probe_live_provider_readiness as P  # noqa: E402


@pytest.fixture
def clean_anthropic_env(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


class TestReadinessProbeStructure:
    def test_run_report_has_all_required_keys(self, monkeypatch, clean_anthropic_env):
        monkeypatch.setattr(P, "_probe_local_qwen", lambda: {
            "provider": "local_qwen", "order": 1, "available": False,
            "endpoint": "http://localhost:8000/v1",
            "model_id": "Qwen/Qwen2.5-7B-Instruct", "model_version": None,
            "probe_latency_ms": None, "probe_method": "GET /v1/models",
            "failure_reason": "not running",
        })
        report = P.run_readiness_probe()
        assert report["schema_version"] == 1
        assert set(report) >= {
            "schema_version", "executed_at_utc", "candidates",
            "chosen_provider", "chosen_reason", "unavailable_reasons",
        }
        assert isinstance(report["candidates"], list)
        assert len(report["candidates"]) == 2
        providers = {c["provider"] for c in report["candidates"]}
        assert providers == {"local_qwen", "anthropic_haiku"}

    def test_chosen_provider_is_local_qwen_when_available(
        self, monkeypatch, clean_anthropic_env
    ):
        monkeypatch.setattr(P, "_probe_local_qwen", lambda: {
            "provider": "local_qwen", "order": 1, "available": True,
            "endpoint": "http://localhost:8000/v1",
            "model_id": "Qwen2.5-7B-Instruct", "model_version": "Qwen2.5-7B-Instruct",
            "probe_latency_ms": 12.5, "probe_method": "GET /v1/models",
            "failure_reason": None,
        })
        report = P.run_readiness_probe()
        assert report["chosen_provider"] == "local_qwen"

    def test_fallback_to_anthropic_when_qwen_unavailable(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-not-logged")
        monkeypatch.setattr(P, "_probe_local_qwen", lambda: {
            "provider": "local_qwen", "order": 1, "available": False,
            "endpoint": "http://localhost:8000/v1",
            "model_id": "Qwen2.5-7B-Instruct", "model_version": None,
            "probe_latency_ms": None, "probe_method": "GET /v1/models",
            "failure_reason": "connection refused",
        })
        report = P.run_readiness_probe()
        assert report["chosen_provider"] == "anthropic_haiku"

    def test_no_chosen_when_neither_available(
        self, monkeypatch, clean_anthropic_env
    ):
        monkeypatch.setattr(P, "_probe_local_qwen", lambda: {
            "provider": "local_qwen", "order": 1, "available": False,
            "endpoint": "http://localhost:8000/v1",
            "model_id": "Qwen2.5-7B-Instruct", "model_version": None,
            "probe_latency_ms": None, "probe_method": "GET /v1/models",
            "failure_reason": "connection refused",
        })
        report = P.run_readiness_probe()
        assert report["chosen_provider"] is None
        assert len(report["unavailable_reasons"]) == 2

    def test_mock_safe_never_appears_as_chosen(
        self, monkeypatch, clean_anthropic_env
    ):
        # Even if someone sets LLMJUDGEVETO_APPROVED_MOCK_SAFE=1 the
        # readiness probe must not surface mock_safe as a candidate.
        monkeypatch.setenv("LLMJUDGEVETO_APPROVED_MOCK_SAFE", "1")
        monkeypatch.setattr(P, "_probe_local_qwen", lambda: {
            "provider": "local_qwen", "order": 1, "available": False,
            "endpoint": "http://localhost:8000/v1",
            "model_id": "Qwen2.5-7B-Instruct", "model_version": None,
            "probe_latency_ms": None, "probe_method": "GET /v1/models",
            "failure_reason": "connection refused",
        })
        report = P.run_readiness_probe()
        providers = {c["provider"] for c in report["candidates"]}
        assert "mock_safe" not in providers
        assert report["chosen_provider"] != "mock_safe"


class TestReadinessArtifactWrite:
    def test_main_writes_artifact(self, monkeypatch, tmp_path, clean_anthropic_env):
        monkeypatch.setattr(P, "ARTIFACT_DIR", tmp_path)
        monkeypatch.setattr(P, "ARTIFACT_PATH", tmp_path / "live_provider_readiness.json")
        monkeypatch.setattr(P, "_probe_local_qwen", lambda: {
            "provider": "local_qwen", "order": 1, "available": False,
            "endpoint": "http://localhost:8000/v1",
            "model_id": "Qwen2.5-7B-Instruct", "model_version": None,
            "probe_latency_ms": None, "probe_method": "GET /v1/models",
            "failure_reason": "not running",
        })
        rc = P.main()
        assert rc == 0
        payload = json.loads(
            (tmp_path / "live_provider_readiness.json").read_text(encoding="utf-8")
        )
        assert payload["chosen_provider"] is None


class TestNoSecretsInArtifact:
    def test_api_key_value_never_recorded(self, monkeypatch, tmp_path):
        """Even if ANTHROPIC_API_KEY is set, its value must not leak into
        the readiness artifact. Only the presence boolean is allowed."""
        secret = "sk-should-never-appear-in-artifact-12345"
        monkeypatch.setenv("ANTHROPIC_API_KEY", secret)
        monkeypatch.setattr(P, "ARTIFACT_DIR", tmp_path)
        monkeypatch.setattr(P, "ARTIFACT_PATH", tmp_path / "r.json")
        monkeypatch.setattr(P, "_probe_local_qwen", lambda: {
            "provider": "local_qwen", "order": 1, "available": False,
            "endpoint": "http://localhost:8000/v1",
            "model_id": "Qwen", "model_version": None,
            "probe_latency_ms": None, "probe_method": "GET /v1/models",
            "failure_reason": "not running",
        })
        P.main()
        text = (tmp_path / "r.json").read_text(encoding="utf-8")
        assert secret not in text
