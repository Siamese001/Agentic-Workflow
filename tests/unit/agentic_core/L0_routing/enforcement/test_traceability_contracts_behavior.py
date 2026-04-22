"""Behavioral tests for agentic_core.L0_routing.enforcement.traceability_contracts.

Covers V15 P4 (Immutable Traceability) runtime contracts:
  - generate_trace_id (§15.5) — CC3AL1-{8 uppercase hex} format
  - build_error_signature (§5.2) — deterministic hash, fail-closed wrap
  - pin_policy_config / verify_policy_config_unchanged (§4.2) — SHA-256 pin
  - verify_manifest_hash (§1.6) — AST snippet integrity
  - build_plan_provenance (§6.7) — SHA-256 of plan content
  - build_retrieval_query / build_retrieved_chunk (§6.5) — RAG chain
  - validate_retrieval_set (§6.5) — all-scored + descending order
  - validate_citation_chain (§6.5) — bundle/query hash consistency
  - build_cognitive_diff_bundle (§15.2)
  - enforce_advisory_only (§6.9) — ADVISORY pass-through, CONTROL rejection

L0 ×2.0 criticality. Module ranked in top-10 by fan-in (8).
"""

from __future__ import annotations

import hashlib

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def tc():
    return pytest.importorskip(
        "agentic_core.L0_routing.enforcement.traceability_contracts",
    )


@pytest.fixture(scope="module")
def tt():
    return pytest.importorskip("agentic_core.L0_routing.types.traceability_types")


EXPECTED_EXPORTS = [
    "AdvisoryViolationError",
    "CognitiveDiffError",
    "ErrorSignatureError",
    "ManifestHashError",
    "PlanProvenanceError",
    "PolicyConfigPinError",
    "RAGChainError",
    "TraceIDFormatError",
    "build_cognitive_diff_bundle",
    "build_error_signature",
    "build_plan_provenance",
    "build_retrieval_query",
    "build_retrieved_chunk",
    "enforce_advisory_only",
    "generate_trace_id",
    "pin_policy_config",
    "validate_citation_chain",
    "validate_retrieval_set",
    "verify_manifest_hash",
    "verify_policy_config_unchanged",
]


# --------------------------------------------------------------------------- #
# Public surface                                                              #
# --------------------------------------------------------------------------- #


class TestPublicSurface:
    @pytest.mark.parametrize("name", EXPECTED_EXPORTS)
    def test_export_present(self, tc, name):
        assert name in tc.__all__, f"{name} missing from __all__"

    def test_all_has_no_extras(self, tc):
        assert set(tc.__all__) == set(EXPECTED_EXPORTS)


# --------------------------------------------------------------------------- #
# generate_trace_id (§15.5)                                                   #
# --------------------------------------------------------------------------- #


class TestGenerateTraceId:
    def test_valid_uppercase(self, tc):
        result = tc.generate_trace_id("ABCDEF12")
        assert result == "CC3AL1-ABCDEF12"

    def test_lowercase_normalized_to_uppercase(self, tc):
        result = tc.generate_trace_id("abcdef12")
        assert result == "CC3AL1-ABCDEF12"

    def test_mixed_case_normalized(self, tc):
        result = tc.generate_trace_id("AbCdEf12")
        assert result == "CC3AL1-ABCDEF12"

    @pytest.mark.parametrize("bad_len", ["", "ABC", "ABCDEF1", "ABCDEF123", "X" * 16])
    def test_wrong_length_raises(self, tc, bad_len):
        with pytest.raises(tc.TraceIDFormatError, match=r"must be exactly 8 chars"):
            tc.generate_trace_id(bad_len)

    def test_error_is_exception_subclass(self, tc):
        assert issubclass(tc.TraceIDFormatError, Exception)


# --------------------------------------------------------------------------- #
# build_error_signature (§5.2)                                                #
# --------------------------------------------------------------------------- #


class TestBuildErrorSignature:
    def test_construction_returns_error_signature(self, tc, tt):
        sig = tc.build_error_signature("TypeError", "node-1", 42)
        assert isinstance(sig, tt.ErrorSignature)
        assert sig.error_type == "TypeError"
        assert sig.target_node_id == "node-1"
        assert sig.time_bucket == 42

    def test_signature_hash_deterministic(self, tc):
        a = tc.build_error_signature("E", "n", 1)
        b = tc.build_error_signature("E", "n", 1)
        assert a.signature_hash == b.signature_hash

    def test_signature_hash_differs_with_error_type(self, tc):
        a = tc.build_error_signature("E1", "n", 1)
        b = tc.build_error_signature("E2", "n", 1)
        assert a.signature_hash != b.signature_hash

    def test_signature_hash_differs_with_node(self, tc):
        a = tc.build_error_signature("E", "n1", 1)
        b = tc.build_error_signature("E", "n2", 1)
        assert a.signature_hash != b.signature_hash


