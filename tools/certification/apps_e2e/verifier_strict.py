"""Strict-mode extension for shared_verifier (W2.4).

Plan: apps-e2e-two-gate-certification-d8b3a1 §5.3, S1-S19.

The base `shared_verifier.verify_bundle()` covers schema-level rules and
some success-path checks. This module adds the strict-mode-only rules
that apply when `mode=strict`:

  - S4   runtime_mode_classification must be live_run; mock/fixture/synth rejected
  - S7   computed certification_level must equal SPINE_COMPLETE_CERTIFIED
  - S8   success=True legal only when level == SPINE_COMPLETE_CERTIFIED
  - S9   exit_x3 always required (verified via required_receipts)
  - S10  exhaust separately gated by l6_exhaust_required
  - S12  expected_execution_form != UNKNOWN
  - S13  form ↔ l3_path consistency
  - S15  waiver complete (when required)
  - S16  waiver expiry parses + future
  - N16  success=True with weaker computed level
  - N17  fixture_data_used + live_run = OK (positive control, no violation)
  - N18  fixture_runtime_mode = True is rejected
  - N19  declared *_ref absent from manifest
  - N20  duplicate single-occurrence artifact_kind in manifest

Returns Violation list (using shared_verifier.Violation) so the caller can
concat with the base verifier's output.
"""
from __future__ import annotations

from datetime import datetime
from typing import Sequence

from tools.certification.apps_e2e.app_specs import (
    AppSpec,
    EXECUTION_FORM_MANAGED_WORKFLOW,
    EXECUTION_FORM_SINGLE_STEP,
    EXECUTION_FORM_TERMINAL_SHORTCIRCUIT,
    EXECUTION_FORM_UNKNOWN,
    L3_PATH_BYPASSED,
    L3_PATH_RAN,
    L3_PATH_UNKNOWN,
)
from tools.certification.apps_e2e.artifact_kinds import (
    SINGLE_OCCURRENCE_KINDS,
    TRACE_SLOT_KINDS,
    ArtifactKind,
)
from tools.certification.apps_e2e.certification_levels import (
    APPROVED_LIVE_MODES,
    CertificationLevel,
    classify_runtime_mode,
    compute_level,
)
from tools.certification.apps_e2e.required_receipts import (
    required_receipts,
)
from tools.certification.apps_e2e.shared_verifier import Violation
from tools.certification.apps_e2e.waivers import (
    waiver_required,
    waiver_violation_rule_id,
)


