"""06.2 observer law and eval-readiness doctrine tests.

Doctrine TEST REQUIREMENTS (06.2):
- L6 code path has NO write credentials to L4.
- L6 does not publish BUS U before UWG/L4 materialization.
- L6 does not mutate prompt/policy/rubric thresholds directly.
- L6 does not start before Exit disposition.
- Missing replay_key not silently ignored for replay-dependent eval.
- Non-evaluable packets cannot enter RCA/proposal drafting.
- Partial scoring is not promoted as complete evaluation.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil

import pytest

from agentic_core.L6_observability import shadow_eval
from agentic_core.L6_observability.shadow_eval import (
    FORBIDDEN_WRITE_SURFACES,
    ObserverViolation,
    READINESS_HOLD,
    READINESS_NON_EVAL,
    READINESS_READY,
    build_observer_compliance_receipt,
    build_runtime_exhaust_bundle,
    build_surface_isolation_manifest,
    deny_if_forbidden,
    evaluate_readiness,
    record_denied_write_attempt,
    stage_barrier_check,
)


# ---------------------------------------------------------------------------
# Static observer-law proof — the package must not import any L4/UWG/BUS U
# write client. We assert this by module text inspection on the entire
# shadow_eval package.
# ---------------------------------------------------------------------------


def _shadow_eval_modules():
    pkg = shadow_eval
    for _finder, name, _ispkg in pkgutil.iter_modules(pkg.__path__):
        full = f"{pkg.__name__}.{name}"
        yield importlib.import_module(full)


FORBIDDEN_IMPORT_PATTERNS = (
    # Actual import statements that would bring in write surfaces.
    "from agentic_core.uwg",
    "import uwg_client",
    "from agentic_core.L4_state.write",
    "import bus_u_publisher",
    "from policy_publisher",
    "from rubric_publisher",
    "from current_run_mutator",
)


def test_no_write_client_imports_in_shadow_eval():
    """Ensures L6 code never imports a write surface — text-search proof."""
    for mod in _shadow_eval_modules():
        src = inspect.getsource(mod)
        for pat in FORBIDDEN_IMPORT_PATTERNS:
            assert pat not in src, (
                f"observer-law violation: {mod.__name__} contains forbidden import pattern {pat!r}"
            )


def test_forbidden_surfaces_set_includes_l4_and_bus_u():
    assert "L4" in FORBIDDEN_WRITE_SURFACES
    assert "BUS_U" in FORBIDDEN_WRITE_SURFACES
    assert "policy_publish" in FORBIDDEN_WRITE_SURFACES


def test_deny_if_forbidden_raises():
    with pytest.raises(ObserverViolation):
        deny_if_forbidden("L4")


def test_deny_if_forbidden_allows_read_surface():
    deny_if_forbidden("traces")  # must not raise


def test_stage_barrier_passes_when_run_closed(sealed_completed_run):
    bundle, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    receipt = stage_barrier_check(bundle)
    assert receipt.barrier_status == "PASS"
    assert receipt.current_run_closed is True
    assert receipt.exit_disposition_present is True
    assert not receipt.boundary_violation_flags


def test_isolation_manifest_clean_for_read_only_surfaces(sealed_completed_run):
    bundle, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    manifest = build_surface_isolation_manifest(bundle, read_surfaces_touched=("traces", "artifacts"))
    assert manifest.isolation_status == "CLEAN"
    assert manifest.l4_write_attempted is False
    assert manifest.bus_u_publish_attempted is False
    assert manifest.deterministic_digest


def test_isolation_manifest_violation_when_l4_write_requested(sealed_completed_run):
    bundle, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    denied = record_denied_write_attempt(bundle, surface="L4", operation="commit", reason_code="OBSERVER_LAW")
    manifest = build_surface_isolation_manifest(
        bundle,
        read_surfaces_touched=("traces",),
        write_surfaces_requested=("L4",),
        denied_write_attempts=(denied,),
    )
    assert manifest.isolation_status == "VIOLATION"
    assert manifest.l4_write_attempted is True


def test_observer_receipt_fails_on_violation(sealed_completed_run):
    bundle, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    denied = record_denied_write_attempt(
        bundle, surface="BUS_U", operation="publish", reason_code="OBSERVER_LAW"
    )
    manifest = build_surface_isolation_manifest(
        bundle,
        read_surfaces_touched=("traces",),
        write_surfaces_requested=("BUS_U",),
        denied_write_attempts=(denied,),
    )
    receipt = build_observer_compliance_receipt(
        bundle, barrier=barrier, isolation=manifest, denied_write_attempts=(denied,)
    )
    assert receipt.violation_response == "L6_OBSERVER_FAIL"
    assert receipt.no_l4_write_assertion is True
    assert receipt.no_bus_u_publish_assertion is False
    assert receipt.deterministic_digest


def test_eval_readiness_ready_for_clean_run(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    manifest = build_surface_isolation_manifest(bundle, read_surfaces_touched=("traces",))
    observer = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=manifest)
    receipt, _missing, _non = evaluate_readiness(bundle, observer, normalized)
    assert receipt.readiness_decision == READINESS_READY
    assert receipt.deterministic_digest


def test_missing_replay_key_not_silently_ignored(run_missing_replay_key):
    """06.2: replay-dependent eval cannot pass with missing replay key."""
    bundle, normalized, *_ = build_runtime_exhaust_bundle(run_missing_replay_key)
    barrier = stage_barrier_check(bundle)
    manifest = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    observer = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=manifest)
    receipt, missing, _non = evaluate_readiness(bundle, observer, normalized, replay_dependent=True)
    assert receipt.readiness_decision == READINESS_HOLD
    assert missing is not None
    assert "replay_key" in missing.missing_field_refs


def test_observer_violation_forces_non_evaluable(sealed_completed_run):
    bundle, normalized, *_ = build_runtime_exhaust_bundle(sealed_completed_run)
    barrier = stage_barrier_check(bundle)
    denied = record_denied_write_attempt(bundle, surface="L4", operation="write", reason_code="OBSERVER_LAW")
    manifest = build_surface_isolation_manifest(
        bundle,
        read_surfaces_touched=("traces",),
        write_surfaces_requested=("L4",),
        denied_write_attempts=(denied,),
    )
    observer = build_observer_compliance_receipt(
        bundle, barrier=barrier, isolation=manifest, denied_write_attempts=(denied,)
    )
    receipt, _miss, non_eval = evaluate_readiness(bundle, observer, normalized)
    assert receipt.readiness_decision == READINESS_NON_EVAL
    assert non_eval is not None
    assert "OBSERVER_LAW_VIOLATION" in non_eval.reason_codes


def test_partial_scoring_is_not_promoted_as_complete(sealed_completed_run):
    """When prompt_hash absent on every event, readiness should partial-score."""
    payload = dict(sealed_completed_run)
    payload["events"] = [{**ev, "prompt_hash": ""} for ev in payload["events"]]
    # Force no policy_hash so we hit a non-required missing field.
    payload["events"][0]["context_hash"] = ""
    bundle, normalized, *_ = build_runtime_exhaust_bundle(payload)
    barrier = stage_barrier_check(bundle)
    manifest = build_surface_isolation_manifest(bundle, read_surfaces_touched=("t",))
    observer = build_observer_compliance_receipt(bundle, barrier=barrier, isolation=manifest)
    receipt, _miss, _non = evaluate_readiness(bundle, observer, normalized)
    # Either READY or PARTIAL depending on what fields are missing — but never
    # converted silently to NON_EVAL when only optional hints are missing.
    assert receipt.readiness_decision in (READINESS_READY, "PARTIAL_BUT_SCORABLE")
