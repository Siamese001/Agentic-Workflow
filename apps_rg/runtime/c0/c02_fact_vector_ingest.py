"""C0-P1: ingest C0.2 claim-sized atoms into Chroma ``fact_vectors`` (one atom = one chunk)."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.c0.constants import (
    CONFIDENCE_PENDING,
    NOT_PROOF,
    PROOF_ELIGIBLE,
    REPO_ROOT,
    SOURCE_PRIOR_VARIANT,
    TARGETING_ONLY,
)
from apps_rg.runtime.c0.c02_evidence_fetch import C02Atom
from apps_rg.tools.fact_vector_ingest import FactVectorChunk, FactVectorSchema

_logger = logging.getLogger(__name__)

INGEST_RECEIPT_NAME = "c02_fact_vectors_ingest_receipt.json"
CHUNK_ID_PREFIX = "apps_rg:fv:"


def c02_atom_ingest_eligible(atom: C02Atom) -> tuple[bool, str]:
    """Return (eligible, reason) for fact_vectors upsert."""
    conf = str(atom.get("confidence") or "").upper()
    proof = str(atom.get("proof_status") or "")
    text = str(atom.get("text_to_embed") or "").strip()
    if not text or len(text) < 12:
        return False, "text_too_short"
    if conf == CONFIDENCE_PENDING:
        return False, "pending_trace_not_ingested"
    if proof in (NOT_PROOF, TARGETING_ONLY):
        return False, f"proof_status_{proof}"
    if atom.get("source_type") == SOURCE_PRIOR_VARIANT and proof != PROOF_ELIGIBLE:
        return False, "prior_variant_not_proof_eligible"
    if proof != PROOF_ELIGIBLE and conf != "HIGH":
        return False, "requires_proof_eligible_or_high_confidence"
    return True, "eligible"


def chunk_to_chroma_document(chunk: FactVectorChunk, atom: C02Atom | None = None) -> dict[str, Any]:
    """Chroma JSONL row with optional C0.2 scalar metadata."""
    doc = chunk.to_chroma_document()
    if atom is not None:
        fid = str(atom.get("fact_id") or "")
        doc["metadata"]["candidate_fact_id"] = fid
        doc["metadata"]["confidence"] = str(atom.get("confidence") or "")
        doc["metadata"]["proof_status"] = str(atom.get("proof_status") or "")
        doc["metadata"]["source_span_ref"] = str(atom.get("source_span_ref") or "")[:500]
    return doc


def c02_atom_to_fact_vector_chunk(
    atom: C02Atom,
    *,
    section_id: str,
    ledger_version_hash: str,
) -> FactVectorChunk:
    """Map one C0.2 atom to a single fact_vectors chunk (no paragraph splitting)."""
    fid = str(atom.get("fact_id") or "").strip()
    text = str(atom.get("text_to_embed") or "").strip()[:2000]
    allowed = list(atom.get("allowed_sections") or [section_id])
    section_targets = ",".join(sorted({str(s).strip() for s in allowed if str(s).strip()}))
    skills = [str(t) for t in (atom.get("skill_tags") or []) if str(t).strip()]
    chunk_id = f"{CHUNK_ID_PREFIX}{fid}"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:32]
    return FactVectorChunk(
        chunk_id=chunk_id,
        content=text,
        app="apps_rg",
        source_class=str(atom.get("source_class") or "candidate_profile"),
        ingestion_timestamp=datetime.now(timezone.utc).isoformat(),
        source_document_id=fid,
        source_version_hash=ledger_version_hash or digest,
        skills_mentioned=skills,
        section_type=section_id,
        company="",
        role="",
        section_targets=section_targets or section_id,
        citation_anchor=str(atom.get("source_span_ref") or f"ledger:{fid}"),
        chunk_digest=digest,
        authority_class="PRIMARY" if atom.get("proof_status") == PROOF_ELIGIBLE else "SUPPORTING",
    )


def atoms_to_fact_vector_chunks(
    atoms: list[C02Atom],
    *,
    section_id: str,
    ledger_version_hash: str = "",
) -> tuple[list[FactVectorChunk], list[C02Atom], list[dict[str, str]]]:
    """Filter eligible atoms and build chunks (parallel atom list for metadata)."""
    schema = FactVectorSchema()
    chunks: list[FactVectorChunk] = []
    chunk_atoms: list[C02Atom] = []
    skipped: list[dict[str, str]] = []
    for atom in atoms:
        ok, reason = c02_atom_ingest_eligible(atom)
        fid = str(atom.get("fact_id") or "")
        if not ok:
            skipped.append({"fact_id": fid, "reason": reason})
            continue
        chunk = c02_atom_to_fact_vector_chunk(
            atom,
            section_id=section_id,
            ledger_version_hash=ledger_version_hash,
        )
        valid, errs = schema.validate_chunk(chunk)
        if not valid:
            skipped.append({"fact_id": fid, "reason": ";".join(errs)})
            continue
        chunks.append(chunk)
        chunk_atoms.append(atom)
    return chunks, chunk_atoms, skipped


def _ledger_version_hash(repo_root: Path) -> str:
    from apps_rg.fact_inventory.candidate_fact_ledger import default_ledger_path

    path = default_ledger_path(repo_root)
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()[:32]


def upsert_fact_vector_chunks(
    chunks: list[FactVectorChunk],
    *,
    chroma_path: str,
    collection_name: str = "fact_vectors",
    atoms: list[C02Atom] | None = None,
) -> int:
    """Upsert chunks into Chroma (stable ids — safe to re-run per section)."""
    if not chunks:
        return 0
    import chromadb

    from apps_rg.runtime.chroma_precomputed_collection import (
        get_precomputed_embeddings_collection,
    )
    from apps_rg.runtime.embedding_settings import (
        apply_apps_rg_embedding_env_guards,
        assert_dense_retrieval_allowed,
        load_bge_sentence_transformer,
        resolve_apps_rg_embedding_settings,
    )
    from tools.ingestion.chroma_ingest_pipeline import embed_text

    apply_apps_rg_embedding_env_guards(chroma_persist_dir=chroma_path)
    settings = resolve_apps_rg_embedding_settings(chroma_persist_dir=chroma_path)
    assert_dense_retrieval_allowed(settings)
    model = load_bge_sentence_transformer(settings)
    client = chromadb.PersistentClient(path=chroma_path)
    collection = get_precomputed_embeddings_collection(
        client,
        collection_name,
        metadata={"hnsw:space": "cosine", "collection_role": "fact_vectors"},
    )
    atom_list = atoms if atoms is not None and len(atoms) == len(chunks) else [None] * len(chunks)
    docs = [
        chunk_to_chroma_document(c, a)
        for c, a in zip(chunks, atom_list, strict=True)
    ]
    ids = [d["id"] for d in docs]
    texts = [d["text"] for d in docs]
    embeddings = [embed_text(model, t) for t in texts]
    metadatas = [
        {
            k: str(v) if not isinstance(v, (str, int, float, bool)) else v
            for k, v in d["metadata"].items()
        }
        for d in docs
    ]
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    return len(chunks)


def maybe_upsert_c02_fact_vectors(
    atoms: list[C02Atom],
    *,
    section_id: str,
    artifact_dir: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Best-effort C0.2 → fact_vectors upsert; never blocks evidence room on failure."""
    root = repo_root or REPO_ROOT
    chroma_path = os.environ.get("CHROMA_PERSIST_DIR", "").strip()
    receipt: dict[str, Any] = {
        "schema_version": "c02_fact_vectors_ingest_v1",
        "section_id": section_id,
        "chroma_path": chroma_path or None,
        "attempted": False,
        "upserted_count": 0,
        "skipped_count": 0,
        "skipped": [],
        "status": "NOT_APPLICABLE",
        "reason": "",
    }
    if not chroma_path:
        receipt["reason"] = "CHROMA_PERSIST_DIR unset"
        _write_receipt(artifact_dir, receipt)
        return receipt

    from apps_rg.runtime.embedding_settings import (
        apply_apps_rg_embedding_env_guards,
        bootstrap_apps_rg_embedding_env,
        resolve_apps_rg_embedding_settings,
    )

    bootstrap_apps_rg_embedding_env(repo_root=root)
    apply_apps_rg_embedding_env_guards(chroma_persist_dir=chroma_path or None)
    settings = resolve_apps_rg_embedding_settings(chroma_persist_dir=chroma_path)
    if not settings.embeddings_enabled or settings.route_result == "FAIL_CLOSED":
        receipt["reason"] = settings.decisive_reason or "embeddings_disabled"
        _write_receipt(artifact_dir, receipt)
        return receipt

    receipt["attempted"] = True
    ledger_hash = _ledger_version_hash(root)
    chunks, chunk_atoms, skipped = atoms_to_fact_vector_chunks(
        atoms,
        section_id=section_id,
        ledger_version_hash=ledger_hash,
    )
    receipt["skipped"] = skipped[:50]
    receipt["skipped_count"] = len(skipped)
    try:
        count = upsert_fact_vector_chunks(
            chunks,
            chroma_path=chroma_path,
            atoms=chunk_atoms,
        )
        receipt["upserted_count"] = count
        receipt["status"] = "PASS" if count else "EMPTY"
        receipt["reason"] = "upsert_ok" if count else "no_eligible_atoms"
    except Exception as exc:  # guardian: allow-broad-exception -- P2 burndown: upsert failure recorded in receipt  # guardian: allow-log-and-swallow -- P2 burndown: upsert failure recorded in receipt
        receipt["status"] = "FAIL"
        receipt["reason"] = f"{type(exc).__name__}:{exc}"
        _logger.warning("C0.2 fact_vectors upsert failed: %s", exc)
    _write_receipt(artifact_dir, receipt)
    return receipt


def _write_receipt(artifact_dir: Path | None, receipt: dict[str, Any]) -> None:
    if artifact_dir is None:
        return
    try:
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / INGEST_RECEIPT_NAME).write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError:  # guardian: allow-silent-swallow -- P2 burndown: ingest receipt is best-effort
        pass


__all__ = [
    "INGEST_RECEIPT_NAME",
    "atoms_to_fact_vector_chunks",
    "c02_atom_ingest_eligible",
    "c02_atom_to_fact_vector_chunk",
    "maybe_upsert_c02_fact_vectors",
    "upsert_fact_vector_chunks",
]
