"""Formal-exception negative-control query helpers (Phase B.5).

Design references
-----------------
- ``docs/reference/runtime_certification/contract_span_binding_matrix.md`` v2 §6
- ``docs/reports/runtime_certification/phase_a_trace_inventory.md``
- Sibling: ``system_learning/runtime_adg/formal_exception_evidence.py`` (B.4)

What this module does
---------------------
Provides **pure**, row-iterable-based negative-control checks for the
three formal-exception apps. These helpers operate on an
``Iterable[Mapping[str, Any]]`` of span / event rows supplied by the
caller \u2014 NO live runtime ADG database dependency. A future cert
harness will wire these helpers to the real runtime-ADG query surface
(``tools/adg/runtime_query.py``) in Phase C; Phase B.5 keeps them
query-adapter-agnostic.

Controls implemented
--------------------
- **CC-EVAL-01** \u2014 no evaluator-of-evaluator circularity in apps_eval traces.
- **CC-EVAL-02** \u2014 apps_eval must not leak R3 contracts outside its allowed surface.
- **CC-UW-02** \u2014 apps_underwriting_ai must not leak R3 contracts outside its allowed surface.
- **CC-SHARED-03** \u2014 apps_shared ``SealedArtifact`` must be proof-harness only.

What this module is NOT
-----------------------
- Not a trace collector (Phase C).
- Not a certification evaluator end-to-end (Phase D).
- Not a CI gate (Phase E).
- Does NOT change app behavior, emit any span, or mutate any state.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

CC_EVAL_01: str = "CC-EVAL-01"
CC_EVAL_02: str = "CC-EVAL-02"
CC_UW_02: str = "CC-UW-02"
CC_SHARED_03: str = "CC-SHARED-03"

#: Canonical R3 contract set \u2014 mirrors
#: ``system_learning/runtime_adg/app_route_contracts.py::R3_GROUNDED_READ_CONTRACTS``
#: plus the ``PromptEnvelope`` equivalence-group member.
R3_CONTRACT_SET: frozenset[str] = frozenset(
    {
        "ValidatedRequest",
        "L1PlanContract",
        "RouteContract",
        "RetrievalPlan",
        "FinalEvidenceContract",
        "CompiledPromptArtifact",
        "PromptEnvelope",  # equivalence group member
        "SealedArtifact",
        "ExitReviewPacket",
    }
)

#: apps_eval surfaces on which an R3 contract would be architecturally legal
#: (evaluator reading graded prompts for stability scoring). Callers may
#: override via the ``allowed_surfaces`` parameter.
_DEFAULT_EVAL_ALLOWED_SURFACES: frozenset[str] = frozenset(
    {
        "evaluator_only",
        "evaluation",
        "eval_stability",
    }
)

#: apps_underwriting_ai surfaces on which an R3 contract would be legal
#: (regulated-domain evaluation). Callers may override.
_DEFAULT_UW_ALLOWED_SURFACES: frozenset[str] = frozenset(
    {
        "regulated_decision",
        "governance.regulated_decision",
        "regulatory_domain",
    }
)

#: File-path substrings identifying the proof-harness origin of
#: apps_shared's ``SealedArtifact`` import.
_PROOF_HARNESS_PATH_MARKERS: tuple[str, ...] = (
    "apps_shared/proof/",
    "apps_shared\\proof\\",  # windows-style path
    "apps_shared/proof_",  # conservative
)


# ---------------------------------------------------------------------------
# Result record
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class NegativeControlResult:
    """Structured result of a single negative-control check."""

    control_id: str
    passed: bool
    violation_count: int
    violations: tuple[Mapping[str, Any], ...]
    query_summary: Mapping[str, Any]
    failure_reasons: tuple[str, ...]
    notes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.control_id:
            raise ValueError("NegativeControlResult.control_id must be non-empty")
        if self.violation_count != len(self.violations):
            raise ValueError(
                f"NegativeControlResult({self.control_id!r}): violation_count="
                f"{self.violation_count} does not match len(violations)="
                f"{len(self.violations)}"
            )
        if self.passed and self.violation_count > 0:
            raise ValueError(
                f"NegativeControlResult({self.control_id!r}): passed=True "
                f"contradicts violation_count={self.violation_count}"
            )

    def to_dict(self) -> dict[str, Any]:
        """JSON-safe serialization for cert-report archival."""
        d = asdict(self)
        # asdict deep-copies dicts; convert Mapping-typed fields explicitly.
        d["violations"] = [dict(v) for v in self.violations]
        d["query_summary"] = dict(self.query_summary)
        return d


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _row_app_name(row: Mapping[str, Any]) -> str | None:
    """Defensive accessor that tolerates missing ``app_name`` fields."""
    value = row.get("app_name")
    if isinstance(value, str) and value:
        return value
    # Some rows may put app_name under attributes.
    attrs = row.get("attributes")
    if isinstance(attrs, Mapping):
        value = attrs.get("app_name")
        if isinstance(value, str) and value:
            return value
    return None


def _row_contract_name(row: Mapping[str, Any]) -> str | None:
    """Defensive accessor for ``contract_name``."""
    value = row.get("contract_name")
    if isinstance(value, str) and value:
        return value
    attrs = row.get("attributes")
    if isinstance(attrs, Mapping):
        value = attrs.get("contract_name")
        if isinstance(value, str) and value:
            return value
    return None


def _row_source_path(row: Mapping[str, Any]) -> str | None:
    """Defensive accessor for the span emitter's source file path."""
    for key in ("source_path", "file_path", "code.filepath"):
        value = row.get(key)
        if isinstance(value, str) and value:
            return value
    attrs = row.get("attributes")
    if isinstance(attrs, Mapping):
        for key in ("source_path", "file_path", "code.filepath"):
            value = attrs.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _is_proof_harness_path(path: str | None) -> bool:
    if not path:
        return False
    return any(marker in path for marker in _PROOF_HARNESS_PATH_MARKERS)


