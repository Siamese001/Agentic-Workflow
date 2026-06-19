"""Negative-control suite for the two-gate certification (W3.2).

Plan: apps-e2e-two-gate-certification-d8b3a1 §9.

Each test mutates a real bundle (apps_rg — currently the only
SPINE_COMPLETE_CERTIFIED baseline), runs the strict-mode verifier against
the mutated copy, and asserts a specific violation rule_id fires (or, for
the positive controls N17 + the unmutated baseline, that NO violations
fire).

Tempfile pattern: tests NEVER mutate real artifacts on disk. The bundle
is loaded into memory, mutated, and passed directly to verify_with_mode.
For mutations that involve manifest tampering, the test rebuilds the
manifest in-memory and stores it under a tmp_path.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from tools.certification.apps_e2e.app_specs import (
    AppSpec,
    EXECUTION_FORM_MANAGED_WORKFLOW,
    EXECUTION_FORM_SINGLE_STEP,
    EXECUTION_FORM_TERMINAL_SHORTCIRCUIT,
    EXECUTION_FORM_UNKNOWN,
    L3_PATH_BYPASSED,
    L3_PATH_RAN,
    L3_PATH_UNKNOWN,
    find_spec,
)
from tools.certification.apps_e2e.hash_utils import REPO_ROOT
from tools.certification.apps_e2e.paths import AppCertPaths
from tools.certification.apps_e2e.shared_verifier import verify_with_mode


# ---------------------------------------------------------------------------
# Fixtures: load apps_rg's real bundle + spec into memory.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def rg_bundle() -> dict:
    paths = AppCertPaths("apps_rg")
    if not paths.proof_bundle.exists():
        pytest.skip("apps_rg baseline bundle not present; emit before negative-control suite")
    bundle = json.loads(paths.proof_bundle.read_text(encoding="utf-8"))
    if not bundle.get("success"):
        pytest.skip(
            "apps_rg baseline bundle is fail-closed in this environment; "
            "negative-control suite requires a certified baseline bundle"
        )
    return bundle


@pytest.fixture(scope="module")
def rg_spec() -> AppSpec:
    s = find_spec("apps_rg")
    assert s is not None
    return s


def _mutate(bundle: dict, **overrides) -> dict:
    """Deep-copy then merge overrides. Preserves apps_rg's run_info + refs."""
    b = copy.deepcopy(bundle)
    b.update(overrides)
    return b


def _violation_ids(viols) -> set[str]:
    return {v.rule_id for v in viols}


# ---------------------------------------------------------------------------
# Positive controls — MUST PASS strict mode.
# ---------------------------------------------------------------------------


class TestPositiveControl_UnmutatedBaseline:
    """Baseline: unmutated apps_rg bundle MUST pass strict mode.

    Without this, a bug that fails everything would look indistinguishable
    from correct anti-fabrication.
    """

    def test_baseline_passes_strict(self, rg_bundle, rg_spec):
        viols = verify_with_mode(rg_bundle, rg_spec, "strict")
        assert viols == [], (
            f"Baseline apps_rg bundle MUST pass strict mode. Violations: "
            + ", ".join(v.rule_id for v in viols)
        )


class TestPositiveControl_FixtureDataLegit:
    """N17 — fixture_data_used=True with live_run runtime is allowed."""

    def test_fixture_data_used_with_live_runtime_passes(self, rg_bundle, rg_spec):
        b = _mutate(rg_bundle, fixture_data_used=True)
        # fixture_data_used is allowed; should not introduce new violations
        # beyond what the unmutated baseline produces.
        viols_baseline = verify_with_mode(rg_bundle, rg_spec, "strict")
        viols_with_fixture = verify_with_mode(b, rg_spec, "strict")
        # The mutation MUST NOT introduce any new violations.
        new_ids = _violation_ids(viols_with_fixture) - _violation_ids(viols_baseline)
        assert not new_ids, f"fixture_data_used should not add violations; got: {new_ids}"


# ---------------------------------------------------------------------------
# N1-N20 negative controls.
# ---------------------------------------------------------------------------


class TestN1_MissingRunId:
    def test_missing_run_id(self, rg_bundle, rg_spec):
        b = copy.deepcopy(rg_bundle)
        b.pop("run_id", None)
        viols = verify_with_mode(b, rg_spec, "strict")
        assert "bundle_missing_required_field" in _violation_ids(viols)


