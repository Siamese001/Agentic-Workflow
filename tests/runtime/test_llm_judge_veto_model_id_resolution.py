"""W2b regression test — LLMJudgeVeto model_id resolution precedence.

Precedent: 2026-05-01 first live Scenario A run against
Qwen/Qwen2.5-32B-Instruct-AWQ failed with vLLM 404 because
LLMJudgeVeto hardcoded a non-served model id in both its default argument
and in probe constructors. The correct model was advertised at GET
/v1/models but was ignored. Fail-closed prevented a poisoned attestation;
the fix below replaces hardcoding with runtime discovery.

Resolution precedence locked by these tests:
  1. Explicit `model_id=` constructor arg (back-compat for tests)
  2. QWEN_VLLM_MODEL / LOCAL_QWEN_MODEL env var (operator escape hatch)
  3. GET {endpoint}/v1/models first data[].id (preferred default)
  4. _FALLBACK_MODEL_ID (catalog QWEN_LOCAL_MODEL_ID) if all three above fail

Plan: docs/archive/windsurf/legacy-tree/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md § 7 (P1)
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.certification.safety.llm_judge_veto import LLMJudgeVeto  # noqa: E402
from agentic_core.config.model_catalog import QWEN_LOCAL_MODEL_ID  # noqa: E402


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Make sure no env-var drift between tests."""
    monkeypatch.delenv("LOCAL_QWEN_MODEL", raising=False)
    monkeypatch.delenv("QWEN_VLLM_MODEL", raising=False)
    monkeypatch.delenv("LOCAL_QWEN_ENDPOINT", raising=False)


class TestPrecedenceTier1Explicit:
    """Explicit constructor arg wins over everything."""

    def test_explicit_wins_over_env(self, monkeypatch):
        monkeypatch.setenv("LOCAL_QWEN_MODEL", "ignored/env-model")
        with patch.object(LLMJudgeVeto, "_discover_local_qwen_model",
                          return_value="ignored/discovered-model"):
            veto = LLMJudgeVeto(provider="local_qwen", model_id="my-explicit-model")
            resolved = veto.resolved_model_id
            source = veto.model_id_source
        assert resolved == "my-explicit-model"
        assert source == "explicit"

    def test_explicit_still_records_advertised_for_mismatch_detection(self):
        with patch.object(LLMJudgeVeto, "_discover_local_qwen_model",
                          return_value="Qwen/Qwen2.5-32B-Instruct-AWQ"):
            veto = LLMJudgeVeto(provider="local_qwen", model_id="explicit/non-served-model")
            resolved = veto.resolved_model_id
            advertised = veto.advertised_model_id
            source = veto.model_id_source
        assert resolved == "explicit/non-served-model"
        assert advertised == "Qwen/Qwen2.5-32B-Instruct-AWQ"
        assert source == "explicit"


class TestPrecedenceTier2EnvVar:
    """QWEN_VLLM_MODEL / LOCAL_QWEN_MODEL env vars override discovery + fallback."""

    def test_env_wins_over_discovery(self, monkeypatch):
        monkeypatch.setenv("QWEN_VLLM_MODEL", "Qwen/Qwen2.5-32B-Instruct-AWQ")
        with patch.object(LLMJudgeVeto, "_discover_local_qwen_model",
                          return_value="Qwen/different-model"):
            veto = LLMJudgeVeto(provider="local_qwen")
            # Trigger lazy resolution inside the patch scope
            resolved = veto.resolved_model_id
            source = veto.model_id_source
            advertised = veto.advertised_model_id
        assert resolved == "Qwen/Qwen2.5-32B-Instruct-AWQ"
        assert source == "env"
        assert advertised == "Qwen/different-model"

    def test_env_ignored_for_non_local_qwen_provider(self, monkeypatch):
        monkeypatch.setenv("QWEN_VLLM_MODEL", "should-not-apply")
        veto = LLMJudgeVeto(provider="anthropic_haiku")
        # Anthropic has its own hardcoded id path
        assert veto.resolved_model_id == "claude-3-haiku-20240307"
        assert veto.model_id_source == "anthropic_fixed"


class TestPrecedenceTier3Discovery:
    """/v1/models discovery is the preferred default for local_qwen."""

    def test_discovery_used_when_no_explicit_or_env(self):
        with patch.object(LLMJudgeVeto, "_discover_local_qwen_model",
                          return_value="Qwen/Qwen2.5-32B-Instruct-AWQ"):
            veto = LLMJudgeVeto(provider="local_qwen")
            resolved = veto.resolved_model_id
            advertised = veto.advertised_model_id
            source = veto.model_id_source
        assert resolved == "Qwen/Qwen2.5-32B-Instruct-AWQ"
        assert advertised == "Qwen/Qwen2.5-32B-Instruct-AWQ"
        assert source == "discovery"


class TestPrecedenceTier4Fallback:
    """Fallback fires only when all three above fail."""

    def test_fallback_when_discovery_returns_none(self):
        with patch.object(LLMJudgeVeto, "_discover_local_qwen_model",
                          return_value=None):
            veto = LLMJudgeVeto(provider="local_qwen")
            resolved = veto.resolved_model_id
            advertised = veto.advertised_model_id
            source = veto.model_id_source
        assert resolved == LLMJudgeVeto._FALLBACK_MODEL_ID
        assert resolved == QWEN_LOCAL_MODEL_ID
        assert advertised is None
        assert source == "fallback"


class TestNoHardcodingInDefault:
    """Regression guard: the default constructor must not silently return
    a hardcoded id when a real endpoint is serving something else."""

    def test_default_arg_is_none_not_hardcoded_string(self):
        import inspect
        sig = inspect.signature(LLMJudgeVeto.__init__)
        default = sig.parameters["model_id"].default
        assert default is None, (
            "LLMJudgeVeto.__init__ model_id default must be None. "
            "A hardcoded default model id produces "
            "poisoned attestations when the endpoint serves a different "
            "model. See 2026-05-01 Scenario A failure."
        )

    def test_fallback_model_id_constant_exists(self):
        # _FALLBACK_MODEL_ID must be clearly named so it's obvious what
        # it is and why. Accidental hardcoding elsewhere should be
        # greppable against this one symbol.
        assert hasattr(LLMJudgeVeto, "_FALLBACK_MODEL_ID")
        assert isinstance(LLMJudgeVeto._FALLBACK_MODEL_ID, str)


class TestRequestBodyUsesResolvedId:
    """The vLLM request body must use the RESOLVED model id, not the
    raw _model_id field (which is None before resolution)."""

    def test_call_local_qwen_uses_resolved_id(self, monkeypatch):
        monkeypatch.setenv("QWEN_VLLM_MODEL", "Qwen/Qwen2.5-32B-Instruct-AWQ")
        veto = LLMJudgeVeto(provider="local_qwen")
        captured = {}

        class _FakeResp:
            class choices_item:
                class message:
                    content = '{"verdict": "SAFE", "confidence": 0.9, "rationale": "ok"}'
            choices = [choices_item()]

        class _FakeClient:
            class chat:
                class completions:
                    @staticmethod
                    def create(**kwargs):
                        captured.update(kwargs)
                        return _FakeResp()

        fake_openai_module = type("F", (), {"OpenAI": lambda **kw: _FakeClient()})
        monkeypatch.setitem(sys.modules, "openai", fake_openai_module)

        veto._call_local_qwen("dummy prompt")
        assert captured.get("model") == "Qwen/Qwen2.5-32B-Instruct-AWQ", (
            f"vLLM request body should use the resolved model id, got "
            f"{captured.get('model')!r}"
        )
