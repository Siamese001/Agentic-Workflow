"""
agentic_core/L5_safety/audit/safety_audit_registry.py

P2/L5 Safety Audit Registry — central storage and query for safety audit trails.

Provides SafetyAuditRecord (12 required fields) and thread-safe registry
for audit record persistence, querying, and human review audit extension.
"""

from __future__ import annotations

import hashlib
import logging
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic_core.utils.runners.providers import get_clock
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

logger = logging.getLogger(__name__)
_AUDIT_LOG = logging.getLogger("adg.safety_audit_emitted")
_HUMAN_REVIEW_LOG = logging.getLogger("adg.human_review_audited")


# ---------------------------------------------------------------------------
# Exception classes for Gates A-E
# ---------------------------------------------------------------------------


class SafetyAuditMissingError(Exception):
    """Raised when safety decision occurs without required audit record (Gate A)."""

    pass


class HumanReviewAuditError(Exception):
    """Raised when human review occurs without reviewer metadata (Gate D)."""

    pass


class AuditQueryError(Exception):
    """Raised when audit record query fails (Gate E)."""

    pass


# ---------------------------------------------------------------------------
# SafetyAuditRecord — 12 required fields per spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SafetyAuditRecord:
    """Immutable audit record for safety-governed actions (12 required fields)."""

    safety_audit_id: str
    run_id: str
    trace_id: str
    policy_hash: str
    policy_version: str
    decision_type: str
    decision_outcome: str
    reason_hash: str
    actor_id: str
    action_class: str
    evaluated_input_hash: str
    evaluated_output_hash: str | None
    audit_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        run_id: str,
        trace_id: str,
        policy_hash: str,
        policy_version: str,
        decision_type: str,
        decision_outcome: str,
        reason: str,
        actor_id: str,
        action_class: str,
        evaluated_input: Any,
        evaluated_output: Any = None,
    ) -> SafetyAuditRecord:
        """Factory to create SafetyAuditRecord with computed hashes."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "SafetyAuditRecord.create", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "SafetyAuditRecord.create", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyAuditRecord.create")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyAuditRecord.create".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        safety_audit_id = str(uuid.uuid4())
        reason_hash = hashlib.sha256(reason.encode()).hexdigest()[:16]
        evaluated_input_hash = hashlib.sha256(str(evaluated_input).encode()).hexdigest()[:16]
        evaluated_output_hash = (
            hashlib.sha256(str(evaluated_output).encode()).hexdigest()[:16]
            if evaluated_output is not None
            else None
        )

        return cls(
            safety_audit_id=safety_audit_id,
            run_id=run_id,
            trace_id=trace_id,
            policy_hash=policy_hash,
            policy_version=policy_version,
            decision_type=decision_type,
            decision_outcome=decision_outcome,
            reason_hash=reason_hash,
            actor_id=actor_id,
            action_class=action_class,
            evaluated_input_hash=evaluated_input_hash,
            evaluated_output_hash=evaluated_output_hash,
        )


# ---------------------------------------------------------------------------
# HumanReviewAuditRecord — extends SafetyAuditRecord with review metadata
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HumanReviewAuditRecord:
    """Audit record for human-reviewed safety decisions."""

    base_audit: SafetyAuditRecord
    reviewer_id: str
    reviewer_outcome: str
    override_flag: bool
    override_reason_hash: str
    review_epoch: float = field(default_factory=lambda: get_clock().now_epoch())

    @classmethod
    def create(
        cls,
        base_audit: SafetyAuditRecord,
        reviewer_id: str,
        reviewer_outcome: str,
        override_flag: bool,
        override_reason: str,
    ) -> HumanReviewAuditRecord:
        """Factory to create HumanReviewAuditRecord."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HumanReviewAuditRecord.create")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HumanReviewAuditRecord.create".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        override_reason_hash = hashlib.sha256(override_reason.encode()).hexdigest()[:16]

        return cls(
            base_audit=base_audit,
            reviewer_id=reviewer_id,
            reviewer_outcome=reviewer_outcome,
            override_flag=override_flag,
            override_reason_hash=override_reason_hash,
        )


# ---------------------------------------------------------------------------
# SafetyAuditRegistry — thread-safe audit storage and query
# ---------------------------------------------------------------------------


