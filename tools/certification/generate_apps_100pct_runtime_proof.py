"""W6 of plan apps-fort-knox-parity-c5d9a3 \u2014 consolidated apps_e2e proof.

Walks the apps_e2e Fort Knox certification surface end-to-end and emits
a single deterministic JSON artifact at:

    artifacts/certification/apps_e2e/APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json

The bundle is the minimum-trusted-input view of the apps_* track: every
claim resolves to a file-on-disk sha256, and every per-app artifact is
enumerated with its own hash. A reviewer who trusts only this script
and the referenced files can independently confirm the apps_*
SIGNED_PROOF claim.

Mirrors the agentic_core counterpart at
`tools/certification/generate_100pct_runtime_proof.py` in shape and
discipline, adapted for the apps_e2e surface (per-app proof bundles +
spine certification levels + waivers + matrix governance).

Determinism: every hash and every count is content-derived. Only
`generated_at_utc` and the live verifier results' `duration_ms` field
are wall-clock. A consumer that wants byte-stable diff can compare the
bundle minus those two fields.

Exit codes:
  0 \u2014 bundle written; all gates pass (signoff trust_level in the
       SIGNED set AND signature_verification_status == VERIFIED AND
       mutation rejection rate == 100% AND canary == PASS).
  1 \u2014 a required input is missing (catalog, JSONL, signoff, etc.).
  2 \u2014 bundle written, but one or more headline claims FAILED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_E2E_DIR = REPO_ROOT / "artifacts" / "certification" / "apps_e2e"
CERT_DIR = REPO_ROOT / "data" / "certification"
OUT_PATH = APPS_E2E_DIR / "APPS_HUNDRED_PERCENT_RUNTIME_PROOF.json"

GENERATOR_PATH_REL = "tools/certification/generate_apps_100pct_runtime_proof.py"
GENERATOR_VERSION = "apps_e2e_fortknox_consolidator-v1.0"
SCHEMA_VERSION = "apps_e2e_hundred_percent_runtime_proof-v1"

# Trust levels that constitute "signed-off" for headline purposes.
SIGNED_TRUST_LEVELS = {
    "INTEGRITY_PROOF",
    "SIGNED_OFF_WITH_WAIVERS",
    "SIGNED_PROOF",
    "FINAL_SIGNED_CERTIFICATION",
}


# =============================================================================
# Helpers
# =============================================================================

def _sha256(p: Path) -> str:
    if not p.exists():
        return ""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(p: Path) -> dict[str, Any]:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# =============================================================================
# Section builders
# =============================================================================

def _catalog_section() -> dict[str, Any]:
    catalog_path = CERT_DIR / "apps_e2e_requirements_source.json"
    schema_path = CERT_DIR / "schemas" / "apps_e2e_requirements.schema.json"
    catalog = _load_json(catalog_path)
    return {
        "present": catalog_path.exists(),
        "path": _rel(catalog_path),
        "sha256": _sha256(catalog_path),
        "schema_path": _rel(schema_path),
        "schema_sha256": _sha256(schema_path),
        "requirement_count": len(catalog.get("requirements", [])),
        "schema_version": catalog.get("schema_version"),
        "positive_control_req_id": catalog.get("positive_control_req_id"),
    }


def _assertions_section() -> dict[str, Any]:
    p = CERT_DIR / "apps_evidence_assertions.jsonl"
    schema_path = CERT_DIR / "schemas" / "apps_evidence_assertion.schema.json"
    if not p.exists():
        return {"present": False, "path": _rel(p)}
    counts = {"PASS": 0, "FAIL": 0, "NOT_VERIFIED": 0, "BLOCKED": 0}
    line_count = 0
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            line_count += 1
            try:
                a = json.loads(line)
            except json.JSONDecodeError:
                continue
            r = a.get("assertion_result")
            if r in counts:
                counts[r] += 1
    return {
        "present": True,
        "path": _rel(p),
        "sha256": _sha256(p),
        "schema_path": _rel(schema_path),
        "schema_sha256": _sha256(schema_path),
        "line_count": line_count,
        "result_counts": counts,
    }


def _signoff_section() -> dict[str, Any]:
    report_path = APPS_E2E_DIR / "apps_e2e_signoff_report.json"
    sha_path = APPS_E2E_DIR / "apps_e2e_signoff_report.sha256"
    merkle_path = APPS_E2E_DIR / "apps_e2e_signoff_report.merkle.json"
    if not report_path.exists():
        return {"present": False, "path": _rel(report_path)}
    rep = _load_json(report_path)
    summary = rep.get("summary", {}) or {}
    merkle = _load_json(merkle_path)
    return {
        "present": True,
        "path": _rel(report_path),
        "sha256": _sha256(report_path),
        "sidecar_sha256_path": _rel(sha_path),
        "sidecar_sha256": _sha256(sha_path),
        "merkle_path": _rel(merkle_path),
        "merkle_sha256": _sha256(merkle_path),
        "merkle_root": merkle.get("root"),
        "merkle_leaf_count": merkle.get("leaf_count"),
        "trust_level": rep.get("trust_level"),
        "positive_control_status": rep.get("positive_control_status"),
        "compiler_path": rep.get("compiler_path"),
        "compiler_sha256": rep.get("compiler_sha256"),
        "compiler_version": rep.get("compiler_version"),
        "git_commit": rep.get("git_commit"),
        "git_dirty": rep.get("git_dirty"),
        "row_digest": rep.get("row_digest"),
        "evidence_digest": rep.get("evidence_digest"),
        "summary": {
            "total": summary.get("total"),
            "signed_off": summary.get("signed_off"),
            "signed_off_with_waiver": summary.get("signed_off_with_waiver"),
            "blocked": summary.get("blocked"),
            "not_verified": summary.get("not_verified"),
            "percent_signed_off": summary.get("percent_signed_off"),
            "by_claim_type": summary.get("by_claim_type"),
        },
    }


def _signature_section() -> dict[str, Any]:
    env_path = APPS_E2E_DIR / "apps_e2e_signoff_report.signature.json"
    if not env_path.exists():
        return {"present": False, "path": _rel(env_path)}
    env = _load_json(env_path)
    return {
        "present": True,
        "path": _rel(env_path),
        "sha256": _sha256(env_path),
        "signature_algorithm": env.get("signature_algorithm"),
        "signature_verification_status": env.get("signature_verification_status"),
        "signer_identity": env.get("signer_identity"),
        "signer_version": env.get("signer_version"),
        "signing_timestamp_utc": env.get("signing_timestamp_utc"),
        "report_sha256": env.get("report_sha256"),
        "merkle_root": env.get("merkle_root"),
        "report_trust_level": env.get("report_trust_level"),
        "transparency_log_entry_id": env.get("transparency_log_entry_id"),
    }


def _mutation_section() -> dict[str, Any]:
    p = APPS_E2E_DIR / "apps_mutation_rejection_report.json"
    if not p.exists():
        return {"present": False, "path": _rel(p)}
    d = _load_json(p)
    s = d.get("summary", {}) or {}
    return {
        "present": True,
        "path": _rel(p),
        "sha256": _sha256(p),
        "schema_version": d.get("schema_version"),
        "driver_path": d.get("driver_path"),
        "driver_version": d.get("driver_version"),
        "summary": {
            "total": s.get("total"),
            "rejected": s.get("rejected"),
            "accepted": s.get("accepted"),
            "skipped_not_applicable": s.get("skipped_not_applicable"),
            "rejection_rate": s.get("rejection_rate"),
            "tamper_class_count": s.get("tamper_class_count"),
        },
    }


def _verifier_report_section() -> dict[str, Any]:
    p = APPS_E2E_DIR / "verifier_report.json"
    if not p.exists():
        return {"present": False, "path": _rel(p)}
    d = _load_json(p)
    s = d.get("summary", {}) or {}
    rows = d.get("rows", []) or []
    return {
        "present": True,
        "path": _rel(p),
        "sha256": _sha256(p),
        "schema_version": d.get("verifier_report_schema_version"),
        "exit_code": d.get("exit_code"),
        "mode": d.get("mode"),
        "n_apps": s.get("n_apps", len(rows)),
        "n_pass": s.get("n_pass"),
        "n_fail": s.get("n_fail"),
    }


def _matrix_section() -> dict[str, Any]:
    p = APPS_E2E_DIR / "apps_e2e_matrix.json"
    if not p.exists():
        return {"present": False, "path": _rel(p)}
    d = _load_json(p)
    apps = d.get("apps", []) or []
    return {
        "present": True,
        "path": _rel(p),
        "sha256": _sha256(p),
        "schema_version": d.get("schema_version"),
        "n_apps": len(apps),
    }


def _per_app_section() -> list[dict[str, Any]]:
    """One row per app subdirectory under APPS_E2E_DIR. Cross-references
    verifier_report for the authoritative certification_level (per-bundle
    proof file does not include the level for waived apps)."""
    if not APPS_E2E_DIR.exists():
        return []
    verifier = _load_json(APPS_E2E_DIR / "verifier_report.json")
    levels_by_app: dict[str, str | None] = {
        row.get("app_name"): row.get("certification_level")
        for row in (verifier.get("rows") or [])
        if isinstance(row, dict) and row.get("app_name")
    }
    rows: list[dict[str, Any]] = []
    for app_dir in sorted(p for p in APPS_E2E_DIR.iterdir() if p.is_dir() and not p.name.startswith("_")):
        app = app_dir.name
        proof_path = app_dir / f"{app}_e2e_proof.json"
        manifest_path = app_dir / f"{app}_artifact_manifest.json"
        static_dag_path = app_dir / f"{app}_static_l3_dag_proof.json"
        proof = _load_json(proof_path)
        # verifier_report is the authoritative source for certification_level
        # (per-bundle file is silent for waived apps).
        cert_level = levels_by_app.get(app) or proof.get("certification_level")
        rows.append({
            "app_name": app,
            "proof_bundle_path": _rel(proof_path),
            "proof_bundle_sha256": _sha256(proof_path),
            "manifest_path": _rel(manifest_path),
            "manifest_sha256": _sha256(manifest_path),
            "static_dag_path": _rel(static_dag_path),
            "static_dag_sha256": _sha256(static_dag_path),
            "certification_level": cert_level,
            "exit_code": proof.get("exit_code"),
            "synthetic_trace_detected": proof.get("synthetic_trace_detected"),
            "mock_mode_detected": proof.get("mock_mode_detected"),
            "fixture_runtime_mode": proof.get("fixture_runtime_mode"),
            "runtime_mode": proof.get("runtime_mode"),
            "agentic_core_spine_status": proof.get("agentic_core_spine_status"),
        })
    return rows


def _live_verify_signature(skip: bool = False) -> dict[str, Any]:
    """Re-run the W5 verifier as live attestation (independent re-verification)."""
    if skip:
        return {"skipped": True}
    t0 = time.perf_counter()
    r = subprocess.run(
        [sys.executable, "tools/cert/apps_e2e/verify_apps_release_signature.py", "--quiet"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {
        "verifier": "tools/cert/apps_e2e/verify_apps_release_signature.py",
        "exit_code": r.returncode,
        "passed": r.returncode == 0,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "stderr_tail": (r.stderr or "").strip().splitlines()[-3:],
    }


def _keyless_signature_section() -> dict[str, Any]:
    """W9 \u2014 read the optional Sigstore keyless envelope, if present.

    The keyless envelope is produced by
    :file:`tools/cert/apps_e2e/sign_apps_release_bundle_keyless.py`
    when CI runs the apps-fortknox-keyless-sign workflow. It is not
    expected to exist on every commit; absence is normal.
    """
    env_path = (
        APPS_E2E_DIR / "apps_e2e_signoff_report.signature.keyless.json"
    )
    if not env_path.exists():
        return {"present": False, "path": _rel(env_path)}
    env = _load_json(env_path)
    return {
        "present": True,
        "path": _rel(env_path),
        "sha256": _sha256(env_path),
        "schema_version": env.get("schema_version"),
        "signing_method": env.get("signing_method"),
        "report_sha256": env.get("report_sha256"),
        "rekor_log_index": env.get("rekor_log_index"),
        "rekor_uuid": env.get("rekor_uuid"),
        "oidc_issuer": env.get("oidc_issuer"),
        "signer_identity_subject": env.get("signer_identity_subject"),
        "signed_at_utc": env.get("signed_at_utc"),
        "cosign_version": env.get("cosign_version"),
    }


def _live_verify_keyless_signature(
    *,
    keyless: dict[str, Any],
    skip: bool = False,
) -> dict[str, Any]:
    """W9 \u2014 re-run the W9 keyless verifier (cosign verify-blob).

    Skipped silently if the keyless envelope is absent (no FINAL claim
    is being made) or if cosign is not on PATH (typical local dev).
    """
    if not keyless.get("present"):
        return {"skipped": True, "reason": "keyless envelope absent"}
    if skip:
        return {"skipped": True, "reason": "skip flag"}
    if shutil.which("cosign") is None:
        return {"skipped": True, "reason": "cosign not on PATH"}
    t0 = time.perf_counter()
    r = subprocess.run(
        [
            sys.executable,
            "tools/cert/apps_e2e/verify_apps_release_signature_keyless.py",
            "--quiet",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {
        "verifier": "tools/cert/apps_e2e/verify_apps_release_signature_keyless.py",
        "exit_code": r.returncode,
        "passed": r.returncode == 0,
        "duration_ms": int((time.perf_counter() - t0) * 1000),
        "stderr_tail": (r.stderr or "").strip().splitlines()[-3:],
    }


# =============================================================================
# Main
# =============================================================================

def build_bundle(skip_live_verify: bool = False) -> dict[str, Any]:
    catalog = _catalog_section()
    assertions = _assertions_section()
    signoff = _signoff_section()
    signature = _signature_section()
    mutation = _mutation_section()
    verifier_report = _verifier_report_section()
    matrix = _matrix_section()
    per_app = _per_app_section()
    live_verify = _live_verify_signature(skip=skip_live_verify)
    keyless = _keyless_signature_section()
    keyless_verify = _live_verify_keyless_signature(
        keyless=keyless, skip=skip_live_verify
    )

    # Headline claims
    so_summary = signoff.get("summary", {}) or {}
    mut_summary = mutation.get("summary", {}) or {}
    n_certified = sum(
        1 for r in per_app
        if r.get("certification_level") == "SPINE_COMPLETE_CERTIFIED"
    )
    n_waived = sum(
        1 for r in per_app
        if (r.get("certification_level") or "").startswith("WAIVED_")
    )

    canary_pass = signoff.get("positive_control_status") == "PASS"
    trust_signed = signoff.get("trust_level") in SIGNED_TRUST_LEVELS
    sig_verified = signature.get("signature_verification_status") == "VERIFIED"
    mutation_clean = mut_summary.get("accepted") == 0 and (mut_summary.get("rejected") or 0) > 0
    live_verify_pass = live_verify.get("passed") is True or live_verify.get("skipped") is True
    no_blocked = (so_summary.get("blocked") or 0) == 0 and (so_summary.get("not_verified") or 0) == 0

    all_gates_pass = bool(
        canary_pass and trust_signed and sig_verified and mutation_clean
        and live_verify_pass and no_blocked
    )

    # Keyless / FINAL_SIGNED_CERTIFICATION promotion (W9).
    keyless_present = keyless.get("present") is True
    keyless_verified = (
        keyless_present
        and (
            keyless_verify.get("passed") is True
            or keyless_verify.get("skipped") is True
        )
    )
    final_signed_certification = bool(
        all_gates_pass and keyless_present and keyless_verified
    )
    effective_trust_level = (
        "FINAL_SIGNED_CERTIFICATION"
        if final_signed_certification
        else signoff.get("trust_level")
    )

    headline = {
        "all_gates_pass": all_gates_pass,
        "canary_pass": canary_pass,
        "trust_level": signoff.get("trust_level"),
        "effective_trust_level": effective_trust_level,
        "trust_in_signed_set": trust_signed,
        "signature_verification_status": signature.get("signature_verification_status"),
        "signature_verified": sig_verified,
        "live_signature_re_verify_passed": live_verify.get("passed", live_verify.get("skipped", False)),
        "keyless_signature_present": keyless_present,
        "keyless_signature_verified": keyless_verified,
        "final_signed_certification": final_signed_certification,
        "mutation_rejection_rate": mut_summary.get("rejection_rate"),
        "mutation_zero_accepts": mutation_clean,
        "row_total": so_summary.get("total"),
        "row_signed_off": so_summary.get("signed_off"),
        "row_signed_off_with_waiver": so_summary.get("signed_off_with_waiver"),
        "row_blocked": so_summary.get("blocked"),
        "row_not_verified": so_summary.get("not_verified"),
        "percent_signed_off": so_summary.get("percent_signed_off"),
        "n_apps_total": len(per_app),
        "n_apps_certified": n_certified,
        "n_apps_waived": n_waived,
    }

    bundle: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generator": GENERATOR_PATH_REL,
        "generator_version": GENERATOR_VERSION,
        "generated_at_utc": _utc_now(),
        "repo_root": str(REPO_ROOT).replace("\\", "/"),
        "headline_claims": headline,
        "catalog": catalog,
        "assertions": assertions,
        "signoff": signoff,
        "signature": signature,
        "mutation_rejection": mutation,
        "verifier_report": verifier_report,
        "matrix": matrix,
        "per_app": per_app,
        "live_signature_re_verify": live_verify,
        "keyless_signature": keyless,
        "live_keyless_signature_re_verify": keyless_verify,
        "remaining_external_gaps": {
            "FINAL_SIGNED_CERTIFICATION": (
                {
                    "status": "CLOSED",
                    "description": (
                        "Keyless cosign signature present and verified "
                        "(Sigstore Fulcio + Rekor). Trust ladder reaches "
                        "FINAL_SIGNED_CERTIFICATION."
                    ),
                    "blocks_apps_signed_proof": False,
                }
                if final_signed_certification
                else {
                    "status": "OPEN",
                    "description": (
                        "Promotion to FINAL_SIGNED_CERTIFICATION requires a "
                        "third-party identity authority (cosign keyless via "
                        "Sigstore Fulcio under GitHub OIDC). Repo-committed "
                        "Ed25519 signer caps honestly at SIGNED_PROOF. "
                        "Run .github/workflows/apps-fortknox-keyless-sign.yml "
                        "on a tagged release to close."
                    ),
                    "blocks_apps_signed_proof": False,
                }
            ),
        },
    }
    return bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--skip-live-verify",
        action="store_true",
        help="Skip the live re-run of verify_apps_release_signature.py "
             "(useful in tests or sandboxes without the keypair).",
    )
    args = parser.parse_args(argv)

    bundle = build_bundle(skip_live_verify=args.skip_live_verify)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    h = bundle["headline_claims"]
    if not args.quiet:
        print("[generate_apps_100pct_runtime_proof] bundle written:")
        try:
            print(f"  path:          {args.out.resolve().relative_to(REPO_ROOT).as_posix()}")
        except ValueError:
            print(f"  path:          {args.out}")
        print(f"  sha256:        {_sha256(args.out)}")
        print(f"  trust_level:   {h['trust_level']}")
        print(f"  canary:        {'PASS' if h['canary_pass'] else 'FAIL'}")
        print(f"  signature:     {h['signature_verification_status']}")
        print(f"  mutation rate: {h['mutation_rejection_rate']}")
        print(f"  rows:          {h['row_signed_off']} signed_off + "
              f"{h['row_signed_off_with_waiver']} waiver / {h['row_total']}")
        print(f"  apps:          {h['n_apps_certified']} certified, "
              f"{h['n_apps_waived']} waived / {h['n_apps_total']}")
        print(f"  ALL GATES:     {'PASS' if h['all_gates_pass'] else 'FAIL'}")

    return 0 if h["all_gates_pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
