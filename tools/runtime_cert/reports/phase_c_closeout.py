"""Phase C closeout report — runtime-certification readiness aggregator.

Aggregates the outputs of Phase C.3 (R3 evidence), C.4 (BTC evidence),
C.5 (formal-exception evidence), and C.7 (attribute-hardening gap report)
into a single non-promoting cross-app readiness view. Produces a
structured ``PhaseCCloseoutReport`` and an optional Markdown emitter.

This module is strictly non-promoting. Every app summary pins
``runtime_certification_status = NOT_CERTIFIED`` regardless of evidence
state. Phase D certification decisions are out of scope.

Design references
-----------------
- C.3 extractor: ``tools/runtime_cert/extractors/r3_evidence.py``
- C.4 extractor: ``tools/runtime_cert/extractors/btc_evidence.py``
- C.5 extractor: ``tools/runtime_cert/extractors/formal_exception_evidence.py``
- C.7 gap report: ``tools/runtime_cert/reports/attribute_hardening_gap.py``
- Contracts:    ``system_learning/runtime_adg/app_route_contracts.py``
- Phase C plan: ``docs/plans/runtime_cert_phase_c_trace_collector_plan.md``

What this module does
---------------------
- Accepts a sequence of ``AppRouteContract`` objects and a per-app
  mapping of ``NormalizedTraceRow`` batches.
- For each app, dispatches to the correct Phase C extractor based on
  ``contract.route_shape``:

    * ``R3_grounded_read``         → ``extract_r3_evidence`` + C.7 gap report
    * ``build_time_compiler``      → ``extract_btc_evidence`` + C.7 gap report
    * ``evaluator_only`` or
      ``core_adjacent_utility``    → ``extract_formal_exception_evidence``
                                     (no gap report — formal-exception apps
                                     have no required R3/BTC contracts)

- Produces one ``AppCloseoutSummary`` per app and a top-level
  ``PhaseCCloseoutReport`` with aggregated counts and recommendations.

What this module does NOT do
----------------------------
- Does NOT certify any app. ``runtime_certification_status`` is always
  ``NOT_CERTIFIED`` (both constructors enforce this).
- Does NOT scan the filesystem (the builder is pure); an optional helper
  ``load_contracts_from_manifests`` exists for operator convenience.
- Does NOT modify any emitter, scanner, or CI gate.
- Does NOT promote any app to ``RUNTIME_CERTIFIED`` or
  ``FORMAL_EXCEPTION_VERIFIED``.
- Does NOT implement Phase D certification decision logic — the
  closeout is the handoff artifact for Phase D planning, nothing more.
"""

from __future__ import annotations

# ADR-079 consumer mode declaration (required for all runtime-cert tools).
__adg_consumer_mode__ = "runtime_cert_read"

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Iterable, Mapping

from agentic_core.L6_system_learning.app_route_contracts import (
    AppRouteContract,
    RouteShape,
)
from tools.runtime_cert.extractors.btc_evidence import extract_btc_evidence
from tools.runtime_cert.extractors.formal_exception_evidence import (
    extract_formal_exception_evidence,
)
from tools.runtime_cert.extractors.r3_evidence import extract_r3_evidence
from tools.runtime_cert.reports.attribute_hardening_gap import (
    AttributeHardeningGapReport,
    SEVERITY_INFO,
    build_attribute_hardening_gap_report,
)
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED
from tools.runtime_cert.trace_row_normalizer import NormalizedTraceRow

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Evidence kind label per app summary.
EVIDENCE_KIND_R3: Final[str] = "r3"
EVIDENCE_KIND_BTC: Final[str] = "btc"
EVIDENCE_KIND_FORMAL_EXCEPTION: Final[str] = "formal_exception"
EVIDENCE_KIND_SKIPPED: Final[str] = "skipped"

_VALID_EVIDENCE_KINDS: Final[frozenset[str]] = frozenset(
    {
        EVIDENCE_KIND_R3,
        EVIDENCE_KIND_BTC,
        EVIDENCE_KIND_FORMAL_EXCEPTION,
        EVIDENCE_KIND_SKIPPED,
    }
)

#: The single disclaimer embedded in every Markdown output.
REPORT_DISCLAIMER: Final[str] = (
    "No runtime certification performed. This is Phase C closeout evidence only; "
    "Phase D planning is required before any certification decision logic."
)