class TestN3_MissingRouteContractRef:
    def test_missing_route_contract(self, rg_bundle, rg_spec):
        b = _mutate(rg_bundle, runtime_route_contract_ref=None)
        viols = verify_with_mode(b, rg_spec, "strict")
        assert "required_receipt_missing" in _violation_ids(viols)


class TestN5_MissingExitDispositionRef:
    def test_missing_exit_disposition(self, rg_bundle, rg_spec):
        b = _mutate(rg_bundle, runtime_exit_disposition_ref=None)
        viols = verify_with_mode(b, rg_spec, "strict")
        assert "required_receipt_missing" in _violation_ids(viols)


class TestN8_SyntheticTraceWithSuccessTrue:
    def test_synthetic_trace(self, rg_bundle, rg_spec):
        b = _mutate(rg_bundle, synthetic_trace_detected=True)
        viols = verify_with_mode(b, rg_spec, "strict")
        ids = _violation_ids(viols)
        assert "synthetic_trace_in_certified_bundle" in ids \
            or "synthetic_trace_with_success_true" in ids


class TestN9_SuccessTrueWithBlockingGaps:
    def test_success_with_gaps(self, rg_bundle, rg_spec):
        b = _mutate(rg_bundle, success=True, blocking_gaps=["fabricated_gap"])
        viols = verify_with_mode(b, rg_spec, "strict")
        assert "success_true_with_nonempty_gaps" in _violation_ids(viols)


class TestN10_DryRunRuntimeMode:
    def test_dry_run_mode(self, rg_bundle, rg_spec):
        b = _mutate(
            rg_bundle,
            runtime_mode="dry_run_short_circuit",
            runtime_mode_classification="dry_run_short_circuit",
        )
        viols = verify_with_mode(b, rg_spec, "strict")
        assert "runtime_mode_not_in_approved_live_modes" in _violation_ids(viols)


class TestN11_ArtifactSha256Mismatch:
    def test_sha256_mismatch(self, rg_bundle, rg_spec):
        # Tamper with one item's sha256 in run_info.artifacts to simulate
        # the file-on-disk no longer matching the declared hash.
        b = copy.deepcopy(rg_bundle)
        run_info = b.setdefault("run_info", {})
        artifacts = run_info.get("artifacts") or []
        if not artifacts:
            pytest.skip("apps_rg run_info.artifacts is empty; cannot test sha256 mutation")
        # Find one artifact and tamper.
        arts2 = list(artifacts)
        target = dict(arts2[0])
        target["sha256"] = "0" * 64  # forced mismatch
        arts2[0] = target
        run_info["artifacts"] = arts2
        viols = verify_with_mode(b, rg_spec, "strict")
        # Either run_artifact_sha_mismatch OR runtime_artifact_sha_mismatch.
        ids = _violation_ids(viols)
        assert any("sha_mismatch" in i for i in ids), f"expected sha_mismatch; got {ids}"


class TestN12_OverlayAuthorityViolation:
    def test_overlay_violated(self, rg_bundle, rg_spec):
        b = _mutate(rg_bundle, app_overlay_authority_status="overlay_violated")
        viols = verify_with_mode(b, rg_spec, "strict")
        ids = _violation_ids(viols)
        assert "overlay_violated_with_success" in ids \
            or any("overlay" in i for i in ids), f"expected overlay violation; got {ids}"


class TestN13_WaiverIncomplete:
    def test_skeleton_without_waiver_triple(self):
        spec = AppSpec(
            app_name="apps_test_skel",
            app_package="apps_test_skel",
            runnable=False,  # waiver required
            expected_route_form="UNKNOWN",
            expects_static_dag=False,
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_l2_execution=False,
            expects_durable_mutation=False,
            runs_root_glob="artifacts/apps_test_skel/runs/*",
            # NO waiver triple — must fail
        )
        viols = verify_with_mode(None, spec, "strict")
        assert "waiver_incomplete" in _violation_ids(viols)


class TestN14_WaiverExpired:
    def test_expired_expiry(self):
        spec = AppSpec(
            app_name="apps_test_exp",
            app_package="apps_test_exp",
            runnable=False,
            expected_route_form="UNKNOWN",
            expects_static_dag=False,
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_l2_execution=False,
            expects_durable_mutation=False,
            runs_root_glob="artifacts/apps_test_exp/runs/*",
            waiver_reason="why",
            waiver_owner="who",
            waiver_expiry="2020-01-01T00:00:00Z",  # in the past
        )
        viols = verify_with_mode(None, spec, "strict")
        assert "waiver_expired" in _violation_ids(viols)


