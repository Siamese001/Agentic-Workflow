"""Tests for consensus_juror_clients — env resolution + model-override
rejection + safe reject-reason wrapping.

No real SDK calls. The dispatch functions (_call_gemini, _call_anthropic,
_call_openai) are NOT exercised here; their behavior is covered by
integration tests that require API keys.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from tools.certification.safety.consensus_juror_clients import (
    api_key_presence,
    make_real_juror_call_impl,
    resolve_api_key,
    resolve_model_id,
)
from tools.certification.safety.rtc_req_056_panel import (
    ANTHROPIC_JUROR,
    GEMINI_JUROR,
    OPENAI_JUROR,
    RejectReason,
)


# ---------------------------------------------------------------------------
# resolve_api_key
# ---------------------------------------------------------------------------


class TestResolveApiKey:
    def test_returns_primary_when_set(self):
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "g-test"}, clear=True):
            assert resolve_api_key(GEMINI_JUROR) == "g-test"

    def test_returns_deprecated_alias_when_primary_missing(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "g-legacy"}, clear=True):
            assert resolve_api_key(GEMINI_JUROR) == "g-legacy"

    def test_prefers_primary_over_deprecated_alias(self):
        with patch.dict(os.environ, {
            "GOOGLE_API_KEY": "canonical", "GEMINI_API_KEY": "legacy"
        }, clear=True):
            assert resolve_api_key(GEMINI_JUROR) == "canonical"

    def test_returns_none_when_nothing_set(self):
        with patch.dict(os.environ, {}, clear=True):
            assert resolve_api_key(GEMINI_JUROR) is None
            assert resolve_api_key(ANTHROPIC_JUROR) is None
            assert resolve_api_key(OPENAI_JUROR) is None

    def test_api_key_presence_boolean(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-x"}, clear=True):
            assert api_key_presence(OPENAI_JUROR) is True
            assert api_key_presence(ANTHROPIC_JUROR) is False


# ---------------------------------------------------------------------------
# resolve_model_id — accepted overrides + rejection
# ---------------------------------------------------------------------------


class TestResolveModelId:
    def test_no_override_returns_registry_pin(self):
        with patch.dict(os.environ, {}, clear=True):
            model, reject = resolve_model_id(GEMINI_JUROR)
            assert model == GEMINI_JUROR.model_id
            assert reject is None

    def test_empty_override_treated_as_unset(self):
        with patch.dict(os.environ, {"GOOGLE_AI_MODEL": ""}, clear=True):
            model, reject = resolve_model_id(GEMINI_JUROR)
            assert model == GEMINI_JUROR.model_id
            assert reject is None

        with patch.dict(os.environ, {"GEMINI_MODEL": ""}, clear=True):
            model, reject = resolve_model_id(GEMINI_JUROR)
            assert model == GEMINI_JUROR.model_id
            assert reject is None

    def test_matching_override_accepted_via_legacy_gemini_env(self):
        with patch.dict(os.environ, {
            "GEMINI_MODEL": "gemini-3.1-pro-preview"
        }, clear=True):
            model, reject = resolve_model_id(GEMINI_JUROR)
            assert model == "gemini-3.1-pro-preview"
            assert reject is None

    def test_matching_override_accepted_via_google_ai_env(self):
        with patch.dict(os.environ, {
            "GOOGLE_AI_MODEL": "gemini-3.1-pro-preview"
        }, clear=True):
            model, reject = resolve_model_id(GEMINI_JUROR)
            assert model == "gemini-3.1-pro-preview"
            assert reject is None

    def test_google_ai_model_override_precedes_legacy_gemini(self):
        with patch.dict(os.environ, {
            "GOOGLE_AI_MODEL": "gemini-3.1-pro-preview",
            "GEMINI_MODEL": "gemini-2.5-flash",
        }, clear=True):
            model, reject = resolve_model_id(GEMINI_JUROR)
            assert model == "gemini-3.1-pro-preview"
            assert reject is None

    def test_wrong_gemini_override_rejected(self):
        with patch.dict(os.environ, {
            "GEMINI_MODEL": "gemini-2.5-flash"
        }, clear=True):
            model, reject = resolve_model_id(GEMINI_JUROR)
            assert reject == RejectReason.REJECT_UNREGISTERED_MODEL

    def test_wrong_anthropic_override_rejected(self):
        with patch.dict(os.environ, {
            "ANTHROPIC_MODEL": "claude-3-haiku-20240307"
        }, clear=True):
            model, reject = resolve_model_id(ANTHROPIC_JUROR)
            assert reject == RejectReason.REJECT_UNREGISTERED_MODEL

    def test_wrong_openai_override_rejected(self):
        with patch.dict(os.environ, {"OPENAI_MODEL": "gpt-4o"}, clear=True):
            model, reject = resolve_model_id(OPENAI_JUROR)
            assert reject == RejectReason.REJECT_UNREGISTERED_MODEL


# ---------------------------------------------------------------------------
# make_real_juror_call_impl — guardrails before SDK dispatch
# ---------------------------------------------------------------------------


class TestJurorCallImplGuardrails:
    def test_unregistered_family_returns_error_verdict(self):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk", "ANTHROPIC_API_KEY": "sk",
            "GEMINI_API_KEY": "g"
        }, clear=True):
            impl = make_real_juror_call_impl()
            verdict = impl("cohere", "command-r", "q1", "q2", None, None)
            assert verdict.verdict == "ERROR"
            assert RejectReason.REJECT_UNREGISTERED_PROVIDER in verdict.rationale

    def test_wrong_model_for_registered_family_returns_error(self):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk", "ANTHROPIC_API_KEY": "sk",
            "GEMINI_API_KEY": "g"
        }, clear=True):
            impl = make_real_juror_call_impl()
            verdict = impl(
                "google_gemini", "gemini-2.5-flash", "q1", "q2", None, None
            )
            assert verdict.verdict == "ERROR"
            assert RejectReason.REJECT_UNREGISTERED_MODEL in verdict.rationale

    def test_missing_api_key_returns_infrastructure_gap(self):
        with patch.dict(os.environ, {}, clear=True):
            impl = make_real_juror_call_impl()
            verdict = impl(
                "google_gemini", GEMINI_JUROR.model_id,
                "q1", "q2", None, None,
            )
            assert verdict.verdict == "ERROR"
            assert RejectReason.INFRASTRUCTURE_GAP_MISSING_KEY in verdict.rationale

    def test_env_override_pointing_to_wrong_model_rejected(self):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk", "ANTHROPIC_API_KEY": "sk",
            "GEMINI_API_KEY": "g",
            "OPENAI_MODEL": "gpt-4o",  # unregistered override
        }, clear=True):
            impl = make_real_juror_call_impl()
            verdict = impl(
                "openai", OPENAI_JUROR.model_id, "q1", "q2", None, None
            )
            assert verdict.verdict == "ERROR"
            assert RejectReason.REJECT_UNREGISTERED_MODEL in verdict.rationale

    def test_no_secret_values_ever_logged_or_returned(self):
        # Use a uniquely identifiable fake key; ensure it never appears
        # in the JurorVerdict's rationale when a gate rejects.
        secret = "super-secret-should-not-appear"
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": secret, "ANTHROPIC_API_KEY": "sk",
            "GEMINI_API_KEY": "g",
        }, clear=True):
            impl = make_real_juror_call_impl()
            # Trigger a rejection path (wrong model)
            verdict = impl(
                "openai", "gpt-4o", "q1", "q2", None, None
            )
            assert secret not in verdict.rationale
            assert secret not in verdict.juror_id
            assert secret not in verdict.model_id
