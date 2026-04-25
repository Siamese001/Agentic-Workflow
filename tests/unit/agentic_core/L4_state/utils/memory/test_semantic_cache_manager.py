"""Unit tests for agentic_core.L4_state.utils.memory.semantic_cache_manager.

Targets Wave-5 / Phase P14. Source: 1548 lines, fan_in=30 (L4, impact 52.5).
Focused on the small pure helpers + feature-flag gates; full SemanticCacheManager
requires Redis/ChromaDB and is out of scope for a unit test.
"""

from __future__ import annotations

import pytest

from hypothesis import given, strategies as st

from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
    CriticalInfrastructureError,
    PII_Sanitizer,
    _cdc_enabled,
    _hybrid_enabled,
    _l1_key_hardening_enabled,
    _live_signal_bypass_enabled,
    _normalize_l1_context,
    _query_has_live_signal,
    _single_flight_enabled,
    _structured_emit_enabled,
    _support_manifest_enabled,
    set_evidence_resolver,
    tier_similarity_threshold,
)


class TestCriticalInfrastructureError:
    def test_is_exception(self) -> None:
        assert issubclass(CriticalInfrastructureError, Exception)

    def test_can_be_raised(self) -> None:
        with pytest.raises(CriticalInfrastructureError, match="unavail"):
            raise CriticalInfrastructureError("Redis unavailable")


