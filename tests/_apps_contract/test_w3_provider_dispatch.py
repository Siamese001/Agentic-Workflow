"""E3 integration tests — apps_qna provider dispatch layer.

Plan: ``.windsurf/plans/bge-m3-deferred-scope-remaining-c4e7a1.md`` W3
"""

from __future__ import annotations

import os

import pytest

from apps_qna.engines.dispatch import DispatchResult, ProviderDispatcher, dispatch
from apps_qna.engines.dispatch.provider_dispatch import (
    ProviderName,
    QueryType,
    _classify_query,
    _resolve_provider,
)
from apps_qna.types.evidence_contracts import FinalEvidenceContract


# ---------------------------------------------------------------------------
# Query classification
# ---------------------------------------------------------------------------


class TestQueryClassification:
    def test_technical_question(self):
        assert _classify_query("How would you implement a distributed cache?") == QueryType.TECHNICAL

    def test_behavioral_question(self):
        assert _classify_query("Tell me about a time you resolved a conflict.") == QueryType.BEHAVIORAL

    def test_factual_question(self):
        assert _classify_query("What is the difference between SQL and NoSQL?") == QueryType.FACTUAL

    def test_open_ended_fallback(self):
        assert _classify_query("Prepare me for an interview at Google.") == QueryType.OPEN_ENDED

    def test_empty_question_classifies_open_ended(self):
        assert _classify_query("something something") == QueryType.OPEN_ENDED


# ---------------------------------------------------------------------------
# Provider resolution
# ---------------------------------------------------------------------------


class TestProviderResolution:
    def test_stub_when_no_keys(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("JUDGE_PROVIDER", raising=False)
        assert _resolve_provider(QueryType.FACTUAL) == ProviderName.STUB

    def test_anthropic_when_key_present(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("JUDGE_PROVIDER", raising=False)
        assert _resolve_provider(QueryType.FACTUAL) == ProviderName.ANTHROPIC

    def test_gemini_when_google_key_present(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
        monkeypatch.delenv("JUDGE_PROVIDER", raising=False)
        assert _resolve_provider(QueryType.BEHAVIORAL) == ProviderName.GEMINI

    def test_judge_provider_override_stub(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.setenv("JUDGE_PROVIDER", "stub")
        assert _resolve_provider(QueryType.FACTUAL) == ProviderName.STUB

    def test_anthropic_fallback_when_gemini_key_missing(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("JUDGE_PROVIDER", raising=False)
        assert _resolve_provider(QueryType.BEHAVIORAL) == ProviderName.ANTHROPIC


# ---------------------------------------------------------------------------
# ProviderDispatcher stub mode (no real LLM calls)
# ---------------------------------------------------------------------------


class TestProviderDispatcherStub:
    def test_empty_question_returns_stub(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        result = dispatch("")
        assert isinstance(result, DispatchResult)
        assert result.provider == ProviderName.STUB.value
        assert result.success is False

    def test_stub_dispatch_no_keys(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("JUDGE_PROVIDER", raising=False)
        result = dispatch("What is REST?", context="HTTP context", route_id="r-rest")
        assert result.provider == ProviderName.STUB.value
        assert result.success is False
        assert result.query_type == QueryType.FACTUAL.value
        assert any("route_id=r-rest" in e for e in result.evidence_refs)

    def test_dispatch_result_to_dict(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        result = dispatch("What is a microservice?")
        d = result.to_dict()
        assert "provider" in d
        assert "model" in d
        assert "query_type" in d
        assert "evidence_refs" in d
        assert "success" in d

    def test_dispatcher_class_and_module_fn_equivalent(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        q = "How do you handle technical debt?"
        r1 = ProviderDispatcher().dispatch(q)
        r2 = dispatch(q)
        assert r1.provider == r2.provider
        assert r1.query_type == r2.query_type


# ---------------------------------------------------------------------------
# FinalEvidenceContract — provider_dispatch sidecar
# ---------------------------------------------------------------------------


class TestFinalEvidenceContractDispatchField:
    def test_default_no_dispatch(self):
        c = FinalEvidenceContract()
        assert c.provider_dispatch is None
        d = c.to_dict()
        assert "provider_dispatch" not in d

    def test_with_dispatch_sidecar(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        result = dispatch("Tell me about microservices.", route_id="r-arch")
        c = FinalEvidenceContract(
            route_id="r-arch",
            query_text="Tell me about microservices.",
            provider_dispatch=result.to_dict(),
        )
        assert c.provider_dispatch is not None
        d = c.to_dict()
        assert "provider_dispatch" in d
        assert d["provider_dispatch"]["provider"] == ProviderName.STUB.value

    def test_evidence_refs_populated(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        result = dispatch("What is recursion?", route_id="r-cs-basics")
        assert len(result.evidence_refs) >= 2
        joined = " ".join(result.evidence_refs)
        assert "dispatch::v1" in joined
