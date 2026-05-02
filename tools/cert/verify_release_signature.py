#!/usr/bin/env python3
"""Independently verify the Fort Knox release signature.

Reads:
- ``artifacts/certification/final_requirement_signoff_report.json`` (canonical bytes)
- ``artifacts/certification/final_requirement_signoff_report.signature.json`` (envelope)
- ``config/release_signer/release_signer.pub.pem`` (public key) — OR the
  embedded ``signer_public_key_pem`` field from the envelope (envelope wins
  when present, then a check against the on-disk pub.pem confirms the
  envelope did not silently swap keys).

Performs:

1. Re-hash the report file → must match envelope.report_sha256 and envelope.signed_bytes_sha256.
2. Cross-check envelope.signer_public_key_pem == on-disk pub.pem (no key swap).
3. Cryptographically verify the ed25519 signature over the report bytes.
4. Echo signer identity, signing timestamp, and report row count.

Exit codes:
- ``0`` — verification PASS, signature is cryptographically valid.
- ``1`` — input missing or malformed.
- ``2`` — verification FAIL (sha drift, key swap, or InvalidSignature).
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


_REPORT_NAME = "final_requirement_signoff_report.json"
_ENVELOPE_NAME = "final_requirement_signoff_report.signature.json"
_PUBKEY_REL = Path("config/release_signer/release_signer.pub.pem")


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / ".git").exists():
            return p
    return Path.cwd()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=None,
                        help="Override path to the report JSON.")
    parser.add_argument("--envelope", default=None,
                        help="Override path to the signature envelope JSON.")
    parser.add_argument("--pubkey", default=None,
                        help="Override path to the on-disk public key PEM.")
    parser.add_argument("--quiet", action="store_true", help="Suppress success output.")
    args = parser.parse_args()

    repo = _repo_root()
    cert_dir = repo / "artifacts" / "certification"
    report_path = Path(args.report) if args.report else cert_dir / _REPORT_NAME
    envelope_path = Path(args.envelope) if args.envelope else cert_dir / _ENVELOPE_NAME
    pub_path = Path(args.pubkey) if args.pubkey else repo / _PUBKEY_REL

    for label, p in [("report", report_path), ("envelope", envelope_path),
                     ("pubkey", pub_path)]:
        if not p.exists():
            print(f"[verify_release_signature] FAIL: {label} missing at {p}",
                  file=sys.stderr)
            return 1

    try:
        report_bytes = report_path.read_bytes()
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
        pub_pem_disk = pub_path.read_bytes()
    except (OSError, ValueError) as exc:
        print(f"[verify_release_signature] FAIL: input unreadable: {exc}",
              file=sys.stderr)
        return 1

    failures: list[str] = []

    # 1. sha256 cross-check
    actual_sha = hashlib.sha256(report_bytes).hexdigest()
    env_report_sha = envelope.get("report_sha256")
    env_signed_sha = envelope.get("signed_bytes_sha256")
    if env_report_sha != actual_sha:
        failures.append(f"envelope.report_sha256 != recomputed "
                        f"({env_report_sha} != {actual_sha})")
    if env_signed_sha and env_signed_sha != actual_sha:
        failures.append(f"envelope.signed_bytes_sha256 != recomputed "
                        f"({env_signed_sha} != {actual_sha})")

    # 2. Key cross-check — envelope's embedded pub key must match on-disk pub
    env_pub_pem = (envelope.get("signer_public_key_pem") or "").encode("ascii")
    if env_pub_pem and env_pub_pem.strip() != pub_pem_disk.strip():
        failures.append("envelope.signer_public_key_pem disagrees with on-disk "
                        f"{_PUBKEY_REL} (key swap detected)")

    # 3. Cryptographic verification (the actual signature check)
    sig_b64 = envelope.get("signature_value", "") or ""
    sig_alg = envelope.get("signature_algorithm", "")
    if not sig_b64:
        failures.append("envelope.signature_value missing — no signature to verify")
    if sig_alg != "ed25519":
        failures.append(f"unsupported signature_algorithm={sig_alg!r} "
                        f"(this verifier only handles ed25519)")

    if not failures:
        try:
            pub = serialization.load_pem_public_key(pub_pem_disk)
            if not isinstance(pub, Ed25519PublicKey):
                failures.append("on-disk public key is not ed25519")
            else:
                pub.verify(base64.b64decode(sig_b64), report_bytes)
        except InvalidSignature:
            failures.append("InvalidSignature — ed25519 verification failed "
                            "(report bytes do not match the signed payload)")
        except Exception as exc:  # noqa: BLE001 -- top-level guard
            failures.append(f"verification raised {type(exc).__name__}: {exc}")

    # 4. Status field cross-check
    env_status = envelope.get("signature_verification_status")
    if not failures and env_status != "VERIFIED":
        failures.append(f"envelope claims status={env_status!r} but cryptographic "
                        f"verification PASSED — envelope is internally inconsistent")

    if failures:
        print("[verify_release_signature] FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(f"[verify_release_signature] PASS")
        print(f"  signer:       {envelope.get('signer_identity')}")
        print(f"  algorithm:    ed25519")
        print(f"  signed at:    {envelope.get('signing_timestamp_utc')}")
        print(f"  report sha:   {actual_sha}")
        print(f"  rows signed:  {envelope.get('report_row_count')}")
        print(f"  trust level:  {envelope.get('report_trust_level')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
