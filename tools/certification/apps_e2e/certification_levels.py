"""CertificationLevel enum + pure compute_level() resolver.

Plan: apps-e2e-two-gate-certification-d8b3a1 §3 + amendment 4.

Per amendment 4: `certification_level` is ALWAYS computed by the verifier;
the bundle's self-declared `certification_level`, if present, is NEVER
trusted. The bundle emitter MAY include an advisory level for matrix
display, but strict mode recomputes from the bundle + spec + violations
and fails if the recomputed level is weaker than `SPINE_COMPLETE_CERTIFIED`
when `success=True`.

This module is pure logic: no I/O, no time-of-day reads except via the
explicit `now` parameter to compute_level. That makes the function
deterministically testable.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Iterable, Sequence

from tools.certification.apps_e2e.app_specs import (
    AppSpec,
    has_waiver,
)


class CertificationLevel(str, Enum):
    """The five canonical certification levels (plan §3).

    Ordering, weakest → strongest:
        EMITS_BUNDLE
        FAILS_CLOSED_WITH_GAPS
        SPINE_COMPLETE_CERTIFIED

    Plus two waiver levels that exit the runnable axis:
        WAIVED_SKELETON           (runnable=False)
        WAIVED_NOT_RUNTIME_APP    (certification_required=False)
    """

    EMITS_BUNDLE = "EMITS_BUNDLE"
    FAILS_CLOSED_WITH_GAPS = "FAILS_CLOSED_WITH_GAPS"
    SPINE_COMPLETE_CERTIFIED = "SPINE_COMPLETE_CERTIFIED"
    WAIVED_SKELETON = "WAIVED_SKELETON"
    WAIVED_NOT_RUNTIME_APP = "WAIVED_NOT_RUNTIME_APP"

    @classmethod
    def values(cls) -> frozenset[str]:
        return frozenset(member.value for member in cls)


# Subsets used by callers (reporting, gating).
PASSING_LEVELS: frozenset[CertificationLevel] = frozenset({
    CertificationLevel.SPINE_COMPLETE_CERTIFIED,
    CertificationLevel.WAIVED_SKELETON,
    CertificationLevel.WAIVED_NOT_RUNTIME_APP,
})

WAIVED_LEVELS: frozenset[CertificationLevel] = frozenset({
    CertificationLevel.WAIVED_SKELETON,
    CertificationLevel.WAIVED_NOT_RUNTIME_APP,
})


# ---------------------------------------------------------------------------
# runtime_mode_classification — derived from the bundle's existing runtime_mode
# field plus mock/fixture/synthetic detection signals. Strict mode allows
# ONLY "live_run". Plan §17 Q4 locks the enum here.
# ---------------------------------------------------------------------------

RUNTIME_MODE_LIVE_RUN = "live_run"
RUNTIME_MODE_DRY_RUN_SHORT_CIRCUIT = "dry_run_short_circuit"
RUNTIME_MODE_STANDALONE_ORCHESTRATOR = "standalone_orchestrator_pre_spine"
RUNTIME_MODE_FIXTURE = "fixture_runtime"
RUNTIME_MODE_MOCK = "mock_runtime"
RUNTIME_MODE_SKELETON_ONLY = "skeleton_only"
RUNTIME_MODE_UNKNOWN = "unknown"

VALID_RUNTIME_MODE_CLASSIFICATIONS: frozenset[str] = frozenset({
    RUNTIME_MODE_LIVE_RUN,
    RUNTIME_MODE_DRY_RUN_SHORT_CIRCUIT,
    RUNTIME_MODE_STANDALONE_ORCHESTRATOR,
    RUNTIME_MODE_FIXTURE,
    RUNTIME_MODE_MOCK,
    RUNTIME_MODE_SKELETON_ONLY,
    RUNTIME_MODE_UNKNOWN,
})

# The ONLY classification that is acceptable in strict mode.
APPROVED_LIVE_MODES: frozenset[str] = frozenset({RUNTIME_MODE_LIVE_RUN})


def classify_runtime_mode(bundle: dict) -> str:
    """Pure classifier: maps a bundle to a runtime_mode_classification value.

    Precedence (first match wins):
      1. mock_mode_detected=True       -> mock_runtime
      2. fixture_runtime_mode=True     -> fixture_runtime
      3. synthetic_trace_detected=True -> mock_runtime  (synthetic OTEL = fake)
      4. raw runtime_mode contains "skeleton" -> skeleton_only
      5. raw runtime_mode contains "dry_run"  -> dry_run_short_circuit
      6. raw runtime_mode == "standalone_orchestrator_pre_spine" -> same
      7. raw runtime_mode == "live_run" -> live_run
      8. else -> unknown

    NOTE: ``fixture_data_used=True`` is NOT a downgrade signal. Deterministic
    input data is allowed in strict mode (per amendment 3); only the
    *runtime mode* itself being a fixture is rejected.
    """
    if bundle.get("mock_mode_detected") is True:
        return RUNTIME_MODE_MOCK
    if bundle.get("fixture_runtime_mode") is True:
        return RUNTIME_MODE_FIXTURE
    if bundle.get("synthetic_trace_detected") is True:
        return RUNTIME_MODE_MOCK
    raw = str(bundle.get("runtime_mode") or "").strip()
    if not raw:
        return RUNTIME_MODE_UNKNOWN
    raw_l = raw.lower()
    if "skeleton" in raw_l:
        return RUNTIME_MODE_SKELETON_ONLY
    if "dry_run" in raw_l or raw_l == "dry-run":
        return RUNTIME_MODE_DRY_RUN_SHORT_CIRCUIT
    if raw == RUNTIME_MODE_STANDALONE_ORCHESTRATOR:
        return RUNTIME_MODE_STANDALONE_ORCHESTRATOR
    # Live-run aliases. The harness today emits "governed_spine_active"
    # when spine_status=="spine_active". That is semantically a live run.
    if raw in {RUNTIME_MODE_LIVE_RUN, "governed_spine_active"}:
        return RUNTIME_MODE_LIVE_RUN
    if raw == "fail_closed":
        return RUNTIME_MODE_UNKNOWN
    return RUNTIME_MODE_UNKNOWN


# ---------------------------------------------------------------------------
# Waiver validity — delegated to waivers.py (W2.2). Local alias preserved
# for backward-compat callers.
# ---------------------------------------------------------------------------

from tools.certification.apps_e2e.waivers import is_waiver_valid as _waiver_currently_valid  # noqa: E402


# ---------------------------------------------------------------------------
# Pure compute_level() — the verifier authority for certification_level.
# ---------------------------------------------------------------------------


# Violations that disqualify SPINE_COMPLETE_CERTIFIED but do not by themselves
# downgrade past FAILS_CLOSED_WITH_GAPS. Schema-level violations always
# downgrade to EMITS_BUNDLE.
_SCHEMA_RULE_PREFIXES: tuple[str, ...] = (
    "bundle_missing_required_field",
    "app_name_mismatch",
    "entrypoint_command_invalid",
    "timestamp_not_iso_utc",
    "harness_pass_false",
    "static_dag_proof_missing_on_disk",
    "static_dag_proof_sha_mismatch",
    "artifact_sha256_mismatch",
)


def _is_schema_violation(rule_id: str) -> bool:
    return any(rule_id.startswith(p) for p in _SCHEMA_RULE_PREFIXES)


def _gaps_are_well_formed(gaps: Iterable) -> bool:
    """blocking_gaps may be a list of strings (legacy) or list of dicts.
    Either form is well-formed; the verifier upgrades string gaps to dicts
    in W2.4. Empty iterables are NOT well-formed for this check (caller
    handles empty separately).
    """
    found_any = False
    for g in gaps:
        found_any = True
        if isinstance(g, str):
            if not g.strip():
                return False
        elif isinstance(g, dict):
            if not (g.get("rule_id") or g.get("stage") or g.get("reason")):
                return False
        else:
            return False
    return found_any


def compute_level(
    bundle: dict | None,
    spec: AppSpec,
    violations: Sequence[object] | None = None,
    *,
    now: datetime | None = None,
    required_receipts_present: bool | None = None,
) -> CertificationLevel:
    """Compute the certification level for ``spec`` from ``bundle`` evidence.

    The verifier ALWAYS calls this. Any ``certification_level`` field
    pre-existing on the bundle is IGNORED — that is the amendment-4
    invariant: bundle-declared level is never trusted.

    Parameters
    ----------
    bundle:
        The proof-bundle dict, or None when no bundle exists.
    spec:
        The AppSpec under evaluation.
    violations:
        Verifier-emitted violations. Each may be a Violation dataclass,
        a dict, or a string with a ``rule_id`` field/attr/start. None is
        treated as "no violations known".
    now:
        For testability. Defaults to ``datetime.now(timezone.utc)``.
    required_receipts_present:
        Optional precomputed signal from required_receipts.py (W2.1). When
        None, this function does NOT attempt to verify receipts on disk —
        it only checks the locally-derivable conditions. The full receipt-
        existence check lands in the verifier when W2.1 wires the resolver.

    Decision tree (first match wins):
        1. If runnable=False:
             - waiver currently valid -> WAIVED_SKELETON
             - else -> EMITS_BUNDLE  (verifier will separately raise
                                       a waiver_incomplete violation)
        2. If certification_required=False:
             - waiver currently valid -> WAIVED_NOT_RUNTIME_APP
             - else -> EMITS_BUNDLE
        3. If bundle is None or any schema violation fired -> EMITS_BUNDLE.
        4. If bundle.success is True AND no violations AND
              required_receipts_present is True (or unknown=None) AND
              classify_runtime_mode(bundle) is in APPROVED_LIVE_MODES AND
              blocking_gaps is empty
             -> SPINE_COMPLETE_CERTIFIED
        5. If bundle.success is False AND blocking_gaps is non-empty AND
              every gap is well-formed
             -> FAILS_CLOSED_WITH_GAPS
        6. Else -> EMITS_BUNDLE.
    """
    # 1 + 2 — waiver paths exit early.
    if not spec.runnable:
        if _waiver_currently_valid(spec, now):
            return CertificationLevel.WAIVED_SKELETON
        return CertificationLevel.EMITS_BUNDLE
    if not spec.certification_required:
        if _waiver_currently_valid(spec, now):
            return CertificationLevel.WAIVED_NOT_RUNTIME_APP
        return CertificationLevel.EMITS_BUNDLE

    # 3 — no bundle or schema-level violation -> bottom level.
    if bundle is None:
        return CertificationLevel.EMITS_BUNDLE
    viols = list(violations or [])
    for v in viols:
        rid = _violation_rule_id(v)
        if rid and _is_schema_violation(rid):
            return CertificationLevel.EMITS_BUNDLE

    success = bool(bundle.get("success"))
    gaps = bundle.get("blocking_gaps") or []
    rt_class = classify_runtime_mode(bundle)

    # 4 — full SPINE_COMPLETE_CERTIFIED criteria.
    if (
        success
        and not viols
        and not gaps
        and rt_class in APPROVED_LIVE_MODES
        and required_receipts_present is not False
    ):
        return CertificationLevel.SPINE_COMPLETE_CERTIFIED

    # 5 — FAILS_CLOSED_WITH_GAPS path: the bundle is honest about failing.
    if (not success) and gaps and _gaps_are_well_formed(gaps):
        return CertificationLevel.FAILS_CLOSED_WITH_GAPS

    # 6 — anything else (e.g. success=True with non-empty gaps, or fixture
    # runtime, or success=True with non-schema violations) drops to the
    # base level. The verifier emits the matching violations elsewhere
    # (S8 etc.); this function just refuses to award a stronger level.
    return CertificationLevel.EMITS_BUNDLE


def _violation_rule_id(v: object) -> str:
    """Extract a rule_id string from a Violation, dict, or str. Returns ''
    if not extractable.
    """
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    if isinstance(v, dict):
        return str(v.get("rule_id") or "")
    rid = getattr(v, "rule_id", "")
    return str(rid or "")


__all__ = [
    "CertificationLevel",
    "PASSING_LEVELS",
    "WAIVED_LEVELS",
    "RUNTIME_MODE_LIVE_RUN",
    "RUNTIME_MODE_DRY_RUN_SHORT_CIRCUIT",
    "RUNTIME_MODE_STANDALONE_ORCHESTRATOR",
    "RUNTIME_MODE_FIXTURE",
    "RUNTIME_MODE_MOCK",
    "RUNTIME_MODE_SKELETON_ONLY",
    "RUNTIME_MODE_UNKNOWN",
    "VALID_RUNTIME_MODE_CLASSIFICATIONS",
    "APPROVED_LIVE_MODES",
    "classify_runtime_mode",
    "compute_level",
]
