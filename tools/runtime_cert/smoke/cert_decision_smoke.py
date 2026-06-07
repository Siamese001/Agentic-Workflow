"""Phase D.4 non-promoting cert-decision smoke harness.

End-to-end wiring:

    PhaseCCloseoutReport
        -> evaluate_phase_c_closeout(report, history)            # D.2
        -> write_cert_decision_record(record, repo_root=...)     # D.3
        -> read_cert_decision_records(app_name, repo_root=...)   # D.3 read-back
        -> CertDecisionSmokeReport                               # D.4 output

Implements the approved plan at
``docs/archive/windsurf/legacy-tree/plans/runtime-cert-d4-cert-decision-smoke-7acad5.md``.

Hard invariants enforced at five layers (C.8 input -> D.1 construction ->
D.3 SQL CHECK -> D.3 read-back hydration -> this report's
``__post_init__``):

* ``runtime_certification_status`` is ``NOT_CERTIFIED`` everywhere.
* A ``verdict == "certify"`` row is **not** a certification. It is a
  statement that a hypothetical Phase F would promote the app.
  Phase F does not exist; no scanner ``runtime_mode`` is changed; no
  CI gate is added; no emitter is modified; no app behavior is altered.

This module performs **no** real ``artifacts/ledgers/`` writes in tests
(callers pass ``repo_root=tmp_path``). It performs **no** runtime
certification at any time.
"""

from __future__ import annotations

__adg_consumer_mode__ = "runtime_cert_read"

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Union

from tools.runtime_cert.decisions.cert_decision_evaluator import (
    evaluate_phase_c_closeout,
)
from tools.runtime_cert.decisions.cert_decision_ledger import (
    CertDecisionLedgerWriteResult,
    ledger_path_for_app,
    read_cert_decision_records,
    write_cert_decision_record,
)
from tools.runtime_cert.decisions.cert_decision_record import (
    NOT_CERTIFIED,
    CertificationDecisionRecord,
)
from tools.runtime_cert.reports.phase_c_closeout import PhaseCCloseoutReport


# ---------------------------------------------------------------------------
# Constants.
# ---------------------------------------------------------------------------

DISCLAIMER = (
    "no runtime certification performed — this is Phase D.4 "
    "non-promoting smoke evidence only"
)

SCHEMA_VERSION = "d4-smoke-v1"

# Closed failure-reason ontology (plan §7).
WRITE_COUNT_MISMATCH = "WRITE_COUNT_MISMATCH"
LEDGER_WRITE_SKIPPED = "LEDGER_WRITE_SKIPPED"
MISSING_READBACK = "MISSING_READBACK"
STATUS_NOT_NOT_CERTIFIED = "STATUS_NOT_NOT_CERTIFIED"
DECISION_COUNT_DOES_NOT_MATCH_INPUT = "DECISION_COUNT_DOES_NOT_MATCH_INPUT"
READBACK_DECISION_ID_MISMATCH = "READBACK_DECISION_ID_MISMATCH"

SMOKE_FAILURE_REASONS = frozenset(
    {
        WRITE_COUNT_MISMATCH,
        LEDGER_WRITE_SKIPPED,
        MISSING_READBACK,
        STATUS_NOT_NOT_CERTIFIED,
        DECISION_COUNT_DOES_NOT_MATCH_INPUT,
        READBACK_DECISION_ID_MISMATCH,
    }
)


