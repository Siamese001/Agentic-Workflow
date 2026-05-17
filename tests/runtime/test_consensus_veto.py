"""Unit tests for ConsensusVeto under the RTC-REQ-056 all_required_safe rule.

Tests cover:
  - Aggregation: only 3/3 SAFE allows; any other outcome fail-closed.
  - Juror families sourced from the panel registry
    (google_gemini / anthropic / openai).
  - is_available() env-probe honors aliases (GOOGLE_API_KEY, etc).
  - JurorVerdict serialization shape.
  - R2.1-foundation fail-closed when no juror_call_impl is wired.

Provider calls are mocked; no network, no SDK, no keys required.
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import patch

import pytest

from tools.certification.safety.consensus_veto import (
    DEFAULT_JURORS,
    ConsensusVeto,
    JurorVerdict,
    hash_raw_response,
)
from tools.certification.safety.rtc_req_056_panel import (
    ANTHROPIC_JUROR,
    GEMINI_JUROR,
    OPENAI_JUROR,
    REQUIRED_JURORS,
    REQUIRED_JUROR_COUNT,
)
from tools.certification.safety.veto_protocol import VetoStatus


# ---------------------------------------------------------------------------
# Fixtures — mock juror call implementations
# ---------------------------------------------------------------------------


def _make_mock_impl(verdict_by_family: dict[str, str]):
    """Build a mock juror_call_impl returning canned verdicts by family."""

    def _impl(
        family: str,
        model_id: str,
        query: str,
        cached_query: str,
        cached_answer: str | None,
        context: dict[str, Any] | None,
    ) -> JurorVerdict:
        v = verdict_by_family.get(family, "UNCERTAIN")
        return JurorVerdict(
            juror_id=f"{family}_{model_id}",
            family=family,
            model_id=model_id,
            verdict=v,
            confidence=0.9 if v == "SAFE" else 0.3,
            rationale=f"mock verdict={v}",
            latency_ms=100.0,
            raw_response_sha256=hash_raw_response(f"raw-{family}-{v}"),
        )

    return _impl


# ---------------------------------------------------------------------------
# Aggregation tests — all_required_safe
# ---------------------------------------------------------------------------


class TestAllRequiredSafeAllows:
    def test_3_of_3_safe_is_allow(self):
        impl = _make_mock_impl({
            "google_gemini": "SAFE",
            "anthropic": "SAFE",
            "openai": "SAFE",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2", "answer")

        assert result.status == VetoStatus.SAFE
        assert result.metadata["consensus_mode"] == "unanimous"
        assert result.metadata["safe_count"] == 3
        assert result.metadata["dissent_count"] == 0
        assert result.metadata["error_count"] == 0
        assert result.metadata["quorum_rule"] == "all_required_safe"
        assert len(result.metadata["per_juror"]) == 3


class TestAllRequiredSafeBlocks:
    def test_2_of_3_safe_blocks_under_all_required_safe(self):
        # Previously 2/3 would allow under majority rule; now BLOCKS
        impl = _make_mock_impl({
            "google_gemini": "SAFE",
            "anthropic": "SAFE",
            "openai": "UNSAFE_DIFFERENT_INTENT",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "quorum_fail"
        assert result.metadata["safe_count"] == 2
        assert result.metadata["unsafe_count"] == 1

    def test_1_of_3_safe_blocks(self):
        impl = _make_mock_impl({
            "google_gemini": "SAFE",
            "anthropic": "UNSAFE_DIFFERENT_INTENT",
            "openai": "UNSAFE_POLICY_DRIFT",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "quorum_fail"
        assert result.metadata["safe_count"] == 1

    def test_0_of_3_safe_is_unanimous_unsafe(self):
        impl = _make_mock_impl({
            "google_gemini": "UNSAFE_DIFFERENT_INTENT",
            "anthropic": "UNSAFE_DIFFERENT_INTENT",
            "openai": "UNSAFE_POLICY_DRIFT",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "unanimous_unsafe"
        assert result.metadata["safe_count"] == 0
        assert "QUORUM_FAIL" in result.rationale

    def test_unknown_verdict_blocks_even_with_2_safe(self):
        impl = _make_mock_impl({
            "google_gemini": "SAFE",
            "anthropic": "SAFE",
            "openai": "UNCERTAIN",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "quorum_fail_unknown"
        assert result.metadata["unknown_count"] == 1


class TestFailClosedOnError:
    def test_any_error_triggers_incomplete_fail_closed(self):
        impl = _make_mock_impl({
            "google_gemini": "SAFE",
            "anthropic": "SAFE",
            "openai": "ERROR",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "incomplete"
        assert result.metadata["error_count"] >= 1
        assert "CONSENSUS_INCOMPLETE" in result.rationale

    def test_all_errors_is_incomplete(self):
        impl = _make_mock_impl({
            "google_gemini": "ERROR",
            "anthropic": "ERROR",
            "openai": "ERROR",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "incomplete"

    def test_juror_exception_captured_as_error(self):
        def _raising_impl(*args, **kwargs):
            raise RuntimeError("mock transport failure")

        veto = ConsensusVeto(juror_call_impl=_raising_impl)
        result = veto.evaluate("q1", "q2")

        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "incomplete"
        for j in result.metadata["per_juror"]:
            assert j["verdict"] == "ERROR"
            assert "mock transport failure" in j["rationale"]


# ---------------------------------------------------------------------------
# Default juror fleet sourced from panel registry
# ---------------------------------------------------------------------------


class TestDefaultJurorsFromRegistry:
    def test_default_jurors_match_panel_registry(self):
        families = [f for f, _ in DEFAULT_JURORS]
        assert len(DEFAULT_JURORS) == REQUIRED_JUROR_COUNT == 3
        assert "google_gemini" in families
        assert "anthropic" in families
        assert "openai" in families

    def test_default_models_match_registry_pins(self):
        models = dict(DEFAULT_JURORS)
        assert models["google_gemini"] == GEMINI_JUROR.model_id
        assert models["anthropic"] == ANTHROPIC_JUROR.model_id
        assert models["openai"] == OPENAI_JUROR.model_id

    def test_registered_model_pins_are_2026_05_01_fleet(self):
        assert GEMINI_JUROR.model_id == "gemini-3.1-pro-preview"
        assert ANTHROPIC_JUROR.model_id == "claude-sonnet-4-6"
        assert OPENAI_JUROR.model_id == "gpt-5.4-mini"


# ---------------------------------------------------------------------------
# is_available tests
# ---------------------------------------------------------------------------


class TestIsAvailable:
    def test_available_when_google_api_key_set(self):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-test",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GOOGLE_API_KEY": "g-test",
        }, clear=False):
            veto = ConsensusVeto()
            assert veto.is_available() is True

    def test_available_with_deprecated_gemini_env_alias(self):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-test",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GEMINI_API_KEY": "g-test",
        }, clear=False):
            veto = ConsensusVeto()
            assert veto.is_available() is True

    def test_unavailable_missing_openai_key(self):
        env = {
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GEMINI_API_KEY": "g-test",
        }
        with patch.dict(os.environ, env, clear=True):
            veto = ConsensusVeto()
            assert veto.is_available() is False

    def test_unavailable_missing_gemini_and_google_keys(self):
        env = {
            "OPENAI_API_KEY": "sk-test",
            "ANTHROPIC_API_KEY": "sk-ant-test",
        }
        with patch.dict(os.environ, env, clear=True):
            veto = ConsensusVeto()
            assert veto.is_available() is False


# ---------------------------------------------------------------------------
# R2.1 foundation behavior
# ---------------------------------------------------------------------------


class TestR21FoundationState:
    def test_no_impl_fails_closed(self):
        veto = ConsensusVeto()
        result = veto.evaluate("q1", "q2")
        assert result.status == VetoStatus.ERROR
        assert "juror_call_impl" in result.rationale.lower()


# ---------------------------------------------------------------------------
# Utility tests
# ---------------------------------------------------------------------------


class TestHashRawResponse:
    def test_hash_of_non_empty_string(self):
        h = hash_raw_response("SAFE")
        assert len(h) == 64
        assert h == "10a87133a313ecf05f5be2f63a927977b5347ec0578bb5d21fcab2f86695d49c"

    def test_hash_of_empty_string_is_empty(self):
        assert hash_raw_response("") == ""


class TestJurorVerdictSerialization:
    def test_to_dict_has_all_fields(self):
        v = JurorVerdict(
            juror_id="openai_gpt-5.4-mini",
            family="openai",
            model_id="gpt-5.4-mini",
            verdict="SAFE",
            confidence=0.92,
            rationale="looks safe",
            latency_ms=1240.0,
            raw_response_sha256="abc123",
        )
        d = v.to_dict()
        assert d["juror_id"] == "openai_gpt-5.4-mini"
        assert d["family"] == "openai"
        assert d["model_id"] == "gpt-5.4-mini"
        assert d["verdict"] == "SAFE"
        assert d["confidence"] == 0.92
        assert d["latency_ms"] == 1240.0
        assert d["raw_response_sha256"] == "abc123"
