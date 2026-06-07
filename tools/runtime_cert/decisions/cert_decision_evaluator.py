"""Phase D.2 — closeout-to-decision evaluator (ADR-080 §11 D.2).

Pure function. No I/O. No ledger writes. No scanner edits. No CI gates.
No emitter changes. No app behavior changes. No runtime-certification
promotion.

Converts a :class:`PhaseCCloseoutReport` plus an in-memory iterable of
prior :class:`CertificationDecisionRecord` objects into a tuple of
new :class:`CertificationDecisionRecord` objects (one per app in
``report.app_summaries``).

Every produced record carries
``runtime_certification_status_before == runtime_certification_status_after
== NOT_CERTIFIED`` — enforced structurally by the D.1 ``__post_init__``.
A ``verdict == "certify"`` record is **not** a certification. Promotion to
``RUNTIME_CERTIFIED`` / ``FORMAL_EXCEPTION_VERIFIED`` is Phase F's job
(explicitly out of scope for D.2 and all prior D sub-phases).

Adaptations from the planning doc (`docs/archive/windsurf/legacy-tree/plans/runtime-cert-d2-decision-
evaluator-227b38.md`)
----------------------------------------------------------------------------
During implementation three shapes in the D.1 / C.8 contract surface turned
out to differ from the planning assumptions:

1. **`AppCloseoutSummary` stores booleans, not numeric counts.** The plan
   §7 table assumed fields like ``passed_trace_observed_n``; the actual
   summary exposes ``passed_trace_observed: bool``. Each summary is treated
   as **one observation** contributing ``(1, 1)`` to ``(successes, n)`` if
   the readiness flag is ``True`` and ``(0, 1)`` otherwise. Per ADR-080
   §13, accumulating to ``n ≥ 30`` therefore requires 30 weekly closeouts
   over a stable ``manifest_hash`` — which is the intended pace.
2. **`PhaseCCloseoutReport` carries no ``closeout_report_id`` /
   ``closeout_report_hash`` field.** Both are derived deterministically
   from ``report.to_dict()`` via :func:`derive_closeout_report_hash`. No
   filesystem bytes are read.
3. **`AppCloseoutSummary.forbidden_violations` doubles as the
   ``failed_controls`` list for formal-exception apps.** The evaluator
   branches on ``evidence_kind`` to map it to
   :data:`FORBIDDEN_SPAN_VIOLATION` vs
   :data:`FORMAL_CONTROL_MISSING_OR_FAILED`.

These adaptations preserve the evaluator's purity and the plan's decision
rules; no new I/O surface is introduced.

Also resolves plan §14 unresolved questions:

- **Q1 (existing Wilson helper reuse)**: Declined. The existing
  ``agentic_core.L2_execution.healers.cascade_calibrator.wilson_lower_bound``
  uses keyword-only ``z`` and silently clamps invalid inputs; this module's
  contract requires positional ``z`` and ``ValueError`` on invalid inputs,
  and ``tools/runtime_cert`` avoids hard dependencies on L2 healers
  (layer-gravity). A local helper ships here.
- **Q2 (``next_review_utc`` cadence)**: 7 days for ``hold`` and ``reject``
  (both states indicate action is needed), 30 days for ``certify``
  (matches ADR-080 §5 default for certify).
- **Q3 (formal-control required set)**: Consumed from
  ``AppCloseoutSummary.missing_contracts`` and ``.forbidden_violations``,
  which C.5 already populates from
  ``system_learning.runtime_adg.app_route_contracts.FormalExceptionContract``.
  D.2 does not re-derive the required set.
- **Q4 (z-score boundary smoothing)**: No smoothing; ``z_score`` is
  clamped to ``>= 0.0`` at boundaries. Negative observed regressions
  surface through ``UPLIFT_NOT_POSITIVE``.
- **Q5 (output order)**: Output preserves ``report.app_summaries`` order.
"""

from __future__ import annotations

# ADR-079 consumer mode declaration (required for all runtime-cert tools).
__adg_consumer_mode__ = "runtime_cert_read"

import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from typing import Iterable, Mapping, Optional

from tools.runtime_cert.decisions.cert_decision_record import (
    CertificationDecisionRecord,
    EVIDENCE_KIND_BTC,
    EVIDENCE_KIND_FORMAL_EXCEPTION,
    EVIDENCE_KIND_R3,
    EVIDENCE_KIND_SKIPPED,
    NOT_CERTIFIED,
    VERDICT_CERTIFY,
    VERDICT_HOLD,
    VERDICT_REJECT,
    compute_decision_id,
)
from tools.runtime_cert.reports.phase_c_closeout import (
    AppCloseoutSummary,
    PhaseCCloseoutReport,
)

