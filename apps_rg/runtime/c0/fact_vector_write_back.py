"""fact_vectors write-back discipline (plan apps-rg-fact-vector-writeback-discipline-67652c).

Customized mental model for apps_rg:

    Write back to ``fact_vectors`` ONLY when inference TRANSFORMS already-grounded content —
    never when it GENERATES new content. A chunk earns a spot in ``fact_vectors`` only if it
    traces back to a source document. Inference can reshape that grounding, not invent it.

Three safe write-back operations (the only ones allowed into ``fact_vectors``):
  * EXTRACT — atomize a retrieved/grounded paragraph into discrete claims.
  * FUSE    — reconcile multiple grounded chunks into one canonical fact (evidence fusion).
  * ENRICH  — add metadata to an existing grounded fact (confidence/role-relevance/recency).

Generated/synthesized output (LLM rewrites, JD-tailored phrasings, cover-letter prose) belongs in
the semantic cache as intent vectors (``apps_rg_r1b_semantic_cache``, tagged ``not_c0_fact_vectors``),
NOT in ``fact_vectors``. If you cannot point to the source document a fact came from, it does not
belong in ``fact_vectors``.

Gate: write-backs land in a staging collection (off the hot path); a deterministic validation check
(or HITL) promotes them to the live fact store. This module is pure for the classifier/grounding/
routing surface (no Chroma deps); only the promotion helper touches Chroma.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.c0.constants import (
    FORBIDDEN_PROOF_SOURCE_TYPES,
    NOT_PROOF,
    TARGETING_ONLY,
)

_logger = logging.getLogger(__name__)

# --- Operation taxonomy -----------------------------------------------------

# The three safe transforms of already-grounded content.
EXTRACT = "extract"
FUSE = "fuse"
ENRICH = "enrich"
# Everything else: synthesized / invented — forbidden in fact_vectors.
GENERATED = "generated"

ALLOWED_WRITE_BACK_OPERATIONS: frozenset[str] = frozenset({EXTRACT, FUSE, ENRICH})

# --- Routing ----------------------------------------------------------------

STAGE_FOR_FACT_VECTORS = "stage_for_fact_vectors"
SEMANTIC_CACHE = "semantic_cache"
REJECT = "reject"

STAGING_COLLECTION_NAME = "fact_vectors_staging"
LIVE_COLLECTION_NAME = "fact_vectors"

PROMOTION_HITL_ENV = "APPS_RG_FACT_VECTOR_PROMOTION_HITL"


@dataclass(frozen=True)
class WriteBackDecision:
    """Routing decision for one candidate write-back atom."""

    route: str  # STAGE_FOR_FACT_VECTORS | SEMANTIC_CACHE | REJECT
    operation: str  # extract | fuse | enrich | generated
    reason: str

    @property
    def stage(self) -> bool:
        return self.route == STAGE_FOR_FACT_VECTORS


def _norm(value: Any) -> str:
    return str(value or "").strip()


def is_generated_source(atom: dict[str, Any]) -> tuple[bool, str]:
    """True when the atom comes from a generated/non-grounded SOURCE (belongs in the semantic
    cache, not fact_vectors).

    Generated-by-nature ⇔ a forbidden ``source_type`` (jd_payload / briefing / company_research /
    generic_best_practice / governance_docs / …), OR ``proof_status`` of not_proof/targeting_only,
    OR an explicit ``write_back_operation == "generated"``. This is orthogonal to whether a specific
    source pointer is present (that is the REJECT condition, see ``has_source_pointer``).
    """
    if _norm(atom.get("write_back_operation")).lower() == GENERATED:
        return True, "declared_generated"
    proof = _norm(atom.get("proof_status"))
    if proof in (NOT_PROOF, TARGETING_ONLY):
        return True, f"proof_status_{proof or 'empty'}"
    source_type = _norm(atom.get("source_type"))
    if source_type and source_type in FORBIDDEN_PROOF_SOURCE_TYPES:
        return True, f"non_grounded_source:{source_type}"
    return False, ""


def has_source_pointer(atom: dict[str, Any]) -> bool:
    """True when the atom carries a concrete pointer to its source document."""
    return bool(_norm(atom.get("source_span_ref")) or _norm(atom.get("source_ref")))


def source_grounding_ok(atom: dict[str, Any]) -> tuple[bool, str]:
    """True when the atom traces back to a real source document: NOT a generated source AND it
    carries a concrete source pointer. The "can you point to the source document" test.
    """
    generated, greason = is_generated_source(atom)
    if generated:
        return False, greason
    if not _norm(atom.get("source_type")):
        return False, "no_source_type"
    if not has_source_pointer(atom):
        return False, "no_source_span_or_ref"
    return True, "grounded"


def classify_write_back_operation(atom: dict[str, Any]) -> tuple[str, str]:
    """Classify the write-back OPERATION TYPE: EXTRACT / FUSE / ENRICH / GENERATED.

    This is about *what kind of inference* produced the atom, independent of whether the specific
    source pointer is present (the REJECT condition lives in ``decide_write_back``). A generated
    source ⇒ GENERATED; an explicit fuse/enrich claim is honored; otherwise a grounded-class atom is
    an EXTRACT (atomization of retrieved content).
    """
    generated, greason = is_generated_source(atom)
    if generated:
        return GENERATED, greason
    declared = _norm(atom.get("write_back_operation")).lower()
    if declared in (FUSE, ENRICH):
        return declared, f"declared_{declared}"
    return EXTRACT, "grounded_atomization"


def decide_write_back(atom: dict[str, Any]) -> WriteBackDecision:
    """Single routing call: where does this candidate write-back atom go?

    * grounded transform (extract/fuse/enrich) with a source pointer ⇒ STAGE_FOR_FACT_VECTORS
    * generated/synthesized ⇒ SEMANTIC_CACHE (intent-vector domain, not fact_vectors)
    * a claimed transform with NO source provenance ⇒ REJECT (fail closed)
    """
    operation, reason = classify_write_back_operation(atom)
    if operation == GENERATED:
        return WriteBackDecision(SEMANTIC_CACHE, GENERATED, reason)
    if not _norm(atom.get("source_type")) or not has_source_pointer(atom):
        return WriteBackDecision(REJECT, operation, "no_source_provenance")
    return WriteBackDecision(STAGE_FOR_FACT_VECTORS, operation, reason)


def promotion_hitl_required(explicit: bool | None = None) -> bool:
    """Whether staging→live promotion must wait for human approval.

    ``explicit`` overrides; otherwise reads ``APPS_RG_FACT_VECTOR_PROMOTION_HITL`` (1/true/yes/on).
    """
    if explicit is not None:
        return bool(explicit)
    return _norm(os.environ.get(PROMOTION_HITL_ENV)).lower() in ("1", "true", "yes", "on")


def _staged_row_is_promotable(metadata: dict[str, Any]) -> tuple[bool, str]:
    """Hostile re-validation at promotion time — re-derive eligibility from the staged row's own
    metadata (never trust that it was validated on the way in).
    """
    op = _norm(metadata.get("write_back_operation")).lower()
    if op not in ALLOWED_WRITE_BACK_OPERATIONS:
        return False, f"operation_not_allowed:{op or 'missing'}"
    if not _norm(metadata.get("source_document_id")):
        return False, "missing_source_document_id"
    src = _norm(metadata.get("source_type"))
    if src and src in FORBIDDEN_PROOF_SOURCE_TYPES:
        return False, f"non_grounded_source:{src}"
    return True, "promotable"


def promote_staged_fact_vectors(
    *,
    chroma_path: str,
    require_hitl: bool | None = None,
    staging_collection: str = STAGING_COLLECTION_NAME,
    live_collection: str = LIVE_COLLECTION_NAME,
    limit: int | None = None,
) -> dict[str, Any]:
    """Promote validated staged chunks from ``fact_vectors_staging`` to live ``fact_vectors``.

    Deterministic gate: each staged row is re-validated (operation allowed + source provenance) from
    its own metadata. When HITL is required, rows are LEFT in staging (held, not lost). Otherwise
    promotable rows are upserted to live and removed from staging.

    Returns a promotion receipt (never raises — best-effort, off the hot path).
    """
    receipt: dict[str, Any] = {
        "schema_version": "fact_vector_promotion_v1",
        "staging_collection": staging_collection,
        "live_collection": live_collection,
        "staged_count": 0,
        "promoted_count": 0,
        "held_count": 0,
        "rejected_count": 0,
        "rejected": [],
        "hitl_required": promotion_hitl_required(require_hitl),
        "status": "NOT_APPLICABLE",
        "reason": "",
    }
    if not _norm(chroma_path):
        receipt["reason"] = "chroma_path_unset"
        return receipt

    try:
        # Route through the sanctioned L4 chromadb adapter rather than importing
        # the raw SDK directly in this runtime layer (infra-wiring gate).
        from agentic_core.L4_state.utils.client.chroma_client import (
            chromadb_module as chromadb,
        )

        from apps_rg.runtime.chroma_precomputed_collection import (
            get_precomputed_embeddings_collection,
        )

        client = chromadb.PersistentClient(path=chroma_path)
        staging = get_precomputed_embeddings_collection(
            client,
            staging_collection,
            metadata={"hnsw:space": "cosine", "collection_role": "fact_vectors_staging"},
        )
        staged = staging.get(include=["documents", "embeddings", "metadatas"])

        # NOTE: Chroma returns embeddings as a numpy array; ``<ndarray> or []`` raises the
        # "truth value of an array is ambiguous" error — extract with an explicit None check.
        def _as_list(value: Any) -> list[Any]:
            return list(value) if value is not None else []

        ids = _as_list(staged.get("ids"))
        receipt["staged_count"] = len(ids)
        if not ids:
            receipt["status"] = "EMPTY"
            receipt["reason"] = "no_staged_rows"
            return receipt

        documents = _as_list(staged.get("documents"))
        embeddings = _as_list(staged.get("embeddings"))
        metadatas = _as_list(staged.get("metadatas"))

        promotable: list[int] = []
        for i, meta in enumerate(metadatas):
            ok, why = _staged_row_is_promotable(meta or {})
            if ok:
                promotable.append(i)
            else:
                receipt["rejected"].append({"id": ids[i], "reason": why})
        receipt["rejected_count"] = len(receipt["rejected"])

        if limit is not None and limit >= 0:
            promotable = promotable[:limit]

        if receipt["hitl_required"]:
            # Hold validated rows in staging for human review — do not promote or delete.
            receipt["held_count"] = len(promotable)
            receipt["status"] = "HELD_FOR_HITL"
            receipt["reason"] = f"{len(promotable)} rows await HITL approval ({PROMOTION_HITL_ENV})"
            return receipt

        if not promotable:
            receipt["status"] = "NONE_PROMOTABLE"
            receipt["reason"] = "no_staged_rows_passed_revalidation"
            return receipt

        live = get_precomputed_embeddings_collection(
            client,
            live_collection,
            metadata={"hnsw:space": "cosine", "collection_role": "fact_vectors"},
        )
        promote_ids = [ids[i] for i in promotable]
        live.upsert(
            ids=promote_ids,
            embeddings=[embeddings[i] for i in promotable],
            documents=[documents[i] for i in promotable],
            metadatas=[metadatas[i] for i in promotable],
        )
        staging.delete(ids=promote_ids)
        receipt["promoted_count"] = len(promote_ids)
        receipt["status"] = "PASS"
        receipt["reason"] = "promoted_ok"
    except Exception as exc:  # guardian: allow-broad-except -- promotion is best-effort, recorded in receipt
        receipt["status"] = "FAIL"
        receipt["reason"] = f"{type(exc).__name__}:{exc}"
        _logger.warning("fact_vectors staging promotion failed: %s", exc)
    return receipt


__all__ = [
    "ALLOWED_WRITE_BACK_OPERATIONS",
    "ENRICH",
    "EXTRACT",
    "FUSE",
    "GENERATED",
    "LIVE_COLLECTION_NAME",
    "PROMOTION_HITL_ENV",
    "REJECT",
    "SEMANTIC_CACHE",
    "STAGE_FOR_FACT_VECTORS",
    "STAGING_COLLECTION_NAME",
    "WriteBackDecision",
    "classify_write_back_operation",
    "decide_write_back",
    "has_source_pointer",
    "is_generated_source",
    "promote_staged_fact_vectors",
    "promotion_hitl_required",
    "source_grounding_ok",
]
