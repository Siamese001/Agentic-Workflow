"""Formal-exception per-app evidence extractor — Phase C.5.

Consumes ``NormalizedTraceRow`` rows (Phase C.2 output) and a formal-exception
``AppRouteContract`` (``evaluator_only`` or ``core_adjacent_utility``), then
reports compensating-control evidence for the three formal-exception apps:

- ``apps_eval``              — CC-EVAL-01, CC-EVAL-02 (CC-UW-01 style
                                positive evidence is not applicable here)
- ``apps_underwriting_ai``   — CC-UW-02 (CC-UW-01 positive regulated-decision
                                evidence is **not implemented** in Phase C.5
                                and is honestly reported as missing)
- ``apps_shared``            — CC-SHARED-03, CC-SHARED-05 (CC-SHARED-01/02/04
                                are static, not runtime-verifiable in C.5)

Design references
-----------------
- Phase C plan: ``docs/plans/runtime_cert_phase_c_trace_collector_plan.md``
- C.3 / C.4 extractors:  ``tools/runtime_cert/extractors/r3_evidence.py`` and
                         ``tools/runtime_cert/extractors/btc_evidence.py``
- B.4 helper:            ``system_learning/runtime_adg/formal_exception_evidence.py``
                         (``collect_cc_shared_05_evidence``, ``assert_cc_shared_05_passes``)
- B.5 helpers:           ``tools/runtime_cert/negative_controls.py``
                         (``check_no_eval_of_evaluator_circularity``,
                          ``check_apps_eval_no_r3_contract_leak``,
                          ``check_underwriting_no_r3_contract_leak``,
                          ``check_apps_shared_sealed_artifact_proof_only``)
- B.2 schema:            ``system_learning/runtime_adg/app_route_contracts.py``
                         (``build_formal_exception_contract``)
- B.3 hash:              ``system_learning/runtime_adg/manifest_hash.py``
- Matrix v2 §6:          ``docs/reference/runtime_certification/contract_span_binding_matrix.md``

What this module does
---------------------
- Validates the contract (``route_shape`` must be a formal-exception route;
  ``compensating_controls`` must be non-empty; ``formal_exception_reason_code``
  must be non-empty).
- Adapts the typed ``NormalizedTraceRow`` inputs into the ``Mapping[str, Any]``
  shape that the B.5 negative-control helpers consume.
- Dispatches to the implemented helpers per app.
- For compensating controls listed in the manifest but **not implemented**
  in Phase C.5, marks them missing with an honest, specific note — does
  NOT fake-pass them.
- Emits ``passed_formal_exception_observed=True`` **only** when every
  compensating control in the contract has implemented evidence AND
  passes. In Phase C.5 this is expected to be False for most apps.
- ``runtime_certification_status`` remains ``NOT_CERTIFIED`` — not promoted
  to ``FORMAL_EXCEPTION_VERIFIED``.

What this module does NOT do
----------------------------
- Does NOT certify any app.
- Does NOT promote ``runtime_certification_status``.
- Does NOT edit emitters, scanners, CI gates, or app behavior.
- Does NOT fake-pass unimplemented compensating controls.
- Does NOT filter rows before running circularity checks — they need the
  full batch (root-span analysis on the whole trace).
"""

from __future__ import annotations

# ADR-079 consumer mode declaration.
__adg_consumer_mode__ = "runtime_cert_read"

import dataclasses
import json
import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

from system_learning.runtime_adg.app_route_contracts import (
    AppRouteContract,
    RouteShape,
)
from system_learning.runtime_adg.formal_exception_evidence import (
    CC_SHARED_05_CONTROL_ID,
    collect_cc_shared_05_evidence,
)
from system_learning.runtime_adg.manifest_hash import compute_manifest_hash
from tools.runtime_cert.negative_controls import (
    CC_EVAL_01,
    CC_EVAL_02,
    CC_SHARED_03,
    CC_UW_02,
    check_apps_eval_no_r3_contract_leak,
    check_apps_shared_sealed_artifact_proof_only,
    check_no_eval_of_evaluator_circularity,
    check_underwriting_no_r3_contract_leak,
)
from tools.runtime_cert.runtime_adg_query_adapter import NOT_CERTIFIED
from tools.runtime_cert.trace_row_normalizer import NormalizedTraceRow

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Control IDs not yet implemented by any runtime helper. They remain in the
#: manifest (static compensating controls) but cannot be runtime-verified
#: by Phase C.5. Honest bookkeeping — NOT a fake-pass list.
_STATIC_SHARED_CONTROLS: Final[frozenset[str]] = frozenset(
    {"CC-SHARED-01", "CC-SHARED-02", "CC-SHARED-04"}
)
_STATIC_UW_CONTROLS: Final[frozenset[str]] = frozenset({"CC-UW-01"})

