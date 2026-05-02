"""Spine verifier — UWG blocked-commit receipts are well-formed when present.

R1B / cache-reuse runs do NOT issue a CommitRequest, so there is no
``blocked_commit_receipt.json`` to verify (passes trivially).

Future MANAGED_WORKFLOW or write-class runs that DO issue a
CommitRequest MUST emit either an AtomicCommitReceipt (commit succeeded)
or a BlockedCommitReceipt (commit denied). This verifier validates ANY
present blocked_commit_receipt for shape and identity continuity.

Asserts (when ``blocked_commit_receipt.json`` exists):
  1. ``schema_version`` matches the contract version.
  2. ``no_durable_write_assertion == True``.
  3. ``block_reason`` is in the allowed set.
  4. ``run_id`` / ``request_id`` / ``trace_root`` match the
     RuntimeIdentityEnvelope.
  5. ``deterministic_digest`` is non-empty and prefixed ``sha256:``.

When the file is absent: PASS with note (acceptable for cache-reuse).

Exit codes: 0 PASS / 2 FAIL_CLOSED / 3 HARNESS_ERROR.
"""

from __future__ import annotations

import sys

import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent))
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from _w2_verifier_common import (  # noqa: E402
    EXIT_HARNESS_ERROR,
    fail,
    load_payload,
    passed,
    resolve_artifact_dir,
)

from agentic_core.L4_state.uwg.blocked_commit_receipt import (  # noqa: E402
    ALLOWED_BLOCK_REASONS,
    BLOCKED_COMMIT_RECEIPT_SCHEMA_VERSION,
)


def main(argv: list[str]) -> int:
    art_dir = resolve_artifact_dir(argv[1] if len(argv) > 1 else None)
    print(f"[verify_uwg_blocked_commit_receipts] artifact_dir={art_dir}")

    receipt_path = art_dir / "blocked_commit_receipt.json"
    if not receipt_path.exists():
        return passed(
            "no blocked_commit_receipt.json present (acceptable: "
            "cache-reuse and read-only paths do not issue CommitRequest)"
        )

    receipt = load_payload(art_dir, "blocked_commit_receipt.json")

    if receipt.get("schema_version") != BLOCKED_COMMIT_RECEIPT_SCHEMA_VERSION:
        return fail(
            "BLOCKED_COMMIT_SCHEMA_VERSION_MISMATCH",
            f"schema_version={receipt.get('schema_version')!r} != "
            f"{BLOCKED_COMMIT_RECEIPT_SCHEMA_VERSION!r}",
        )
    if receipt.get("no_durable_write_assertion") is not True:
        return fail(
            "BLOCKED_COMMIT_DURABLE_WRITE_ASSERTION_FALSE",
            "no_durable_write_assertion must be True on a BlockedCommitReceipt",
        )
    reason = receipt.get("block_reason", "")
    if reason not in ALLOWED_BLOCK_REASONS:
        return fail(
            "BLOCKED_COMMIT_REASON_INVALID",
            f"block_reason={reason!r} not in {sorted(ALLOWED_BLOCK_REASONS)}",
        )
    digest = receipt.get("deterministic_digest", "")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        return fail(
            "BLOCKED_COMMIT_DIGEST_INVALID",
            f"deterministic_digest={digest!r} must be sha256:<hex>",
        )

    # Identity continuity.
    try:
        identity = load_payload(art_dir, "runtime_identity_envelope.json")
    except FileNotFoundError as exc:
        return fail("RUNTIME_IDENTITY_ENVELOPE_MISSING", str(exc))
    for key in ("run_id", "request_id", "trace_root"):
        if receipt.get(key) != identity.get(key):
            return fail(
                "BLOCKED_COMMIT_IDENTITY_DIVERGENCE",
                f"{key}: receipt={receipt.get(key)!r} != identity={identity.get(key)!r}",
            )

    return passed(f"BlockedCommitReceipt valid: block_reason={reason!r}")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # noqa: BLE001 - top-level harness boundary
        print(f"HARNESS_ERROR: {exc}")
        sys.exit(EXIT_HARNESS_ERROR)
