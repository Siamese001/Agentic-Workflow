"""Unit tests for the generic L4 fact writeback engine."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from agentic_core.L4_state.fact_writeback import (
    FactWritebackEngine,
    FactWritebackProfile,
    PromotedFactRow,
    PromotionRequest,
    ScalarMetadataValue,
    StagedFactRow,
)


def _profile() -> FactWritebackProfile:
    return FactWritebackProfile(
        stage_route="stage",
        semantic_cache_route="semantic_cache",
        reject_route="reject",
        default_operation="extract",
        generated_operation="generated",
        allowed_operations=("extract", "fuse", "enrich"),
        generated_proof_statuses=("not_proof",),
        forbidden_source_types=("synthesis",),
        confidence_scores={"HIGH": 1.0, "LOW": 0.25},
        proof_status_scores={"eligible": 1.0},
        authority_scores={"PRIMARY": 1.0, "SUPPORTING": 0.5},
        x3_allow_code="ALLOW",
    )


def _request(**overrides: Any) -> PromotionRequest:
    values = {
        "staging_collection": "staging",
        "live_collection": "live",
        "promotion_run_id": "promotion-run",
        "promotion_mode": "inline",
        "promoted_at_utc": "2026-06-10T00:00:00+00:00",
        "score_floor": 0.5,
        "hitl_required": False,
    }
    values.update(overrides)
    return PromotionRequest(**values)


def _row(row_id: str, **metadata: Any) -> StagedFactRow:
    base = {
        "write_back_operation": "extract",
        "source_document_id": row_id,
        "source_type": "ledger",
        "confidence": "HIGH",
        "proof_status": "eligible",
        "authority_class": "PRIMARY",
        "chunk_digest": f"digest-{row_id}",
    }
    base.update(metadata)
    return StagedFactRow(
        row_id=row_id,
        document=f"grounded claim {row_id}",
        embedding=[0.1, 0.2, 0.3],
        metadata=base,
    )


class _MemoryStore:
    def __init__(
        self,
        staged: Sequence[StagedFactRow] = (),
        live: Sequence[PromotedFactRow] = (),
    ) -> None:
        self.staged = {row.row_id: row for row in staged}
        self.live = {row.row_id: row for row in live}
        self.deleted: list[str] = []

    def list_staged_rows(self, *, include_embeddings: bool = True) -> list[StagedFactRow]:
        del include_embeddings
        return list(self.staged.values())

    def find_live_id_by_digest(self, digest: str) -> str:
        for row in self.live.values():
            if str(row.metadata.get("chunk_digest") or "") == digest:
                return row.row_id
        return ""

    def upsert_live_rows(self, rows: Sequence[PromotedFactRow]) -> None:
        for row in rows:
            self.live[row.row_id] = row

    def delete_staged_rows(self, row_ids: Sequence[str]) -> None:
        for row_id in row_ids:
            self.deleted.append(row_id)
            self.staged.pop(row_id, None)

    def mark_staged_rows_held(
        self,
        metadata_by_id: Mapping[str, Mapping[str, ScalarMetadataValue]],
    ) -> None:
        for row_id, metadata in metadata_by_id.items():
            current = self.staged[row_id]
            self.staged[row_id] = StagedFactRow(
                row_id=current.row_id,
                document=current.document,
                embedding=current.embedding,
                metadata=dict(metadata),
            )

    def live_count(self) -> int:
        return len(self.live)


class _ExplodingStore(_MemoryStore):
    def list_staged_rows(self, *, include_embeddings: bool = True) -> list[StagedFactRow]:
        del include_embeddings
        raise RuntimeError("staged rows unavailable")


def test_profile_driven_routing_uses_no_app_taxonomy() -> None:
    engine = FactWritebackEngine(_profile())

    staged = engine.decide_write_back({"source_type": "ledger", "source_ref": "source:1"})
    assert staged.route == "stage"
    assert staged.operation == "extract"
    assert staged.stage is True

    generated = engine.decide_write_back({"source_type": "synthesis", "source_ref": "source:1"})
    assert generated.route == "semantic_cache"
    assert generated.operation == "generated"
    assert generated.stage is False

    rejected = engine.decide_write_back({"source_type": "ledger", "write_back_operation": "enrich"})
    assert rejected.route == "reject"
    assert rejected.operation == "enrich"


def test_promotion_holds_for_x3_and_marks_staged_metadata() -> None:
    engine = FactWritebackEngine(_profile())
    store = _MemoryStore([_row("held", run_id="run-held")])

    receipt = engine.promote(
        store,
        _request(run_id="run-held", x3_code="BLOCK", require_x3_allow=True),
    )

    assert receipt["status"] == "HELD_FOR_X3"
    assert receipt["held"] == [
        {
            "id": "held",
            "reason": "run_not_x3_allow:BLOCK",
            "run_id": "run-held",
            "x3_code": "BLOCK",
        }
    ]
    metadata = store.staged["held"].metadata
    assert metadata["promotion_hold_reason"] == "run_not_x3_allow:BLOCK"
    assert metadata["promotion_run_id"] == "promotion-run"
    assert metadata["x3_code"] == "BLOCK"
    assert "held" not in store.deleted


def test_promotion_scores_dedupes_stamps_and_syncs() -> None:
    engine = FactWritebackEngine(_profile())
    duplicate_live = PromotedFactRow(
        row_id="existing",
        document="existing",
        embedding=[0.1],
        metadata={"chunk_digest": "digest-duplicate"},
    )
    store = _MemoryStore(
        [
            _row("good"),
            _row("duplicate", chunk_digest="digest-duplicate"),
            _row("low", confidence="LOW"),
        ],
        live=[duplicate_live],
    )
    synced: dict[str, Any] = {}

    def _sync(rows: Sequence[PromotedFactRow], dense_count: int) -> dict[str, Any]:
        synced["ids"] = [row.row_id for row in rows]
        return {
            "sparse_synced": True,
            "sparse_doc_count": dense_count,
            "sparse_sync_reason": "ok",
        }

    receipt = engine.promote(store, _request(), sparse_sync_callback=_sync)

    assert receipt["status"] == "PASS"
    assert receipt["promoted_count"] == 1
    assert receipt["held_count"] == 2
    assert receipt["reason"] == "promoted_ok_sparse_parity"
    assert synced["ids"] == ["good"]
    assert "good" in store.live
    assert "good" not in store.staged
    assert store.live["good"].metadata["tier"] == "learned"
    assert store.live["good"].metadata["promotion_score"] == 1.0
    assert store.staged["duplicate"].metadata["promotion_hold_reason"] == "duplicate_digest:existing"
    assert store.staged["low"].metadata["promotion_hold_reason"].startswith("promotion_score_below_floor")
    assert store.staged["low"].metadata["promotion_score"] == 0.25


def test_promotion_reports_specific_runtime_failures() -> None:
    engine = FactWritebackEngine(_profile())

    receipt = engine.promote(_ExplodingStore(), _request())

    assert receipt["status"] == "FAIL"
    assert receipt["reason"].startswith("RuntimeError:staged rows unavailable")


def test_list_reject_and_drain_held_rows() -> None:
    engine = FactWritebackEngine(_profile())
    store = _MemoryStore(
        [
            _row("a", section_type="summary", run_id="run-a", staged_at_utc="now"),
            _row("held", promotion_hold_reason="manual_hold"),
        ]
    )

    listed = engine.list_staged(store, staging_collection="staging", limit=1)
    assert listed["status"] == "PASS"
    assert listed["staged_count"] == 2
    assert listed["rows"][0]["section_id"] == "summary"

    rejected = engine.reject_staged(
        store,
        staging_collection="staging",
        ids=("a", "missing"),
        reason="operator",
    )
    assert rejected["status"] == "PASS"
    assert rejected["rejected_ids"] == ["a"]
    assert rejected["missing_selected_ids"] == ["missing"]

    drained = engine.drain_held(store, staging_collection="staging")
    assert drained["status"] == "PASS"
    assert drained["drained_ids"] == ["held"]
    assert store.staged == {}


def test_core_fact_writeback_package_has_no_app_literals() -> None:
    package_root = Path("agentic_core/L4_state/fact_writeback")
    text = "\n".join(path.read_text(encoding="utf-8") for path in package_root.glob("*.py"))

    assert "apps_rg" not in text
    assert "apps_" not in text
