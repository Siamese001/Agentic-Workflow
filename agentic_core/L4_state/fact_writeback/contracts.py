"""Storage-agnostic contracts for governed fact writeback promotion."""
from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Protocol

ScalarMetadataValue = str | int | float | bool


@dataclass(frozen=True, slots=True)
class WriteBackDecision:
    """Routing decision for one candidate writeback atom."""

    route: str
    operation: str
    reason: str
    stage_route: str = field(default="", repr=False, compare=False)

    @property
    def stage(self) -> bool:
        return bool(self.stage_route and self.route == self.stage_route)


@dataclass(frozen=True, slots=True)
class FactWritebackProfile:
    """Profile values supplied by an application binding."""

    stage_route: str
    semantic_cache_route: str
    reject_route: str
    default_operation: str
    generated_operation: str
    allowed_operations: tuple[str, ...]
    operation_key: str = "write_back_operation"
    source_type_key: str = "source_type"
    source_pointer_keys: tuple[str, ...] = ("source_span_ref", "source_ref")
    source_document_id_key: str = "source_document_id"
    digest_key: str = "chunk_digest"
    confidence_key: str = "confidence"
    proof_status_key: str = "proof_status"
    authority_key: str = "authority_class"
    tier_key: str = "tier"
    learned_tier_value: str = "learned"
    promoted_at_key: str = "promoted_at_utc"
    promotion_run_id_key: str = "promotion_run_id"
    promotion_score_key: str = "promotion_score"
    promotion_score_components_key: str = "promotion_score_components"
    hold_reason_key: str = "promotion_hold_reason"
    hold_at_key: str = "promotion_hold_at_utc"
    run_id_key: str = "run_id"
    x3_code_key: str = "x3_code"
    section_key: str = "section_type"
    staged_at_key: str = "staged_at_utc"
    x3_allow_code: str = "X3_ALLOW"
    generated_proof_statuses: tuple[str, ...] = ()
    forbidden_source_types: tuple[str, ...] = ()
    confidence_scores: Mapping[str, float] = field(default_factory=dict)
    proof_status_scores: Mapping[str, float] = field(default_factory=dict)
    authority_scores: Mapping[str, float] = field(default_factory=dict)
    default_confidence_score: float = 0.3
    default_proof_status_score: float = 0.5
    default_authority_score: float = 0.8
    promotion_receipt_schema_version: str = "fact_writeback_promotion_v1"
    staging_list_schema_version: str = "fact_writeback_staging_list_v1"
    staging_reject_schema_version: str = "fact_writeback_staging_reject_v1"
    staging_drain_schema_version: str = "fact_writeback_staging_drain_held_v1"


@dataclass(frozen=True, slots=True)
class StagedFactRow:
    """One row currently waiting in a staging store."""

    row_id: str
    document: str
    embedding: Any
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PromotedFactRow:
    """One row accepted for promotion into the live store."""

    row_id: str
    document: str
    embedding: Any
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PromotionRequest:
    """Inputs for one staging-to-live promotion attempt."""

    staging_collection: str
    live_collection: str
    promotion_run_id: str
    promotion_mode: str
    promoted_at_utc: str
    score_floor: float
    hitl_required: bool
    selected_ids: tuple[str, ...] = ()
    run_id: str = ""
    x3_code: str = ""
    require_x3_allow: bool = False
    limit: int | None = None
    receipt_path: str = ""


class FactWritebackStore(Protocol):
    """Minimal storage contract required by the generic writeback engine."""

    def list_staged_rows(self, *, include_embeddings: bool = True) -> list[StagedFactRow]:
        """Return staged rows in deterministic store order."""

    def find_live_id_by_digest(self, digest: str) -> str:
        """Return the first live row id matching a digest, or an empty string."""

    def upsert_live_rows(self, rows: Sequence[PromotedFactRow]) -> None:
        """Write accepted rows into the live store."""

    def delete_staged_rows(self, row_ids: Sequence[str]) -> None:
        """Remove accepted or rejected rows from staging."""

    def mark_staged_rows_held(
        self,
        metadata_by_id: Mapping[str, Mapping[str, ScalarMetadataValue]],
    ) -> None:
        """Persist hold metadata for rows that remain in staging."""

    def live_count(self) -> int:
        """Return the live store row count."""


SparseSyncCallback = Callable[[Sequence[PromotedFactRow], int], Mapping[str, Any]]