# ---------------------------------------------------------------------------
# AppCloseoutSummary
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AppCloseoutSummary:
    """One app's Phase C closeout summary.

    ``runtime_certification_status`` is always ``NOT_CERTIFIED``; the
    constructor rejects any other value. ``passed_trace_observed`` /
    ``passed_formal_exception_observed`` signal Phase D readiness only and
    do NOT promote the certification status.
    """

    app_name: str
    route_shape: str
    static_runtime_mode: str
    manifest_hash: str
    runtime_certification_status: str

    #: One of ``EVIDENCE_KIND_*`` — identifies which extractor ran.
    evidence_kind: str

    #: Readiness flags (meaningful only for the matching evidence kind).
    passed_trace_observed: bool
    passed_formal_exception_observed: bool

    #: Contract-level gap buckets.
    missing_contracts: tuple[str, ...]
    forbidden_violations: tuple[str, ...]
    attribute_hardening_required: tuple[str, ...]
    unknown_needs_runtime_run: tuple[str, ...]

    #: Gap-report aggregates (zero for formal-exception / skipped apps).
    gap_count: int
    highest_gap_severity: str

    #: Deduplicated recommendations from extractor + gap report.
    recommendations: tuple[str, ...]

    notes: str

    def __post_init__(self) -> None:
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                f"AppCloseoutSummary.runtime_certification_status must be "
                f"{NOT_CERTIFIED!r}; got {self.runtime_certification_status!r}. "
                "Phase C closeout never writes a certification verdict."
            )
        if self.evidence_kind not in _VALID_EVIDENCE_KINDS:
            raise ValueError(
                f"AppCloseoutSummary.evidence_kind must be one of "
                f"{sorted(_VALID_EVIDENCE_KINDS)}; got {self.evidence_kind!r}"
            )
        if self.gap_count < 0:
            raise ValueError(
                f"AppCloseoutSummary.gap_count must be >= 0; got {self.gap_count}"
            )

    @property
    def has_blocker(self) -> bool:
        """True iff this app has any readiness blocker (see ``blocker_count``)."""
        if self.missing_contracts:
            return True
        if self.forbidden_violations:
            return True
        if self.attribute_hardening_required:
            return True
        if self.unknown_needs_runtime_run:
            return True
        if self.evidence_kind == EVIDENCE_KIND_FORMAL_EXCEPTION:
            # For formal-exception apps, `passed_formal_exception_observed=False`
            # is itself a blocker — either failed controls OR missing implementations.
            if not self.passed_formal_exception_observed:
                return True
        if self.gap_count > 0:
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "route_shape": self.route_shape,
            "static_runtime_mode": self.static_runtime_mode,
            "manifest_hash": self.manifest_hash,
            "runtime_certification_status": self.runtime_certification_status,
            "evidence_kind": self.evidence_kind,
            "passed_trace_observed": self.passed_trace_observed,
            "passed_formal_exception_observed": self.passed_formal_exception_observed,
            "missing_contracts": list(self.missing_contracts),
            "forbidden_violations": list(self.forbidden_violations),
            "attribute_hardening_required": list(self.attribute_hardening_required),
            "unknown_needs_runtime_run": list(self.unknown_needs_runtime_run),
            "gap_count": self.gap_count,
            "highest_gap_severity": self.highest_gap_severity,
            "recommendations": list(self.recommendations),
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# PhaseCCloseoutReport
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PhaseCCloseoutReport:
    """Top-level Phase C closeout report."""

    generated_at: str
    app_summaries: tuple[AppCloseoutSummary, ...]
    total_apps: int
    not_certified_count: int
    trace_observed_ready_count: int
    formal_exception_observed_ready_count: int
    blocker_count: int
    top_recommendations: tuple[str, ...]
    runtime_certification_status: str
    disclaimer: str

    def __post_init__(self) -> None:
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                f"PhaseCCloseoutReport.runtime_certification_status must be "
                f"{NOT_CERTIFIED!r}; got {self.runtime_certification_status!r}. "
                "Phase C closeout never writes a certification verdict."
            )
        if self.total_apps != len(self.app_summaries):
            raise ValueError(
                f"total_apps ({self.total_apps}) must equal len(app_summaries) "
                f"({len(self.app_summaries)})."
            )
        if self.not_certified_count != self.total_apps:
            raise ValueError(
                f"not_certified_count ({self.not_certified_count}) must equal "
                f"total_apps ({self.total_apps}) — every app is NOT_CERTIFIED "
                "during Phase C."
            )
        if self.blocker_count < 0 or self.blocker_count > self.total_apps:
            raise ValueError(
                f"blocker_count ({self.blocker_count}) out of range "
                f"[0, {self.total_apps}]"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "disclaimer": self.disclaimer,
            "runtime_certification_status": self.runtime_certification_status,
            "total_apps": self.total_apps,
            "not_certified_count": self.not_certified_count,
            "trace_observed_ready_count": self.trace_observed_ready_count,
            "formal_exception_observed_ready_count":
                self.formal_exception_observed_ready_count,
            "blocker_count": self.blocker_count,
            "top_recommendations": list(self.top_recommendations),
            "app_summaries": [s.to_dict() for s in self.app_summaries],
        }


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------