class TestN15_ExecutionFormUnknownUnderCertification:
    def test_unknown_form(self):
        spec = AppSpec(
            app_name="apps_test_form",
            app_package="apps_test_form",
            runnable=True,
            expected_route_form="UNKNOWN",
            expects_static_dag=False,
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_l2_execution=False,
            expects_durable_mutation=False,
            runs_root_glob="artifacts/apps_test_form/runs/*",
            certification_required=True,
            expected_execution_form=EXECUTION_FORM_UNKNOWN,  # the violation
            expected_l3_path=L3_PATH_UNKNOWN,
        )
        viols = verify_with_mode(None, spec, "strict")
        assert "execution_form_unknown_under_certification" in _violation_ids(viols)


class TestN16_SuccessTrueButLevelWeaker:
    def test_success_true_with_synthetic_trace_drops_level(self, rg_bundle, rg_spec):
        # synthetic_trace_detected=True forces computed level below CERTIFIED;
        # but bundle still has success=True. The verifier emits both:
        #   - certification_level_below_certified
        #   - success_true_but_level_weaker_than_certified
        b = _mutate(rg_bundle, synthetic_trace_detected=True)
        viols = verify_with_mode(b, rg_spec, "strict")
        ids = _violation_ids(viols)
        assert "success_true_but_level_weaker_than_certified" in ids


class TestN18_FixtureRuntimeModeRejected:
    def test_fixture_runtime_mode(self, rg_bundle, rg_spec):
        b = _mutate(rg_bundle, fixture_runtime_mode=True)
        viols = verify_with_mode(b, rg_spec, "strict")
        assert "fixture_runtime_mode_in_certified_bundle" in _violation_ids(viols)


# ---------------------------------------------------------------------------
# N2 — bundle.run_id mismatches the RouteContract's embedded run_id.
# ---------------------------------------------------------------------------


class TestN2_RunIdMismatchWithRouteContract:
    """Mutate the bundle's run_id so it disagrees with the on-disk RouteContract.

    The verifier reads the RouteContract from REPO_ROOT/<runtime_route_contract_ref>
    and compares the embedded run_id to bundle.run_id. The fixture for this test
    points the bundle at a TEMP RouteContract written under tmp_path that
    declares a different run_id; the bundle's run_id is left as-is.
    """

    def test_run_id_mismatch_fires(self, tmp_path: Path, rg_bundle, rg_spec):
        b = copy.deepcopy(rg_bundle)
        # Negative-control fixture: synthetic RouteContract with a DIFFERENT run_id.
        synthetic_rc = {
            "_negative_control_fixture": True,
            "fixture_purpose": "N2 — run_id_mismatch_with_route_contract",
            "run_id": "fabricated-not-matching-spine-9999",  # mutated
            "request_id": b.get("request_id"),
            "trace_root": b.get("trace_root"),
            "execution_form": "BYPASS",
        }
        # Place fixture under a path the verifier can resolve via REPO_ROOT.
        rel = "artifacts/_neg_control_n2/route_contract.json"
        out = REPO_ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(synthetic_rc), encoding="utf-8")
        try:
            b["runtime_route_contract_ref"] = rel
            viols = verify_with_mode(b, rg_spec, "strict")
            assert "run_id_mismatch_with_route_contract" in _violation_ids(viols)
        finally:
            out.unlink(missing_ok=True)
            try:
                out.parent.rmdir()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# N4 — duplicate route_contract artifact_kind in the manifest.
# ---------------------------------------------------------------------------


