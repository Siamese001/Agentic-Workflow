"""build_time_compiler per-app evidence extractor — Phase C.4.

Consumes an ordered sequence of ``NormalizedTraceRow`` instances (Phase C.2
output) and an ``AppRouteContract`` for a ``build_time_compiler`` app (today
only ``apps_qna``), then reports whether the BTC 3-contract evidence shape
was **observed**, **missing**, **attribute-hardening-required**, **unknown**,
or **forbidden** (R3-chain leakage).

Design references
-----------------
- Phase C plan: ``docs/plans/runtime_cert_phase_c_trace_collector_plan.md`` v2
- C.1 adapter:  ``tools/runtime_cert/runtime_adg_query_adapter.py``
- C.2 normalizer: ``tools/runtime_cert/trace_row_normalizer.py``
- C.3 extractor: ``tools/runtime_cert/extractors/r3_evidence.py`` (sibling pattern)
- B.2 schema:   ``system_learning/runtime_adg/app_route_contracts.py``
- B.3 hash:     ``system_learning/runtime_adg/manifest_hash.py``
- Matrix v2 §5: ``docs/reference/runtime_certification/contract_span_binding_matrix.md``

What this module does
---------------------
- Accepts ``NormalizedTraceRow`` rows pre-filtered or mixed (rows from other
  apps are counted in ``notes`` but do not contribute to evidence).
- Groups rows by their resolved ``contract_name`` (from C.2).
- Required BTC contracts (§5.1): ``ValidatedRequest``, ``build.pack_artifact``,
  ``ledger.emit``. Sourced from ``AppRouteContract.required_contracts``.
- Forbidden contracts (§5.2): the full R3 chain is forbidden unless also
  present in ``required_contracts`` (carve-out for ``ValidatedRequest``).
  Rows whose canonical contract is forbidden are flagged as
  ``FORBIDDEN_SPAN_VIOLATION`` and **preserved** (not filtered).
- Emits ``passed_trace_observed=True`` iff all required contracts have at
  least one observed row AND no forbidden violations, attribute-hardening
  gaps, or unknown-runtime-run gaps exist.  This flag signals Phase D
  readiness only; it does NOT promote ``runtime_certification_status``.

What this module does NOT do
----------------------------
- Does NOT certify any app.
- Does NOT write to any store.
- Does NOT modify any emitter, scanner, or CI gate.
- Does NOT promote ``runtime_certification_status`` beyond ``NOT_CERTIFIED``.
- Does NOT mutate the ``AppRouteContract`` object.
- Does NOT fail hard if the manifest path is absent at ``STATIC_EVIDENCE``
  level; emits a note instead.
"""

from __future__ import annotations

# ADR-079 consumer mode declaration.
__adg_consumer_mode__ = "runtime_cert_read"