def build_phase_c_closeout_report(
    app_contracts: Iterable[AppRouteContract],
    rows_by_app: Mapping[str, Iterable[NormalizedTraceRow]],
    *,
    generated_at: str | None = None,
    cc_shared_env: Mapping[str, str] | None = None,
) -> PhaseCCloseoutReport:
    """Build a non-promoting Phase C closeout report.

    Parameters
    ----------
    app_contracts:
        The apps being reported on. One ``AppCloseoutSummary`` is produced
        per contract.
    rows_by_app:
        Per-app iterable of ``NormalizedTraceRow`` rows. Lookup key is
        ``contract.app_name``. If an app is absent from the map, it is
        treated as having zero rows (honest missing-contracts summary).
    generated_at:
        Optional ISO-8601 UTC timestamp. Defaults to "now" in UTC.
    cc_shared_env:
        Forwarded to ``extract_formal_exception_evidence`` for apps_shared
        CC-SHARED-05 deterministic testing.

    Returns
    -------
    PhaseCCloseoutReport
        ``runtime_certification_status`` always ``NOT_CERTIFIED``.
    """
    ts = generated_at or _utc_now_iso()
    summaries: list[AppCloseoutSummary] = []

    for contract in app_contracts:
        rows = tuple(rows_by_app.get(contract.app_name, ()))
        summaries.append(
            _summarize_app(contract, rows, cc_shared_env=cc_shared_env)
        )

    # Deterministic app-name sort.
    summaries.sort(key=lambda s: s.app_name)
    summaries_tuple = tuple(summaries)

    total_apps = len(summaries_tuple)

    trace_observed_ready = sum(
        1
        for s in summaries_tuple
        if s.evidence_kind in (EVIDENCE_KIND_R3, EVIDENCE_KIND_BTC)
        and s.passed_trace_observed
    )
    formal_ready = sum(
        1
        for s in summaries_tuple
        if s.evidence_kind == EVIDENCE_KIND_FORMAL_EXCEPTION
        and s.passed_formal_exception_observed
    )
    blocker_count = sum(1 for s in summaries_tuple if s.has_blocker)

    top_recs = _collect_top_recommendations(summaries_tuple)

    return PhaseCCloseoutReport(
        generated_at=ts,
        app_summaries=summaries_tuple,
        total_apps=total_apps,
        not_certified_count=total_apps,
        trace_observed_ready_count=trace_observed_ready,
        formal_exception_observed_ready_count=formal_ready,
        blocker_count=blocker_count,
        top_recommendations=top_recs,
        runtime_certification_status=NOT_CERTIFIED,
        disclaimer=REPORT_DISCLAIMER,
    )


# ---------------------------------------------------------------------------
# Per-app summarizer
# ---------------------------------------------------------------------------


def _summarize_app(
    contract: AppRouteContract,
    rows: tuple[NormalizedTraceRow, ...],
    *,
    cc_shared_env: Mapping[str, str] | None,
) -> AppCloseoutSummary:
    """Dispatch on route_shape and build one summary."""
    route = contract.route_shape

    if route == RouteShape.R3_grounded_read:
        return _summarize_r3(contract, rows)
    if route == RouteShape.build_time_compiler:
        return _summarize_btc(contract, rows)
    if route in (RouteShape.evaluator_only, RouteShape.core_adjacent_utility):
        return _summarize_formal_exception(contract, rows, cc_shared_env=cc_shared_env)

    # Defensive — route enum exhaustiveness. Should not reach here because
    # AppRouteContract.__post_init__ restricts to the above routes.
    return _skipped_summary(
        contract,
        reason=f"Unsupported route_shape {route!r}; no extractor dispatch.",
    )


