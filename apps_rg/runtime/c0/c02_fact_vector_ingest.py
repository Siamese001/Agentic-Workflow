"""C0-P1: ingest C0.2 claim-sized atoms into Chroma ``fact_vectors`` (one atom = one chunk)."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.runtime.c0.c02_evidence_fetch import C02Atom
from apps_rg.runtime.c0.constants import (
    CONFIDENCE_PENDING,
    NOT_PROOF,
    PROOF_ELIGIBLE,
    REPO_ROOT,
    SOURCE_PRIOR_VARIANT,
    TARGETING_ONLY,
)
from apps_rg.runtime.c0.fact_vector_write_back import (
    ENRICH,
    FUSE,
    GENERATED,
    PROMOTION_MODE_DEFERRED,
    STAGE_FOR_FACT_VECTORS,
    STAGING_COLLECTION_NAME,
    decide_write_back,
    promote_staged_fact_vectors,
    promotion_mode,
)
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
        # Write-back discipline provenance — carried so the staging→live promotion gate can
        # re-validate the row from its own metadata (hostile verifier; never trust prior validation).
        doc["metadata"]["source_type"] = str(atom.get("source_type") or "")
        doc["metadata"]["write_back_operation"] = str(atom.get("write_back_operation") or "")
        doc["metadata"]["run_id"] = str(atom.get("run_id") or "")
        doc["metadata"]["staged_at_utc"] = str(atom.get("staged_at_utc") or "")
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
    # Source class is atom-driven (schema allows candidate_profile + project_evidence). Employment
    # achievements seed as project_evidence; skills-ledger facts as candidate_profile — the FEC needs
    # >=2 normative source classes (single-class evidence is WEAK). Clamp to the allowed pair.
    sc_hint = str(atom.get("fact_vector_source_class") or "").strip()
    source_class = sc_hint if sc_hint in ("candidate_profile", "project_evidence") else "candidate_profile"
    return FactVectorChunk(
        chunk_id=chunk_id,
        content=text,
        app="apps_rg",
        source_class=source_class,
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
    run_id: str = "",
    staged_at_utc: str = "",
) -> tuple[list[FactVectorChunk], list[C02Atom], list[dict[str, str]]]:
    """Filter eligible atoms and build chunks (parallel atom list for metadata)."""
    schema = FactVectorSchema()
    chunks: list[FactVectorChunk] = []
    chunk_atoms: list[C02Atom] = []
    skipped: list[dict[str, str]] = []
    for atom in atoms:
        fid = str(atom.get("fact_id") or "")
        # Write-back discipline FIRST: only a transform (extract/fuse/enrich) of grounded content
        # may be staged for fact_vectors. Generated/synthesized → semantic-cache domain; a claimed
        # transform without source provenance → rejected (fail closed).
        decision = decide_write_back(atom)
        if decision.route != STAGE_FOR_FACT_VECTORS:
            skipped.append(
                {"fact_id": fid, "reason": f"route_{decision.route}:{decision.operation}:{decision.reason}"}
            )
            continue
        ok, reason = c02_atom_ingest_eligible(atom)
        if not ok:
            skipped.append({"fact_id": fid, "reason": reason})
            continue
        # Stamp the resolved operation so the promotion gate can re-validate from metadata.
        atom_staged: C02Atom = {
            **atom,
            "write_back_operation": decision.operation,
            "run_id": run_id,
            "staged_at_utc": staged_at_utc,
        }
        chunk = c02_atom_to_fact_vector_chunk(
            atom_staged,
            section_id=section_id,
            ledger_version_hash=ledger_version_hash,
        )
        valid, errs = schema.validate_chunk(chunk)
        if not valid:
            skipped.append({"fact_id": fid, "reason": ";".join(errs)})
            continue
        chunks.append(chunk)
        chunk_atoms.append(atom_staged)
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
    from agentic_core.L4_state.utils.client.chroma_client import (
        chromadb_module as chromadb,
    )
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
    from apps_rg.runtime.c0.chroma_persistent_client import ensure_apps_rg_chroma_client

    client = ensure_apps_rg_chroma_client(chroma_path)
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
    run_id: str | None = None,
    promotion_mode_override: str | None = None,
) -> dict[str, Any]:
    """Best-effort C0.2 → fact_vectors upsert; never blocks evidence room on failure."""
    root = repo_root or REPO_ROOT
    chroma_path = os.environ.get("CHROMA_PERSIST_DIR", "").strip()
    resolved_run_id = str(run_id or (artifact_dir.name if artifact_dir is not None else "")).strip()
    resolved_promotion_mode = promotion_mode(promotion_mode_override)
    staged_at_utc = datetime.now(timezone.utc).isoformat()
    receipt: dict[str, Any] = {
        "schema_version": "c02_fact_vectors_ingest_v1",
        "section_id": section_id,
        "chroma_path": chroma_path or None,
        "run_id": resolved_run_id,
        "promotion_mode": resolved_promotion_mode,
        "staged_at_utc": staged_at_utc,
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
        run_id=resolved_run_id,
        staged_at_utc=staged_at_utc,
    )
    receipt["skipped"] = skipped[:50]
    receipt["skipped_count"] = len(skipped)
    # Write-back discipline summary: operations of staged atoms + where the rest were routed.
    operations: dict[str, int] = {}
    for a in chunk_atoms:
        op = str(a.get("write_back_operation") or "")
        operations[op] = operations.get(op, 0) + 1
    receipt["operations"] = operations
    receipt["routed_to_semantic_cache"] = sum(
        1 for s in skipped if str(s.get("reason", "")).startswith("route_semantic_cache")
    )
    receipt["rejected_ungrounded"] = sum(
        1 for s in skipped if str(s.get("reason", "")).startswith("route_reject")
    )
    receipt["staged_count"] = 0
    receipt["promotion"] = {}
    try:
        # Write-backs land in the STAGING collection (off the live fact store)...
        staged = upsert_fact_vector_chunks(
            chunks,
            chroma_path=chroma_path,
            collection_name=STAGING_COLLECTION_NAME,
            atoms=chunk_atoms,
        )
        receipt["staged_count"] = staged
        if not staged:
            receipt["status"] = "EMPTY"
            receipt["reason"] = "no_eligible_atoms"
            _write_receipt(artifact_dir, receipt)
            return receipt
        if resolved_promotion_mode == PROMOTION_MODE_DEFERRED:
            receipt["status"] = "STAGED_DEFERRED"
            receipt["reason"] = "staged_awaiting_post_x3_promotion"
            _write_receipt(artifact_dir, receipt)
            return receipt
        # ...then the deterministic validation gate promotes them to live fact_vectors (or holds
        # for HITL when APPS_RG_FACT_VECTOR_PROMOTION_HITL=1). Live store stays populated for
        # grounded transforms — non-breaking vs the prior direct-upsert path.
        promotion = promote_staged_fact_vectors(
            chroma_path=chroma_path,
            artifact_dir=artifact_dir,
            run_id=resolved_run_id,
        )
        receipt["promotion"] = promotion
        receipt["upserted_count"] = int(promotion.get("promoted_count", 0))
        if promotion.get("status") == "HELD_FOR_HITL":
            receipt["status"] = "STAGED_HELD"
            receipt["reason"] = "staged_awaiting_hitl_promotion"
        elif receipt["upserted_count"]:
            receipt["status"] = "PASS"
            receipt["reason"] = "staged_and_promoted"
        elif staged:
            receipt["status"] = "STAGED"
            receipt["reason"] = "staged_none_promoted"
        else:
            receipt["status"] = "EMPTY"
            receipt["reason"] = "no_eligible_atoms"
    except Exception as exc:  # guardian: allow-broad-exception -- P2 burndown: upsert failure recorded in receipt  # guardian: allow-log-and-swallow -- P2 burndown: upsert failure recorded in receipt
        receipt["status"] = "FAIL"
        receipt["reason"] = f"{type(exc).__name__}:{exc}"
        _logger.warning("C0.2 fact_vectors staged write-back failed: %s", exc)
    _write_receipt(artifact_dir, receipt)
    return receipt


def _read_x3_for_artifact_dir(artifact_dir: Path | None) -> dict[str, Any]:
    if artifact_dir is None:
        return {}
    path = artifact_dir / "x3_disposition.json"
    if not path.is_file():
        return {}
    try:
        blob = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return blob if isinstance(blob, dict) else {}


def promote_deferred_c02_fact_vectors_after_x3(
    result: dict[str, Any],
    *,
    section_id: str = "",
) -> dict[str, Any]:
    """Post-X3 seam: in deferred mode, promote only rows for a run that reached X3_ALLOW."""
    resolved_mode = promotion_mode()
    receipt: dict[str, Any] = {
        "schema_version": "c02_fact_vectors_deferred_promotion_v1",
        "section_id": section_id,
        "promotion_mode": resolved_mode,
        "attempted": False,
        "status": "SKIPPED",
        "reason": "",
        "promotion": {},
    }
    if resolved_mode != PROMOTION_MODE_DEFERRED:
        receipt["reason"] = "promotion_mode_inline"
        return receipt
    chroma_path = os.environ.get("CHROMA_PERSIST_DIR", "").strip()
    receipt["chroma_path"] = chroma_path or None
    if not chroma_path:
        receipt["reason"] = "CHROMA_PERSIST_DIR unset"
        return receipt
    artifact_dir_raw = str(result.get("artifact_dir") or "").strip()
    artifact_dir = Path(artifact_dir_raw) if artifact_dir_raw else None
    x3_doc = _read_x3_for_artifact_dir(artifact_dir)
    resolved_run_id = str(
        result.get("run_id")
        or x3_doc.get("run_id")
        or (artifact_dir.name if artifact_dir is not None else "")
    ).strip()
    resolved_x3_code = str(x3_doc.get("x3_code") or result.get("x3_disposition") or "").strip()
    receipt["run_id"] = resolved_run_id
    receipt["x3_code"] = resolved_x3_code
    receipt["artifact_dir"] = str(artifact_dir) if artifact_dir is not None else ""
    receipt["attempted"] = True
    promotion = promote_staged_fact_vectors(
        chroma_path=chroma_path,
        artifact_dir=artifact_dir,
        run_id=resolved_run_id,
        x3_code=resolved_x3_code,
        require_x3_allow=True,
    )
    receipt["promotion"] = promotion
    receipt["status"] = str(promotion.get("status") or "UNKNOWN")
    receipt["reason"] = str(promotion.get("reason") or "")
    return receipt


def c05_fact_vector_write_back_atoms(c05: dict[str, Any]) -> list[C02Atom]:
    """Extract explicit C0.5 FUSE/ENRICH write-back atoms from the evidence-contract receipt."""
    raw_atoms = list(c05.get("fact_vector_write_back_atoms") or c05.get("write_back_atoms") or [])
    atoms: list[C02Atom] = []
    for raw in raw_atoms:
        if not isinstance(raw, dict):
            continue
        atom = dict(raw)
        operation = str(atom.get("write_back_operation") or atom.get("operation") or ENRICH).lower()
        if operation not in (FUSE, ENRICH, GENERATED):
            operation = ENRICH
        atom["write_back_operation"] = operation
        atoms.append(atom)
    return atoms


def maybe_upsert_c05_fact_vector_write_back_atoms(
    c05: dict[str, Any],
    *,
    section_id: str,
    artifact_dir: Path | None = None,
    repo_root: Path | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Stage explicit FUSE/ENRICH atoms produced by the C0.5 evidence-contract path."""
    atoms = c05_fact_vector_write_back_atoms(c05)
    receipt: dict[str, Any] = {
        "schema_version": "c05_fact_vector_write_back_v1",
        "section_id": section_id,
        "run_id": str(run_id or (artifact_dir.name if artifact_dir is not None else "")).strip(),
        "attempted": False,
        "atom_count": len(atoms),
        "status": "EMPTY",
        "reason": "no_c05_write_back_atoms",
        "ingest": {},
    }
    if not atoms:
        return receipt
    ingest = maybe_upsert_c02_fact_vectors(
        atoms,
        section_id=section_id,
        artifact_dir=None,
        repo_root=repo_root,
        run_id=receipt["run_id"],
    )
    receipt["attempted"] = True
    receipt["ingest"] = ingest
    receipt["status"] = str(ingest.get("status") or "UNKNOWN")
    receipt["reason"] = str(ingest.get("reason") or "")
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
    "c05_fact_vector_write_back_atoms",
    "maybe_upsert_c02_fact_vectors",
    "maybe_upsert_c05_fact_vector_write_back_atoms",
    "promote_deferred_c02_fact_vectors_after_x3",
    "upsert_fact_vector_chunks",
]
