"""Runtime proof: persisted Chroma ``fact_vectors`` + ``c0_retrieve_apps_rg`` dense lane.

Skips when chromadb or sentence-transformers is unavailable (operator env).
Hermetic: uses tmp_path Chroma store + repo smoke JSONL fixture.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("chromadb")
pytest.importorskip("sentence_transformers")

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.final_evidence_contract import SUPPORT_STATUS_PASS
from apps_rg.runtime.bindings import c0_binding
from apps_rg.runtime.bindings.c0_binding import (
    C0_GRAPH_LANE_NA_REF,
    C0_METADATA_FILTER_REF,
    C0_QUERY_VEC_REF_BGE,
    C0_SPARSE_LANE_NA_REF,
    c0_retrieve_apps_rg,
)
from tools.ingestion.chroma_ingest_pipeline import load_documents, run_ingestion

REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "apps_rg" / "fact_vectors_c0_smoke.chroma_input"


def _route() -> RouteContract:
    r = RouteContract.__new__(RouteContract)
    object.__setattr__(r, "grounding_required", True)
    object.__setattr__(r, "request_id", "fv-runtime-req")
    object.__setattr__(r, "run_id", "fv-runtime-run")
    object.__setattr__(r, "app_id", "apps_rg")
    object.__setattr__(r, "trace_id", "fv-runtime-trace")
    return r


def _validated() -> ValidatedRequest:
    vr = ValidatedRequest.__new__(ValidatedRequest)
    object.__setattr__(vr, "request_id", "fv-runtime-req")
    object.__setattr__(vr, "run_id", "fv-runtime-run")
    object.__setattr__(vr, "app_id", "apps_rg")
    object.__setattr__(vr, "trace_id", "fv-runtime-trace")
    object.__setattr__(
        vr,
        "app_payload",
        {
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
                "summary": (
                    "SMOKE_C0_UNIFY_NARR_ANCHOR cohesive story arc linking problem discovery "
                    "execution and verification without invented employers or dates."
                ),
                "competencies": (
                    "SMOKE_C0_COMPETENCIES_ANCHOR Python asyncio PostgreSQL Redis Kubernetes "
                    "distributed tracing and performance profiling in production."
                ),
                "skills": "Python Kubernetes PostgreSQL Redis asyncio observability",
                "unify_bullets": (
                    "SMOKE_C0_UNIFY_BULLETS_ANCHOR quantified bullets with verbs metrics and "
                    "ownership statements suitable for consulting-style resume synthesis."
                ),
                "unify_narrative": (
                    "SMOKE_C0_UNIFY_NARR_ANCHOR cohesive story arc linking problem discovery "
                    "execution and verification without invented employers or dates."
                ),
                "ibm_bullets": (
                    "SMOKE_C0_IBM_BULLETS_ANCHOR enterprise platform delivery metrics ownership "
                    "stakeholder alignment for global programs."
                ),
                "ibm_narrative": (
                    "SMOKE_C0_IBM_NARR_ANCHOR enterprise stakeholder narrative scope outcomes "
                    "verification without speculative claims."
                ),
                "experience": (
                    "SMOKE_C0_UNIFY_BULLETS_ANCHOR led platform migrations with measurable "
                    "latency improvements and audit-friendly operational receipts."
                ),
                "resume_text": (
                    "SMOKE_C0_PROJECT_ANCHOR resume body referencing project evidence lane "
                    "for dense retrieval smoke testing."
                ),
            },
        },
    )
    return vr


@pytest.fixture()
def chroma_dir(tmp_path: Path) -> Path:
    d = tmp_path / "chroma_store"
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_c0_retrieve_hits_fact_vectors_and_fec_maps(chroma_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Real PersistentClient + BGE-M3 query; FEC maps populated from Chroma lane."""
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    monkeypatch.setenv("EMBEDDING_ENABLED", "true")
    c0_binding._embedding_singleton = None

    assert SMOKE_FIXTURE.is_file(), f"missing fixture {SMOKE_FIXTURE}"
    docs = load_documents(SMOKE_FIXTURE)
    n = run_ingestion(docs, chromadb_path=str(chroma_dir), collection_name="fact_vectors")
    assert n == len(docs)

    import chromadb  # type: ignore

    client = chromadb.PersistentClient(path=str(chroma_dir))
    col = client.get_collection("fact_vectors")
    assert col.count() > 0
    peek = col.get(include=["embeddings"], limit=1)
    raw_embs = peek.get("embeddings")
    assert raw_embs is not None and len(raw_embs) > 0
    emb = raw_embs[0]
    assert emb is not None
    assert len(emb) == 1024

    fec = c0_retrieve_apps_rg(_route(), _validated(), chromadb_path=str(chroma_dir))
    assert any(str(r).startswith("dense:fact_vectors:") for r in (fec.dense_search_refs or ()))

    fv = [it for it in fec.evidence_items if getattr(it, "source_type", "") == "fact_vectors"]
    assert fv, "expected fact_vectors EvidenceItem rows from Chroma"
    joined = "\n".join(it.content for it in fv)
    for anchor in (
        "SMOKE_C0_HEADLINE_ANCHOR",
        "SMOKE_C0_EXEC_SUMMARY_ANCHOR",
        "SMOKE_C0_COMPETENCIES_ANCHOR",
        "SMOKE_C0_UNIFY_BULLETS_ANCHOR",
        "SMOKE_C0_UNIFY_NARR_ANCHOR",
        "SMOKE_C0_IBM_BULLETS_ANCHOR",
        "SMOKE_C0_IBM_NARR_ANCHOR",
    ):
        assert anchor in joined, f"missing lane anchor {anchor}"

    assert fec.support_status == SUPPORT_STATUS_PASS
    assert fec.citation_map, "citation_map from chroma_lane_items"
    assert fec.source_lineage_map, "source_lineage_map from chroma_lane_items"
    assert fec.freshness_receipts, "freshness_receipts from chroma_lane_items"
    assert fec.query_vec_ref == C0_QUERY_VEC_REF_BGE
    assert C0_METADATA_FILTER_REF in fec.metadata_filter_refs
    assert C0_SPARSE_LANE_NA_REF in fec.sparse_search_refs
    assert C0_GRAPH_LANE_NA_REF in fec.graph_expansion_refs
    assert fec.evidence_strata, "CANONICAL stratum for Chroma hits"
    assert fec.source_version_map, "source_version_map from chunk metadata"