def _summarize_r3(
    contract: AppRouteContract,
    rows: tuple[NormalizedTraceRow, ...],
) -> AppCloseoutSummary:
    evidence = extract_r3_evidence(rows, contract)
    gap_report = build_attribute_hardening_gap_report(
        rows, contract, observed_contracts=evidence.observed_contracts,
    )

    forbidden_names = _forbidden_contract_names(evidence.forbidden_violations)
    notes_parts: list[str] = []
    if evidence.notes:
        notes_parts.append(f"evidence: {evidence.notes}")
    if gap_report.notes:
        notes_parts.append(f"gap_report: {gap_report.notes}")

    recs = _dedupe_recommendations(gap_report.recommendations)

    return AppCloseoutSummary(
        app_name=contract.app_name,
        route_shape=contract.route_shape.value,
        static_runtime_mode=contract.static_runtime_mode,
        manifest_hash=evidence.manifest_hash,
        runtime_certification_status=NOT_CERTIFIED,
        evidence_kind=EVIDENCE_KIND_R3,
        passed_trace_observed=evidence.passed_trace_observed,
        passed_formal_exception_observed=False,
        missing_contracts=evidence.missing_contracts,
        forbidden_violations=forbidden_names,
        attribute_hardening_required=evidence.attribute_hardening_required,
        unknown_needs_runtime_run=evidence.unknown_needs_runtime_run,
        gap_count=gap_report.gap_count,
        highest_gap_severity=gap_report.highest_severity,
        recommendations=recs,
        notes="  ".join(notes_parts),
    )


def _summarize_btc(
    contract: AppRouteContract,
    rows: tuple[NormalizedTraceRow, ...],
) -> AppCloseoutSummary:
    evidence = extract_btc_evidence(rows, contract)
    gap_report = build_attribute_hardening_gap_report(
        rows, contract, observed_contracts=evidence.observed_contracts,
    )

    forbidden_names = _forbidden_contract_names(evidence.forbidden_violations)
    notes_parts: list[str] = []
    if evidence.notes:
        notes_parts.append(f"evidence: {evidence.notes}")
    if gap_report.notes:
        notes_parts.append(f"gap_report: {gap_report.notes}")

    recs = _dedupe_recommendations(gap_report.recommendations)

    return AppCloseoutSummary(
        app_name=contract.app_name,
        route_shape=contract.route_shape.value,
        static_runtime_mode=contract.static_runtime_mode,
        manifest_hash=evidence.manifest_hash,
        runtime_certification_status=NOT_CERTIFIED,
        evidence_kind=EVIDENCE_KIND_BTC,
        passed_trace_observed=evidence.passed_trace_observed,
        passed_formal_exception_observed=False,
        missing_contracts=evidence.missing_contracts,
        forbidden_violations=forbidden_names,
        attribute_hardening_required=evidence.attribute_hardening_required,
        unknown_needs_runtime_run=evidence.unknown_needs_runtime_run,
        gap_count=gap_report.gap_count,
        highest_gap_severity=gap_report.highest_severity,
        recommendations=recs,
        notes="  ".join(notes_parts),
    )


def _summarize_formal_exception(
    contract: AppRouteContract,
    rows: tuple[NormalizedTraceRow, ...],
    *,
    cc_shared_env: Mapping[str, str] | None,
) -> AppCloseoutSummary:
    evidence = extract_formal_exception_evidence(
        rows, contract, cc_shared_env=cc_shared_env,
    )

    # Formal-exception apps do NOT carry required R3/BTC contracts; running
    # the gap report would produce a noise-only output. Skip it and note
    # why, per task spec §4.
    notes_parts: list[str] = [
        "attribute-hardening gap report not run: route_shape is a formal "
        "exception class with no required R3/BTC contracts."
    ]
    if evidence.notes:
        notes_parts.append(f"evidence: {evidence.notes}")
    if evidence.failed_controls:
        notes_parts.append(
            f"failed_controls: {sorted(evidence.failed_controls)}"
        )
    if evidence.missing_controls:
        notes_parts.append(
            f"missing_controls: {sorted(evidence.missing_controls)}"
        )

    # Recommendations: lift failure_reasons as actionable items.
    recs = _dedupe_recommendations(evidence.failure_reasons)

    return AppCloseoutSummary(
        app_name=contract.app_name,
        route_shape=contract.route_shape.value,
        static_runtime_mode=contract.static_runtime_mode,
        manifest_hash=evidence.manifest_hash,
        runtime_certification_status=NOT_CERTIFIED,
        evidence_kind=EVIDENCE_KIND_FORMAL_EXCEPTION,
        passed_trace_observed=False,
        passed_formal_exception_observed=evidence.passed_formal_exception_observed,
        missing_contracts=evidence.missing_controls,
        forbidden_violations=evidence.failed_controls,
        attribute_hardening_required=(),
        unknown_needs_runtime_run=(),
        gap_count=0,
        highest_gap_severity=SEVERITY_INFO,
        recommendations=recs,
        notes="  ".join(notes_parts),
    )