import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from agentic_core.L6_system_learning.app_route_contracts import (
    BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS,
    AppRouteContract,
    RouteShape,
)
from agentic_core.L6_system_learning.manifest_hash import compute_manifest_hash
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED
from tools.runtime_cert.trace_row_normalizer import (
    ATTRIBUTE_HARDENING_REQUIRED,
    FORBIDDEN_SPAN_VIOLATION,
    UNKNOWN_NEEDS_RUNTIME_RUN,
    NormalizedTraceRow,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Default expected app for the build_time_compiler route shape (currently
#: only apps_qna uses this shape — see matrix v2 §5).  The contract may
#: specify a different ``app_name``; this constant is informational only.
_DEFAULT_BTC_APP: Final[str] = "apps_qna"

#: PromptEnvelope is treated as an equivalent of CompiledPromptArtifact for
#: forbidden-contract detection (binding matrix §4.1 Q7).
_PROMPT_ENVELOPE_EQUIVALENCE: Final[frozenset[str]] = frozenset(
    {"CompiledPromptArtifact", "PromptEnvelope"}
)
_PROMPT_ENVELOPE_CANONICAL: Final[str] = "CompiledPromptArtifact"

#: Statuses that indicate a row was matched to a binding but lacks attributes.
_HARDENING_STATUSES: Final[frozenset[str]] = frozenset(
    {ATTRIBUTE_HARDENING_REQUIRED}
)

#: Statuses that indicate evidence is present but requires a live trace.
_UNKNOWN_STATUSES: Final[frozenset[str]] = frozenset(
    {UNKNOWN_NEEDS_RUNTIME_RUN}
)


# ---------------------------------------------------------------------------
# BTCContractEvidence — per-contract evidence record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BTCContractEvidence:
    """Evidence for one BTC contract within one trace batch.

    Attributes
    ----------
    contract_name : str
        Canonical contract name (e.g. ``"build.pack_artifact"``).
    observed : bool
        ``True`` if at least one ``NormalizedTraceRow`` resolved to this
        contract AND its ``phase_c_status`` is not a fail-closed gap status.
    rows : tuple[NormalizedTraceRow, ...]
        All rows that resolved to this contract (all statuses).
    row_count : int
        ``len(rows)``.
    statuses : tuple[str, ...]
        De-duplicated set of ``phase_c_status`` values seen.
    artifact_ids, contract_ids : tuple[str, ...]
        Non-empty identifier values collected from matching rows.
    missing_required_attributes : tuple[str, ...]
        Attribute names flagged as missing across hardening-required rows.
    failure_reasons : tuple[str, ...]
        Failure reason strings.
    notes : str
        Free-form diagnostics.
    """

    contract_name: str
    observed: bool
    rows: tuple[NormalizedTraceRow, ...]
    row_count: int
    statuses: tuple[str, ...]
    artifact_ids: tuple[str, ...]
    contract_ids: tuple[str, ...]
    missing_required_attributes: tuple[str, ...]
    failure_reasons: tuple[str, ...]
    notes: str

    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable representation (rows omitted — use row_count)."""
        return {
            "contract_name": self.contract_name,
            "observed": self.observed,
            "row_count": self.row_count,
            "statuses": list(self.statuses),
            "artifact_ids": list(self.artifact_ids),
            "contract_ids": list(self.contract_ids),
            "missing_required_attributes": list(self.missing_required_attributes),
            "failure_reasons": list(self.failure_reasons),
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# BTCEvidenceReport — top-level report for one BTC app's trace batch
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BTCEvidenceReport:
    """Evidence report for one ``build_time_compiler`` app across a row batch.

    ``runtime_certification_status`` is always ``NOT_CERTIFIED`` —
    ``__post_init__`` raises ``ValueError`` on any other value.

    ``passed_trace_observed=True`` signals Phase D readiness only; it does
    NOT promote the certification status.
    """

    app_name: str
    route_shape: str
    manifest_hash: str
    static_runtime_mode: str
    runtime_certification_status: str
    required_contracts: tuple[str, ...]
    observed_contracts: tuple[str, ...]
    missing_contracts: tuple[str, ...]
    attribute_hardening_required: tuple[str, ...]
    unknown_needs_runtime_run: tuple[str, ...]
    forbidden_violations: tuple[NormalizedTraceRow, ...]
    contract_evidence: tuple[BTCContractEvidence, ...]
    passed_trace_observed: bool
    failure_reasons: tuple[str, ...]
    notes: str

    def __post_init__(self) -> None:
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                f"BTCEvidenceReport.runtime_certification_status must be "
                f"{NOT_CERTIFIED!r}; got {self.runtime_certification_status!r}. "
                "Phase C never writes a certification verdict."
            )

    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable representation."""
        return {
            "app_name": self.app_name,
            "route_shape": self.route_shape,
            "manifest_hash": self.manifest_hash,
            "static_runtime_mode": self.static_runtime_mode,
            "runtime_certification_status": self.runtime_certification_status,
            "required_contracts": list(self.required_contracts),
            "observed_contracts": list(self.observed_contracts),
            "missing_contracts": list(self.missing_contracts),
            "attribute_hardening_required": list(self.attribute_hardening_required),
            "unknown_needs_runtime_run": list(self.unknown_needs_runtime_run),
            "forbidden_violation_count": len(self.forbidden_violations),
            "contract_evidence": [e.to_dict() for e in self.contract_evidence],
            "passed_trace_observed": self.passed_trace_observed,
            "failure_reasons": list(self.failure_reasons),
            "notes": self.notes,
        }

    def to_json(self) -> str:
        """Compact JSON serialisation for archival."""
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Public extractor function
# ---------------------------------------------------------------------------


def extract_btc_evidence(
    rows: Iterable[NormalizedTraceRow],
    contract: AppRouteContract,
) -> BTCEvidenceReport:
    """Build a ``BTCEvidenceReport`` from a batch of ``NormalizedTraceRow`` rows.

    Parameters
    ----------
    rows:
        Iterable of ``NormalizedTraceRow`` instances (Phase C.2 output).
        Input order is not significant — rows are grouped by contract.
        Rows from other apps are counted in ``notes`` but not used as
        evidence for ``contract.app_name``.
    contract:
        An ``AppRouteContract`` for one BTC app. Must have
        ``route_shape == build_time_compiler`` and
        ``app_name.startswith("apps_")``.

    Returns
    -------
    BTCEvidenceReport
        Structured evidence report. ``runtime_certification_status`` is
        always ``NOT_CERTIFIED``.

    Raises
    ------
    ValueError
        If ``contract.route_shape != build_time_compiler`` or
        ``contract.app_name`` does not start with ``apps_``.
    """
    # -- Input validation ---------------------------------------------------
    if contract.route_shape != RouteShape.build_time_compiler:
        raise ValueError(
            f"extract_btc_evidence requires route_shape=build_time_compiler; "
            f"got {contract.route_shape.value!r} for app {contract.app_name!r}."
        )
    if not contract.app_name.startswith("apps_"):
        raise ValueError(
            f"extract_btc_evidence: contract.app_name must start with 'apps_'; "
            f"got {contract.app_name!r}."
        )

    # -- Manifest hash resolution ------------------------------------------
    resolved_manifest_hash, manifest_note = _resolve_manifest_hash(contract)

    # -- Partition rows into same-app / other-app --------------------------
    all_rows = list(rows)
    app_rows = [r for r in all_rows if r.app_name == contract.app_name]
    other_rows = [r for r in all_rows if r.app_name != contract.app_name]

    notes_parts: list[str] = []
    if manifest_note:
        notes_parts.append(manifest_note)
    if other_rows:
        other_apps = sorted({r.app_name for r in other_rows})
        notes_parts.append(
            f"{len(other_rows)} row(s) from other app(s) "
            f"({', '.join(other_apps)}) were ignored."
        )
    if contract.app_name != _DEFAULT_BTC_APP:
        notes_parts.append(
            f"BTC contract app_name={contract.app_name!r} differs from the "
            f"default expected BTC app {_DEFAULT_BTC_APP!r}; proceeding anyway."
        )

    # -- Build the effective forbidden set ---------------------------------
    # Forbidden = (contract.forbidden_contracts ∪ BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS)
    # minus any contract that is explicitly in required_contracts (carve-out).
    required_set = set(contract.required_contracts)
    forbidden_set: frozenset[str] = frozenset(
        (set(contract.forbidden_contracts) | set(BUILD_TIME_COMPILER_FORBIDDEN_CONTRACTS))
        - required_set
    )

    # -- Detect forbidden rows (BTC-specific, beyond what C.2 flagged) -----
    # Also include any rows already flagged FORBIDDEN_SPAN_VIOLATION by C.2
    # (e.g. CommitRequest on R3R4 apps — shouldn't happen on BTC but preserved
    # if present).
    forbidden_rows: list[NormalizedTraceRow] = []
    evidence_rows: list[NormalizedTraceRow] = []

    for row in app_rows:
        if row.phase_c_status == FORBIDDEN_SPAN_VIOLATION:
            forbidden_rows.append(row)
            continue
        canonical = _canonical_contract(row)
        # A row is forbidden if its canonical contract is in the forbidden set.
        if canonical is not None and canonical in forbidden_set:
            forbidden_rows.append(row)
            continue
        # Also flag raw span-name matches (e.g. literal "CommitRequest" as span_name)
        if row.span_name in forbidden_set:
            forbidden_rows.append(row)
            continue
        evidence_rows.append(row)

    # -- Group evidence rows by resolved contract name ---------------------
    contract_row_map: dict[str, list[NormalizedTraceRow]] = {
        c: [] for c in contract.required_contracts
    }

    for row in evidence_rows:
        canonical = _canonical_contract(row)
        if canonical is None:
            notes_parts.append(
                f"Row span_id={row.span_id!r} has no resolved contract_name; skipped."
            )
            continue
        if canonical in contract_row_map:
            contract_row_map[canonical].append(row)
        else:
            notes_parts.append(
                f"Row span_id={row.span_id!r} resolved to contract "
                f"{canonical!r} which is not in required_contracts; skipped."
            )

    # -- Build per-contract evidence records -------------------------------
    evidence_list: list[BTCContractEvidence] = []
    observed_contracts: list[str] = []
    missing_contracts: list[str] = []
    hardening_contracts: list[str] = []
    unknown_contracts: list[str] = []
    all_failure_reasons: list[str] = []

    for cname in contract.required_contracts:
        c_rows = contract_row_map.get(cname, [])
        evidence = _build_contract_evidence(cname, c_rows)
        evidence_list.append(evidence)
        all_failure_reasons.extend(evidence.failure_reasons)

        if not c_rows:
            missing_contracts.append(cname)
        elif evidence.observed:
            observed_contracts.append(cname)
        else:
            statuses_set = set(evidence.statuses)
            if statuses_set <= _HARDENING_STATUSES:
                hardening_contracts.append(cname)
            elif statuses_set <= _UNKNOWN_STATUSES:
                unknown_contracts.append(cname)
            elif statuses_set <= (_HARDENING_STATUSES | _UNKNOWN_STATUSES):
                hardening_contracts.append(cname)
                unknown_contracts.append(cname)
            else:
                unknown_contracts.append(cname)

    # -- passed_trace_observed logic --------------------------------------
    passed = (
        set(contract.required_contracts) == set(observed_contracts)
        and not forbidden_rows
        and not hardening_contracts
        and not unknown_contracts
    )

    notes = "  ".join(notes_parts) if notes_parts else ""

    return BTCEvidenceReport(
        app_name=contract.app_name,
        route_shape=RouteShape.build_time_compiler.value,
        manifest_hash=resolved_manifest_hash,
        static_runtime_mode=contract.static_runtime_mode,
        runtime_certification_status=NOT_CERTIFIED,
        required_contracts=contract.required_contracts,
        observed_contracts=tuple(observed_contracts),
        missing_contracts=tuple(missing_contracts),
        attribute_hardening_required=tuple(hardening_contracts),
        unknown_needs_runtime_run=tuple(unknown_contracts),
        forbidden_violations=tuple(forbidden_rows),
        contract_evidence=tuple(evidence_list),
        passed_trace_observed=passed,
        failure_reasons=tuple(dict.fromkeys(all_failure_reasons)),
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _canonical_contract(row: NormalizedTraceRow) -> str | None:
    """Return the canonical contract name for a row, honouring equivalences.

    Priority:
    1. ``row.contract_name`` (set by C.2 binding resolution)
    2. ``row.attributes["contract_name"]``

    ``PromptEnvelope`` is mapped to ``CompiledPromptArtifact`` so that the
    forbidden-contract check covers both names (§4.1 Q7).
    """
    name = row.contract_name or row.attributes.get("contract_name")
    if not name or not isinstance(name, str):
        return None
    if name in _PROMPT_ENVELOPE_EQUIVALENCE:
        return _PROMPT_ENVELOPE_CANONICAL
    return name


def _build_contract_evidence(
    contract_name: str,
    rows: list[NormalizedTraceRow],
) -> BTCContractEvidence:
    """Construct a ``BTCContractEvidence`` record for one contract from its rows."""
    if not rows:
        return BTCContractEvidence(
            contract_name=contract_name,
            observed=False,
            rows=(),
            row_count=0,
            statuses=(),
            artifact_ids=(),
            contract_ids=(),
            missing_required_attributes=(),
            failure_reasons=(f"No rows observed for {contract_name!r}.",),
            notes="",
        )

    statuses_seen: set[str] = set()
    artifact_ids: list[str] = []
    contract_ids: list[str] = []
    missing_attrs: set[str] = set()
    failure_reasons: list[str] = []

    for row in rows:
        statuses_seen.add(row.phase_c_status)
        if row.artifact_id:
            artifact_ids.append(row.artifact_id)
        if row.contract_id:
            contract_ids.append(row.contract_id)
        if row.phase_c_status == ATTRIBUTE_HARDENING_REQUIRED and row.mapping_notes:
            missing_attrs.update(_parse_missing_attrs(row.mapping_notes))

    _gap_statuses = _HARDENING_STATUSES | _UNKNOWN_STATUSES | {FORBIDDEN_SPAN_VIOLATION}
    observed = any(r.phase_c_status not in _gap_statuses for r in rows)

    if not observed:
        if statuses_seen & _HARDENING_STATUSES:
            failure_reasons.append(
                f"{contract_name!r}: rows present but attribute hardening required."
            )
        if statuses_seen & _UNKNOWN_STATUSES:
            failure_reasons.append(
                f"{contract_name!r}: rows present but live trace run required."
            )

    return BTCContractEvidence(
        contract_name=contract_name,
        observed=observed,
        rows=tuple(rows),
        row_count=len(rows),
        statuses=tuple(sorted(statuses_seen)),
        artifact_ids=tuple(dict.fromkeys(artifact_ids)),
        contract_ids=tuple(dict.fromkeys(contract_ids)),
        missing_required_attributes=tuple(sorted(missing_attrs)),
        failure_reasons=tuple(failure_reasons),
        notes="",
    )


def _parse_missing_attrs(mapping_notes: str) -> list[str]:
    """Extract attribute names from a 'Missing required attributes: [x, y].' note."""
    marker = "Missing required attributes:"
    idx = mapping_notes.find(marker)
    if idx == -1:
        return []
    tail = mapping_notes[idx + len(marker):].strip().rstrip(".")
    tail = tail.strip("[]")
    parts = [p.strip().strip("'\"") for p in tail.split(",")]
    return [p for p in parts if p]


def _resolve_manifest_hash(contract: AppRouteContract) -> tuple[str, str]:
    """Return ``(hash_str, note)`` for the contract's manifest.

    If ``contract.manifest_hash`` is non-empty, returns it as-is (no I/O).
    Otherwise, attempts ``compute_manifest_hash(contract.manifest_path)``.
    On failure, returns ``("", note)`` — non-fatal at STATIC_EVIDENCE level.
    """
    if contract.manifest_hash:
        return (contract.manifest_hash, "")

    if not contract.manifest_path:
        return ("", "manifest_path is empty; manifest_hash unavailable.")

    try:
        h = compute_manifest_hash(Path(contract.manifest_path))
        return (h, f"manifest_hash computed at runtime from {contract.manifest_path!r}.")
    except FileNotFoundError:
        return (
            "",
            f"manifest_path {contract.manifest_path!r} not found; "
            "manifest_hash unavailable (expected at STATIC_EVIDENCE level).",
        )
    except Exception as exc:  # noqa: BLE001  # guardian: allow-broad-exception -- I/O fallback only, non-critical path
        return (
            "",
            f"manifest_hash computation failed for {contract.manifest_path!r}: {exc}",
        )


# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------

__all__ = [
    "BTCContractEvidence",
    "BTCEvidenceReport",
    "extract_btc_evidence",
]
