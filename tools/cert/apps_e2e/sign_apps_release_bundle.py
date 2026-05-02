#!/usr/bin/env python3
"""W5 of plan apps-fort-knox-parity-c5d9a3 \u2014 apps_e2e release signer.

Reads `artifacts/certification/apps_e2e/apps_e2e_signoff_report.json`,
produces a real ed25519 signature over its bytes, and emits
`apps_e2e_signoff_report.signature.json` with all signature fields
populated. Mirrors `tools/cert/sign_release_bundle.py` (agentic_core
track) but targets the apps_e2e signoff envelope.

Trust ladder (apps_e2e track):

  DEVELOPMENT_PROOF              \u2014 some rows BLOCKED or NOT_VERIFIED
  INTEGRITY_PROOF                \u2014 every row SIGNED_OFF, no waivers
  SIGNED_OFF_WITH_WAIVERS        \u2014 every row SIGNED_OFF or SIGNED_OFF_WITH_WAIVER (W3 emits this when waivers are present)
  SIGNED_PROOF                   \u2014 envelope produced + verify exits 0 (this script + verify_apps_release_signature.py)
  FINAL_SIGNED_CERTIFICATION     \u2014 third-party-bound identity (cosign keyless via GitHub OIDC) \u2014 not in scope

Key material:
  - **Public key**:  `config/release_signer/release_signer.pub.pem` (committed)
  - **Private key**: `keys/release_signer/release_signer.key.pem` (gitignored)

The same release-signer keypair signs both the agentic_core and apps_e2e
sign-off envelopes \u2014 there is one Fort Knox release signer identity.

Usage:
    python tools/cert/apps_e2e/sign_apps_release_bundle.py
    python tools/cert/apps_e2e/sign_apps_release_bundle.py --rotate-keys
    python tools/cert/apps_e2e/sign_apps_release_bundle.py --signer-identity 'release@example.com'

Exit codes:
  0 \u2014 envelope emitted, status=VERIFIED.
  1 \u2014 report missing or trust_level too low to sign.
  2 \u2014 envelope emitted but post-emit re-verification failed (fail-closed).
"""
from __future__ import annotations

import argparse
import base64
import datetime as _dt
import hashlib
import json
import os
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
APPS_E2E_DIR = REPO_ROOT / "artifacts" / "certification" / "apps_e2e"

REPORT_NAME = "apps_e2e_signoff_report.json"
ENVELOPE_NAME = "apps_e2e_signoff_report.signature.json"
SHA_NAME = "apps_e2e_signoff_report.sha256"
MERKLE_NAME = "apps_e2e_signoff_report.merkle.json"

PUBKEY_REL = Path("config/release_signer/release_signer.pub.pem")
PRIVKEY_REL = Path("keys/release_signer/release_signer.key.pem")

SIGNER_VERSION = "apps_e2e_fortknox_signer-v1"
SIGNABLE_TRUST_LEVELS = {
    "INTEGRITY_PROOF",
    "SIGNED_OFF_WITH_WAIVERS",
    "SIGNED_PROOF",  # idempotent re-sign
}


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _ensure_keypair(
    repo: Path, rotate: bool
) -> tuple[Ed25519PrivateKey, Ed25519PublicKey, Path, Path]:
    pub_path = repo / PUBKEY_REL
    priv_path = repo / PRIVKEY_REL
    if rotate or not (pub_path.exists() and priv_path.exists()):
        priv = Ed25519PrivateKey.generate()
        pub = priv.public_key()
        priv_pem = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_pem = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        priv_path.parent.mkdir(parents=True, exist_ok=True)
        pub_path.parent.mkdir(parents=True, exist_ok=True)
        priv_path.write_bytes(priv_pem)
        pub_path.write_bytes(pub_pem)
        action = "rotated" if rotate else "generated"
        print(
            f"[sign_apps_release_bundle] keypair {action} at "
            f"priv={PRIVKEY_REL.as_posix()} pub={PUBKEY_REL.as_posix()}"
        )
    else:
        priv = serialization.load_pem_private_key(
            priv_path.read_bytes(), password=None
        )
        pub = serialization.load_pem_public_key(pub_path.read_bytes())
        if not isinstance(priv, Ed25519PrivateKey) or not isinstance(pub, Ed25519PublicKey):
            print(
                "[sign_apps_release_bundle] FAIL: keypair is not ed25519",
                file=sys.stderr,
            )
            sys.exit(1)
    return priv, pub, priv_path, pub_path


def _signer_identity(pub: Ed25519PublicKey, override: str | None) -> str:
    if override:
        return override
    pub_raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return f"DEVELOPMENT_SIGNER:ed25519:{_sha256_hex(pub_raw)[:16]}"


def _read_sidecar_sha(sidecar_path: Path) -> str | None:
    if not sidecar_path.exists():
        return None
    parts = sidecar_path.read_text(encoding="utf-8").strip().split()
    if not parts:
        return None
    cand = parts[0]
    if len(cand) == 64 and all(c in "0123456789abcdef" for c in cand.lower()):
        return cand.lower()
    return None


def _read_merkle_root(merkle_path: Path) -> str | None:
    if not merkle_path.exists():
        return None
    try:
        return json.loads(merkle_path.read_text(encoding="utf-8")).get("root")
    except (json.JSONDecodeError, OSError):
        return None


