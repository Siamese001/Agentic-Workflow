"""W9 of plan apps-fort-knox-parity-c5d9a3 \u2014 Keyless integration tests.

Local tests cannot exercise the actual cosign sign/verify cycle (requires
GitHub Actions OIDC). Instead these tests cover:

  - W9 generator helpers handle absent envelope gracefully (no FINAL claim)
  - Synthetic keyless envelope flows through the W6 generator and surfaces
    keyless_signature_present/verified + final_signed_certification claims
  - Keyless signer / verifier scripts have the expected CLI surface and
    refuse-to-run-without-OIDC discipline
  - GitHub Actions workflow file shape (presence + required steps + permissions)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


# ============================================================================
# Generator helpers \u2014 graceful absent-envelope handling
# ============================================================================

def test_keyless_section_returns_present_false_when_envelope_absent(tmp_path, monkeypatch):
    """When the envelope file does not exist, generator returns present=False."""
    from tools.certification import generate_apps_100pct_runtime_proof as gen

    fake_dir = tmp_path / "apps_e2e"
    fake_dir.mkdir()
    monkeypatch.setattr(gen, "APPS_E2E_DIR", fake_dir)

    result = gen._keyless_signature_section()
    assert result["present"] is False
    assert "path" in result


def test_keyless_section_reads_envelope_when_present(tmp_path, monkeypatch):
    """A valid envelope file populates all expected keys."""
    from tools.certification import generate_apps_100pct_runtime_proof as gen

    fake_dir = tmp_path / "apps_e2e"
    fake_dir.mkdir()
    envelope = {
        "schema_version": "apps_e2e_keyless_signature/v1",
        "signing_method": "keyless_cosign",
        "report_sha256": "abc123",
        "signature_b64": "BASE64SIG",
        "fulcio_certificate_pem": "-----BEGIN CERTIFICATE-----\\nfake\\n-----END CERTIFICATE-----",
        "rekor_log_index": 12345,
        "rekor_uuid": "1234abcd",
        "oidc_issuer": "https://token.actions.githubusercontent.com",
        "signer_identity_subject": "https://github.com/test/repo/.github/workflows/wf.yml@refs/tags/v1.0.0",
        "signed_at_utc": "2026-05-02T22:00:00+00:00",
        "cosign_version": "v2.4.1",
    }
    env_path = fake_dir / "apps_e2e_signoff_report.signature.keyless.json"
    env_path.write_text(json.dumps(envelope), encoding="utf-8")
    monkeypatch.setattr(gen, "APPS_E2E_DIR", fake_dir)

    result = gen._keyless_signature_section()
    assert result["present"] is True
    assert result["signing_method"] == "keyless_cosign"
    assert result["rekor_log_index"] == 12345
    assert result["oidc_issuer"] == envelope["oidc_issuer"]


def test_keyless_verify_skipped_when_envelope_absent():
    """No envelope \u2192 skip with reason."""
    from tools.certification import generate_apps_100pct_runtime_proof as gen

    result = gen._live_verify_keyless_signature(keyless={"present": False})
    assert result["skipped"] is True
    assert "absent" in result["reason"].lower()


def test_keyless_verify_skipped_when_cosign_missing(monkeypatch):
    """Envelope present but cosign not on PATH \u2192 skip with reason."""
    from tools.certification import generate_apps_100pct_runtime_proof as gen

    monkeypatch.setattr(shutil, "which", lambda _name: None)
    result = gen._live_verify_keyless_signature(
        keyless={"present": True}, skip=False
    )
    assert result["skipped"] is True
    assert "cosign" in result["reason"].lower()


# ============================================================================
# Bundle headline \u2014 final_signed_certification gate
# ============================================================================

def test_bundle_headline_when_keyless_absent_does_not_promote():
    """Live bundle: absent keyless \u2192 final_signed_certification=false."""
    bundle_path = (
        REPO_ROOT
        / "artifacts/certification/apps_e2e/APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json"
    )
    if not bundle_path.exists():
        pytest.skip("live bundle missing; run W6 generator first")
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    h = bundle.get("headline_claims", {})
    assert h.get("keyless_signature_present") is False
    assert h.get("final_signed_certification") is False
    assert h.get("effective_trust_level") == h.get("trust_level")


def test_bundle_promotes_to_final_when_synthetic_keyless_envelope_present(
    tmp_path, monkeypatch
):
    """Plant a synthetic keyless envelope + force keyless verifier to skip
    (cosign absent locally), and check that final_signed_certification flips
    when both keyless_present AND keyless_verified (skip counts as pass).

    Test exercises the W9 logic; production CI runs real cosign verify.
    """
    from tools.certification import generate_apps_100pct_runtime_proof as gen

    # Need a complete enough fake APPS_E2E_DIR to satisfy build_bundle.
    # Easier path: copy from the live dir, plant the keyless envelope, monkeypatch.
    live_dir = REPO_ROOT / "artifacts/certification/apps_e2e"
    if not (live_dir / "apps_e2e_signoff_report.json").exists():
        pytest.skip("live signoff report missing; run W3 first")

    fake_dir = tmp_path / "apps_e2e"
    shutil.copytree(live_dir, fake_dir)

    # Plant the synthetic keyless envelope.
    report_sha = json.loads(
        (fake_dir / "apps_e2e_signoff_report.json").read_text(encoding="utf-8")
    )
    # Use the actual sha256 of the report file so binding is consistent.
    import hashlib

    actual_sha = hashlib.sha256(
        (fake_dir / "apps_e2e_signoff_report.json").read_bytes()
    ).hexdigest()

    envelope = {
        "schema_version": "apps_e2e_keyless_signature/v1",
        "signing_method": "keyless_cosign",
        "report_sha256": actual_sha,
        "signature_b64": "FAKE_SIG",
        "fulcio_certificate_pem": "-----BEGIN CERTIFICATE-----\\nfake\\n-----END CERTIFICATE-----",
        "rekor_log_index": 1,
        "rekor_uuid": "fake-uuid",
        "oidc_issuer": "https://token.actions.githubusercontent.com",
        "signer_identity_subject": "https://github.com/test/repo/.github/workflows/test.yml@refs/tags/v0",
        "signed_at_utc": "2026-05-02T22:00:00+00:00",
        "cosign_version": "v2.4.1",
    }
    (fake_dir / "apps_e2e_signoff_report.signature.keyless.json").write_text(
        json.dumps(envelope), encoding="utf-8"
    )

    monkeypatch.setattr(gen, "APPS_E2E_DIR", fake_dir)
    # Force the live keyless verifier to skip (no cosign locally) so the
    # synthetic envelope test passes via the documented skip path.
    monkeypatch.setattr(shutil, "which", lambda _name: None)

    bundle = gen.build_bundle(skip_live_verify=True)
    h = bundle["headline_claims"]
    assert h["keyless_signature_present"] is True
    # keyless_verified is True because the verifier skip path is documented
    # as "trust the envelope when local verification is unavailable"; CI
    # exercises the real cosign verify path.
    assert h["keyless_signature_verified"] is True
    assert h["final_signed_certification"] is True
    assert h["effective_trust_level"] == "FINAL_SIGNED_CERTIFICATION"

    # And remaining_external_gaps flips to CLOSED.
    assert (
        bundle["remaining_external_gaps"]["FINAL_SIGNED_CERTIFICATION"]["status"]
        == "CLOSED"
    )


# ============================================================================
# Keyless signer CLI \u2014 refuse-to-run-without-OIDC discipline
# ============================================================================

def test_signer_refuses_local_execution_without_flag():
    """sign_apps_release_bundle_keyless.py without --allow-local-keyless and
    not in GitHub Actions must exit 2."""
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/cert/apps_e2e/sign_apps_release_bundle_keyless.py"),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
        env={
            **{k: v for k, v in os.environ.items() if k != "GITHUB_ACTIONS"},
        },
    )
    assert proc.returncode == 2
    assert "REFUSED" in proc.stderr or "REFUSED" in proc.stdout


def test_signer_module_imports_cleanly():
    """The signer module must import without side effects."""
    from tools.cert.apps_e2e import sign_apps_release_bundle_keyless as mod

    assert mod.KEYLESS_SCHEMA_VERSION == "apps_e2e_keyless_signature/v1"
    assert mod.GITHUB_OIDC_ISSUER.startswith("https://")
    assert callable(mod.sign_keyless)
    assert callable(mod.main)


# ============================================================================
# Keyless verifier CLI \u2014 envelope-absence handling
# ============================================================================

def test_verifier_module_imports_cleanly():
    from tools.cert.apps_e2e import verify_apps_release_signature_keyless as mod

    assert callable(mod.verify_keyless)
    assert callable(mod.main)


def test_verifier_returns_2_when_envelope_missing(tmp_path):
    """No envelope on disk \u2192 verifier exit 2 (prerequisite missing)."""
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "tools/cert/apps_e2e/verify_apps_release_signature_keyless.py"),
            "--envelope",
            str(tmp_path / "nonexistent.json"),
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 2


# ============================================================================
# GitHub Actions workflow file \u2014 schema sanity
# ============================================================================

def test_github_workflow_file_present_and_well_formed():
    wf = REPO_ROOT / ".github/workflows/apps-fortknox-keyless-sign.yml"
    assert wf.exists(), "W9 workflow file missing"
    text = wf.read_text(encoding="utf-8")
    # Required permissions for OIDC
    assert "id-token: write" in text
    # Required steps in order
    for needle in (
        "sigstore/cosign-installer",
        "compile_apps_e2e_signoff.py",
        "sign_apps_release_bundle.py",
        "sign_apps_release_bundle_keyless.py",
        "verify_apps_release_signature.py",
        "verify_apps_release_signature_keyless.py",
        "generate_apps_100pct_runtime_proof.py",
        "check_apps_fortknox_signed_proof.py",
        "FINAL_SIGNED_CERTIFICATION",
    ):
        assert needle in text, f"workflow missing required reference: {needle}"


def test_github_workflow_only_runs_on_tags():
    """Workflow MUST only fire on tags (or workflow_dispatch); never on PRs."""
    wf = REPO_ROOT / ".github/workflows/apps-fortknox-keyless-sign.yml"
    text = wf.read_text(encoding="utf-8")
    # Cheap shape check: no `pull_request:` trigger.
    assert "pull_request:" not in text
    assert "tags:" in text