# ---------------------------------------------------------------------------
# Report dataclass.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CertDecisionSmokeReport:
    """Structured output of one :func:`run_cert_decision_smoke` invocation.

    Every field is immutable. ``__post_init__`` enforces the
    non-promotion + count-balance invariants from plan §7.

    The presence of any ``failure_reasons`` is a **diagnostic**, not a
    fatal error. The harness never raises on a partial-failure;
    downstream tooling (future Phase D.5 calibration) is the one that
    acts on them.
    """

    generated_at_utc: str
    input_app_count: int
    decision_count: int
    written_count: int
    already_exists_count: int
    skipped_count: int
    read_back_count: int
    runtime_certification_status: str  # MUST equal NOT_CERTIFIED
    decision_ids: tuple[str, ...]
    ledger_paths: tuple[Path, ...]
    verdicts: tuple[str, ...]
    write_results: tuple[CertDecisionLedgerWriteResult, ...]
    read_back_records: tuple[CertificationDecisionRecord, ...]
    failure_reasons: tuple[str, ...]
    notes: str = ""
    schema_version: str = SCHEMA_VERSION
    disclaimer: str = DISCLAIMER

    # ------------------------------------------------------------------
    # Invariants (plan §7).
    # ------------------------------------------------------------------

    def __post_init__(self) -> None:
        # Status pin — load-bearing non-promotion invariant.
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                "CertDecisionSmokeReport.runtime_certification_status must "
                f"be {NOT_CERTIFIED!r}; got "
                f"{self.runtime_certification_status!r}"
            )

        # Schema version pin — parsers dispatch on this value.
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(
                "CertDecisionSmokeReport.schema_version must be "
                f"{SCHEMA_VERSION!r}; got {self.schema_version!r}"
            )

        # Disclaimer pin — must carry the canonical no-certification text.
        if "no runtime certification performed" not in self.disclaimer:
            raise ValueError(
                "CertDecisionSmokeReport.disclaimer must contain "
                "'no runtime certification performed'; got "
                f"{self.disclaimer!r}"
            )

        # Type pins for tuple collections.
        for name, val in (
            ("decision_ids", self.decision_ids),
            ("ledger_paths", self.ledger_paths),
            ("verdicts", self.verdicts),
            ("write_results", self.write_results),
            ("read_back_records", self.read_back_records),
            ("failure_reasons", self.failure_reasons),
        ):
            if not isinstance(val, tuple):
                raise TypeError(
                    f"CertDecisionSmokeReport.{name} must be a tuple; got "
                    f"{type(val).__name__}"
                )

        # Non-negative counts.
        for name, val in (
            ("input_app_count", self.input_app_count),
            ("decision_count", self.decision_count),
            ("written_count", self.written_count),
            ("already_exists_count", self.already_exists_count),
            ("skipped_count", self.skipped_count),
            ("read_back_count", self.read_back_count),
        ):
            if not isinstance(val, int) or isinstance(val, bool):
                raise TypeError(
                    f"CertDecisionSmokeReport.{name} must be int; got "
                    f"{type(val).__name__}"
                )
            if val < 0:
                raise ValueError(
                    f"CertDecisionSmokeReport.{name} must be >= 0; got {val}"
                )

        # Parallel-tuple length pins.
        if len(self.decision_ids) != self.decision_count:
            raise ValueError(
                f"CertDecisionSmokeReport.decision_ids length "
                f"({len(self.decision_ids)}) must equal decision_count "
                f"({self.decision_count})"
            )
        if len(self.verdicts) != self.decision_count:
            raise ValueError(
                f"CertDecisionSmokeReport.verdicts length "
                f"({len(self.verdicts)}) must equal decision_count "
                f"({self.decision_count})"
            )
        if len(self.ledger_paths) != self.decision_count:
            raise ValueError(
                f"CertDecisionSmokeReport.ledger_paths length "
                f"({len(self.ledger_paths)}) must equal decision_count "
                f"({self.decision_count})"
            )
        if len(self.write_results) != self.decision_count:
            raise ValueError(
                f"CertDecisionSmokeReport.write_results length "
                f"({len(self.write_results)}) must equal decision_count "
                f"({self.decision_count})"
            )
        if len(self.read_back_records) != self.read_back_count:
            raise ValueError(
                f"CertDecisionSmokeReport.read_back_records length "
                f"({len(self.read_back_records)}) must equal read_back_count "
                f"({self.read_back_count})"
            )

        # Count-balance invariant (plan §7).
        balance = (
            self.written_count + self.already_exists_count + self.skipped_count
        )
        if balance != self.decision_count:
            raise ValueError(
                "CertDecisionSmokeReport: written_count + "
                "already_exists_count + skipped_count "
                f"({balance}) must equal decision_count "
                f"({self.decision_count})"
            )

        # write_results flag counts must match the summary counters.
        written_seen = sum(1 for r in self.write_results if r.written)
        already_seen = sum(1 for r in self.write_results if r.already_exists)
        skipped_seen = sum(1 for r in self.write_results if r.skipped)
        if written_seen != self.written_count:
            raise ValueError(
                f"CertDecisionSmokeReport.written_count ({self.written_count}) "
                f"disagrees with write_results[...].written count "
                f"({written_seen})"
            )
        if already_seen != self.already_exists_count:
            raise ValueError(
                "CertDecisionSmokeReport.already_exists_count "
                f"({self.already_exists_count}) disagrees with "
                f"write_results[...].already_exists count ({already_seen})"
            )
        if skipped_seen != self.skipped_count:
            raise ValueError(
                f"CertDecisionSmokeReport.skipped_count ({self.skipped_count}) "
                f"disagrees with write_results[...].skipped count "
                f"({skipped_seen})"
            )

        # Read-back ceiling (plan §7): can't read back what was never written
        # and can't read back a skipped write.
        max_readable = self.written_count + self.already_exists_count
        if self.read_back_count > max_readable:
            raise ValueError(
                f"CertDecisionSmokeReport.read_back_count ({self.read_back_count}) "
                f"exceeds written + already_exists ({max_readable})"
            )

        # Write-result paths must be non-empty (belt-and-suspenders with D.3).
        for i, wr in enumerate(self.write_results):
            if str(wr.ledger_path) == "":
                raise ValueError(
                    f"CertDecisionSmokeReport.write_results[{i}].ledger_path "
                    "must be non-empty"
                )

        # Every read-back record must carry NOT_CERTIFIED. Structurally
        # guaranteed by D.3 read-back hydration through D.1's
        # __post_init__; this is a defensive cross-check.
        for i, rec in enumerate(self.read_back_records):
            if rec.runtime_certification_status_after != NOT_CERTIFIED:
                raise ValueError(
                    f"CertDecisionSmokeReport.read_back_records[{i}] has "
                    "runtime_certification_status_after="
                    f"{rec.runtime_certification_status_after!r}; "
                    f"must be {NOT_CERTIFIED!r}"
                )
            if rec.runtime_certification_status_before != NOT_CERTIFIED:
                raise ValueError(
                    f"CertDecisionSmokeReport.read_back_records[{i}] has "
                    "runtime_certification_status_before="
                    f"{rec.runtime_certification_status_before!r}; "
                    f"must be {NOT_CERTIFIED!r}"
                )

        # failure_reasons must be drawn from the closed ontology.
        for reason in self.failure_reasons:
            if reason not in SMOKE_FAILURE_REASONS:
                raise ValueError(
                    f"CertDecisionSmokeReport.failure_reasons contains "
                    f"unknown reason {reason!r}; must be one of "
                    f"{sorted(SMOKE_FAILURE_REASONS)}"
                )

    # ------------------------------------------------------------------
    # Serialization.
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Return a JSON-safe dict view.

        ``Path`` instances in ``ledger_paths`` and ``write_results`` are
        converted to ``str``. ``write_results`` items and
        ``read_back_records`` are emitted as nested dicts so that the
        on-disk JSON is fully self-describing.
        """
        return {
            "schema_version": self.schema_version,
            "disclaimer": self.disclaimer,
            "runtime_certification_status": self.runtime_certification_status,
            "generated_at_utc": self.generated_at_utc,
            "input_app_count": self.input_app_count,
            "decision_count": self.decision_count,
            "written_count": self.written_count,
            "already_exists_count": self.already_exists_count,
            "skipped_count": self.skipped_count,
            "read_back_count": self.read_back_count,
            "decision_ids": list(self.decision_ids),
            "ledger_paths": [str(p) for p in self.ledger_paths],
            "verdicts": list(self.verdicts),
            "write_results": [
                {
                    "app_name": wr.app_name,
                    "ledger_path": str(wr.ledger_path),
                    "decision_id": wr.decision_id,
                    "written": wr.written,
                    "already_exists": wr.already_exists,
                    "skipped": wr.skipped,
                    "error": wr.error,
                    "notes": wr.notes,
                }
                for wr in self.write_results
            ],
            "read_back_records": [rec.to_dict() for rec in self.read_back_records],
            "failure_reasons": list(self.failure_reasons),
            "notes": self.notes,
        }

    def to_json(self) -> str:
        """Return a deterministic JSON string with sorted keys."""
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )


# ---------------------------------------------------------------------------
# Internal helpers.
# ---------------------------------------------------------------------------


def _iso_now_utc() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _distinct_apps(
    records: tuple[CertificationDecisionRecord, ...],
) -> tuple[str, ...]:
    """Preserve first-seen order per app (plan §8)."""
    seen: set[str] = set()
    order: list[str] = []
    for rec in records:
        if rec.app_name not in seen:
            seen.add(rec.app_name)
            order.append(rec.app_name)
    return tuple(order)


# ---------------------------------------------------------------------------
# Public API.
# ---------------------------------------------------------------------------


def run_cert_decision_smoke(
    report: PhaseCCloseoutReport,
    *,
    repo_root: Union[str, Path],
    history: Iterable[CertificationDecisionRecord] = (),
    fail_soft: bool = True,
) -> CertDecisionSmokeReport:
    """End-to-end non-promoting smoke: C.8 -> D.2 -> D.3 -> D.3 read-back.

    Parameters
    ----------
    report:
        A ``PhaseCCloseoutReport`` from Phase C.8. Synthetic fixtures
        are the canonical test input; in-production callers pass the
        real closeout built by ``build_phase_c_closeout_report``.
    repo_root:
        **Required** keyword argument. Passed through to
        ``write_cert_decision_record`` and ``read_cert_decision_records``
        so every ledger file lands under
        ``<repo_root>/artifacts/ledgers/cert_decision_<app>.sqlite``.
        Tests pass ``tmp_path``; real runs pass the repo root.
    history:
        Prior ``CertificationDecisionRecord`` values for D.2's
        accumulation + baseline lookup. Default empty tuple.
    fail_soft:
        Forwarded to ``write_cert_decision_record``. Default ``True``
        matches D.3 (SQLite errors absorbed into
        ``CertDecisionLedgerWriteResult.skipped``).

    Returns
    -------
    CertDecisionSmokeReport
        Structured round-trip evidence. Non-empty ``failure_reasons``
        are non-fatal diagnostics; the function never raises on a
        partial failure.

    Raises
    ------
    TypeError
        If ``report`` is not a ``PhaseCCloseoutReport``.
    ValueError
        If ``repo_root`` is ``None`` / empty, or if the D.2 evaluator
        or D.3 read-back raises (propagated unchanged).
    """
    # ------------------------------------------------------------------
    # Input validation.
    # ------------------------------------------------------------------
    if not isinstance(report, PhaseCCloseoutReport):
        raise TypeError(
            "run_cert_decision_smoke: report must be a "
            f"PhaseCCloseoutReport; got {type(report).__name__}"
        )
    if repo_root is None:
        raise ValueError(
            "run_cert_decision_smoke: repo_root is required (pass tmp_path "
            "in tests; never default to the real repo root)"
        )
    repo_root_path = Path(repo_root)
    if str(repo_root_path) == "":
        raise ValueError(
            "run_cert_decision_smoke: repo_root must be a non-empty path"
        )

    input_app_count = len(report.app_summaries)

    # ------------------------------------------------------------------
    # D.2 — evaluate.
    # ------------------------------------------------------------------
    records = evaluate_phase_c_closeout(report, history)
    decision_count = len(records)

    # ------------------------------------------------------------------
    # D.3 — write each record.
    # ------------------------------------------------------------------
    write_results: list[CertDecisionLedgerWriteResult] = []
    for rec in records:
        wr = write_cert_decision_record(
            rec, repo_root=repo_root_path, fail_soft=fail_soft
        )
        write_results.append(wr)
    write_results_t = tuple(write_results)

    written_count = sum(1 for w in write_results_t if w.written)
    already_exists_count = sum(1 for w in write_results_t if w.already_exists)
    skipped_count = sum(1 for w in write_results_t if w.skipped)

    # ------------------------------------------------------------------
    # D.3 — read-back, one call per distinct app, first-seen order.
    # ------------------------------------------------------------------
    distinct_apps = _distinct_apps(records)
    read_back: list[CertificationDecisionRecord] = []
    for app in distinct_apps:
        read_back.extend(
            read_cert_decision_records(app, repo_root=repo_root_path)
        )
    read_back_t = tuple(read_back)
    read_back_ids = {r.decision_id for r in read_back_t}

    # ------------------------------------------------------------------
    # Collect failure reasons (plan §7).
    # ------------------------------------------------------------------
    failure_reasons: list[str] = []
    notes_parts: list[str] = []

    # WRITE_COUNT_MISMATCH — structurally impossible via D.3 but defensive.
    if written_count + already_exists_count + skipped_count != decision_count:
        failure_reasons.append(WRITE_COUNT_MISMATCH)

    # DECISION_COUNT_DOES_NOT_MATCH_INPUT — D.2 contract says one record per
    # app_summary; defensive cross-check.
    if decision_count != input_app_count:
        failure_reasons.append(DECISION_COUNT_DOES_NOT_MATCH_INPUT)

    # LEDGER_WRITE_SKIPPED — any skipped write surfaces as a diagnostic.
    skipped_results = [w for w in write_results_t if w.skipped]
    if skipped_results:
        failure_reasons.append(LEDGER_WRITE_SKIPPED)
        for w in skipped_results:
            notes_parts.append(
                f"skip[{w.app_name}/{w.decision_id[:12]}]: {w.error}"
            )

    # MISSING_READBACK — any written or already-exists decision_id not seen
    # in the read-back set.
    produced_ids = {r.decision_id for r in records}
    expected_in_readback = {
        w.decision_id for w in write_results_t if w.written or w.already_exists
    }
    missing = expected_in_readback - read_back_ids
    if missing:
        failure_reasons.append(MISSING_READBACK)
        notes_parts.append(
            f"missing_readback_ids={sorted(missing)[:5]}"
        )

    # READBACK_DECISION_ID_MISMATCH — read-back has ids not produced by this
    # run (pre-existing ledger rows for the same app).
    extra_readback = read_back_ids - produced_ids
    if extra_readback:
        failure_reasons.append(READBACK_DECISION_ID_MISMATCH)
        notes_parts.append(
            f"extra_readback_ids={sorted(extra_readback)[:5]}"
        )

    # STATUS_NOT_NOT_CERTIFIED — structurally impossible via D.1/D.3 but
    # defensive. Checks records produced by D.2 and records read back.
    status_violation = False
    for rec in records:
        if (
            rec.runtime_certification_status_before != NOT_CERTIFIED
            or rec.runtime_certification_status_after != NOT_CERTIFIED
        ):
            status_violation = True
            break
    if not status_violation:
        for rec in read_back_t:
            if (
                rec.runtime_certification_status_before != NOT_CERTIFIED
                or rec.runtime_certification_status_after != NOT_CERTIFIED
            ):
                status_violation = True
                break
    if status_violation:
        failure_reasons.append(STATUS_NOT_NOT_CERTIFIED)

    # ------------------------------------------------------------------
    # Build report.
    # ------------------------------------------------------------------
    decision_ids = tuple(r.decision_id for r in records)
    verdicts = tuple(r.verdict for r in records)
    ledger_paths = tuple(
        ledger_path_for_app(r.app_name, repo_root=repo_root_path)
        for r in records
    )

    return CertDecisionSmokeReport(
        generated_at_utc=_iso_now_utc(),
        input_app_count=input_app_count,
        decision_count=decision_count,
        written_count=written_count,
        already_exists_count=already_exists_count,
        skipped_count=skipped_count,
        read_back_count=len(read_back_t),
        runtime_certification_status=NOT_CERTIFIED,
        decision_ids=decision_ids,
        ledger_paths=ledger_paths,
        verdicts=verdicts,
        write_results=write_results_t,
        read_back_records=read_back_t,
        failure_reasons=tuple(failure_reasons),
        notes=" | ".join(notes_parts),
        schema_version=SCHEMA_VERSION,
        disclaimer=DISCLAIMER,
    )


def write_cert_decision_smoke_report(
    report: CertDecisionSmokeReport,
    output_path: Union[str, Path],
) -> Path:
    """Write a ``CertDecisionSmokeReport`` to disk as JSON.

    The written document is ``report.to_dict()`` serialized with sorted
    keys. It always includes top-level ``disclaimer``,
    ``runtime_certification_status`` (``NOT_CERTIFIED``), and
    ``schema_version`` (``d4-smoke-v1``) keys.

    Parameters
    ----------
    report:
        A ``CertDecisionSmokeReport``. ``TypeError`` otherwise.
    output_path:
        Target file path. Parent directories are created.

    Returns
    -------
    Path
        The resolved absolute path of the written file.

    Raises
    ------
    TypeError
        If ``report`` is not a ``CertDecisionSmokeReport``.
    ValueError
        Defensive second check that
        ``report.runtime_certification_status == NOT_CERTIFIED``.
    """
    if not isinstance(report, CertDecisionSmokeReport):
        raise TypeError(
            "write_cert_decision_smoke_report: report must be a "
            f"CertDecisionSmokeReport; got {type(report).__name__}"
        )
    # Belt-and-suspenders with the dataclass __post_init__ — guards
    # against bit-rot in a future refactor.
    if report.runtime_certification_status != NOT_CERTIFIED:
        raise ValueError(
            "write_cert_decision_smoke_report: refusing to write report "
            "with runtime_certification_status="
            f"{report.runtime_certification_status!r} — only "
            f"{NOT_CERTIFIED!r} is allowed."
        )

    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report.to_json(), encoding="utf-8")
    return out


__all__ = [
    "DISCLAIMER",
    "SCHEMA_VERSION",
    "SMOKE_FAILURE_REASONS",
    "WRITE_COUNT_MISMATCH",
    "LEDGER_WRITE_SKIPPED",
    "MISSING_READBACK",
    "STATUS_NOT_NOT_CERTIFIED",
    "DECISION_COUNT_DOES_NOT_MATCH_INPUT",
    "READBACK_DECISION_ID_MISMATCH",
    "CertDecisionSmokeReport",
    "run_cert_decision_smoke",
    "write_cert_decision_smoke_report",
]