def _skipped_summary(
    contract: AppRouteContract,
    *,
    reason: str,
) -> AppCloseoutSummary:
    return AppCloseoutSummary(
        app_name=contract.app_name,
        route_shape=contract.route_shape.value,
        static_runtime_mode=getattr(contract, "static_runtime_mode", "") or "",
        manifest_hash=contract.manifest_hash,
        runtime_certification_status=NOT_CERTIFIED,
        evidence_kind=EVIDENCE_KIND_SKIPPED,
        passed_trace_observed=False,
        passed_formal_exception_observed=False,
        missing_contracts=(),
        forbidden_violations=(),
        attribute_hardening_required=(),
        unknown_needs_runtime_run=(),
        gap_count=0,
        highest_gap_severity=SEVERITY_INFO,
        recommendations=(),
        notes=reason,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _forbidden_contract_names(
    forbidden_rows: tuple[NormalizedTraceRow, ...],
) -> tuple[str, ...]:
    """Extract unique forbidden contract names in first-seen order."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for r in forbidden_rows:
        name = r.contract_name or (
            r.attributes.get("contract_name") if r.attributes else None
        )
        if not name:
            name = "(unresolved)"
        if name not in seen_set:
            seen_set.add(name)
            seen.append(name)
    return tuple(seen)


def _dedupe_recommendations(recs: Iterable[str]) -> tuple[str, ...]:
    """Deduplicate recommendation strings in first-seen order."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for r in recs:
        if r and r not in seen_set:
            seen_set.add(r)
            seen.append(r)
    return tuple(seen)


def _collect_top_recommendations(
    summaries: tuple[AppCloseoutSummary, ...],
) -> tuple[str, ...]:
    """Collect dedup-ordered recommendations across all summaries.

    Preserves first-seen order (app_name sorted, then rec order within each
    summary). Caps at a reasonable number so the report stays readable.
    """
    CAP = 25
    seen: list[str] = []
    seen_set: set[str] = set()
    for s in summaries:
        for r in s.recommendations:
            if r and r not in seen_set:
                seen_set.add(r)
                seen.append(r)
                if len(seen) >= CAP:
                    return tuple(seen)
    return tuple(seen)


def _utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------


def write_phase_c_closeout_markdown(
    report: PhaseCCloseoutReport,
    output_path: str | Path,
) -> Path:
    """Write the closeout report as a Markdown file.

    The file ALWAYS contains an explicit disclaimer that no runtime
    certification was performed, a summary block, a per-app table with
    every row carrying ``NOT_CERTIFIED``, a blocker section, the top
    recommendations, and a next-phase note pointing to Phase D planning.

    Parameters
    ----------
    report:
        A ``PhaseCCloseoutReport`` from
        :func:`build_phase_c_closeout_report`.
    output_path:
        Target path for the Markdown file. Parent directories are created.

    Returns
    -------
    Path
        The absolute path of the written file.
    """
    if report.runtime_certification_status != NOT_CERTIFIED:
        raise ValueError(
            "write_phase_c_closeout_markdown: refusing to write report "
            f"with runtime_certification_status="
            f"{report.runtime_certification_status!r}."
        )

    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render_markdown(report), encoding="utf-8")
    return out


