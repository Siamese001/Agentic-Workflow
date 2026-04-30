"""Pure trace-row normalizer — Phase C.2.

Converts ``PhaseC1Row`` instances (from Phase C.1) into
``NormalizedTraceRow`` instances by resolving ``contract_name`` and
``normalized_cert_alias`` using the Phase C §4 five-priority matching
precedence and the ``ContractSpanBinding`` catalog from Phase B.2.

Design references
-----------------
- Phase C plan: ``docs/plans/runtime_cert_phase_c_trace_collector_plan.md`` v2 §4
- C.1 adapter:  ``tools/runtime_cert/runtime_adg_query_adapter.py``
- B.2 schema:   ``system_learning/runtime_adg/app_route_contracts.py``
- Tier-1 cats:  ``system_learning/runtime_adg/span_contracts.py``
- Matrix v2:    ``docs/reference/runtime_certification/contract_span_binding_matrix.md``

Five-priority matching (parent plan §4)
----------------------------------------
P1  Tier-1 multi-signal category hit (≥2 of 4 signals: name/kind/layer/attrs)
    If a node scores ≥2 signals for a Tier-1 category AND that category maps
    to a canonical contract, that contract wins.

P2  GenAI semantic-convention attributes
    ``gen_ai.operation.name`` or ``gen_ai.system`` present → maps to the
    ``CompiledPromptArtifact`` equivalence group (``invoke_agent``
    or ``execute_tool`` operation → GenAI.semconv category).

P3  ``accepted_span_name_patterns`` substring match (case-insensitive).

P4  ``accepted_emitter_files`` suffix/substring match against
    ``row.source_path`` or ``row.attributes["code.filepath"]``.

P5  Direct ``attributes["contract_name"]`` assertion
    (post-hardening; present after Phase C.7).

Tie-breaking / ambiguity
------------------------
If two or more bindings match at the *same* priority level, the row is
flagged ``phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN`` with a note that
describes the conflict.  The first binding in the caller-supplied
``bindings`` iterable wins at strictly different priority levels.

What this module does NOT do
----------------------------
- Does NOT certify apps. ``runtime_certification_status`` is always
  ``NOT_CERTIFIED`` — the ``NormalizedTraceRow.__post_init__`` enforces
  this with a ``ValueError``.
- Does NOT write to any store.
- Does NOT modify any emitter, scanner, or CI gate.
- Does NOT import ``RuntimeADGQuery`` (static ADG — distinct store).
- Does NOT remove or filter ``CommitRequest`` rows; it flags them as
  ``FORBIDDEN_SPAN_VIOLATION`` on R3 apps and preserves the row.
"""

from __future__ import annotations

# ADR-079 consumer mode declaration.
__adg_consumer_mode__ = "runtime_cert_read"

import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Final