# ---------------------------------------------------------------------------
# Thresholds — ADR-080 §7 global defaults. Per-route thresholds deferred
# to D.5 calibration (ADR-080 §0 Q2). Not configurable in D.2.
# ---------------------------------------------------------------------------

MIN_N: int = 30
MIN_WILSON_LOWER: float = 0.60
MIN_Z_SCORE: float = 1.96
MIN_UPLIFT: float = 0.0  # strict inequality applied at check-time

# Review cadences (days). See module docstring §Q2.
NEXT_REVIEW_DAYS_CERTIFY: int = 30
NEXT_REVIEW_DAYS_HOLD: int = 7
NEXT_REVIEW_DAYS_REJECT: int = 7


# ---------------------------------------------------------------------------
# Failure-reason ontology (closed) — plan §6, AG-3.
# ---------------------------------------------------------------------------

CLOSEOUT_MISSING = "CLOSEOUT_MISSING"
SAMPLE_SIZE_TOO_SMALL = "SAMPLE_SIZE_TOO_SMALL"
WILSON_BELOW_THRESHOLD = "WILSON_BELOW_THRESHOLD"
Z_SCORE_BELOW_THRESHOLD = "Z_SCORE_BELOW_THRESHOLD"
UPLIFT_NOT_POSITIVE = "UPLIFT_NOT_POSITIVE"
CRITICAL_BLOCKERS_PRESENT = "CRITICAL_BLOCKERS_PRESENT"
FORBIDDEN_SPAN_VIOLATION = "FORBIDDEN_SPAN_VIOLATION"
FORMAL_CONTROL_MISSING_OR_FAILED = "FORMAL_CONTROL_MISSING_OR_FAILED"
MANIFEST_HASH_DRIFT = "MANIFEST_HASH_DRIFT"
AMBIGUOUS_EVIDENCE = "AMBIGUOUS_EVIDENCE"
NOT_TRACE_OBSERVED_READY = "NOT_TRACE_OBSERVED_READY"
NOT_FORMAL_EXCEPTION_OBSERVED_READY = "NOT_FORMAL_EXCEPTION_OBSERVED_READY"

FAILURE_REASONS: frozenset[str] = frozenset(
    {
        CLOSEOUT_MISSING,
        SAMPLE_SIZE_TOO_SMALL,
        WILSON_BELOW_THRESHOLD,
        Z_SCORE_BELOW_THRESHOLD,
        UPLIFT_NOT_POSITIVE,
        CRITICAL_BLOCKERS_PRESENT,
        FORBIDDEN_SPAN_VIOLATION,
        FORMAL_CONTROL_MISSING_OR_FAILED,
        MANIFEST_HASH_DRIFT,
        AMBIGUOUS_EVIDENCE,
        NOT_TRACE_OBSERVED_READY,
        NOT_FORMAL_EXCEPTION_OBSERVED_READY,
    }
)


# ---------------------------------------------------------------------------
# Wilson lower-bound — plan §4, AG-1. Local, pure, stdlib only.
# ---------------------------------------------------------------------------


