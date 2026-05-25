"""Attribute-hardening gap report — Phase C.7.

Consumes ``NormalizedTraceRow`` rows and an ``AppRouteContract`` and emits a
structured backlog of runtime-certification evidence gaps. The report is
informational / operational only — it **does not certify any app** and
**does not promote ``runtime_certification_status``**. Its purpose is to
tell operators precisely which gaps block Phase D certification, so the
hardening work can be prioritized deterministically.

Design references
-----------------
- Phase C plan: ``docs/plans/runtime_cert_phase_c_trace_collector_plan.md``
- C.2 normalizer: ``tools/runtime_cert/trace_row_normalizer.py``
- C.3 R3 extractor: ``tools/runtime_cert/extractors/r3_evidence.py``
- C.4 BTC extractor: ``tools/runtime_cert/extractors/btc_evidence.py``
- C.6 smoke harness: ``tools/runtime_cert/smoke/live_trace_smoke.py``

What this module does
---------------------
- Groups rows by canonicalized contract name (honors
  ``CompiledPromptArtifact`` ↔ ``PromptEnvelope`` equivalence).
- Classifies per-row gaps by ``phase_c_status`` into the canonical gap
  types (see :data:`GAP_TYPES`) and assigns a deterministic severity
  (see :data:`SEVERITY_ORDER`).
- Compares observed contracts against ``contract.required_contracts`` to
  emit one ``MISSING_CONTRACT`` CRITICAL gap per absent required contract.
- Filters rows to ``contract.app_name`` — other-app rows are counted in
  ``notes`` but do not contribute gaps (matches C.3/C.4/C.6 behavior).
- Preserves ``CommitRequest`` rows as CRITICAL ``FORBIDDEN_SPAN_VIOLATION``
  gaps.
- Produces deterministic recommendation text per gap type.

What this module does NOT do
----------------------------
- Does NOT certify any app. ``runtime_certification_status`` is always
  ``NOT_CERTIFIED``; the report's ``__post_init__`` raises ``ValueError``
  on any other value.
- Does NOT modify any emitter, scanner, or CI gate.
- Does NOT change app behavior or rename spans.
"""

from __future__ import annotations

# ADR-079 consumer mode declaration (required for all runtime-cert tools).
__adg_consumer_mode__ = "runtime_cert_read"

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Final, Iterable, Mapping

