"""W3–W4 apps_rg C0 sparse/exact wiring via generic core seam."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

pytest.importorskip("chromadb")
pytest.importorskip("sentence_transformers")

from agentic_core.knowledge.retrieval.c0_sparse_exact_seam import (
    SparseLexicalLaneOutcome,
    SparseLexicalLaneStatus,
    format_sparse_lane_receipt,
)
from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import HybridSearchResult
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.final_evidence_contract import (
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_PASSING_VALUES,
)
from agentic_core.runtime.contracts.route_contract import RouteContract
from apps_rg.runtime.bindings import c0_binding
from apps_rg.runtime.bindings.c0_binding import (
    C0_SPARSE_LANE_NA_REF,
    EvidenceItem,
    SectionRetrievalProfile,
    _chunk_id_from_evidence_item,
    _merge_section_dense_sparse_items,
    _resolve_fec_sparse_search_refs,
    c0_retrieve_apps_rg,
)
from tools.ingestion.chroma_ingest_pipeline import load_documents, run_ingestion

REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "apps_rg" / "fact_vectors_c0_smoke.chroma_input"


def _route() -> RouteContract:
    r = RouteContract.__new__(RouteContract)
    object.__setattr__(r, "grounding_required", True)
    object.__setattr__(r, "request_id", "sparse-wiring-req")
    object.__setattr__(r, "run_id", "sparse-wiring-run")
    object.__setattr__(r, "app_id", "apps_rg")
    object.__setattr__(r, "trace_id", "sparse-wiring-trace")
    return r


def _validated() -> ValidatedRequest:
    vr = ValidatedRequest.__new__(ValidatedRequest)
    object.__setattr__(vr, "request_id", "sparse-wiring-req")
    object.__setattr__(vr, "run_id", "sparse-wiring-run")
    object.__setattr__(vr, "app_id", "apps_rg")
    object.__setattr__(vr, "trace_id", "sparse-wiring-trace")
    object.__setattr__(vr, "app_payload", _validated_app_payload())
    return vr


def _validated_app_payload() -> dict[str, Any]:
    return {
        "jd_payload": {
            "jd_text": (
                "SMOKE_C0_HEADLINE_ANCHOR hiring Principal Engineer at Contoso Labs "
                "for SaaS reliability and platform leadership."
            ),
            "target_company": "Contoso Labs",
            "target_role": "Principal Engineer",
        },
        "resume_payload": {
            "headline": (
                "SMOKE_C0_HEADLINE_ANCHOR principal product leader driving measurable "
                "revenue and reliability outcomes across global SaaS platforms."
            ),
            "executive_summary": (
                "SMOKE_C0_EXEC_SUMMARY_ANCHOR concise narrative tying scope constraints "
                "and evidence-backed outcomes for senior hiring managers."
            ),
            "competencies": (
                "SMOKE_C0_COMPETENCIES_ANCHOR Python asyncio PostgreSQL Redis Kubernetes "
                "distributed tracing and performance profiling in production."
            ),
            "unify_bullets": (
                "SMOKE_C0_UNIFY_BULLETS_ANCHOR quantified bullets with verbs metrics and "
                "ownership statements suitable for consulting-style resume synthesis."
            ),
            "ibm_bullets": (
                "SMOKE_C0_IBM_BULLETS_ANCHOR enterprise platform delivery metrics ownership "
                "stakeholder alignment for global programs."
            ),
            "resume_text": "SMOKE_C0_PROJECT_ANCHOR resume body for dense retrieval smoke testing.",
        },
    }


class _StubSparseIndex:
    def __init__(self, hits: list[dict[str, Any]], *, available: bool = True):
        self._hits = hits
        self._available = available

    @property
    def is_available(self) -> bool:
        return self._available

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        return list(self._hits)[:top_k]


def _enable_sparse_on_profile(monkeypatch: pytest.MonkeyPatch, section_ids: set[str] | None = None) -> None:
    orig = SectionRetrievalProfile.section_sparse_config

    def _patched(self: SectionRetrievalProfile, section: dict[str, Any]) -> dict[str, Any]:
        cfg = orig(self, section)
        sid = section.get("section_id", "")
        if section_ids is None or sid in section_ids:
            cfg["sparse_enabled"] = True
            cfg["sparse_collection_ref"] = "fact_vectors"
        return cfg

    def _any_sparse(self: SectionRetrievalProfile) -> bool:
        return True

    monkeypatch.setattr(SectionRetrievalProfile, "section_sparse_config", _patched)
    monkeypatch.setattr(SectionRetrievalProfile, "any_sparse_enabled", _any_sparse)


@pytest.fixture()
def chroma_dir(tmp_path: Path) -> Path:
    d = tmp_path / "chroma_store"
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_sparse_disabled_keeps_not_applicable_receipt(chroma_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_C0_DENSE_SPARSE_MANDATORY", "0")
    monkeypatch.setenv("APPS_RG_C0_SPARSE_ENABLED", "0")
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    c0_binding._embedding_singleton = None
    docs = load_documents(SMOKE_FIXTURE)
    run_ingestion(docs, chromadb_path=str(chroma_dir), collection_name="fact_vectors")
    fec = c0_retrieve_apps_rg(_route(), _validated(), chromadb_path=str(chroma_dir))
    assert C0_SPARSE_LANE_NA_REF in fec.sparse_search_refs
    assert fec.support_status == SUPPORT_STATUS_PASS


def test_sparse_enabled_unavailable_emits_unavailable_receipt_not_pass(
    chroma_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_RG_C0_DENSE_SPARSE_MANDATORY", "0")
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    c0_binding._embedding_singleton = None
    _enable_sparse_on_profile(monkeypatch)
    monkeypatch.setattr(
        "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
        lambda _n: None,
    )
    docs = load_documents(SMOKE_FIXTURE)
    run_ingestion(docs, chromadb_path=str(chroma_dir), collection_name="fact_vectors")
    fec = c0_retrieve_apps_rg(_route(), _validated(), chromadb_path=str(chroma_dir))
    assert C0_SPARSE_LANE_NA_REF not in fec.sparse_search_refs
    assert any("UNAVAILABLE" in r for r in fec.sparse_search_refs)
    assert fec.support_status in SUPPORT_STATUS_PASSING_VALUES or fec.support_status == SUPPORT_STATUS_PASS


def test_sparse_enabled_empty_emits_empty_receipt(chroma_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_C0_DENSE_SPARSE_MANDATORY", "0")
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    c0_binding._embedding_singleton = None
    _enable_sparse_on_profile(monkeypatch, section_ids={"competencies"})
    stub = _StubSparseIndex([])
    monkeypatch.setattr(
        "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
        lambda _n: stub,
    )
    docs = load_documents(SMOKE_FIXTURE)
    run_ingestion(docs, chromadb_path=str(chroma_dir), collection_name="fact_vectors")
    fec = c0_retrieve_apps_rg(_route(), _validated(), chromadb_path=str(chroma_dir))
    assert any("EMPTY" in r for r in fec.sparse_search_refs)


def test_sparse_enabled_hits_populate_sparse_refs_and_scores(
    chroma_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    c0_binding._embedding_singleton = None
    _enable_sparse_on_profile(monkeypatch, section_ids={"ibm_bullets", "unify_bullets", "competencies"})
    hits = [
        {
            "id": "sparse-chunk-1",
            "content": "SMOKE_C0_IBM_BULLETS_ANCHOR enterprise platform delivery",
            "score": 0.88,
            "metadata": {"app": "apps_rg", "source_class": "candidate_profile"},
            "source": "sparse_fts",
        },
        {
            "id": "sparse-chunk-2",
            "content": "SMOKE_C0_UNIFY_BULLETS_ANCHOR quantified bullets",
            "score": 0.77,
            "metadata": {"app": "apps_rg", "source_class": "candidate_profile"},
            "source": "sparse_fts",
        },
        {
            "id": "sparse-chunk-3",
            "content": "SMOKE_C0_COMPETENCIES_ANCHOR Python asyncio PostgreSQL",
            "score": 0.66,
            "metadata": {"app": "apps_rg", "source_class": "candidate_profile"},
            "source": "sparse_fts",
        },
    ]
    stub = _StubSparseIndex(hits)
    monkeypatch.setattr(
        "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
        lambda _n: stub,
    )
    docs = load_documents(SMOKE_FIXTURE)
    run_ingestion(docs, chromadb_path=str(chroma_dir), collection_name="fact_vectors")
    fec = c0_retrieve_apps_rg(_route(), _validated(), chromadb_path=str(chroma_dir))
    assert any("status=OK" in r for r in fec.sparse_search_refs)
    fv = [it for it in fec.evidence_items if getattr(it, "source_type", "") == "fact_vectors"]
    assert any(getattr(it, "bm25_score", 0.0) > 0.0 for it in fv)
    joined = "\n".join(it.content for it in fv)
    for anchor in (
        "SMOKE_C0_IBM_BULLETS_ANCHOR",
        "SMOKE_C0_UNIFY_BULLETS_ANCHOR",
        "SMOKE_C0_COMPETENCIES_ANCHOR",
    ):
        assert anchor in joined


def test_merge_section_dense_sparse_is_deterministic() -> None:
    dense = [
        EvidenceItem(
            source="chromadb:candidate_profile:d1",
            content="alpha dense",
            evidence_id="chroma:d1",
            dense_score=0.9,
            confidence_score=0.9,
            allowed_prompt_slot="C0_EVIDENCE_DATA_ONLY",
        ),
    ]
    outcome = SparseLexicalLaneOutcome(
        lane_id="lane.test",
        status=SparseLexicalLaneStatus.OK,
        hits=(),
        receipt_ref=format_sparse_lane_receipt("lane.test", SparseLexicalLaneStatus.OK, 1),
        hybrid_rows=(
            HybridSearchResult(
                chunk_id="d1",
                content="alpha dense",
                metadata={},
                combined_score=0.7,
                source="lexical",
                vector_score=0.0,
                lexical_score=0.7,
            ),
        ),
    )
    a = _merge_section_dense_sparse_items(dense, outcome, merge_policy="rrf", timestamp_iso="t1")
    b = _merge_section_dense_sparse_items(dense, outcome, merge_policy="rrf", timestamp_iso="t1")
    assert [(_chunk_id_from_evidence_item(x), x.bm25_score, x.dense_score) for x in a] == [
        (_chunk_id_from_evidence_item(x), x.bm25_score, x.dense_score) for x in b
    ]


def test_dedupe_preserves_single_chunk_id_after_merge() -> None:
    dense = [
        EvidenceItem(
            source="chromadb:candidate_profile:same",
            content="dup body",
            evidence_id="chroma:same",
            dense_score=0.5,
            confidence_score=0.5,
            allowed_prompt_slot="C0_EVIDENCE_DATA_ONLY",
        ),
    ]
    outcome = SparseLexicalLaneOutcome(
        lane_id="lane.dedupe",
        status=SparseLexicalLaneStatus.OK,
        hits=(),
        receipt_ref="ref:sparse:lane:lane_dedupe:status=OK:hits=1",
        hybrid_rows=(
            HybridSearchResult(
                chunk_id="same",
                content="dup body",
                metadata={},
                combined_score=0.8,
                source="lexical",
                vector_score=0.0,
                lexical_score=0.8,
            ),
        ),
    )
    merged = _merge_section_dense_sparse_items(dense, outcome, merge_policy="rrf", timestamp_iso="t")
    assert len(merged) == 1
    assert merged[0].bm25_score == pytest.approx(0.8)


def test_resolve_fec_sparse_refs_na_when_disabled() -> None:
    profile = MagicMock()
    profile.any_sparse_enabled.return_value = False
    refs = _resolve_fec_sparse_search_refs(profile, [])
    assert refs == (C0_SPARSE_LANE_NA_REF,)


def test_sparse_mandatory_fail_closed_when_bm25_unavailable(
    chroma_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_rg.runtime.bindings.c0_binding import C0EvidenceGapError

    monkeypatch.setenv("APPS_RG_C0_DENSE_SPARSE_MANDATORY", "1")
    monkeypatch.setenv("APPS_RG_C0_SPARSE_ENABLED", "1")
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    c0_binding._embedding_singleton = None
    _enable_sparse_on_profile(monkeypatch)
    monkeypatch.setattr(
        "agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index",
        lambda _n: None,
    )
    docs = load_documents(SMOKE_FIXTURE)
    run_ingestion(docs, chromadb_path=str(chroma_dir), collection_name="fact_vectors")
    with pytest.raises(C0EvidenceGapError, match="sparse"):
        c0_retrieve_apps_rg(_route(), _validated(), chromadb_path=str(chroma_dir))