# --------------------------------------------------------------------------- #
# pin_policy_config / verify_policy_config_unchanged (§4.2)                   #
# --------------------------------------------------------------------------- #


class TestPolicyConfigPin:
    def test_pin_returns_sha256_hash(self, tc, tt):
        payload = b"policy-config-v1"
        pin = tc.pin_policy_config("wave-1", payload, 0)
        assert isinstance(pin, tt.PolicyConfigPin)
        assert pin.policy_config_hash == hashlib.sha256(payload).hexdigest()
        assert pin.wave_id == "wave-1"
        assert pin.semantic_clock_tick == 0

    def test_verify_unchanged_returns_true(self, tc):
        payload = b"policy-config"
        pin = tc.pin_policy_config("w", payload, 1)
        assert tc.verify_policy_config_unchanged(pin, payload) is True

    def test_verify_mutated_raises(self, tc):
        pin = tc.pin_policy_config("w", b"original", 0)
        with pytest.raises(tc.PolicyConfigPinError, match=r"mutated during wave 'w'"):
            tc.verify_policy_config_unchanged(pin, b"modified")

    def test_verify_empty_bytes_mismatch(self, tc):
        pin = tc.pin_policy_config("w", b"non-empty", 0)
        with pytest.raises(tc.PolicyConfigPinError):
            tc.verify_policy_config_unchanged(pin, b"")


# --------------------------------------------------------------------------- #
# verify_manifest_hash (§1.6)                                                 #
# --------------------------------------------------------------------------- #


class TestVerifyManifestHash:
    def test_match_returns_true(self, tc):
        snippet = "def foo(): pass"
        expected = hashlib.sha256(snippet.encode("utf-8")).hexdigest()
        assert tc.verify_manifest_hash(snippet, expected) is True

    def test_mismatch_raises(self, tc):
        with pytest.raises(tc.ManifestHashError, match=r"manifest_hash mismatch"):
            tc.verify_manifest_hash("code-A", "wrong-hash")

    def test_error_reports_expected_and_actual(self, tc):
        with pytest.raises(tc.ManifestHashError) as exc_info:
            tc.verify_manifest_hash("x", "deadbeef")
        assert "deadbeef" in str(exc_info.value)
        # Expected hash is also embedded
        expected = hashlib.sha256(b"x").hexdigest()
        assert expected in str(exc_info.value)


# --------------------------------------------------------------------------- #
# build_plan_provenance (§6.7)                                                #
# --------------------------------------------------------------------------- #


class TestBuildPlanProvenance:
    def test_returns_plan_provenance_with_hash(self, tc, tt):
        pp = tc.build_plan_provenance("t", "plan-1", "node-A", 0, "plan content")
        assert isinstance(pp, tt.PlanProvenance)
        assert pp.plan_hash == hashlib.sha256(b"plan content").hexdigest()

    def test_hash_differs_with_content(self, tc):
        a = tc.build_plan_provenance("t", "p", "n", 0, "one")
        b = tc.build_plan_provenance("t", "p", "n", 0, "two")
        assert a.plan_hash != b.plan_hash


# --------------------------------------------------------------------------- #
# build_retrieval_query + build_retrieved_chunk (§6.5)                        #
# --------------------------------------------------------------------------- #


class TestRAGBuilders:
    def test_retrieval_query_hash_is_sha256_of_query(self, tc, tt):
        q = tc.build_retrieval_query("t", "search me", "agent-A", 0)
        assert isinstance(q, tt.RetrievalQuery)
        assert q.query_hash == hashlib.sha256(b"search me").hexdigest()
        assert q.source_agent == "agent-A"

    def test_retrieved_chunk_content_hash(self, tc, tt):
        c = tc.build_retrieved_chunk("c1", "doc", "body text", "loc", "qh")
        assert isinstance(c, tt.RetrievedChunk)
        assert c.content_hash == hashlib.sha256(b"body text").hexdigest()
        assert c.retrieval_query_hash == "qh"

    def test_chunks_with_same_content_share_hash(self, tc):
        a = tc.build_retrieved_chunk("c1", "d1", "same", "l", "qh")
        b = tc.build_retrieved_chunk("c2", "d2", "same", "l", "qh")
        assert a.content_hash == b.content_hash


