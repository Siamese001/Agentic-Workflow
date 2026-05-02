#!/usr/bin/env python3
"""W5 of plan apps-fort-knox-parity-c5d9a3 \u2014 verify the apps_e2e release signature.

Independently re-verifies the apps_e2e signoff signature without trusting
the envelope's `signature_verification_status` field. Mirrors
`tools/cert/verify_release_signature.py` shape.

Reads:
  - `artifacts/certification/apps_e2e/apps_e2e_signoff_report.json` (canonical bytes)
  - `artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.json` (envelope)
  - `config/release_signer/release_signer.pub.pem` (on-disk public key)

Performs:
  1. Re-hash the report file \u2192 must match envelope.report_sha256 and envelope.signed_bytes_sha256.
  2. Cross-check envelope.signer_public_key_pem against on-disk pub.pem (no key swap).
  3. Cryptographically verify the ed25519 signature over the report bytes.
  4. Cross-check the merkle_root against the report's separate .merkle.json sidecar.
  5. Cross-check positive_control_status == "PASS".

Exit codes:
  0 \u2014 verification PASS, signature is cryptographically valid.
  1 \u2014 input missing or malformed.
  2 \u2014 verification FAIL (sha drift, key swap, merkle drift, InvalidSignature, or canary FAIL).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

REPO_ROOT = Path(__file__).resolve().parents[3]
APPS_E2E_DIR = REPO_ROOT / "artifacts" / "certification" / "apps_e2e"

REPORT_NAME = "apps_e2e_signoff_report.json"
ENVELOPE_NAME = "apps_e2e_signoff_report.signature.json"
MERKLE_NAME = "apps_e2e_signoff_report.merkle.json"
PUBKEY_REL = Path("config/release_signer/release_signer.pub.pem")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=None, help="Override report path.")
    parser.add_argument("--envelope", default=None, help="Override envelope path.")
    parser.add_argument("--merkle", default=None, help="Override merkle sidecar path.")
    parser.add_argument("--pubkey", default=None, help="Override on-disk public key path.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    report_path = Path(args.report) if args.report else APPS_E2E_DIR / REPORT_NAME
    envelope_path = (
        Path(args.envelope) if args.envelope else APPS_E2E_DIR / ENVELOPE_NAME
    )
    merkle_path = Path(args.merkle) if args.merkle else APPS_E2E_DIR / MERKLE_NAME
    pub_path = Path(args.pubkey) if args.pubkey else REPO_ROOT / PUBKEY_REL

    for label, p in [
        ("report", report_path),
        ("envelope", envelope_path),
        ("pubkey", pub_path),
    ]:
        if not p.exists():
            print(
                f"[verify_apps_release_signature] FAIL: {label} missing at {p}",
                file=sys.stderr,
            )
            return 1

    try:
        report_bytes = report_path.read_bytes()
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        pub_pem_disk = pub_path.read_bytes()
        report = json.loads(report_bytes.decode("utf-8"))
    except (OSError, ValueError) as exc:
        print(
            f"[verify_apps_release_signature] FAIL: input unreadable: {exc}",
            file=sys.stderr,
        )
        return 1

    failures: list[str] = []

    # 1. sha256 cross-check
    actual_sha = hashlib.sha256(report_bytes).hexdigest()
    env_report_sha = envelope.get("report_sha256")
    env_signed_sha = envelope.get("signed_bytes_sha256")
    if env_report_sha != actual_sha:
        failures.append(
            f"envelope.report_sha256 != recomputed ({env_report_sha} != {actual_sha})"
        )
    if env_signed_sha and env_signed_sha != actual_sha:
        failures.append(
            f"envelope.signed_bytes_sha256 != recomputed ({env_signed_sha} != {actual_sha})"
        )

    # 2. Key cross-check
    env_pub_pem = (envelope.get("signer_public_key_pem") or "").encode("ascii")
    if env_pub_pem and env_pub_pem.strip() != pub_pem_disk.strip():
        failures.append(
            "envelope.signer_public_key_pem disagrees with on-disk "
            f"{PUBKEY_REL.as_posix()} (key swap detected)"
        )

    # 3. Cryptographic signature verification
    sig_b64 = envelope.get("signature_value", "") or ""
    sig_alg = envelope.get("signature_algorithm", "")
    if not sig_b64:
        failures.append(
            "envelope.signature_value missing \u2014 no signature to verify"
        )
    if sig_alg != "ed25519":
        failures.append(
            f"unsupported signature_algorithm={sig_alg!r} "
            f"(this verifier only handles ed25519)"
        )

    if not failures:
        try:
            pub = serialization.load_pem_public_key(pub_pem_disk)
            if not isinstance(pub, Ed25519PublicKey):
                failures.append("on-disk public key is not ed25519")
            else:
                pub.verify(base64.b64decode(sig_b64), report_bytes)
        except InvalidSignature:
            failures.append(
                "InvalidSignature \u2014 ed25519 verification failed "
                "(report bytes do not match the signed payload)"
            )
        except Exception as exc:  # noqa: BLE001 -- top-level guard
            failures.append(
                f"verification raised {type(exc).__name__}: {exc}"
            )

    # 4. Merkle sidecar cross-check (if present)
    env_merkle = envelope.get("merkle_root")
    if env_merkle and merkle_path.exists():
        try:
            sidecar_root = json.loads(merkle_path.read_text(encoding="utf-8")).get("root")
        except (json.JSONDecodeError, OSError):
            sidecar_root = None
        if sidecar_root and sidecar_root != env_merkle:
            failures.append(
                f"envelope.merkle_root ({env_merkle[:12]}...) "
                f"!= merkle.json.root ({sidecar_root[:12]}...)"
            )

    # 5. Canary cross-check
    if report.get("positive_control_status") != "PASS":
        failures.append(
            f"report.positive_control_status="
            f"{report.get('positive_control_status')!r} \u2014 must be PASS"
        )

    # 6. Status cross-check
    env_status = envelope.get("signature_verification_status")
    if not failures and env_status != "VERIFIED":
        failures.append(
            f"envelope claims status={env_status!r} but cryptographic "
            f"verification PASSED \u2014 envelope is internally inconsistent"
        )

    if failures:
        print("[verify_apps_release_signature] FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 2

    if not args.quiet:
        print("[verify_apps_release_signature] PASS")
        print(f"  signer:       {envelope.get('signer_identity')}")
        print(f"  algorithm:    ed25519")
        print(f"  signed at:    {envelope.get('signing_timestamp_utc')}")
        print(f"  report sha:   {actual_sha}")
        print(f"  rows signed:  {envelope.get('report_row_count')}")
        print(f"  trust level:  {envelope.get('report_trust_level')}")
        print(f"  merkle root:  {env_merkle}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
