"""CI gate: verify the runtime HITL ledger audit chain (W7 P7.1).

Per plan runtime-hitl-exit-control-c4e7b3 W7 and ADR-023 §5:
this script opens a ``hitl_audit_chain`` SQLite database and walks every row,
recomputing hashes and (when a public key is supplied) validating ed25519
signatures. On any violation it exits with a non-zero status and prints a
deterministic report.

Usage::

    python ops_scripts/ci/check_runtime_hitl_ledger_integrity.py \
        --audit-db artifacts/runtime/hitl_audit.db \
        [--public-key <hex>] \
        [--public-key-file path/to/pub.bin] \
        [--require-signatures]

Exit codes
----------

0  — chain verified (and — if a key was provided — every signature verified)
1  — chain violations found
2  — bad invocation (missing file, unreadable public key, etc.)

The script does not mutate any artifact — safe to run in read-only CI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agentic_core.L3_orchestration.exit_control.ledger_integrity import (
    AuditChain,
    Ed25519VerifyingKey,
    IntegrityReport,
    VerifyingKey,
)


def _load_verifying_key(args: argparse.Namespace) -> VerifyingKey | None:
    raw_hex: str | None = None
    if args.public_key:
        raw_hex = args.public_key.strip()
    elif args.public_key_file:
        path = Path(args.public_key_file)
        if not path.exists():
            print(f"ERROR: public-key-file not found: {path}", file=sys.stderr)
            raise SystemExit(2)
        raw_hex = path.read_text(encoding="utf-8").strip()
    if raw_hex is None:
        return None
    try:
        raw = bytes.fromhex(raw_hex)
    except ValueError as exc:
        print(f"ERROR: public key not hex-decodable: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    try:
        return Ed25519VerifyingKey(raw)
    except RuntimeError as exc:  # cryptography not installed
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


def _emit_report(report: IntegrityReport, audit_db: Path) -> None:
    out = {
        "audit_db": str(audit_db),
        "ok": report.ok,
        "total_events": report.total_events,
        "verified_events": report.verified_events,
        "signed_events": report.signed_events,
        "verified_signatures": report.verified_signatures,
        "violations": [
            {
                "audit_id": v.audit_id,
                "reason": v.reason,
                "detail": v.detail,
            }
            for v in report.violations
        ],
        "notes": dict(report.notes),
    }
    print(json.dumps(out, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify HITL audit chain integrity (P7.1)",
    )
    parser.add_argument(
        "--audit-db",
        required=True,
        type=Path,
        help="Path to the audit-chain SQLite file",
    )
    parser.add_argument(
        "--public-key",
        default=None,
        help="Ed25519 public key as hex string (optional)",
    )
    parser.add_argument(
        "--public-key-file",
        default=None,
        help="Path to a file containing a hex-encoded ed25519 public key",
    )
    parser.add_argument(
        "--require-signatures",
        action="store_true",
        help=("Fail if any chain row lacks a signature. Implies that a public key must verify all rows."),
    )
    args = parser.parse_args(argv)

    if not args.audit_db.exists():
        print(f"ERROR: audit-db not found: {args.audit_db}", file=sys.stderr)
        return 2

    verifying_key = _load_verifying_key(args)

    chain = AuditChain(args.audit_db)
    try:
        report = chain.verify(verifying_key=verifying_key)
    finally:
        chain.close()

    _emit_report(report, args.audit_db)

    if not report.ok:
        print("FAIL: chain integrity violations detected", file=sys.stderr)
        return 1
    if args.require_signatures and report.signed_events < report.total_events:
        print(
            f"FAIL: --require-signatures set but "
            f"{report.total_events - report.signed_events} unsigned row(s) found",
            file=sys.stderr,
        )
        return 1
    if args.require_signatures and report.verified_signatures < report.signed_events:
        print("FAIL: not all signatures verified", file=sys.stderr)
        return 1
    print("OK: audit chain verified", file=sys.stderr)
    return 0


if __name__ == "__main__":  # pragma: no cover — CLI entry
    raise SystemExit(main())