def wilson_lower_bound(successes: int, n: int, z: float = 1.96) -> float:
    """Wilson score-interval lower bound for a binomial proportion.

    Formula (same as every standard reference; see e.g. Wikipedia's
    "Binomial proportion confidence interval — Wilson score interval")::

        phat   = successes / n
        denom  = 1 + z^2 / n
        centre = (phat + z^2 / (2n)) / denom
        halfw  = z * sqrt((phat*(1-phat) + z^2 / (4n)) / n) / denom
        lower  = max(0.0, centre - halfw)

    Parameters
    ----------
    successes : int
        Observed success count. Must satisfy ``0 <= successes <= n``.
    n : int
        Total observation count. Must satisfy ``n >= 0``.
    z : float, optional
        Standard-normal quantile. Must be strictly positive. Default
        ``1.96`` = 95% two-sided confidence interval.

    Returns
    -------
    float
        Lower bound of the Wilson interval, clamped to ``[0.0, 1.0]``.
        Returns ``0.0`` when ``n == 0``.

    Raises
    ------
    TypeError
        If ``successes`` or ``n`` is not ``int`` (``bool`` rejected too).
    ValueError
        If ``n < 0``, ``successes < 0``, ``successes > n``, or ``z <= 0``.
    """
    if isinstance(successes, bool) or not isinstance(successes, int):
        raise TypeError("wilson_lower_bound: successes must be int")
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("wilson_lower_bound: n must be int")
    if not isinstance(z, (int, float)) or isinstance(z, bool):
        raise TypeError("wilson_lower_bound: z must be a positive real number")
    if n < 0:
        raise ValueError(f"wilson_lower_bound: n must be >= 0; got {n}")
    if successes < 0:
        raise ValueError(
            f"wilson_lower_bound: successes must be >= 0; got {successes}"
        )
    if successes > n:
        raise ValueError(
            f"wilson_lower_bound: successes ({successes}) must be <= n ({n})"
        )
    if z <= 0.0:
        raise ValueError(f"wilson_lower_bound: z must be > 0; got {z}")

    if n == 0:
        return 0.0

    zf = float(z)
    nf = float(n)
    phat = successes / nf
    z2 = zf * zf
    denom = 1.0 + z2 / nf
    centre = (phat + z2 / (2.0 * nf)) / denom
    halfwidth = zf * math.sqrt((phat * (1.0 - phat) + z2 / (4.0 * nf)) / nf) / denom
    lower = centre - halfwidth
    return max(0.0, min(1.0, lower))


# ---------------------------------------------------------------------------
# Closeout-hash derivation (pure; no filesystem).
# ---------------------------------------------------------------------------


