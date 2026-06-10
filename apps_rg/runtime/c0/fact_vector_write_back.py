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

import hashlib
import json
import logging
import os
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.L4_state.fact_writeback import (
    FactWritebackEngine,
    FactWritebackProfile,
    PromotedFactRow,
    PromotionRequest,
    StagedFactRow,
    WriteBackDecision,
    scalarize_metadata,
)
from agentic_core.L4_state.fact_writeback import (
    norm as _core_norm,
)
from apps_rg.runtime.c0.constants import (
    FORBIDDEN_PROOF_SOURCE_TYPES,
    NOT_PROOF,
    PROOF_ELIGIBLE,
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
PROMOTION_MODE_ENV = "APPS_RG_FACT_VECTOR_PROMOTION_MODE"
PROMOTION_SCORE_FLOOR_ENV = "APPS_RG_FACT_VECTOR_PROMOTION_SCORE_FLOOR"
PROMOTION_MODE_INLINE = "inline"
PROMOTION_MODE_DEFERRED = "deferred"
DEFAULT_PROMOTION_SCORE_FLOOR = 0.48
PROMOTION_RECEIPT_NAME = "fact_vector_promotion_receipt.json"
X3_ALLOW = "X3_ALLOW"
PROMOTION_HOLD_REASON_METADATA_KEY = "promotion_hold_reason"

_CONFIDENCE_SCORE = {
    "HIGH": 1.0,
    "MEDIUM": 0.6,
    "LOW": 0.3,
}
_AUTHORITY_SCORE = {
    "PRIMARY": 1.0,
    "SUPPORTING": 0.8,
}

APPS_RG_FACT_WRITEBACK_PROFILE = FactWritebackProfile(
    stage_route=STAGE_FOR_FACT_VECTORS,
    semantic_cache_route=SEMANTIC_CACHE,
    reject_route=REJECT,
    default_operation=EXTRACT,
    generated_operation=GENERATED,
    allowed_operations=(EXTRACT, FUSE, ENRICH),
    generated_proof_statuses=(NOT_PROOF, TARGETING_ONLY),
    forbidden_source_types=tuple(FORBIDDEN_PROOF_SOURCE_TYPES),
    confidence_scores=_CONFIDENCE_SCORE,
    proof_status_scores={PROOF_ELIGIBLE: 1.0},
    authority_scores=_AUTHORITY_SCORE,
    x3_allow_code=X3_ALLOW,
    promotion_receipt_schema_version="fact_vector_promotion_v2",
    staging_list_schema_version="fact_vector_staging_list_v1",
    staging_reject_schema_version="fact_vector_staging_reject_v1",
    staging_drain_schema_version="fact_vector_staging_drain_held_v1",
)
_ENGINE = FactWritebackEngine(APPS_RG_FACT_WRITEBACK_PROFILE)


def _norm(value: Any) -> str:
    return _core_norm(value)


def is_generated_source(atom: dict[str, Any]) -> tuple[bool, str]:
    """True when the atom comes from a generated/non-grounded SOURCE (belongs in the semantic
    cache, not fact_vectors).

    Generated-by-nature ⇔ a forbidden ``source_type`` (jd_payload / briefing / company_research /
    generic_best_practice / governance_docs / …), OR ``proof_status`` of not_proof/targeting_only,
    OR an explicit ``write_back_operation == "generated"``. This is orthogonal to whether a specific
    source pointer is present (that is the REJECT condition, see ``has_source_pointer``).
    """
    return _ENGINE.is_generated_source(atom)


def has_source_pointer(atom: dict[str, Any]) -> bool:
    """True when the atom carries a concrete pointer to its source document."""
    return _ENGINE.has_source_pointer(atom)


def source_grounding_ok(atom: dict[str, Any]) -> tuple[bool, str]:
    """True when the atom traces back to a real source document: NOT a generated source AND it
    carries a concrete source pointer. The "can you point to the source document" test.
    """
    return _ENGINE.source_grounding_ok(atom)


def classify_write_back_operation(atom: dict[str, Any]) -> tuple[str, str]:
    """Classify the write-back OPERATION TYPE: EXTRACT / FUSE / ENRICH / GENERATED.

    This is about *what kind of inference* produced the atom, independent of whether the specific
    source pointer is present (the REJECT condition lives in ``decide_write_back``). A generated
    source ⇒ GENERATED; an explicit fuse/enrich claim is honored; otherwise a grounded-class atom is
    an EXTRACT (atomization of retrieved content).
    """
    return _ENGINE.classify_write_back_operation(atom)


def decide_write_back(atom: dict[str, Any]) -> WriteBackDecision:
    """Single routing call: where does this candidate write-back atom go?

    * grounded transform (extract/fuse/enrich) with a source pointer ⇒ STAGE_FOR_FACT_VECTORS
    * generated/synthesized ⇒ SEMANTIC_CACHE (intent-vector domain, not fact_vectors)
    * a claimed transform with NO source provenance ⇒ REJECT (fail closed)
    """
    return _ENGINE.decide_write_back(atom)


def promotion_hitl_required(explicit: bool | None = None) -> bool:
    """Whether staging→live promotion must wait for human approval.

    ``explicit`` overrides; otherwise reads ``APPS_RG_FACT_VECTOR_PROMOTION_HITL`` (1/true/yes/on).
    """
    if explicit is not None:
        return bool(explicit)
    return _norm(os.environ.get(PROMOTION_HITL_ENV)).lower() in ("1", "true", "yes", "on")


def promotion_mode(explicit: str | None = None) -> str:
    """Return inline/deferred promotion mode, defaulting to inline for current behavior."""
    raw = _norm(explicit if explicit is not None else os.environ.get(PROMOTION_MODE_ENV)).lower()
    if not raw:
        return PROMOTION_MODE_INLINE
    if raw in (PROMOTION_MODE_INLINE, PROMOTION_MODE_DEFERRED):
        return raw
    _logger.warning(
        "Invalid %s=%r; using %s",
        PROMOTION_MODE_ENV,
        raw,
        PROMOTION_MODE_INLINE,
    )
    return PROMOTION_MODE_INLINE


def deferred_promotion_enabled(explicit: str | None = None) -> bool:
    """Whether C0.2 staging should wait for the post-X3 promotion seam."""
    return promotion_mode(explicit) == PROMOTION_MODE_DEFERRED


def promotion_score_floor(explicit: float | None = None) -> float:
    """Return the configured promotion score floor."""
    if explicit is not None:
        return max(0.0, float(explicit))
    raw = _norm(os.environ.get(PROMOTION_SCORE_FLOOR_ENV))
    if not raw:
        return DEFAULT_PROMOTION_SCORE_FLOOR
    try:
        return max(0.0, float(raw))
    except ValueError:
        _logger.warning("Invalid %s=%r; using default %.2f", PROMOTION_SCORE_FLOOR_ENV, raw, DEFAULT_PROMOTION_SCORE_FLOOR)
        return DEFAULT_PROMOTION_SCORE_FLOOR


def promotion_score(metadata: dict[str, Any]) -> tuple[float, dict[str, float]]:
    """Compute the deterministic W2 promotion score and component values."""
    return _ENGINE.promotion_score(metadata)


def _staged_row_is_promotable(metadata: dict[str, Any]) -> tuple[bool, str]:
    """Hostile re-validation at promotion time — re-derive eligibility from the staged row's own
    metadata (never trust that it was validated on the way in).
    """
    return _ENGINE.staged_row_is_promotable(metadata)


def _find_live_id_by_digest(live_collection: Any, digest: str) -> str:
    """Return the first live row id with this chunk digest, if any."""
    if not _norm(digest):
        return ""
    match = live_collection.get(
        where={"chunk_digest": digest},
        include=["metadatas"],
        limit=1,
    )
    ids = list(match.get("ids") or [])
    return str(ids[0]) if ids else ""


def _write_promotion_receipt(artifact_dir: str | Path | None, receipt: dict[str, Any]) -> None:
    if artifact_dir is None:
        return
    try:
        path = Path(artifact_dir)
        path.mkdir(parents=True, exist_ok=True)
        (path / PROMOTION_RECEIPT_NAME).write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:  # guardian: allow-log-and-swallow -- promotion receipt is best-effort telemetry.
        _logger.warning("fact_vectors promotion receipt write failed: %s", exc)


def _promotion_receipt_digest(receipt: Mapping[str, Any]) -> str:
    """Stable digest for the promotion decision payload before witness annotation."""
    payload = {
        key: value
        for key, value in receipt.items()
        if key not in {"uwg_witness"}
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _attach_promotion_uwg_witness(
    receipt: dict[str, Any],
    *,
    artifact_dir: str | Path | None,
) -> None:
    """Attach a fail-soft L4/UWG receipt witness to the promotion receipt.

    This is a receipt witness, not a full UWG MutationRecord. Promotion remains
    the app-specific vector-store operation; the ledger row makes the decision
    UWG-visible with a digest back to the standalone promotion receipt.
    """
    if artifact_dir is None:
        return

    digest = _promotion_receipt_digest(receipt)
    decision_id = f"fact_vector_promotion_{digest[:12]}"
    status = str(receipt.get("status") or "")
    promoted_count = int(receipt.get("promoted_count") or 0)
    held_count = int(receipt.get("held_count") or 0)
    rejected_count = int(receipt.get("rejected_count") or 0)
    staged_count = int(receipt.get("staged_count") or 0)
    success = status == "PASS" and promoted_count > 0
    selected = "commit" if success else "blocked"
    receipt_path = str(Path(artifact_dir) / PROMOTION_RECEIPT_NAME)
    confidence = 1.0 if success else 0.5
    eu_score = 1.0 if success else 0.0
    prediction = {
        "decision_id": decision_id,
        "selected": selected,
        "fingerprint": digest[:12],
        "cell": {
            "source_surface": "apps_rg.fact_vectors.promotion",
            "blast_radius": "fact_vectors_live",
        },
        "predicted_p_success": confidence,
        "eu_score": eu_score,
        "validation_status": "PASS" if success else "FAIL",
        "block_stage": "" if success else str(receipt.get("reason") or status or "blocked"),
        "n_state_diffs": promoted_count,
        "n_target_surfaces": 1,
        "tenant_id": "apps_rg",
        "promotion_status": status,
        "staged_count": staged_count,
        "promoted_count": promoted_count,
        "held_count": held_count,
        "rejected_count": rejected_count,
    }
    outcome = {
        "success": success,
        "latency_ms": 0,
        "commit_receipt_id": receipt_path if success else None,
        "blocked_receipt_id": None if success else receipt_path,
        "n_refresh_receipts": 0,
        "snapshot_after": None,
        "promotion_receipt_digest": digest,
        "dense_count": receipt.get("dense_count"),
        "sparse_doc_count": receipt.get("sparse_doc_count"),
        "sparse_synced": bool(receipt.get("sparse_synced")),
    }
    metadata = {
        "router": "L4/uwg",
        "witness_kind": "fact_vector_promotion_receipt",
        "promotion_receipt_digest": digest,
        "promotion_receipt_path": receipt_path,
        "promotion_run_id": str(receipt.get("promotion_run_id") or ""),
        "live_collection": str(receipt.get("live_collection") or LIVE_COLLECTION_NAME),
        "staging_collection": str(receipt.get("staging_collection") or STAGING_COLLECTION_NAME),
    }
    event_id = ""
    try:
        from tools.ledgers.hook_helpers import emit_ledger_event

        event_id = emit_ledger_event(
            ledger="router_l4_uwg",
            event_kind="route_decision",
            prediction=prediction,
            outcome=outcome,
            score_band=selected,
            score_numeric=eu_score,
            repo_area="apps_rg/runtime/c0/fact_vector_write_back.py",
            latency_ms=0,
            metadata=metadata,
        )
    except (
        ImportError,
        AttributeError,
        TypeError,
        ValueError,
        RuntimeError,
        OSError,
    ):  # guardian: allow-log-and-swallow -- witness telemetry must not block promotion receipts.
        _logger.debug("fact_vectors promotion UWG witness emit failed", exc_info=True)

    _logger.info(
        "ROUTER_DECISION: layer=L4 router=uwg decision_id=%s trace_id=%s "
        "route_id=fact_vectors_promotion selected=%s eu_score=%.4f "
        "brier_score=pending confidence=%.4f",
        decision_id,
        str(receipt.get("promotion_run_id") or decision_id),
        selected,
        eu_score,
        confidence,
    )
    receipt["uwg_witness"] = {
        "ledger": "router_l4_uwg",
        "event_kind": "route_decision",
        "event_id": event_id,
        "decision_id": decision_id,
        "selected": selected,
        "promotion_receipt_digest": digest,
        "promotion_receipt_path": receipt_path,
        "witness_status": "PASS" if event_id else "FAIL_SOFT",
    }


def _metadata_scalarize(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
    return scalarize_metadata(metadata)


class _ChromaFactWritebackStore:
    """Chroma-backed storage adapter for the generic core writeback engine."""

    def __init__(self, *, staging: Any, live: Any | None = None) -> None:
        self._staging = staging
        self._live = live

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        return list(value) if value is not None else []

    def list_staged_rows(self, *, include_embeddings: bool = True) -> list[StagedFactRow]:
        include = ["documents", "metadatas"]
        if include_embeddings:
            include.append("embeddings")
        staged = self._staging.get(include=include)
        row_ids = [str(v) for v in self._as_list(staged.get("ids"))]
        documents = self._as_list(staged.get("documents"))
        metadatas = self._as_list(staged.get("metadatas"))
        embeddings = self._as_list(staged.get("embeddings")) if include_embeddings else []
        rows: list[StagedFactRow] = []
        for idx, row_id in enumerate(row_ids):
            rows.append(
                StagedFactRow(
                    row_id=row_id,
                    document=str(documents[idx] or "") if idx < len(documents) else "",
                    embedding=embeddings[idx] if idx < len(embeddings) else None,
                    metadata=dict(metadatas[idx] or {}) if idx < len(metadatas) else {},
                )
            )
        return rows

    def find_live_id_by_digest(self, digest: str) -> str:
        if self._live is None:
            return ""
        return _find_live_id_by_digest(self._live, digest)

    def upsert_live_rows(self, rows: Sequence[PromotedFactRow]) -> None:
        if self._live is None:
            raise RuntimeError("live collection unavailable")
        self._live.upsert(
            ids=[row.row_id for row in rows],
            embeddings=[row.embedding for row in rows],
            documents=[row.document for row in rows],
            metadatas=[_metadata_scalarize(row.metadata) for row in rows],
        )

    def delete_staged_rows(self, row_ids: Sequence[str]) -> None:
        if row_ids:
            self._staging.delete(ids=list(row_ids))

    def mark_staged_rows_held(
        self,
        metadata_by_id: Mapping[str, Mapping[str, str | int | float | bool]],
    ) -> None:
        if not metadata_by_id:
            return
        try:
            self._staging.update(
                ids=list(metadata_by_id),
                metadatas=[dict(metadata) for metadata in metadata_by_id.values()],
            )
        except Exception as exc:  # guardian: allow-broad-except -- hold annotation must not block receipts.
            _logger.warning("fact_vectors staging hold annotation failed: %s", exc)

    def live_count(self) -> int:
        if self._live is None:
            return 0
        return int(self._live.count())


def _open_collection(*, chroma_path: str, collection_name: str, collection_role: str) -> Any:
    from agentic_core.L4_state.utils.client.chroma_client import (
        chromadb_module as chromadb,
    )
    from apps_rg.runtime.chroma_precomputed_collection import (
        get_precomputed_embeddings_collection,
    )

    client = chromadb.PersistentClient(path=chroma_path)
    return get_precomputed_embeddings_collection(
        client,
        collection_name,
        metadata={"hnsw:space": "cosine", "collection_role": collection_role},
    )


def _open_fact_writeback_store(
    *,
    chroma_path: str,
    staging_collection: str,
    live_collection: str | None = None,
) -> _ChromaFactWritebackStore:
    staging = _open_collection(
        chroma_path=chroma_path,
        collection_name=staging_collection,
        collection_role="fact_vectors_staging",
    )
    live = None
    if live_collection:
        live = _open_collection(
            chroma_path=chroma_path,
            collection_name=live_collection,
            collection_role="fact_vectors",
        )
    return _ChromaFactWritebackStore(staging=staging, live=live)


def _sync_sparse_fact_vectors(
    *,
    chroma_path: str,
    live_collection: str,
    sparse_dir: str | Path | None,
):
    def _sync(rows: Sequence[PromotedFactRow], dense_count: int) -> dict[str, Any]:
        update: dict[str, Any] = {
            "sparse_synced": False,
            "sparse_doc_count": None,
            "sparse_sync_reason": "",
        }
        try:
            from tools.generate.ingestion import build_sparse_index

            sparse_stats = build_sparse_index.upsert_documents(
                live_collection,
                [
                    {
                        "id": row.row_id,
                        "document": row.document,
                        "metadata": row.metadata,
                    }
                    for row in rows
                ],
                sparse_dir=sparse_dir,
            )
            update["sparse_synced"] = True
            update["sparse_doc_count"] = int(sparse_stats.get("doc_count", 0))
            update["sparse_sync_reason"] = "incremental_upsert_ok"
            if update["sparse_doc_count"] != dense_count:
                sparse_stats = build_sparse_index.build_for_collection(
                    live_collection,
                    dry_run=False,
                    chroma_path=chroma_path,
                    sparse_dir=sparse_dir,
                )
                update["sparse_doc_count"] = int(sparse_stats.get("doc_count", 0))
                update["sparse_sync_reason"] += ";full_rebuild_after_count_mismatch"
        except Exception as exc:  # guardian: allow-broad-except -- dense promotion succeeded; record sparse drift.
            update["sparse_sync_reason"] = f"incremental_failed:{type(exc).__name__}:{exc}"
            try:
                from tools.generate.ingestion import build_sparse_index

                sparse_stats = build_sparse_index.build_for_collection(
                    live_collection,
                    dry_run=False,
                    chroma_path=chroma_path,
                    sparse_dir=sparse_dir,
                )
                update["sparse_synced"] = True
                update["sparse_doc_count"] = int(sparse_stats.get("doc_count", 0))
                update["sparse_sync_reason"] += ";full_rebuild_ok"
            except Exception as rebuild_exc:  # guardian: allow-broad-except -- record sparse rebuild failure.
                update["sparse_synced"] = False
                update["sparse_sync_reason"] += (
                    f";full_rebuild_failed:{type(rebuild_exc).__name__}:{rebuild_exc}"
                )
        return update

    return _sync


def promote_staged_fact_vectors(
    *,
    chroma_path: str,
    require_hitl: bool | None = None,
    staging_collection: str = STAGING_COLLECTION_NAME,
    live_collection: str = LIVE_COLLECTION_NAME,
    limit: int | None = None,
    promotion_run_id: str | None = None,
    score_floor: float | None = None,
    artifact_dir: str | Path | None = None,
    sparse_dir: str | Path | None = None,
    ids: list[str] | tuple[str, ...] | None = None,
    run_id: str | None = None,
    x3_code: str | None = None,
    require_x3_allow: bool = False,
) -> dict[str, Any]:
    """Promote validated staged chunks from ``fact_vectors_staging`` to live ``fact_vectors``.

    Deterministic gate: each staged row is re-validated (operation allowed + source provenance) from
    its own metadata. When HITL is required, rows are LEFT in staging (held, not lost). Otherwise
    promotable rows are upserted to live and removed from staging.

    Returns a promotion receipt (never raises — best-effort, off the hot path).
    """
    promoted_at_utc = datetime.now(timezone.utc).isoformat()
    resolved_promotion_run_id = (
        _norm(promotion_run_id)
        or f"fact_vector_promotion:{promoted_at_utc.replace('+00:00', 'Z')}"
    )
    resolved_score_floor = promotion_score_floor(score_floor)
    resolved_run_id = _norm(run_id)
    resolved_x3_code = _norm(x3_code)
    selected_ids = tuple(str(v).strip() for v in (ids or []) if _norm(v))
    request = PromotionRequest(
        staging_collection=staging_collection,
        live_collection=live_collection,
        promotion_run_id=resolved_promotion_run_id,
        promotion_mode=promotion_mode(),
        promoted_at_utc=promoted_at_utc,
        score_floor=resolved_score_floor,
        hitl_required=promotion_hitl_required(require_hitl),
        selected_ids=selected_ids,
        run_id=resolved_run_id,
        x3_code=resolved_x3_code,
        require_x3_allow=bool(require_x3_allow),
        limit=limit,
        receipt_path=str(Path(artifact_dir) / PROMOTION_RECEIPT_NAME) if artifact_dir is not None else "",
    )
    receipt = _ENGINE.make_promotion_receipt(request)

    def _finish(done: dict[str, Any]) -> dict[str, Any]:
        if done.get("status") == "HELD_FOR_HITL":
            done["reason"] = f"{done.get('held_count', 0)} rows await HITL approval ({PROMOTION_HITL_ENV})"
        _attach_promotion_uwg_witness(done, artifact_dir=artifact_dir)
        _write_promotion_receipt(artifact_dir, done)
        return done

    if not _norm(chroma_path):
        receipt["reason"] = "chroma_path_unset"
        return _finish(receipt)

    try:
        store = _open_fact_writeback_store(
            chroma_path=chroma_path,
            staging_collection=staging_collection,
            live_collection=live_collection,
        )
        receipt = _ENGINE.promote(
            store,
            request,
            sparse_sync_callback=_sync_sparse_fact_vectors(
                chroma_path=chroma_path,
                live_collection=live_collection,
                sparse_dir=sparse_dir,
            ),
        )
    except Exception as exc:  # guardian: allow-broad-except -- promotion is best-effort, recorded in receipt
        receipt["status"] = "FAIL"
        receipt["reason"] = f"{type(exc).__name__}:{exc}"
        _logger.warning("fact_vectors staging promotion failed: %s", exc)
    return _finish(receipt)


def list_staged_fact_vectors(
    *,
    chroma_path: str,
    staging_collection: str = STAGING_COLLECTION_NAME,
    limit: int | None = None,
) -> dict[str, Any]:
    """List staged fact-vector rows for operator review."""
    receipt = _ENGINE.make_staging_list_receipt(
        staging_collection=staging_collection,
        chroma_path=chroma_path,
    )
    if not _norm(chroma_path):
        receipt["reason"] = "chroma_path_unset"
        return receipt
    try:
        store = _open_fact_writeback_store(
            chroma_path=chroma_path,
            staging_collection=staging_collection,
        )
        receipt = _ENGINE.list_staged(
            store,
            staging_collection=staging_collection,
            chroma_path=chroma_path,
            limit=limit,
        )
    except Exception as exc:  # guardian: allow-broad-except -- operator list should report errors as JSON.
        receipt["status"] = "FAIL"
        receipt["reason"] = f"{type(exc).__name__}:{exc}"
        _logger.warning("fact_vectors staging list failed: %s", exc)
    return receipt


def reject_staged_fact_vectors(
    *,
    chroma_path: str,
    ids: list[str] | tuple[str, ...],
    reason: str,
    staging_collection: str = STAGING_COLLECTION_NAME,
) -> dict[str, Any]:
    """Reject selected staged rows by deleting them from staging with an operator receipt."""
    selected_ids = tuple(str(v).strip() for v in ids if _norm(v))
    receipt = _ENGINE.make_staging_reject_receipt(
        staging_collection=staging_collection,
        chroma_path=chroma_path,
        selected_ids=selected_ids,
        reason=_norm(reason),
    )
    if not _norm(chroma_path):
        receipt["reason"] = "chroma_path_unset"
        return receipt
    if not selected_ids:
        receipt["status"] = "FAIL"
        receipt["reason"] = "ids_required"
        return receipt
    if not _norm(reason):
        receipt["status"] = "FAIL"
        receipt["reason"] = "reason_required"
        return receipt
    try:
        store = _open_fact_writeback_store(
            chroma_path=chroma_path,
            staging_collection=staging_collection,
        )
        receipt = _ENGINE.reject_staged(
            store,
            staging_collection=staging_collection,
            chroma_path=chroma_path,
            ids=selected_ids,
            reason=reason,
        )
    except Exception as exc:  # guardian: allow-broad-except -- operator reject should report errors as JSON.
        receipt["status"] = "FAIL"
        receipt["reason"] = f"{type(exc).__name__}:{exc}"
        _logger.warning("fact_vectors staging reject failed: %s", exc)
    return receipt


def drain_held_staged_fact_vectors(
    *,
    chroma_path: str,
    staging_collection: str = STAGING_COLLECTION_NAME,
    reason: str = "drain_held",
) -> dict[str, Any]:
    """Delete staged rows already marked held by a promotion gate."""
    if not _norm(chroma_path):
        return {
            "schema_version": APPS_RG_FACT_WRITEBACK_PROFILE.staging_drain_schema_version,
            "staging_collection": staging_collection,
            "chroma_path": chroma_path or None,
            "drained_ids": [],
            "status": "EMPTY",
            "reason": "no_held_rows",
        }
    try:
        store = _open_fact_writeback_store(
            chroma_path=chroma_path,
            staging_collection=staging_collection,
        )
        return _ENGINE.drain_held(
            store,
            staging_collection=staging_collection,
            chroma_path=chroma_path,
            reason=reason,
        )
    except Exception as exc:  # guardian: allow-broad-except -- operator drain should report errors as JSON.
        _logger.warning("fact_vectors staging held drain failed: %s", exc)
        return {
            "schema_version": APPS_RG_FACT_WRITEBACK_PROFILE.staging_drain_schema_version,
            "staging_collection": staging_collection,
            "chroma_path": chroma_path or None,
            "drained_ids": [],
            "status": "FAIL",
            "reason": f"{type(exc).__name__}:{exc}",
        }


__all__ = [
    "ALLOWED_WRITE_BACK_OPERATIONS",
    "APPS_RG_FACT_WRITEBACK_PROFILE",
    "DEFAULT_PROMOTION_SCORE_FLOOR",
    "ENRICH",
    "EXTRACT",
    "FUSE",
    "GENERATED",
    "LIVE_COLLECTION_NAME",
    "PROMOTION_RECEIPT_NAME",
    "PROMOTION_HITL_ENV",
    "PROMOTION_HOLD_REASON_METADATA_KEY",
    "PROMOTION_MODE_DEFERRED",
    "PROMOTION_MODE_ENV",
    "PROMOTION_MODE_INLINE",
    "PROMOTION_SCORE_FLOOR_ENV",
    "REJECT",
    "SEMANTIC_CACHE",
    "STAGE_FOR_FACT_VECTORS",
    "STAGING_COLLECTION_NAME",
    "WriteBackDecision",
    "X3_ALLOW",
    "classify_write_back_operation",
    "decide_write_back",
    "deferred_promotion_enabled",
    "drain_held_staged_fact_vectors",
    "has_source_pointer",
    "is_generated_source",
    "list_staged_fact_vectors",
    "promote_staged_fact_vectors",
    "promotion_hitl_required",
    "promotion_mode",
    "promotion_score",
    "promotion_score_floor",
    "reject_staged_fact_vectors",
    "source_grounding_ok",
]
