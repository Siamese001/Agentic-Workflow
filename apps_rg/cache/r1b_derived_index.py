"""W11 — derived R1B lookup index projected from UWG-admitted durable truth."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.cache.r1b_constants import (
    CACHE_GRAIN_ROLE_TARGET_RUN,
    C0_FACT_VECTORS_COLLECTION,
    R1B_NOT_C0_FACT_VECTORS,
    R1B_STORAGE_SUBSYSTEM,
    STORAGE_TIER_UWG_ADMITTED,
)
from apps_rg.cache.r1b_intent_vector import (
    cosine_similarity,
    intent_text_from_request,
    normalized_intent_digest,
    pseudo_vector_from_digest,
    vector_payload,
)
from apps_rg.cache.r1b_models import HistoricalIntentRecord, HistoricalOutputChunk
from apps_rg.cache.r1b_store import R1BSemanticCacheStore, default_store_root

DERIVED_INDEX_SUBDIR = "derived_index"
INDEX_MANIFEST = "manifest.json"
INTENT_VECTORS_SUBDIR = "intent_vectors"
BY_DIGEST_SUBDIR = "by_digest"
DURABLE_INTENTS_SUBDIR = Path("durable") / "uwg_admitted" / "intents"
DURABLE_CHUNKS_SUBDIR = Path("durable") / "uwg_admitted" / "chunks"

INDEXED_FIELDS: tuple[str, ...] = (
    "record_id",
    "normalized_intent_digest",
    "request_intent_vector",
    "cache_grain",
    "cache_admissible",
    "prompt_profile_hash",
    "gate_profile_hash",
    "source_run_id",
    "durable_bundle_ref",
)

EXCLUDED_FROM_INDEX: tuple[str, ...] = (
    "child_chunk_vectors",
    "chunk_id_as_lookup_key",
    "c0_fact_vectors",
    "fixture_proof_mirror",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def derived_index_root(projection_root: Path | str) -> Path:
    return Path(projection_root) / DERIVED_INDEX_SUBDIR


def durable_truth_root(projection_root: Path | str) -> Path:
    return Path(projection_root) / "durable" / "uwg_admitted"


def derived_index_available(projection_root: Path | str) -> bool:
    return (derived_index_root(projection_root) / INDEX_MANIFEST).is_file()


@dataclass
class IndexRefreshReceipt:
    refreshed_at_utc: str
    entries_projected: int
    durable_bundles_scanned: int
    index_path: str
    durable_truth_path: str
    indexed_fields: tuple[str, ...] = INDEXED_FIELDS
    excluded_fields: tuple[str, ...] = EXCLUDED_FROM_INDEX
    child_chunks_indexed_as_independent_identities: bool = False
    c0_fact_vectors_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "refreshed_at_utc": self.refreshed_at_utc,
            "entries_projected": self.entries_projected,
            "durable_bundles_scanned": self.durable_bundles_scanned,
            "index_path": self.index_path,
            "durable_truth_path": self.durable_truth_path,
            "indexed_fields": list(self.indexed_fields),
            "excluded_fields": list(self.excluded_fields),
            "child_chunks_indexed_as_independent_identities": self.child_chunks_indexed_as_independent_identities,
            "c0_fact_vectors_used": self.c0_fact_vectors_used,
            "storage_subsystem": R1B_STORAGE_SUBSYSTEM,
            "index_surface": "derived_read_only",
            "durable_truth_tier": STORAGE_TIER_UWG_ADMITTED,
        }


def _load_durable_bundle(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def project_durable_to_derived_index(projection_root: Path | str) -> IndexRefreshReceipt:
    """Project UWG-admitted durable bundles into derived intent-vector index (W11)."""
    root = Path(projection_root)
    idx_root = derived_index_root(root)
    vec_dir = idx_root / INTENT_VECTORS_SUBDIR
    digest_dir = idx_root / BY_DIGEST_SUBDIR
    for d in (vec_dir, digest_dir):
        d.mkdir(parents=True, exist_ok=True)

    durable_intents = root / DURABLE_INTENTS_SUBDIR
    scanned = 0
    projected = 0
    for bundle_path in sorted(durable_intents.glob("*.json")):
        scanned += 1
        bundle = _load_durable_bundle(bundle_path)
        if not bundle:
            continue
        if bundle.get("storage_tier") != STORAGE_TIER_UWG_ADMITTED:
            continue
        parent = bundle.get("parent_intent_record") or {}
        if not isinstance(parent, dict):
            continue
        record = HistoricalIntentRecord.from_dict(parent)
        if not record.cache_admissible:
            continue
        digest = record.normalized_intent_digest
        vec = pseudo_vector_from_digest(digest)
        entry = {
            "record_id": record.record_id,
            "normalized_intent_digest": digest,
            "cache_grain": record.cache_grain,
            "cache_admissible": record.cache_admissible,
            "prompt_profile_hash": record.prompt_profile_hash,
            "gate_profile_hash": record.gate_profile_hash,
            "source_run_id": record.source_run_id,
            "durable_bundle_ref": str(bundle_path.relative_to(root)),
            "lookup_anchor": "HistoricalIntentRecord.request_intent_vector",
            "child_chunk_count": len(bundle.get("child_chunks") or []),
            "child_chunks_independent_index_identities": False,
            "c0_fact_vectors_consulted": False,
            "c0_collection_excluded": C0_FACT_VECTORS_COLLECTION,
            "vector": vector_payload(digest),
            "governance_receipt": bundle.get("governance_receipt"),
            "uwg_commit_receipt_id": bundle.get("uwg_commit_receipt_id", ""),
        }
        (vec_dir / f"{record.record_id}.json").write_text(
            json.dumps(entry, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (digest_dir / f"{digest}.json").write_text(
            json.dumps({"record_id": record.record_id}, indent=2) + "\n",
            encoding="utf-8",
        )
        projected += 1

    manifest = {
        "schema_version": "2026-05-18-r1b-w11-w12-v1",
        "refreshed_at_utc": _utc_now(),
        "entries_count": projected,
        "durable_truth_path": str(durable_truth_root(root)),
        "derived_index_path": str(idx_root),
        "indexed_fields": list(INDEXED_FIELDS),
        "excluded_fields": list(EXCLUDED_FROM_INDEX),
        "lookup_anchor": "HistoricalIntentRecord.request_intent_vector",
        "child_chunks_parent_bound_only": True,
        "not_c0_fact_vectors": True,
        "r1b_vs_c0": R1B_NOT_C0_FACT_VECTORS,
    }
    (idx_root / INDEX_MANIFEST).write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return IndexRefreshReceipt(
        refreshed_at_utc=manifest["refreshed_at_utc"],
        entries_projected=projected,
        durable_bundles_scanned=scanned,
        index_path=str(idx_root),
        durable_truth_path=str(durable_truth_root(root)),
    )


def list_derived_index_record_ids(projection_root: Path | str) -> list[str]:
    vec_dir = derived_index_root(projection_root) / INTENT_VECTORS_SUBDIR
    if not vec_dir.is_dir():
        return []
    return sorted(p.stem for p in vec_dir.glob("*.json"))


def load_derived_index_entry(
    projection_root: Path | str,
    record_id: str,
) -> dict[str, Any] | None:
    path = derived_index_root(projection_root) / INTENT_VECTORS_SUBDIR / f"{record_id}.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def load_durable_record_and_chunks(
    projection_root: Path | str,
    record_id: str,
) -> tuple[HistoricalIntentRecord | None, list[HistoricalOutputChunk]]:
    """Load truth from durable projection — chunks always parent-bound."""
    root = Path(projection_root)
    bundle_path = root / DURABLE_INTENTS_SUBDIR / f"{record_id}.json"
    bundle = _load_durable_bundle(bundle_path)
    if not bundle:
        return None, []
    parent = bundle.get("parent_intent_record") or {}
    record = HistoricalIntentRecord.from_dict(parent) if isinstance(parent, dict) else None
    chunks_raw = bundle.get("child_chunks") or []
    chunks = [
        HistoricalOutputChunk.from_dict(c)
        for c in chunks_raw
        if isinstance(c, dict)
    ]
    chunk_dir = root / DURABLE_CHUNKS_SUBDIR / record_id
    if chunk_dir.is_dir() and not chunks:
        for cf in sorted(chunk_dir.glob("*.json")):
            try:
                data = json.loads(cf.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    chunks.append(HistoricalOutputChunk.from_dict(data))
            except (json.JSONDecodeError, OSError):
                continue
    return record, chunks


def lookup_r1b_via_derived_index(
    raw_request: dict[str, Any],
    *,
    projection_root: Path | str,
    similarity_threshold: float = 0.88,
    query_prompt_hash: str = "",
    query_gate_hash: str = "",
) -> tuple[Any | None, list[dict[str, Any]]]:
    """Lookup using derived index vectors; load record/chunks from durable truth on hit."""
    from apps_rg.cache.r1b_compatibility import assess_candidate_for_reuse, compatibility_report_row
    from apps_rg.cache.r1b_retrieval import R1BLookupHit

    root = Path(projection_root)
    if not derived_index_available(root):
        st = R1BSemanticCacheStore(root)
        from apps_rg.cache.r1b_retrieval import lookup_r1b_with_compatibility_report

        return lookup_r1b_with_compatibility_report(
            raw_request,
            store=st,
            similarity_threshold=similarity_threshold,
            query_prompt_hash=query_prompt_hash,
            query_gate_hash=query_gate_hash,
        )

    intent_text = intent_text_from_request(raw_request)
    query_digest = normalized_intent_digest(intent_text)
    query_vec = pseudo_vector_from_digest(query_digest)
    report: list[dict[str, Any]] = []
    best: R1BLookupHit | None = None

    for rid in list_derived_index_record_ids(root):
        entry = load_derived_index_entry(root, rid)
        if not entry or not entry.get("cache_admissible"):
            continue
        vec_data = entry.get("vector") or {}
        vals = vec_data.get("values") if isinstance(vec_data, dict) else None
        if not isinstance(vals, list):
            vals = pseudo_vector_from_digest(str(entry.get("normalized_intent_digest") or ""))
        sim = cosine_similarity(query_vec, [float(x) for x in vals])
        record, chunks = load_durable_record_and_chunks(root, rid)
        if record is None:
            continue
        verdict = assess_candidate_for_reuse(
            record,
            chunks,
            query_digest=query_digest,
            query_prompt_hash=query_prompt_hash,
            query_gate_hash=query_gate_hash,
        )
        report.append(
            compatibility_report_row(
                candidate_record_id=rid,
                verdict=verdict,
                similarity=sim,
            )
        )
        report[-1]["lookup_surface"] = "derived_index"
        report[-1]["durable_truth_ref"] = entry.get("durable_bundle_ref")
        if not record.cache_admissible or not verdict.admissible or sim < similarity_threshold:
            continue
        if best is None or sim > best.similarity:
            best = R1BLookupHit(record=record, chunks=chunks, similarity=sim, verdict=verdict)

    return best, report


def build_durable_truth_vs_index_matrix() -> list[dict[str, Any]]:
    return [
        {
            "layer": "durable_uwg_admitted_projection",
            "role": "production_truth",
            "path": "durable/uwg_admitted/",
            "contains": "parent_intent_record, child_chunks, governance_receipt, uwg_commit_receipt_id",
        },
        {
            "layer": "derived_index",
            "role": "read_surface_only",
            "path": "derived_index/intent_vectors/",
            "contains": "intent vectors + metadata pointers only",
        },
        {
            "layer": "fixture_mirror",
            "role": "test_proof_only",
            "path": "intents/, chunks/ (R1BSemanticCacheStore)",
            "contains": "non-durable mirror for W7-W10b fixtures",
        },
        {
            "layer": "c0_fact_vectors",
            "role": "excluded",
            "path": "N/A for R1B",
            "contains": "never used for R1B lookup identity",
        },
    ]


def resolve_r1b_projection_root(
    *,
    store_root: Path | str | None = None,
    artifact_dir: Path | str | None = None,
) -> Path:
    env = os.environ.get("APPS_RG_R1B_CACHE_ROOT", "").strip()
    if env:
        p = Path(env)
        return p if p.is_absolute() else (Path.cwd() / p).resolve()
    if store_root:
        return Path(store_root)
    if artifact_dir:
        return Path(artifact_dir)
    return default_store_root()


__all__ = [
    "DERIVED_INDEX_SUBDIR",
    "EXCLUDED_FROM_INDEX",
    "INDEXED_FIELDS",
    "IndexRefreshReceipt",
    "build_durable_truth_vs_index_matrix",
    "derived_index_available",
    "derived_index_root",
    "durable_truth_root",
    "list_derived_index_record_ids",
    "load_derived_index_entry",
    "load_durable_record_and_chunks",
    "lookup_r1b_via_derived_index",
    "project_durable_to_derived_index",
    "resolve_r1b_projection_root",
]