def _row_is_production(row: Mapping[str, Any]) -> bool:
    """Return False if the row is explicitly marked test / proof / non-production.

    Defaults to True (conservative) when no explicit marker is present \u2014 this
    is a fail-closed choice for CC-SHARED-03. Callers that know their rows
    are all test-origin should set ``environment=test`` (or similar).
    """
    env = row.get("environment")
    if isinstance(env, str) and env.lower() in {
        "test",
        "tests",
        "proof",
        "proof_harness",
        "non_production",
        "nonprod",
    }:
        return False
    kind = row.get("span_kind") or row.get("kind")
    if isinstance(kind, str) and kind.lower() in {"test", "proof"}:
        return False
    attrs = row.get("attributes")
    if isinstance(attrs, Mapping):
        env2 = attrs.get("environment") or attrs.get("deployment.environment")
        if isinstance(env2, str) and env2.lower() in {
            "test",
            "tests",
            "proof",
            "proof_harness",
            "non_production",
            "nonprod",
        }:
            return False
    return True


# ---------------------------------------------------------------------------
# CC-EVAL-01
# ---------------------------------------------------------------------------


def check_no_eval_of_evaluator_circularity(
    rows: Iterable[Mapping[str, Any]],
) -> NegativeControlResult:
    """CC-EVAL-01: no evaluator-of-evaluator circularity in apps_eval traces.

    A trace is circular if its root span has ``app_name=apps_eval`` AND
    any non-root span in the same trace also has ``app_name=apps_eval``.
    """
    rows_list = list(rows)
    # Group by trace_id.
    traces: dict[str, list[Mapping[str, Any]]] = {}
    rows_without_trace = 0
    for row in rows_list:
        tid = row.get("trace_id")
        if not isinstance(tid, str) or not tid:
            rows_without_trace += 1
            continue
        traces.setdefault(tid, []).append(row)

    violations: list[Mapping[str, Any]] = []
    notes: list[str] = []
    if rows_without_trace:
        notes.append(
            f"{rows_without_trace} row(s) skipped: missing or empty trace_id"
        )

    for tid, trace_rows in traces.items():
        root = _find_trace_root(trace_rows)
        if root is None:
            notes.append(f"trace_id={tid!r}: no root span identifiable; skipped")
            continue
        if _row_app_name(root) != "apps_eval":
            continue
        descendants = [r for r in trace_rows if r is not root]
        for desc in descendants:
            if _row_app_name(desc) == "apps_eval":
                violations.append(
                    {
                        "control": CC_EVAL_01,
                        "trace_id": tid,
                        "root_span_id": root.get("span_id"),
                        "descendant_span_id": desc.get("span_id"),
                        "descendant_span_name": desc.get("span_name"),
                        "descendant_contract_name": _row_contract_name(desc),
                    }
                )

    failure_reasons: tuple[str, ...] = ()
    if violations:
        failure_reasons = (
            f"{len(violations)} evaluator-of-evaluator circularity "
            f"violation(s) detected across apps_eval traces",
        )

    return NegativeControlResult(
        control_id=CC_EVAL_01,
        passed=not violations,
        violation_count=len(violations),
        violations=tuple(violations),
        query_summary={
            "traces_scanned": len(traces),
            "rows_scanned": len(rows_list),
            "rows_without_trace_id": rows_without_trace,
        },
        failure_reasons=failure_reasons,
        notes=tuple(notes),
    )


