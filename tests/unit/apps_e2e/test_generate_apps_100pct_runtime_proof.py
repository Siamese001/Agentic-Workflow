"""W6 of plan apps-fort-knox-parity-c5d9a3 \u2014 consolidated proof tests.

Covers tools/certification/generate_apps_100pct_runtime_proof.py.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.certification import generate_apps_100pct_runtime_proof as gen

REPO_ROOT = Path(__file__).resolve().parents[3]


# ----------------------------- synthetic workspace -----------------------------

def _write_synthetic_tree(tmp_path: Path) -> dict:
    """Materialize a minimal apps_e2e/ + certification/ tree under tmp_path."""
    apps_dir = tmp_path / "artifacts" / "certification" / "apps_e2e"
    apps_dir.mkdir(parents=True)
    cert_dir = tmp_path / "certification"
    schemas_dir = cert_dir / "schemas"
    schemas_dir.mkdir(parents=True)

    # Catalog + schema
    (cert_dir / "apps_e2e_requirements_source.json").write_text(
        json.dumps({
            "schema_version": "apps_e2e_fortknox-v1",
            "positive_control_req_id": "APPS-REQ-001",
            "requirements": [
                {"req_id": f"APPS-REQ-{i:03d}"} for i in range(1, 4)
            ],
        }, sort_keys=True),
        encoding="utf-8",
    )
    (schemas_dir / "apps_e2e_requirements.schema.json").write_text("{}", encoding="utf-8")
    (schemas_dir / "apps_evidence_assertion.schema.json").write_text("{}", encoding="utf-8")

    # Assertions JSONL
    assertions = [
        {"assertion_id": f"ASRT-{i}", "assertion_result": "PASS", "req_id": "APPS-REQ-001"}
        for i in range(3)
    ]
    (cert_dir / "apps_evidence_assertions.jsonl").write_text(
        "\n".join(json.dumps(a) for a in assertions) + "\n",
        encoding="utf-8",
    )

    # Signoff report + sidecars
    signoff = {
        "trust_level": "SIGNED_OFF_WITH_WAIVERS",
        "positive_control_status": "PASS",
        "compiler_path": "scripts/compile_apps_e2e_signoff.py",
        "compiler_sha256": "a" * 64,
        "compiler_version": "test",
        "git_commit": "abc",
        "git_dirty": False,
        "row_digest": "b" * 64,
        "evidence_digest": "c" * 64,
        "summary": {
            "total": 3, "signed_off": 1, "signed_off_with_waiver": 2,
            "blocked": 0, "not_verified": 0, "percent_signed_off": 100.0,
            "by_claim_type": {},
        },
    }
    (apps_dir / "apps_e2e_signoff_report.json").write_text(
        json.dumps(signoff, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    sha = hashlib.sha256((apps_dir / "apps_e2e_signoff_report.json").read_bytes()).hexdigest()
    (apps_dir / "apps_e2e_signoff_report.sha256").write_text(
        f"{sha}  apps_e2e_signoff_report.json\n", encoding="utf-8"
    )
    (apps_dir / "apps_e2e_signoff_report.merkle.json").write_text(
        json.dumps({"root": "d" * 64, "leaf_count": 3}, sort_keys=True),
        encoding="utf-8",
    )

    # Signature envelope
    (apps_dir / "apps_e2e_signoff_report.signature.json").write_text(
        json.dumps({
            "signature_algorithm": "ed25519",
            "signature_verification_status": "VERIFIED",
            "signer_identity": "TEST_SIGNER:ed25519:cafebabe",
            "signing_timestamp_utc": "2026-05-02T20:00:00Z",
            "report_sha256": sha,
            "merkle_root": "d" * 64,
            "report_trust_level": "SIGNED_OFF_WITH_WAIVERS",
        }, sort_keys=True),
        encoding="utf-8",
    )

    # Mutation report
    (apps_dir / "apps_mutation_rejection_report.json").write_text(
        json.dumps({
            "schema_version": "apps_mutation_rejection_report-v1",
            "driver_path": "tools/cert/apps_e2e/apps_mutation_driver.py",
            "summary": {
                "total": 88, "rejected": 85, "accepted": 0,
                "skipped_not_applicable": 3, "rejection_rate": 1.0,
                "tamper_class_count": 11,
            },
        }, sort_keys=True),
        encoding="utf-8",
    )

    # Verifier report
    (apps_dir / "verifier_report.json").write_text(
        json.dumps({
            "verifier_report_schema_version": "apps_e2e_verifier_report/2026-05-02/v1",
            "exit_code": 0,
            "mode": "strict",
            "rows": [
                {"app_name": "apps_alpha", "certification_level": "SPINE_COMPLETE_CERTIFIED"},
                {"app_name": "apps_beta", "certification_level": "WAIVED_NOT_RUNTIME_APP"},
            ],
            "summary": {"n_apps": 2, "n_pass": 2, "n_fail": 0},
        }, sort_keys=True),
        encoding="utf-8",
    )

    # Matrix
    (apps_dir / "apps_e2e_matrix.json").write_text(
        json.dumps({
            "schema_version": "apps_e2e_matrix/2026-05-02/v1",
            "apps": [
                {"app_name": "apps_alpha"},
                {"app_name": "apps_beta"},
            ],
        }, sort_keys=True),
        encoding="utf-8",
    )

    # Per-app dirs with proof bundle
    (apps_dir / "apps_alpha").mkdir()
    (apps_dir / "apps_alpha" / "apps_alpha_e2e_proof.json").write_text(
        json.dumps({
            "app_name": "apps_alpha",
            "certification_level": "SPINE_COMPLETE_CERTIFIED",
            "exit_code": 0,
            "synthetic_trace_detected": False,
            "mock_mode_detected": False,
            "fixture_runtime_mode": False,
            "runtime_mode": "governed_spine_active",
        }, sort_keys=True),
        encoding="utf-8",
    )
    (apps_dir / "apps_beta").mkdir()
    # apps_beta is waived \u2014 bundle present but level absent
    (apps_dir / "apps_beta" / "apps_beta_e2e_proof.json").write_text(
        json.dumps({"app_name": "apps_beta", "exit_code": 0}, sort_keys=True),
        encoding="utf-8",
    )

    return {"root": tmp_path, "apps_dir": apps_dir, "cert_dir": cert_dir}


@pytest.fixture
def synthetic(tmp_path, monkeypatch):
    tree = _write_synthetic_tree(tmp_path)
    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gen, "APPS_E2E_DIR", tree["apps_dir"])
    monkeypatch.setattr(gen, "CERT_DIR", tree["cert_dir"])
    monkeypatch.setattr(gen, "OUT_PATH", tree["apps_dir"] / "APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json")
    return tree


# ----------------------------- tests -----------------------------

def test_build_bundle_returns_dict_with_required_top_keys(synthetic):
    bundle = gen.build_bundle(skip_live_verify=True)
    required = {
        "schema_version", "generator", "generated_at_utc", "headline_claims",
        "catalog", "assertions", "signoff", "signature", "mutation_rejection",
        "verifier_report", "matrix", "per_app", "live_signature_re_verify",
    }
    assert required.issubset(bundle.keys())


def test_headline_all_gates_pass_on_clean_inputs(synthetic):
    bundle = gen.build_bundle(skip_live_verify=True)
    h = bundle["headline_claims"]
    assert h["all_gates_pass"] is True
    assert h["canary_pass"] is True
    assert h["signature_verified"] is True
    assert h["mutation_zero_accepts"] is True
    assert h["trust_in_signed_set"] is True


def test_per_app_section_cross_references_verifier_report(synthetic):
    bundle = gen.build_bundle(skip_live_verify=True)
    rows = {r["app_name"]: r for r in bundle["per_app"]}
    assert rows["apps_alpha"]["certification_level"] == "SPINE_COMPLETE_CERTIFIED"
    # apps_beta has no level in its bundle, but verifier_report says WAIVED \u2014 cross-ref must pick that up
    assert rows["apps_beta"]["certification_level"] == "WAIVED_NOT_RUNTIME_APP"


def test_n_apps_certified_and_waived_counts(synthetic):
    bundle = gen.build_bundle(skip_live_verify=True)
    h = bundle["headline_claims"]
    assert h["n_apps_total"] == 2
    assert h["n_apps_certified"] == 1
    assert h["n_apps_waived"] == 1


def test_main_writes_file_and_returns_zero(synthetic):
    out = synthetic["apps_dir"] / "APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json"
    rc = gen.main(["--out", str(out), "--skip-live-verify", "--quiet"])
    assert rc == 0
    assert out.exists()
    bundle = json.loads(out.read_text(encoding="utf-8"))
    assert bundle["headline_claims"]["all_gates_pass"] is True


def test_main_returns_two_when_signature_not_verified(synthetic):
    """Tamper signature envelope status \u2192 main exits 2 (gates fail)."""
    sig_path = synthetic["apps_dir"] / "apps_e2e_signoff_report.signature.json"
    sig = json.loads(sig_path.read_text(encoding="utf-8"))
    sig["signature_verification_status"] = "INVALID"
    sig_path.write_text(json.dumps(sig, sort_keys=True), encoding="utf-8")

    rc = gen.main(["--out", str(synthetic["apps_dir"] / "out.json"),
                   "--skip-live-verify", "--quiet"])
    assert rc == 2


def test_main_returns_two_when_canary_fails(synthetic):
    rep_path = synthetic["apps_dir"] / "apps_e2e_signoff_report.json"
    rep = json.loads(rep_path.read_text(encoding="utf-8"))
    rep["positive_control_status"] = "FAIL"
    rep_path.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rc = gen.main(["--out", str(synthetic["apps_dir"] / "out.json"),
                   "--skip-live-verify", "--quiet"])
    assert rc == 2


def test_main_returns_two_when_mutation_accepted(synthetic):
    mut_path = synthetic["apps_dir"] / "apps_mutation_rejection_report.json"
    mut = json.loads(mut_path.read_text(encoding="utf-8"))
    mut["summary"]["accepted"] = 1
    mut_path.write_text(json.dumps(mut, sort_keys=True), encoding="utf-8")

    rc = gen.main(["--out", str(synthetic["apps_dir"] / "out.json"),
                   "--skip-live-verify", "--quiet"])
    assert rc == 2


def test_bundle_is_deterministic_modulo_wallclock(synthetic):
    """Two consecutive runs must produce byte-identical output except for
    `generated_at_utc` and live_signature_re_verify.duration_ms."""
    b1 = gen.build_bundle(skip_live_verify=True)
    b2 = gen.build_bundle(skip_live_verify=True)
    for b in (b1, b2):
        b.pop("generated_at_utc", None)
    assert json.dumps(b1, sort_keys=True) == json.dumps(b2, sort_keys=True)


def test_assertions_section_counts_results(synthetic):
    bundle = gen.build_bundle(skip_live_verify=True)
    a = bundle["assertions"]
    assert a["present"] is True
    assert a["line_count"] == 3
    assert a["result_counts"]["PASS"] == 3


# ----------------------------- live smoke -----------------------------

@pytest.mark.skipif(
    not (REPO_ROOT / "artifacts" / "certification" / "apps_e2e" / "apps_e2e_signoff_report.json").exists(),
    reason="live signoff not present",
)
def test_live_bundle_all_gates_pass():
    """Full live run against current repo state (post-W5)."""
    bundle = gen.build_bundle(skip_live_verify=False)
    h = bundle["headline_claims"]
    assert h["canary_pass"] is True
    assert h["signature_verified"] is True
    assert h["mutation_zero_accepts"] is True
    assert h["trust_in_signed_set"] is True
    assert h["all_gates_pass"] is True