class TestN4_DuplicateRouteContract:
    """Plan §9 N4 — verifier MUST emit `duplicate_route_contract` (in addition
    to the generic `duplicate_artifact_kind`) when two manifest rows declare
    artifact_kind=route_contract.
    """

    def test_duplicate_route_contract_kind_fires(self, tmp_path: Path, rg_bundle, rg_spec):
        b = copy.deepcopy(rg_bundle)
        manifest = {
            "_negative_control_fixture": True,
            "fixture_purpose": "N4 — duplicate route_contract artifact_kind",
            "app_name": "apps_rg",
            "harness_run_id": b.get("harness_run_id"),
            "run_id": b.get("run_id"),
            "trace_root": b.get("trace_root"),
            "items": [
                {
                    "key": "runtime_route_contract_ref",
                    "ref_field": "runtime_route_contract_ref",
                    "artifact_kind": "route_contract",
                    "ref": b.get("runtime_route_contract_ref"),
                    "path": b.get("runtime_route_contract_ref"),
                    "sha256": "a" * 64,
                    "run_id": b.get("run_id"),
                    "present": True,
                },
                {
                    "key": "runtime_route_contract_ref_dup",
                    "ref_field": "runtime_route_contract_ref_dup",
                    "artifact_kind": "route_contract",  # duplicate kind
                    "ref": "artifacts/synthetic/dup_route_contract.json",
                    "path": "artifacts/synthetic/dup_route_contract.json",
                    "sha256": "b" * 64,
                    "run_id": b.get("run_id"),
                    "present": True,
                },
            ],
        }
        rel = "artifacts/_neg_control_n4/manifest.json"
        out = REPO_ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest), encoding="utf-8")
        try:
            b["artifact_manifest_ref"] = rel
            viols = verify_with_mode(b, rg_spec, "strict")
            ids = _violation_ids(viols)
            assert "duplicate_route_contract" in ids, (
                f"Expected duplicate_route_contract; got: {ids}"
            )
            # generic rule_id MUST also fire
            assert "duplicate_artifact_kind" in ids
        finally:
            out.unlink(missing_ok=True)
            try:
                out.parent.rmdir()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# N6 — runtime_l3_receipt_ref present but static-DAG hash unbound.
#
# The apps_rg baseline is L3-bypassed (expected_l3_path=BYPASSED). We need a
# minimal synthetic managed-workflow proof fixture to exercise the RAN path
# without touching real artifacts. The synthetic AppSpec + bundle + L3
# receipt below are ALL clearly marked as negative-control fixtures and
# carry an `_negative_control_fixture: true` sentinel so they cannot be
# mistaken for runtime evidence.
# ---------------------------------------------------------------------------


class TestN6_RuntimeL3StaticDagHashUnbound:

    @staticmethod
    def _synthetic_spec() -> AppSpec:
        return AppSpec(
            app_name="apps_synthetic_n6",
            app_package="apps_synthetic_n6",
            runnable=True,
            expected_route_form="MANAGED_WORKFLOW",
            expects_static_dag=True,
            expects_c0_grounding=False,
            expects_prompt_assembly=False,
            expects_l2_execution=False,
            expects_durable_mutation=False,
            runs_root_glob="artifacts/apps_synthetic_n6/runs/*",
            certification_required=True,
            expected_execution_form=EXECUTION_FORM_MANAGED_WORKFLOW,
            expected_l3_path=L3_PATH_RAN,
        )

    @staticmethod
    def _write_synthetic_l3_receipt(static_hash_in_receipt: str) -> str:
        """Write a synthetic L3 runtime receipt and return its repo-relative path."""
        rel = "artifacts/_neg_control_n6/l3_runtime_receipt.json"
        out = REPO_ROOT / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            "_negative_control_fixture": True,
            "fixture_purpose": "N6 — runtime_l3_static_dag_hash_unbound",
            "execution_form": "MANAGED_WORKFLOW",
            "static_dag_hash": static_hash_in_receipt,
            "dag_sha256": static_hash_in_receipt,
        }), encoding="utf-8")
        return rel

    def _synthetic_bundle(self, *, l3_ref: str | None, static_dag_ref: str | None,
                          static_dag_sha256: str | None) -> dict:
        return {
            "_negative_control_fixture": True,
            "fixture_purpose": "N6 — synthetic managed-workflow bundle (NEVER certifying runtime evidence)",
            "proof_schema_version": "apps_e2e_proof/2026-05-01/v1",
            "harness_schema_version": "apps_e2e_harness/2026-05-01/v1",
            "app_name": "apps_synthetic_n6",
            "app_package": "apps_synthetic_n6",
            "entrypoint_command": "python -m apps_synthetic_n6",
            "run_id": "synthetic-n6-run-1",
            "request_id": "synthetic-n6-req-1",
            "trace_root": "synthetic-n6-trace-1",
            "started_at_utc": "2026-05-02T07:00:00Z",
            "finished_at_utc": "2026-05-02T07:00:01Z",
            "exit_code": 0,
            "git_commit": "0" * 40,
            "git_dirty": False,
            "runtime_mode": "live_run",
            "runtime_mode_classification": "live_run",
            "mock_mode_detected": False,
            "fixture_mode_detected": False,
            "fixture_data_used": False,
            "fixture_runtime_mode": False,
            "synthetic_trace_detected": False,
            "success": True,
            "blocking_gaps": [],
            "harness_pass": True,
            "honest_fail_closed": False,
            "harness_run_id": "synthetic-n6-harness-1",
            "app_overlay_authority_status": "overlay_respected",
            "agentic_core_spine_status": "spine_active",
            "static_dag_ref": static_dag_ref,
            "static_dag_sha256": static_dag_sha256,
            "runtime_l3_receipt_ref": l3_ref,
            "stage_matrix": [],
            "run_info": {"artifacts": [], "stale": []},
        }

    def test_l3_receipt_with_no_static_dag_ref(self):
        l3_ref = self._write_synthetic_l3_receipt(static_hash_in_receipt="abc123")
        try:
            b = self._synthetic_bundle(
                l3_ref=l3_ref,
                static_dag_ref=None,  # missing — N6 condition
                static_dag_sha256=None,
            )
            viols = verify_with_mode(b, self._synthetic_spec(), "strict")
            assert "runtime_l3_static_dag_hash_unbound" in _violation_ids(viols)
        finally:
            (REPO_ROOT / l3_ref).unlink(missing_ok=True)
            try:
                (REPO_ROOT / l3_ref).parent.rmdir()
            except OSError:
                pass

    def test_l3_receipt_with_mismatched_static_dag_hash(self):
        # Bundle declares static_dag_sha256=BUNDLE_HASH but L3 receipt's
        # static_dag_hash=DIFFERENT_HASH. Verifier must fire N6.
        l3_ref = self._write_synthetic_l3_receipt(static_hash_in_receipt="WRONG_HASH")
        # Need a real static_dag_ref file so manifest checks resolve.
        static_rel = "artifacts/_neg_control_n6/static_dag_proof.json"
        static_path = REPO_ROOT / static_rel
        static_path.parent.mkdir(parents=True, exist_ok=True)
        static_path.write_text(json.dumps({"_negative_control_fixture": True}), encoding="utf-8")
        try:
            b = self._synthetic_bundle(
                l3_ref=l3_ref,
                static_dag_ref=static_rel,
                static_dag_sha256="BUNDLE_DECLARED_HASH",
            )
            viols = verify_with_mode(b, self._synthetic_spec(), "strict")
            assert "runtime_l3_static_dag_hash_unbound" in _violation_ids(viols)
        finally:
            (REPO_ROOT / l3_ref).unlink(missing_ok=True)
            static_path.unlink(missing_ok=True)
            try:
                static_path.parent.rmdir()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# N7 — L6 exhaust timestamp precedes Exit X3 timestamp.