def _find_trace_root(trace_rows: list[Mapping[str, Any]]) -> Mapping[str, Any] | None:
    """Return the row whose ``parent_span_id`` is empty / None \u2014 that's the root.

    If multiple candidates exist (multi-root trace), returns the first. If
    none exist, returns None \u2014 the caller records this as ambiguous.
    """
    candidates = [
        r
        for r in trace_rows
        if not r.get("parent_span_id")
        and r.get("parent_span_id") not in {"", None}
        or r.get("parent_span_id") is None
        or r.get("parent_span_id") == ""
    ]
    # The above is deliberately permissive to collapse None / "" / missing
    # into "this is a root". Pick the first.
    for r in trace_rows:
        psid = r.get("parent_span_id")
        if psid is None or psid == "":
            return r
    return None


# ---------------------------------------------------------------------------
# CC-EVAL-02 / CC-UW-02 \u2014 shared "R3 contract leak" shape
# ---------------------------------------------------------------------------


def _r3_leak_check(
    rows: Iterable[Mapping[str, Any]],
    *,
    control_id: str,
    app_name: str,
    allowed_surfaces: frozenset[str],
) -> NegativeControlResult:
    """Shared implementation for CC-EVAL-02 / CC-UW-02."""
    rows_list = list(rows)
    violations: list[Mapping[str, Any]] = []
    notes: list[str] = []
    rows_scanned = 0
    rows_for_app = 0

    for row in rows_list:
        rows_scanned += 1
        if _row_app_name(row) != app_name:
            continue
        rows_for_app += 1
        contract = _row_contract_name(row)
        if contract not in R3_CONTRACT_SET:
            continue
        # Is this R3 contract on an allowed surface for the app?
        surface = row.get("route_shape") or row.get("surface") or ""
        span_name = row.get("span_name") or ""
        allowed = (
            surface in allowed_surfaces
            or any(a in (span_name or "") for a in allowed_surfaces)
        )
        if not allowed:
            violations.append(
                {
                    "control": control_id,
                    "app_name": app_name,
                    "contract_name": contract,
                    "span_id": row.get("span_id"),
                    "span_name": span_name,
                    "trace_id": row.get("trace_id"),
                    "route_shape": surface or None,
                }
            )

    failure_reasons: tuple[str, ...] = ()
    if violations:
        failure_reasons = (
            f"{len(violations)} R3-contract leak(s) detected on "
            f"{app_name!r} outside allowed surfaces {sorted(allowed_surfaces)!r}",
        )

    return NegativeControlResult(
        control_id=control_id,
        passed=not violations,
        violation_count=len(violations),
        violations=tuple(violations),
        query_summary={
            "app_name": app_name,
            "allowed_surfaces": sorted(allowed_surfaces),
            "rows_scanned": rows_scanned,
            "rows_for_app": rows_for_app,
        },
        failure_reasons=failure_reasons,
        notes=tuple(notes),
    )


