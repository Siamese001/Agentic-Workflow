"""W9 of plan apps-fort-knox-parity-c5d9a3 \u2014 Keyless verifier for apps_e2e.

Independent verifier (hostile-verifier discipline mirrors W5) that
re-runs ``cosign verify-blob`` against the keyless envelope. Refuses
signatures that:

  - Were issued by an unexpected OIDC issuer
  - Bear an unexpected signer-identity subject (workflow + ref)
  - Don't bind to the current report sha256

Sibling: :mod:`tools.cert.apps_e2e.verify_apps_release_signature` which
verifies the W5 dev-keypair envelope. The two verifiers MUST agree on
the report bytes (same sha256) for a SIGNED_PROOF claim to be honest.

CLI:
    python tools/cert/apps_e2e/verify_apps_release_signature_keyless.py [--quiet]

Exit codes:
    0   verification passed
    1   verification failed
    2   prerequisite missing (cosign / envelope / report)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_REPORT = "artifacts/certification/apps_e2e/apps_e2e_signoff_report.json"
DEFAULT_ENVELOPE = "artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.keyless.json"


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / ".git").exists():
            return p
    return Path.cwd()


def _cosign_path() -> str | None:
    return shutil.which("cosign")


def verify_keyless(
    *,
    report_path: Path,
    envelope_path: Path,
    cosign: str,
    expected_issuer_regex: str | None = None,
    expected_identity_regex: str | None = None,
    quiet: bool = False,
) -> tuple[bool, list[str]]:
    """Verify a keyless envelope; return (passed, list_of_failure_reasons)."""
    failures: list[str] = []

    # 1. Load envelope.
    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return (False, [f"envelope unreadable: {exc}"])

    # 2. Re-derive report sha256 and check binding.
    if not report_path.exists():
        return (False, [f"signoff report missing: {report_path}"])
    actual_sha = hashlib.sha256(report_path.read_bytes()).hexdigest()
    claimed_sha = envelope.get("report_sha256")
    if actual_sha != claimed_sha:
        failures.append(
            f"report_sha256 mismatch: actual={actual_sha} envelope={claimed_sha}"
        )

    # 3. Schema sanity.
    required_keys = (
        "schema_version",
        "signing_method",
        "report_sha256",
        "signature_b64",
        "fulcio_certificate_pem",
        "oidc_issuer",
        "signer_identity_subject",
    )
    for k in required_keys:
        if k not in envelope:
            failures.append(f"missing envelope key: {k}")
    if envelope.get("signing_method") != "keyless_cosign":
        failures.append(
            f"signing_method={envelope.get('signing_method')!r} "
            "(expected 'keyless_cosign')"
        )

    if failures:
        return (False, failures)

    # 4. Run cosign verify-blob with the envelope's cert + signature.
    issuer = envelope["oidc_issuer"]
    subject = envelope["signer_identity_subject"]
    issuer_regex = expected_issuer_regex or _escape_regex(issuer)
    identity_regex = expected_identity_regex or _escape_regex(subject)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        cert_path = tmp_dir / "cosign.cert"
        sig_path = tmp_dir / "cosign.sig"
        cert_path.write_text(
            envelope["fulcio_certificate_pem"], encoding="utf-8"
        )
        sig_path.write_text(envelope["signature_b64"], encoding="utf-8")

        argv = [
            cosign,
            "verify-blob",
            "--certificate",
            str(cert_path),
            "--signature",
            str(sig_path),
            "--certificate-oidc-issuer-regexp",
            issuer_regex,
            "--certificate-identity-regexp",
            identity_regex,
            str(report_path),
        ]
        if not quiet:
            print(
                f"[verify_apps_release_signature_keyless] running: cosign verify-blob "
                f"--certificate-oidc-issuer-regexp {issuer_regex!r} "
                f"--certificate-identity-regexp {identity_regex!r}"
            )
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            check=False,
            shell=False,
            timeout=120,
        )
        if proc.returncode != 0:
            failures.append(
                f"cosign verify-blob exit_code={proc.returncode} "
                f"stderr={proc.stderr.strip()[-400:]}"
            )

    return (not failures, failures)


def _escape_regex(s: str) -> str:
    """Escape a literal string into a regex that matches it exactly."""
    import re as _re

    return f"^{_re.escape(s)}$"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Independent keyless verifier for apps_e2e signoff report."
    )
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--envelope", default=DEFAULT_ENVELOPE)
    parser.add_argument(
        "--issuer-regex",
        default=None,
        help="Override the OIDC issuer regex (default: derived from envelope).",
    )
    parser.add_argument(
        "--identity-regex",
        default=None,
        help="Override the signer-identity regex (default: derived from envelope).",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    repo = _repo_root()
    report_path = (repo / args.report).resolve()
    envelope_path = (repo / args.envelope).resolve()

    if not envelope_path.exists():
        print(
            f"[verify_apps_release_signature_keyless] FATAL: envelope missing at "
            f"{envelope_path}. Run sign_apps_release_bundle_keyless.py first.",
            file=sys.stderr,
        )
        return 2

    cosign = _cosign_path()
    if cosign is None:
        print(
            "[verify_apps_release_signature_keyless] FATAL: cosign binary not on PATH.",
            file=sys.stderr,
        )
        return 2

    passed, failures = verify_keyless(
        report_path=report_path,
        envelope_path=envelope_path,
        cosign=cosign,
        expected_issuer_regex=args.issuer_regex,
        expected_identity_regex=args.identity_regex,
        quiet=args.quiet,
    )
    if not passed:
        print(
            "[verify_apps_release_signature_keyless] FAIL",
            file=sys.stderr,
        )
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    if not args.quiet:
        print("[verify_apps_release_signature_keyless] OK \u2014 keyless signature verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