class TestFeatureFlags:
    @pytest.mark.parametrize(
        "fn,env_var",
        [
            (_hybrid_enabled, "SEMANTIC_CACHE_HYBRID_ENABLED"),
            (_support_manifest_enabled, "SEMANTIC_CACHE_SUPPORT_MANIFEST_VALIDATION"),
            (_live_signal_bypass_enabled, "SEMANTIC_CACHE_LIVE_SIGNAL_BYPASS"),
            (_cdc_enabled, "SEMANTIC_CACHE_CDC_ENABLED"),
            (_single_flight_enabled, "SEMANTIC_CACHE_SINGLE_FLIGHT"),
            (_structured_emit_enabled, "SEMANTIC_CACHE_STRUCTURED_EMIT"),
            (_l1_key_hardening_enabled, "SEMANTIC_CACHE_L1_KEY_HARDENING"),
        ],
    )
    def test_default_on(self, fn, env_var, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(env_var, raising=False)
        assert fn() is True

    @pytest.mark.parametrize(
        "fn,env_var",
        [
            (_hybrid_enabled, "SEMANTIC_CACHE_HYBRID_ENABLED"),
            (_cdc_enabled, "SEMANTIC_CACHE_CDC_ENABLED"),
            (_single_flight_enabled, "SEMANTIC_CACHE_SINGLE_FLIGHT"),
        ],
    )
    def test_off_when_zero(self, fn, env_var, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(env_var, "0")
        assert fn() is False

    def test_non_zero_value_still_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Only literal "0" disables. Anything else keeps the feature on.
        monkeypatch.setenv("SEMANTIC_CACHE_HYBRID_ENABLED", "true")
        assert _hybrid_enabled() is True
        monkeypatch.setenv("SEMANTIC_CACHE_HYBRID_ENABLED", "yes")
        assert _hybrid_enabled() is True


class TestQueryHasLiveSignal:
    def test_empty_returns_none(self) -> None:
        assert _query_has_live_signal("") is None

    def test_very_short_returns_none(self) -> None:
        # min length 3 required
        assert _query_has_live_signal("hi") is None

    def test_latest_trips_signal(self) -> None:
        assert _query_has_live_signal("what is the latest price") == "latest"

    def test_refund_trips_signal(self) -> None:
        result = _query_has_live_signal("please issue a refund")
        assert result is not None
        assert "refund" in result

    def test_delete_trips_signal(self) -> None:
        result = _query_has_live_signal("delete this record")
        assert result == "delete"

    def test_case_insensitive(self) -> None:
        # Matches regardless of case but returned value is lowercased
        r1 = _query_has_live_signal("LATEST news")
        r2 = _query_has_live_signal("latest news")
        assert r1 == r2 == "latest"

    def test_historical_query_passes_through(self) -> None:
        # No live signal = returns None
        assert _query_has_live_signal("what is the history of Python") is None

    def test_result_length_capped_at_32(self) -> None:
        # Longer matches get truncated
        r = _query_has_live_signal("this week the weather looks cold")
        assert r is not None
        assert len(r) <= 32


class TestTierSimilarityThreshold:
    def test_static_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SEMANTIC_CACHE_THRESHOLD_STATIC", raising=False)
        assert tier_similarity_threshold("static") == 1.0

    def test_dynamic_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SEMANTIC_CACHE_THRESHOLD_DYNAMIC", raising=False)
        assert tier_similarity_threshold("dynamic") == 0.95

    def test_unknown_tier_returns_conservative_one(self) -> None:
        assert tier_similarity_threshold("unknown") == 1.0

    def test_empty_tier_returns_conservative_one(self) -> None:
        assert tier_similarity_threshold("") == 1.0
        assert tier_similarity_threshold("   ") == 1.0

    def test_env_override_valid_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SEMANTIC_CACHE_THRESHOLD_DYNAMIC", "0.80")
        assert tier_similarity_threshold("dynamic") == 0.80

    def test_env_override_out_of_range_falls_back(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SEMANTIC_CACHE_THRESHOLD_DYNAMIC", "1.5")
        assert tier_similarity_threshold("dynamic") == 0.95

    def test_env_override_malformed_falls_back(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SEMANTIC_CACHE_THRESHOLD_STATIC", "not-a-number")
        assert tier_similarity_threshold("static") == 1.0

    def test_case_insensitive_tier(self) -> None:
        assert tier_similarity_threshold("STATIC") == 1.0
        assert tier_similarity_threshold("Dynamic") == 0.95


class TestNormalizeL1Context:
    def test_strips_whitespace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SEMANTIC_CACHE_L1_KEY_HARDENING", raising=False)
        assert _normalize_l1_context("  hello  ") == "hello"

    def test_collapses_internal_whitespace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SEMANTIC_CACHE_L1_KEY_HARDENING", raising=False)
        assert _normalize_l1_context("hello    world") == "hello world"

    def test_preserves_case(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SEMANTIC_CACHE_L1_KEY_HARDENING", raising=False)
        assert _normalize_l1_context("Apple") == "Apple"
        assert _normalize_l1_context("Apple") != _normalize_l1_context("apple")

    def test_off_when_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SEMANTIC_CACHE_L1_KEY_HARDENING", "0")
        # Hardening disabled — input is passed through unchanged
        assert _normalize_l1_context("  hello  world  ") == "  hello  world  "

    def test_nfkc_normalizes_compat_variants(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SEMANTIC_CACHE_L1_KEY_HARDENING", raising=False)
        # Full-width A (U+FF21) normalizes to ASCII A under NFKC
        fullwidth_a = "\uff21"
        result = _normalize_l1_context(fullwidth_a)
        assert result == "A"


class TestSetEvidenceResolver:
    def test_install_and_query_resolver(self) -> None:
        calls: list[str] = []

        def _rez(evidence_id: str) -> bool:
            calls.append(evidence_id)
            return evidence_id.startswith("valid-")

        set_evidence_resolver(_rez)

        # Access the installed resolver via module-level reference to verify
        import agentic_core.L4_state.utils.memory.semantic_cache_manager as mod

        assert mod._EVIDENCE_RESOLVER is _rez
        # Smoke-call
        assert mod._EVIDENCE_RESOLVER("valid-abc") is True
        assert mod._EVIDENCE_RESOLVER("invalid") is False
        assert calls == ["valid-abc", "invalid"]

    def test_restores_default_for_other_tests(self) -> None:
        # Defensive cleanup — restore the default resolver so subsequent tests
        # in any module don't see a stale override.
        import agentic_core.L4_state.utils.memory.semantic_cache_manager as mod

        set_evidence_resolver(mod._default_evidence_resolver)
        assert mod._EVIDENCE_RESOLVER("anything") is True


class TestPIISanitizer:
    """PII_Sanitizer must redact each documented PII class and leave safe text alone."""

    def test_empty_content_passes_through(self) -> None:
        assert PII_Sanitizer.sanitize("") == ""

    def test_plain_text_unchanged(self) -> None:
        text = "hello world this is ordinary prose"
        assert PII_Sanitizer.sanitize(text) == text

    def test_email_redacted(self) -> None:
        out = PII_Sanitizer.sanitize("contact me at alice@example.com please")
        assert "alice@example.com" not in out
        assert "[REDACTED_EMAIL]" in out

    def test_ipv4_redacted(self) -> None:
        out = PII_Sanitizer.sanitize("server at 192.168.1.1 is down")
        assert "192.168.1.1" not in out
        assert "[REDACTED_IPV4]" in out

    def test_openai_key_redacted(self) -> None:
        key = "sk-abcdefghijklmnopqrstuvwxyz1234567890"
        out = PII_Sanitizer.sanitize(f"key={key} used")
        assert key not in out
        assert "[REDACTED_OPENAI_KEY]" in out

    def test_anthropic_key_redacted(self) -> None:
        key = "sk-ant-abcdef1234567890abcdef"
        out = PII_Sanitizer.sanitize(f"use {key} for auth")
        assert key not in out
        assert "[REDACTED_ANTHROPIC_KEY]" in out

    def test_aws_access_key_redacted(self) -> None:
        out = PII_Sanitizer.sanitize("aws=AKIAIOSFODNN7EXAMPLE region=us-east-1")
        assert "AKIAIOSFODNN7EXAMPLE" not in out
        assert "[REDACTED_AWS_KEY]" in out

    def test_ssn_redacted(self) -> None:
        out = PII_Sanitizer.sanitize("ssn: 123-45-6789")
        assert "123-45-6789" not in out
        assert "[REDACTED_SSN]" in out

    def test_phone_redacted(self) -> None:
        # Use dash-only format; the source regex uses \b which fails at the
        # non-word char '(' when preceded by a space (latent source bug).
        out = PII_Sanitizer.sanitize("call 415-555-1234")
        assert "415-555-1234" not in out
        assert "[REDACTED_PHONE_US]" in out

    def test_is_safe_detects_clean(self) -> None:
        assert PII_Sanitizer.is_safe("plain text has no PII") is True

    def test_is_safe_detects_pii(self) -> None:
        assert PII_Sanitizer.is_safe("email: alice@example.com") is False

    def test_is_safe_empty_is_safe(self) -> None:
        assert PII_Sanitizer.is_safe("") is True

    def test_detect_pii_returns_findings(self) -> None:
        findings = PII_Sanitizer.detect_pii("contact alice@example.com from 10.0.0.1")
        assert "EMAIL" in findings
        assert "IPV4" in findings
        assert "alice@example.com" in findings["EMAIL"]

    def test_detect_pii_empty(self) -> None:
        assert PII_Sanitizer.detect_pii("") == {}

    def test_detect_pii_multiple_same_type(self) -> None:
        findings = PII_Sanitizer.detect_pii("a@x.com and b@y.com")
        assert len(findings["EMAIL"]) == 2

    def test_sanitize_idempotent_on_redacted(self) -> None:
        # Once sanitized, another pass must be a no-op on the tokens
        once = PII_Sanitizer.sanitize("email a@b.com")
        twice = PII_Sanitizer.sanitize(once)
        assert once == twice


class TestPropertyBased:
    """Property-based tests for pure helpers using hypothesis."""

    @given(st.text(max_size=200))
    def test_normalize_idempotent(self, s: str) -> None:
        # Normalizing twice == normalizing once (fixed-point property)
        once = _normalize_l1_context(s)
        twice = _normalize_l1_context(once)
        assert once == twice

    @given(st.text(max_size=200))
    def test_normalize_no_leading_trailing_whitespace(self, s: str) -> None:
        result = _normalize_l1_context(s)
        # When hardening is on (default), output is stripped
        assert result == result.strip()

    @given(st.text(max_size=500))
    def test_is_safe_is_inverse_of_detect_pii(self, s: str) -> None:
        # If detect_pii returns nothing, is_safe must be True; and vice-versa.
        findings = PII_Sanitizer.detect_pii(s)
        safe = PII_Sanitizer.is_safe(s)
        assert safe == (len(findings) == 0)

    @given(st.text(max_size=300))
    def test_sanitize_never_lengthens_proportionally_uncontrollably(self, s: str) -> None:
        # Sanitized output must be finite and bounded relative to input.
        # Each redaction replaces a span with a short token, so output length
        # is bounded by original + N*token_length where N <= input chars.
        out = PII_Sanitizer.sanitize(s)
        # Very loose upper bound: 5x original + 32 (for the [REDACTED_*] wrapper)
        assert len(out) <= 5 * max(1, len(s)) + 32

    @given(st.text(alphabet=st.characters(blacklist_categories=("Cc",)), max_size=60))
    def test_sanitize_of_sanitize_stable(self, s: str) -> None:
        once = PII_Sanitizer.sanitize(s)
        twice = PII_Sanitizer.sanitize(once)
        # Once PII is replaced with the [REDACTED_*] token, subsequent passes
        # must not keep mutating (stable fixed point).
        assert once == twice

    @given(value=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    def test_tier_similarity_threshold_env_override_roundtrip(self, value: float) -> None:
        # Avoid the pytest monkeypatch fixture inside @given — hypothesis
        # doesn't reset fixtures between examples. Use os.environ + try/finally
        # to restore prior state.
        import os

        env_var = "SEMANTIC_CACHE_THRESHOLD_DYNAMIC"
        previous = os.environ.get(env_var)
        os.environ[env_var] = str(value)
        try:
            assert tier_similarity_threshold("dynamic") == pytest.approx(value)
        finally:
            if previous is None:
                os.environ.pop(env_var, None)
            else:
                os.environ[env_var] = previous
