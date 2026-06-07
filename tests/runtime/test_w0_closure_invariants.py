"""Tests — W0 closure invariants (5 user-mandated closure checks, 2026-04-30).

Plan: ``docs/archive/windsurf/legacy-tree/plans/runtime-cert-hardened-w0-7e3c9a.md``

Closure checks proven here
--------------------------

1. PENDING / E0 baseline rows cannot pass as ACCEPTED.
   - PENDING final_acceptance_status cannot count toward certification
   - runtime_claim_allowed=False unless proof-depth conditions met
   - Final certification gate cannot pass while actual_proof_depth is
     PENDING/E0

2. CI fail-closed behavior is real (not just YAML syntax).
   - Seeded bad CSV / override / composition-to-E6 / divergence /
     payload-mismatch all cause exit code 2.

3. No W0 report uses runtime-certification overclaim language.

4. Canonical CSV path is the bound location.

5. All W1-W4 rows remain PENDING/PARTIAL/BLOCKED until evidence sidecars
   exist.
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from agentic_core.runtime.prove_requirements.acceptance_validator import (
    apply_to_matrix,
    validate_acceptance,
)
from agentic_core.runtime.prove_requirements.certification_readiness import (
    derive_runtime_claim_allowed,
    is_certification_ready,
    summarize_certification_status,
)
from agentic_core.runtime.prove_requirements.matrix_loader import (
    CANONICAL_CSV_PATH,
    CANONICAL_REQUIREMENT_COUNT,
    REQUIRED_COLUMNS,
    load_matrix,
)
from agentic_core.runtime.prove_requirements.proof_depth_ladder import (
    COMPOSITION_NON_PROMOTABLE_TARGETS,
)

ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "certification"


# ──────────────────────────────────────────────────────────────────────
# Closure check #1 — PENDING / E0 cannot pass as ACCEPTED
# ──────────────────────────────────────────────────────────────────────


class TestPendingNeverCertifiedClosure1:
    """Closure #1: PENDING and E0 baseline never count as certified."""

    def test_pending_status_never_certification_ready(self):
        row = {"req_id": "T-pending", "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(row, final_acceptance_status="PENDING")
        # PENDING is "legal" (no rule violation) ...
        assert v.legal is True
        # ... but it is NEVER certification-ready
        assert is_certification_ready(v) is False

    def test_e0_baseline_never_certification_ready(self):
        """Even if a row says final=ACCEPTED, actual=E0 cannot satisfy any
        non-E0 required tier."""
        row = {"req_id": "T-e0", "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(
            row,
            actual_proof_depth="E0_REQUIREMENT_TEXT",
            final_acceptance_status="ACCEPTED",
        )
        # legality fails (ACCEPTED with weak proof) AND certification-ready fails
        assert v.legal is False
        assert is_certification_ready(v) is False

    def test_partial_never_certification_ready(self):
        row = {"req_id": "T-partial", "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(row, final_acceptance_status="PARTIAL",
                                acceptance_caveat="evidence pending")
        assert v.legal is True
        assert is_certification_ready(v) is False

    def test_blocked_never_certification_ready(self):
        row = {"req_id": "T-blocked", "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(row, final_acceptance_status="BLOCKED",
                                blocking_gap="cache schema not declared")
        assert v.legal is True
        assert is_certification_ready(v) is False

    def test_accepted_with_caveat_never_certification_ready(self):
        row = {"req_id": "T-caveat", "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(
            row,
            actual_proof_depth="E2_STATIC_CHECK",
            final_acceptance_status="ACCEPTED_WITH_CAVEAT",
            acceptance_caveat="pedagogical row",
        )
        assert v.legal is True
        # Strict: caveat'd rows are not strict-ACCEPTED
        assert is_certification_ready(v) is False

    def test_only_clean_accepted_at_or_above_required_is_ready(self):
        row = {"req_id": "T-clean", "claim_type": "INTEGRATED_RUNTIME",
               "required_proof_depth": "E6_INTEGRATED_RUNTIME_PROOF"}
        v_at = validate_acceptance(row, actual_proof_depth="E6_INTEGRATED_RUNTIME_PROOF",
                                   final_acceptance_status="ACCEPTED")
        v_above = validate_acceptance(row, actual_proof_depth="E7_REAL_OTEL_EXPORT",
                                      final_acceptance_status="ACCEPTED")
        assert is_certification_ready(v_at) is True
        assert is_certification_ready(v_above) is True

    def test_runtime_claim_allowed_defaults_false(self):
        """Closure #1 sub-rule: runtime_claim_allowed is False unless
        proof-depth conditions are met (PENDING + E0 always returns False)."""
        row = {"req_id": "T-rca-default", "claim_type": "INTEGRATED_RUNTIME",
               "required_proof_depth": "E6_INTEGRATED_RUNTIME_PROOF"}
        # PENDING baseline
        v_pending = validate_acceptance(row, final_acceptance_status="PENDING")
        assert derive_runtime_claim_allowed(v_pending) is False

        # ACCEPTED with sufficient depth + runtime claim_type
        v_ok = validate_acceptance(
            row,
            actual_proof_depth="E6_INTEGRATED_RUNTIME_PROOF",
            final_acceptance_status="ACCEPTED",
        )
        assert derive_runtime_claim_allowed(v_ok) is True

    def test_runtime_claim_blocked_for_static_claim_type(self):
        """STATIC_ENFORCEMENT rows never get runtime_claim_allowed=True
        regardless of metadata claims."""
        row = {"req_id": "T-static",
               "claim_type": "STATIC_ENFORCEMENT",
               "required_proof_depth": "E2_STATIC_CHECK"}
        v = validate_acceptance(
            row,
            actual_proof_depth="E2_STATIC_CHECK",
            final_acceptance_status="ACCEPTED",
        )
        # Row is certification-ready as a static row...
        assert is_certification_ready(v) is True
        # ... but does NOT carry runtime_claim_allowed=True
        assert derive_runtime_claim_allowed(v) is False

    def test_runtime_claim_blocked_for_doc_reference_only(self):
        row = {"req_id": "T-doc",
               "claim_type": "DOC_REFERENCE_ONLY",
               "required_proof_depth": "E1_SOURCE_MAPPING"}
        v = validate_acceptance(row, actual_proof_depth="E1_SOURCE_MAPPING",
                                final_acceptance_status="ACCEPTED")
        assert derive_runtime_claim_allowed(v) is False

    def test_baseline_universe_summary_blocks_certification(self):
        """W0 baseline: 86 PENDING rows cannot satisfy
        ``can_claim_runtime_certification``."""
        result = load_matrix()
        verdicts = apply_to_matrix(result.rows)  # baseline = all PENDING
        summary = summarize_certification_status(verdicts)
        assert summary.total_rows == CANONICAL_REQUIREMENT_COUNT
        assert summary.pending_rows == CANONICAL_REQUIREMENT_COUNT
        assert summary.ready_rows == 0
        assert summary.runtime_claim_allowed_rows == 0
        assert summary.can_claim_runtime_certification is False
        # All PENDING accumulates blocking reason
        assert summary.blocking_reasons.get("PENDING_NOT_CERTIFIED") == \
               CANONICAL_REQUIREMENT_COUNT


# ──────────────────────────────────────────────────────────────────────
# Closure check #2 — CI fail-closed scenarios are real
# ──────────────────────────────────────────────────────────────────────


def _run_verifier(script: str) -> tuple[int, str]:
    """Invoke a verifier script and return (returncode, stderr_tail)."""
    r = subprocess.run(
        [sys.executable, f"scripts/{script}"],
        capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
    )
    return r.returncode, (r.stdout + "\n" + r.stderr)[-2048:]


def _ensure_baseline():
    """Run the matrix-baseline verifiers so peer reports exist."""
    for s in (
        "verify_runtime_certification_matrix.py",
        "verify_runtime_certification_matrix_schema.py",
        "verify_runtime_certification_acceptance.py",
    ):
        subprocess.run(
            [sys.executable, f"scripts/{s}"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30, check=False,
        )


class TestSeededFailClosedClosure2:
    """Closure #2: each fail-closed scenario must trigger exit=2."""

    def test_seeded_override_forces_acceptance_failure(self):
        """Seed an evidence override claiming RTC-REQ-113 ACCEPTED with E2 depth
        even though required is E7 -> verifier MUST exit 2."""
        sidecar = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
        backup = sidecar.read_text(encoding="utf-8") if sidecar.exists() else None
        try:
            ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
            sidecar.write_text(json.dumps({
                "actual_proof_depth": {"RTC-REQ-113": "E2_STATIC_CHECK"},
                "final_acceptance_status": {"RTC-REQ-113": "ACCEPTED"},
            }), encoding="utf-8")
            rc, _ = _run_verifier("verify_runtime_certification_acceptance.py")
            assert rc == 2
        finally:
            if backup is None:
                if sidecar.exists():
                    os.remove(sidecar)
            else:
                sidecar.write_text(backup, encoding="utf-8")
            _run_verifier("verify_runtime_certification_acceptance.py")

    def test_seeded_composition_to_e6_promotion_fails(self):
        """Seed an override claiming RTC-REQ-113 (E7 required) ACCEPTED with
        actual=E5_COMPOSITION_PROOF — must trigger
        COMPOSITION_PROOF_CANNOT_PROMOTE."""
        sidecar = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
        backup = sidecar.read_text(encoding="utf-8") if sidecar.exists() else None
        downgraded_path = ARTIFACTS_DIR / "downgraded_rows_report.json"
        try:
            sidecar.write_text(json.dumps({
                "actual_proof_depth": {"RTC-REQ-113": "E5_COMPOSITION_PROOF"},
                "final_acceptance_status": {"RTC-REQ-113": "ACCEPTED"},
            }), encoding="utf-8")
            rc, _ = _run_verifier("verify_runtime_certification_acceptance.py")
            assert rc == 2
            dr = json.loads(downgraded_path.read_text(encoding="utf-8"))
            kinds = [
                viol
                for row in dr["downgraded_rows"]
                for viol in row.get("rule_violations", [])
            ]
            assert "COMPOSITION_PROOF_CANNOT_PROMOTE" in kinds, \
                f"expected COMPOSITION_PROOF_CANNOT_PROMOTE, got {kinds}"
        finally:
            if backup is None:
                if sidecar.exists():
                    os.remove(sidecar)
            else:
                sidecar.write_text(backup, encoding="utf-8")
            _run_verifier("verify_runtime_certification_acceptance.py")

    def test_seeded_source_divergence_fails(self):
        """Tamper a peer report's row_count to trigger SOURCE_DIVERGENCE."""
        _ensure_baseline()
        target = ARTIFACTS_DIR / "schema_validation_report.json"
        backup = target.read_text(encoding="utf-8")
        try:
            data = json.loads(backup)
            data["row_count"] = 0  # extreme divergence
            target.write_text(json.dumps(data), encoding="utf-8")
            rc, _ = _run_verifier("verify_source_divergence.py")
            assert rc == 2
            report = json.loads((ARTIFACTS_DIR / "source_divergence_report.json").read_text(encoding="utf-8"))
            assert report["expected_fail_reason"] == "SOURCE_DIVERGENCE"
        finally:
            target.write_text(backup, encoding="utf-8")
            _run_verifier("verify_source_divergence.py")

    def test_seeded_payload_hash_mismatch_fails(self):
        """Manifest with deliberately wrong hash must trigger
        PAYLOAD_HASH_MISMATCH and exit 2."""
        manifest_path = ARTIFACTS_DIR / "artifact_manifest.json"
        backup = manifest_path.read_text(encoding="utf-8") if manifest_path.exists() else None
        try:
            manifest_path.write_text(json.dumps({
                "artifacts": [{
                    "artifact_id": "csv_seed",
                    "payload_path": "docs/reference/contracts/certification/runtime_certification_requirements_100_percent_hardened.csv",
                    "expected_hash": "0" * 64,  # bogus
                }]
            }), encoding="utf-8")
            rc, _ = _run_verifier("verify_artifact_payload_hashes.py")
            assert rc == 2
            report = json.loads((ARTIFACTS_DIR / "artifact_payload_hash_report.json").read_text(encoding="utf-8"))
            assert report["expected_fail_reason"] == "PAYLOAD_HASH_MISMATCH"
        finally:
            if backup is None:
                if manifest_path.exists():
                    os.remove(manifest_path)
            else:
                manifest_path.write_text(backup, encoding="utf-8")
            _run_verifier("verify_artifact_payload_hashes.py")

    def test_seeded_bad_csv_fails_load(self):
        """A CSV missing a required column must fail-close at the loader."""
        from agentic_core.runtime.prove_requirements.matrix_loader import (
            MatrixLoadError,
        )
        with tempfile.TemporaryDirectory() as td:
            bad_csv = Path(td) / "bad.csv"
            cols_short = [c for c in REQUIRED_COLUMNS if c != "claim_type"]
            with bad_csv.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=cols_short)
                w.writeheader()
                w.writerow({c: "x" for c in cols_short})
            with pytest.raises(MatrixLoadError) as ei:
                load_matrix(path=bad_csv)
            assert "MISSING_COLUMNS" in str(ei.value)


# ──────────────────────────────────────────────────────────────────────
# Closure check #3 — No W0 report uses runtime-certification language
# ──────────────────────────────────────────────────────────────────────


class TestNoOverclaimLanguageClosure3:
    """Closure #3: W0 reports may say PASS but never 'runtime certified'."""

    def test_language_discipline_verifier_passes_baseline(self):
        rc, output = _run_verifier("verify_w0_language_discipline.py")
        assert rc == 0, f"language-discipline verifier failed unexpectedly:\n{output}"
        report_path = ARTIFACTS_DIR / "w0_language_discipline_report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report["status"] == "PASS"
        assert report["findings"] == []

    def test_seeded_runtime_certified_phrase_fails(self):
        """Plant a forbidden phrase in a sibling report and confirm the
        language verifier flags it."""
        target = ARTIFACTS_DIR / "schema_validation_report.json"
        backup = target.read_text(encoding="utf-8")
        try:
            data = json.loads(backup)
            data["overclaim_seed"] = "this is 100% runtime certified"
            target.write_text(json.dumps(data), encoding="utf-8")
            rc, _ = _run_verifier("verify_w0_language_discipline.py")
            assert rc == 2
            report = json.loads(
                (ARTIFACTS_DIR / "w0_language_discipline_report.json").read_text(encoding="utf-8")
            )
            assert report["status"] == "FAIL_CLOSED"
            assert any("RUNTIME_CERTIFIED_OVERCLAIM" in
                       (h.get("code", "") for h in f.get("hits", []))
                       for f in report["findings"]) or \
                   len(report["findings"]) > 0
        finally:
            target.write_text(backup, encoding="utf-8")
            _run_verifier("verify_w0_language_discipline.py")

    @pytest.mark.parametrize("forbidden", [
        "semantic cache certified",
        "OTEL certified",
        "replay certified",
        "fully certified",
        "production certified",
    ])
    def test_each_forbidden_phrase_triggers_fail_closed(self, forbidden):
        target = ARTIFACTS_DIR / "schema_validation_report.json"
        backup = target.read_text(encoding="utf-8")
        try:
            data = json.loads(backup)
            data["overclaim_seed"] = forbidden
            target.write_text(json.dumps(data), encoding="utf-8")
            rc, _ = _run_verifier("verify_w0_language_discipline.py")
            assert rc == 2, f"forbidden phrase '{forbidden}' did not trigger fail-closed"
        finally:
            target.write_text(backup, encoding="utf-8")
            _run_verifier("verify_w0_language_discipline.py")


# ──────────────────────────────────────────────────────────────────────
# Closure check #4 — Canonical CSV path
# ──────────────────────────────────────────────────────────────────────


class TestCanonicalPathClosure4:
    def test_canonical_path_matches_user_mandate(self):
        expected = (
            REPO_ROOT
            / "docs" / "reference" / "contracts" / "certification"
            / "runtime_certification_requirements_100_percent_hardened.csv"
        )
        assert CANONICAL_CSV_PATH == expected
        assert CANONICAL_CSV_PATH.exists()


# ──────────────────────────────────────────────────────────────────────
# Closure check #5 — All W1-W4 rows remain PENDING/PARTIAL/BLOCKED
# ──────────────────────────────────────────────────────────────────────


class TestEvidenceSidecarsAbsentClosure5:
    def test_no_runtime_evidence_overrides_in_w0_baseline(self):
        """W0 baseline must NOT carry a runtime_evidence_overrides.json
        sidecar. Future waves create it; W0 stays clean."""
        sidecar = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
        # If a previous test left it behind, allow it but confirm it is empty
        # of runtime-tier overrides (the test fixtures restore baseline at
        # teardown, so this is mainly a sanity check).
        if sidecar.exists():
            data = json.loads(sidecar.read_text(encoding="utf-8"))
            actual_overrides = data.get("actual_proof_depth", {}) or {}
            for rid, depth in actual_overrides.items():
                # Only static tiers are allowed in W0 era; any runtime tier
                # is a violation of the W1-rows-stay-PENDING rule
                assert depth in ("E0_REQUIREMENT_TEXT", "E1_SOURCE_MAPPING",
                                 "E2_STATIC_CHECK", ""), (
                    f"row {rid} carries runtime-tier override {depth} in W0 baseline"
                )

    def test_all_rows_pending_in_w0_baseline(self):
        """In the W0 baseline, every row of the canonical 86 must be
        PENDING (final_acceptance_status). No row leaks into ACCEPTED."""
        # Ensure no override sidecar interferes
        sidecar = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
        if sidecar.exists():
            os.remove(sidecar)
        # Re-run acceptance verifier to refresh the report
        _run_verifier("verify_runtime_certification_acceptance.py")
        report = json.loads((ARTIFACTS_DIR / "acceptance_legality_report.json").read_text(encoding="utf-8"))
        assert report["row_count"] == CANONICAL_REQUIREMENT_COUNT
        verdict_rows = report["verdicts"]
        statuses = {r["final_acceptance_status"] for r in verdict_rows}
        assert statuses == {"PENDING"}, (
            f"W0 baseline must be all-PENDING, found other statuses: {statuses}"
        )

    def test_w1_w4_rows_not_yet_certification_ready(self):
        """Closure #5: W1-W4 rows (semantic cache, OTel, replay, integrated
        runtime, production-dependency) cannot be certification-ready until
        their evidence sidecars exist. W0 has no sidecars => 0 ready."""
        sidecar = ARTIFACTS_DIR / "runtime_evidence_overrides.json"
        if sidecar.exists():
            os.remove(sidecar)
        result = load_matrix()
        # Filter to rows whose required tier is E5+ (i.e., W1+ scope)
        runtime_tier_rows = [
            r for r in result.rows
            if r.get("required_proof_depth", "") in (
                "E5_COMPOSITION_PROOF",
                "E6_INTEGRATED_RUNTIME_PROOF",
                "E7_REAL_OTEL_EXPORT",
                "E8_REPLAY_DETERMINISM",
                "E9_PRODUCTION_DEPENDENCY_PROOF",
            )
        ]
        # The hardened CSV declares 22 such rows (1 + 8 + 5 + 3 + 5)
        assert len(runtime_tier_rows) >= 15, \
               f"expected >=15 runtime-tier rows, found {len(runtime_tier_rows)}"
        verdicts = apply_to_matrix(runtime_tier_rows)
        ready = [v for v in verdicts if is_certification_ready(v)]
        assert ready == [], \
               f"W1-W4 runtime-tier rows must NOT be certification-ready in W0 baseline, found {len(ready)}"