from system_learning.runtime_adg.app_route_contracts import (
    ContractSpanBinding,
    PhaseAStatus,
    R3_FORBIDDEN_CONTRACTS,
)
from system_learning.runtime_adg.span_contracts import (
    SIGNAL_THRESHOLD,
    _CategoryContract,
    _TIER1_CONTRACTS,
)
from tools.runtime_cert.runtime_adg_query_adapter import (
    NOT_CERTIFIED,
    PhaseC1Row,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Phase C status constants  (approved in parent plan §9 / AG-C-8)
# ---------------------------------------------------------------------------

# Fail-closed evidence statuses (used in phase_c_status field)
TRACE_GAP: Final[str] = "TRACE_GAP"
ATTRIBUTE_HARDENING_REQUIRED: Final[str] = "ATTRIBUTE_HARDENING_REQUIRED"
UNKNOWN_NEEDS_RUNTIME_RUN: Final[str] = "UNKNOWN_NEEDS_RUNTIME_RUN"
FORBIDDEN_SPAN_VIOLATION: Final[str] = "FORBIDDEN_SPAN_VIOLATION"
FORMAL_EXCEPTION_VIOLATION: Final[str] = "FORMAL_EXCEPTION_VIOLATION"
CC_SHARED_05_NOT_PASSED: Final[str] = "CC_SHARED_05_NOT_PASSED"

# Positive / informational statuses (reuse PhaseAStatus names where applicable)
EXISTS_MATCHES_MATRIX: Final[str] = PhaseAStatus.EXISTS_MATCHES_MATRIX.value
EXISTS_NEEDS_ATTRIBUTE_HARDENING: Final[str] = PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING.value
EXISTS_NAME_MISMATCH: Final[str] = PhaseAStatus.EXISTS_NAME_MISMATCH.value
TELEMETRY_MARKER_ONLY: Final[str] = PhaseAStatus.TELEMETRY_MARKER_ONLY.value
LEDGER_EVENT_ONLY: Final[str] = PhaseAStatus.LEDGER_EVENT_ONLY.value
STUB_ONLY: Final[str] = PhaseAStatus.STUB_ONLY.value
NOT_FOUND: Final[str] = PhaseAStatus.NOT_FOUND.value

# Tier-1 category → canonical contract name (for P1 mapping).
# Only categories with a 1:1 mapping to a required R3/BTC contract are listed.
_TIER1_CATEGORY_TO_CONTRACT: Final[dict[str, str]] = {
    "L0.route.select": "RouteContract",
    "L2.step.seal": "SealedArtifact",
    "L2.invoke": "CompiledPromptArtifact",
    "Exit.disposition": "ExitReviewPacket",
    # runtime.trace_root maps to ValidatedRequest (ingress intake span)
    "runtime.trace_root": "ValidatedRequest",
}

# GenAI semconv operation names that map to the CompiledPromptArtifact group.
_GENAI_INVOKE_OPERATIONS: Final[frozenset[str]] = frozenset(
    {"invoke_agent", "execute_tool", "chat", "text_completion", "embeddings"}
)

# R3 route shapes — used for CommitRequest forbidden-span detection.
_R3_ROUTE_SHAPES: Final[frozenset[str]] = frozenset(
    {"R3_grounded_read", "R3R4_grounded_write"}
)


# ---------------------------------------------------------------------------
# NormalizedTraceRow dataclass
# ---------------------------------------------------------------------------


@dataclass
class NormalizedTraceRow:
    """Phase C.2 output — a PhaseC1Row enriched with contract resolution.

    All fields from ``PhaseC1Row`` are preserved.  Added fields:

    contract_name : str | None
        Resolved canonical contract name (e.g. ``"SealedArtifact"``).
        ``None`` if no binding matched.
    normalized_cert_alias : str | None
        From ``ContractSpanBinding.normalized_cert_alias``.
        ``None`` if no binding matched.
    phase_c_status : str
        One of the Phase C status constants defined in this module.
    match_basis : str
        Short human-readable description of which priority level resolved
        the match (e.g. ``"P1:tier1_category:L2.step.seal"``).
        Empty string if unresolved.
    mapping_notes : str
        Free-form notes (ambiguity explanations, live-trace requirement
        notices, attribute gap lists, etc.)
    binding_contract_name : str | None
        The ``ContractSpanBinding.contract_name`` of the winning binding,
        for cases where the row's ``contract_name`` differs from the
        binding's (e.g. PromptEnvelope equivalence group).

    Invariant
    ---------
    ``runtime_certification_status`` is always ``NOT_CERTIFIED``.
    ``__post_init__`` raises ``ValueError`` if any other value is supplied.
    """

    # ---- identity (from C.1) ----
    app_name: str
    route_shape: str
    trace_id: str
    span_id: str
    parent_span_id: str | None
    span_name: str
    timestamp: int

    # ---- C.2 resolved fields ----
    contract_name: str | None
    normalized_cert_alias: str | None
    phase_c_status: str
    match_basis: str
    mapping_notes: str
    binding_contract_name: str | None

    # ---- app-level provenance (C.3/C.4/C.5 back-fill) ----
    manifest_hash: str = ""
    static_runtime_mode: str = ""

    # ---- certification status — INVARIANT ----
    runtime_certification_status: str = NOT_CERTIFIED

    # ---- optional identifiers ----
    artifact_id: str | None = None
    contract_id: str | None = None
    source_path: str | None = None

    # ---- nested attributes (preserved intact from C.1) ----
    attributes: dict[str, Any] = field(default_factory=dict)

    # ---- provenance ----
    evidence_source: str = ""

    def __post_init__(self) -> None:
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                f"NormalizedTraceRow.runtime_certification_status must be "
                f"{NOT_CERTIFIED!r}; got {self.runtime_certification_status!r}. "
                "Phase C never writes a certification verdict."
            )

    def to_dict(self) -> dict[str, Any]:
        """Return a flat JSON-serialisable dict.

        Includes all fields plus ``schema_version`` for Phase D cache compatibility.
        """
        return {
            "app_name": self.app_name,
            "route_shape": self.route_shape,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "span_name": self.span_name,
            "timestamp": self.timestamp,
            "contract_name": self.contract_name,
            "normalized_cert_alias": self.normalized_cert_alias,
            "phase_c_status": self.phase_c_status,
            "match_basis": self.match_basis,
            "mapping_notes": self.mapping_notes,
            "binding_contract_name": self.binding_contract_name,
            "manifest_hash": self.manifest_hash,
            "static_runtime_mode": self.static_runtime_mode,
            "runtime_certification_status": self.runtime_certification_status,
            "artifact_id": self.artifact_id,
            "contract_id": self.contract_id,
            "source_path": self.source_path,
            "attributes": self.attributes,
            "evidence_source": self.evidence_source,
            "schema_version": "1.0",
        }


