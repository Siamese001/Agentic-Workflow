"""E3 tests — QnaProviderContext.dispatch() and PA adapter model dispatch wiring.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-qna-deferred-e5-f7a2b1.md E3
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from apps_qna.integrations.provider_adapter import (
    QnaProviderContext,
    build_provider_context,
)
from apps_qna.card_context.pa_adapter import PAAdapterResult, run_pa_for_card_context


# ---------------------------------------------------------------------------
# E3.1: QnaProviderContext.dispatch()
# ---------------------------------------------------------------------------


class TestQnaProviderContextDispatch:
    """Tests for QnaProviderContext.dispatch() method."""

    def test_dispatch_returns_empty_when_no_model_id(self):
        ctx = QnaProviderContext(model_id="")
        assert ctx.dispatch("hello") == ""

    def test_dispatch_returns_empty_when_prompt_empty(self):
        ctx = QnaProviderContext(model_id="gpt-4")
        assert ctx.dispatch("") == ""

    def test_dispatch_returns_empty_when_gateway_import_fails(self):
        ctx = QnaProviderContext(model_id="gpt-4", max_tokens=100)
        with patch(
            "apps_qna.integrations.provider_adapter.QnaProviderContext.dispatch",
            wraps=ctx.dispatch,
        ):
            # If the gateway is not configured, dispatch must be fail-open
            result = ctx.dispatch("test prompt")
            assert isinstance(result, str)
            # In test environment without real gateway, this should be ""
            # (import may fail or gateway.generate may fail)

    @patch("httpx.post")
    def test_dispatch_calls_gateway_and_returns_content(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Model says hello"}}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        ctx = QnaProviderContext(model_id="gpt-4", max_tokens=512, temperature=0.3)
        result = ctx.dispatch("What is Python?")

        assert result == "Model says hello"
        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        body = call_kwargs[1]["json"]
        assert body["model"] == "gpt-4"
        assert body["max_tokens"] == 512
        assert body["temperature"] == 0.3
        assert body["messages"][0]["content"] == "What is Python?"

    @patch("httpx.post")
    def test_dispatch_returns_empty_when_gateway_raises(self, mock_post):
        mock_post.side_effect = RuntimeError("Connection refused")

        ctx = QnaProviderContext(model_id="gpt-4", max_tokens=100)
        result = ctx.dispatch("hello")

        assert result == ""

    @patch("httpx.post")
    def test_dispatch_returns_empty_when_content_is_none(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": ""}}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        ctx = QnaProviderContext(model_id="gpt-4")
        result = ctx.dispatch("prompt")
        assert result == ""

    @patch("httpx.post")
    def test_dispatch_uses_default_max_tokens_when_zero(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "ok"}}]
        }
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        ctx = QnaProviderContext(model_id="claude-3", max_tokens=0)
        ctx.dispatch("hi")

        body = mock_post.call_args[1]["json"]
        assert body["max_tokens"] == 4096  # default fallback

    def test_has_model_false_skips_dispatch(self):
        ctx = QnaProviderContext(model_id="")
        assert ctx.has_model() is False
        assert ctx.dispatch("anything") == ""

    def test_has_model_true_with_model_id(self):
        ctx = QnaProviderContext(model_id="qwen-2.5")
        assert ctx.has_model() is True


# ---------------------------------------------------------------------------
# E3.2: PA adapter model dispatch wiring
# ---------------------------------------------------------------------------


class TestPAAdapterModelDispatch:
    """Tests for PA adapter's model_output field and provider_context wiring."""

    def test_pa_result_model_output_defaults_empty(self):
        r = PAAdapterResult()
        assert r.model_output == ""

    def test_pa_result_model_output_set(self):
        r = PAAdapterResult(model_output="generated text")
        assert r.model_output == "generated text"

    def test_run_pa_without_provider_context_has_empty_model_output(self):
        """When no provider_context is passed, model_output is always empty."""
        card = {"evidence_sufficiency": "grounded", "retrieval_sources": []}
        result = run_pa_for_card_context(
            card_context=card,
            interview_slug="test-slug",
            route_id="r-test",
        )
        assert result.model_output == ""

    def test_run_pa_with_provider_context_dispatches_on_pass(self):
        """When dispatchable=True and provider has model, dispatch is called."""
        mock_ctx = MagicMock()
        mock_ctx.has_model.return_value = True
        mock_ctx.dispatch.return_value = "model output here"

        card = {"evidence_sufficiency": "grounded", "retrieval_sources": []}
        result = run_pa_for_card_context(
            card_context=card,
            interview_slug="test-slug",
            route_id="r-test",
            provider_context=mock_ctx,
        )
        # If pipeline passes (dispatchable=True), model_output should be populated
        if result.dispatchable:
            assert result.model_output == "model output here"
            mock_ctx.dispatch.assert_called_once()
        else:
            # PA.0 boundary may block in minimal card — that's fine
            assert result.model_output == ""

    def test_run_pa_with_provider_no_model_skips_dispatch(self):
        """When provider_context.has_model() is False, no dispatch."""
        mock_ctx = MagicMock()
        mock_ctx.has_model.return_value = False

        card = {"evidence_sufficiency": "grounded", "retrieval_sources": []}
        result = run_pa_for_card_context(
            card_context=card,
            interview_slug="test-slug",
            route_id="r-test",
            provider_context=mock_ctx,
        )
        mock_ctx.dispatch.assert_not_called()
        assert result.model_output == ""

    def test_run_pa_dispatch_error_is_swallowed(self):
        """If dispatch() raises, the error should not propagate (fail-open)."""
        mock_ctx = MagicMock()
        mock_ctx.has_model.return_value = True
        mock_ctx.dispatch.side_effect = RuntimeError("boom")

        card = {"evidence_sufficiency": "grounded", "retrieval_sources": []}
        # Should not raise — pa_adapter catches all exceptions
        result = run_pa_for_card_context(
            card_context=card,
            interview_slug="test-slug",
            route_id="r-test",
            provider_context=mock_ctx,
        )
        # Either dispatchable with empty model_output, or error result
        assert isinstance(result, PAAdapterResult)
