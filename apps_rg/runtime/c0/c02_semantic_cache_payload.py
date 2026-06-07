"""C0 semantic-cache payload — per-section intent vector + query output (proposal only).

SPINE BOUNDARY
--------------
C0 PROPOSES. It does not commit. This module computes the per-section C0 **intent vector**
(BGE-M3 embedding of the section retrieval intent text) and serializes the C0 **query output**
(the retrieved fact atoms + scores + dense/sparse refs), then writes a durable run artifact
(``c02_semantic_cache_payload.json``). The artifact is inert evidence — it carries no write
authority. Durable admission happens only post-Exit through UWG → L4 (see
``apps_rg/cache/r1b_governed_receipt_emission.py``), which reads this artifact and attaches the
C0 intent vector + query output to the L4 namespace object + governed Chroma read surface.

Persisting this lets a subsequent section run reuse the C0 retrieval (semantic cache) instead
of recomputing the dense/sparse lanes, while staying inside the
L2-proposes / Exit-clears / UWG-commits / L4-stores law.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

C02_SEMANTIC_CACHE_PAYLOAD_ARTIFACT = "c02_semantic_cache_payload.json"
SCHEMA_VERSION = "c02_semantic_cache_payload_v1"

# Cap serialized query output so the artifact + L4 object stay bounded.
_MAX_QUERY_OUTPUT_ITEMS = 24
_MAX_TEXT_LEN = 400


def section_intent_text(
    *,
    section_id: str,
    target_company: str,
    target_role: str,
    jd_digest: str,
    query_terms: list[str] | None = None,
) -> str:
    """Canonical per-section C0 intent string used as the semantic-cache key text."""
    terms = " ".join(str(t).strip() for t in (query_terms or []) if str(t).strip())
    envelope = "|".join(
        (
            "apps_rg",
            "c0_section_intent",
            str(section_id).strip(),
            str(target_company).strip(),
            str(target_role).strip(),
            str(jd_digest).strip(),
        )
    )
    return f"{envelope}::{terms}".strip(": ")


def _digest(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def serialize_query_output(atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Bounded, durable serialization of the C0 retrieval result (the query output)."""
    out: list[dict[str, Any]] = []
    for atom in atoms[:_MAX_QUERY_OUTPUT_ITEMS]:
        if not isinstance(atom, dict):
            continue
        out.append(
            {
                "fact_id": str(atom.get("fact_id") or ""),
                "text": str(atom.get("text_to_embed") or atom.get("claim_text") or "")[:_MAX_TEXT_LEN],
                "confidence": str(atom.get("confidence") or ""),
                "proof_status": str(atom.get("proof_status") or ""),
                "retrieval_score": float(atom.get("retrieval_score") or 0.0),
                "source_type": str(atom.get("source_type") or ""),
            }
        )
    return out


def build_c02_semantic_cache_payload(
    *,
    section_id: str,
    atoms: list[dict[str, Any]],
    vector_query_receipt: dict[str, Any],
    target_company: str = "",
    target_role: str = "",
    jd_digest: str = "",
    run_id: str = "",
) -> dict[str, Any]:
    """Build the inert C0 semantic-cache payload (intent vector + query output)."""
    query_terms = [str(a.get("fact_id") or "") for a in atoms[:8] if isinstance(a, dict)]
    intent_text = section_intent_text(
        section_id=section_id,
        target_company=target_company,
        target_role=target_role,
        jd_digest=jd_digest,
        query_terms=query_terms,
    )
    intent_digest = _digest(intent_text)

    # Intent vector — BGE-M3 when embeddings active; inert ref otherwise (no fail-closed here,
    # because C0 must never block on cache proposal; product fail-closed is enforced at UWG).
    intent_vector: dict[str, Any]
    try:
        from apps_rg.cache.r1b_bge_embedding import embed_text_bge

        values = embed_text_bge(intent_text)
    except Exception:  # noqa: BLE001 - proposal artifact must never block C0
        values = None
    if values is not None:
        intent_vector = {
            "embedding_model": "BAAI/bge-m3",
            "embedding_provider": "bge_local",
            "dimensions": len(values),
            "values": values,
            "intent_digest": intent_digest,
        }
    else:
        intent_vector = {
            "embedding_model": "unavailable",
            "embedding_provider": "none",
            "dimensions": 0,
            "values": [],
            "intent_digest": intent_digest,
            "note": "BGE unavailable at C0 proposal time; intent vector ref only",
        }

    query_output = serialize_query_output(atoms)
    return {
        "schema_version": SCHEMA_VERSION,
        "section_id": section_id,
        "run_id": run_id,
        "proposal_status": "PENDING_UWG",
        "durable_write_authority": False,
        "spine_note": "C0 proposes; UWG commits; L4 stores. Not a write request.",
        "intent_text": intent_text,
        "intent_digest": intent_digest,
        "intent_vector": intent_vector,
        "query_output": query_output,
        "query_output_count": len(query_output),
        "dense_search_refs": list(vector_query_receipt.get("dense_search_refs") or []),
        "hybrid_enrichment_item_count": int(
            vector_query_receipt.get("hybrid_enrichment_item_count") or 0
        ),
        "target_company": target_company,
        "target_role": target_role,
    }


def write_c02_semantic_cache_payload(
    artifact_dir: Path,
    payload: dict[str, Any],
) -> Path | None:
    """Write the inert C0 semantic-cache payload artifact (best-effort, never blocks C0)."""
    try:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        path = artifact_dir / C02_SEMANTIC_CACHE_PAYLOAD_ARTIFACT
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return path
    except OSError:
        return None


def read_c02_semantic_cache_payload(artifact_dir: Path) -> dict[str, Any]:
    """Read the C0 semantic-cache payload from a run dir (empty dict when absent)."""
    path = artifact_dir / C02_SEMANTIC_CACHE_PAYLOAD_ARTIFACT
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
        return doc if isinstance(doc, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


__all__ = [
    "C02_SEMANTIC_CACHE_PAYLOAD_ARTIFACT",
    "SCHEMA_VERSION",
    "build_c02_semantic_cache_payload",
    "read_c02_semantic_cache_payload",
    "section_intent_text",
    "serialize_query_output",
    "write_c02_semantic_cache_payload",
]
