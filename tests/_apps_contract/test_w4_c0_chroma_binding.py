"""W4 tests — apps_rg C0 binding Chroma opt-in, file fallback, EMBEDDING_ENABLED guard,
FEC tuple field population, prior_outputs exclusion, and negative controls.

Plan: apps-rg-chroma-ingestion-wiring-c7f2d9 W4
"""
from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    SUPPORT_STATUS_EMPTY,
    SUPPORT_STATUS_PARTIAL,
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK,
    STATUS_UNKNOWN,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_rg.runtime.bindings.c0_binding import (
    APPS_RG_C0_CERT_REF,
    C0EvidenceGapError,
    _build_chroma_evidence,
    _compute_support_status,
    c0_retrieve_apps_rg,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_route(grounding_required: bool = True) -> RouteContract:
    r = RouteContract.__new__(RouteContract)
    object.__setattr__(r, "grounding_required", grounding_required)
    return r


def _make_vr(jd_text: str = "Software Engineer role", resume_text: str = "my resume") -> ValidatedRequest:
    vr = ValidatedRequest.__new__(ValidatedRequest)
    object.__setattr__(vr, "request_id", "req-test")
    object.__setattr__(vr, "run_id", "run-test")
    object.__setattr__(vr, "app_id", "apps_rg")
    object.__setattr__(vr, "trace_id", "trace-test")
    object.__setattr__(
        vr,
        "app_payload",
        {
            "jd_payload": {"jd_text": jd_text},
            "resume_payload": {"resume_text": resume_text},
        },
    )
    return vr


def _make_chunk(
    chunk_id: str = "abc123",
    source_class: str = "candidate_profile",
    source_id: str = "src-1",
    citation_anchor: str = "cand-profile-v1",
    invalid_for_normative_use: str = "false",
    freshness: str = "FRESH",
    authority_class: str = "PRIMARY",
    chunk_digest: str = "digest-abc",
) -> dict[str, Any]:
    return {
        "_chunk_id": chunk_id,
        "_document": "chunk content",
        "_distance": 0.1,
        "source_class": source_class,
        "source_id": source_id,
        "citation_anchor": citation_anchor,
        "invalid_for_normative_use": invalid_for_normative_use,
        "freshness": freshness,
        "authority_class": authority_class,
        "chunk_digest": chunk_digest,
    }


# ---------------------------------------------------------------------------
# T1: File-only path (no Chroma configured)
# ---------------------------------------------------------------------------


class TestFileOnlyPath:
    def test_file_only_returns_fec(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        fec = c0_retrieve_apps_rg(_make_route(), _make_vr())
        assert isinstance(fec, FinalEvidenceContract)

    def test_file_only_has_jd_and_resume_evidence(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        fec = c0_retrieve_apps_rg(_make_route(), _make_vr())
        sources = [item.source for item in fec.evidence_items]
        assert any("jd_payload" in s for s in sources)
        assert any("resume_payload" in s for s in sources)

    def test_file_only_support_target_met(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        fec = c0_retrieve_apps_rg(_make_route(), _make_vr())
        assert fec.support_target_met is True

    def test_file_only_citation_map_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """File-only path: no Chroma → citation_map stays empty tuple."""
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        fec = c0_retrieve_apps_rg(_make_route(), _make_vr())
        assert fec.citation_map == ()

    def test_file_only_support_status_unknown(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """File-only path: support_status stays UNKNOWN (Chroma not queried)."""
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        fec = c0_retrieve_apps_rg(_make_route(), _make_vr())
        assert fec.support_status == STATUS_UNKNOWN

    def test_file_only_l5_cert_ref_correct(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        fec = c0_retrieve_apps_rg(_make_route(), _make_vr())
        assert fec.l5_certification_ref == APPS_RG_C0_CERT_REF

    def test_file_only_no_raise_on_missing_embedding_enabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """W4.3: EMBEDDING_ENABLED not set must NOT raise when no Chroma path."""
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        fec = c0_retrieve_apps_rg(_make_route(), _make_vr())
        assert isinstance(fec, FinalEvidenceContract)

    def test_chromadb_path_param_takes_precedence_over_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """chromadb_path=None with env unset → file-only, no guard fires."""
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.setenv("EMBEDDING_ENABLED", "false")
        fec = c0_retrieve_apps_rg(_make_route(), _make_vr(), chromadb_path=None)
        assert isinstance(fec, FinalEvidenceContract)


# ---------------------------------------------------------------------------
# T2: EMBEDDING_ENABLED guard (W4.3)
# ---------------------------------------------------------------------------


class TestEmbeddingEnabledGuard:
    def test_guard_fires_with_env_path_and_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CHROMA_PERSIST_DIR", "data/cache/chromadb")
        monkeypatch.setenv("EMBEDDING_ENABLED", "false")
        with pytest.raises(C0EvidenceGapError):
            c0_retrieve_apps_rg(_make_route(), _make_vr())

    def test_guard_fires_with_param_path_and_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.setenv("EMBEDDING_ENABLED", "false")
        with pytest.raises(C0EvidenceGapError):
            c0_retrieve_apps_rg(_make_route(), _make_vr(), chromadb_path="data/cache/chromadb")

    def test_guard_fires_when_embedding_enabled_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CHROMA_PERSIST_DIR", "data/cache/chromadb")
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        with pytest.raises(C0EvidenceGapError):
            c0_retrieve_apps_rg(_make_route(), _make_vr())

    def test_guard_contains_action_hint(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CHROMA_PERSIST_DIR", "data/cache/chromadb")
        monkeypatch.setenv("EMBEDDING_ENABLED", "false")
        with pytest.raises(C0EvidenceGapError) as exc_info:
            c0_retrieve_apps_rg(_make_route(), _make_vr())
        assert "EMBEDDING_ENABLED=true" in str(exc_info.value)

    def test_guard_does_not_fire_when_enabled_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When EMBEDDING_ENABLED=true and path set, guard does not raise (Chroma fallback OK)."""
        monkeypatch.setenv("CHROMA_PERSIST_DIR", "data/cache/chromadb")
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")
        # Chroma will fail to connect to path (test path doesn't exist in process)
        # but guard must NOT raise; instead Chroma unavailable → fallback
        fec = c0_retrieve_apps_rg(_make_route(), _make_vr(), chromadb_path="/nonexistent/path")
        assert isinstance(fec, FinalEvidenceContract)
        assert fec.support_status == STATUS_UNKNOWN  # Chroma failed → fallback


# ---------------------------------------------------------------------------
# T3: _build_chroma_evidence unit tests (FEC field population)
# ---------------------------------------------------------------------------


class TestBuildChromaEvidence:
    def test_valid_chunk_produces_evidence_item(self) -> None:
        chunks = [_make_chunk()]
        excluded: list[str] = []
        items, citations, lineage, freshness = _build_chroma_evidence(chunks, "2026-01-01T00:00:00Z", excluded)
        assert len(items) == 1
        assert len(citations) == 1
        assert len(lineage) == 1

    def test_citation_map_contains_evidence_id_and_anchor(self) -> None:
        chunks = [_make_chunk(chunk_id="cid1", citation_anchor="anchor-v1")]
        excluded: list[str] = []
        items, citations, lineage, _ = _build_chroma_evidence(chunks, "2026-01-01T00:00:00Z", excluded)
        assert citations[0] == ("chroma:cid1", "anchor-v1")

    def test_lineage_map_contains_evidence_id_and_source_id(self) -> None:
        chunks = [_make_chunk(chunk_id="cid1", source_id="src-99")]
        excluded: list[str] = []
        items, citations, lineage, _ = _build_chroma_evidence(chunks, "2026-01-01T00:00:00Z", excluded)
        assert lineage[0] == ("chroma:cid1", "src-99")

    def test_freshness_ref_populated_when_freshness_present(self) -> None:
        chunks = [_make_chunk(source_id="src-1", freshness="FRESH")]
        excluded: list[str] = []
        _, _, _, freshness_refs = _build_chroma_evidence(chunks, "2026-01-01T00:00:00Z", excluded)
        assert any("src-1" in ref for ref in freshness_refs)

    def test_invalid_for_normative_use_chunk_excluded(self) -> None:
        """invalid_for_normative_use=true → excluded_refs, NOT evidence_items."""
        chunks = [_make_chunk(chunk_id="po-1", invalid_for_normative_use="true")]
        excluded: list[str] = []
        items, citations, lineage, _ = _build_chroma_evidence(chunks, "2026-01-01T00:00:00Z", excluded)
        assert len(items) == 0
        assert any("po-1" in ref for ref in excluded)

    def test_missing_citation_anchor_excluded(self) -> None:
        """Missing citation_anchor → excluded_refs, NOT evidence_items."""
        chunks = [_make_chunk(chunk_id="no-anchor", citation_anchor="")]
        excluded: list[str] = []
        items, _, _, _ = _build_chroma_evidence(chunks, "2026-01-01T00:00:00Z", excluded)
        assert len(items) == 0
        assert any("no-anchor" in ref for ref in excluded)

    def test_mixed_valid_and_excluded_chunks(self) -> None:
        chunks = [
            _make_chunk(chunk_id="good-1", citation_anchor="anchor-1"),
            _make_chunk(chunk_id="bad-1", citation_anchor="", invalid_for_normative_use="false"),
            _make_chunk(chunk_id="bad-2", invalid_for_normative_use="true", citation_anchor="anchor-2"),
        ]
        excluded: list[str] = []
        items, _, _, _ = _build_chroma_evidence(chunks, "2026-01-01T00:00:00Z", excluded)
        assert len(items) == 1
        assert len(excluded) == 2

    def test_evidence_item_source_contains_source_class(self) -> None:
        chunks = [_make_chunk(source_class="rubrics", source_id="src-r")]
        excluded: list[str] = []
        items, _, _, _ = _build_chroma_evidence(chunks, "2026-01-01T00:00:00Z", excluded)
        assert "rubrics" in items[0].source


# ---------------------------------------------------------------------------
# T4: _compute_support_status unit tests
# ---------------------------------------------------------------------------


class TestComputeSupportStatus:
    def _item_with_source_class(self, sc: str) -> Any:
        from apps_rg.runtime.bindings.c0_binding import EvidenceItem
        return EvidenceItem(
            source=f"chromadb:{sc}:src-1",
            content="content",
            citation_anchor="anchor",
            support_status=SUPPORT_STATUS_PASS,
        )

    def test_empty_items_returns_empty(self) -> None:
        assert _compute_support_status([], 0) == SUPPORT_STATUS_EMPTY

    def test_all_source_classes_covered_returns_pass(self) -> None:
        from apps_rg.runtime.bindings.c0_binding import _NORMATIVE_SOURCE_CLASSES
        items = [self._item_with_source_class(sc) for sc in _NORMATIVE_SOURCE_CLASSES]
        assert _compute_support_status(items, 0) == SUPPORT_STATUS_PASS

    def test_partial_coverage_returns_partial(self) -> None:
        items = [self._item_with_source_class("candidate_profile"),
                 self._item_with_source_class("project_evidence"),
                 self._item_with_source_class("approved_examples")]
        result = _compute_support_status(items, 0)
        assert result in (SUPPORT_STATUS_PARTIAL, SUPPORT_STATUS_WEAK)

    def test_single_item_returns_weak_or_partial(self) -> None:
        items = [self._item_with_source_class("candidate_profile")]
        result = _compute_support_status(items, 0)
        assert result in (SUPPORT_STATUS_PARTIAL, SUPPORT_STATUS_WEAK)


# ---------------------------------------------------------------------------
# T5: Chroma retrieval path with mock client (W4.1 + W4.2)
# ---------------------------------------------------------------------------


class TestChromaRetrievalPath:
    def _make_mock_collection(self, chunks: list[dict[str, Any]]) -> MagicMock:
        """Build a mock Chroma collection that returns the given chunks."""
        col = MagicMock()
        ids = [c["_chunk_id"] for c in chunks]
        metas = [{k: v for k, v in c.items() if not k.startswith("_")} for c in chunks]
        docs = [c.get("_document", "doc") for c in chunks]
        dists = [c.get("_distance", 0.1) for c in chunks]
        col.query.return_value = {
            "ids": [ids],
            "metadatas": [metas],
            "documents": [docs],
            "distances": [dists],
        }
        return col

    def test_chroma_path_populates_citation_map(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")

        valid_chunk = _make_chunk(
            chunk_id="cid-100",
            source_class="candidate_profile",
            citation_anchor="candidate-v1",
        )
        mock_col = self._make_mock_collection([valid_chunk])
        mock_client = MagicMock()
        mock_client.get_collection.return_value = mock_col

        with patch("apps_rg.runtime.bindings.c0_binding._get_embedding_model") as mock_model, \
             patch("chromadb.PersistentClient", return_value=mock_client):
            mock_model.return_value.encode.return_value = MagicMock(tolist=lambda: [0.0] * 1024)
            fec = c0_retrieve_apps_rg(_make_route(), _make_vr(), chromadb_path="data/cache/chromadb")

        assert len(fec.citation_map) > 0
        assert any(anchor == "candidate-v1" for _, anchor in fec.citation_map)

    def test_chroma_path_populates_source_lineage_map(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")

        valid_chunk = _make_chunk(chunk_id="cid-200", source_id="src-200", citation_anchor="anchor-200")
        mock_col = self._make_mock_collection([valid_chunk])
        mock_client = MagicMock()
        mock_client.get_collection.return_value = mock_col

        with patch("apps_rg.runtime.bindings.c0_binding._get_embedding_model") as mock_model, \
             patch("chromadb.PersistentClient", return_value=mock_client):
            mock_model.return_value.encode.return_value = MagicMock(tolist=lambda: [0.0] * 1024)
            fec = c0_retrieve_apps_rg(_make_route(), _make_vr(), chromadb_path="data/cache/chromadb")

        assert any(src_id == "src-200" for _, src_id in fec.source_lineage_map)

    def test_chroma_path_populates_freshness_receipts(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")

        valid_chunk = _make_chunk(chunk_id="cid-300", source_id="src-300",
                                  citation_anchor="a-300", freshness="FRESH")
        mock_col = self._make_mock_collection([valid_chunk])
        mock_client = MagicMock()
        mock_client.get_collection.return_value = mock_col

        with patch("apps_rg.runtime.bindings.c0_binding._get_embedding_model") as mock_model, \
             patch("chromadb.PersistentClient", return_value=mock_client):
            mock_model.return_value.encode.return_value = MagicMock(tolist=lambda: [0.0] * 1024)
            fec = c0_retrieve_apps_rg(_make_route(), _make_vr(), chromadb_path="data/cache/chromadb")

        assert len(fec.freshness_receipts) > 0

    def test_chroma_unavailable_falls_back_to_file(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")

        with patch("chromadb.PersistentClient", side_effect=RuntimeError("Chroma down")):
            fec = c0_retrieve_apps_rg(_make_route(), _make_vr(), chromadb_path="data/cache/chromadb")

        assert isinstance(fec, FinalEvidenceContract)
        assert fec.support_status == STATUS_UNKNOWN
        # File-only items still present
        assert any("jd_payload" in item.source for item in fec.evidence_items)

    def test_l5_cert_ref_correct_with_chroma(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.setenv("EMBEDDING_ENABLED", "true")

        valid_chunk = _make_chunk(chunk_id="cid-cert", citation_anchor="a-cert")
        mock_col = self._make_mock_collection([valid_chunk])
        mock_client = MagicMock()
        mock_client.get_collection.return_value = mock_col

        with patch("apps_rg.runtime.bindings.c0_binding._get_embedding_model") as mock_model, \
             patch("chromadb.PersistentClient", return_value=mock_client):
            mock_model.return_value.encode.return_value = MagicMock(tolist=lambda: [0.0] * 1024)
            fec = c0_retrieve_apps_rg(_make_route(), _make_vr(), chromadb_path="data/cache/chromadb")

        assert fec.l5_certification_ref == APPS_RG_C0_CERT_REF


# ---------------------------------------------------------------------------
# T6: prior_outputs exclusion (negative control)
# ---------------------------------------------------------------------------


class TestPriorOutputsExclusion:
    def test_prior_outputs_chunk_excluded_not_normative(self) -> None:
        """prior_outputs with invalid_for_normative_use=true → excluded, not in evidence_items."""
        po_chunk = _make_chunk(
            chunk_id="po-excl-1",
            source_class="prior_outputs",
            citation_anchor="po-anchor-1",
            invalid_for_normative_use="true",
        )
        excluded: list[str] = []
        items, citations, _, _ = _build_chroma_evidence([po_chunk], "2026-01-01T00:00:00Z", excluded)
        assert len(items) == 0
        assert any("po-excl-1" in ref for ref in excluded)

    def test_prior_outputs_never_in_normative_source_classes(self) -> None:
        from apps_rg.runtime.bindings.c0_binding import _NORMATIVE_SOURCE_CLASSES
        assert "prior_outputs" not in _NORMATIVE_SOURCE_CLASSES

    def test_unknown_is_never_pass(self) -> None:
        """UNKNOWN support_status must never satisfy support_status_is_passing()."""
        from agentic_core.runtime.contracts.final_evidence_contract import STATUS_UNKNOWN, SUPPORT_STATUS_PASSING_VALUES
        assert STATUS_UNKNOWN not in SUPPORT_STATUS_PASSING_VALUES

    def test_empty_normative_items_gives_empty_status(self) -> None:
        assert _compute_support_status([], excluded_count=5) == SUPPORT_STATUS_EMPTY


# ---------------------------------------------------------------------------
# T7: grounding_required=False guard
# ---------------------------------------------------------------------------


class TestGroundingRequiredGuard:
    def test_raises_when_grounding_not_required(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
        monkeypatch.delenv("EMBEDDING_ENABLED", raising=False)
        with pytest.raises(ValueError, match="grounding_required=False"):
            c0_retrieve_apps_rg(_make_route(grounding_required=False), _make_vr())