# --------------------------------------------------------------------------- #
# validate_retrieval_set (§6.5)                                               #
# --------------------------------------------------------------------------- #


def _mk_chunk(tc, chunk_id: str, qh: str = "qh"):
    return tc.build_retrieved_chunk(chunk_id, "src", f"content-{chunk_id}", "loc", qh)


class TestValidateRetrievalSet:
    def test_valid_set_returns_true(self, tc, tt):
        chunks = (
            _mk_chunk(tc, "c1"),
            _mk_chunk(tc, "c2"),
            _mk_chunk(tc, "c3"),
        )
        scores = (
            tt.RerankScore(chunk_id="c1", score=0.9, rank=1),
            tt.RerankScore(chunk_id="c2", score=0.5, rank=2),
            tt.RerankScore(chunk_id="c3", score=0.1, rank=3),
        )
        assert tc.validate_retrieval_set(chunks, scores) is True

    def test_empty_chunks_raises(self, tc):
        with pytest.raises(tc.RAGChainError, match=r"at least one chunk"):
            tc.validate_retrieval_set((), ())

    def test_missing_score_raises(self, tc, tt):
        chunks = (_mk_chunk(tc, "c1"), _mk_chunk(tc, "c2"))
        scores = (tt.RerankScore(chunk_id="c1", score=0.5, rank=1),)  # c2 unscored
        with pytest.raises(tc.RAGChainError, match=r"without rerank scores"):
            tc.validate_retrieval_set(chunks, scores)

    def test_non_descending_order_raises(self, tc, tt):
        chunks = (_mk_chunk(tc, "c1"), _mk_chunk(tc, "c2"))
        scores = (
            tt.RerankScore(chunk_id="c1", score=0.2, rank=1),
            tt.RerankScore(chunk_id="c2", score=0.9, rank=2),  # ascending — invalid
        )
        with pytest.raises(tc.RAGChainError, match=r"not in descending order"):
            tc.validate_retrieval_set(chunks, scores)

    def test_equal_adjacent_scores_allowed(self, tc, tt):
        # Non-strict descending (ties allowed; only strict < is rejected)
        chunks = (_mk_chunk(tc, "c1"), _mk_chunk(tc, "c2"))
        scores = (
            tt.RerankScore(chunk_id="c1", score=0.5, rank=1),
            tt.RerankScore(chunk_id="c2", score=0.5, rank=2),
        )
        assert tc.validate_retrieval_set(chunks, scores) is True


# --------------------------------------------------------------------------- #
# validate_citation_chain (§6.5)                                              #
# --------------------------------------------------------------------------- #


def _mk_citation(tt, chunk_id: str, retrieval_hash: str):
    return tt.CitationEntry(
        citation_id=f"cite-{chunk_id}",
        chunk_id=chunk_id,
        source_id="src",
        location="loc",
        retrieval_hash=retrieval_hash,
    )


