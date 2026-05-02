"""W9 of plan apps-fort-knox-parity-c5d9a3 \u2014 Sigstore keyless signer for apps_e2e.

Wraps the canonical ``cosign sign-blob`` CLI to produce a Sigstore Fulcio
keyless signature envelope for the apps_e2e signoff report. Designed to
run in GitHub Actions where the OIDC token is automatically present;
will refuse to run locally without explicit interactive override.

Output schema (alongside the dev-keypair envelope from W5):

    artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.keyless.json

Fields:
    schema_version:           "apps_e2e_keyless_signature/v1"
    signing_method:           "keyless_cosign"
    report_sha256:            sha256 of apps_e2e_signoff_report.json
    signature_b64:            base64-encoded raw signature bytes
    fulcio_certificate_pem:   PEM-encoded leaf certificate from Fulcio
    rekor_log_index:          integer index in the Rekor transparency log
    rekor_uuid:               UUID of the Rekor entry
    oidc_issuer:              expected OIDC issuer (e.g. GitHub Actions)
    signer_identity_subject:  expected subject (workflow + ref)
    signed_at_utc:            ISO-8601 timestamp
    cosign_version:           output of ``cosign version`` (str)

Security floor: this tool does NOT verify what it just signed. The W6
consolidator + verifier extension run a separate ``cosign verify-blob``
to confirm the Fulcio cert + Rekor entry chain. That is the hostile-
verifier path \u2014 the same discipline as W5.

Local execution: refused unless ``--allow-local-keyless`` is passed and
``COSIGN_EXPERIMENTAL=1`` is set, AND the user has cosign + a working
browser-based OIDC flow. Local mode is for debugging the integration,
not producing release signatures.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

KEYLESS_SCHEMA_VERSION = "apps_e2e_keyless_signature/v1"
DEFAULT_REPORT = "artifacts/certification/apps_e2e/apps_e2e_signoff_report.json"
DEFAULT_OUTPUT = "artifacts/certification/apps_e2e/apps_e2e_signoff_report.signature.keyless.json"
GITHUB_OIDC_ISSUER = "https://token.actions.githubusercontent.com"


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / ".git").exists():
            return p
    return Path.cwd()


def _cosign_path() -> str | None:
    """Return path to cosign binary, or None if not on PATH."""
    return shutil.which("cosign")


def _cosign_version(cosign: str) -> str:
    proc = subprocess.run(
        [cosign, "version", "--json"],
        capture_output=True,
        text=True,
        check=False,
        shell=False,
        timeout=15,
    )
    if proc.returncode != 0:
        return "unknown"
    try:
        return json.loads(proc.stdout).get("GitVersion", "unknown")
    except json.JSONDecodeError:
        return proc.stdout.strip().splitlines()[0] if proc.stdout else "unknown"


def _is_github_actions() -> bool:
    """Detect GitHub Actions runtime via well-known env vars."""
    return (
        os.environ.get("GITHUB_ACTIONS") == "true"
        and bool(os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN"))
    )


def _expected_signer_identity_subject() -> str:
    """Compose the expected OIDC subject for the current GHA workflow.

    Format: ``https://github.com/<repo>/.github/workflows/<wf>@<ref>``
    Example: ``https://github.com/Siamese001/Agentic-Workflow/.github/workflows/apps-fortknox-keyless-sign.yml@refs/tags/v1.0.0``
    """
    repo = os.environ.get("GITHUB_REPOSITORY", "Siamese001/Agentic-Workflow")
    workflow_ref = os.environ.get("GITHUB_WORKFLOW_REF", "")
    if workflow_ref:
        return f"https://github.com/{workflow_ref.split('@')[0]}@{workflow_ref.split('@')[-1]}"
    # Fallback shape using individual env vars.
    workflow = os.environ.get("GITHUB_WORKFLOW", "apps-fortknox-keyless-sign")
    ref = os.environ.get("GITHUB_REF", "refs/heads/main")
    return f"https://github.com/{repo}/.github/workflows/{workflow}.yml@{ref}"


def sign_keyless(
    *,
    report_path: Path,
    output_path: Path,
    cosign: str,
    expected_subject: str,
    issuer: str,
) -> dict:
    """Run ``cosign sign-blob`` on the report; emit the keyless envelope dict.

    Side effects:
        - Hits Fulcio CA for an ephemeral signing certificate
        - Writes signature + cert to a Rekor transparency log entry
        - Both side effects require either OIDC token (CI) or browser flow (local)
    """
    if not report_path.exists():
        raise FileNotFoundError(f"signoff report missing: {report_path}")

    report_bytes = report_path.read_bytes()
    report_sha256 = hashlib.sha256(report_bytes).hexdigest()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        cert_path = tmp_dir / "cosign.cert"
        sig_path = tmp_dir / "cosign.sig"

        argv = [
            cosign,
            "sign-blob",
            "--yes",
            "--output-certificate",
            str(cert_path),
            "--output-signature",
            str(sig_path),
            str(report_path),
        ]
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            check=False,
            shell=False,
            timeout=120,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"cosign sign-blob failed: rc={proc.returncode}\nstdout={proc.stdout}\nstderr={proc.stderr}"
            )

        signature_b64 = sig_path.read_text(encoding="utf-8").strip()
        certificate_pem = cert_path.read_text(encoding="utf-8")

    # cosign 2.x prints the Rekor entry URL on stderr; parse if present.
    rekor_log_index, rekor_uuid = _parse_rekor_from_cosign_output(
        proc.stdout + proc.stderr
    )

    envelope = {
        "schema_version": KEYLESS_SCHEMA_VERSION,
        "signing_method": "keyless_cosign",
        "report_sha256": report_sha256,
        "report_path": str(report_path.relative_to(_repo_root())).replace("\\", "/"),
        "signature_b64": signature_b64,
        "fulcio_certificate_pem": certificate_pem,
        "rekor_log_index": rekor_log_index,
        "rekor_uuid": rekor_uuid,
        "oidc_issuer": issuer,
        "signer_identity_subject": expected_subject,
        "signed_at_utc": datetime.now(timezone.utc).isoformat(),
        "cosign_version": _cosign_version(cosign),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(envelope, sort_keys=True, indent=2), encoding="utf-8"
    )
    return envelope


def _parse_rekor_from_cosign_output(text: str) -> tuple[int | None, str | None]:
    """Best-effort parse of ``tlog entry created with index: <N> and uuid: <UUID>``."""
    rekor_log_index: int | None = None
    rekor_uuid: str | None = None
    for line in text.splitlines():
        s = line.strip()
        if "index:" in s:
            try:
                # Format: "tlog entry created with index: 12345"
                tail = s.split("index:", 1)[1].strip().split()[0].rstrip(",")
                rekor_log_index = int(tail)
            except (ValueError, IndexError):
                pass
        if "uuid:" in s:
            try:
                rekor_uuid = s.split("uuid:", 1)[1].strip().split()[0]
            except IndexError:
                pass
    return rekor_log_index, rekor_uuid


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Keyless Sigstore signer for apps_e2e signoff report."
    )
    parser.add_argument(
        "--report",
        default=DEFAULT_REPORT,
        help=f"Path to signoff report (default: {DEFAULT_REPORT})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output path for keyless envelope (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--issuer",
        default=GITHUB_OIDC_ISSUER,
        help=f"Expected OIDC issuer (default: {GITHUB_OIDC_ISSUER})",
    )
    parser.add_argument(
        "--allow-local-keyless",
        action="store_true",
        help="Allow execution outside GitHub Actions (requires browser OIDC flow).",
    )
    args = parser.parse_args(argv)

    repo = _repo_root()
    report_path = (repo / args.report).resolve()
    output_path = (repo / args.output).resolve()

    if not _is_github_actions() and not args.allow_local_keyless:
        print(
            "[sign_apps_release_bundle_keyless] REFUSED: not in GitHub Actions "
            "and --allow-local-keyless not set. The keyless flow REQUIRES an "
            "OIDC identity provider; running locally without --allow-local-keyless "
            "would either fail (no token) or open a browser flow that produces a "
            "user-identity signature, which is NOT what release CI should commit.",
            file=sys.stderr,
        )
        return 2

    cosign = _cosign_path()
    if cosign is None:
        print(
            "[sign_apps_release_bundle_keyless] FATAL: cosign binary not on PATH. "
            "In CI, install via sigstore/cosign-installer@v3 GitHub Action. "
            "Locally, install from https://github.com/sigstore/cosign/releases.",
            file=sys.stderr,
        )
        return 2

    try:
        envelope = sign_keyless(
            report_path=report_path,
            output_path=output_path,
            cosign=cosign,
            expected_subject=_expected_signer_identity_subject(),
            issuer=args.issuer,
        )
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"[sign_apps_release_bundle_keyless] FAIL: {exc}", file=sys.stderr)
        return 1

    print(
        f"[sign_apps_release_bundle_keyless] OK \u2014 "
        f"report_sha256={envelope['report_sha256'][:16]}... "
        f"rekor_log_index={envelope['rekor_log_index']} "
        f"cosign={envelope['cosign_version']}"
    )
    print(f"  envelope: {output_path.relative_to(_repo_root())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
