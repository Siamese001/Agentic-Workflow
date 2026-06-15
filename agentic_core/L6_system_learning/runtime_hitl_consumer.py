"""Runtime HITL shadow consumer (W6 P6.2 + P6.3).

Per plan runtime-hitl-exit-control-c4e7b3 P6.2/P6.3 and ADR-023 §4 +
gap G8: ``UWG commit authority on shadow-eval-generated rule drafts from
runtime HITL``. Resolution: **this module produces DRAFTS ONLY**. It MUST
NEVER write to config/, rules, or any production artifact directly. All
writes go through a :class:`DraftSink` — the default is filesystem-only
(`artifacts/runtime/hitl_drafts/`) and a production binding routes through
UWG for peer review and commit.

Consumer input  : HitlQualityReport (W6 P6.1) + iterable of LedgerEntry
Consumer output : list[DraftProposal]
Sink contract   : :meth:`DraftSink.submit(proposal)` persists the proposal
                  candidate somewhere that the UWG review workflow can pick
                  up. Sinks DO NOT mutate production policy.

Draft kinds (enumerated, stable for UWG review tooling):

- ``TIMEOUT_TIGHTEN`` — pool X times out too often; propose shorter timeout
- ``FALLBACK_REVIEW`` — pool X's fallback (usually DENY) fires too often;
                       propose changing the fallback or raising threshold
- ``THRESHOLD_RAISE`` — class Y's escalations are always approved with no
                       denials; consider raising the trigger threshold so
                       fewer requests escalate to humans
- ``REASON_CODE_GAP`` — denials lack reason_codes; propose making the field
                       mandatory or adding a constrained vocabulary
- ``APPROVAL_INCONSISTENT`` — approvers in the same pool disagree frequently;
                       propose approver training / policy clarification

Each draft carries enough provenance that a UWG reviewer can reconstruct why
the consumer proposed it (``source_ledger_ids``, ``evidence``).
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field

from ._tracing import sl_span
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence

from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerEntry,
    LedgerState,
)
from agentic_core.L6_system_learning.hitl_decision_quality import (
    HitlQualityBucket,
    HitlQualityReport,
)

_log = logging.getLogger(__name__)

DEFAULT_DRAFT_DIR = Path("artifacts/runtime/hitl_drafts")


class DraftKind(str, Enum):
    """Taxonomy of draft proposals produced by the consumer."""

    TIMEOUT_TIGHTEN = "timeout_tighten"
    FALLBACK_REVIEW = "fallback_review"
    THRESHOLD_RAISE = "threshold_raise"
    REASON_CODE_GAP = "reason_code_gap"
    APPROVAL_INCONSISTENT = "approval_inconsistent"


@dataclass(frozen=True)
class DraftProposal:
    """A candidate rule/policy change. Never committed directly — UWG mediated.

    ``target`` identifies the policy surface the draft applies to (usually a
    YAML key path like ``classes.financial.timeout_s``). ``before`` captures
    the snapshot the consumer observed; ``after`` is the proposed value.

    ``source_ledger_ids`` let a UWG reviewer replay the ledger evidence the
    consumer used, so drafts are auditable end-to-end.
    """

    draft_id: str
    kind: DraftKind
    target: str
    before: object
    after: object
    rationale: str
    hitl_class: str
    approver_pool: str
    sample_size: int
    source_ledger_ids: tuple[str, ...] = ()
    evidence: Mapping[str, object] = field(default_factory=dict)
    created_at: float = 0.0

    def to_dict(self) -> dict[str, object]:
        d = asdict(self)
        d["kind"] = self.kind.value
        d["source_ledger_ids"] = list(self.source_ledger_ids)
        d["evidence"] = dict(self.evidence)
        return d


# ---------------------------------------------------------------------------
# Sink contract — the UWG mediation point
# ---------------------------------------------------------------------------


class DraftSink(Protocol):
    """Persist a :class:`DraftProposal` candidate for UWG review.

    Production implementations: route into the UWG review queue. Test /
    default implementations: write to a staging directory. Sinks MUST NOT
    mutate production policy; UWG is the sole committer.
    """

    def submit(self, proposal: DraftProposal) -> str:
        """Persist the proposal. Return an opaque receipt id."""
        ...  # pragma: no cover — Protocol stub


class FileDraftSink:
    """Default sink — writes each draft as a JSON file under ``root``.

    Filenames are ``<draft_id>.json``. The directory is created lazily.
    This sink is intentionally dumb — it does not validate schemas or
    deduplicate; those responsibilities belong to the UWG review workflow.
    """

    def __init__(self, root: Path | str | None = None) -> None:
        self._root = Path(root) if root is not None else DEFAULT_DRAFT_DIR
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def submit(self, proposal: DraftProposal) -> str:
        path = self._root / f"{proposal.draft_id}.json"
        payload = proposal.to_dict()
        path.write_text(json.dumps(payload, sort_keys=True, indent=2), encoding="utf-8")
        return str(path)

    def list_drafts(self) -> list[DraftProposal]:
        drafts: list[DraftProposal] = []
        for path in sorted(self._root.glob("*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:  # malformed or unreadable
                _log.warning("[FileDraftSink] skipping %s: %s", path, exc)
                continue
            drafts.append(_draft_from_dict(raw))
        return drafts


# ---------------------------------------------------------------------------
# Heuristic thresholds — deliberately conservative so drafts are rare
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ConsumerThresholds:
    """Tunable thresholds. Defaults bias toward producing FEW, HIGH-SIGNAL drafts."""

    min_sample_size: int = 5
    timeout_rate_threshold: float = 0.30  # TIMEOUT_TIGHTEN
    fallback_rate_threshold: float = 0.40  # FALLBACK_REVIEW (same as timeout)
    all_approved_min: int = 10  # THRESHOLD_RAISE: require N approvals
    reason_coverage_threshold: float = 0.60  # REASON_CODE_GAP
    consistency_threshold: float = 0.70  # APPROVAL_INCONSISTENT


# ---------------------------------------------------------------------------
# Consumer
# ---------------------------------------------------------------------------


class RuntimeHitlConsumer:
    """Shadow-eval consumer producing UWG drafts from ledger evidence.

    Usage::

        consumer = RuntimeHitlConsumer(sink=FileDraftSink())
        from agentic_core.L6_system_learning.hitl_decision_quality import (
            HitlDecisionQualityEngine,
        )

        report = HitlDecisionQualityEngine().score_entries(all_entries)
        drafts = consumer.consume(report, all_entries)

    The consumer is STATELESS per call — the same input must produce the same
    drafts (modulo ``draft_id`` which is UUID4; set ``id_factory`` for tests).
    """

    def __init__(
        self,
        *,
        sink: DraftSink | None = None,
        thresholds: ConsumerThresholds | None = None,
        id_factory: Callable[[], str] | None = None,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._sink = sink
        self._thresholds = thresholds or ConsumerThresholds()
        self._id_factory: Callable[[], str] = id_factory or (lambda: uuid.uuid4().hex)
        self._now: Callable[[], float] = now or time.time

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def consume(
        self,
        report: HitlQualityReport,
        entries: Iterable[LedgerEntry] | None = None,
    ) -> list[DraftProposal]:
        """Produce drafts from a quality report + optional ledger entries.

        ``entries`` lets the consumer attach source ledger ids to each draft.
        When omitted, drafts carry an empty ``source_ledger_ids`` tuple but
        retain aggregate evidence (bucket-level counts).
        """
        with sl_span(
            "agentic_core.L6_system_learning.v1.runtime_hitl_consumer.consume",
            {"sl.bucket_count": len(report.buckets), "sl.overall_score": report.overall_score},
        ) as span:
            entries_by_bucket = _group_entries_by_bucket(entries or [])
            drafts: list[DraftProposal] = []
            for bucket in report.buckets:
                if bucket.sample_size < self._thresholds.min_sample_size:
                    continue
                bucket_entries = entries_by_bucket.get((bucket.hitl_class, bucket.approver_pool), [])
                drafts.extend(self._drafts_for_bucket(bucket, bucket_entries))
            span.set_attribute("sl.drafts_produced", len(drafts))
            return drafts

    def consume_and_submit(
        self,
        report: HitlQualityReport,
        entries: Iterable[LedgerEntry] | None = None,
    ) -> list[tuple[DraftProposal, str]]:
        """Generate drafts and submit each to the configured sink.

        Returns pairs of ``(draft, receipt_id)``. Raises RuntimeError if no
        sink was configured — submission is an explicit opt-in so tests that
        only want to inspect drafts never hit the filesystem.
        """
        if self._sink is None:
            raise RuntimeError(
                "RuntimeHitlConsumer: no DraftSink configured. Pass one to "
                "__init__ or call consume() instead."
            )
        drafts = self.consume(report, entries)
        receipts: list[tuple[DraftProposal, str]] = []
        for draft in drafts:
            receipts.append((draft, self._sink.submit(draft)))
        return receipts

    # ------------------------------------------------------------------
    # Per-bucket draft generation
    # ------------------------------------------------------------------

    def _drafts_for_bucket(
        self,
        bucket: HitlQualityBucket,
        entries: Sequence[LedgerEntry],
    ) -> list[DraftProposal]:
        out: list[DraftProposal] = []
        th = self._thresholds
        ledger_ids = tuple(e.ledger_id for e in entries)

        # TIMEOUT_TIGHTEN
        if (
            bucket.resolved_count >= th.min_sample_size
            and bucket.dimensions.timeout_rate >= th.timeout_rate_threshold
        ):
            out.append(
                self._mk_draft(
                    kind=DraftKind.TIMEOUT_TIGHTEN,
                    target=f"classes.{bucket.hitl_class}.timeout_s",
                    before={"timeout_rate_observed": bucket.dimensions.timeout_rate},
                    after={"action": "reduce timeout or add secondary approver pool"},
                    rationale=(
                        f"{bucket.dimensions.timeout_rate:.0%} of {bucket.resolved_count}"
                        f" escalations to pool '{bucket.approver_pool}' timed out."
                    ),
                    bucket=bucket,
                    ledger_ids=ledger_ids,
                    evidence={
                        "timeout_rate": bucket.dimensions.timeout_rate,
                        "threshold": th.timeout_rate_threshold,
                        "resolved": bucket.resolved_count,
                        "latency_p95_ms": bucket.dimensions.latency_p95_ms,
                    },
                )
            )

        # FALLBACK_REVIEW — when denial_rate + timeout_rate together dominate
        fallback_rate = bucket.dimensions.timeout_rate + bucket.dimensions.denial_rate
        if bucket.resolved_count >= th.min_sample_size and fallback_rate >= th.fallback_rate_threshold:
            out.append(
                self._mk_draft(
                    kind=DraftKind.FALLBACK_REVIEW,
                    target=f"classes.{bucket.hitl_class}.fallback",
                    before={"fallback_rate_observed": fallback_rate},
                    after={"action": "review fallback directive or tighten trigger"},
                    rationale=(
                        f"{fallback_rate:.0%} of resolutions went to the "
                        f"default-deny fallback path for class "
                        f"'{bucket.hitl_class}'."
                    ),
                    bucket=bucket,
                    ledger_ids=ledger_ids,
                    evidence={
                        "timeout_rate": bucket.dimensions.timeout_rate,
                        "denial_rate": bucket.dimensions.denial_rate,
                        "threshold": th.fallback_rate_threshold,
                    },
                )
            )

        # THRESHOLD_RAISE — only approvals, nothing else
        all_approved = (
            bucket.resolved_count >= th.all_approved_min
            and bucket.dimensions.timeout_rate == 0.0
            and bucket.dimensions.denial_rate == 0.0
        )
        if all_approved:
            out.append(
                self._mk_draft(
                    kind=DraftKind.THRESHOLD_RAISE,
                    target=f"classes.{bucket.hitl_class}.trigger_threshold",
                    before={"approvals": bucket.resolved_count, "denials": 0, "timeouts": 0},
                    after={"action": "raise trigger threshold to reduce noise"},
                    rationale=(
                        f"All {bucket.resolved_count} escalations in class "
                        f"'{bucket.hitl_class}' were approved; humans may be "
                        f"rubber-stamping — consider raising the trigger "
                        f"threshold."
                    ),
                    bucket=bucket,
                    ledger_ids=ledger_ids,
                    evidence={"rubber_stamp_suspected": True},
                )
            )

        # REASON_CODE_GAP
        if (
            bucket.resolved_count >= th.min_sample_size
            and bucket.dimensions.denial_rate > 0.0
            and bucket.dimensions.reason_coverage < th.reason_coverage_threshold
        ):
            out.append(
                self._mk_draft(
                    kind=DraftKind.REASON_CODE_GAP,
                    target=f"classes.{bucket.hitl_class}.require_reason_code",
                    before={"reason_coverage": bucket.dimensions.reason_coverage},
                    after={"action": "make reason_code required on denial path"},
                    rationale=(
                        f"Only {bucket.dimensions.reason_coverage:.0%} of "
                        f"denials in class '{bucket.hitl_class}' carry a "
                        f"reason_code; audit/learning loops lose signal."
                    ),
                    bucket=bucket,
                    ledger_ids=ledger_ids,
                    evidence={
                        "reason_coverage": bucket.dimensions.reason_coverage,
                        "threshold": th.reason_coverage_threshold,
                    },
                )
            )

        # APPROVAL_INCONSISTENT
        if (
            bucket.resolved_count >= th.min_sample_size
            and bucket.dimensions.approval_consistency < th.consistency_threshold
        ):
            out.append(
                self._mk_draft(
                    kind=DraftKind.APPROVAL_INCONSISTENT,
                    target=f"approver_pools.{bucket.approver_pool}.calibration",
                    before={"approval_consistency": bucket.dimensions.approval_consistency},
                    after={"action": "approver calibration session or policy clarification"},
                    rationale=(
                        f"Approvers in pool '{bucket.approver_pool}' disagree "
                        f"frequently on class '{bucket.hitl_class}' "
                        f"(consistency="
                        f"{bucket.dimensions.approval_consistency:.2f})."
                    ),
                    bucket=bucket,
                    ledger_ids=ledger_ids,
                    evidence={
                        "approval_consistency": bucket.dimensions.approval_consistency,
                        "threshold": th.consistency_threshold,
                    },
                )
            )

        return out

    def _mk_draft(
        self,
        *,
        kind: DraftKind,
        target: str,
        before: object,
        after: object,
        rationale: str,
        bucket: HitlQualityBucket,
        ledger_ids: tuple[str, ...],
        evidence: Mapping[str, object],
    ) -> DraftProposal:
        return DraftProposal(
            draft_id=str(self._id_factory()),
            kind=kind,
            target=target,
            before=before,
            after=after,
            rationale=rationale,
            hitl_class=bucket.hitl_class,
            approver_pool=bucket.approver_pool,
            sample_size=bucket.sample_size,
            source_ledger_ids=ledger_ids,
            evidence=dict(evidence),
            created_at=float(self._now()),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _group_entries_by_bucket(
    entries: Iterable[LedgerEntry],
) -> dict[tuple[str, str], list[LedgerEntry]]:
    grouped: dict[tuple[str, str], list[LedgerEntry]] = {}
    for entry in entries:
        key = (entry.hitl_class.value, entry.approver_pool)
        grouped.setdefault(key, []).append(entry)
    return grouped


def _draft_from_dict(raw: Mapping[str, Any]) -> DraftProposal:
    """Best-effort reconstruction of a :class:`DraftProposal` from JSON.

    Used by :meth:`FileDraftSink.list_drafts` — tolerant of legacy files.
    """
    sample_size_raw = raw.get("sample_size", 0) or 0
    created_at_raw = raw.get("created_at", 0.0) or 0.0
    evidence_raw = raw.get("evidence") or {}
    source_ids_raw = raw.get("source_ledger_ids") or []
    return DraftProposal(
        draft_id=str(raw.get("draft_id", "")),
        kind=DraftKind(str(raw.get("kind", DraftKind.TIMEOUT_TIGHTEN.value))),
        target=str(raw.get("target", "")),
        before=raw.get("before"),
        after=raw.get("after"),
        rationale=str(raw.get("rationale", "")),
        hitl_class=str(raw.get("hitl_class", "")),
        approver_pool=str(raw.get("approver_pool", "")),
        sample_size=int(sample_size_raw),
        source_ledger_ids=tuple(str(s) for s in source_ids_raw),
        evidence=dict(evidence_raw),
        created_at=float(created_at_raw),
    )


# Sanity re-export for downstream type narrowing.
_ACTIVE_LEDGER_STATES = (LedgerState.APPROVED, LedgerState.DENIED, LedgerState.TIMEOUT)


__all__ = [
    "ConsumerThresholds",
    "DEFAULT_DRAFT_DIR",
    "DraftKind",
    "DraftProposal",
    "DraftSink",
    "FileDraftSink",
    "RuntimeHitlConsumer",
]