class SafetyAuditRegistry:
    """Thread-safe registry for safety audit records and queries."""

    _instance: SafetyAuditRegistry | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._audits: dict[str, SafetyAuditRecord] = {}
        self._human_reviews: dict[str, HumanReviewAuditRecord] = {}
        self._run_index: dict[str, list[str]] = {}  # run_id -> audit_ids
        self._trace_index: dict[str, list[str]] = {}  # trace_id -> audit_ids
        self._lock = threading.RLock()

    @classmethod
    def get_instance(cls) -> SafetyAuditRegistry:
        """Singleton accessor."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyAuditRegistry.get_instance")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyAuditRegistry.get_instance".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def persist_audit(self, audit: SafetyAuditRecord) -> None:
        """Persist a safety audit record (Gate A step 5)."""
        with self._lock:
            self._audits[audit.safety_audit_id] = audit

            # Index by run_id for Gate E queries
            if audit.run_id not in self._run_index:
                self._run_index[audit.run_id] = []
            self._run_index[audit.run_id].append(audit.safety_audit_id)

            # Index by trace_id for Gate E queries
            if audit.trace_id not in self._trace_index:
                self._trace_index[audit.trace_id] = []
            self._trace_index[audit.trace_id].append(audit.safety_audit_id)

        _AUDIT_LOG.debug(
            "safety_audit_emitted audit_id=%s run_id=%s trace_id=%s decision_type=%s outcome=%s policy_hash=%s actor=%s action=%s",
            audit.safety_audit_id,
            audit.run_id,
            audit.trace_id,
            audit.decision_type,
            audit.decision_outcome,
            audit.policy_hash,
            audit.actor_id,
            audit.action_class,
        )

        logger.debug(
            "SAFETY_AUDIT_PERSISTED audit_id=%s run_id=%s trace_id=%s decision=%s outcome=%s",
            audit.safety_audit_id,
            audit.run_id,
            audit.trace_id,
            audit.decision_type,
            audit.decision_outcome,
        )

    def persist_human_review(self, review: HumanReviewAuditRecord) -> None:
        """Persist a human review audit record."""
        with self._lock:
            self._human_reviews[review.base_audit.safety_audit_id] = review

        _HUMAN_REVIEW_LOG.debug(
            "human_review_audited audit_id=%s reviewer_id=%s outcome=%s override=%s",
            review.base_audit.safety_audit_id,
            review.reviewer_id,
            review.reviewer_outcome,
            review.override_flag,
        )

        logger.debug(
            "HUMAN_REVIEW_AUDITED audit_id=%s reviewer=%s outcome=%s override=%s",
            review.base_audit.safety_audit_id,
            review.reviewer_id,
            review.reviewer_outcome,
            review.override_flag,
        )

    def query_by_run_id(self, run_id: str) -> list[SafetyAuditRecord]:
        """Query audit records by run_id (Gate E)."""
        with self._lock:
            audit_ids = self._run_index.get(run_id, [])
            return [self._audits[audit_id] for audit_id in audit_ids if audit_id in self._audits]

    def query_by_trace_id(self, trace_id: str) -> list[SafetyAuditRecord]:
        """Query audit records by trace_id (Gate E)."""
        with self._lock:
            audit_ids = self._trace_index.get(trace_id, [])
            return [self._audits[audit_id] for audit_id in audit_ids if audit_id in self._audits]

    def query_by_audit_id(self, audit_id: str) -> SafetyAuditRecord | None:
        """Query audit record by safety_audit_id."""
        with self._lock:
            return self._audits.get(audit_id)

    def query_human_review(self, audit_id: str) -> HumanReviewAuditRecord | None:
        """Query human review audit by base audit_id."""
        with self._lock:
            return self._human_reviews.get(audit_id)

    def get_audit_count(self, run_id: str = "") -> int:
        """Get count of audit records, optionally filtered by run_id."""
        with self._lock:
            if run_id:
                return len(self._run_index.get(run_id, []))
            return len(self._audits)

    def verify_audit_exists(self, audit_id: str) -> bool:
        """Verify audit record exists (Gate A)."""
        with self._lock:
            return audit_id in self._audits

    def verify_policy_hash_present(self, audit_id: str) -> bool:
        """Verify audit record has policy hash (Gate B)."""
        with self._lock:
            audit = self._audits.get(audit_id)
            return audit is not None and bool(audit.policy_hash)

    def verify_decision_outcome_present(self, audit_id: str) -> bool:
        """Verify audit record has decision outcome (Gate C)."""
        with self._lock:
            audit = self._audits.get(audit_id)
            return audit is not None and bool(audit.decision_outcome)

    def verify_human_review_metadata(self, audit_id: str) -> bool:
        """Verify human review has reviewer metadata (Gate D)."""
        with self._lock:
            review = self._human_reviews.get(audit_id)
            return review is not None and bool(review.reviewer_id) and bool(review.reviewer_outcome)


# ---------------------------------------------------------------------------
# Singleton accessors
# ---------------------------------------------------------------------------


def get_safety_audit_registry() -> SafetyAuditRegistry:
    """Get the singleton SafetyAuditRegistry instance."""
    return SafetyAuditRegistry.get_instance()


def reset_safety_audit_registry() -> None:
    """Reset the singleton SafetyAuditRegistry (for testing)."""
    with SafetyAuditRegistry._lock:
        SafetyAuditRegistry._instance = None


__all__ = [
    "SafetyAuditRecord",
    "HumanReviewAuditRecord",
    "SafetyAuditRegistry",
    "SafetyAuditMissingError",
    "HumanReviewAuditError",
    "AuditQueryError",
    "get_safety_audit_registry",
    "reset_safety_audit_registry",
]
