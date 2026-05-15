#!/usr/bin/env python3
"""Operator helper: ingest C0 smoke fact_vectors + emit ingestion/C0 proof JSON.

Writes under ``artifacts/apps_rg/c0_embedding_gap/`` (typically gitignored):
  - ingestion_proof.json
  - c0_runtime_proof.json

Does not modify agentic_core. Requires chromadb + sentence-transformers.

Default fixture: ``tests/fixtures/apps_rg/fact_vectors_c0_smoke.chroma_input`` (JSON
lines; not ``*.jsonl`` because repo ``.gitignore`` ignores ``*.jsonl``).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_chroma_path(repo: Path) -> str:
    return os.environ.get("CHROMA_PERSIST_DIR", str(repo / "data" / "cache" / "chromadb"))


def _smoke_fixture(repo: Path) -> Path:
    # Not *.jsonl — repo .gitignore blocks JSONL under fixtures.
    return repo / "tests" / "fixtures" / "apps_rg" / "fact_vectors_c0_smoke.chroma_input"


def _artifact_dir(repo: Path) -> Path:
    return repo / "artifacts" / "apps_rg" / "c0_embedding_gap"


def _reset_collection(chroma_path: str, collection_name: str) -> None:
    import chromadb  # type: ignore

    client = chromadb.PersistentClient(path=chroma_path)
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass


def _ingest(repo: Path, chroma_path: str, collection_name: str, fixture: Path) -> int:
    from tools.ingestion.chroma_ingest_pipeline import load_documents, run_ingestion

    docs = load_documents(fixture)
    return run_ingestion(
        docs,
        chromadb_path=chroma_path,
        collection_name=collection_name,
    )


def _peek_collection(chroma_path: str, collection_name: str) -> dict:
    import chromadb  # type: ignore

    client = chromadb.PersistentClient(path=chroma_path)
    col = client.get_collection(collection_name)
    total = col.count()
    peek = col.get(include=["embeddings", "metadatas", "documents"], limit=1)
    embs = peek.get("embeddings")
    dim = 0
    if embs is not None and len(embs) > 0 and embs[0] is not None:
        dim = len(embs[0])
    meta0 = (peek.get("metadatas") or [None])[0] or {}
    return {
        "collection": collection_name,
        "count": total,
        "embedding_dim_observed": dim,
        "sample_metadata_keys": sorted(meta0.keys()),
        "sample_document_prefix": ((peek.get("documents") or [""])[0] or "")[:120],
    }


def _run_c0(repo: Path, chroma_path: str) -> dict:
    os.environ["EMBEDDING_ENABLED"] = "true"
    os.chdir(repo)

    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.runtime.contracts.route_contract import RouteContract
    from apps_rg.runtime.bindings.c0_binding import c0_retrieve_apps_rg

    route = RouteContract.__new__(RouteContract)
    object.__setattr__(route, "grounding_required", True)
    object.__setattr__(route, "request_id", "prove-fv-c0")
    object.__setattr__(route, "run_id", "prove-run")
    object.__setattr__(route, "app_id", "apps_rg")
    object.__setattr__(route, "trace_id", "prove-trace")

    vr = ValidatedRequest.__new__(ValidatedRequest)
    object.__setattr__(vr, "request_id", "prove-fv-c0")
    object.__setattr__(vr, "run_id", "prove-run")
    object.__setattr__(vr, "app_id", "apps_rg")
    object.__setattr__(vr, "trace_id", "prove-trace")
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

    fec = c0_retrieve_apps_rg(route, vr, chromadb_path=chroma_path)
    fv_items = [it for it in fec.evidence_items if getattr(it, "source_type", "") == "fact_vectors"]
    joined = "\n".join(getattr(it, "content", "") for it in fv_items)
    anchors = (
        "SMOKE_C0_HEADLINE_ANCHOR",
        "SMOKE_C0_EXEC_SUMMARY_ANCHOR",
        "SMOKE_C0_COMPETENCIES_ANCHOR",
        "SMOKE_C0_UNIFY_BULLETS_ANCHOR",
        "SMOKE_C0_UNIFY_NARR_ANCHOR",
    )
    lane_hits = {a: (a in joined) for a in anchors}
    return {
        "chroma_path": chroma_path,
        "chroma_retrieved": any("dense:fact_vectors:" in str(x) for x in (fec.dense_search_refs or ())),
        "dense_search_refs": list(fec.dense_search_refs or ()),
        "support_status": fec.support_status,
        "fact_vectors_evidence_count": len(fv_items),
        "lane_anchor_hits": lane_hits,
        "citation_map_len": len(fec.citation_map or ()),
        "source_lineage_map_len": len(fec.source_lineage_map or ()),
        "freshness_receipts_len": len(fec.freshness_receipts or ()),
        "citation_map_sample": list((fec.citation_map or ())[:8]),
        "support_status_per_item_sample": [
            getattr(it, "support_status", "") for it in fv_items[:5]
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest + prove apps_rg fact_vectors C0 runtime.")
    parser.add_argument("--repo-root", type=Path, default=None, help="Repo root (default: infer).")
    parser.add_argument(
        "--chromadb-path",
        type=str,
        default=None,
        help="Chroma persist dir (default: CHROMA_PERSIST_DIR or data/cache/chromadb).",
    )
    parser.add_argument("--collection", type=str, default="fact_vectors")
    parser.add_argument(
        "--reset-collection",
        action="store_true",
        help="Delete target collection before ingest (recommended for repeat runs).",
    )
    parser.add_argument("--skip-ingest", action="store_true", help="Only peek + C0 proof.")
    args = parser.parse_args(argv)

    repo = args.repo_root.resolve() if args.repo_root else _repo_root()
    rs = str(repo)
    if rs not in sys.path:
        sys.path.insert(0, rs)
    chroma_path = args.chromadb_path or _default_chroma_path(repo)
    fixture = _smoke_fixture(repo)
    out_dir = _artifact_dir(repo)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not fixture.is_file():
        print(f"ERROR: fixture missing: {fixture}", file=sys.stderr)
        return 2

    ingested: int | None = None
    if not args.skip_ingest:
        if args.reset_collection:
            _reset_collection(chroma_path, args.collection)
        ingested = _ingest(repo, chroma_path, args.collection, fixture)

    peek = _peek_collection(chroma_path, args.collection)
    ingest_proof: dict = {
        "fixture": str(fixture),
        "chromadb_path": chroma_path,
        "collection": args.collection,
        **peek,
    }
    if ingested is not None:
        ingest_proof["documents_ingested_last_run"] = ingested
    else:
        ingest_proof["documents_ingested_last_run"] = None
        ingest_proof["ingest_skipped"] = True
    (out_dir / "ingestion_proof.json").write_text(
        json.dumps(ingest_proof, indent=2), encoding="utf-8"
    )

    c0_proof = _run_c0(repo, chroma_path)
    (out_dir / "c0_runtime_proof.json").write_text(
        json.dumps(c0_proof, indent=2), encoding="utf-8"
    )

    print(json.dumps({"ingestion_proof": str(out_dir / "ingestion_proof.json"), "c0_runtime_proof": str(out_dir / "c0_runtime_proof.json")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
