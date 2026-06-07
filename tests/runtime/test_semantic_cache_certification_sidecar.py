"""Tests — R1B semantic-cache subclaim sidecar (W1 phase 1 contract only).

Plan: ``docs/archive/windsurf/legacy-tree/plans/runtime-cert-hardened-w0-7e3c9a.md``
Author-Gate (2026-04-30, architecture_choice):
``map_to_RTC_REQ_055_plus_conditional_056_057_058``.

Coverage (~16 cases — every fail-closed mandate from user §8)
-----------------------------------------------------------

  - missing sidecar -> advisory baseline (REQ-055 stays PENDING, exit=0)
  - empty sidecar -> BLOCKED with MISSING_CORE_SUBCLAIM
  - missing required subclaim -> BLOCKED, exit=2
  - CALIBRATION_GAP keeps PARTIAL, exit=2
  - INFRASTRUCTURE_GAP keeps BLOCKED (hard blocker), exit=2
  - all 6 core PASS (no scope) -> RTC-REQ-055 ACCEPTED at E5, exit=0
  - all 6 core PASS + runtime scope but R1B_INTEGRATED_RUNTIME=NOT_PROVEN
        -> RTC-REQ-055 ACCEPTED, RTC-REQ-056 BLOCKED, exit=2
  - all 6 + 1 conditional PASS in scope -> matching row ACCEPTED
  - sidecar's actual_proof_depth/final_acceptance_status fields ignored
  - conditional NOT_APPLICABLE allowed when scope flag False
  - conditional NOT_APPLICABLE rejected when scope flag True
  - core NOT_APPLICABLE always rejected (malformed)
  - malformed JSON exits 2
  - invalid status value exits 2 (with INVALID_SUBCLAIM_STATUS error)
  - overrides merge preserves other rows
  - acceptance verifier picks up overrides written by sidecar verifier
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.r1b_subclaim_schema import (
    ALL_SUBCLAIMS,
    CORE_SUBCLAIMS,
    GATED_ROWS,
    compute_row_outcomes,
    load_sidecar,
)

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"
SIDECAR = ARTIFACTS_DIR / "semantic_cache_subclaims.json"
OVERRIDES = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
REPORT_JSON = ARTIFACTS_DIR / "semantic_cache_certification_report.json"


# ──────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────


@pytest.fixture
def clean_state():
    """Remove sidecar + overrides + report so each test starts clean.

    On teardown, also remove sidecar so the next test starts clean and
    the W0 baseline is restored.
    """
    sidecar_backup = SIDECAR.read_text(encoding="utf-8") if SIDECAR.exists() else None
    overrides_backup = OVERRIDES.read_text(encoding="utf-8") if OVERRIDES.exists() else None
    if SIDECAR.exists():
        os.remove(SIDECAR)
    if OVERRIDES.exists():
        os.remove(OVERRIDES)
    yield
    # Teardown: restore baseline
    if SIDECAR.exists():
        os.remove(SIDECAR)
    if OVERRIDES.exists():
        os.remove(OVERRIDES)
    if sidecar_backup is not None:
        SIDECAR.write_text(sidecar_backup, encoding="utf-8")
    if overrides_backup is not None:
        OVERRIDES.write_text(overrides_backup, encoding="utf-8")
    # Re-run sidecar verifier to leave a clean state report on disk
    subprocess.run(
        [sys.executable, "scripts/verify_semantic_cache_certification.py"],
        capture_output=True, cwd=str(REPO_ROOT), timeout=15, check=False,
    )


def _run_sidecar(*, strict: bool = False, strict_via_env: bool = False) -> int:
    """Run the sidecar verifier. Strict mode can be selected via --strict or env."""
    cmd = [sys.executable, "scripts/verify_semantic_cache_certification.py"]
    if strict:
        cmd.append("--strict")
    env = dict(os.environ)
    if strict_via_env:
        env["SEMANTIC_CACHE_CERTIFICATION_STRICT"] = "1"
    else:
        env.pop("SEMANTIC_CACHE_CERTIFICATION_STRICT", None)
    return subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(REPO_ROOT),
        timeout=15, check=False, env=env,
    ).returncode


def _write_sidecar(scope: dict | None = None,
                   subclaims: dict | None = None,
                   *,
                   schema_version: int = 1,
                   raw: str | None = None) -> None:
    """Write a sidecar; if ``raw`` is provided, write it verbatim."""
    SIDECAR.parent.mkdir(parents=True, exist_ok=True)
    if raw is not None:
        SIDECAR.write_text(raw, encoding="utf-8")
        return
    payload = {
        "schema_version": schema_version,
        "evaluated_at_utc": "2026-04-30T19:00:00+00:00",
        "evidence_evaluator": "test_harness",
        "scope": scope or {
            "runtime_certification_claimed": False,
            "observability_certification_claimed": False,
            "replay_certification_claimed": False,
        },
        "subclaims": subclaims or {},
    }
    SIDECAR.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _all_core_pass() -> dict:
    """Build a subclaims dict where every core subclaim PASSes."""
    return {sid: {"status": "PASS", "evidence_path": None,
                  "notes": "synthetic test pass"} for sid in CORE_SUBCLAIMS}


def _read_report() -> dict:
    return json.loads(REPORT_JSON.read_text(encoding="utf-8"))


def _read_overrides() -> dict:
    return json.loads(OVERRIDES.read_text(encoding="utf-8"))


# ──────────────────────────────────────────────────────────────────────
# 1. Missing / empty / malformed sidecar
# ──────────────────────────────────────────────────────────────────────


class TestMissingSidecar:
    def test_missing_sidecar_keeps_req055_pending_advisory(self, clean_state):
        rc = _run_sidecar()
        assert rc == 0  # advisory baseline, not blocking
        report = _read_report()
        assert report["status"] == "PASS_ADVISORY_BASELINE"
        assert report["sidecar_present"] is False
        # All 4 gated rows stay PENDING
        for rid in GATED_ROWS:
            o = report["row_outcomes"][rid]
            assert o["final_acceptance_status"] == "PENDING"
            assert o["expected_fail_reason"] == "SIDECAR_ABSENT"

    def test_missing_sidecar_does_not_pollute_overrides(self, clean_state):
        # Pre-seed overrides for an unrelated row
        OVERRIDES.write_text(json.dumps({
            "actual_proof_depth": {"RTC-REQ-999": "E2_STATIC_CHECK"},
            "final_acceptance_status": {"RTC-REQ-999": "ACCEPTED"},
        }), encoding="utf-8")
        rc = _run_sidecar()
        assert rc == 0
        ov = _read_overrides()
        # Unrelated row preserved
        assert ov["actual_proof_depth"]["RTC-REQ-999"] == "E2_STATIC_CHECK"
        assert ov["final_acceptance_status"]["RTC-REQ-999"] == "ACCEPTED"
        # Gated rows get NO entries (PENDING => removed)
        for rid in GATED_ROWS:
            assert rid not in ov.get("actual_proof_depth", {})
            assert rid not in ov.get("final_acceptance_status", {})


class TestMalformedSidecar:
    def test_malformed_json_exits_two(self, clean_state):
        _write_sidecar(raw="{not json,")
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert report["status"] == "FAIL_CLOSED"
        assert report["expected_fail_reason"] == "SIDECAR_MALFORMED"
        assert any("MALFORMED_JSON" in e for e in report["sidecar_schema_errors"])

    def test_top_level_not_object_exits_two(self, clean_state):
        _write_sidecar(raw='["not", "an", "object"]')
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert any("MALFORMED_SIDECAR" in e for e in report["sidecar_schema_errors"])

    def test_invalid_subclaim_status_exits_two(self, clean_state):
        _write_sidecar(subclaims={
            **_all_core_pass(),
            "R1B_DENSE_SIMILARITY_COMPOSITION_PROOF": {"status": "MAGIC_OK"},
        })
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert any("INVALID_SUBCLAIM_STATUS" in e for e in report["sidecar_schema_errors"])

    def test_unsupported_schema_version_exits_two(self, clean_state):
        _write_sidecar(schema_version=99, subclaims=_all_core_pass())
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert any("UNSUPPORTED_SCHEMA_VERSION" in e for e in report["sidecar_schema_errors"])


# ──────────────────────────────────────────────────────────────────────
# 2. Missing required subclaims
# ──────────────────────────────────────────────────────────────────────


class TestMissingRequiredSubclaims:
    def test_empty_subclaims_blocks_all_rows(self, clean_state):
        _write_sidecar(subclaims={})
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        # All 6 core subclaims missing
        missing = [e for e in report["sidecar_schema_errors"] if "MISSING_CORE_SUBCLAIM" in e]
        assert len(missing) == 6
        # RTC-REQ-055 is BLOCKED
        assert report["row_outcomes"]["RTC-REQ-055"]["final_acceptance_status"] == "BLOCKED"

    def test_one_core_missing_blocks_req055(self, clean_state):
        sub = _all_core_pass()
        del sub["R1B_TERMINAL_EXIT_PROOF"]
        _write_sidecar(subclaims=sub)
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert any("R1B_TERMINAL_EXIT_PROOF" in e for e in report["sidecar_schema_errors"])

    def test_runtime_scope_without_integrated_subclaim_blocked(self, clean_state):
        _write_sidecar(
            scope={"runtime_certification_claimed": True,
                   "observability_certification_claimed": False,
                   "replay_certification_claimed": False},
            subclaims=_all_core_pass(),  # no R1B_INTEGRATED_RUNTIME_PROOF
        )
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert any("R1B_INTEGRATED_RUNTIME_PROOF" in e for e in report["sidecar_schema_errors"])


# ──────────────────────────────────────────────────────────────────────
# 3. Soft / hard blockers in subclaims
# ──────────────────────────────────────────────────────────────────────


class TestBlockerStatuses:
    def test_calibration_gap_keeps_req055_partial(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_PRODUCTION_THRESHOLD_PROOF"]["status"] = "CALIBRATION_GAP"
        _write_sidecar(subclaims=sub)
        rc = _run_sidecar()
        assert rc == 2  # PARTIAL is still fail-closed (no ACCEPTED)
        report = _read_report()
        out = report["row_outcomes"]["RTC-REQ-055"]
        assert out["final_acceptance_status"] == "PARTIAL"
        assert out["actual_proof_depth"] == "E0_REQUIREMENT_TEXT"
        assert "CALIBRATION_GAP" in out["acceptance_caveat"]

    def test_infrastructure_gap_keeps_req055_blocked(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_APPROVED_MODEL_PROOF"]["status"] = "INFRASTRUCTURE_GAP"
        _write_sidecar(subclaims=sub)
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        out = report["row_outcomes"]["RTC-REQ-055"]
        assert out["final_acceptance_status"] == "BLOCKED"
        assert "INFRASTRUCTURE_GAP" in out["blocking_gap"]

    def test_not_proven_keeps_blocked(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_DENSE_SIMILARITY_COMPOSITION_PROOF"]["status"] = "NOT_PROVEN"
        _write_sidecar(subclaims=sub)
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert report["row_outcomes"]["RTC-REQ-055"]["final_acceptance_status"] == "BLOCKED"

    def test_explicit_blocked_keeps_blocked(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_NEGATIVE_CONTROL_PROOF"]["status"] = "BLOCKED"
        _write_sidecar(subclaims=sub)
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert report["row_outcomes"]["RTC-REQ-055"]["final_acceptance_status"] == "BLOCKED"


# ──────────────────────────────────────────────────────────────────────
# 4. All-PASS scenarios (still scoped to W1 phase 1 contract)
# ──────────────────────────────────────────────────────────────────────


class TestAllCorePassNoScope:
    def test_all_six_core_pass_no_scope_accepts_only_req055(self, clean_state):
        _write_sidecar(subclaims=_all_core_pass())
        rc = _run_sidecar()
        assert rc == 0  # PASS — no in-scope blockers
        report = _read_report()
        assert report["status"] == "PASS"
        # RTC-REQ-055 ACCEPTED at E5_COMPOSITION_PROOF
        out_55 = report["row_outcomes"]["RTC-REQ-055"]
        assert out_55["final_acceptance_status"] == "ACCEPTED"
        assert out_55["actual_proof_depth"] == "E5_COMPOSITION_PROOF"
        # RTC-REQ-056/057/058 stay PENDING (out of scope)
        for rid in ("RTC-REQ-056", "RTC-REQ-057", "RTC-REQ-058"):
            o = report["row_outcomes"][rid]
            assert o["in_scope"] is False
            assert o["final_acceptance_status"] == "PENDING"

    def test_all_six_core_pass_runtime_scope_with_integrated_pass_accepts_055_and_056(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_INTEGRATED_RUNTIME_PROOF"] = {"status": "PASS"}
        _write_sidecar(
            scope={"runtime_certification_claimed": True,
                   "observability_certification_claimed": False,
                   "replay_certification_claimed": False},
            subclaims=sub,
        )
        rc = _run_sidecar()
        assert rc == 0
        report = _read_report()
        assert report["row_outcomes"]["RTC-REQ-055"]["final_acceptance_status"] == "ACCEPTED"
        assert report["row_outcomes"]["RTC-REQ-056"]["final_acceptance_status"] == "ACCEPTED"
        assert report["row_outcomes"]["RTC-REQ-056"]["actual_proof_depth"] == "E6_INTEGRATED_RUNTIME_PROOF"
        # 057 + 058 still PENDING (out of scope)
        assert report["row_outcomes"]["RTC-REQ-057"]["final_acceptance_status"] == "PENDING"
        assert report["row_outcomes"]["RTC-REQ-058"]["final_acceptance_status"] == "PENDING"


class TestRuntimeScopeWithBlockedConditional:
    def test_runtime_scope_with_integrated_not_proven_blocks_req056_only(self, clean_state):
        """Closure-required: even if 055 PASSes, 056 stays BLOCKED when its
        conditional subclaim is NOT_PROVEN."""
        sub = _all_core_pass()
        sub["R1B_INTEGRATED_RUNTIME_PROOF"] = {"status": "NOT_PROVEN"}
        _write_sidecar(
            scope={"runtime_certification_claimed": True,
                   "observability_certification_claimed": False,
                   "replay_certification_claimed": False},
            subclaims=sub,
        )
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert report["row_outcomes"]["RTC-REQ-055"]["final_acceptance_status"] == "ACCEPTED"
        assert report["row_outcomes"]["RTC-REQ-056"]["final_acceptance_status"] == "BLOCKED"


# ──────────────────────────────────────────────────────────────────────
# 5. NOT_APPLICABLE rules (anti-cheat)
# ──────────────────────────────────────────────────────────────────────


class TestNotApplicableRules:
    def test_not_applicable_on_conditional_with_scope_false_accepted(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_INTEGRATED_RUNTIME_PROOF"] = {"status": "NOT_APPLICABLE",
                                                "notes": "scope flag is False"}
        _write_sidecar(
            scope={"runtime_certification_claimed": False,
                   "observability_certification_claimed": False,
                   "replay_certification_claimed": False},
            subclaims=sub,
        )
        rc = _run_sidecar()
        # Sidecar is valid; 055 ACCEPTED; 056 stays PENDING (out of scope)
        assert rc == 0
        report = _read_report()
        assert report["row_outcomes"]["RTC-REQ-055"]["final_acceptance_status"] == "ACCEPTED"
        assert report["row_outcomes"]["RTC-REQ-056"]["in_scope"] is False
        assert report["row_outcomes"]["RTC-REQ-056"]["final_acceptance_status"] == "PENDING"

    def test_not_applicable_on_conditional_with_scope_true_rejected(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_INTEGRATED_RUNTIME_PROOF"] = {"status": "NOT_APPLICABLE"}
        _write_sidecar(
            scope={"runtime_certification_claimed": True,
                   "observability_certification_claimed": False,
                   "replay_certification_claimed": False},
            subclaims=sub,
        )
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert any("INVALID_NOT_APPLICABLE_WHEN_SCOPE_CLAIMED" in e
                   for e in report["sidecar_schema_errors"])

    def test_not_applicable_on_core_subclaim_rejected(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_DENSE_SIMILARITY_COMPOSITION_PROOF"]["status"] = "NOT_APPLICABLE"
        _write_sidecar(subclaims=sub)
        rc = _run_sidecar()
        assert rc == 2
        report = _read_report()
        assert any("INVALID_NOT_APPLICABLE" in e
                   for e in report["sidecar_schema_errors"])


# ──────────────────────────────────────────────────────────────────────
# 6. Anti-cheat: sidecar cannot mark ACCEPTED directly
# ──────────────────────────────────────────────────────────────────────


class TestSidecarCannotPromoteDirectly:
    def test_sidecar_actual_proof_depth_field_ignored(self, clean_state):
        """A sidecar that tries to declare actual_proof_depth at top level or
        inside subclaims must NOT promote the row. The verifier alone writes
        overrides."""
        SIDECAR.parent.mkdir(parents=True, exist_ok=True)
        # Sidecar with a forbidden 'actual_proof_depth' top-level field +
        # a forbidden 'final_acceptance_status' field. Both must be ignored.
        SIDECAR.write_text(json.dumps({
            "schema_version": 1,
            "evaluated_at_utc": "2026-04-30T19:00:00+00:00",
            "evidence_evaluator": "test",
            "actual_proof_depth": {"RTC-REQ-055": "E9_PRODUCTION_DEPENDENCY_PROOF"},
            "final_acceptance_status": {"RTC-REQ-055": "ACCEPTED"},
            "scope": {"runtime_certification_claimed": False,
                      "observability_certification_claimed": False,
                      "replay_certification_claimed": False},
            "subclaims": {sid: {"status": "NOT_PROVEN"} for sid in CORE_SUBCLAIMS},
        }, indent=2), encoding="utf-8")
        rc = _run_sidecar()
        assert rc == 2
        ov = _read_overrides()
        # The sidecar's forbidden field was IGNORED — the verifier wrote
        # BLOCKED (because subclaims are NOT_PROVEN), not ACCEPTED at E9.
        assert ov["final_acceptance_status"]["RTC-REQ-055"] == "BLOCKED"
        assert ov["actual_proof_depth"]["RTC-REQ-055"] == "E0_REQUIREMENT_TEXT"
        assert ov["actual_proof_depth"]["RTC-REQ-055"] != "E9_PRODUCTION_DEPENDENCY_PROOF"


# ──────────────────────────────────────────────────────────────────────
# 7. Override merging (preserve other rows' overrides)
# ──────────────────────────────────────────────────────────────────────


class TestOverrideMerging:
    def test_overrides_merge_preserves_unrelated_rows(self, clean_state):
        # Pre-seed an unrelated override
        OVERRIDES.parent.mkdir(parents=True, exist_ok=True)
        OVERRIDES.write_text(json.dumps({
            "actual_proof_depth": {"RTC-REQ-001": "E2_STATIC_CHECK"},
            "final_acceptance_status": {"RTC-REQ-001": "ACCEPTED"},
            "acceptance_caveat": {},
            "blocking_gap": {},
        }), encoding="utf-8")
        # All-pass sidecar
        _write_sidecar(subclaims=_all_core_pass())
        rc = _run_sidecar()
        assert rc == 0
        ov = _read_overrides()
        # Unrelated row preserved
        assert ov["actual_proof_depth"]["RTC-REQ-001"] == "E2_STATIC_CHECK"
        assert ov["final_acceptance_status"]["RTC-REQ-001"] == "ACCEPTED"
        # RTC-REQ-055 added by sidecar verifier
        assert ov["final_acceptance_status"]["RTC-REQ-055"] == "ACCEPTED"
        assert ov["actual_proof_depth"]["RTC-REQ-055"] == "E5_COMPOSITION_PROOF"


# ──────────────────────────────────────────────────────────────────────
# 8. End-to-end integration with W0 acceptance verifier
# ──────────────────────────────────────────────────────────────────────


class TestIntegrationWithW0:
    def test_acceptance_verifier_picks_up_blocked_req055(self, clean_state):
        # Plant a hard-blocker sidecar
        sub = _all_core_pass()
        sub["R1B_TERMINAL_EXIT_PROOF"]["status"] = "NOT_PROVEN"
        _write_sidecar(subclaims=sub)
        rc_sidecar = _run_sidecar()
        assert rc_sidecar == 2

        # Now run the W0 acceptance verifier — it should see BLOCKED RTC-REQ-055
        # in the overrides and reflect it in its own report.
        rc_acc = subprocess.run(
            [sys.executable, "scripts/verify_runtime_certification_acceptance.py"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
        ).returncode
        # Acceptance verifier emits exit=0 because BLOCKED with blocking_gap is
        # legal under the validator's rules (it is a legal terminal status).
        assert rc_acc == 0
        acc_report = json.loads(
            (ARTIFACTS_DIR / "acceptance_legality_report.json").read_text(encoding="utf-8")
        )
        # Find RTC-REQ-055 in the verdict list
        verdict_55 = next(
            (v for v in acc_report["verdicts"] if v["req_id"] == "RTC-REQ-055"),
            None,
        )
        assert verdict_55 is not None
        assert verdict_55["final_acceptance_status"] == "BLOCKED"
        assert verdict_55["blocking_gap"] != ""

    def test_acceptance_verifier_picks_up_accepted_req055(self, clean_state):
        _write_sidecar(subclaims=_all_core_pass())
        rc_sidecar = _run_sidecar()
        assert rc_sidecar == 0

        rc_acc = subprocess.run(
            [sys.executable, "scripts/verify_runtime_certification_acceptance.py"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
        ).returncode
        assert rc_acc == 0
        acc_report = json.loads(
            (ARTIFACTS_DIR / "acceptance_legality_report.json").read_text(encoding="utf-8")
        )
        verdict_55 = next(
            (v for v in acc_report["verdicts"] if v["req_id"] == "RTC-REQ-055"),
            None,
        )
        assert verdict_55 is not None
        assert verdict_55["final_acceptance_status"] == "ACCEPTED"
        assert verdict_55["actual_proof_depth"] == "E5_COMPOSITION_PROOF"
        # And the verdict must be legal (since actual >= required)
        assert verdict_55["legal"] is True


# ──────────────────────────────────────────────────────────────────────
# 9. Module-level direct tests on the schema (no subprocess)
# ──────────────────────────────────────────────────────────────────────


class TestSchemaModule:
    def test_canonical_subclaim_count(self):
        assert len(CORE_SUBCLAIMS) == 6
        assert len(ALL_SUBCLAIMS) == 9

    def test_gated_rows_are_canonical(self):
        assert set(GATED_ROWS.keys()) == {
            "RTC-REQ-055", "RTC-REQ-056", "RTC-REQ-057", "RTC-REQ-058",
        }

    def test_load_sidecar_absent_returns_advisory_baseline(self, clean_state):
        result = load_sidecar(SIDECAR)
        assert result.sidecar_present is False
        assert result.is_valid is False
        assert result.schema_errors == ()

    def test_compute_outcomes_absent_sidecar_all_pending(self, clean_state):
        result = load_sidecar(SIDECAR)
        outcomes = compute_row_outcomes(result)
        for o in outcomes.values():
            assert o.final_acceptance_status == "PENDING"
            assert o.expected_fail_reason == "SIDECAR_ABSENT"


# ──────────────────────────────────────────────────────────────────────
# 10. Strict mode (W1 phase 2 hygiene fix, 2026-04-30)
# ──────────────────────────────────────────────────────────────────────


class TestStrictModeViaCliFlag:
    """W0 keeps advisory; W1+/final certification uses strict.

    Strict via ``--strict`` CLI flag.
    """

    def test_strict_flag_absent_sidecar_exits_two(self, clean_state):
        rc = _run_sidecar(strict=True)
        assert rc == 2
        report = _read_report()
        assert report["status"] == "FAIL_CLOSED_STRICT"
        assert report["expected_fail_reason"] == "SEMANTIC_CACHE_SIDECAR_REQUIRED"
        assert report["mode"] == "strict"
        assert report["strict_mode_enabled_via"] == "--strict"

    def test_advisory_still_passes_when_sidecar_absent(self, clean_state):
        rc = _run_sidecar(strict=False)
        assert rc == 0
        report = _read_report()
        assert report["status"] == "PASS_ADVISORY_BASELINE"
        assert report["mode"] == "advisory"

    def test_strict_with_all_pass_sidecar_exits_zero(self, clean_state):
        _write_sidecar(subclaims=_all_core_pass())
        rc = _run_sidecar(strict=True)
        assert rc == 0
        report = _read_report()
        assert report["status"] == "PASS_STRICT"
        assert report["mode"] == "strict"

    def test_strict_with_blocked_subclaim_exits_two(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_NEGATIVE_CONTROL_PROOF"]["status"] = "BLOCKED"
        _write_sidecar(subclaims=sub)
        rc = _run_sidecar(strict=True)
        assert rc == 2
        report = _read_report()
        assert report["status"] == "FAIL_CLOSED"
        assert report["expected_fail_reason"] == "R1B_HARD_BLOCKERS_PRESENT"

    def test_strict_with_calibration_gap_exits_two(self, clean_state):
        sub = _all_core_pass()
        sub["R1B_PRODUCTION_THRESHOLD_PROOF"]["status"] = "CALIBRATION_GAP"
        _write_sidecar(subclaims=sub)
        rc = _run_sidecar(strict=True)
        assert rc == 2
        report = _read_report()
        assert report["expected_fail_reason"] == "R1B_SOFT_BLOCKERS_PRESENT"


class TestStrictModeViaEnvVar:
    """Strict mode via SEMANTIC_CACHE_CERTIFICATION_STRICT=1."""

    def test_env_strict_absent_sidecar_exits_two(self, clean_state):
        rc = _run_sidecar(strict_via_env=True)
        assert rc == 2
        report = _read_report()
        assert report["status"] == "FAIL_CLOSED_STRICT"
        assert report["expected_fail_reason"] == "SEMANTIC_CACHE_SIDECAR_REQUIRED"
        assert report["mode"] == "strict"
        assert report["strict_mode_enabled_via"] == "env_SEMANTIC_CACHE_CERTIFICATION_STRICT"

    def test_env_strict_with_all_pass_sidecar_exits_zero(self, clean_state):
        _write_sidecar(subclaims=_all_core_pass())
        rc = _run_sidecar(strict_via_env=True)
        assert rc == 0


class TestStrictModeEmptyAndIncomplete:
    """Strict-mode-specific fail-closed paths."""

    def test_strict_empty_subclaims_dict_exits_two(self, clean_state):
        SIDECAR.parent.mkdir(parents=True, exist_ok=True)
        SIDECAR.write_text(json.dumps({
            "schema_version": 1,
            "evaluated_at_utc": "2026-04-30T19:00:00+00:00",
            "evidence_evaluator": "test",
            "scope": {
                "runtime_certification_claimed": False,
                "observability_certification_claimed": False,
                "replay_certification_claimed": False,
            },
            "subclaims": {},
        }), encoding="utf-8")
        rc = _run_sidecar(strict=True)
        assert rc == 2
        report = _read_report()
        # The schema validator catches MISSING_CORE_SUBCLAIM first
        # (which is fine; strict-mode SEMANTIC_CACHE_SIDECAR_EMPTY is the
        # backup signal when subclaims is literally empty AND there are
        # no schema errors). Either is fail-closed.
        assert report["expected_fail_reason"] in (
            "SIDECAR_MALFORMED",
            "SEMANTIC_CACHE_SIDECAR_EMPTY",
        )

    def test_strict_missing_required_subclaim_exits_two(self, clean_state):
        sub = _all_core_pass()
        del sub["R1B_TERMINAL_EXIT_PROOF"]
        _write_sidecar(subclaims=sub)
        rc = _run_sidecar(strict=True)
        assert rc == 2
        report = _read_report()
        assert report["expected_fail_reason"] == "SIDECAR_MALFORMED"
        assert any("MISSING_CORE_SUBCLAIM" in e for e in report["sidecar_schema_errors"])


class TestModeProvenance:
    """The report must clearly record which mode was used."""

    def test_advisory_mode_marked_in_report(self, clean_state):
        _run_sidecar(strict=False)
        report = _read_report()
        assert report["mode"] == "advisory"
        assert report["strict_mode_enabled_via"] is None

    def test_strict_mode_marked_in_report(self, clean_state):
        _run_sidecar(strict=True)
        report = _read_report()
        assert report["mode"] == "strict"
        assert report["strict_mode_enabled_via"] == "--strict"