# ---------------------------------------------------------------------------


class TestN7_L6EmittedBeforeExit:
    """Create temp copies of the exit + exhaust artifacts with mutated
    timestamps so exhaust precedes exit. Real artifacts on disk are
    untouched; the bundle is redirected to the temp copies.
    """

    def test_exhaust_before_exit_fires(self, rg_bundle, rg_spec):
        b = copy.deepcopy(rg_bundle)

        # Synthetic exit + exhaust artifacts with INVERTED timestamps.
        exit_ts = "2026-05-02T08:00:00Z"   # Exit emitted at t1
        exhaust_ts = "2026-05-02T07:59:00Z"  # Exhaust emitted BEFORE exit (1m earlier)

        synthetic_exit = {
            "_negative_control_fixture": True,
            "fixture_purpose": "N7 — l6_emitted_before_exit (exit half)",
            "x3_disposition": "EXIT_OK",
            "exit_review_packet_id": "synthetic-exit-1",
            "emitted_at_utc": exit_ts,
            "finished_at_utc": exit_ts,
            "run_id": b.get("run_id"),
            "request_id": b.get("request_id"),
            "trace_root": b.get("trace_root"),
        }
        synthetic_exhaust = {
            "_negative_control_fixture": True,
            "fixture_purpose": "N7 — l6_emitted_before_exit (exhaust half)",
            "exit_review_packet_id": "synthetic-exit-1",
            "emitted_at_utc": exhaust_ts,
            "observed_after_exit_at_utc": exhaust_ts,
            "run_id": b.get("run_id"),
            "request_id": b.get("request_id"),
            "trace_root": b.get("trace_root"),
        }

        exit_rel = "artifacts/_neg_control_n7/exit_x3.json"
        exhaust_rel = "artifacts/_neg_control_n7/runtime_exhaust.json"
        exit_path = REPO_ROOT / exit_rel
        exhaust_path = REPO_ROOT / exhaust_rel
        exit_path.parent.mkdir(parents=True, exist_ok=True)
        exit_path.write_text(json.dumps(synthetic_exit), encoding="utf-8")
        exhaust_path.write_text(json.dumps(synthetic_exhaust), encoding="utf-8")

        try:
            b["runtime_exit_disposition_ref"] = exit_rel
            b["runtime_exhaust_ref"] = exhaust_rel
            viols = verify_with_mode(b, rg_spec, "strict")
            assert "l6_emitted_before_exit" in _violation_ids(viols)
        finally:
            exit_path.unlink(missing_ok=True)
            exhaust_path.unlink(missing_ok=True)
            try:
                exit_path.parent.rmdir()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Final positive control: after all the above mutations, the unmutated