from agentic_core.L6_system_learning.app_route_contracts import AppRouteContract
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED
from tools.runtime_cert.trace_row_normalizer import (
    ATTRIBUTE_HARDENING_REQUIRED,
    EXISTS_NAME_MISMATCH,
    FORBIDDEN_SPAN_VIOLATION,
    LEDGER_EVENT_ONLY,
    NormalizedTraceRow,
    STUB_ONLY,
    TELEMETRY_MARKER_ONLY,
    TRACE_GAP,
    UNKNOWN_NEEDS_RUNTIME_RUN,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Gap types
# ---------------------------------------------------------------------------

#: Required contract has zero observed rows for this app.
GAP_MISSING_CONTRACT: Final[str] = "MISSING_CONTRACT"

#: A row matched a binding but is missing required attributes.
GAP_MISSING_REQUIRED_ATTRIBUTE: Final[str] = "MISSING_REQUIRED_ATTRIBUTE"

#: A row was resolved to a binding but the binding's phase_a_status is
#: UNKNOWN_NEEDS_RUNTIME_RUN (e.g. FinalEvidenceContract).
GAP_UNKNOWN_NEEDS_RUNTIME_RUN: Final[str] = UNKNOWN_NEEDS_RUNTIME_RUN

#: A CommitRequest / other forbidden-contract span on a route where it is
#: explicitly banned (e.g. R3 apps).
GAP_FORBIDDEN_SPAN_VIOLATION: Final[str] = FORBIDDEN_SPAN_VIOLATION

#: A row was expected but no trace observation exists.
GAP_TRACE_GAP: Final[str] = TRACE_GAP

#: The span name disagrees with the canonical accepted-pattern list.
GAP_NAME_MISMATCH: Final[str] = "NAME_MISMATCH"

#: Only a telemetry marker exists for a required contract.
GAP_TELEMETRY_MARKER_ONLY: Final[str] = TELEMETRY_MARKER_ONLY

#: Only a ledger event exists for a required contract.
GAP_LEDGER_EVENT_ONLY: Final[str] = LEDGER_EVENT_ONLY

#: Only a stub implementation exists for a required contract.
GAP_STUB_ONLY: Final[str] = STUB_ONLY

#: Complete list of gap types emitted by this extractor.
GAP_TYPES: Final[tuple[str, ...]] = (
    GAP_MISSING_CONTRACT,
    GAP_MISSING_REQUIRED_ATTRIBUTE,
    GAP_UNKNOWN_NEEDS_RUNTIME_RUN,
    GAP_FORBIDDEN_SPAN_VIOLATION,
    GAP_TRACE_GAP,
    GAP_NAME_MISMATCH,
    GAP_TELEMETRY_MARKER_ONLY,
    GAP_LEDGER_EVENT_ONLY,
    GAP_STUB_ONLY,
)


# ---------------------------------------------------------------------------
# Severity
# ---------------------------------------------------------------------------

SEVERITY_CRITICAL: Final[str] = "CRITICAL"
SEVERITY_HIGH: Final[str] = "HIGH"
SEVERITY_MEDIUM: Final[str] = "MEDIUM"
SEVERITY_LOW: Final[str] = "LOW"
SEVERITY_INFO: Final[str] = "INFO"

#: Ordered from lowest (INFO) to highest (CRITICAL); used for
#: ``highest_severity`` computation.
SEVERITY_ORDER: Final[tuple[str, ...]] = (
    SEVERITY_INFO,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    SEVERITY_HIGH,
    SEVERITY_CRITICAL,
)

_SEVERITY_RANK: Final[Mapping[str, int]] = {
    s: i for i, s in enumerate(SEVERITY_ORDER)
}

#: Default severity for each gap type (deterministic per task spec §6).
GAP_TYPE_SEVERITY: Final[Mapping[str, str]] = {
    GAP_MISSING_CONTRACT: SEVERITY_CRITICAL,
    GAP_FORBIDDEN_SPAN_VIOLATION: SEVERITY_CRITICAL,
    GAP_UNKNOWN_NEEDS_RUNTIME_RUN: SEVERITY_HIGH,
    GAP_MISSING_REQUIRED_ATTRIBUTE: SEVERITY_HIGH,
    GAP_TRACE_GAP: SEVERITY_HIGH,
    GAP_TELEMETRY_MARKER_ONLY: SEVERITY_MEDIUM,
    GAP_LEDGER_EVENT_ONLY: SEVERITY_MEDIUM,
    GAP_STUB_ONLY: SEVERITY_MEDIUM,
    GAP_NAME_MISMATCH: SEVERITY_LOW,
}


# ---------------------------------------------------------------------------
# PromptEnvelope equivalence (mirrors C.3)
# ---------------------------------------------------------------------------

_PROMPT_ENVELOPE_EQUIVALENCE: Final[frozenset[str]] = frozenset(
    {"CompiledPromptArtifact", "PromptEnvelope"}
)
_PROMPT_ENVELOPE_CANONICAL: Final[str] = "CompiledPromptArtifact"


def _canonicalize_contract_name(name: str | None) -> str | None:
    """Collapse PromptEnvelope onto CompiledPromptArtifact."""
    if not name:
        return None
    if name in _PROMPT_ENVELOPE_EQUIVALENCE:
        return _PROMPT_ENVELOPE_CANONICAL
    return name


# ---------------------------------------------------------------------------
# Recommendations (deterministic text per gap type)
# ---------------------------------------------------------------------------


def _recommendation(
    gap_type: str,
    contract_name: str,
    missing_attrs: tuple[str, ...] = (),
) -> str:
    """Return deterministic recommendation text for the given gap type."""
    if gap_type == GAP_MISSING_CONTRACT:
        return (
            f"Add or bind runtime evidence for {contract_name!r}; "
            "do not certify until observed."
        )
    if gap_type == GAP_MISSING_REQUIRED_ATTRIBUTE:
        attrs_str = ", ".join(missing_attrs) if missing_attrs else "<unspecified>"
        return (
            f"Add required attributes [{attrs_str}] to existing emitter or "
            f"binding for {contract_name!r}."
        )
    if gap_type == GAP_UNKNOWN_NEEDS_RUNTIME_RUN:
        return (
            f"Run live trace or add binding evidence for {contract_name!r}."
        )
    if gap_type == GAP_FORBIDDEN_SPAN_VIOLATION:
        return (
            f"Remove forbidden span {contract_name!r} or change manifest "
            "route shape through Author-Gate."
        )
    if gap_type in {
        GAP_TELEMETRY_MARKER_ONLY,
        GAP_LEDGER_EVENT_ONLY,
        GAP_STUB_ONLY,
    }:
        return (
            f"Replace marker/stub evidence with real OTel/runtime ADG span "
            f"for {contract_name!r} before certification."
        )
    if gap_type == GAP_NAME_MISMATCH:
        return (
            f"Align span-name with the canonical accepted pattern for "
            f"{contract_name!r}."
        )
    if gap_type == GAP_TRACE_GAP:
        return (
            f"Investigate missing trace row for {contract_name!r}; re-run "
            "live capture."
        )
    return f"Resolve {gap_type} for {contract_name!r}."


# ---------------------------------------------------------------------------
# Missing-attrs note parser (mirrors C.3 ``_parse_missing_attrs``)
# ---------------------------------------------------------------------------


def _parse_missing_attrs(mapping_notes: str) -> tuple[str, ...]:
    """Extract attribute names from a 'Missing required attributes: [x, y].' note."""
    if not mapping_notes:
        return ()
    marker = "Missing required attributes:"
    idx = mapping_notes.find(marker)
    if idx == -1:
        return ()
    tail = mapping_notes[idx + len(marker):].strip().rstrip(".")
    tail = tail.strip("[]")
    parts = [p.strip().strip("'\"") for p in tail.split(",")]
    return tuple(p for p in parts if p)


# ---------------------------------------------------------------------------
# AttributeGap
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AttributeGap:
    """One actionable evidence gap entry."""

    app_name: str
    route_shape: str
    contract_name: str
    normalized_cert_alias: str | None
    gap_type: str
    severity: str
    row_count: int
    missing_attributes: tuple[str, ...]
    observed_statuses: tuple[str, ...]
    sample_span_names: tuple[str, ...]
    sample_source_paths: tuple[str, ...]
    recommendation: str
    notes: str

    def __post_init__(self) -> None:
        if self.gap_type not in GAP_TYPES:
            raise ValueError(
                f"AttributeGap.gap_type must be one of {list(GAP_TYPES)}; "
                f"got {self.gap_type!r}"
            )
        if self.severity not in _SEVERITY_RANK:
            raise ValueError(
                f"AttributeGap.severity must be one of {list(SEVERITY_ORDER)}; "
                f"got {self.severity!r}"
            )
        if self.row_count < 0:
            raise ValueError(
                f"AttributeGap.row_count must be >= 0; got {self.row_count!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "route_shape": self.route_shape,
            "contract_name": self.contract_name,
            "normalized_cert_alias": self.normalized_cert_alias,
            "gap_type": self.gap_type,
            "severity": self.severity,
            "row_count": self.row_count,
            "missing_attributes": list(self.missing_attributes),
            "observed_statuses": list(self.observed_statuses),
            "sample_span_names": list(self.sample_span_names),
            "sample_source_paths": list(self.sample_source_paths),
            "recommendation": self.recommendation,
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# AttributeHardeningGapReport
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AttributeHardeningGapReport:
    """Structured gap backlog for one app (Phase C.7).

    ``runtime_certification_status`` is always ``NOT_CERTIFIED`` —
    ``__post_init__`` rejects any other value. ``gaps`` is the canonical
    ranked backlog; convenience fields (``blocked_contracts``,
    ``attribute_hardening_required``, etc.) project the same gap set into
    operator-friendly groupings.
    """

    app_name: str
    route_shape: str
    manifest_hash: str
    static_runtime_mode: str
    runtime_certification_status: str

    gap_count: int
    gaps: tuple[AttributeGap, ...]

    highest_severity: str
    blocked_contracts: tuple[str, ...]
    attribute_hardening_required: tuple[str, ...]
    unknown_needs_runtime_run: tuple[str, ...]
    forbidden_violations: tuple[str, ...]
    missing_contracts: tuple[str, ...]
    recommendations: tuple[str, ...]
    notes: str

    def __post_init__(self) -> None:
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                f"AttributeHardeningGapReport.runtime_certification_status "
                f"must be {NOT_CERTIFIED!r}; got "
                f"{self.runtime_certification_status!r}. Phase C.7 never "
                "writes a certification verdict."
            )
        if self.gap_count != len(self.gaps):
            raise ValueError(
                f"AttributeHardeningGapReport.gap_count ({self.gap_count}) "
                f"must equal len(gaps) ({len(self.gaps)})."
            )
        if self.highest_severity not in _SEVERITY_RANK:
            raise ValueError(
                f"AttributeHardeningGapReport.highest_severity must be one of "
                f"{list(SEVERITY_ORDER)}; got {self.highest_severity!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "route_shape": self.route_shape,
            "manifest_hash": self.manifest_hash,
            "static_runtime_mode": self.static_runtime_mode,
            "runtime_certification_status": self.runtime_certification_status,
            "gap_count": self.gap_count,
            "gaps": [g.to_dict() for g in self.gaps],
            "highest_severity": self.highest_severity,
            "blocked_contracts": list(self.blocked_contracts),
            "attribute_hardening_required": list(self.attribute_hardening_required),
            "unknown_needs_runtime_run": list(self.unknown_needs_runtime_run),
            "forbidden_violations": list(self.forbidden_violations),
            "missing_contracts": list(self.missing_contracts),
            "recommendations": list(self.recommendations),
            "notes": self.notes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Row → gap-type mapping
# ---------------------------------------------------------------------------


_ROW_STATUS_TO_GAP_TYPE: Final[Mapping[str, str]] = {
    FORBIDDEN_SPAN_VIOLATION: GAP_FORBIDDEN_SPAN_VIOLATION,
    ATTRIBUTE_HARDENING_REQUIRED: GAP_MISSING_REQUIRED_ATTRIBUTE,
    UNKNOWN_NEEDS_RUNTIME_RUN: GAP_UNKNOWN_NEEDS_RUNTIME_RUN,
    TELEMETRY_MARKER_ONLY: GAP_TELEMETRY_MARKER_ONLY,
    LEDGER_EVENT_ONLY: GAP_LEDGER_EVENT_ONLY,
    STUB_ONLY: GAP_STUB_ONLY,
    EXISTS_NAME_MISMATCH: GAP_NAME_MISMATCH,
    TRACE_GAP: GAP_TRACE_GAP,
}


# ---------------------------------------------------------------------------
# Public extractor
# ---------------------------------------------------------------------------


def build_attribute_hardening_gap_report(
    rows: Iterable[NormalizedTraceRow],
    contract: AppRouteContract,
    *,
    observed_contracts: Iterable[str] | None = None,
) -> AttributeHardeningGapReport:
    """Build a non-promoting attribute-hardening gap report.

    Parameters
    ----------
    rows:
        ``NormalizedTraceRow`` rows from Phase C.2. Rows for other apps
        are counted in ``notes`` but do not contribute gaps.
    contract:
        ``AppRouteContract`` identifying the app being analyzed. Used for
        ``app_name``, ``route_shape``, ``manifest_hash``, and
        ``required_contracts``.
    observed_contracts:
        Optional explicit set of contracts known to be observed (e.g. the
        ``observed_contracts`` field from ``extract_r3_evidence`` or
        ``extract_btc_evidence``). When ``None``, the set is derived from
        rows with a non-empty ``contract_name``.

    Returns
    -------
    AttributeHardeningGapReport
        ``runtime_certification_status`` is always ``NOT_CERTIFIED``.
    """
    rows_list = list(rows)
    app = contract.app_name
    route = contract.route_shape.value

    # ---- Partition by app ------------------------------------------------
    own_rows = [r for r in rows_list if r.app_name == app]
    foreign_rows = [r for r in rows_list if r.app_name != app]

    # ---- Derive observed contracts (canonicalized) ----------------------
    if observed_contracts is not None:
        observed_set = {
            _canonicalize_contract_name(c)
            for c in observed_contracts
            if c
        }
        observed_set.discard(None)
    else:
        observed_set = set()
        for r in own_rows:
            canon = _canonicalize_contract_name(
                r.contract_name or r.attributes.get("contract_name") if r.attributes else r.contract_name
            )
            if canon:
                observed_set.add(canon)

    # ---- Build per-row gaps ---------------------------------------------
    gaps_by_key: dict[tuple[str, str], _GapAccumulator] = {}

    for r in own_rows:
        gap_type = _ROW_STATUS_TO_GAP_TYPE.get(r.phase_c_status)
        if gap_type is None:
            # Clean status (EXISTS_MATCHES_MATRIX / EXISTS_NEEDS_ATTRIBUTE_HARDENING /
            # NOT_FOUND); no gap emitted for the row itself.
            continue

        # Canonicalize the contract name for grouping; preserve the actual
        # contract_name for display (so PromptEnvelope-labeled rows show
        # both the canonical group and the raw name in notes).
        raw_contract = r.contract_name or (
            r.attributes.get("contract_name") if r.attributes else None
        )
        canon = _canonicalize_contract_name(raw_contract) or "(unresolved)"

        key = (canon, gap_type)
        acc = gaps_by_key.get(key)
        if acc is None:
            acc = _GapAccumulator(
                contract_name=canon,
                gap_type=gap_type,
                normalized_cert_alias=r.normalized_cert_alias,
            )
            gaps_by_key[key] = acc
        acc.ingest(r)

    # ---- Build missing-contract gaps ------------------------------------
    required = tuple(contract.required_contracts)
    required_canon = [
        _canonicalize_contract_name(c) or c for c in required
    ]
    missing_contract_names: list[str] = []
    for req, req_canon in zip(required, required_canon):
        if req_canon not in observed_set:
            missing_contract_names.append(req)

    # ---- Assemble the ranked gap list -----------------------------------
    assembled_gaps: list[AttributeGap] = []

    # Missing contracts go first (CRITICAL).
    for cname in missing_contract_names:
        assembled_gaps.append(
            AttributeGap(
                app_name=app,
                route_shape=route,
                contract_name=cname,
                normalized_cert_alias=None,
                gap_type=GAP_MISSING_CONTRACT,
                severity=GAP_TYPE_SEVERITY[GAP_MISSING_CONTRACT],
                row_count=0,
                missing_attributes=(),
                observed_statuses=(),
                sample_span_names=(),
                sample_source_paths=(),
                recommendation=_recommendation(GAP_MISSING_CONTRACT, cname),
                notes=(
                    f"Required contract {cname!r} has zero observed rows for "
                    f"app {app!r}; Phase D cannot certify until at least one "
                    "row is observed."
                ),
            )
        )

    # Per-row aggregated gaps follow.
    for acc in gaps_by_key.values():
        assembled_gaps.append(acc.finalize(app=app, route=route))

    # Deterministic sort: severity DESC, then gap_type, then contract_name.
    assembled_gaps.sort(
        key=lambda g: (
            -_SEVERITY_RANK[g.severity],
            g.gap_type,
            g.contract_name,
        )
    )
    gaps_tuple = tuple(assembled_gaps)

    # ---- Derived summary fields -----------------------------------------
    blocked_contracts = tuple(
        sorted(
            {
                g.contract_name
                for g in gaps_tuple
                if g.severity in (SEVERITY_CRITICAL, SEVERITY_HIGH)
            }
        )
    )
    attribute_hardening = tuple(
        sorted(
            {
                g.contract_name
                for g in gaps_tuple
                if g.gap_type == GAP_MISSING_REQUIRED_ATTRIBUTE
            }
        )
    )
    unknown_runtime = tuple(
        sorted(
            {
                g.contract_name
                for g in gaps_tuple
                if g.gap_type == GAP_UNKNOWN_NEEDS_RUNTIME_RUN
            }
        )
    )
    forbidden_list = tuple(
        sorted(
            {
                g.contract_name
                for g in gaps_tuple
                if g.gap_type == GAP_FORBIDDEN_SPAN_VIOLATION
            }
        )
    )
    missing_list = tuple(
        sorted(
            {
                g.contract_name
                for g in gaps_tuple
                if g.gap_type == GAP_MISSING_CONTRACT
            }
        )
    )
    # Deduplicate recommendations in deterministic order.
    recommendations: list[str] = []
    seen_recs: set[str] = set()
    for g in gaps_tuple:
        if g.recommendation not in seen_recs:
            seen_recs.add(g.recommendation)
            recommendations.append(g.recommendation)

    highest = _highest_severity(gaps_tuple)

    notes_parts: list[str] = []
    if foreign_rows:
        other_apps = sorted({r.app_name for r in foreign_rows})
        notes_parts.append(
            f"{len(foreign_rows)} row(s) from other app(s) "
            f"({', '.join(other_apps)}) ignored by app-scope filter."
        )
    if not gaps_tuple:
        notes_parts.append(
            "No gaps detected in rows and observed contracts — still "
            "NOT_CERTIFIED (Phase C.7 never certifies)."
        )

    return AttributeHardeningGapReport(
        app_name=app,
        route_shape=route,
        manifest_hash=contract.manifest_hash,
        static_runtime_mode=getattr(contract, "static_runtime_mode", "")
        or "",
        runtime_certification_status=NOT_CERTIFIED,
        gap_count=len(gaps_tuple),
        gaps=gaps_tuple,
        highest_severity=highest,
        blocked_contracts=blocked_contracts,
        attribute_hardening_required=attribute_hardening,
        unknown_needs_runtime_run=unknown_runtime,
        forbidden_violations=forbidden_list,
        missing_contracts=missing_list,
        recommendations=tuple(recommendations),
        notes="  ".join(notes_parts),
    )


# ---------------------------------------------------------------------------
# Internal aggregation helper
# ---------------------------------------------------------------------------


@dataclass
class _GapAccumulator:
    """Aggregates multiple rows for the same (contract, gap_type) key."""

    contract_name: str
    gap_type: str
    normalized_cert_alias: str | None
    row_count: int = 0
    missing_attrs: set[str] = field(default_factory=set)
    statuses: set[str] = field(default_factory=set)
    span_names: list[str] = field(default_factory=list)
    source_paths: list[str] = field(default_factory=list)
    raw_contract_names: set[str] = field(default_factory=set)

    def ingest(self, row: NormalizedTraceRow) -> None:
        self.row_count += 1
        self.statuses.add(row.phase_c_status)
        if row.span_name and row.span_name not in self.span_names:
            self.span_names.append(row.span_name)
        if row.source_path and row.source_path not in self.source_paths:
            self.source_paths.append(row.source_path)

        raw = row.contract_name or (
            row.attributes.get("contract_name") if row.attributes else None
        )
        if raw:
            self.raw_contract_names.add(raw)

        if self.gap_type == GAP_MISSING_REQUIRED_ATTRIBUTE and row.mapping_notes:
            self.missing_attrs.update(_parse_missing_attrs(row.mapping_notes))

        # Preserve the first non-None alias we see.
        if self.normalized_cert_alias is None:
            self.normalized_cert_alias = row.normalized_cert_alias

    def finalize(self, *, app: str, route: str) -> AttributeGap:
        missing_sorted = tuple(sorted(self.missing_attrs))
        statuses_sorted = tuple(sorted(self.statuses))
        # Cap samples at a reasonable number so reports stay compact.
        sample_cap = 5
        span_samples = tuple(self.span_names[:sample_cap])
        path_samples = tuple(self.source_paths[:sample_cap])

        recommendation = _recommendation(
            self.gap_type, self.contract_name, missing_sorted
        )

        notes_parts: list[str] = []
        extra_raw = self.raw_contract_names - {self.contract_name}
        if extra_raw:
            # PromptEnvelope-labelled rows that collapsed onto
            # CompiledPromptArtifact show up here.
            notes_parts.append(
                f"Equivalent raw contract_name(s): {sorted(extra_raw)}."
            )
        if self.row_count > sample_cap:
            notes_parts.append(
                f"{self.row_count - sample_cap} additional row(s) not shown."
            )

        return AttributeGap(
            app_name=app,
            route_shape=route,
            contract_name=self.contract_name,
            normalized_cert_alias=self.normalized_cert_alias,
            gap_type=self.gap_type,
            severity=GAP_TYPE_SEVERITY[self.gap_type],
            row_count=self.row_count,
            missing_attributes=missing_sorted,
            observed_statuses=statuses_sorted,
            sample_span_names=span_samples,
            sample_source_paths=path_samples,
            recommendation=recommendation,
            notes="  ".join(notes_parts),
        )


def _highest_severity(gaps: tuple[AttributeGap, ...]) -> str:
    if not gaps:
        return SEVERITY_INFO
    return max(gaps, key=lambda g: _SEVERITY_RANK[g.severity]).severity


# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------

__all__ = [
    # Dataclasses
    "AttributeGap",
    "AttributeHardeningGapReport",
    # Entry point
    "build_attribute_hardening_gap_report",
    # Gap type constants
    "GAP_FORBIDDEN_SPAN_VIOLATION",
    "GAP_LEDGER_EVENT_ONLY",
    "GAP_MISSING_CONTRACT",
    "GAP_MISSING_REQUIRED_ATTRIBUTE",
    "GAP_NAME_MISMATCH",
    "GAP_STUB_ONLY",
    "GAP_TELEMETRY_MARKER_ONLY",
    "GAP_TRACE_GAP",
    "GAP_TYPES",
    "GAP_TYPE_SEVERITY",
    "GAP_UNKNOWN_NEEDS_RUNTIME_RUN",
    # Severity constants
    "SEVERITY_CRITICAL",
    "SEVERITY_HIGH",
    "SEVERITY_INFO",
    "SEVERITY_LOW",
    "SEVERITY_MEDIUM",
    "SEVERITY_ORDER",
]