# ---------------------------------------------------------------------------
# Public normalization functions
# ---------------------------------------------------------------------------


def normalize_trace_row(
    row: PhaseC1Row,
    bindings: Iterable[ContractSpanBinding],
) -> NormalizedTraceRow:
    """Resolve contract binding for one ``PhaseC1Row``.

    Parameters
    ----------
    row:
        A ``PhaseC1Row`` produced by Phase C.1 (``node_to_row`` /
        ``iter_rows_from_snapshot``).  ``contract_name`` and
        ``normalized_cert_alias`` must be ``None`` on entry (C.1 guarantees
        this); if they are already set, their values are used as a P5
        attribute assertion fallback.
    bindings:
        Ordered iterable of ``ContractSpanBinding`` objects for the
        app/route being normalized.  Typically sourced from
        ``AppRouteContract.bindings``.

    Returns
    -------
    NormalizedTraceRow
        A new row with ``contract_name``, ``normalized_cert_alias``,
        ``phase_c_status``, ``match_basis``, and ``mapping_notes`` populated.
        All other fields are carried forward unchanged from ``row``.

    Notes
    -----
    - ``CommitRequest`` spans on R3 apps are preserved and flagged
      ``FORBIDDEN_SPAN_VIOLATION``.
    - If no binding matches, ``phase_c_status`` is ``UNKNOWN_NEEDS_RUNTIME_RUN``.
    - If a binding matches but required attributes are missing,
      ``phase_c_status`` is ``ATTRIBUTE_HARDENING_REQUIRED``.
    - ``runtime_certification_status`` is always ``NOT_CERTIFIED``.
    """
    bindings_list = list(bindings)

    # ---- forbidden-span check (before contract resolution) ----------------
    forbidden_result = _check_forbidden_span(row)
    if forbidden_result is not None:
        return _make_normalized(row, **forbidden_result)

    # ---- five-priority matching -------------------------------------------
    match = _resolve_binding(row, bindings_list)

    if match is None:
        return _make_normalized(
            row,
            contract_name=None,
            normalized_cert_alias=None,
            phase_c_status=UNKNOWN_NEEDS_RUNTIME_RUN,
            match_basis="",
            mapping_notes="No binding matched any of the 5 priority levels.",
            binding_contract_name=None,
        )

    binding, match_basis, notes = match

    # ---- attribute completeness check ------------------------------------
    missing_attrs = _check_required_attributes(row, binding)
    if missing_attrs:
        notes_full = (
            f"{notes}  Missing required attributes: {missing_attrs}."
            if notes
            else f"Missing required attributes: {missing_attrs}."
        )
        return _make_normalized(
            row,
            contract_name=binding.contract_name,
            normalized_cert_alias=binding.normalized_cert_alias,
            phase_c_status=ATTRIBUTE_HARDENING_REQUIRED,
            match_basis=match_basis,
            mapping_notes=notes_full,
            binding_contract_name=binding.contract_name,
        )

    # ---- derive phase_c_status from binding's Phase A status -------------
    phase_c_status = _phase_a_to_phase_c_status(binding.phase_a_status)
    if binding.live_trace_required:
        notes = (
            f"{notes}  live_trace_required=True (Phase A status: "
            f"{binding.phase_a_status.value})."
            if notes
            else (
                f"live_trace_required=True (Phase A status: "
                f"{binding.phase_a_status.value})."
            )
        )

    return _make_normalized(
        row,
        contract_name=binding.contract_name,
        normalized_cert_alias=binding.normalized_cert_alias,
        phase_c_status=phase_c_status,
        match_basis=match_basis,
        mapping_notes=notes,
        binding_contract_name=binding.contract_name,
    )


