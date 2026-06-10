"""Generic fact writeback routing and promotion engine."""
from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any

from agentic_core.L4_state.fact_writeback.contracts import (
    FactWritebackProfile,
    FactWritebackStore,
    PromotedFactRow,
    PromotionRequest,
    ScalarMetadataValue,
    SparseSyncCallback,
    StagedFactRow,
    WriteBackDecision,
)

_logger = logging.getLogger(__name__)


def norm(value: Any) -> str:
    """Normalize loosely typed metadata into a comparable string."""
    return str(value or "").strip()


def scalarize_metadata(metadata: Mapping[str, Any]) -> dict[str, ScalarMetadataValue]:
    """Convert metadata values into scalar values accepted by vector stores."""
    out: dict[str, ScalarMetadataValue] = {}
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            out[str(key)] = value
        else:
            out[str(key)] = json.dumps(value, sort_keys=True)
    return out


class FactWritebackEngine:
    """Profile-driven writeback classifier and staging promotion engine."""

    def __init__(self, profile: FactWritebackProfile) -> None:
        self.profile = profile

    def is_generated_source(self, atom: Mapping[str, Any]) -> tuple[bool, str]:
        """Return whether an atom comes from a generated or non-grounded source."""
        profile = self.profile
        if norm(atom.get(profile.operation_key)).lower() == profile.generated_operation:
            return True, f"declared_{profile.generated_operation}"
        proof = norm(atom.get(profile.proof_status_key))
        if proof in profile.generated_proof_statuses:
            return True, f"proof_status_{proof or 'empty'}"
        source_type = norm(atom.get(profile.source_type_key))
        if source_type and source_type in profile.forbidden_source_types:
            return True, f"non_grounded_source:{source_type}"
        return False, ""

    def has_source_pointer(self, atom: Mapping[str, Any]) -> bool:
        """Return whether an atom has any configured concrete source pointer."""
        return any(norm(atom.get(key)) for key in self.profile.source_pointer_keys)

    def source_grounding_ok(self, atom: Mapping[str, Any]) -> tuple[bool, str]:
        """Return whether an atom has grounded source class plus source pointer."""
        generated, reason = self.is_generated_source(atom)
        if generated:
            return False, reason
        if not norm(atom.get(self.profile.source_type_key)):
            return False, "no_source_type"
        if not self.has_source_pointer(atom):
            return False, "no_source_span_or_ref"
        return True, "grounded"

    def classify_write_back_operation(self, atom: Mapping[str, Any]) -> tuple[str, str]:
        """Classify the writeback operation type independently of pointer presence."""
        generated, reason = self.is_generated_source(atom)
        if generated:
            return self.profile.generated_operation, reason
        declared = norm(atom.get(self.profile.operation_key)).lower()
        if declared in {operation.lower() for operation in self.profile.allowed_operations}:
            if declared != self.profile.default_operation:
                return declared, f"declared_{declared}"
        return self.profile.default_operation, "grounded_atomization"

    def decide_write_back(self, atom: Mapping[str, Any]) -> WriteBackDecision:
        """Route one candidate atom to staging, semantic cache, or rejection."""
        operation, reason = self.classify_write_back_operation(atom)
        if operation == self.profile.generated_operation:
            return WriteBackDecision(
                self.profile.semantic_cache_route,
                operation,
                reason,
                stage_route=self.profile.stage_route,
            )
        if not norm(atom.get(self.profile.source_type_key)) or not self.has_source_pointer(atom):
            return WriteBackDecision(
                self.profile.reject_route,
                operation,
                "no_source_provenance",
                stage_route=self.profile.stage_route,
            )
        return WriteBackDecision(
            self.profile.stage_route,
            operation,
            reason,
            stage_route=self.profile.stage_route,
        )

    def promotion_score(self, metadata: Mapping[str, Any]) -> tuple[float, dict[str, float]]:
        """Compute deterministic promotion score and its components."""
        confidence = norm(metadata.get(self.profile.confidence_key)).upper()
        proof_status = norm(metadata.get(self.profile.proof_status_key))
        authority = norm(metadata.get(self.profile.authority_key)).upper()
        components = {
            "confidence": self.profile.confidence_scores.get(
                confidence,
                self.profile.default_confidence_score,
            ),
            "proof_status": self.profile.proof_status_scores.get(
                proof_status,
                self.profile.default_proof_status_score,
            ),
            "authority_class": self.profile.authority_scores.get(
                authority,
                self.profile.default_authority_score,
            ),
        }
        score = components["confidence"] * components["proof_status"] * components["authority_class"]
        return score, components

    def staged_row_is_promotable(self, metadata: Mapping[str, Any]) -> tuple[bool, str]:
        """Re-derive staged row eligibility from its own metadata."""
        operation = norm(metadata.get(self.profile.operation_key)).lower()
        allowed = {value.lower() for value in self.profile.allowed_operations}
        if operation not in allowed:
            return False, f"operation_not_allowed:{operation or 'missing'}"
        if not norm(metadata.get(self.profile.source_document_id_key)):
            return False, "missing_source_document_id"
        source_type = norm(metadata.get(self.profile.source_type_key))
        if source_type and source_type in self.profile.forbidden_source_types:
            return False, f"non_grounded_source:{source_type}"
        return True, "promotable"

    def make_promotion_receipt(self, request: PromotionRequest) -> dict[str, Any]:
        """Build the canonical initial promotion receipt."""
        receipt: dict[str, Any] = {
            "schema_version": self.profile.promotion_receipt_schema_version,
            "staging_collection": request.staging_collection,
            "live_collection": request.live_collection,
            "promotion_run_id": request.promotion_run_id,
            "promotion_mode": request.promotion_mode,
            "promoted_at_utc": request.promoted_at_utc,
            "promotion_score_floor": request.score_floor,
            "run_id": request.run_id,
            "x3_code": request.x3_code,
            "require_x3_allow": bool(request.require_x3_allow),
            "selected_ids": list(request.selected_ids),
            "missing_selected_ids": [],
            "staged_count": 0,
            "considered_count": 0,
            "other_run_count": 0,
            "promoted_count": 0,
            "held_count": 0,
            "rejected_count": 0,
            "promoted": [],
            "held": [],
            "rejected": [],
            "sparse_synced": False,
            "dense_count": None,
            "sparse_doc_count": None,
            "sparse_sync_reason": "",
            "hitl_required": bool(request.hitl_required),
            "status": "NOT_APPLICABLE",
            "reason": "",
        }
        if request.receipt_path:
            receipt["receipt_path"] = request.receipt_path
        return receipt

    def promote(
        self,
        store: FactWritebackStore,
        request: PromotionRequest,
        *,
        sparse_sync_callback: SparseSyncCallback | None = None,
    ) -> dict[str, Any]:
        """Promote validated staged rows into live storage and return a diagnostic receipt."""
        receipt = self.make_promotion_receipt(request)
        try:
            self._promote_into_receipt(store, request, receipt, sparse_sync_callback=sparse_sync_callback)
        except Exception as exc:  # guardian: allow-broad-except -- promotion reports diagnostics off the hot path.
            receipt["status"] = "FAIL"
            receipt["reason"] = f"{type(exc).__name__}:{exc}"
            _logger.warning("fact writeback promotion failed: %s", exc)
        return receipt

    def _promote_into_receipt(
        self,
        store: FactWritebackStore,
        request: PromotionRequest,
        receipt: dict[str, Any],
        *,
        sparse_sync_callback: SparseSyncCallback | None,
    ) -> None:
        staged_rows = store.list_staged_rows(include_embeddings=True)
        receipt["staged_count"] = len(staged_rows)
        if not staged_rows:
            receipt["status"] = "EMPTY"
            receipt["reason"] = "no_staged_rows"
            return

        selected_id_set = set(request.selected_ids)
        candidate_rows = list(staged_rows)
        if selected_id_set:
            present_ids = {row.row_id for row in staged_rows}
            receipt["missing_selected_ids"] = [
                row_id for row_id in request.selected_ids if row_id not in present_ids
            ]
            candidate_rows = [row for row in candidate_rows if row.row_id in selected_id_set]

        if request.run_id:
            before_run_filter = len(candidate_rows)
            candidate_rows = [
                row
                for row in candidate_rows
                if norm(row.metadata.get(self.profile.run_id_key)) == request.run_id
            ]
            receipt["other_run_count"] = before_run_filter - len(candidate_rows)

        receipt["considered_count"] = len(candidate_rows)
        if not candidate_rows:
            receipt["status"] = "EMPTY"
            receipt["reason"] = "no_staged_rows_for_run_or_selection"
            return

        rows_by_id = {row.row_id: row for row in staged_rows}
        promotable_rows: list[StagedFactRow] = []
        for row in candidate_rows:
            ok, why = self.staged_row_is_promotable(row.metadata)
            if ok:
                promotable_rows.append(row)
            else:
                receipt["rejected"].append({"id": row.row_id, "reason": why})
        receipt["rejected_count"] = len(receipt["rejected"])

        if request.limit is not None and request.limit >= 0:
            promotable_rows = promotable_rows[: request.limit]

        if request.require_x3_allow and request.x3_code != self.profile.x3_allow_code:
            reason = f"run_not_x3_allow:{request.x3_code or 'missing'}"
            receipt["held"] = [
                {
                    "id": row.row_id,
                    "reason": reason,
                    "run_id": request.run_id,
                    "x3_code": request.x3_code,
                }
                for row in promotable_rows
            ]
            receipt["held_count"] = len(receipt["held"])
            receipt["status"] = "HELD_FOR_X3"
            receipt["reason"] = f"{len(promotable_rows)} rows held pending {self.profile.x3_allow_code}"
            self._mark_held_rows(store, rows_by_id, receipt["held"], request)
            return

        if request.hitl_required:
            receipt["held"] = [
                {"id": row.row_id, "reason": "hitl_required"}
                for row in promotable_rows
            ]
            receipt["held_count"] = len(receipt["held"])
            receipt["status"] = "HELD_FOR_HITL"
            receipt["reason"] = f"{len(promotable_rows)} rows await HITL approval"
            self._mark_held_rows(store, rows_by_id, receipt["held"], request)
            return

        if not promotable_rows:
            receipt["status"] = "NONE_PROMOTABLE"
            receipt["reason"] = "no_staged_rows_passed_revalidation"
            return

        scored_promotable_rows: list[StagedFactRow] = []
        for row in promotable_rows:
            metadata = dict(row.metadata)
            digest = norm(metadata.get(self.profile.digest_key))
            duplicate_id = store.find_live_id_by_digest(digest) if digest else ""
            if duplicate_id:
                receipt["held"].append(
                    {"id": row.row_id, "reason": f"duplicate_digest:{duplicate_id}"}
                )
                continue
            score, components = self.promotion_score(metadata)
            metadata[self.profile.promotion_score_key] = round(score, 6)
            metadata[self.profile.promotion_score_components_key] = json.dumps(
                components,
                sort_keys=True,
            )
            scored_row = StagedFactRow(row.row_id, row.document, row.embedding, metadata)
            rows_by_id[row.row_id] = scored_row
            if score < request.score_floor:
                receipt["held"].append(
                    {
                        "id": row.row_id,
                        "reason": f"promotion_score_below_floor:{score:.3f}<{request.score_floor:.3f}",
                        "promotion_score": round(score, 6),
                    }
                )
                continue
            scored_promotable_rows.append(scored_row)

        receipt["held_count"] = len(receipt["held"])
        self._mark_held_rows(store, rows_by_id, receipt["held"], request)

        if not scored_promotable_rows:
            receipt["status"] = "NONE_PROMOTABLE"
            receipt["reason"] = "no_staged_rows_passed_dedupe_or_score_floor"
            receipt["dense_count"] = store.live_count()
            return

        promoted_rows = [
            PromotedFactRow(
                row_id=row.row_id,
                document=row.document,
                embedding=row.embedding,
                metadata={
                    **row.metadata,
                    self.profile.tier_key: self.profile.learned_tier_value,
                    self.profile.promoted_at_key: request.promoted_at_utc,
                    self.profile.promotion_run_id_key: request.promotion_run_id,
                },
            )
            for row in scored_promotable_rows
        ]
        store.upsert_live_rows(promoted_rows)
        receipt["dense_count"] = store.live_count()
        receipt["promoted"] = [
            {
                "id": row.row_id,
                "promotion_score": row.metadata.get(self.profile.promotion_score_key),
            }
            for row in promoted_rows
        ]

        if sparse_sync_callback is not None:
            sync_update = dict(sparse_sync_callback(promoted_rows, int(receipt["dense_count"] or 0)) or {})
            for key in ("sparse_synced", "sparse_doc_count", "sparse_sync_reason"):
                if key in sync_update:
                    receipt[key] = sync_update[key]

        store.delete_staged_rows([row.row_id for row in promoted_rows])
        receipt["promoted_count"] = len(promoted_rows)
        receipt["status"] = "PASS"
        if receipt["sparse_synced"] and receipt["dense_count"] == receipt["sparse_doc_count"]:
            receipt["reason"] = "promoted_ok_sparse_parity"
        elif receipt["sparse_synced"]:
            receipt["reason"] = "promoted_ok_sparse_count_mismatch"
        else:
            receipt["reason"] = "promoted_ok_sparse_sync_failed"

    def _mark_held_rows(
        self,
        store: FactWritebackStore,
        rows_by_id: Mapping[str, StagedFactRow],
        held: list[dict[str, Any]],
        request: PromotionRequest,
    ) -> None:
        if not held:
            return
        updates: dict[str, dict[str, ScalarMetadataValue]] = {}
        for item in held:
            row_id = str(item.get("id") or "")
            if not row_id:
                continue
            metadata = dict(rows_by_id.get(row_id, StagedFactRow(row_id, "", None, {})).metadata)
            metadata[self.profile.hold_reason_key] = str(item.get("reason") or "held")
            metadata[self.profile.hold_at_key] = request.promoted_at_utc
            metadata[self.profile.promotion_run_id_key] = request.promotion_run_id
            if request.x3_code:
                metadata[self.profile.x3_code_key] = request.x3_code
            updates[row_id] = scalarize_metadata(metadata)
        store.mark_staged_rows_held(updates)

    def make_staging_list_receipt(
        self,
        *,
        staging_collection: str,
        chroma_path: str | None,
    ) -> dict[str, Any]:
        """Build the initial staging list receipt."""
        return {
            "schema_version": self.profile.staging_list_schema_version,
            "staging_collection": staging_collection,
            "chroma_path": chroma_path or None,
            "staged_count": 0,
            "rows": [],
            "status": "NOT_APPLICABLE",
            "reason": "",
        }

    def list_staged(
        self,
        store: FactWritebackStore,
        *,
        staging_collection: str,
        chroma_path: str | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """List staged rows for operator review."""
        receipt = self.make_staging_list_receipt(
            staging_collection=staging_collection,
            chroma_path=chroma_path,
        )
        rows = store.list_staged_rows(include_embeddings=False)
        receipt["staged_count"] = len(rows)
        selected = rows
        if limit is not None and limit >= 0:
            selected = selected[:limit]
        receipt["rows"] = [self._staged_row_summary(row) for row in selected]
        receipt["status"] = "PASS" if rows else "EMPTY"
        receipt["reason"] = "listed_staged_rows" if rows else "no_staged_rows"
        return receipt

    def _staged_row_summary(self, row: StagedFactRow) -> dict[str, str]:
        metadata = row.metadata
        return {
            "id": row.row_id,
            "run_id": str(metadata.get(self.profile.run_id_key) or ""),
            "section_id": str(metadata.get(self.profile.section_key) or ""),
            "operation": str(metadata.get(self.profile.operation_key) or ""),
            "source_document_id": str(metadata.get(self.profile.source_document_id_key) or ""),
            "hold_reason": str(metadata.get(self.profile.hold_reason_key) or ""),
            "staged_at_utc": str(metadata.get(self.profile.staged_at_key) or ""),
            "document_preview": row.document[:160],
        }

    def make_staging_reject_receipt(
        self,
        *,
        staging_collection: str,
        chroma_path: str | None,
        selected_ids: tuple[str, ...],
        reason: str,
    ) -> dict[str, Any]:
        """Build the initial staging reject receipt."""
        return {
            "schema_version": self.profile.staging_reject_schema_version,
            "staging_collection": staging_collection,
            "chroma_path": chroma_path or None,
            "selected_ids": list(selected_ids),
            "rejected_ids": [],
            "missing_selected_ids": [],
            "reason": reason,
            "status": "NOT_APPLICABLE",
        }

    def reject_staged(
        self,
        store: FactWritebackStore,
        *,
        staging_collection: str,
        chroma_path: str | None = None,
        ids: tuple[str, ...],
        reason: str,
    ) -> dict[str, Any]:
        """Delete selected staged rows and return an operator receipt."""
        selected_ids = tuple(row_id for row_id in ids if norm(row_id))
        clean_reason = norm(reason)
        receipt = self.make_staging_reject_receipt(
            staging_collection=staging_collection,
            chroma_path=chroma_path,
            selected_ids=selected_ids,
            reason=clean_reason,
        )
        if not selected_ids:
            receipt["status"] = "FAIL"
            receipt["reason"] = "ids_required"
            return receipt
        if not clean_reason:
            receipt["status"] = "FAIL"
            receipt["reason"] = "reason_required"
            return receipt

        staged_rows = store.list_staged_rows(include_embeddings=False)
        present_ids = {row.row_id for row in staged_rows}
        existing_ids = [row_id for row_id in selected_ids if row_id in present_ids]
        if existing_ids:
            store.delete_staged_rows(existing_ids)
        receipt["rejected_ids"] = existing_ids
        existing = set(existing_ids)
        receipt["missing_selected_ids"] = [row_id for row_id in selected_ids if row_id not in existing]
        receipt["status"] = "PASS" if existing_ids else "EMPTY"
        return receipt

    def drain_held(
        self,
        store: FactWritebackStore,
        *,
        staging_collection: str,
        chroma_path: str | None = None,
        reason: str = "drain_held",
    ) -> dict[str, Any]:
        """Delete staged rows already marked held by a promotion gate."""
        staged = self.list_staged(
            store,
            staging_collection=staging_collection,
            chroma_path=chroma_path,
        )
        held_ids = [
            str(row.get("id") or "")
            for row in list(staged.get("rows") or [])
            if str(row.get("hold_reason") or "")
        ]
        held_ids = [row_id for row_id in held_ids if row_id]
        if not held_ids:
            return {
                "schema_version": self.profile.staging_drain_schema_version,
                "staging_collection": staging_collection,
                "chroma_path": chroma_path or None,
                "drained_ids": [],
                "status": "EMPTY",
                "reason": "no_held_rows",
            }
        receipt = self.reject_staged(
            store,
            staging_collection=staging_collection,
            chroma_path=chroma_path,
            ids=tuple(held_ids),
            reason=reason,
        )
        receipt["schema_version"] = self.profile.staging_drain_schema_version
        receipt["drained_ids"] = list(receipt.get("rejected_ids") or [])
        return receipt