#: Formal-exception route shapes permitted for this extractor.
_FORMAL_EXCEPTION_ROUTES: Final[frozenset[RouteShape]] = frozenset(
    {RouteShape.evaluator_only, RouteShape.core_adjacent_utility}
)


# ---------------------------------------------------------------------------
# FormalControlEvidence — per-control evidence record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FormalControlEvidence:
    """Structured evidence for one compensating control.

    Attributes
    ----------
    control_id : str
        Control identifier (e.g. ``"CC-EVAL-01"``).
    observed : bool
        ``True`` if this control has an implemented runtime helper that
        actually ran on the input rows / environment. ``False`` when the
        control is listed in the manifest but no Phase-C.5 helper exists
        for it — this is honest, not fake-pass.
    passed : bool
        ``True`` iff ``observed`` AND the helper's own ``passed`` is True.
        Always False when ``observed`` is False.
    violation_count : int
        Number of violations recorded by the underlying helper. 0 when
        not observed or when the helper returned no violations.
    violations : tuple[Mapping[str, Any], ...]
        Raw violation records (shape defined by the underlying helper).
    failure_reasons : tuple[str, ...]
        Human-readable failure explanations.
    notes : str
        Free-form notes. For unimplemented controls, explains why the
        helper is missing.
    """

    control_id: str
    observed: bool
    passed: bool
    violation_count: int
    violations: tuple[Mapping[str, Any], ...]
    failure_reasons: tuple[str, ...]
    notes: str

    def __post_init__(self) -> None:
        if not self.observed and self.passed:
            raise ValueError(
                f"FormalControlEvidence({self.control_id!r}): passed=True with "
                "observed=False is not allowed (would be a fake-pass)"
            )
        if self.violation_count != len(self.violations):
            raise ValueError(
                f"FormalControlEvidence({self.control_id!r}): violation_count="
                f"{self.violation_count} does not match len(violations)="
                f"{len(self.violations)}"
            )

    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable representation."""
        return {
            "control_id": self.control_id,
            "observed": self.observed,
            "passed": self.passed,
            "violation_count": self.violation_count,
            "violations": [dict(v) for v in self.violations],
            "failure_reasons": list(self.failure_reasons),
            "notes": self.notes,
        }


# ---------------------------------------------------------------------------
# FormalExceptionEvidenceReport — top-level report
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FormalExceptionEvidenceReport:
    """Per-app formal-exception evidence report.

    ``runtime_certification_status`` is always ``NOT_CERTIFIED`` —
    ``__post_init__`` raises ``ValueError`` on any other value.

    ``passed_formal_exception_observed=True`` signals that every
    compensating control listed in the contract has an implemented helper
    that passed. It does NOT promote the certification status.
    """

    app_name: str
    route_shape: str
    manifest_hash: str
    static_runtime_mode: str
    formal_exception_reason_code: str
    compensating_controls: tuple[str, ...]
    runtime_certification_status: str
    controls_evidence: tuple[FormalControlEvidence, ...]
    missing_controls: tuple[str, ...]
    failed_controls: tuple[str, ...]
    passed_formal_exception_observed: bool
    failure_reasons: tuple[str, ...]
    notes: str

    def __post_init__(self) -> None:
        if self.runtime_certification_status != NOT_CERTIFIED:
            raise ValueError(
                f"FormalExceptionEvidenceReport.runtime_certification_status must be "
                f"{NOT_CERTIFIED!r}; got {self.runtime_certification_status!r}. "
                "Phase C never writes a certification verdict."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "route_shape": self.route_shape,
            "manifest_hash": self.manifest_hash,
            "static_runtime_mode": self.static_runtime_mode,
            "formal_exception_reason_code": self.formal_exception_reason_code,
            "compensating_controls": list(self.compensating_controls),
            "runtime_certification_status": self.runtime_certification_status,
            "controls_evidence": [c.to_dict() for c in self.controls_evidence],
            "missing_controls": list(self.missing_controls),
            "failed_controls": list(self.failed_controls),
            "passed_formal_exception_observed": self.passed_formal_exception_observed,
            "failure_reasons": list(self.failure_reasons),
            "notes": self.notes,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# Public extractor
# ---------------------------------------------------------------------------


def extract_formal_exception_evidence(
    rows: Iterable[NormalizedTraceRow],
    contract: AppRouteContract,
    *,
    cc_shared_env: Mapping[str, str] | None = None,
) -> FormalExceptionEvidenceReport:
    """Build a ``FormalExceptionEvidenceReport`` from a row batch + contract.

    Parameters
    ----------
    rows:
        Iterable of ``NormalizedTraceRow`` instances. Rows are NOT filtered
        by ``app_name`` before circularity checks — cross-app evidence is
        semantically meaningful for CC-EVAL-01 (evaluator-of-evaluator).
    contract:
        A formal-exception ``AppRouteContract`` with
        ``route_shape in {evaluator_only, core_adjacent_utility}``,
        non-empty ``compensating_controls``, and non-empty
        ``formal_exception_reason_code``.
    cc_shared_env:
        Optional environment mapping forwarded to
        ``collect_cc_shared_05_evidence`` for apps_shared. Enables
        deterministic testing of env-gated CC-SHARED-05 behavior.

    Returns
    -------
    FormalExceptionEvidenceReport
        Structured report. ``runtime_certification_status`` is always
        ``NOT_CERTIFIED``.

    Raises
    ------
    ValueError
        If the contract is not a valid formal-exception shape.
    """
    # -- Contract validation -------------------------------------------------
    if contract.route_shape not in _FORMAL_EXCEPTION_ROUTES:
        raise ValueError(
            f"extract_formal_exception_evidence: contract.route_shape must be "
            f"one of {{evaluator_only, core_adjacent_utility}}; got "
            f"{contract.route_shape.value!r} for app {contract.app_name!r}."
        )
    if not contract.formal_exception_reason_code:
        raise ValueError(
            f"extract_formal_exception_evidence: contract "
            f"({contract.app_name!r}) has empty formal_exception_reason_code; "
            "this is required for formal-exception contracts."
        )
    if not contract.compensating_controls:
        raise ValueError(
            f"extract_formal_exception_evidence: contract "
            f"({contract.app_name!r}) has empty compensating_controls; "
            "formal-exception contracts must list at least one control."
        )
    if not contract.app_name.startswith("apps_"):
        raise ValueError(
            f"extract_formal_exception_evidence: contract.app_name must start "
            f"with 'apps_'; got {contract.app_name!r}."
        )

    # -- Resolve manifest hash ----------------------------------------------
    resolved_manifest_hash, manifest_note = _resolve_manifest_hash(contract)
    notes_parts: list[str] = []
    if manifest_note:
        notes_parts.append(manifest_note)

    # -- Materialize rows and adapt to mapping shape for B.5 helpers --------
    rows_list = list(rows)
    row_mappings = [_to_mapping(r) for r in rows_list]

    # -- Dispatch by app_name -----------------------------------------------
    controls_evidence: list[FormalControlEvidence] = []
    app = contract.app_name

    # Build a lookup so we can process each manifest-listed control
    # regardless of order; avoids missing any control the manifest lists.
    evidence_by_id: dict[str, FormalControlEvidence] = {}

    if app == "apps_eval":
        evidence_by_id[CC_EVAL_01] = _wrap_negative_control(
            check_no_eval_of_evaluator_circularity(row_mappings),
        )
        evidence_by_id[CC_EVAL_02] = _wrap_negative_control(
            check_apps_eval_no_r3_contract_leak(row_mappings),
        )
    elif app == "apps_underwriting_ai":
        evidence_by_id[CC_UW_02] = _wrap_negative_control(
            check_underwriting_no_r3_contract_leak(row_mappings),
        )
        # CC-UW-01 (positive regulated-decision evidence) has no helper yet.
    elif app == "apps_shared":
        evidence_by_id[CC_SHARED_03] = _wrap_negative_control(
            check_apps_shared_sealed_artifact_proof_only(row_mappings),
        )
        shared05 = collect_cc_shared_05_evidence(env=cc_shared_env)
        evidence_by_id[CC_SHARED_05_CONTROL_ID] = _wrap_shared05(shared05)
    else:
        notes_parts.append(
            f"app_name={app!r} has no implemented formal-exception helpers "
            "in Phase C.5; all listed controls will be marked missing."
        )

    # -- Build per-control records for every manifest-listed control --------
    missing_controls: list[str] = []
    failed_controls: list[str] = []
    all_failure_reasons: list[str] = []

    for ctrl_id in contract.compensating_controls:
        if ctrl_id in evidence_by_id:
            rec = evidence_by_id[ctrl_id]
        else:
            rec = _unimplemented_control(ctrl_id, app)
        controls_evidence.append(rec)

        if not rec.observed:
            missing_controls.append(ctrl_id)
        elif not rec.passed:
            failed_controls.append(ctrl_id)

        all_failure_reasons.extend(rec.failure_reasons)

    # -- Warn about any evidence we collected that is NOT in the manifest ---
    manifest_set = set(contract.compensating_controls)
    extra = [cid for cid in evidence_by_id if cid not in manifest_set]
    if extra:
        notes_parts.append(
            f"Helpers produced evidence for control(s) not listed in the "
            f"manifest: {sorted(extra)}. These are omitted from the report."
        )

    # -- Compute top-level pass flag ----------------------------------------
    passed = (
        len(controls_evidence) == len(contract.compensating_controls)
        and not missing_controls
        and not failed_controls
    )

    notes = "  ".join(notes_parts) if notes_parts else ""

    return FormalExceptionEvidenceReport(
        app_name=contract.app_name,
        route_shape=contract.route_shape.value,
        manifest_hash=resolved_manifest_hash,
        static_runtime_mode=contract.static_runtime_mode,
        formal_exception_reason_code=contract.formal_exception_reason_code,
        compensating_controls=contract.compensating_controls,
        runtime_certification_status=NOT_CERTIFIED,
        controls_evidence=tuple(controls_evidence),
        missing_controls=tuple(missing_controls),
        failed_controls=tuple(failed_controls),
        passed_formal_exception_observed=passed,
        failure_reasons=tuple(dict.fromkeys(all_failure_reasons)),
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _to_mapping(row: NormalizedTraceRow) -> dict[str, Any]:
    """Convert a ``NormalizedTraceRow`` dataclass into a plain dict.

    The B.5 negative-control helpers consume ``Iterable[Mapping[str, Any]]``,
    so we adapt here. ``dataclasses.asdict`` deep-copies nested containers
    (e.g. the ``attributes`` dict), which matches the helpers' assumption
    that rows are plain dicts.
    """
    return dataclasses.asdict(row)


def _wrap_negative_control(result: Any) -> FormalControlEvidence:
    """Wrap a ``NegativeControlResult`` into a ``FormalControlEvidence`` record."""
    return FormalControlEvidence(
        control_id=result.control_id,
        observed=True,
        passed=bool(result.passed),
        violation_count=int(result.violation_count),
        violations=tuple(dict(v) for v in result.violations),
        failure_reasons=tuple(result.failure_reasons),
        notes="  ".join(result.notes) if result.notes else "",
    )


def _wrap_shared05(evidence: Any) -> FormalControlEvidence:
    """Wrap a ``SharedShimEvidence`` record into a ``FormalControlEvidence``.

    CC-SHARED-05 does NOT produce violation rows — it produces an
    environment/sys.modules assessment. We map its ``passed`` directly and
    surface its ``failure_reasons`` and ``notes``.
    """
    return FormalControlEvidence(
        control_id=evidence.control_id,
        observed=True,
        passed=bool(evidence.passed),
        violation_count=0,
        violations=(),
        failure_reasons=tuple(evidence.failure_reasons),
        notes="  ".join(evidence.notes) if evidence.notes else "",
    )


def _unimplemented_control(control_id: str, app_name: str) -> FormalControlEvidence:
    """Build an honest 'not implemented' evidence record — no fake-pass."""
    if app_name == "apps_shared" and control_id in _STATIC_SHARED_CONTROLS:
        note = (
            f"{control_id}: static compensating control not runtime-verifiable "
            "in Phase C.5 (manifest-reviewed only)."
        )
    elif app_name == "apps_underwriting_ai" and control_id in _STATIC_UW_CONTROLS:
        note = (
            f"{control_id}: positive regulated-decision evidence not implemented "
            "in Phase C.5 (requires positive-evidence helper, not a negative "
            "control)."
        )
    else:
        note = (
            f"{control_id}: no Phase-C.5 runtime helper implemented for this "
            f"compensating control on {app_name!r}."
        )

    reason = f"{control_id}: no runtime evidence helper implemented (Phase C.5)"

    return FormalControlEvidence(
        control_id=control_id,
        observed=False,
        passed=False,
        violation_count=0,
        violations=(),
        failure_reasons=(reason,),
        notes=note,
    )


def _resolve_manifest_hash(contract: AppRouteContract) -> tuple[str, str]:
    """Return ``(hash_str, note)`` — mirrors C.3 / C.4 behavior."""
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
    "FormalControlEvidence",
    "FormalExceptionEvidenceReport",
    "extract_formal_exception_evidence",
]