def normalize_trace_rows(
    rows: Iterable[PhaseC1Row],
    bindings: Iterable[ContractSpanBinding],
) -> tuple[NormalizedTraceRow, ...]:
    """Normalize an ordered sequence of ``PhaseC1Row`` objects.

    Parameters
    ----------
    rows:
        Iterable of ``PhaseC1Row`` instances (typically from
        ``iter_rows_from_snapshot``).  Input order is preserved in the output.
    bindings:
        ``ContractSpanBinding`` objects to match against.  The iterable is
        consumed once and materialised internally so it can be reused across
        each row.

    Returns
    -------
    tuple[NormalizedTraceRow, ...]
        One ``NormalizedTraceRow`` per input row, in the same order.
    """
    bindings_list = list(bindings)
    return tuple(normalize_trace_row(r, bindings_list) for r in rows)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _make_normalized(row: PhaseC1Row, **overrides: Any) -> NormalizedTraceRow:
    """Construct a ``NormalizedTraceRow`` from a ``PhaseC1Row`` + override fields."""
    return NormalizedTraceRow(
        app_name=row.app_name,
        route_shape=row.route_shape,
        trace_id=row.trace_id,
        span_id=row.span_id,
        parent_span_id=row.parent_span_id,
        span_name=row.span_name,
        timestamp=row.timestamp,
        manifest_hash=row.manifest_hash,
        static_runtime_mode=row.static_runtime_mode,
        runtime_certification_status=NOT_CERTIFIED,
        artifact_id=row.artifact_id,
        contract_id=row.contract_id,
        source_path=row.source_path,
        attributes=row.attributes,
        evidence_source=row.evidence_source,
        **overrides,
    )


def _check_forbidden_span(row: PhaseC1Row) -> dict[str, Any] | None:
    """Return override kwargs if this span is forbidden, else None.

    A ``CommitRequest`` span on an R3 app is a forbidden-span violation per
    the binding matrix §9.3.  The row is preserved; the status is flagged.
    """
    is_r3 = row.route_shape in _R3_ROUTE_SHAPES
    if not is_r3:
        return None
    span_is_commit = row.span_name in R3_FORBIDDEN_CONTRACTS
    attr_contract = row.attributes.get("contract_name", "")
    attr_is_commit = isinstance(attr_contract, str) and attr_contract in R3_FORBIDDEN_CONTRACTS
    if span_is_commit or attr_is_commit:
        trigger = row.span_name if span_is_commit else attr_contract
        return {
            "contract_name": trigger,
            "normalized_cert_alias": None,
            "phase_c_status": FORBIDDEN_SPAN_VIOLATION,
            "match_basis": "forbidden_span",
            "mapping_notes": (
                f"CommitRequest span detected on R3 app ({row.route_shape}). "
                "Row preserved; violation flagged per binding matrix §9.3."
            ),
            "binding_contract_name": None,
        }
    return None


