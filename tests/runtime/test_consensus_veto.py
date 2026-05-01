"""Unit tests for ConsensusVeto aggregation logic.

Tests cover all 5 aggregation modes (unanimous, majority, no_majority,
unanimous_unsafe, incomplete) plus the is_available() env-probe and
the optional 4th Qwen juror activation.

Provider calls are mocked via the juror_call_impl dependency-injection
hook. No real SDK calls, no network, no API keys required.

Plan: .windsurf/plans/rtc-w2b-consensus-jury-rewrite-9a4c71.md § 4 R4.1
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import patch

import pytest

from tools.certification.safety.consensus_veto import (
    DEFAULT_JURORS,
    DEFAULT_TIMEOUT_MS_PER_JUROR,
    ConsensusVeto,
    JurorVerdict,
    hash_raw_response,
)
from tools.certification.safety.veto_protocol import VetoStatus


# ----------------------------------------------------------------------
# Fixtures — mock juror call implementations
# ----------------------------------------------------------------------


def _make_mock_impl(verdict_by_family: dict[str, str]):
    """Build a mock juror_call_impl that returns canned verdicts by family."""

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


# ----------------------------------------------------------------------
# Aggregation tests
# ----------------------------------------------------------------------


class TestAggregationUnanimous:
    def test_3_of_3_safe_is_unanimous_allow(self):
        impl = _make_mock_impl({
            "openai": "SAFE",
            "anthropic": "SAFE",
            "google": "SAFE",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2", "answer")

        assert result.status == VetoStatus.SAFE
        assert result.metadata["consensus_mode"] == "unanimous"
        assert result.metadata["safe_count"] == 3
        assert result.metadata["dissent_count"] == 0
        assert result.metadata["error_count"] == 0
        assert len(result.metadata["per_juror"]) == 3
        # avg confidence = 0.9
        assert 0.89 <= result.confidence <= 0.91


class TestAggregationMajority:
    def test_2_of_3_safe_is_majority_allow(self):
        impl = _make_mock_impl({
            "openai": "SAFE",
            "anthropic": "SAFE",
            "google": "UNSAFE_DIFFERENT_INTENT",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2", "answer")

        assert result.status == VetoStatus.SAFE
        assert result.metadata["consensus_mode"] == "majority"
        assert result.metadata["safe_count"] == 2
        assert result.metadata["dissent_count"] == 1
        # confidence averages ONLY the SAFE jurors
        assert 0.89 <= result.confidence <= 0.91

    def test_majority_records_dissent_in_per_juror(self):
        impl = _make_mock_impl({
            "openai": "SAFE",
            "anthropic": "SAFE",
            "google": "UNSAFE_POLICY_DRIFT",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        per_juror = result.metadata["per_juror"]
        dissenting = [j for j in per_juror if j["verdict"] != "SAFE"]
        assert len(dissenting) == 1
        assert dissenting[0]["family"] == "google"
        assert dissenting[0]["verdict"] == "UNSAFE_POLICY_DRIFT"


class TestAggregationNoMajority:
    def test_1_of_3_safe_blocks_with_no_majority(self):
        impl = _make_mock_impl({
            "openai": "SAFE",
            "anthropic": "UNSAFE_DIFFERENT_INTENT",
            "google": "UNSAFE_POLICY_DRIFT",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "no_majority"
        assert result.metadata["safe_count"] == 1
        assert "CONSENSUS_NO_MAJORITY" in result.rationale


class TestAggregationUnanimousUnsafe:
    def test_0_of_3_safe_is_unanimous_unsafe(self):
        impl = _make_mock_impl({
            "openai": "UNSAFE_DIFFERENT_INTENT",
            "anthropic": "UNSAFE_DIFFERENT_INTENT",
            "google": "UNSAFE_POLICY_DRIFT",
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "unanimous_unsafe"
        assert result.metadata["safe_count"] == 0
        assert "UNANIMOUS_NOT_SAFE" in result.rationale


class TestAggregationIncomplete:
    def test_any_error_triggers_incomplete_fail_closed(self):
        impl = _make_mock_impl({
            "openai": "SAFE",
            "anthropic": "SAFE",
            "google": "ERROR",  # one juror erred — fail closed
        })
        veto = ConsensusVeto(juror_call_impl=impl)
        result = veto.evaluate("q1", "q2")

        # 2/3 SAFE would normally allow, but ERROR forces fail-closed
        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "incomplete"
        assert result.metadata["error_count"] >= 1
        assert "CONSENSUS_INCOMPLETE" in result.rationale

    def test_all_errors_is_incomplete_not_unanimous_unsafe(self):
        impl = _make_mock_impl({
            "openai": "ERROR",
            "anthropic": "ERROR",
            "google": "ERROR",
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

        # All jurors raised — all captured as ERROR — incomplete mode
        assert result.status == VetoStatus.VETO
        assert result.metadata["consensus_mode"] == "incomplete"
        for j in result.metadata["per_juror"]:
            assert j["verdict"] == "ERROR"
            assert "mock transport failure" in j["rationale"]


# ----------------------------------------------------------------------
# Configuration tests
# ----------------------------------------------------------------------


class TestJurorComposition:
    def test_default_jurors_match_registry(self):
        # Sanity: DEFAULT_JURORS uses registry constants, not string literals
        families = [f for f, _ in DEFAULT_JURORS]
        assert families == ["openai", "anthropic", "google"]
        assert len(DEFAULT_JURORS) == 3

    def test_qwen_opt_in_adds_4th_juror(self):
        with patch.dict(os.environ, {"USE_CERT_JURY_QWEN": "1"}, clear=False):
            veto = ConsensusVeto(juror_call_impl=_make_mock_impl({}))
            assert len(veto._jurors) == 4
            families = [f for f, _ in veto._jurors]
            assert "local_qwen" in families

    def test_qwen_opt_in_ignored_when_explicit_jurors(self):
        with patch.dict(os.environ, {"USE_CERT_JURY_QWEN": "1"}, clear=False):
            veto = ConsensusVeto(
                jurors=(("openai", "gpt-5.4-mini"),),
                juror_call_impl=_make_mock_impl({"openai": "SAFE"}),
            )
            # Explicit jurors override env opt-in
            assert len(veto._jurors) == 1

    def test_4th_juror_raises_threshold_to_3(self):
        with patch.dict(os.environ, {"USE_CERT_JURY_QWEN": "1"}, clear=False):
            impl = _make_mock_impl({
                "openai": "SAFE",
                "anthropic": "SAFE",
                "google": "UNSAFE_DIFFERENT_INTENT",
                "local_qwen": "UNCERTAIN",
            })
            veto = ConsensusVeto(juror_call_impl=impl)
            result = veto.evaluate("q1", "q2")

            # UNCERTAIN counts as NOT SAFE → 2/4 SAFE → threshold is 3/4 → no majority
            # But UNCERTAIN also not ERROR, so we should land in no_majority, not incomplete
            assert result.status == VetoStatus.VETO
            assert result.metadata["consensus_mode"] == "no_majority"
            assert result.metadata["threshold"] == 3


# ----------------------------------------------------------------------
# is_available tests
# ----------------------------------------------------------------------


class TestIsAvailable:
    def test_available_when_all_keys_set(self):
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-test",
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GOOGLE_API_KEY": "g-test",
        }, clear=False):
            veto = ConsensusVeto()
            assert veto.is_available() is True

    def test_unavailable_missing_openai_key(self):
        env = {
            "ANTHROPIC_API_KEY": "sk-ant-test",
            "GOOGLE_API_KEY": "g-test",
        }
        with patch.dict(os.environ, env, clear=True):
            veto = ConsensusVeto()
            assert veto.is_available() is False

    def test_unavailable_missing_google_key(self):
        env = {
            "OPENAI_API_KEY": "sk-test",
            "ANTHROPIC_API_KEY": "sk-ant-test",
        }
        with patch.dict(os.environ, env, clear=True):
            veto = ConsensusVeto()
            assert veto.is_available() is False

    def test_local_qwen_juror_does_not_require_key(self):
        with patch.dict(os.environ, {}, clear=True):
            veto = ConsensusVeto(
                jurors=(("local_qwen", "Qwen/Qwen2.5-32B-Instruct-AWQ"),),
            )
            assert veto.is_available() is True


# ----------------------------------------------------------------------
# R2.1 foundation behavior (no impl wired)
# ----------------------------------------------------------------------


class TestR21FoundationState:
    def test_no_impl_fails_closed(self):
        """Without juror_call_impl, ConsensusVeto must fail-closed.

        R2.2 wires the real multi-provider impl. Until then, callers
        get an explicit ERROR — never an accidental allow.
        """
        veto = ConsensusVeto()
        result = veto.evaluate("q1", "q2")
        assert result.status == VetoStatus.ERROR
        assert "juror_call_impl" in result.rationale.lower()


# ----------------------------------------------------------------------
# Utility tests
# ----------------------------------------------------------------------


class TestHashRawResponse:
    def test_hash_of_non_empty_string(self):
        h = hash_raw_response("SAFE")
        assert len(h) == 64  # sha256 hex
        # sha256("SAFE") pre-computed
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
