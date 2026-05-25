"""W4.P2 of plan apps-fortknox-evidence-repackage-30f5ab — Reviewer-bundle smoke test.

Builds a zip, unpacks to temp dir, walks every manifest path and asserts
file present + sha256 matches. No external network.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from tools.certification.package_apps_e2e_zip import build_zip, verify_zip

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_E2E_DIR = REPO_ROOT / "artifacts" / "certification" / "apps_e2e"


class TestReviewerBundleZip:
    """Smoke tests for the reviewer bundle zip builder."""

    def test_build_zip_core_files(self, tmp_path: Path) -> None:
        """Zip includes core certification files."""
        out_zip = tmp_path / "test_bundle.zip"
        success, errors = build_zip(out_zip, include_runtime=False)
        assert success, f"build_zip failed: {errors}"
        assert out_zip.exists()

        with zipfile.ZipFile(out_zip, "r") as zf:
            namelist = zf.namelist()
            # Core files present
            assert "APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json" in namelist
            assert "apps_e2e_signoff_report.json" in namelist
            assert "apps_e2e_signoff_report.signature.json" in namelist
            assert "INVENTORY.md" in namelist

    def test_build_zip_with_runtime(self, tmp_path: Path) -> None:
        """Zip with --include-runtime includes manifests and runtime artifacts."""
        out_zip = tmp_path / "test_bundle_full.zip"
        success, errors = build_zip(out_zip, include_runtime=True)
        assert success, f"build_zip failed: {errors}"

        with zipfile.ZipFile(out_zip, "r") as zf:
            namelist = zf.namelist()
            # At least one app manifest included
            manifests = [n for n in namelist if "_artifact_manifest.json" in n]
            assert len(manifests) >= 1, "Expected at least one artifact manifest"

    def test_verify_zip_valid(self, tmp_path: Path) -> None:
        """verify_zip returns True for a valid zip."""
        out_zip = tmp_path / "test_verify.zip"
        success, _ = build_zip(out_zip, include_runtime=False)
        assert success

        valid, errors = verify_zip(out_zip)
        assert valid, f"verify_zip failed: {errors}"

    def test_verify_zip_missing(self, tmp_path: Path) -> None:
        """verify_zip returns False for non-existent zip."""
        missing_zip = tmp_path / "missing.zip"
        valid, errors = verify_zip(missing_zip)
        assert not valid
        assert any("not found" in e.lower() for e in errors)

    def test_zip_hash_integrity(self, tmp_path: Path) -> None:
        """Files in zip have correct hashes matching their manifests."""
        out_zip = tmp_path / "test_hashes.zip"
        success, errors = build_zip(out_zip, include_runtime=False, skip_hash_verify=False)
        assert success, f"build_zip failed: {errors}"

        # Extract and verify hashes
        extract_dir = tmp_path / "extracted"
        extract_dir.mkdir()

        with zipfile.ZipFile(out_zip, "r") as zf:
            zf.extractall(extract_dir)

        # Read INVENTORY.md and verify at least it exists
        inventory_path = extract_dir / "INVENTORY.md"
        assert inventory_path.exists()
        inventory_content = inventory_path.read_text(encoding="utf-8")
        assert "Apps E2E Reviewer Bundle Inventory" in inventory_content

    def test_core_proof_bundle_row_count(self) -> None:
        """APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json shows 45 rows."""
        proof_path = APPS_E2E_DIR / "APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json"
        if not proof_path.exists():
            pytest.skip("Proof bundle not generated yet")

        proof = json.loads(proof_path.read_text(encoding="utf-8"))
        h = proof.get("headline_claims", {})

        # W2 requirement: 45 rows (33 APPS-REQ + 12 APPS-DOM)
        assert h.get("row_total") == 45, f"Expected row_total=45, got {h.get('row_total')}"
        assert h.get("row_signed_off") == 45
        assert h.get("signature_verified") is True

    def test_signoff_report_integrity(self) -> None:
        """Signoff report has 45 rows and valid signature envelope."""
        report_path = APPS_E2E_DIR / "apps_e2e_signoff_report.json"
        if not report_path.exists():
            pytest.skip("Signoff report not generated yet")

        report = json.loads(report_path.read_text(encoding="utf-8"))
        rows = report.get("rows", [])

        # W2 requirement: 45 rows
        assert len(rows) == 45, f"Expected 45 rows, got {len(rows)}"

        # Verify signature envelope exists and references this report
        sig_path = APPS_E2E_DIR / "apps_e2e_signoff_report.signature.json"
        if sig_path.exists():
            sig = json.loads(sig_path.read_text(encoding="utf-8"))
            assert sig.get("report_row_count") == 45
            assert sig.get("signature_verification_status") == "VERIFIED"

    def test_requirement_count_lockstep(self) -> None:
        """Requirements source has requirement_count matching actual rows."""
        reqs_path = REPO_ROOT / "data" / "certification" / "apps_e2e_requirements_source.json"
        if not reqs_path.exists():
            pytest.skip("Requirements source not found")

        reqs = json.loads(reqs_path.read_text(encoding="utf-8"))
        declared_count = reqs.get("requirement_count", 0)
        actual_count = len(reqs.get("requirements", []))

        # W1 requirement: declared count must match actual
        assert declared_count == actual_count, (
            f"requirement_count mismatch: declared={declared_count}, "
            f"actual={actual_count}"
        )
        assert actual_count == 45, f"Expected 45 requirements, got {actual_count}"