class TestValidateCitationChain:
    def _build_valid(self, tc, tt):
        query = tc.build_retrieval_query("t", "q", "a", 0)
        chunks = (_mk_chunk(tc, "c1", query.query_hash), _mk_chunk(tc, "c2", query.query_hash))
        bundle = tt.CitationBundle(
            trace_id="t",
            bundle_id="b1",
            citations=(
                _mk_citation(tt, "c1", query.query_hash),
                _mk_citation(tt, "c2", query.query_hash),
            ),
            retrieval_query_hash=query.query_hash,
            bundle_hash="bh",
        )
        return query, chunks, bundle

    def test_valid_chain_returns_true(self, tc, tt):
        query, chunks, bundle = self._build_valid(tc, tt)
        assert tc.validate_citation_chain(bundle, chunks, query) is True

    def test_bundle_query_hash_mismatch_raises(self, tc, tt):
        query, chunks, bundle = self._build_valid(tc, tt)
        bad_bundle = tt.CitationBundle(
            trace_id="t", bundle_id="b1",
            citations=bundle.citations,
            retrieval_query_hash="wrong-hash",
            bundle_hash="bh",
        )
        with pytest.raises(tc.RAGChainError, match=r"CitationBundle retrieval_query_hash mismatch"):
            tc.validate_citation_chain(bad_bundle, chunks, query)

    def test_uncited_chunk_raises(self, tc, tt):
        query, chunks, bundle = self._build_valid(tc, tt)
        # Remove citation for c2
        trimmed_bundle = tt.CitationBundle(
            trace_id="t", bundle_id="b1",
            citations=(bundle.citations[0],),  # only c1
            retrieval_query_hash=query.query_hash,
            bundle_hash="bh",
        )
        with pytest.raises(tc.RAGChainError, match=r"Chunks without citations"):
            tc.validate_citation_chain(trimmed_bundle, chunks, query)

    def test_phantom_citation_raises(self, tc, tt):
        query, chunks, bundle = self._build_valid(tc, tt)
        phantom_bundle = tt.CitationBundle(
            trace_id="t", bundle_id="b1",
            citations=bundle.citations + (_mk_citation(tt, "c99", query.query_hash),),
            retrieval_query_hash=query.query_hash,
            bundle_hash="bh",
        )
        with pytest.raises(tc.RAGChainError, match=r"non-existent chunks"):
            tc.validate_citation_chain(phantom_bundle, chunks, query)

    def test_per_citation_hash_mismatch_raises(self, tc, tt):
        query, chunks, bundle = self._build_valid(tc, tt)
        # Citation with wrong retrieval_hash
        bad_bundle = tt.CitationBundle(
            trace_id="t", bundle_id="b1",
            citations=(
                _mk_citation(tt, "c1", query.query_hash),
                _mk_citation(tt, "c2", "wrong-hash"),
            ),
            retrieval_query_hash=query.query_hash,
            bundle_hash="bh",
        )
        with pytest.raises(tc.RAGChainError, match=r"retrieval_hash does not match"):
            tc.validate_citation_chain(bad_bundle, chunks, query)


# --------------------------------------------------------------------------- #
# build_cognitive_diff_bundle (§15.2)                                         #
# --------------------------------------------------------------------------- #


class TestBuildCognitiveDiffBundle:
    def test_construction(self, tc, tt):
        b = tc.build_cognitive_diff_bundle(
            "t", "inc-1", "intended", "actual", "diff", 0,
        )
        assert isinstance(b, tt.CognitiveDiffBundle)
        assert b.incident_id == "inc-1"
        assert b.diff_summary == "diff"


# --------------------------------------------------------------------------- #
# enforce_advisory_only (§6.9)                                                #
# --------------------------------------------------------------------------- #


class TestEnforceAdvisoryOnly:
    def test_advisory_passes_through(self, tc, tt):
        constraint = tt.KnowledgeAdvisoryConstraint(
            source_layer="L3",
            directive_type=tt.KnowledgeDirective.ADVISORY,
            content="advice",
            trace_id="t",
        )
        result = tc.enforce_advisory_only(constraint)
        assert result is constraint

    def test_control_directive_rejected(self, tc, tt):
        constraint = tt.KnowledgeAdvisoryConstraint(
            source_layer="L3",
            directive_type=tt.KnowledgeDirective.CONTROL,
            content="override",
            trace_id="t-abc",
        )
        with pytest.raises(tc.AdvisoryViolationError, match=r"CONTROL directive"):
            tc.enforce_advisory_only(constraint)

    def test_control_error_includes_trace_id(self, tc, tt):
        constraint = tt.KnowledgeAdvisoryConstraint(
            source_layer="L3",
            directive_type=tt.KnowledgeDirective.CONTROL,
            content="x",
            trace_id="trace-xyz",
        )
        with pytest.raises(tc.AdvisoryViolationError, match=r"trace-xyz"):
            tc.enforce_advisory_only(constraint)

    def test_wrong_type_rejected(self, tc):
        with pytest.raises(tc.AdvisoryViolationError, match=r"Expected KnowledgeAdvisoryConstraint"):
            tc.enforce_advisory_only("not-a-constraint")

    def test_none_rejected(self, tc):
        with pytest.raises(tc.AdvisoryViolationError):
            tc.enforce_advisory_only(None)


# --------------------------------------------------------------------------- #
# Exception hierarchy                                                         #
# --------------------------------------------------------------------------- #


class TestExceptionHierarchy:
    @pytest.mark.parametrize(
        "name",
        [
            "AdvisoryViolationError",
            "CognitiveDiffError",
            "ErrorSignatureError",
            "ManifestHashError",
            "PlanProvenanceError",
            "PolicyConfigPinError",
            "RAGChainError",
            "TraceIDFormatError",
        ],
    )
    def test_is_exception_subclass(self, tc, name):
        assert issubclass(getattr(tc, name), Exception)