def derive_closeout_report_hash(report: PhaseCCloseoutReport) -> str:
    """Deterministic SHA-256 of the report's canonical-JSON dict view.

    Pure. No filesystem access. The hash is stable across equivalent
    in-memory report objects and changes whenever any nested summary
    changes.
    """
    payload = json.dumps(
        report.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Evidence counting — plan §7, AG-5.
# ---------------------------------------------------------------------------


def _successes_and_total_from_summary(summary: AppCloseoutSummary) -> tuple[int, int]:
    """Return ``(successes, total)`` for a single closeout summary.

    Per module docstring §1 adaptation: each summary contributes one
    observation. ``(1, 1)`` when the readiness flag for the summary's
    evidence kind is True, else ``(0, 1)``. ``skipped`` summaries
    contribute ``(0, 0)`` — they add no weight to the evidence window.
    """
    kind = summary.evidence_kind
    if kind in (EVIDENCE_KIND_R3, EVIDENCE_KIND_BTC):
        return (1, 1) if summary.passed_trace_observed else (0, 1)
    if kind == EVIDENCE_KIND_FORMAL_EXCEPTION:
        return (
            (1, 1) if summary.passed_formal_exception_observed else (0, 1)
        )
    # EVIDENCE_KIND_SKIPPED — contributes nothing.
    return (0, 0)


def _accumulate_history(
    summary: AppCloseoutSummary,
    history: tuple[CertificationDecisionRecord, ...],
) -> tuple[int, int, tuple[CertificationDecisionRecord, ...]]:
    """Accumulate history matching ``(app_name, manifest_hash)``.

    Returns ``(successes, n, same_app_history)`` where ``same_app_history``
    is the subset of history for the same ``app_name`` regardless of
    manifest (used by uplift baseline selection per ADR-080 §0 Q3).
    """
    current_succ, current_n = _successes_and_total_from_summary(summary)
    succ = current_succ
    n = current_n
    same_app: list[CertificationDecisionRecord] = []
    for prior in history:
        if prior.app_name != summary.app_name:
            continue
        same_app.append(prior)
        if prior.manifest_hash == summary.manifest_hash:
            succ += prior.trace_observed_success_n
            n += prior.trace_observed_n
    return succ, n, tuple(same_app)


def _select_baseline_rate(
    same_app_history: tuple[CertificationDecisionRecord, ...],
) -> float:
    """Pick most-recent prior decision for same app, irrespective of manifest.

    Returns ``0.0`` when no prior exists. Per plan §8 and ADR-080 §0 Q3.
    """
    if not same_app_history:
        return 0.0
    prior = max(same_app_history, key=lambda r: r.generated_at_utc)
    return float(prior.evidence_rate)


def _compute_z_score(
    evidence_rate: float, baseline_rate: float, n: int
) -> float:
    """Normal-approximation z-score. Clamped at ``>= 0.0``."""
    if n <= 0:
        return 0.0
    if baseline_rate <= 0.0 or baseline_rate >= 1.0:
        # Boundary case: std-err collapses. Return 0.0 rather than
        # infinities or NaN; plan §14 Q4 explicitly chose "no smoothing".
        return 0.0
    std_err = math.sqrt(baseline_rate * (1.0 - baseline_rate) / n)
    if std_err == 0.0:
        return 0.0
    z = (evidence_rate - baseline_rate) / std_err
    return max(0.0, z)


# ---------------------------------------------------------------------------
# Verdict derivation — plan §5, AG-4.
# ---------------------------------------------------------------------------


def _derive_reject_reasons(
    summary: AppCloseoutSummary,
    n: int,
    same_app_history: tuple[CertificationDecisionRecord, ...],
) -> list[str]:
    """Collect ALL firing reject reasons. Empty list => no reject."""
    reasons: list[str] = []
    kind = summary.evidence_kind

    # Blocker pre-check. For R3/BTC: critical-blocker = missing_contracts
    # OR unknown_needs_runtime_run (hard blockers that prevent evidence
    # accumulation). For formal_exception: handled below under
    # FORMAL_CONTROL_MISSING_OR_FAILED.
    if kind in (EVIDENCE_KIND_R3, EVIDENCE_KIND_BTC):
        if summary.missing_contracts or summary.unknown_needs_runtime_run:
            reasons.append(CRITICAL_BLOCKERS_PRESENT)
        if summary.forbidden_violations:
            reasons.append(FORBIDDEN_SPAN_VIOLATION)
    elif kind == EVIDENCE_KIND_FORMAL_EXCEPTION:
        if (
            summary.missing_contracts  # unpopulated required controls
            or summary.forbidden_violations  # C.5's failed_controls list
            or not summary.passed_formal_exception_observed
        ):
            # Only fire the reject reason when there is a *concrete* failure
            # (missing or failed). If formal-exception is simply
            # unobserved-yet (passed_formal_exception_observed False with
            # empty missing/failed), that is a HOLD (see hold pre-check),
            # not a REJECT.
            if summary.missing_contracts or summary.forbidden_violations:
                reasons.append(FORMAL_CONTROL_MISSING_OR_FAILED)

    # Manifest-hash drift — only rejects when history existed for the same
    # app on a different manifest AND current n is still below threshold
    # (per plan AG-5). This prevents false-reject on a legitimate first-
    # ever run for a new manifest.
    if same_app_history and n < MIN_N:
        prior_on_same_manifest = any(
            h.manifest_hash == summary.manifest_hash for h in same_app_history
        )
        if not prior_on_same_manifest:
            reasons.append(MANIFEST_HASH_DRIFT)

    # Ambiguous evidence — skipped summaries whose notes/blockers suggest
    # runnable work exists. Heuristic: a skipped summary should be a
    # truly-inapplicable app; non-empty missing/forbidden/unknown lists
    # contradict that intent.
    if kind == EVIDENCE_KIND_SKIPPED:
        if (
            summary.missing_contracts
            or summary.forbidden_violations
            or summary.unknown_needs_runtime_run
            or summary.passed_trace_observed
            or summary.passed_formal_exception_observed
        ):
            reasons.append(AMBIGUOUS_EVIDENCE)

    # Dedupe while preserving insertion order.
    seen: set[str] = set()
    deduped: list[str] = []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            deduped.append(r)
    return deduped


def _derive_hold_reasons(
    summary: AppCloseoutSummary,
    n: int,
    wilson: float,
    z: float,
    uplift: float,
) -> list[str]:
    """Collect hold reasons when no reject fired but certify also does not pass."""
    reasons: list[str] = []
    kind = summary.evidence_kind

    if kind == EVIDENCE_KIND_SKIPPED:
        # A skipped summary with no ambiguity simply has no evidence.
        reasons.append(CLOSEOUT_MISSING)
        return reasons

    if n < MIN_N:
        reasons.append(SAMPLE_SIZE_TOO_SMALL)
    if wilson < MIN_WILSON_LOWER:
        reasons.append(WILSON_BELOW_THRESHOLD)
    if z < MIN_Z_SCORE:
        reasons.append(Z_SCORE_BELOW_THRESHOLD)
    if uplift <= MIN_UPLIFT:
        reasons.append(UPLIFT_NOT_POSITIVE)

    # Evidence-kind-specific readiness checks — only when the app hasn't
    # produced a single successful observation yet AND has unresolved
    # observations. Captures the "promising but not yet observed" state.
    if kind in (EVIDENCE_KIND_R3, EVIDENCE_KIND_BTC):
        if not summary.passed_trace_observed and summary.unknown_needs_runtime_run:
            reasons.append(NOT_TRACE_OBSERVED_READY)
    elif kind == EVIDENCE_KIND_FORMAL_EXCEPTION:
        if (
            not summary.passed_formal_exception_observed
            and not summary.missing_contracts
            and not summary.forbidden_violations
        ):
            reasons.append(NOT_FORMAL_EXCEPTION_OBSERVED_READY)

    return reasons


def _derive_verdict(
    summary: AppCloseoutSummary,
    n: int,
    wilson: float,
    z: float,
    uplift: float,
    same_app_history: tuple[CertificationDecisionRecord, ...],
) -> tuple[str, tuple[str, ...]]:
    """Return ``(verdict, failure_reasons)``. All rule-table logic here."""
    reject = _derive_reject_reasons(summary, n, same_app_history)
    if reject:
        return VERDICT_REJECT, tuple(reject)

    if (
        n >= MIN_N
        and wilson >= MIN_WILSON_LOWER
        and z >= MIN_Z_SCORE
        and uplift > MIN_UPLIFT
    ):
        return VERDICT_CERTIFY, ()

    hold = _derive_hold_reasons(summary, n, wilson, z, uplift)
    # Defensive: if no concrete hold reason but we reached here, surface
    # SAMPLE_SIZE_TOO_SMALL as the honest default (evidence is too thin
    # to certify).
    if not hold:
        hold.append(SAMPLE_SIZE_TOO_SMALL)
    return VERDICT_HOLD, tuple(hold)


# ---------------------------------------------------------------------------
# Next-review-date computation.
# ---------------------------------------------------------------------------


def _parse_iso8601_utc(s: str) -> datetime:
    """Parse ``generated_at`` / ``generated_at_utc`` ISO-8601.

    Accepts both ``...Z`` suffix and ``+00:00`` offset. Returns a
    timezone-aware UTC datetime.
    """
    candidate = s.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    dt = datetime.fromisoformat(candidate)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


def _next_review_utc(generated_at: str, verdict: str) -> str:
    """Return ISO-8601 UTC string for the next review.

    Delta: 30d certify, 7d hold, 7d reject.
    """
    try:
        base = _parse_iso8601_utc(generated_at)
    except ValueError:
        # Defensive: unparseable timestamps should not crash the evaluator;
        # fall back to "now + delta" without raising. This cannot happen
        # for well-formed PhaseCCloseoutReport inputs (C.8 always emits
        # ``_utc_now_iso``) but keeps D.2 robust to future changes.
        base = datetime.now(tz=timezone.utc)

    if verdict == VERDICT_CERTIFY:
        days = NEXT_REVIEW_DAYS_CERTIFY
    elif verdict == VERDICT_HOLD:
        days = NEXT_REVIEW_DAYS_HOLD
    else:
        days = NEXT_REVIEW_DAYS_REJECT
    return (base + timedelta(days=days)).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Public evaluator — plan §4.
# ---------------------------------------------------------------------------


def evaluate_phase_c_closeout(
    report: PhaseCCloseoutReport,
    history: Iterable[CertificationDecisionRecord] = (),
    *,
    closeout_report_id: Optional[str] = None,
    closeout_report_hash: Optional[str] = None,
) -> tuple[CertificationDecisionRecord, ...]:
    """Convert a C.8 closeout + history into D.1 decision records.

    Pure. No I/O. No ledger writes. No scanner promotion. One record
    per app in ``report.app_summaries``, in input order.

    Parameters
    ----------
    report : PhaseCCloseoutReport
        The closeout report from Phase C.8.
    history : Iterable[CertificationDecisionRecord], optional
        Prior decision records for accumulation and baseline lookup.
        Consumed at most once. Default empty tuple.
    closeout_report_id : str, optional
        Identifier of the closeout report (file path, UUID, etc.). If
        omitted, derives to ``"closeout:<hash16>"`` from the computed
        hash. Non-empty string.
    closeout_report_hash : str, optional
        64-lowercase-hex SHA-256 of the closeout report. If omitted,
        derives deterministically from ``report.to_dict()`` via
        :func:`derive_closeout_report_hash`.

    Returns
    -------
    tuple[CertificationDecisionRecord, ...]
        One record per ``report.app_summaries`` entry, same order. Each
        record has ``runtime_certification_status_after == NOT_CERTIFIED``
        unconditionally (enforced structurally by the D.1
        ``__post_init__``).

    Raises
    ------
    TypeError
        If ``report`` is not a :class:`PhaseCCloseoutReport`.
    ValueError
        If the report's ``runtime_certification_status`` is anything
        other than ``NOT_CERTIFIED`` (defensive cross-check).
    """
    if not isinstance(report, PhaseCCloseoutReport):
        raise TypeError(
            "evaluate_phase_c_closeout: report must be PhaseCCloseoutReport"
        )
    if report.runtime_certification_status != NOT_CERTIFIED:
        raise ValueError(
            "evaluate_phase_c_closeout: report.runtime_certification_status "
            f"must be {NOT_CERTIFIED!r}; got "
            f"{report.runtime_certification_status!r}. "
            "Phase D.2 never evaluates a pre-certified report."
        )

    history_tuple: tuple[CertificationDecisionRecord, ...] = tuple(history)

    effective_hash = closeout_report_hash or derive_closeout_report_hash(report)
    effective_id = closeout_report_id or f"closeout:{effective_hash[:16]}"

    records: list[CertificationDecisionRecord] = []
    for summary in report.app_summaries:
        records.append(
            _evaluate_one(
                summary=summary,
                report_generated_at=report.generated_at,
                closeout_report_id=effective_id,
                closeout_report_hash=effective_hash,
                history=history_tuple,
            )
        )
    return tuple(records)


def _evaluate_one(
    *,
    summary: AppCloseoutSummary,
    report_generated_at: str,
    closeout_report_id: str,
    closeout_report_hash: str,
    history: tuple[CertificationDecisionRecord, ...],
) -> CertificationDecisionRecord:
    """Build one decision record for one summary."""

    # --- evidence accumulation -------------------------------------------
    succ, n, same_app_history = _accumulate_history(summary, history)

    evidence_rate = (succ / n) if n > 0 else 0.0
    wilson = wilson_lower_bound(succ, n, 1.96) if n > 0 else 0.0
    baseline_rate = _select_baseline_rate(same_app_history)
    uplift = evidence_rate - baseline_rate
    z = _compute_z_score(evidence_rate, baseline_rate, n)

    # --- verdict ---------------------------------------------------------
    verdict, failure_reasons = _derive_verdict(
        summary=summary,
        n=n,
        wilson=wilson,
        z=z,
        uplift=uplift,
        same_app_history=same_app_history,
    )

    # --- assemble record --------------------------------------------------
    decision_id = compute_decision_id(
        summary.app_name, summary.manifest_hash, closeout_report_hash
    )
    return CertificationDecisionRecord(
        decision_id=decision_id,
        generated_at_utc=report_generated_at,
        app_name=summary.app_name,
        route_shape=summary.route_shape,
        manifest_hash=summary.manifest_hash,
        evidence_kind=summary.evidence_kind,
        closeout_report_id=closeout_report_id,
        closeout_report_hash=closeout_report_hash,
        trace_observed_n=n,
        trace_observed_success_n=succ,
        evidence_rate=evidence_rate,
        wilson_lower=wilson,
        z_score=z,
        uplift=uplift,
        verdict=verdict,
        failure_reasons=failure_reasons,
        next_review_utc=_next_review_utc(report_generated_at, verdict),
        runtime_certification_status_before=NOT_CERTIFIED,
        runtime_certification_status_after=NOT_CERTIFIED,
    )


__all__ = [
    # Thresholds
    "MIN_N",
    "MIN_WILSON_LOWER",
    "MIN_Z_SCORE",
    "MIN_UPLIFT",
    "NEXT_REVIEW_DAYS_CERTIFY",
    "NEXT_REVIEW_DAYS_HOLD",
    "NEXT_REVIEW_DAYS_REJECT",
    # Failure reasons
    "FAILURE_REASONS",
    "CLOSEOUT_MISSING",
    "SAMPLE_SIZE_TOO_SMALL",
    "WILSON_BELOW_THRESHOLD",
    "Z_SCORE_BELOW_THRESHOLD",
    "UPLIFT_NOT_POSITIVE",
    "CRITICAL_BLOCKERS_PRESENT",
    "FORBIDDEN_SPAN_VIOLATION",
    "FORMAL_CONTROL_MISSING_OR_FAILED",
    "MANIFEST_HASH_DRIFT",
    "AMBIGUOUS_EVIDENCE",
    "NOT_TRACE_OBSERVED_READY",
    "NOT_FORMAL_EXCEPTION_OBSERVED_READY",
    # Functions
    "wilson_lower_bound",
    "derive_closeout_report_hash",
    "evaluate_phase_c_closeout",
]