def check_apps_eval_no_r3_contract_leak(
    rows: Iterable[Mapping[str, Any]],
    *,
    allowed_surfaces: frozenset[str] | None = None,
) -> NegativeControlResult:
    """CC-EVAL-02: apps_eval must not leak R3 contracts outside its surface."""
    surfaces = (
        allowed_surfaces
        if allowed_surfaces is not None
        else _DEFAULT_EVAL_ALLOWED_SURFACES
    )
    return _r3_leak_check(
        rows,
        control_id=CC_EVAL_02,
        app_name="apps_eval",
        allowed_surfaces=surfaces,
    )


def check_underwriting_no_r3_contract_leak(
    rows: Iterable[Mapping[str, Any]],
    *,
    allowed_surfaces: frozenset[str] | None = None,
) -> NegativeControlResult:
    """CC-UW-02: apps_underwriting_ai must stay on its formal surface."""
    surfaces = (
        allowed_surfaces
        if allowed_surfaces is not None
        else _DEFAULT_UW_ALLOWED_SURFACES
    )
    return _r3_leak_check(
        rows,
        control_id=CC_UW_02,
        app_name="apps_underwriting_ai",
        allowed_surfaces=surfaces,
    )


# ---------------------------------------------------------------------------
# CC-SHARED-03
# ---------------------------------------------------------------------------


def check_apps_shared_sealed_artifact_proof_only(
    rows: Iterable[Mapping[str, Any]],
) -> NegativeControlResult:
    """CC-SHARED-03: apps_shared ``SealedArtifact`` must be proof-harness only.

    Fails if any production trace has ``contract_name=SealedArtifact`` whose
    emitter source path lies under ``apps_shared/proof/``.
    """
    rows_list = list(rows)
    violations: list[Mapping[str, Any]] = []
    notes: list[str] = []
    rows_scanned = 0
    rows_with_sealed = 0
    rows_with_unknown_source = 0

    for row in rows_list:
        rows_scanned += 1
        if _row_contract_name(row) != "SealedArtifact":
            continue
        rows_with_sealed += 1
        source = _row_source_path(row)
        if source is None:
            rows_with_unknown_source += 1
            # Ambiguous row: can't confirm violation, can't confirm safe.
            # Record in notes only \u2014 do not fail closed here because many
            # legitimate SealedArtifact spans elsewhere in the repo will
            # not carry source_path. Callers can upgrade to fail-closed
            # by filtering for apps_shared-originated spans upstream.
            continue
        if not _is_proof_harness_path(source):
            continue
        # At this point: SealedArtifact + source under apps_shared/proof/
        # \u2014 only a violation if the row is production.
        if _row_is_production(row):
            violations.append(
                {
                    "control": CC_SHARED_03,
                    "contract_name": "SealedArtifact",
                    "source_path": source,
                    "span_id": row.get("span_id"),
                    "trace_id": row.get("trace_id"),
                    "environment": row.get("environment"),
                }
            )

    if rows_with_unknown_source:
        notes.append(
            f"{rows_with_unknown_source} SealedArtifact row(s) skipped: no "
            "source_path/file_path attribute \u2014 cannot confirm apps_shared/proof/ origin"
        )

    failure_reasons: tuple[str, ...] = ()
    if violations:
        failure_reasons = (
            f"{len(violations)} production SealedArtifact emission(s) "
            "originated from apps_shared/proof/ harness code",
        )

    return NegativeControlResult(
        control_id=CC_SHARED_03,
        passed=not violations,
        violation_count=len(violations),
        violations=tuple(violations),
        query_summary={
            "rows_scanned": rows_scanned,
            "rows_with_sealed_artifact": rows_with_sealed,
            "rows_with_unknown_source": rows_with_unknown_source,
        },
        failure_reasons=failure_reasons,
        notes=tuple(notes),
    )


__all__ = [
    "CC_EVAL_01",
    "CC_EVAL_02",
    "CC_SHARED_03",
    "CC_UW_02",
    "NegativeControlResult",
    "R3_CONTRACT_SET",
    "check_apps_eval_no_r3_contract_leak",
    "check_apps_shared_sealed_artifact_proof_only",
    "check_no_eval_of_evaluator_circularity",
    "check_underwriting_no_r3_contract_leak",
]
