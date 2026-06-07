#!/usr/bin/env python3
"""Fort Knox signature envelope writer — Constitutional §32 / ADR-091.

UNSIGNED scaffold. Validates the report shape and rewrites
`artifacts/certification/final_requirement_signoff_report.signature.json`
with the SLSA/Sigstore-pattern envelope fields populated for the
deterministic claims, while marking `signature_verification_status` as
`UNSIGNED_BLOCKED`. Actual signing (cosign keyless via GitHub OIDC) is
deferred to a follow-up Author-Gate that picks the signer identity —
see ADR-091 §"Deferred decisions".

This file is the legacy-allowlisted entrypoint at `scripts/`
(constitutional §31 allowlist: `verify_*`/`scripts/proof/**`/etc.) The
script does not introduce a new tier-verify pattern; it sits with its
canonical compiler/verifier siblings in `scripts/`.

Exit codes:
    0 — envelope rewrite succeeded; status=UNSIGNED_BLOCKED (expected)
    1 — report or sidecar invalid; refused to populate envelope
    2 — `--enforce` was passed but no real signer is wired yet

Usage:
    python scripts/sign_requirement_signoff.py
    python scripts/sign_requirement_signoff.py --enforce   # pin to fail until ADR-091 P5b lands

Bypass: `FORTKNOX_DISCIPLINE_BYPASS=1` (skips rewrite, exit 0).

Producer-allowlist note: this script DOES NOT emit atomic assertions; it
only updates the envelope. Constitutional §32 emitter restrictions do
not apply here.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
from pathlib import Path


_REPORT_NAME = "final_requirement_signoff_report.json"
_ENVELOPE_NAME = "final_requirement_signoff_report.signature.json"
_SHA_NAME = "final_requirement_signoff_report.sha256"

_PENDING_SIGNER = "cosign-keyless-via-github-oidc-pending-adr-091-p5b"


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here, *here.parents]:
        if (p / ".git").exists():
            return p
    return Path.cwd()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _validate_report_shape(report: dict) -> str | None:
    """Return None on OK, error string on shape violation."""
    if not isinstance(report, dict):
        return "report root is not a JSON object"
    for required in ("trust_level", "rows", "row_digest", "evidence_digest"):
        if required not in report:
            return f"report missing required field {required!r}"
    rows = report.get("rows")
    if not isinstance(rows, list):
        return "report.rows is not a list"
    return None


def _read_sidecar_sha(sidecar_path: Path) -> str | None:
    """Parse a `<hex>  <filename>` line; return the hex or None."""
    try:
        text = sidecar_path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    # Accept either bare hex or `hex  filename` (sha256sum format).
    parts = text.split()
    if not parts:
        return None
    candidate = parts[0]
    if len(candidate) == 64 and all(c in "0123456789abcdef" for c in candidate.lower()):
        return candidate.lower()
    return None


def _build_envelope(report_bytes: bytes, sidecar_sha: str | None, report: dict) -> dict:
    """Produce the canonical envelope. Deterministic across runs."""
    report_sha = _sha256_bytes(report_bytes)
    if sidecar_sha and sidecar_sha != report_sha:
        # Drift between sidecar and actual file — flag in envelope notes,
        # but still record both for forensic reconstruction.
        sha_status = "DRIFT"
    elif sidecar_sha:
        sha_status = "MATCHES_SIDECAR"
    else:
        sha_status = "SIDECAR_MISSING"

    envelope = {
        "schema_version": "fortknox-signature-envelope-v1",
        "envelope_generated_at_utc": _utc_now(),
        "report_filename": _REPORT_NAME,
        "report_sha256": report_sha,
        "sidecar_sha256": sidecar_sha,
        "report_sha_vs_sidecar": sha_status,
        "report_trust_level": report.get("trust_level"),
        "report_row_count": len(report.get("rows") or []),
        "merkle_root": (report.get("merkle") or {}).get("root") or report.get("merkle_root"),
        "signed_bytes_sha256": None,
        "signer_identity": None,
        "signer_identity_pending": _PENDING_SIGNER,
        "signing_timestamp_utc": None,
        "signature_algorithm": None,
        "signature_value": None,
        "signature_verification_status": "UNSIGNED_BLOCKED",
        "transparency_log_entry_id": None,
        "notes": (
            "Scaffold envelope — actual signing requires cosign keyless via "
            "GitHub OIDC (ADR-091 §Deferred decisions). Until then, the "
            "trust_level upgrade path SIGNED_PROOF / FINAL_SIGNED_CERTIFICATION "
            "remains gated. See .cursor/rules/fortknox-certification-discipline.md."
        ),
    }
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Exit 2 instead of 0 when no real signer is wired (CI canary).",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Override path to the final report JSON.",
    )
    args = parser.parse_args()

    if os.environ.get("FORTKNOX_DISCIPLINE_BYPASS") == "1":
        print("[sign_requirement_signoff] BYPASS (FORTKNOX_DISCIPLINE_BYPASS=1)")
        return 0

    repo = _repo_root()
    cert_dir = repo / "artifacts" / "certification"
    report_path = Path(args.report) if args.report else cert_dir / _REPORT_NAME
    envelope_path = cert_dir / _ENVELOPE_NAME
    sidecar_path = cert_dir / _SHA_NAME

    if not report_path.exists():
        print(f"[sign_requirement_signoff] FAIL: report missing at {report_path}", file=sys.stderr)
        return 1

    try:
        report_bytes = report_path.read_bytes()
        report = json.loads(report_bytes.decode("utf-8"))
    except (OSError, ValueError) as exc:
        print(f"[sign_requirement_signoff] FAIL: report unreadable: {exc}", file=sys.stderr)
        return 1

    err = _validate_report_shape(report)
    if err is not None:
        print(f"[sign_requirement_signoff] FAIL: invalid report shape — {err}", file=sys.stderr)
        return 1

    sidecar_sha = _read_sidecar_sha(sidecar_path) if sidecar_path.exists() else None
    envelope = _build_envelope(report_bytes, sidecar_sha, report)

    cert_dir.mkdir(parents=True, exist_ok=True)
    envelope_path.write_text(
        json.dumps(envelope, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(
        f"[sign_requirement_signoff] envelope rewritten — "
        f"status={envelope['signature_verification_status']!r} "
        f"sha256={envelope['report_sha256'][:12]}... "
        f"sidecar={envelope['report_sha_vs_sidecar']}"
    )

    if args.enforce:
        print(
            "[sign_requirement_signoff] --enforce passed, but no real signer is "
            "wired (ADR-091 §Deferred decisions). Exit 2.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
