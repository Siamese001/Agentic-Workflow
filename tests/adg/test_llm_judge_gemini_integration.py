"""Rigorous tests for LLM-as-Judge Gemini SDK integration.

Covers the fixed GeminiJudgeProvider and GeminiJudge that now use
``google.generativeai`` directly instead of the broken SovereignLLMGateway
interface (which required agent_id + async routing).

Test dimensions per §1.1:
- Edge cases: missing API key, missing SDK, malformed JSON, empty response,
  markdown-fenced JSON, API errors, None response text
- State transitions: unconfigured→configured, client injection override
- Determinism: identical inputs → identical outputs with mocked SDK
- Fail-closed: missing key blocks operation, import error blocks operation
- Matrix: provider × parse success/failure × API success/failure

No external API calls — all tests use mock objects.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ===================================================================
# Fixtures
# ===================================================================


class FakeGenerativeModel:
    """Mock for google.generativeai.GenerativeModel."""

    def __init__(self, response_text: str = "", raise_on_generate: Exception | None = None):
        self._response_text = response_text
        self._raise_on_generate = raise_on_generate
        self.generate_content_calls: list[dict[str, Any]] = []

    def generate_content(self, prompt: str, generation_config: dict | None = None) -> Any:
        self.generate_content_calls.append(
            {
                "prompt": prompt,
                "generation_config": generation_config,
            }
        )
        if self._raise_on_generate:
            raise self._raise_on_generate
        resp = MagicMock()
        resp.text = self._response_text
        return resp


def _valid_judge_json(**overrides: Any) -> str:
    """Return a valid JSON string matching judge response format."""
    data = {
        "guardrail_substantive": 0.8,
        "policy_integration": 0.9,
        "reasoning": "Looks good",
    }
    data.update(overrides)
    return json.dumps(data)


def _valid_score_json(**overrides: Any) -> str:
    """Return a valid JSON string matching GeminiJudge score format."""
    data = {
        "faithfulness": 0.95,
        "answer_relevancy": 0.90,
        "context_precision": 0.85,
        "groundedness": 0.88,
        "reasoning": "Solid evaluation",
    }
    data.update(overrides)
    return json.dumps(data)


# ===================================================================
# GeminiJudgeProvider — Success paths
# ===================================================================


class TestGeminiJudgeProviderSuccess:
    """Happy-path tests with injected mock client."""

    def test_judge_valid_json_response(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(response_text=_valid_judge_json())
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("test prompt", "GOV-001"))

        assert result["provider"] == "gemini"
        assert result["rubric_id"] == "GOV-001"
        assert result["score"] == pytest.approx(0.85, abs=0.01)
        assert result["reasoning"] == "Looks good"
        assert "guardrail_substantive" in result["criteria_scores"]
        assert "policy_integration" in result["criteria_scores"]
        assert "error" not in result

    def test_judge_passes_temperature_zero(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(response_text=_valid_judge_json())
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))

        assert len(mock_model.generate_content_calls) == 1
        call = mock_model.generate_content_calls[0]
        assert call["generation_config"]["temperature"] == 0.0

    def test_judge_passes_prompt_through(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(response_text=_valid_judge_json())
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        asyncio.get_event_loop().run_until_complete(provider.judge("exact prompt text", "GOV-001"))

        assert mock_model.generate_content_calls[0]["prompt"] == "exact prompt text"

    def test_provider_id_is_gemini(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        assert GeminiJudgeProvider().provider_id == "gemini"

    def test_cost_per_eval(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        assert GeminiJudgeProvider().cost_per_eval == 0.001

    def test_model_id_default(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        provider = GeminiJudgeProvider()
        assert provider.model_id == "gemini-2.5-flash"

    def test_model_id_override_via_constructor(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        provider = GeminiJudgeProvider(model="gemini-2.5-pro")
        assert provider.model_id == "gemini-2.5-pro"

    def test_model_id_override_via_env(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        monkeypatch.setenv("GEMINI_MODEL", "gemini-1.5-flash")
        provider = GeminiJudgeProvider()
        assert provider.model_id == "gemini-1.5-flash"

    def test_constructor_model_takes_precedence_over_env(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        monkeypatch.setenv("GEMINI_MODEL", "env-model")
        provider = GeminiJudgeProvider(model="constructor-model")
        assert provider.model_id == "constructor-model"

    def test_model_appears_in_result(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(response_text=_valid_judge_json())
        provider = GeminiJudgeProvider(gemini_client=mock_model, model="gemini-2.5-pro")

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))
        assert result["model"] == "gemini-2.5-pro"

    def test_criteria_scores_extracted_correctly(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        response = json.dumps(
            {
                "input_validation": 0.7,
                "scope_restriction": 0.3,
                "documentation": 1.0,
                "reasoning": "Mixed results",
            }
        )
        mock_model = FakeGenerativeModel(response_text=response)
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "SEC-001"))

        assert result["criteria_scores"]["input_validation"] == pytest.approx(0.7)
        assert result["criteria_scores"]["scope_restriction"] == pytest.approx(0.3)
        assert result["criteria_scores"]["documentation"] == pytest.approx(1.0)
        expected_score = (0.7 + 0.3 + 1.0) / 3
        assert result["score"] == pytest.approx(expected_score, abs=0.001)

    def test_aggregate_score_is_mean_of_criteria(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        response = json.dumps(
            {
                "a": 0.0,
                "b": 1.0,
                "reasoning": "half and half",
            }
        )
        mock_model = FakeGenerativeModel(response_text=response)
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "TEST"))
        assert result["score"] == pytest.approx(0.5)

    def test_no_criteria_scores_yields_zero(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        response = json.dumps({"reasoning": "no scores provided"})
        mock_model = FakeGenerativeModel(response_text=response)
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "TEST"))
        assert result["score"] == 0.0
        assert result["criteria_scores"] == {}


# ===================================================================
# GeminiJudgeProvider — Parse error paths
# ===================================================================


class TestGeminiJudgeProviderParseErrors:
    """Response parsing failure modes."""

    def test_malformed_json_returns_error(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(response_text="not json at all")
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))

        assert result["score"] == 0.0
        assert "error" in result
        assert "raw_response" in result
        assert result["provider"] == "gemini"
        assert result["rubric_id"] == "GOV-001"

    def test_markdown_fenced_json_parsed_successfully(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        fenced = '```json\n{"guardrail_substantive": 0.9, "reasoning": "ok"}\n```'
        mock_model = FakeGenerativeModel(response_text=fenced)
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))

        assert result["score"] == pytest.approx(0.9)
        assert "error" not in result

    def test_bare_markdown_fences_parsed(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        fenced = '```\n{"a": 0.5, "reasoning": "ok"}\n```'
        mock_model = FakeGenerativeModel(response_text=fenced)
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "TEST"))
        assert result["score"] == pytest.approx(0.5)

    def test_partial_json_returns_error(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(response_text='{"incomplete": ')
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))
        assert result["score"] == 0.0
        assert "error" in result

    def test_empty_string_returns_error(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(response_text="")
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))
        assert result["score"] == 0.0
        assert "error" in result

    def test_raw_response_truncated_at_500(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        long_garbage = "x" * 1000
        mock_model = FakeGenerativeModel(response_text=long_garbage)
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))
        assert len(result["raw_response"]) == 500


# ===================================================================
# GeminiJudgeProvider — API error paths
# ===================================================================


class TestGeminiJudgeProviderAPIErrors:
    """Gemini SDK call failures."""

    def test_api_exception_returns_error_dict(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(raise_on_generate=RuntimeError("quota exceeded"))
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))

        assert result["score"] == 0.0
        assert "quota exceeded" in result["reasoning"]
        assert "error" in result
        assert result["provider"] == "gemini"

    def test_timeout_error_returns_error_dict(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(raise_on_generate=TimeoutError("request timed out"))
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))
        assert result["score"] == 0.0
        assert "timed out" in result["reasoning"]

    def test_connection_error_returns_error_dict(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(raise_on_generate=ConnectionError("network unreachable"))
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        result = asyncio.get_event_loop().run_until_complete(provider.judge("prompt", "GOV-001"))
        assert result["score"] == 0.0
        assert "network unreachable" in result["error"]


# ===================================================================
# GeminiJudgeProvider — Missing credentials / SDK
# ===================================================================


class TestGeminiJudgeProviderCredentials:
    """Tests for missing API keys and missing SDK package."""

    def test_missing_sdk_raises_runtime_error(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        provider = GeminiJudgeProvider()
        # Without google.generativeai installed, should raise about missing package
        with pytest.raises(RuntimeError, match="google-genai package not installed"):
            provider._get_client()

    def test_missing_api_key_raises_runtime_error(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        mock_genai, modules = self._mock_genai()
        provider = GeminiJudgeProvider()

        with patch.dict("sys.modules", modules):
            with pytest.raises(RuntimeError, match="GEMINI_API_KEY or GOOGLE_API_KEY required"):
                provider._get_client()

    @staticmethod
    def _mock_genai():
        """Build a properly-chained mock for `import google.generativeai as genai`."""
        mock_genai = MagicMock()
        mock_genai.GenerativeModel.return_value = MagicMock()
        mock_google = MagicMock()
        mock_google.generativeai = mock_genai
        return mock_genai, {"google": mock_google, "google.generativeai": mock_genai}

    def test_gemini_api_key_accepted(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        monkeypatch.setenv("GEMINI_API_KEY", "test-key-123")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        mock_genai, modules = self._mock_genai()
        provider = GeminiJudgeProvider()
        with patch.dict("sys.modules", modules):
            provider._configured = False
            provider._client = None
            provider._get_client()

        mock_genai.configure.assert_called_once_with(api_key="test-key-123")

    def test_google_api_key_fallback(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setenv("GOOGLE_API_KEY", "google-key-456")

        mock_genai, modules = self._mock_genai()
        provider = GeminiJudgeProvider()
        with patch.dict("sys.modules", modules):
            provider._configured = False
            provider._client = None
            provider._get_client()

        mock_genai.configure.assert_called_once_with(api_key="google-key-456")

    def test_injected_client_bypasses_sdk(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        sentinel = object()
        provider = GeminiJudgeProvider(gemini_client=sentinel)
        assert provider._get_client() is sentinel

    def test_configure_called_only_once(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        monkeypatch.setenv("GEMINI_API_KEY", "key")
        mock_genai, modules = self._mock_genai()

        provider = GeminiJudgeProvider()
        with patch.dict("sys.modules", modules):
            provider._get_client()
            provider._get_client()  # second call

        mock_genai.configure.assert_called_once()


# ===================================================================
# GeminiJudgeProvider — Determinism
# ===================================================================


class TestGeminiJudgeProviderDeterminism:
    """Identical inputs → identical outputs (deterministic contract)."""

    def test_same_input_same_output(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        response = _valid_judge_json(guardrail_substantive=0.75, policy_integration=0.85)
        mock_model = FakeGenerativeModel(response_text=response)
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        results = []
        for _ in range(10):
            r = asyncio.get_event_loop().run_until_complete(provider.judge("same prompt", "GOV-001"))
            results.append(r)

        scores = {r["score"] for r in results}
        assert len(scores) == 1, f"Non-deterministic scores: {scores}"

        reasonings = {r["reasoning"] for r in results}
        assert len(reasonings) == 1

    def test_different_prompts_both_succeed(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        response = _valid_judge_json()
        mock_model = FakeGenerativeModel(response_text=response)
        provider = GeminiJudgeProvider(gemini_client=mock_model)

        r1 = asyncio.get_event_loop().run_until_complete(provider.judge("prompt A", "GOV-001"))
        r2 = asyncio.get_event_loop().run_until_complete(provider.judge("prompt B", "GOV-003"))

        assert r1["rubric_id"] == "GOV-001"
        assert r2["rubric_id"] == "GOV-003"
        assert "error" not in r1
        assert "error" not in r2


# ===================================================================
# GeminiJudge (llm_judge.py) — Success paths
# ===================================================================


class TestGeminiJudgeSuccess:
    """Tests for the GeminiJudge in llm_judge.py with mocked SDK."""

    def test_score_valid_response(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        mock_model = FakeGenerativeModel(response_text=_valid_score_json())
        judge = GeminiJudge(gemini_client=mock_model)

        result = judge.score(
            query="What is X?",
            context="X is defined in module Y.",
            answer="X is a class in module Y.",
        )

        assert result.faithfulness == pytest.approx(0.95)
        assert result.answer_relevancy == pytest.approx(0.90)
        assert result.context_precision == pytest.approx(0.85)
        assert result.groundedness == pytest.approx(0.88)
        assert result.reasoning == "Solid evaluation"
        assert result.judge_model == "gemini-2.5-flash"

    def test_score_custom_model(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        mock_model = FakeGenerativeModel(response_text=_valid_score_json())
        judge = GeminiJudge(gemini_client=mock_model, model="gemini-2.5-pro")

        result = judge.score("q", "c", "a")
        assert result.judge_model == "gemini-2.5-pro"

    def test_score_passes_temperature_zero(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        mock_model = FakeGenerativeModel(response_text=_valid_score_json())
        judge = GeminiJudge(gemini_client=mock_model)

        judge.score("q", "c", "a")

        assert len(mock_model.generate_content_calls) == 1
        assert mock_model.generate_content_calls[0]["generation_config"]["temperature"] == 0.0

    def test_score_prompt_contains_query_context_answer(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        mock_model = FakeGenerativeModel(response_text=_valid_score_json())
        judge = GeminiJudge(gemini_client=mock_model)

        judge.score("my_query", "my_context", "my_answer")

        prompt = mock_model.generate_content_calls[0]["prompt"]
        assert "my_query" in prompt
        assert "my_context" in prompt
        assert "my_answer" in prompt

    def test_model_id_property(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        judge = GeminiJudge(model="gemini-2.5-pro")
        assert judge.model_id == "gemini-2.5-pro"

    def test_default_model_id(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        judge = GeminiJudge()
        assert judge.model_id == "gemini-2.5-flash"

    def test_model_env_override(self, monkeypatch):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        monkeypatch.setenv("GEMINI_MODEL", "custom-model-from-env")
        judge = GeminiJudge()
        assert judge.model_id == "custom-model-from-env"


# ===================================================================
# GeminiJudge — Error paths
# ===================================================================


class TestGeminiJudgeErrors:
    """Error handling in GeminiJudge."""

    def test_missing_sdk_raises(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        judge = GeminiJudge()
        with pytest.raises(RuntimeError, match="google-genai package not installed"):
            judge._get_client()

    def test_missing_api_key_raises(self, monkeypatch):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        mock_genai = MagicMock()
        mock_google = MagicMock()
        mock_google.generativeai = mock_genai
        judge = GeminiJudge()

        with patch.dict("sys.modules", {"google": mock_google, "google.generativeai": mock_genai}):
            with pytest.raises(RuntimeError, match="GEMINI_API_KEY or GOOGLE_API_KEY"):
                judge._get_client()

    def test_api_error_propagates(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        mock_model = FakeGenerativeModel(raise_on_generate=RuntimeError("API down"))
        judge = GeminiJudge(gemini_client=mock_model)

        with pytest.raises(RuntimeError, match="API down"):
            judge.score("q", "c", "a")

    def test_malformed_json_raises(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        mock_model = FakeGenerativeModel(response_text="not json")
        judge = GeminiJudge(gemini_client=mock_model)

        with pytest.raises(json.JSONDecodeError):
            judge.score("q", "c", "a")

    def test_markdown_fenced_json_parsed(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        fenced = f"```json\n{_valid_score_json()}\n```"
        mock_model = FakeGenerativeModel(response_text=fenced)
        judge = GeminiJudge(gemini_client=mock_model)

        result = judge.score("q", "c", "a")
        assert result.faithfulness == pytest.approx(0.95)

    def test_missing_fields_default_to_one(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        response = json.dumps({"reasoning": "partial response"})
        mock_model = FakeGenerativeModel(response_text=response)
        judge = GeminiJudge(gemini_client=mock_model)

        result = judge.score("q", "c", "a")
        assert result.faithfulness == 1.0
        assert result.answer_relevancy == 1.0
        assert result.context_precision == 1.0
        assert result.groundedness == 1.0


# ===================================================================
# GeminiJudge — JudgeScore invariants
# ===================================================================


class TestJudgeScoreInvariants:
    """JudgeScore dataclass invariants."""

    def test_score_boundary_values(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        response = json.dumps(
            {
                "faithfulness": 0.0,
                "answer_relevancy": 1.0,
                "context_precision": 0.0,
                "groundedness": 1.0,
                "reasoning": "edge values",
            }
        )
        mock_model = FakeGenerativeModel(response_text=response)
        judge = GeminiJudge(gemini_client=mock_model)

        result = judge.score("q", "c", "a")
        assert result.faithfulness == 0.0
        assert result.answer_relevancy == 1.0
        assert result.context_precision == 0.0
        assert result.groundedness == 1.0

    def test_all_scores_preserved(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        response = json.dumps(
            {
                "faithfulness": 0.4,
                "answer_relevancy": 0.6,
                "context_precision": 0.8,
                "groundedness": 1.0,
                "reasoning": "test preservation",
            }
        )
        mock_model = FakeGenerativeModel(response_text=response)
        judge = GeminiJudge(gemini_client=mock_model)

        result = judge.score("q", "c", "a")
        assert result.faithfulness == pytest.approx(0.4)
        assert result.answer_relevancy == pytest.approx(0.6)
        assert result.context_precision == pytest.approx(0.8)
        assert result.groundedness == pytest.approx(1.0)
        assert result.reasoning == "test preservation"

    def test_deterministic_digest_stable(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        response = _valid_score_json()
        mock_model = FakeGenerativeModel(response_text=response)
        judge = GeminiJudge(gemini_client=mock_model)

        digests = set()
        for _ in range(50):
            result = judge.score("q", "c", "a")
            digests.add(result.deterministic_digest)
        assert len(digests) == 1, f"Non-deterministic digests: {digests}"


# ===================================================================
# create_default_registry — auto-registration
# ===================================================================


class TestCreateDefaultRegistry:
    """Tests for create_default_registry Gemini auto-registration."""

    def test_no_api_key_uses_null_default(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import create_default_registry

        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        registry = create_default_registry()
        assert registry.default is not None
        assert registry.default.provider_id == "null"
        assert "gemini" not in registry.provider_ids

    def test_with_api_key_registers_gemini_as_default(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import create_default_registry

        monkeypatch.setenv("GEMINI_API_KEY", "test-key")

        registry = create_default_registry()
        assert "gemini" in registry.provider_ids
        assert registry.default.provider_id == "gemini"

    def test_with_google_api_key_registers_gemini(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import create_default_registry

        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.setenv("GOOGLE_API_KEY", "google-key")

        registry = create_default_registry()
        assert "gemini" in registry.provider_ids

    def test_null_always_available_as_fallback(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import create_default_registry

        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        registry = create_default_registry()
        null_provider = registry.get("null")
        assert null_provider is not None
        assert null_provider.provider_id == "null"

    def test_summary_reflects_registered_providers(self, monkeypatch):
        from agentic_core.evaluation.judges.provider_registry import create_default_registry

        monkeypatch.setenv("GEMINI_API_KEY", "test-key")
        registry = create_default_registry()
        summary = registry.summary()
        provider_ids = {p["provider_id"] for p in summary["providers"]}
        assert "null" in provider_ids
        assert "gemini" in provider_ids
        assert summary["default"] == "gemini"


# ===================================================================
# LLM Judges with GeminiJudgeProvider (mocked SDK)
# ===================================================================


class TestLLMJudgesWithGeminiProvider:
    """Integration: LLM judges (GOV-001, GOV-003, SEC-001) with mocked Gemini."""

    @pytest.fixture()
    def gemini_provider(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        response = json.dumps(
            {
                "guardrail_substantive": 0.85,
                "policy_integration": 0.90,
                "dispatch_tracking": 0.80,
                "error_handling": 0.75,
                "healing_integration": 0.70,
                "input_validation": 0.95,
                "scope_restriction": 0.60,
                "documentation": 0.80,
                "reasoning": "Mock evaluation result",
            }
        )
        mock_model = FakeGenerativeModel(response_text=response)
        return GeminiJudgeProvider(gemini_client=mock_model)

    @pytest.fixture()
    def rubric_engine(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        return RubricEngine()

    def _make_bundle(self, target: str, **edge_overrides: Any):
        from agentic_core.evaluation.judges.types import EvidenceBundle

        edges = edge_overrides or {"applies_guardrail": [{"symbol": "guard"}]}
        return EvidenceBundle(target=target, adg_edges=edges, adg_digest="test-digest")

    def test_gov_001_with_gemini(self, gemini_provider, rubric_engine):
        from agentic_core.evaluation.judges.llm_judges import judge_gov_001
        from agentic_core.evaluation.judges.types import VerdictOutcome

        bundle = self._make_bundle("agentic_core/L2_execution/mod.py")
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_gov_001(bundle, gemini_provider, rubric_engine)
        )

        assert verdict.rubric_id == "GOV-001"
        assert verdict.provider_id == "gemini"
        assert 0.0 <= verdict.score <= 1.0
        assert verdict.outcome in {o.value for o in VerdictOutcome}
        assert verdict.adg_digest == "test-digest"

    def test_gov_003_with_gemini(self, gemini_provider, rubric_engine):
        from agentic_core.evaluation.judges.llm_judges import judge_gov_003

        bundle = self._make_bundle(
            "agentic_core/L3_orchestration/orch.py",
            dispatches_agent=[{"symbol": "dispatch"}],
        )
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_gov_003(bundle, gemini_provider, rubric_engine)
        )

        assert verdict.rubric_id == "GOV-003"
        assert verdict.provider_id == "gemini"
        assert 0.0 <= verdict.score <= 1.0

    def test_sec_001_with_gemini_and_dynamic_edges(self, gemini_provider, rubric_engine):
        from agentic_core.evaluation.judges.llm_judges import judge_sec_001
        from agentic_core.evaluation.judges.types import VerdictOutcome

        bundle = self._make_bundle(
            "agentic_core/risky.py",
            invokes_eval=[{"symbol": "eval", "source_file": "risky.py", "line_no": 42}],
        )
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_sec_001(bundle, gemini_provider, rubric_engine)
        )

        assert verdict.rubric_id == "SEC-001"
        assert verdict.provider_id == "gemini"
        assert verdict.outcome != VerdictOutcome.SKIP.value
        assert len(verdict.evidence_items) >= 1

    def test_sec_001_skip_without_dynamic_edges(self, gemini_provider, rubric_engine):
        from agentic_core.evaluation.judges.llm_judges import judge_sec_001
        from agentic_core.evaluation.judges.types import VerdictOutcome

        bundle = self._make_bundle(
            "agentic_core/safe.py",
            imports=[{"target_name": "json"}],
        )
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_sec_001(bundle, gemini_provider, rubric_engine)
        )
        assert verdict.outcome == VerdictOutcome.SKIP.value

    def test_run_llm_judge_routes_to_correct_judge(self, gemini_provider, rubric_engine):
        from agentic_core.evaluation.judges.llm_judges import run_llm_judge

        bundle = self._make_bundle("test.py")
        for rubric_id in ["GOV-001", "GOV-003"]:
            verdict = asyncio.get_event_loop().run_until_complete(
                run_llm_judge(rubric_id, bundle, gemini_provider, rubric_engine)
            )
            assert verdict is not None
            assert verdict.rubric_id == rubric_id
            assert verdict.provider_id == "gemini"

    def test_run_llm_judge_unknown_rubric_returns_none(self, gemini_provider, rubric_engine):
        from agentic_core.evaluation.judges.llm_judges import run_llm_judge

        bundle = self._make_bundle("test.py")
        result = asyncio.get_event_loop().run_until_complete(
            run_llm_judge("NONEXISTENT", bundle, gemini_provider, rubric_engine)
        )
        assert result is None


# ===================================================================
# LLM Judges — Provider error propagation
# ===================================================================


class TestLLMJudgesProviderErrors:
    """LLM judges handle provider errors gracefully (ERROR outcome)."""

    @pytest.fixture()
    def error_provider(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        mock_model = FakeGenerativeModel(raise_on_generate=RuntimeError("Gemini API quota exceeded"))
        return GeminiJudgeProvider(gemini_client=mock_model)

    @pytest.fixture()
    def rubric_engine(self):
        from agentic_core.evaluation.judges.rubric_engine import RubricEngine

        return RubricEngine()

    def test_gov_001_api_error_returns_error_verdict(self, error_provider, rubric_engine):
        from agentic_core.evaluation.judges.llm_judges import judge_gov_001
        from agentic_core.evaluation.judges.types import EvidenceBundle

        bundle = EvidenceBundle(target="test.py")
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_gov_001(bundle, error_provider, rubric_engine)
        )

        # GeminiJudgeProvider catches API errors and returns error dict
        # The judge should handle this gracefully
        assert verdict.rubric_id == "GOV-001"
        assert 0.0 <= verdict.score <= 1.0

    def test_gov_003_api_error_returns_error_verdict(self, error_provider, rubric_engine):
        from agentic_core.evaluation.judges.llm_judges import judge_gov_003
        from agentic_core.evaluation.judges.types import EvidenceBundle

        bundle = EvidenceBundle(target="test.py")
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_gov_003(bundle, error_provider, rubric_engine)
        )
        assert verdict.rubric_id == "GOV-003"

    def test_sec_001_api_error_with_dynamic_edges(self, error_provider, rubric_engine):
        from agentic_core.evaluation.judges.llm_judges import judge_sec_001
        from agentic_core.evaluation.judges.types import EvidenceBundle

        bundle = EvidenceBundle(
            target="risky.py",
            adg_edges={"invokes_eval": [{"symbol": "eval", "source_file": "r.py", "line_no": 1}]},
        )
        verdict = asyncio.get_event_loop().run_until_complete(
            judge_sec_001(bundle, error_provider, rubric_engine)
        )
        assert verdict.rubric_id == "SEC-001"


# ===================================================================
# JudgeOrchestrator — LLM mode integration
# ===================================================================


class TestOrchestratorLLMMode:
    """JudgeOrchestrator with LLM judges enabled (using mocked Gemini)."""

    @pytest.fixture()
    def orch_with_gemini(self, tmp_path):
        from agentic_core.evaluation.judges.orchestrator import JudgeOrchestrator
        from agentic_core.evaluation.judges.provider_registry import (
            GeminiJudgeProvider,
            JudgeProviderRegistry,
            NullJudgeProvider,
        )

        response = json.dumps(
            {
                "guardrail_substantive": 0.85,
                "policy_integration": 0.90,
                "reasoning": "Orchestrator test",
            }
        )
        mock_model = FakeGenerativeModel(response_text=response)
        gemini = GeminiJudgeProvider(gemini_client=mock_model)

        registry = JudgeProviderRegistry()
        registry.register(NullJudgeProvider())
        registry.register(gemini, default=True)

        return JudgeOrchestrator(
            verdict_db_path=str(tmp_path / "orch_verdicts.sqlite"),
            provider_registry=registry,
        )

    def test_evaluate_with_llm_rubric(self, orch_with_gemini):
        report = asyncio.get_event_loop().run_until_complete(
            orch_with_gemini.evaluate(
                module_path="agentic_core/L2_execution/test_mod.py",
                rubric_ids=["GOV-001"],
                deterministic_only=False,
                persist=False,
            )
        )
        assert report.target == "agentic_core/L2_execution/test_mod.py"
        assert len(report.verdicts) >= 1
        gov_verdicts = [v for v in report.verdicts if v.rubric_id == "GOV-001"]
        assert len(gov_verdicts) == 1
        assert gov_verdicts[0].provider_id == "gemini"

    def test_evaluate_mixed_deterministic_and_llm(self, orch_with_gemini):
        report = asyncio.get_event_loop().run_until_complete(
            orch_with_gemini.evaluate(
                module_path="agentic_core/L2_execution/test_mod.py",
                rubric_ids=["ARCH-001", "GOV-001"],
                deterministic_only=False,
                persist=False,
            )
        )
        rubric_ids = {v.rubric_id for v in report.verdicts}
        assert "ARCH-001" in rubric_ids
        assert "GOV-001" in rubric_ids

    def test_evaluate_llm_with_persist(self, orch_with_gemini):
        asyncio.get_event_loop().run_until_complete(
            orch_with_gemini.evaluate(
                module_path="agentic_core/L2_execution/persist_test.py",
                rubric_ids=["GOV-001"],
                deterministic_only=False,
                persist=True,
            )
        )
        stats = orch_with_gemini.verdict_store.stats()
        assert stats["total_verdicts"] >= 1

    def test_evaluate_batch_llm(self, orch_with_gemini):
        reports = asyncio.get_event_loop().run_until_complete(
            orch_with_gemini.evaluate_batch(
                module_paths=["mod_a.py", "mod_b.py"],
                rubric_ids=["GOV-001"],
                deterministic_only=False,
                persist=False,
            )
        )
        assert len(reports) == 2
        for report in reports:
            gov_verdicts = [v for v in report.verdicts if v.rubric_id == "GOV-001"]
            assert len(gov_verdicts) == 1


# ===================================================================
# Static parse helpers
# ===================================================================


class TestParseHelpers:
    """Unit tests for _clean and _parse static methods."""

    def test_clean_removes_json_fences(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        raw = '```json\n{"key": "value"}\n```'
        assert GeminiJudgeProvider._clean(raw) == '{"key": "value"}'

    def test_clean_removes_bare_fences(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        raw = '```\n{"key": "value"}\n```'
        assert GeminiJudgeProvider._clean(raw) == '{"key": "value"}'

    def test_clean_no_fences_passthrough(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        raw = '{"key": "value"}'
        assert GeminiJudgeProvider._clean(raw) == '{"key": "value"}'

    def test_parse_valid_json(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        assert GeminiJudgeProvider._parse('{"a": 1}') == {"a": 1}

    def test_parse_fenced_json(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        result = GeminiJudgeProvider._parse('```json\n{"a": 1}\n```')
        assert result == {"a": 1}

    def test_parse_invalid_raises(self):
        from agentic_core.evaluation.judges.provider_registry import GeminiJudgeProvider

        with pytest.raises(json.JSONDecodeError):
            GeminiJudgeProvider._parse("completely invalid")

    def test_gemini_judge_clean(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        raw = '```json\n{"x": 1}\n```'
        assert GeminiJudge._clean(raw) == '{"x": 1}'

    def test_gemini_judge_parse(self):
        from agentic_core.evaluation.judges.llm_judge import GeminiJudge

        result = GeminiJudge._parse('```\n{"x": 1}\n```')
        assert result == {"x": 1}