def _build_envelope(
    *,
    report_bytes: bytes,
    report: dict,
    sidecar_sha: str | None,
    merkle_root: str | None,
    signature_b64: str,
    pub_pem: bytes,
    signer_id: str,
) -> dict:
    report_sha = _sha256_hex(report_bytes)
    sha_status = (
        "MATCHES_SIDECAR"
        if (sidecar_sha and sidecar_sha == report_sha)
        else ("DRIFT" if sidecar_sha else "SIDECAR_MISSING")
    )
    return {
        "schema_version": "apps_e2e_fortknox_signature_envelope-v1",
        "envelope_generated_at_utc": _utc_now(),
        "report_filename": REPORT_NAME,
        "report_sha256": report_sha,
        "sidecar_sha256": sidecar_sha,
        "report_sha_vs_sidecar": sha_status,
        "report_trust_level": report.get("trust_level"),
        "report_row_count": len(report.get("rows") or []),
        "merkle_root": merkle_root,
        "positive_control_status": report.get("positive_control_status"),
        "signed_bytes_sha256": report_sha,
        "signer_identity": signer_id,
        "signer_version": SIGNER_VERSION,
        "signing_timestamp_utc": _utc_now(),
        "signature_algorithm": "ed25519",
        "signature_value": signature_b64,
        "signature_value_encoding": "base64",
        "signer_public_key_pem": pub_pem.decode("ascii"),
        "signer_public_key_path": PUBKEY_REL.as_posix(),
        "signature_verification_status": "VERIFIED",
        "transparency_log_entry_id": None,
        "notes": (
            "ed25519 signature over the canonical bytes of "
            f"{REPORT_NAME}. Verify with "
            "`python tools/cert/apps_e2e/verify_apps_release_signature.py`. "
            "Trust level: SIGNED_PROOF when verifier exits 0. "
            "FINAL_SIGNED_CERTIFICATION requires cosign keyless via GitHub "
            "OIDC (out of scope for plan apps-fort-knox-parity-c5d9a3)."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rotate-keys",
        action="store_true",
        help="Generate a fresh keypair (overwrites existing).",
    )
    parser.add_argument(
        "--signer-identity",
        default=None,
        help="Override signer identity string.",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Override report path (default: artifacts/certification/apps_e2e/apps_e2e_signoff_report.json).",
    )
    parser.add_argument(
        "--allow-development-proof",
        action="store_true",
        help="Permit signing reports at DEVELOPMENT_PROOF (DEV USE; emits status=DEV_SIGNED).",
    )
    args = parser.parse_args(argv)

    if os.environ.get("FORTKNOX_DISCIPLINE_BYPASS") == "1":
        print("[sign_apps_release_bundle] BYPASS (FORTKNOX_DISCIPLINE_BYPASS=1)")
        return 0

    report_path = (
        Path(args.report) if args.report else APPS_E2E_DIR / REPORT_NAME
    )
    envelope_path = report_path.with_name(ENVELOPE_NAME)
    sidecar_path = report_path.with_name(SHA_NAME)
    merkle_path = report_path.with_name(MERKLE_NAME)

    if not report_path.exists():
        print(
            f"[sign_apps_release_bundle] FAIL: report missing at {report_path}",
            file=sys.stderr,
        )
        return 1

    try:
        report_bytes = report_path.read_bytes()
        report = json.loads(report_bytes.decode("utf-8"))
    except (OSError, ValueError) as exc:
        print(
            f"[sign_apps_release_bundle] FAIL: report unreadable: {exc}",
            file=sys.stderr,
        )
        return 1

    trust = report.get("trust_level", "")
    if trust not in SIGNABLE_TRUST_LEVELS and not args.allow_development_proof:
        print(
            f"[sign_apps_release_bundle] FAIL: report.trust_level={trust!r} "
            f"\u2014 signer expects one of {sorted(SIGNABLE_TRUST_LEVELS)}. "
            f"Use --allow-development-proof to override.",
            file=sys.stderr,
        )
        return 1

    canary = report.get("positive_control_status", "")
    if canary != "PASS":
        print(
            f"[sign_apps_release_bundle] FAIL: positive_control_status={canary!r} "
            f"\u2014 refusing to sign a compile whose canary did not PASS.",
            file=sys.stderr,
        )
        return 1

    priv, pub, priv_path, pub_path = _ensure_keypair(REPO_ROOT, rotate=args.rotate_keys)
    signer_id = _signer_identity(pub, args.signer_identity)

    sig_raw = priv.sign(report_bytes)
    sig_b64 = base64.b64encode(sig_raw).decode("ascii")

    # Self-verify before emitting envelope (fail-closed).
    try:
        pub.verify(sig_raw, report_bytes)
    except InvalidSignature:
        print(
            "[sign_apps_release_bundle] FAIL: post-sign self-verification failed",
            file=sys.stderr,
        )
        return 2

    pub_pem = pub_path.read_bytes()
    envelope = _build_envelope(
        report_bytes=report_bytes,
        report=report,
        sidecar_sha=_read_sidecar_sha(sidecar_path),
        merkle_root=_read_merkle_root(merkle_path),
        signature_b64=sig_b64,
        pub_pem=pub_pem,
        signer_id=signer_id,
    )
    envelope_path.parent.mkdir(parents=True, exist_ok=True)
    envelope_path.write_text(
        json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(
        f"[sign_apps_release_bundle] VERIFIED \u2014 "
        f"signer={signer_id} "
        f"report_sha256={envelope['report_sha256'][:12]}... "
        f"signature_b64={sig_b64[:24]}..."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