def _resolve_binding(
    row: PhaseC1Row,
    bindings: list[ContractSpanBinding],
) -> tuple[ContractSpanBinding, str, str] | None:
    """Apply the five-priority matching to find the best binding.

    Returns ``(binding, match_basis_str, notes_str)`` or ``None``.
    """
    attrs = row.attributes

    # P1 — Tier-1 multi-signal category match
    p1_result = _try_p1_tier1(row, attrs, bindings)
    if p1_result is not None:
        return p1_result

    # P2 — GenAI semantic-convention attributes
    p2_result = _try_p2_genai(attrs, bindings)
    if p2_result is not None:
        return p2_result

    # P3 — accepted_span_name_patterns
    p3_result = _try_p3_name_patterns(row, bindings)
    if p3_result is not None:
        return p3_result

    # P4 — accepted_emitter_files
    p4_result = _try_p4_emitter_files(row, attrs, bindings)
    if p4_result is not None:
        return p4_result

    # P5 — direct attributes["contract_name"] assertion
    p5_result = _try_p5_direct_attr(attrs, bindings)
    if p5_result is not None:
        return p5_result

    return None


# ---------- P1 ---------------------------------------------------------------


def _score_tier1(row: PhaseC1Row, attrs: dict[str, Any], contract: _CategoryContract) -> int:
    """Score a node against a Tier-1 _CategoryContract (0-4 signals)."""
    score = 0
    name_lower = row.span_name.lower()
    if any(pat.lower() in name_lower for pat in contract.name_patterns):
        score += 1
    kind_lower = row.attributes.get("kind", "").lower() if not row.span_name else ""
    # Use the node's kind from attributes if available; otherwise skip kind signal
    node_kind = attrs.get("kind", "") or attrs.get("span_kind", "")
    if node_kind and contract.kinds:
        nk = str(node_kind).lower()
        if any(nk == k.lower() or nk.startswith(k.lower()) for k in contract.kinds):
            score += 1
    # Layer signal
    node_layer = attrs.get("layer", "") or attrs.get("arch_layer", "")
    if node_layer and contract.layers:
        nl = str(node_layer).lower()
        if any(nl.startswith(lyr.lower()) for lyr in contract.layers):
            score += 1
    # Attr signal
    if any(k in attrs for k in contract.required_any_attr):
        score += 1
    return score


def _try_p1_tier1(
    row: PhaseC1Row,
    attrs: dict[str, Any],
    bindings: list[ContractSpanBinding],
) -> tuple[ContractSpanBinding, str, str] | None:
    """P1: find highest-scoring Tier-1 category, map to contract, find binding."""
    best_cat: str | None = None
    best_score = 0
    for cat_name, cat_contract in _TIER1_CONTRACTS.items():
        score = _score_tier1(row, attrs, cat_contract)
        if score > best_score:
            best_score = score
            best_cat = cat_name
        elif score == best_score and score >= SIGNAL_THRESHOLD:
            # Tie at threshold — ambiguous; clear best to force no P1 match
            best_cat = None

    if best_cat is None or best_score < SIGNAL_THRESHOLD:
        return None

    target_contract = _TIER1_CATEGORY_TO_CONTRACT.get(best_cat)
    if target_contract is None:
        return None

    # Find matching binding for target_contract
    candidates = [b for b in bindings if b.contract_name == target_contract]
    if not candidates:
        return None
    if len(candidates) > 1:
        logger.debug(
            "P1: multiple bindings for contract=%s; using first.", target_contract
        )
    binding = candidates[0]
    return (
        binding,
        f"P1:tier1_category:{best_cat}",
        f"Tier-1 signal score={best_score}/4 for category {best_cat!r}.",
    )


# ---------- P2 ---------------------------------------------------------------

_GENAI_ATTR_KEYS: Final[tuple[str, ...]] = (
    "gen_ai.operation.name",
    "gen_ai.system",
    "gen_ai.request.model",
    "gen_ai.response.model",
)