def verify_strict_extras(
    bundle: dict | None,
    spec: AppSpec,
    base_violations: Sequence[Violation],
    *,
    now: datetime | None = None,
) -> list[Violation]:
    """Return the additional strict-mode violations on top of base rules.

    base_violations is the output of shared_verifier.verify_bundle(); it is
    NOT mutated. The combined set is returned by callers as
    list(base_violations) + verify_strict_extras(...).
    """
    extras: list[Violation] = []

    # ---- Waiver path (S15, S16) ----
    if waiver_required(spec):
        rid = waiver_violation_rule_id(spec, now=now)
        if rid:
            extras.append(Violation(
                rule_id=rid, stage="waiver",
                expected="waiver triple set + ISO-8601 UTC future expiry",
                observed=f"reason={spec.waiver_reason!r}, owner={spec.waiver_owner!r}, "
                         f"expiry={spec.waiver_expiry!r}",
            ))
        # Waived specs do not need bundle/cert checks below.
        return extras

    if not spec.runnable:
        return extras  # already handled via waiver path
    if not spec.certification_required:
        return extras

    # ---- S12 : execution_form != UNKNOWN under certification ----
    if spec.expected_execution_form == EXECUTION_FORM_UNKNOWN:
        extras.append(Violation(
            rule_id="execution_form_unknown_under_certification",
            stage="spec",
            expected="expected_execution_form ∈ {TERMINAL_SHORTCIRCUIT, SINGLE_STEP, MANAGED_WORKFLOW}",
            observed="UNKNOWN",
        ))

    # ---- S13 : form ↔ l3_path consistency ----
    if spec.expected_execution_form == EXECUTION_FORM_MANAGED_WORKFLOW \
       and spec.expected_l3_path != L3_PATH_RAN:
        extras.append(Violation(
            rule_id="execution_form_l3_path_inconsistent", stage="spec",
            expected="MANAGED_WORKFLOW requires expected_l3_path=RAN",
            observed=f"l3_path={spec.expected_l3_path}",
        ))
    if spec.expected_execution_form in (EXECUTION_FORM_TERMINAL_SHORTCIRCUIT, EXECUTION_FORM_SINGLE_STEP) \
       and spec.expected_l3_path != L3_PATH_BYPASSED:
        extras.append(Violation(
            rule_id="execution_form_l3_path_inconsistent", stage="spec",
            expected=f"{spec.expected_execution_form} requires expected_l3_path=BYPASSED",
            observed=f"l3_path={spec.expected_l3_path}",
        ))

    if bundle is None:
        extras.append(Violation(
            rule_id="bundle_missing", stage="bundle",
            expected="bundle file present",
            observed="absent",
        ))
        return extras

    # ---- S4 : runtime_mode_classification + fixture/mock/synthetic ----
    rt_class = bundle.get("runtime_mode_classification") or classify_runtime_mode(bundle)
    if rt_class not in APPROVED_LIVE_MODES:
        extras.append(Violation(
            rule_id="runtime_mode_not_in_approved_live_modes",
            stage="runtime_mode",
            expected=f"runtime_mode_classification ∈ {sorted(APPROVED_LIVE_MODES)}",
            observed=str(rt_class),
        ))
    # N18
    if bundle.get("fixture_runtime_mode") is True:
        extras.append(Violation(
            rule_id="fixture_runtime_mode_in_certified_bundle",
            stage="runtime_mode",
            expected="fixture_runtime_mode=False (deterministic input is OK; fake runtime is not)",
            observed="fixture_runtime_mode=True",
        ))
    if bundle.get("mock_mode_detected") is True:
        extras.append(Violation(
            rule_id="mock_mode_in_certified_bundle",
            stage="runtime_mode",
            expected="mock_mode_detected=False",
            observed="mock_mode_detected=True",
        ))
    if bundle.get("synthetic_trace_detected") is True:
        extras.append(Violation(
            rule_id="synthetic_trace_in_certified_bundle",
            stage="otel_or_runtime_trace",
            expected="synthetic_trace_detected=False",
            observed="synthetic_trace_detected=True",
        ))
    # N17 — fixture_data_used is INTENTIONALLY allowed: no violation emitted.

    # ---- S1, S2 : success + gaps ----
    if not bundle.get("success"):
        extras.append(Violation(
            rule_id="strict_success_required",
            stage="success",
            expected="success=True for certification_required apps",
            observed=f"success={bundle.get('success')}",
        ))
    gaps = bundle.get("blocking_gaps") or []
    if gaps:
        # If success=True with non-empty gaps, the underlying base verifier
        # also flags this; here we additionally treat it as a strict failure.
        extras.append(Violation(
            rule_id="blocking_gaps_nonempty_under_strict",
            stage="blocking_gaps",
            expected="empty list",
            observed=f"{len(gaps)} gap(s)",
        ))
    if bundle.get("success") and gaps:
        # N9 / classic invariant: success=True paired with blocking_gaps.
        extras.append(Violation(
            rule_id="success_true_with_nonempty_gaps",
            stage="success",
            expected="success=False when blocking_gaps non-empty",
            observed=f"success=True, gaps={len(gaps)}",
        ))

    # ---- S3 + N19 + S6.5 artifact-kind checks ----
    manifest_items = _resolve_manifest_items(bundle)
    items_by_field = _index_manifest_by_field(manifest_items)
    for req in required_receipts(spec):
        ref_value = bundle.get(req.ref_field)
        if not ref_value:
            extras.append(Violation(
                rule_id="required_receipt_missing",
                stage=req.ref_field,
                expected=f"non-null ref ({_describe_kind(req.expected_kind)})",
                observed="null",
            ))
            continue
        # N19 — declared ref must appear in artifact manifest
        if req.ref_field not in items_by_field or items_by_field[req.ref_field].get("ref") != ref_value:
            extras.append(Violation(
                rule_id="ref_missing_from_manifest",
                stage=req.ref_field,
                expected="declared ref appears in artifact_manifest with matching path",
                observed=f"ref={ref_value} not in manifest under field {req.ref_field}",
                artifact_ref=ref_value,
            ))
            continue
        # Artifact-kind binding (manifest row's kind matches expected)
        row = items_by_field[req.ref_field]
        kind_value = row.get("artifact_kind")
        if not req.kind_matches(kind_value):
            extras.append(Violation(
                rule_id="artifact_kind_mismatch",
                stage=req.ref_field,
                expected=_describe_kind(req.expected_kind),
                observed=f"artifact_kind={kind_value!r}",
                artifact_ref=ref_value,
            ))
        # Manifest run_id must equal bundle.run_id
        m_run_id = row.get("run_id")
        if m_run_id and m_run_id != bundle.get("run_id"):
            extras.append(Violation(
                rule_id="manifest_run_id_drift",
                stage=req.ref_field,
                expected=f"run_id={bundle.get('run_id')}",
                observed=f"manifest run_id={m_run_id}",
                artifact_ref=ref_value,
            ))

    # ---- N20 : duplicate single-occurrence kinds ----
    # ---- N4  : route_contract gets a kind-specific rule_id alias ----
    kind_counts: dict[str, int] = {}
    for item in manifest_items:
        kind = item.get("artifact_kind")
        if not kind:
            continue
        if not item.get("ref"):
            continue  # only count rows that point to a real artifact
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
    for kind_value, count in kind_counts.items():
        if count <= 1:
            continue
        # Is this a single-occurrence kind?
        try:
            kind_enum = ArtifactKind(kind_value)
        except ValueError:
            continue
        if kind_enum in SINGLE_OCCURRENCE_KINDS:
            extras.append(Violation(
                rule_id="duplicate_artifact_kind",
                stage="artifact_manifest",
                expected=f"exactly one manifest row with artifact_kind={kind_value}",
                observed=f"{count} rows",
            ))
            # N4 — route_contract is the canonical anti-fabrication target.
            # Emit a kind-specific rule_id so callers can grep for it.
            if kind_enum == ArtifactKind.route_contract:
                extras.append(Violation(
                    rule_id="duplicate_route_contract",
                    stage="artifact_manifest",
                    expected="exactly one manifest row with artifact_kind=route_contract",
                    observed=f"{count} rows",
                ))

    # ---- N2 : run_id mismatch with RouteContract ----
    # The bundle's run_id must equal the run_id embedded inside the
    # RouteContract artifact. Base verifier rule 10
    # (`run_id_threading_violation`) already covers this for any artifact;
    # here we add the strict-mode-specific rule_id named in plan §9 N2 so
    # the rule stays grep-able by name.
    route_ref_value = bundle.get("runtime_route_contract_ref")
    if route_ref_value:
        from pathlib import Path as _Path
        from tools.certification.apps_e2e.hash_utils import REPO_ROOT as _REPO_ROOT
        import json as _json
        rc_path = _REPO_ROOT / route_ref_value
        if rc_path.exists():
            try:
                rc_data = _json.loads(rc_path.read_text(encoding="utf-8"))
            except (OSError, _json.JSONDecodeError):
                rc_data = {}
            rc_run_id = rc_data.get("run_id")
            if rc_run_id is not None and rc_run_id != bundle.get("run_id"):
                extras.append(Violation(
                    rule_id="run_id_mismatch_with_route_contract",
                    stage="run_id",
                    expected=f"bundle.run_id == RouteContract.run_id (={rc_run_id})",
                    observed=f"bundle.run_id={bundle.get('run_id')}",
                    artifact_ref=route_ref_value,
                ))

    # ---- N6 : runtime_l3_receipt_ref present but static-DAG hash unbound ----
    # When expected_l3_path=RAN, the bundle MUST emit runtime_l3_receipt_ref
    # AND that receipt's static_dag_hash field MUST equal the bundle's
    # static_dag_sha256. Otherwise the L3 runtime path is unbound from the
    # static DAG that was supposed to drive it. Plan §9 N6.
    l3_ref_value = bundle.get("runtime_l3_receipt_ref")
    if l3_ref_value:
        from pathlib import Path as _Path
        from tools.certification.apps_e2e.hash_utils import REPO_ROOT as _REPO_ROOT
        import json as _json
        l3_path = _REPO_ROOT / l3_ref_value
        l3_data: dict = {}
        if l3_path.exists():
            try:
                l3_data = _json.loads(l3_path.read_text(encoding="utf-8"))
            except (OSError, _json.JSONDecodeError):
                l3_data = {}
        # Possible field names for the static-dag hash inside the L3 receipt.
        # Existing apps_rg-style receipts use `dag_sha256`; canonical name in
        # the plan is `static_dag_hash`. Accept either.
        l3_static_hash = l3_data.get("static_dag_hash") or l3_data.get("dag_sha256")
        bundle_static_sha = bundle.get("static_dag_sha256")
        bundle_static_ref = bundle.get("static_dag_ref")
        # The bundle declares TWO canonical static-DAG hashes:
        #   (a) bundle.static_dag_sha256 — hash of the on-disk cert-proof file
        #   (b) bundle.static_dag_proof_inline_summary.dag_sha256 — hash of
        #       the DAG YAML SSOT itself (what base verifier rule 11 uses)
        # Either is a legitimate binding target for the L3 runtime receipt;
        # N6 fires only if neither matches.
        inline_summary = bundle.get("static_dag_proof_inline_summary") or {}
        bundle_inline_sha = inline_summary.get("dag_sha256")
        accepted_hashes = {h for h in (bundle_static_sha, bundle_inline_sha) if h}
        if (not bundle_static_ref) or not accepted_hashes:
            extras.append(Violation(
                rule_id="runtime_l3_static_dag_hash_unbound",
                stage="L3_orchestrate",
                expected="runtime_l3_receipt_ref requires static_dag_ref + (static_dag_sha256 OR inline_summary.dag_sha256)",
                observed=f"static_dag_ref={bundle_static_ref!r}, static_dag_sha256={bundle_static_sha!r}, inline_summary.dag_sha256={bundle_inline_sha!r}",
                artifact_ref=l3_ref_value,
            ))
        elif l3_static_hash is None or l3_static_hash not in accepted_hashes:
            expected_str = " OR ".join(sorted(accepted_hashes))
            extras.append(Violation(
                rule_id="runtime_l3_static_dag_hash_unbound",
                stage="L3_orchestrate",
                expected=f"L3 receipt static_dag_hash in {{{expected_str}}}",
                observed=f"L3 receipt static_dag_hash={l3_static_hash!r}",
                artifact_ref=l3_ref_value,
            ))

    # ---- N7 : L6 exhaust emitted before Exit X3 ----
    # Plan §9 N7: rule_id `l6_emitted_before_exit`. Base verifier rule 15
    # has `l6_observed_before_exit` for the same condition; we emit the
    # plan-specified rule_id here in strict mode.
    exhaust_ref_value = bundle.get("runtime_exhaust_ref")
    exit_ref_value = bundle.get("runtime_exit_disposition_ref")
    if exhaust_ref_value and exit_ref_value:
        from pathlib import Path as _Path
        from tools.certification.apps_e2e.hash_utils import REPO_ROOT as _REPO_ROOT
        import json as _json
        ex_path = _REPO_ROOT / exhaust_ref_value
        exit_path = _REPO_ROOT / exit_ref_value
        if ex_path.exists() and exit_path.exists():
            try:
                ex_data = _json.loads(ex_path.read_text(encoding="utf-8"))
            except (OSError, _json.JSONDecodeError):
                ex_data = {}
            try:
                exit_data = _json.loads(exit_path.read_text(encoding="utf-8"))
            except (OSError, _json.JSONDecodeError):
                exit_data = {}
            # Accept multiple timestamp field names. Canonical ones used by
            # the existing apps_rg emitter:
            #   exhaust: observed_after_exit_at_utc, emitted_at_utc
            #   exit:    emitted_at_utc, finished_at_utc
            ex_ts = (
                ex_data.get("emitted_at_utc")
                or ex_data.get("observed_after_exit_at_utc")
                or ex_data.get("timestamp_utc")
            )
            exit_ts = (
                exit_data.get("emitted_at_utc")
                or exit_data.get("finished_at_utc")
                or exit_data.get("timestamp_utc")
            )
            if ex_ts and exit_ts and ex_ts < exit_ts:
                extras.append(Violation(
                    rule_id="l6_emitted_before_exit",
                    stage="L6_exhaust",
                    expected=f"exhaust timestamp >= exit timestamp ({exit_ts})",
                    observed=f"exhaust timestamp={ex_ts}",
                    artifact_ref=exhaust_ref_value,
                ))

    # ---- S7 + S8 + N16 : computed level invariant ----
    combined_violations = list(base_violations) + list(extras)
    computed = compute_level(
        bundle, spec,
        violations=combined_violations,
        now=now,
        required_receipts_present=_all_required_present(bundle, spec, manifest_items),
    )
    if computed != CertificationLevel.SPINE_COMPLETE_CERTIFIED:
        extras.append(Violation(
            rule_id="certification_level_below_certified",
            stage="certification_level",
            expected="SPINE_COMPLETE_CERTIFIED",
            observed=f"computed={computed.value}",
        ))
    if bundle.get("success") and computed != CertificationLevel.SPINE_COMPLETE_CERTIFIED:
        extras.append(Violation(
            rule_id="success_true_but_level_weaker_than_certified",
            stage="certification_level",
            expected="success=True implies computed certification_level=SPINE_COMPLETE_CERTIFIED",
            observed=f"success=True, computed={computed.value}",
        ))

    return extras


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_manifest_items(bundle: dict) -> list[dict]:
    """Best-effort manifest resolution.

    1. If the bundle's `artifact_manifest_ref` points to a JSON file, load it.
    2. Else fall back to constructing items from `run_info.artifacts[]` plus
       per-ref-field mapping.
    """
    from pathlib import Path

    from tools.certification.apps_e2e.hash_utils import REPO_ROOT
    import json as _json

    ref = bundle.get("artifact_manifest_ref")
    if ref:
        p = REPO_ROOT / ref
        if p.exists():
            try:
                manifest = _json.loads(p.read_text(encoding="utf-8"))
            except (OSError, _json.JSONDecodeError):
                manifest = None
            if isinstance(manifest, dict):
                items = manifest.get("items") or []
                if items:
                    return list(items)
    # Fallback — synthesize manifest items from run_info.artifacts[]
    run_info = bundle.get("run_info") or {}
    arts = list(run_info.get("artifacts") or [])
    return arts


def _index_manifest_by_field(items: list[dict]) -> dict[str, dict]:
    """Map ref_field -> manifest row. Falls back to `key` for legacy rows."""
    out: dict[str, dict] = {}
    for it in items:
        field = it.get("ref_field") or it.get("key")
        if field:
            out[field] = it
    return out


def _describe_kind(expected) -> str:
    if isinstance(expected, frozenset):
        return "{" + ", ".join(sorted(k.value for k in expected)) + "}"
    try:
        return str(expected.value)
    except AttributeError:
        return str(expected)


def _all_required_present(bundle: dict, spec: AppSpec, manifest_items: list[dict]) -> bool:
    """True iff every required receipt has a non-null ref + present manifest row."""
    items_by_field = _index_manifest_by_field(manifest_items)
    for req in required_receipts(spec):
        ref = bundle.get(req.ref_field)
        if not ref:
            return False
        if req.ref_field not in items_by_field:
            return False
    return True


__all__ = ["verify_strict_extras"]