def _render_markdown(report: PhaseCCloseoutReport) -> str:
    lines: list[str] = []
    lines.append("# Phase C Closeout — Runtime-Certification Readiness")
    lines.append("")
    lines.append(f"_Generated at {report.generated_at} (UTC)._")
    lines.append("")
    lines.append(f"> **Disclaimer:** {report.disclaimer}")
    lines.append("")
    lines.append(
        f"> **runtime_certification_status:** `{report.runtime_certification_status}` "
        "for every app in this report."
    )
    lines.append("")

    # ---- Summary section -----------------------------------------------
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Total apps | {report.total_apps} |")
    lines.append(f"| NOT_CERTIFIED | {report.not_certified_count} |")
    lines.append(
        f"| Trace-observed-ready (R3/BTC) | {report.trace_observed_ready_count} |"
    )
    lines.append(
        f"| Formal-exception-observed-ready | "
        f"{report.formal_exception_observed_ready_count} |"
    )
    lines.append(f"| Apps with any blocker | {report.blocker_count} |")
    lines.append("")

    # ---- Per-app table --------------------------------------------------
    lines.append("## Per-app Summary")
    lines.append("")
    lines.append(
        "| App | Route shape | Evidence | Status | Trace-obs | Formal-obs | "
        "Missing | Forbidden | Hardening | Unknown | Gaps | Highest |"
    )
    lines.append("|---|---|---|---|:---:|:---:|---:|---:|---:|---:|---:|---|")
    for s in report.app_summaries:
        lines.append(
            "| `{app}` | {route} | {kind} | `{status}` | {ptrace} | "
            "{pformal} | {miss} | {forb} | {hard} | {unk} | {gaps} | {sev} |".format(
                app=s.app_name,
                route=s.route_shape,
                kind=s.evidence_kind,
                status=s.runtime_certification_status,
                ptrace="✅" if s.passed_trace_observed else "·",
                pformal="✅" if s.passed_formal_exception_observed else "·",
                miss=len(s.missing_contracts),
                forb=len(s.forbidden_violations),
                hard=len(s.attribute_hardening_required),
                unk=len(s.unknown_needs_runtime_run),
                gaps=s.gap_count,
                sev=s.highest_gap_severity,
            )
        )
    lines.append("")

    # ---- Blockers -------------------------------------------------------
    blockers = [s for s in report.app_summaries if s.has_blocker]
    lines.append("## Blockers")
    lines.append("")
    if not blockers:
        lines.append("_No apps currently block Phase D readiness._")
    else:
        lines.append(
            f"{len(blockers)} app(s) currently block Phase D readiness:"
        )
        lines.append("")
        for s in blockers:
            lines.append(f"### `{s.app_name}` ({s.route_shape} · {s.evidence_kind})")
            lines.append("")
            lines.append(f"- `runtime_certification_status`: `{s.runtime_certification_status}`")
            if s.missing_contracts:
                lines.append(
                    f"- **Missing contracts ({len(s.missing_contracts)})**: "
                    + ", ".join(f"`{c}`" for c in s.missing_contracts)
                )
            if s.forbidden_violations:
                lines.append(
                    f"- **Forbidden violations / failed controls "
                    f"({len(s.forbidden_violations)})**: "
                    + ", ".join(f"`{c}`" for c in s.forbidden_violations)
                )
            if s.attribute_hardening_required:
                lines.append(
                    f"- **Attribute hardening required "
                    f"({len(s.attribute_hardening_required)})**: "
                    + ", ".join(
                        f"`{c}`" for c in s.attribute_hardening_required
                    )
                )
            if s.unknown_needs_runtime_run:
                lines.append(
                    f"- **Unknown — needs runtime run "
                    f"({len(s.unknown_needs_runtime_run)})**: "
                    + ", ".join(
                        f"`{c}`" for c in s.unknown_needs_runtime_run
                    )
                )
            if s.gap_count:
                lines.append(
                    f"- Gap report: `{s.gap_count}` gap(s); highest severity "
                    f"`{s.highest_gap_severity}`"
                )
            if s.notes:
                lines.append(f"- Notes: {s.notes}")
            lines.append("")

    # ---- Top recommendations -------------------------------------------
    lines.append("## Top Recommendations")
    lines.append("")
    if not report.top_recommendations:
        lines.append("_No recommendations emitted — no gaps or failure reasons._")
    else:
        for i, rec in enumerate(report.top_recommendations, start=1):
            lines.append(f"{i}. {rec}")
    lines.append("")

    # ---- Next phase note ------------------------------------------------
    lines.append("## Next Phase")
    lines.append("")
    lines.append(
        "Phase D planning is required before any certification decision "
        "logic is implemented. This closeout report is the input contract "
        "for that planning — it documents readiness and blockers, but it "
        "does **not** certify any app and does **not** promote any "
        "`runtime_certification_status` value. Every row above carries "
        "`NOT_CERTIFIED` by design."
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Optional filesystem helper (best-effort; not required by core builder)
# ---------------------------------------------------------------------------


def load_contracts_from_manifests(repo_root: Path) -> tuple[AppRouteContract, ...]:
    """Best-effort loader for every ``apps_*/spine_manifest.yaml`` in a repo.

    Reads each manifest's ``route_shape`` claim and synthesizes an
    ``AppRouteContract`` via the appropriate factory
    (``build_r3_grounded_read_contract``, etc.). Apps whose manifest
    cannot be parsed or which claim an unsupported route shape are
    skipped silently and logged — the goal is a best-effort aggregation,
    not a strict validation pass.

    This helper is intentionally minimal — it does NOT compute manifest
    hashes, NOT validate binding coverage, and does NOT certify anything.
    Its output is suitable as input to
    :func:`build_phase_c_closeout_report` for exploratory runs. For
    production reports, operators should construct ``AppRouteContract``
    objects explicitly.

    Parameters
    ----------
    repo_root:
        Repository root containing ``apps_*`` directories with
        ``spine_manifest.yaml`` files.
    """
    # Deliberately lazy import: keep the core builder free of any
    # YAML / filesystem dependency at import time.
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        logger.info(
            "load_contracts_from_manifests: PyYAML not installed; returning empty."
        )
        return ()

    from agentic_core.L6_system_learning.app_route_contracts import (
        build_build_time_compiler_contract,
        build_formal_exception_contract,
        build_r3_grounded_read_contract,
    )
    from agentic_core.L6_system_learning.manifest_hash import (
        compute_manifest_hash_for_app,
    )

    root = Path(repo_root)
    contracts: list[AppRouteContract] = []

    for app_dir in sorted(root.glob("apps_*")):
        if not app_dir.is_dir():
            continue
        manifest = app_dir / "spine_manifest.yaml"
        if not manifest.exists():
            continue
        try:
            raw = yaml.safe_load(manifest.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            logger.info("Skipping %s: YAML parse error: %s", manifest, exc)
            continue

        app_name = app_dir.name
        route_str = str(raw.get("route_shape") or raw.get("route") or "").strip()
        try:
            manifest_hash = compute_manifest_hash_for_app(app_name, repo_root=root)
        except FileNotFoundError:
            manifest_hash = ""

        manifest_path_rel = f"{app_name}/spine_manifest.yaml"

        if route_str == RouteShape.R3_grounded_read.value:
            contracts.append(
                build_r3_grounded_read_contract(
                    app_name=app_name,
                    manifest_path=manifest_path_rel,
                    manifest_hash=manifest_hash,
                )
            )
        elif route_str == RouteShape.build_time_compiler.value:
            contracts.append(
                build_build_time_compiler_contract(
                    app_name=app_name,
                    manifest_path=manifest_path_rel,
                    manifest_hash=manifest_hash,
                )
            )
        elif route_str in (
            RouteShape.evaluator_only.value,
            RouteShape.core_adjacent_utility.value,
        ):
            # Extract compensating_controls + reason_code from manifest;
            # skip if absent.
            ccs = tuple(raw.get("compensating_controls") or ())
            reason = str(raw.get("formal_exception_reason_code") or "").strip()
            if not ccs or not reason:
                logger.info(
                    "Skipping %s: formal-exception manifest missing "
                    "compensating_controls or formal_exception_reason_code.",
                    app_name,
                )
                continue
            contracts.append(
                build_formal_exception_contract(
                    app_name=app_name,
                    route_shape=RouteShape(route_str),
                    manifest_path=manifest_path_rel,
                    manifest_hash=manifest_hash,
                    reason_code=reason,
                    compensating_controls=tuple(ccs),
                )
            )
        else:
            logger.info(
                "Skipping %s: unsupported / unspecified route_shape %r.",
                app_name,
                route_str,
            )
            continue

    return tuple(contracts)


# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------

__all__ = [
    # Dataclasses
    "AppCloseoutSummary",
    "PhaseCCloseoutReport",
    # Entry points
    "build_phase_c_closeout_report",
    "write_phase_c_closeout_markdown",
    "load_contracts_from_manifests",
    # Constants
    "EVIDENCE_KIND_BTC",
    "EVIDENCE_KIND_FORMAL_EXCEPTION",
    "EVIDENCE_KIND_R3",
    "EVIDENCE_KIND_SKIPPED",
    "REPORT_DISCLAIMER",
]
