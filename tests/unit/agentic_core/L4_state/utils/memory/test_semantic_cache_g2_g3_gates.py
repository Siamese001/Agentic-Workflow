"""Unit tests for G2 support-manifest validator and G3 live-signal bypass."""

from __future__ import annotations

import pytest

from agentic_core.L4_state.utils.memory import semantic_cache_manager as scm_mod


class TestG3LiveSignalBypass:
    @pytest.mark.parametrize(
        "query",
        [
            "What is the latest revenue figure?",
            "Show me the current system status",
            "What happened today with the outage?",
            "Events this week in the ledger",
            "Update the billing address",
            "Please delete record 42",
            "Create a new customer entry",
            "Cancel the pending order",
            "Issue refund for invoice 7",
            "What is the status of service alpha?",
            "Is the database up right now?",
            "As of today, what is the count?",
        ],
    )
    def test_live_signals_are_flagged(self, query: str) -> None:
        assert scm_mod._query_has_live_signal(query) is not None

    @pytest.mark.parametrize(
        "query",
        [
            "What is the refund policy for annual plans?",
            "Explain the difference between BGE-M3 and text-embedding-3",
            "Summarize the 2022 annual report",
            "How does SSL work",
        ],
    )
    def test_reuse_safe_queries_not_flagged(self, query: str) -> None:
        assert scm_mod._query_has_live_signal(query) is None

    def test_empty_and_short_inputs_pass(self) -> None:
        assert scm_mod._query_has_live_signal("") is None
        assert scm_mod._query_has_live_signal("x") is None

    def test_bypass_can_be_disabled_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SEMANTIC_CACHE_LIVE_SIGNAL_BYPASS", "0")
        assert scm_mod._live_signal_bypass_enabled() is False

    def test_bypass_default_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SEMANTIC_CACHE_LIVE_SIGNAL_BYPASS", raising=False)
        assert scm_mod._live_signal_bypass_enabled() is True


class TestG2EvidenceResolver:
    def setup_method(self) -> None:
        scm_mod.set_evidence_resolver(scm_mod._default_evidence_resolver)

    def teardown_method(self) -> None:
        scm_mod.set_evidence_resolver(scm_mod._default_evidence_resolver)

    def test_default_resolver_returns_true(self) -> None:
        assert scm_mod._default_evidence_resolver("any-id") is True

    def test_set_evidence_resolver_installs_callable(self) -> None:
        calls: list[str] = []

        def resolver(eid: str) -> bool:
            calls.append(eid)
            return eid != "missing"

        scm_mod.set_evidence_resolver(resolver)
        assert scm_mod._EVIDENCE_RESOLVER("present") is True
        assert scm_mod._EVIDENCE_RESOLVER("missing") is False
        assert calls == ["present", "missing"]

    def test_resolver_exceptions_treated_as_unresolvable(self) -> None:
        def raising_resolver(eid: str) -> bool:
            raise ValueError(f"backend unreachable: {eid}")

        scm_mod.set_evidence_resolver(raising_resolver)
        with pytest.raises(ValueError):
            scm_mod._EVIDENCE_RESOLVER("x")

    def test_validation_can_be_disabled_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SEMANTIC_CACHE_SUPPORT_MANIFEST_VALIDATION", "0")
        assert scm_mod._support_manifest_enabled() is False

    def test_validation_default_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SEMANTIC_CACHE_SUPPORT_MANIFEST_VALIDATION", raising=False)
        assert scm_mod._support_manifest_enabled() is True


class TestG1FlagSurface:
    def test_hybrid_default_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SEMANTIC_CACHE_HYBRID_ENABLED", raising=False)
        assert scm_mod._hybrid_enabled() is True

    def test_hybrid_disable_via_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SEMANTIC_CACHE_HYBRID_ENABLED", "0")
        assert scm_mod._hybrid_enabled() is False