def _try_p2_genai(
    attrs: dict[str, Any],
    bindings: list[ContractSpanBinding],
) -> tuple[ContractSpanBinding, str, str] | None:
    """P2: GenAI semantic-convention attributes → CompiledPromptArtifact binding."""
    genai_present = any(k in attrs for k in _GENAI_ATTR_KEYS)
    if not genai_present:
        return None

    op_name = str(attrs.get("gen_ai.operation.name", "")).lower()
    is_invoke = op_name in {op.lower() for op in _GENAI_INVOKE_OPERATIONS} or bool(op_name)

    if not is_invoke and not genai_present:
        return None

    # Map to CompiledPromptArtifact (GenAI semconv equivalence group).
    candidates = [
        b for b in bindings
        if b.contract_name in ("CompiledPromptArtifact", "PromptEnvelope")
        or "GenAI.semconv" in b.accepted_emitter_categories
    ]
    if not candidates:
        return None
    binding = candidates[0]
    matched_key = next((k for k in _GENAI_ATTR_KEYS if k in attrs), "gen_ai.*")
    return (
        binding,
        f"P2:genai_semconv:{matched_key}",
        f"GenAI semconv attribute {matched_key!r} present.",
    )


# ---------- P3 ---------------------------------------------------------------


def _span_name_matches_pattern(name_lower: str, pattern: str) -> bool:
    """Return True if ``name_lower`` matches ``pattern`` (case-insensitive).

    Patterns may use a single leading or trailing ``*`` as a wildcard:

    - ``"exit.*"``   → name starts with ``"exit."``
    - ``"*.seal"``   → name ends with   ``".seal"``
    - ``"*.v1.*"``   → plain substring match of ``".v1."``
    - ``"foo"``      → plain substring match of ``"foo"``
    """
    pat = pattern.lower()
    if pat.endswith("*") and not pat.startswith("*"):
        # prefix glob: "exit.*" → name must start with "exit."
        prefix = pat[:-1]  # strip trailing *
        return name_lower.startswith(prefix)
    if pat.startswith("*") and not pat.endswith("*"):
        # suffix glob: "*.seal" → name must end with ".seal"
        suffix = pat[1:]  # strip leading *
        return name_lower.endswith(suffix)
    # Wildcard in middle or no wildcard: strip all * and do substring match
    stripped = pat.replace("*", "")
    if not stripped:
        return False
    return stripped in name_lower or name_lower in stripped


def _try_p3_name_patterns(
    row: PhaseC1Row,
    bindings: list[ContractSpanBinding],
) -> tuple[ContractSpanBinding, str, str] | None:
    """P3: accepted_span_name_patterns substring/glob match (case-insensitive)."""
    name_lower = row.span_name.lower()
    matches: list[ContractSpanBinding] = []
    for b in bindings:
        for pat in b.accepted_span_name_patterns:
            if _span_name_matches_pattern(name_lower, pat):
                matches.append(b)
                break

    if not matches:
        return None
    if len(matches) > 1:
        contracts = [b.contract_name for b in matches]
        return (
            matches[0],
            f"P3:name_pattern:{row.span_name!r}",
            f"Ambiguous: span name matched {len(matches)} bindings "
            f"({contracts}). Using first match.",
        )
    binding = matches[0]
    matched_pat = next(
        p for p in binding.accepted_span_name_patterns
        if _span_name_matches_pattern(name_lower, p)
    )
    return (
        binding,
        f"P3:name_pattern:{matched_pat!r}",
        "",
    )


# ---------- P4 ---------------------------------------------------------------


def _try_p4_emitter_files(
    row: PhaseC1Row,
    attrs: dict[str, Any],
    bindings: list[ContractSpanBinding],
) -> tuple[ContractSpanBinding, str, str] | None:
    """P4: accepted_emitter_files suffix/substring match against source_path."""
    source = (
        row.source_path
        or str(attrs.get("code.filepath", ""))
        or str(attrs.get("source_path", ""))
    )
    if not source:
        return None

    source_norm = source.replace("\\", "/").lower()
    matches: list[ContractSpanBinding] = []
    for b in bindings:
        for ef in b.accepted_emitter_files:
            ef_norm = ef.replace("\\", "/").lower()
            if ef_norm in source_norm or source_norm.endswith(ef_norm):
                matches.append(b)
                break

    if not matches:
        return None
    if len(matches) > 1:
        contracts = [b.contract_name for b in matches]
        return (
            matches[0],
            f"P4:emitter_file:{source!r}",
            f"Ambiguous: source path matched {len(matches)} bindings "
            f"({contracts}). Using first match.",
        )
    binding = matches[0]
    return (
        binding,
        f"P4:emitter_file:{source!r}",
        "",
    )


