"""Tests for tools/adg/prompt_assembly/adapters/c0_bridge_adapter.py.

These tests verify:
- Abstain gate fires correctly for all four abstain conditions
- Valid contract produces a shaped EvidenceBundle + correct replay_extras
- evidence_hmac is preserved unchanged through the adapter
- Span sorting, truncation, and source-diversity rules apply correctly
- Low-coverage and weak-support cases are handled correctly
- No changes to contracts.py, evidence_shaper.py, or token_budgeter.py are required
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.types.c0_evidence_contract_types import (
    C0ContractViolation,
    C0EvidenceContract,
    CitedSpan,
)
from tools.adg.prompt_assembly.adapters.c0_bridge_adapter import (
    _MAX_TEXT_SNIPPET_CHARS,
    _MIN_RELEVANCE_SCORE,
    _SPAN_CAPS,
    _classify_source_type,
    _prune_and_sort_spans,
    _truncate_snippet,
    translate_contract,
)
from tools.adg.prompt_assembly.contracts import EvidenceBundle


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_span(
    span_id: str = "s1",
    source_ref: str = "snapshot.json",
    text_snippet: str = "Some evidence text",
    relevance_score: float = 0.80,
    chunk_hash: str = "hash001",
) -> CitedSpan:
    return CitedSpan(
        span_id=span_id,
        source_ref=source_ref,
        text_snippet=text_snippet,
        relevance_score=relevance_score,
        chunk_hash=chunk_hash,
    )


def _make_contract(
    spans: tuple = (),
    coverage: float = 0.75,
    abstain_hint: bool = False,
    retrieval_id: str = "ret-001",
    request_id: str = "req-001",
) -> C0EvidenceContract:
    hmac_val = C0EvidenceContract.compute_hmac(spans, request_id)
    return C0EvidenceContract(
        retrieval_id=retrieval_id,
        request_id=request_id,
        coverage_score=coverage,
        abstain_hint=abstain_hint,
        cited_spans=spans,
        evidence_hmac=hmac_val,
    )


# ---------------------------------------------------------------------------
# Abstain gate tests
# ---------------------------------------------------------------------------


class TestAbstainGate:
    def test_abstain_hint_true_returns_none(self) -> None:
        span = _make_span()
        contract = _make_contract(spans=(span,), coverage=0.80, abstain_hint=True)
        bundle, extras = translate_contract(contract, "executive_summary")
        assert bundle is None
        assert extras["abstain_hint"] is True
        assert extras["confidence_band"] == "LOW"

    def test_coverage_below_threshold_returns_none(self) -> None:
        span = _make_span(relevance_score=0.85)
        contract = _make_contract(spans=(span,), coverage=0.20)
        bundle, extras = translate_contract(contract, "executive_summary")
        assert bundle is None
        assert extras["abstain_hint"] is True

    def test_empty_spans_returns_none(self) -> None:
        contract = _make_contract(spans=(), coverage=0.80, abstain_hint=True)
        bundle, extras = translate_contract(contract, "executive_summary")
        assert bundle is None
        assert extras["abstain_hint"] is True

    def test_all_spans_below_min_relevance_returns_none(self) -> None:
        low_span1 = _make_span(span_id="s1", relevance_score=0.05)
        low_span2 = _make_span(span_id="s2", relevance_score=0.08)
        contract = _make_contract(spans=(low_span1, low_span2), coverage=0.75)
        bundle, extras = translate_contract(contract, "executive_summary")
        assert bundle is None
        assert extras["abstain_hint"] is True

    def test_abstain_extras_preserve_hmac(self) -> None:
        span = _make_span()
        contract = _make_contract(spans=(span,), coverage=0.20)
        _, extras = translate_contract(contract, "executive_summary")
        assert extras["evidence_hmac"] == contract.evidence_hmac

    def test_abstain_extras_preserve_retrieval_and_request_ids(self) -> None:
        span = _make_span()
        contract = _make_contract(spans=(span,), coverage=0.20, retrieval_id="ret-xyz", request_id="req-abc")
        _, extras = translate_contract(contract, "executive_summary")
        assert extras["retrieval_id"] == "ret-xyz"
        assert extras["request_id"] == "req-abc"


# ---------------------------------------------------------------------------
# Valid contract → shaped bundle tests
# ---------------------------------------------------------------------------


class TestValidContractTranslation:
    def _valid_contract(self, n_spans: int = 3, coverage: float = 0.75) -> C0EvidenceContract:
        spans = tuple(
            _make_span(
                span_id=f"s{i}",
                source_ref=f"report_{i}.json",
                relevance_score=0.90 - i * 0.05,
                chunk_hash=f"hash{i:03d}",
            )
            for i in range(n_spans)
        )
        return _make_contract(spans=spans, coverage=coverage)

    def test_returns_evidence_bundle_on_valid_contract(self) -> None:
        contract = self._valid_contract()
        bundle, extras = translate_contract(contract, "executive_summary")
        assert isinstance(bundle, EvidenceBundle)
        assert extras["abstain_hint"] is False

    def test_bundle_coverage_matches_contract(self) -> None:
        contract = self._valid_contract(coverage=0.82)
        bundle, _ = translate_contract(contract, "executive_summary")
        assert bundle is not None
        assert bundle.coverage_score == pytest.approx(0.82)

    def test_replay_extras_hmac_preserved_unchanged(self) -> None:
        contract = self._valid_contract()
        _, extras = translate_contract(contract, "executive_summary")
        assert extras["evidence_hmac"] == contract.evidence_hmac

    def test_replay_extras_retrieval_id_preserved(self) -> None:
        contract = self._valid_contract()
        _, extras = translate_contract(contract, "executive_summary")
        assert extras["retrieval_id"] == contract.retrieval_id
        assert extras["request_id"] == contract.request_id

    def test_replay_extras_packet_type_set(self) -> None:
        contract = self._valid_contract()
        _, extras = translate_contract(contract, "executive_summary")
        assert extras["packet_type"] == "executive_summary"

    def test_replay_extras_confidence_band_high(self) -> None:
        contract = self._valid_contract(coverage=0.85)
        _, extras = translate_contract(contract, "executive_summary")
        assert extras["confidence_band"] == "HIGH"

    def test_replay_extras_confidence_band_medium(self) -> None:
        contract = self._valid_contract(coverage=0.65)
        _, extras = translate_contract(contract, "executive_summary")
        assert extras["confidence_band"] == "MEDIUM"

    def test_replay_extras_confidence_band_low(self) -> None:
        span = _make_span(relevance_score=0.50)
        contract = _make_contract(spans=(span,), coverage=0.40)
        bundle, extras = translate_contract(contract, "executive_summary")
        assert bundle is not None
        assert extras["confidence_band"] == "LOW"


# ---------------------------------------------------------------------------
# Span rules: sorting, truncation, diversity, caps
# ---------------------------------------------------------------------------


class TestSpanRules:
    def test_spans_sorted_by_relevance_descending(self) -> None:
        spans = (
            _make_span(span_id="s3", relevance_score=0.50, chunk_hash="h3"),
            _make_span(span_id="s1", relevance_score=0.95, chunk_hash="h1"),
            _make_span(span_id="s2", relevance_score=0.70, chunk_hash="h2"),
        )
        result = _prune_and_sort_spans(spans, "executive_summary")
        scores = [s.relevance_score for s in result]
        assert scores == sorted(scores, reverse=True)

    def test_low_relevance_spans_discarded(self) -> None:
        spans = (
            _make_span(span_id="s1", relevance_score=0.80, chunk_hash="h1"),
            _make_span(span_id="s2", relevance_score=0.05, chunk_hash="h2"),
            _make_span(span_id="s3", relevance_score=0.09, chunk_hash="h3"),
        )
        result = _prune_and_sort_spans(spans, "executive_summary")
        assert all(s.relevance_score >= _MIN_RELEVANCE_SCORE for s in result)
        assert len(result) == 1

    def test_source_diversity_cap_applied(self) -> None:
        spans = tuple(
            _make_span(
                span_id=f"s{i}", source_ref="same_source.json", chunk_hash=f"h{i}", relevance_score=0.80
            )
            for i in range(6)
        )
        result = _prune_and_sort_spans(spans, "executive_summary")
        assert len(result) <= 3

    def test_span_cap_executive_summary(self) -> None:
        spans = tuple(
            _make_span(span_id=f"s{i}", source_ref=f"src{i}.json", chunk_hash=f"h{i}", relevance_score=0.80)
            for i in range(20)
        )
        result = _prune_and_sort_spans(spans, "executive_summary")
        assert len(result) <= _SPAN_CAPS["executive_summary"]

    def test_span_cap_graph_path_explanation(self) -> None:
        spans = tuple(
            _make_span(span_id=f"s{i}", source_ref=f"src{i}.json", chunk_hash=f"h{i}", relevance_score=0.80)
            for i in range(25)
        )
        result = _prune_and_sort_spans(spans, "graph_path_explanation")
        assert len(result) <= _SPAN_CAPS["graph_path_explanation"]

    def test_snippet_truncated_at_word_boundary(self) -> None:
        long_text = "word " * 200  # 1000 chars
        result = _truncate_snippet(long_text)
        assert len(result) <= _MAX_TEXT_SNIPPET_CHARS
        assert not result.endswith(" ")  # trailing space trimmed or word boundary respected

    def test_snippet_under_limit_unchanged(self) -> None:
        short_text = "Short evidence."
        assert _truncate_snippet(short_text) == short_text


# ---------------------------------------------------------------------------
# Source type classification
# ---------------------------------------------------------------------------


class TestClassifySourceType:
    def test_sqlite_extension(self) -> None:
        assert _classify_source_type("artifacts/adg/adg_indexed.sqlite") == "sqlite"

    def test_ratchet_ref(self) -> None:
        assert _classify_source_type("artifacts/ratchet/defect_ceiling.json") == "ratchet"

    def test_json_report_fallback(self) -> None:
        assert _classify_source_type("snapshot_report.json") == "json_report"

    def test_infra_view(self) -> None:
        assert _classify_source_type("infra/wiring_map.json") == "infra_view"

    def test_structural(self) -> None:
        assert _classify_source_type("ast_module_scan.json") == "structural"

    def test_graph_db(self) -> None:
        assert _classify_source_type("adg_graph_db.sqlite") == "sqlite"  # sqlite wins over graph_db


# ---------------------------------------------------------------------------
# Low-coverage and weak-support semantics
# ---------------------------------------------------------------------------


class TestCoverageAndWeakSupport:
    def test_low_coverage_produces_weak_support(self) -> None:
        span = _make_span(span_id="s1", relevance_score=0.75)
        contract = _make_contract(spans=(span,), coverage=0.45)
        bundle, _ = translate_contract(contract, "executive_summary")
        assert bundle is not None
        assert bundle.weak_support is True

    def test_high_coverage_no_weak_support(self) -> None:
        spans = tuple(
            _make_span(span_id=f"s{i}", source_ref=f"src{i}.json", chunk_hash=f"h{i}", relevance_score=0.85)
            for i in range(3)
        )
        contract = _make_contract(spans=spans, coverage=0.85)
        bundle, _ = translate_contract(contract, "executive_summary")
        assert bundle is not None
        assert bundle.weak_support is False

    def test_single_span_produces_weak_support(self) -> None:
        span = _make_span(relevance_score=0.85)
        contract = _make_contract(spans=(span,), coverage=0.75)
        bundle, _ = translate_contract(contract, "executive_summary")
        assert bundle is not None
        assert bundle.weak_support is True

    def test_bundle_coverage_score_is_contract_authoritative(self) -> None:
        spans = tuple(
            _make_span(span_id=f"s{i}", source_ref=f"src{i}.json", chunk_hash=f"h{i}", relevance_score=0.85)
            for i in range(3)
        )
        contract = _make_contract(spans=spans, coverage=0.67)
        bundle, _ = translate_contract(contract, "executive_summary")
        assert bundle is not None
        assert bundle.coverage_score == pytest.approx(0.67)


# ---------------------------------------------------------------------------
# Contract validation forwarded correctly
# ---------------------------------------------------------------------------


class TestContractValidation:
    def test_invalid_contract_raises(self) -> None:
        invalid = C0EvidenceContract(
            retrieval_id="",
            request_id="req",
            coverage_score=0.8,
            abstain_hint=False,
            cited_spans=(_make_span(),),
            evidence_hmac="abc",
        )
        with pytest.raises(C0ContractViolation):
            translate_contract(invalid, "executive_summary")