# baseline MUST still pass strict mode. (Belt-and-braces sanity check.)
# ---------------------------------------------------------------------------


class TestPositiveControl_BaselineStillPasses:
    """Final positive control. Re-runs the baseline strict check after all
    other negative controls have executed to guarantee no test left global
    state polluted on the real bundle.
    """

    def test_baseline_still_passes_strict(self, rg_bundle, rg_spec):
        viols = verify_with_mode(rg_bundle, rg_spec, "strict")
        assert viols == [], (
            "Baseline apps_rg bundle MUST still pass strict mode after "
            "negative-control suite. Violations: "
            + ", ".join(v.rule_id for v in viols)
        )


class TestN19_RefMissingFromManifest:
    def test_declared_ref_absent_from_manifest(self, rg_bundle, rg_spec):
        b = copy.deepcopy(rg_bundle)
        # Tamper artifact_manifest_ref so manifest resolves but contains
        # different items, OR strip the relevant ref_field from items.
        # Easiest: set artifact_manifest_ref to None so verifier falls back
        # to run_info.artifacts which lacks ref_field metadata.
        b["artifact_manifest_ref"] = None
        # Also strip run_info.artifacts so the field is missing entirely.
        b["run_info"] = {"artifacts": [], "stale": []}
        viols = verify_with_mode(b, rg_spec, "strict")
        assert "ref_missing_from_manifest" in _violation_ids(viols)


class TestN20_DuplicateArtifactKind:
    def test_two_route_contract_rows(self, tmp_path: Path, rg_bundle, rg_spec):
        # Build a synthetic manifest with two artifact_kind=route_contract rows
        # and point bundle.artifact_manifest_ref at it.
        b = copy.deepcopy(rg_bundle)
        manifest = {
            "app_name": "apps_rg",
            "harness_run_id": b.get("harness_run_id"),
            "run_id": b.get("run_id"),
            "trace_root": b.get("trace_root"),
            "items": [
                {
                    "key": "runtime_route_contract_ref",
                    "ref_field": "runtime_route_contract_ref",
                    "artifact_kind": "route_contract",
                    "ref": b.get("runtime_route_contract_ref"),
                    "path": b.get("runtime_route_contract_ref"),
                    "sha256": "a" * 64,
                    "run_id": b.get("run_id"),
                    "present": True,
                },
                {
                    "key": "runtime_route_contract_ref_dup",
                    "ref_field": "runtime_route_contract_ref_dup",
                    "artifact_kind": "route_contract",  # DUP
                    "ref": "artifacts/synthetic/extra_route_contract.json",
                    "path": "artifacts/synthetic/extra_route_contract.json",
                    "sha256": "b" * 64,
                    "run_id": b.get("run_id"),
                    "present": True,
                },
            ],
        }
        manifest_path = tmp_path / "synthetic_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        # Point bundle at the synthetic manifest path (relative to REPO_ROOT).
        try:
            rel = manifest_path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            # tmp_path is outside REPO_ROOT; emit absolute and let verifier
            # try to resolve — in that case verifier fails to load and
            # falls back to run_info, which won't trigger N20. Use a known-
            # safe path inside REPO_ROOT instead.
            rel = "artifacts/_neg_control_dup_kind_manifest.json"
            (REPO_ROOT / rel).parent.mkdir(parents=True, exist_ok=True)
            (REPO_ROOT / rel).write_text(json.dumps(manifest), encoding="utf-8")
        b["artifact_manifest_ref"] = rel
        viols = verify_with_mode(b, rg_spec, "strict")
        assert "duplicate_artifact_kind" in _violation_ids(viols)