# ---------- P5 ---------------------------------------------------------------


def _try_p5_direct_attr(
    attrs: dict[str, Any],
    bindings: list[ContractSpanBinding],
) -> tuple[ContractSpanBinding, str, str] | None:
    """P5: direct ``attributes["contract_name"]`` assertion."""
    attr_contract = attrs.get("contract_name")
    if not attr_contract or not isinstance(attr_contract, str):
        return None

    candidates = [b for b in bindings if b.contract_name == attr_contract]
    if not candidates:
        # No binding for asserted contract_name — note it but return no match.
        logger.debug(
            "P5: attributes['contract_name']=%r has no matching binding.", attr_contract
        )
        return None
    binding = candidates[0]
    return (
        binding,
        f"P5:direct_attr:contract_name={attr_contract!r}",
        "Direct attribute assertion (post-hardening path).",
    )


# ---------- Attribute completeness -------------------------------------------


def _check_required_attributes(
    row: PhaseC1Row,
    binding: ContractSpanBinding,
) -> list[str]:
    """Return list of required attribute names that are missing from the row."""
    missing: list[str] = []
    for req in binding.required_attributes:
        if not req.required:
            continue
        # Check top-level row fields first, then nested attributes dict.
        name = req.name
        top_val = getattr(row, name, None)
        attr_val = row.attributes.get(name)
        if top_val is None and not attr_val:
            missing.append(name)
    return missing


# ---------- Phase A → Phase C status mapping ---------------------------------

_PHASE_A_TO_C: Final[dict[PhaseAStatus, str]] = {
    PhaseAStatus.EXISTS_MATCHES_MATRIX: EXISTS_MATCHES_MATRIX,
    PhaseAStatus.EXISTS_NEEDS_ATTRIBUTE_HARDENING: EXISTS_NEEDS_ATTRIBUTE_HARDENING,
    PhaseAStatus.EXISTS_NAME_MISMATCH: EXISTS_NAME_MISMATCH,
    PhaseAStatus.TELEMETRY_MARKER_ONLY: TELEMETRY_MARKER_ONLY,
    PhaseAStatus.LEDGER_EVENT_ONLY: LEDGER_EVENT_ONLY,
    PhaseAStatus.STUB_ONLY: STUB_ONLY,
    PhaseAStatus.NOT_FOUND: NOT_FOUND,
    PhaseAStatus.UNKNOWN_NEEDS_RUNTIME_RUN: UNKNOWN_NEEDS_RUNTIME_RUN,
}


def _phase_a_to_phase_c_status(phase_a: PhaseAStatus) -> str:
    return _PHASE_A_TO_C.get(phase_a, UNKNOWN_NEEDS_RUNTIME_RUN)


# ---------------------------------------------------------------------------
# Public API surface
# ---------------------------------------------------------------------------

__all__ = [
    # Dataclass
    "NormalizedTraceRow",
    # Normalization functions
    "normalize_trace_row",
    "normalize_trace_rows",
    # Phase C status constants
    "TRACE_GAP",
    "ATTRIBUTE_HARDENING_REQUIRED",
    "UNKNOWN_NEEDS_RUNTIME_RUN",
    "FORBIDDEN_SPAN_VIOLATION",
    "FORMAL_EXCEPTION_VIOLATION",
    "CC_SHARED_05_NOT_PASSED",
    "EXISTS_MATCHES_MATRIX",
    "EXISTS_NEEDS_ATTRIBUTE_HARDENING",
    "EXISTS_NAME_MISMATCH",
    "TELEMETRY_MARKER_ONLY",
    "LEDGER_EVENT_ONLY",
    "STUB_ONLY",
    "NOT_FOUND",
]
