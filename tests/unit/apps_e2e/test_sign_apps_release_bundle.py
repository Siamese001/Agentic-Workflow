"""W5 of plan apps-fort-knox-parity-c5d9a3 \u2014 signer + verifier tests.

Covers:
  tools/cert/apps_e2e/sign_apps_release_bundle.py
  tools/cert/apps_e2e/verify_apps_release_signature.py
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from tools.cert.apps_e2e import sign_apps_release_bundle as signer
from tools.cert.apps_e2e import verify_apps_release_signature as verifier

REPO_ROOT = Path(__file__).resolve().parents[3]


def _minimal_report(trust_level: str = "SIGNED_OFF_WITH_WAIVERS",
                    canary: str = "PASS") -> dict:
    return {
        "schema_version": "apps_e2e_fortknox-v1",
        "compiler_version": "apps_e2e_fortknox-v1.0",
        "compiler_path": "scripts/compile_apps_e2e_signoff.py",
        "run_timestamp_utc": "2026-05-02T20:00:00+00:00",
        "source_repo_root": "/test",
        "git_commit": "abc",
        "git_dirty": False,
        "requirements_source_sha256": "0" * 64,
        "evidence_assertions_sha256": "1" * 64,
        "row_digest": "2" * 64,
        "evidence_digest": "3" * 64,
        "rows": [],
        "summary": {
            "total": 1,
            "signed_off": 1,
            "blocked": 0,
            "not_verified": 0,
            "percent_signed_off": 100.0,
        },
        "trust_level": trust_level,
        "positive_control_status": canary,
    }


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    """Materialize a tmp apps_e2e/ tree with a minimal report + sidecar."""
    apps_dir = tmp_path / "apps_e2e"
    apps_dir.mkdir(parents=True)
    # Copy real keypair into the tmp repo so the signer sees a stable key.
    real_repo = REPO_ROOT
    pub_src = real_repo / signer.PUBKEY_REL
    priv_src = real_repo / signer.PRIVKEY_REL
    if not (pub_src.exists() and priv_src.exists()):
        pytest.skip("real keypair not present; run signer once to materialize")
    (tmp_path / signer.PUBKEY_REL.parent).mkdir(parents=True, exist_ok=True)
    (tmp_path / signer.PRIVKEY_REL.parent).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pub_src, tmp_path / signer.PUBKEY_REL)
    shutil.copyfile(priv_src, tmp_path / signer.PRIVKEY_REL)

    monkeypatch.setattr(signer, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(signer, "APPS_E2E_DIR", apps_dir)
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(verifier, "APPS_E2E_DIR", apps_dir)
    return {"root": tmp_path, "apps_dir": apps_dir}


def _write_report(apps_dir: Path, report: dict) -> Path:
    p = apps_dir / signer.REPORT_NAME
    p.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # sidecar
    import hashlib
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    (apps_dir / signer.SHA_NAME).write_text(f"{sha}  {p.name}\n", encoding="utf-8")
    return p


# ----------------------------- signer accept paths -----------------------------

def test_sign_writes_envelope_with_valid_signature(sandbox):
    _write_report(sandbox["apps_dir"], _minimal_report())
    rc = signer.main([])
    assert rc == 0
    env_path = sandbox["apps_dir"] / signer.ENVELOPE_NAME
    assert env_path.exists()
    env = json.loads(env_path.read_text(encoding="utf-8"))
    assert env["signature_algorithm"] == "ed25519"
    assert env["signature_verification_status"] == "VERIFIED"
    assert env["signer_identity"].startswith("DEVELOPMENT_SIGNER:ed25519:")


def test_sign_envelope_round_trip_verifies(sandbox):
    _write_report(sandbox["apps_dir"], _minimal_report())
    assert signer.main([]) == 0
    rc = verifier.main(["--quiet"])
    assert rc == 0


def test_sign_idempotent_with_signed_proof(sandbox):
    """Re-signing a report at SIGNED_PROOF must not fail."""
    _write_report(sandbox["apps_dir"], _minimal_report(trust_level="SIGNED_PROOF"))
    assert signer.main([]) == 0
    assert signer.main([]) == 0  # idempotent


# ----------------------------- signer refuse paths -----------------------------

def test_sign_refuses_development_proof_by_default(sandbox, capsys):
    _write_report(sandbox["apps_dir"], _minimal_report(trust_level="DEVELOPMENT_PROOF"))
    rc = signer.main([])
    assert rc == 1
    err = capsys.readouterr().err
    assert "DEVELOPMENT_PROOF" in err or "trust_level" in err


def test_sign_refuses_canary_fail(sandbox, capsys):
    _write_report(sandbox["apps_dir"], _minimal_report(canary="FAIL"))
    rc = signer.main([])
    assert rc == 1
    err = capsys.readouterr().err
    assert "positive_control_status" in err


def test_sign_refuses_when_report_missing(sandbox, capsys):
    rc = signer.main([])
    assert rc == 1
    err = capsys.readouterr().err
    assert "report missing" in err


# ----------------------------- verifier reject paths -----------------------------

def _sign_then_tamper_report(apps_dir: Path, transform):
    """Helper: sign, then apply transform to the report bytes, return paths."""
    _write_report(apps_dir, _minimal_report())
    assert signer.main([]) == 0
    report_path = apps_dir / signer.REPORT_NAME
    raw = report_path.read_bytes()
    report_path.write_bytes(transform(raw))
    return report_path


def test_verify_rejects_tampered_report_bytes(sandbox, capsys):
    _sign_then_tamper_report(
        sandbox["apps_dir"], lambda raw: raw.replace(b'"total": 1', b'"total": 9', 1)
    )
    rc = verifier.main(["--quiet"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "FAIL" in err


def test_verify_rejects_corrupted_signature_value(sandbox, capsys):
    _write_report(sandbox["apps_dir"], _minimal_report())
    assert signer.main([]) == 0
    env_path = sandbox["apps_dir"] / signer.ENVELOPE_NAME
    env = json.loads(env_path.read_text(encoding="utf-8"))
    # Flip a base64 char in the signature
    sig = env["signature_value"]
    env["signature_value"] = ("A" if sig[0] != "A" else "B") + sig[1:]
    env_path.write_text(json.dumps(env, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rc = verifier.main(["--quiet"])
    assert rc == 2


def test_verify_rejects_swapped_pubkey(sandbox, capsys):
    """If envelope's embedded pubkey != on-disk pubkey, refuse."""
    _write_report(sandbox["apps_dir"], _minimal_report())
    assert signer.main([]) == 0
    env_path = sandbox["apps_dir"] / signer.ENVELOPE_NAME
    env = json.loads(env_path.read_text(encoding="utf-8"))
    # Replace embedded pub with a fake PEM blob
    env["signer_public_key_pem"] = (
        "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAFAKE_KEY_BYTES_FAKE_KEY_BYTES_FAKE_KEY_BYTES==\n-----END PUBLIC KEY-----\n"
    )
    env_path.write_text(json.dumps(env, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rc = verifier.main(["--quiet"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "key swap" in err or "disagree" in err


def test_verify_rejects_canary_fail_in_report(sandbox, capsys):
    """Verifier must refuse a report whose canary is not PASS even if signature is valid."""
    # Write a canary-PASS report so we get past the signer's pre-check
    _write_report(sandbox["apps_dir"], _minimal_report(canary="PASS"))
    assert signer.main([]) == 0
    # Now mutate the report to canary=FAIL after signing (simulates a tamper)
    report_path = sandbox["apps_dir"] / signer.REPORT_NAME
    report_path.write_bytes(
        report_path.read_bytes().replace(b'"PASS"', b'"FAIL"', 1)
    )
    rc = verifier.main(["--quiet"])
    # Either sha drift or canary check fires \u2014 either way fail
    assert rc == 2


# ----------------------------- signature envelope shape -----------------------------

def test_envelope_contains_required_fields(sandbox):
    _write_report(sandbox["apps_dir"], _minimal_report())
    assert signer.main([]) == 0
    env = json.loads((sandbox["apps_dir"] / signer.ENVELOPE_NAME).read_text(encoding="utf-8"))
    required = {
        "schema_version", "envelope_generated_at_utc", "report_filename",
        "report_sha256", "signed_bytes_sha256", "signer_identity",
        "signing_timestamp_utc", "signature_algorithm", "signature_value",
        "signature_value_encoding", "signer_public_key_pem",
        "signature_verification_status", "report_trust_level", "report_row_count",
    }
    missing = required - env.keys()
    assert not missing, f"envelope missing fields: {missing}"


# ----------------------------- live smoke -----------------------------

@pytest.mark.skipif(
    not (REPO_ROOT / "artifacts" / "certification" / "apps_e2e" / "apps_e2e_signoff_report.json").exists(),
    reason="live signoff report not present",
)
def test_live_sign_then_verify():
    rc_sign = signer.main([])
    assert rc_sign == 0
    rc_ver = verifier.main(["--quiet"])
    assert rc_ver == 0
