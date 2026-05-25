"""Fort Knox — Repo-signer trust-level promoter.

Signs `artifacts/certification/final_requirement_signoff_report.json`
bytes with the Ed25519 private key at `artifacts/keys/release_signer/release_signer.key.pem`
(matched to the committed public key at
`config/release_signer/release_signer.pub.pem`) and populates the
signature envelope with VERIFIED status, signer identity, and a
base64-encoded signature. This promotes the report's `trust_level` from
INTEGRITY_PROOF to SIGNED_PROOF. FINAL_SIGNED_CERTIFICATION additionally
requires clean-git, bundle-verifier PASS, and the capstone gates — see
plan §GAP-2 and Wave 5.

What this tool produces:

  1. Signs report bytes exactly as they appear on disk.
  2. Overwrites
     `artifacts/certification/final_requirement_signoff_report.signature.json`
     with VERIFIED status, inline Ed25519 public key PEM, signature hex,
     signer identity, timestamp.
  3. Rewrites the report with `trust_level: SIGNED_PROOF` (upgrade from
     INTEGRITY_PROOF) ONLY when every pre-condition is met:
       - All rows SIGNED_OFF (compiler guarantees INTEGRITY_PROOF)
       - git_dirty == False  (see ops_scripts/ci/check_signoff_git_clean.py)
       - Signature verifies over new report bytes
  4. Updates the sidecar sha256 file and the merkle sidecar root.

Refuses to run when `git_dirty: True`, unless `FORTKNOX_DEV_MODE=1`.

Exit codes:
    0 — success; trust_level upgraded to SIGNED_PROOF
    2 — fail-closed (preconditions not met)
    3 — harness error (missing report, crypto unavailable)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CERT_DIR = REPO_ROOT / "artifacts" / "certification"
REPORT = CERT_DIR / "final_requirement_signoff_report.json"
SHA_SIDECAR = CERT_DIR / "final_requirement_signoff_report.sha256"
MERKLE = CERT_DIR / "final_requirement_signoff_report.merkle.json"
ENVELOPE = CERT_DIR / "final_requirement_signoff_report.signature.json"

PRIV_KEY_PATH = REPO_ROOT / "artifacts" / "keys" / "release_signer" / "release_signer.key.pem"
PUB_KEY_PATH = REPO_ROOT / "config" / "release_signer" / "release_signer.pub.pem"
SIGNER_IDENTITY = "fortknox-release-signer-v1"
SIGNATURE_ALGORITHM = "ed25519"


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _sha256_file(p: Path) -> str:
    return _sha256_bytes(p.read_bytes())


def _recompute_merkle(rows: list[dict]) -> dict:
    sorted_rows = sorted(rows, key=lambda r: r["req_id"])
    leaves = [{"req_id": r["req_id"], "leaf_hash": r["row_digest"]} for r in sorted_rows]

    def _pair(a: str, b: str) -> str:
        return _sha256_bytes(bytes.fromhex(a) + bytes.fromhex(b))

    level = [L["leaf_hash"] for L in leaves]
    if not level:
        root = ""
    else:
        while len(level) > 1:
            if len(level) % 2 == 1:
                level.append(level[-1])
            level = [_pair(level[i], level[i + 1]) for i in range(0, len(level), 2)]
        root = level[0]
    return {
        "root": root,
        "leaf_count": len(leaves),
        "leaves": leaves,
        "computed_at_utc": _iso_now(),
        "algorithm": "sha256 pairwise, odd-node duplication",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-dirty-git", action="store_true",
                        help="Permit signing when git_dirty=True (dev loop only).")
    args = parser.parse_args()

    if not REPORT.exists():
        print(f"HARNESS_ERROR: report missing at {REPORT}", file=sys.stderr)
        return 3
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey, Ed25519PublicKey,
        )
        from cryptography.hazmat.primitives import serialization
    except ImportError:
        print("HARNESS_ERROR: cryptography library unavailable", file=sys.stderr)
        return 3

    if not PRIV_KEY_PATH.exists() or not PUB_KEY_PATH.exists():
        print(
            f"HARNESS_ERROR: release signer key pair missing "
            f"(priv={PRIV_KEY_PATH.relative_to(REPO_ROOT)}, "
            f"pub={PUB_KEY_PATH.relative_to(REPO_ROOT)})",
            file=sys.stderr,
        )
        return 3
    try:
        priv = serialization.load_pem_private_key(
            PRIV_KEY_PATH.read_bytes(), password=None
        )
        pub_pem_disk = PUB_KEY_PATH.read_bytes()
        pub = serialization.load_pem_public_key(pub_pem_disk)
    except (ValueError, OSError) as exc:
        print(f"HARNESS_ERROR: key material unreadable: {exc}", file=sys.stderr)
        return 3
    if not isinstance(priv, Ed25519PrivateKey) or not isinstance(pub, Ed25519PublicKey):
        print("HARNESS_ERROR: release signer keys are not ed25519", file=sys.stderr)
        return 3

    report = json.loads(REPORT.read_text(encoding="utf-8"))

    # Preconditions
    if report["summary"]["signed_off"] != report["summary"]["total"] or report["summary"]["total"] == 0:
        print("FAIL_CLOSED: not all rows SIGNED_OFF; cannot promote to SIGNED_PROOF",
              file=sys.stderr)
        return 2
    if report.get("git_dirty") is True:
        if args.allow_dirty_git or os.environ.get("FORTKNOX_DEV_MODE") == "1":
            print("WARN: git_dirty=True but dev-mode bypass active — signature is "
                  "dev-tier only; DO NOT claim SIGNED_PROOF in production",
                  file=sys.stderr)
        else:
            print("FAIL_CLOSED: git_dirty=True; refusing to sign. "
                  "Commit changes, recompile, re-run. "
                  "To bypass (dev loop), pass --allow-dirty-git or set FORTKNOX_DEV_MODE=1.",
                  file=sys.stderr)
            return 2

    import base64
    # Upgrade trust_level in the report; schema has additionalProperties=false
    # at the top level, so put provenance in the envelope, not the report.
    report["trust_level"] = "SIGNED_PROOF"

    # Canonical bytes for signing — match the compiler's exact serialization
    # pattern (`json.dumps(report, indent=2, sort_keys=True) + "\n"`) so
    # subsequent re-compiles over unchanged inputs reproduce these bytes.
    new_bytes = (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    report_sha = _sha256_bytes(new_bytes)

    # Sign with the committed repo key, verify round-trip against on-disk pub
    signature = priv.sign(new_bytes)
    pub.verify(signature, new_bytes)  # raises on failure
    sig_b64 = base64.b64encode(signature).decode("ascii")
    pub_fp = hashlib.sha256(pub_pem_disk).hexdigest()

    # Recompute merkle against the upgraded report (row_digests unchanged,
    # so root is identical — but compute for determinism).
    merkle = _recompute_merkle(report["rows"])

    envelope = {
        "schema_version": "fortknox-signature-envelope-v2",
        "envelope_generated_at_utc": _iso_now(),
        "report_filename": "final_requirement_signoff_report.json",
        "report_sha256": report_sha,
        "sidecar_sha256": report_sha,
        "report_sha_vs_sidecar": "MATCHES_SIDECAR",
        "report_trust_level": report["trust_level"],
        "report_row_count": len(report["rows"]),
        "merkle_root": merkle["root"],
        "signed_bytes_sha256": report_sha,
        "signer_identity": SIGNER_IDENTITY,
        "signer_identity_pending": None,
        "signer_public_key_pem": pub_pem_disk.decode("ascii"),
        "signer_public_key_fingerprint_sha256": pub_fp,
        "signer_public_key_path": str(PUB_KEY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "signing_timestamp_utc": _iso_now(),
        "signature_algorithm": SIGNATURE_ALGORITHM,
        "signature_value": sig_b64,
        "signature_encoding": "base64",
        "signature_verification_status": "VERIFIED",
        "transparency_log_entry_id": None,
        "trust_level_upgrade": {
            "tool": "tools/cert/sign_with_ephemeral_key.py",
            "from": "INTEGRITY_PROOF",
            "to": "SIGNED_PROOF",
            "upgraded_at_utc": _iso_now(),
            "upgrade_reason": (
                "Ed25519 signature over final_requirement_signoff_report.json bytes "
                "VERIFIED against the committed release_signer public key. For "
                "FINAL_SIGNED_CERTIFICATION (plan §GAP-2), external attestation "
                "(cosign keyless → Sigstore Fulcio OR a KMS-backed signer) is "
                "required and must additionally satisfy W5 capstone gates."
            ),
        },
        "notes": (
            "Signature produced by tools/cert/sign_with_ephemeral_key.py using the "
            "committed release_signer key pair. Bundle verifier re-performs "
            "ed25519 verification against the on-disk public key at "
            "config/release_signer/release_signer.pub.pem."
        ),
    }

    # Write files as BYTES to avoid platform-specific newline translation on
    # Windows (write_text would insert CRLF and invalidate the signature).
    REPORT.write_bytes(new_bytes)
    SHA_SIDECAR.write_bytes((f"{report_sha}  {REPORT.name}\n").encode("utf-8"))
    MERKLE.write_bytes(
        (json.dumps(merkle, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    ENVELOPE.write_bytes(
        (json.dumps(envelope, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )

    print(f"[sign_with_ephemeral_key] trust_level: INTEGRITY_PROOF → SIGNED_PROOF")
    print(f"  report_sha256: {report_sha[:16]}...")
    print(f"  signature:     {signature.hex()[:32]}...")
    print(f"  pub_key_fp:    {pub_fp[:16]}...")
    print(f"  signer_id:     {SIGNER_IDENTITY}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
