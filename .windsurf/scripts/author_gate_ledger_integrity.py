#!/usr/bin/env python3
"""
author_gate_ledger_integrity.py — Hash-chain integrity for the Author-Gate ledger.

Implements the W5 deliverable:
  - compute_row_hash   → deterministic SHA-256 over canonicalized row + prev_hash
  - canonicalize_row   → stable JSON serialization, excluding self-referential columns
  - verify_chain       → walks the ledger in order, reports first break
  - backfill_chain     → one-shot populator for existing NULL-hash rows
  - ensure_row_hash    → INSERT-time helper (called by post_cascade_hitl_capture)

INVARIANTS
----------
  - Genesis row: prev_hash = "0" * 64
  - Chain order: ORDER BY created_at ASC, decision_id ASC
  - Canonical blob EXCLUDES: prev_hash, row_hash, sig_alg, signature
    (self-referential; would change the hash)
  - Canonical blob EXCLUDES: status (mutable — can transition surfaced → executed)
    To keep the chain stable across lifecycle transitions, status is NOT hashed.
    Outcome mutations live in decision_outcomes which is a separate table.
  - Hash encoding: hexdigest lowercase

USAGE AS LIBRARY
----------------
    from author_gate_ledger_integrity import verify_chain, backfill_chain

    ok, broken_id, err = verify_chain(DB_PATH)
    if not ok:
        ...

USAGE AS CLI
------------
    python .windsurf/scripts/author_gate_ledger_integrity.py --verify
    python .windsurf/scripts/author_gate_ledger_integrity.py --backfill
    python .windsurf/scripts/author_gate_ledger_integrity.py --report

CONSTITUTIONAL
    - No subprocess, no shell, pure stdlib (sqlite3, hashlib, json)
    - Specific exceptions: sqlite3.Error, json.JSONDecodeError, OSError
    - UTF-8 on all reads/writes
    - Bounded: chain walk uses streaming cursor, not full load
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = REPO_ROOT / ".windsurf" / "state" / "refactor_decisions" / "refactor_decision_ledger.sqlite"

GENESIS_PREV_HASH = "0" * 64
HASH_ALGO = "sha256"
SIGNING_KEY_ENV = "AUTHOR_GATE_SIGNING_KEY"  # guardian: allow-hardcoded-secret -- env-var NAME, not a secret value; actual signing key loaded from os.environ at runtime
SIG_ALG_NONE = "none"
SIG_ALG_HMAC = "hmac-sha256"
# ed25519 upgrade path: when cryptography lib is available + pubkey distributed,
# sig_alg = "ed25519" with signature = hex(ed25519.sign(row_hash)). The sig_alg
# column already accepts arbitrary strings so the schema is forward-compatible.

# Columns excluded from the canonical blob (self-referential or mutable).
_EXCLUDED_COLUMNS: frozenset[str] = frozenset(
    {
        "prev_hash",
        "row_hash",
        "sig_alg",
        "signature",
        "status",  # mutable lifecycle flag; see module docstring
    }
)


# ===================================================================== #
# Canonicalization + hashing                                            #
# ===================================================================== #


def canonicalize_row(row: dict) -> str:
    """Return stable JSON for the hashable subset of a decisions row.

    Sorts keys, excludes self-referential columns, normalizes None/"" to "",
    serializes everything as strings for cross-SQLite-driver stability.
    """
    cleaned: dict[str, str] = {}
    for k, v in row.items():
        if k in _EXCLUDED_COLUMNS:
            continue
        if v is None:
            cleaned[k] = ""
        elif isinstance(v, (int, float)):
            cleaned[k] = str(v)
        elif isinstance(v, bytes):
            cleaned[k] = v.hex()
        else:
            cleaned[k] = str(v)
    return json.dumps(cleaned, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def compute_row_hash(row: dict, prev_hash: str) -> str:
    """SHA-256 over `prev_hash || canonical(row)`."""
    h = hashlib.sha256()
    h.update(prev_hash.encode("ascii"))
    h.update(b"\n")
    h.update(canonicalize_row(row).encode("utf-8"))
    return h.hexdigest()


# ===================================================================== #
# Signing (opt-in HMAC-SHA256; forward-compat for ed25519)              #
# ===================================================================== #


def _get_signing_key() -> bytes | None:
    """Return the signing key bytes from AUTHOR_GATE_SIGNING_KEY or None.

    Key formats accepted:
      - raw utf-8 string (minimum 32 bytes)
      - hex:HEXDIGITS (decoded as hex)
      - file:PATH  (read bytes from file; useful for keys managed outside shell)
    """
    raw = os.environ.get(SIGNING_KEY_ENV)
    if not raw:
        return None
    try:
        if raw.startswith("hex:"):
            return bytes.fromhex(raw[4:])
        if raw.startswith("file:"):
            key_path = Path(raw[5:])
            if not key_path.is_absolute():
                key_path = REPO_ROOT / key_path
            return key_path.read_bytes().strip()
        data = raw.encode("utf-8")
        if len(data) < 32:
            print(
                f"[ledger_integrity] WARNING: {SIGNING_KEY_ENV} is <32 bytes; refusing to sign",
                file=sys.stderr,
            )
            return None
        return data
    except (OSError, ValueError):
        return None


def compute_signature(row_hash: str, key: bytes) -> str:
    """HMAC-SHA256 of row_hash under the signing key. Returns hex digest."""
    mac = hmac.new(key, row_hash.encode("ascii"), hashlib.sha256)
    return mac.hexdigest()


def verify_signature(row_hash: str, sig_alg: str | None, signature: str | None, key: bytes | None) -> bool:
    """Return True if signature matches (or no signing was configured).

    Policy:
      - sig_alg is None / 'none' → unsigned; pass (chain already protects integrity)
      - sig_alg == 'hmac-sha256' AND key present → must match
      - sig_alg == 'hmac-sha256' AND no key → cannot verify; treated as PASS
        (signing is opt-in verification; absence of key on consumer side is allowed)
      - unknown sig_alg (e.g. future 'ed25519' without lib) → PASS with warning
    """
    if not sig_alg or sig_alg == SIG_ALG_NONE:
        return True
    if sig_alg == SIG_ALG_HMAC:
        if key is None:
            return True  # cannot verify without key; do not fail chain walk
        if not signature:
            return False
        expected = compute_signature(row_hash, key)
        return hmac.compare_digest(expected, signature)
    # Forward-compat: unknown algorithm, do not fail the chain.
    print(
        f"[ledger_integrity] INFO: unknown sig_alg {sig_alg!r}; skipping signature verify",
        file=sys.stderr,
    )
    return True


# ===================================================================== #
# Chain walker                                                          #
# ===================================================================== #


def _open_db(db_path: Path) -> sqlite3.Connection | None:
    if not db_path.exists():
        return None
    try:
        conn = sqlite3.connect(str(db_path), timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error:
        return None


def _iter_rows(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    """Yield decisions rows in canonical chain order."""
    cur = conn.execute(
        """
        SELECT * FROM decisions
         ORDER BY created_at ASC, decision_id ASC
        """
    )
    yield from cur


@dataclass
class ChainResult:
    ok: bool
    total_rows: int
    verified_rows: int
    first_broken_id: str | None
    reason: str | None


def verify_chain(db_path: Path = DB_PATH) -> ChainResult:
    """Walk the decisions table in canonical order and verify the hash chain.

    Returns ChainResult with first_broken_id set at the first row whose stored
    row_hash does not match the recomputed value.

    Rows with NULL row_hash are treated as "unsealed" — skipped from chain check
    but counted in total_rows. Use backfill_chain to seal them.
    """
    conn = _open_db(db_path)
    if conn is None:
        return ChainResult(
            ok=True,
            total_rows=0,
            verified_rows=0,
            first_broken_id=None,
            reason="ledger db not present — treated as empty",
        )
    key = _get_signing_key()
    try:
        prev_hash = GENESIS_PREV_HASH
        total = 0
        verified = 0
        for row in _iter_rows(conn):
            total += 1
            row_dict = dict(row)
            stored_hash = row_dict.get("row_hash")
            stored_prev = row_dict.get("prev_hash")

            if stored_hash is None or stored_prev is None:
                # Unsealed row — cannot verify, but do not break the chain.
                # backfill_chain should be run to seal it.
                continue

            if stored_prev != prev_hash:
                return ChainResult(
                    ok=False,
                    total_rows=total,
                    verified_rows=verified,
                    first_broken_id=row_dict.get("decision_id"),
                    reason=f"prev_hash mismatch: expected {prev_hash[:12]}…, got {str(stored_prev)[:12]}…",
                )

            expected = compute_row_hash(row_dict, prev_hash)
            if expected != stored_hash:
                return ChainResult(
                    ok=False,
                    total_rows=total,
                    verified_rows=verified,
                    first_broken_id=row_dict.get("decision_id"),
                    reason=f"row_hash mismatch: expected {expected[:12]}…, got {str(stored_hash)[:12]}…",
                )

            # Signature verification (opt-in; only fails if we have the key AND it mismatches)
            if not verify_signature(
                str(stored_hash),
                row_dict.get("sig_alg"),
                row_dict.get("signature"),
                key,
            ):
                return ChainResult(
                    ok=False,
                    total_rows=total,
                    verified_rows=verified,
                    first_broken_id=row_dict.get("decision_id"),
                    reason=f"signature mismatch under sig_alg={row_dict.get('sig_alg')}",
                )

            prev_hash = stored_hash
            verified += 1

        return ChainResult(
            ok=True, total_rows=total, verified_rows=verified, first_broken_id=None, reason=None
        )
    finally:
        conn.close()


# ===================================================================== #
# Backfill (one-shot seal for existing NULL-hash rows)                  #
# ===================================================================== #


def backfill_chain(db_path: Path = DB_PATH, dry_run: bool = False) -> ChainResult:
    """Populate prev_hash + row_hash + sig_alg for rows where they are NULL.

    Walks rows in canonical order. For each row with NULL hashes, computes the
    value based on the current chain tail and writes it back. Rows that already
    have hashes are verified; any mismatch aborts the backfill.
    """
    conn = _open_db(db_path)
    if conn is None:
        return ChainResult(
            ok=True,
            total_rows=0,
            verified_rows=0,
            first_broken_id=None,
            reason="ledger db not present — nothing to backfill",
        )
    conn.isolation_level = None  # autocommit per statement; explicit tx below
    total = 0
    sealed = 0
    try:
        conn.execute("BEGIN IMMEDIATE")
        prev_hash = GENESIS_PREV_HASH
        for row in _iter_rows(conn):
            total += 1
            row_dict = dict(row)
            decision_id = row_dict.get("decision_id")
            stored_prev = row_dict.get("prev_hash")
            stored_hash = row_dict.get("row_hash")

            if stored_prev is not None and stored_hash is not None:
                # Already sealed — verify before advancing tail
                if stored_prev != prev_hash:
                    conn.execute("ROLLBACK")
                    return ChainResult(
                        ok=False,
                        total_rows=total,
                        verified_rows=sealed,
                        first_broken_id=decision_id,
                        reason=f"existing chain broken at {decision_id}: prev_hash mismatch",
                    )
                expected = compute_row_hash(row_dict, prev_hash)
                if expected != stored_hash:
                    conn.execute("ROLLBACK")
                    return ChainResult(
                        ok=False,
                        total_rows=total,
                        verified_rows=sealed,
                        first_broken_id=decision_id,
                        reason=f"existing chain broken at {decision_id}: row_hash mismatch",
                    )
                prev_hash = stored_hash
                continue

            # Seal this row — compute row_hash; if signing key present, co-sign
            new_hash = compute_row_hash(row_dict, prev_hash)
            key = _get_signing_key()
            if key is not None:
                sig_alg_val = SIG_ALG_HMAC
                sig_val: str | None = compute_signature(new_hash, key)
            else:
                sig_alg_val = SIG_ALG_NONE
                sig_val = None
            if not dry_run:
                conn.execute(
                    """
                    UPDATE decisions
                       SET prev_hash = ?, row_hash = ?, sig_alg = ?, signature = ?
                     WHERE decision_id = ?
                    """,
                    (prev_hash, new_hash, sig_alg_val, sig_val, decision_id),
                )
            sealed += 1
            prev_hash = new_hash

        if dry_run:
            conn.execute("ROLLBACK")
        else:
            conn.execute("COMMIT")
    except sqlite3.Error as exc:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:  # guardian: allow-rollback-failure -- best-effort cleanup
            pass
        return ChainResult(
            ok=False,
            total_rows=total,
            verified_rows=sealed,
            first_broken_id=None,
            reason=f"sqlite error: {exc}",
        )
    finally:
        conn.close()

    return ChainResult(
        ok=True,
        total_rows=total,
        verified_rows=sealed,
        first_broken_id=None,
        reason=f"backfill {'(dry-run) would seal' if dry_run else 'sealed'} {sealed} row(s)",
    )


def resign_chain(db_path: Path = DB_PATH) -> ChainResult:
    """Resign every sealed row under the current AUTHOR_GATE_SIGNING_KEY.

    Reads each row's existing row_hash (which is based on immutable hashed columns)
    and writes a fresh HMAC signature. The chain is NOT rebuilt — only sig_alg and
    signature columns change. Requires AUTHOR_GATE_SIGNING_KEY to be set.

    Use this when:
      - First enabling signing on an existing ledger
      - Rotating the signing key (re-sign under new key)
    """
    key = _get_signing_key()
    if key is None:
        return ChainResult(
            ok=False,
            total_rows=0,
            verified_rows=0,
            first_broken_id=None,
            reason=f"{SIGNING_KEY_ENV} not set — cannot sign",
        )
    conn = _open_db(db_path)
    if conn is None:
        return ChainResult(
            ok=True, total_rows=0, verified_rows=0, first_broken_id=None, reason="ledger db not present"
        )
    conn.isolation_level = None
    signed = 0
    total = 0
    try:
        conn.execute("BEGIN IMMEDIATE")
        for row in _iter_rows(conn):
            total += 1
            rh = row["row_hash"]
            if rh is None:
                continue  # unsealed row — needs backfill first
            sig = compute_signature(str(rh), key)
            conn.execute(
                "UPDATE decisions SET sig_alg = ?, signature = ? WHERE decision_id = ?",
                (SIG_ALG_HMAC, sig, row["decision_id"]),
            )
            signed += 1
        conn.execute("COMMIT")
    except sqlite3.Error as exc:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:  # guardian: allow-rollback-failure -- best-effort cleanup
            pass
        return ChainResult(
            ok=False,
            total_rows=total,
            verified_rows=signed,
            first_broken_id=None,
            reason=f"sqlite error: {exc}",
        )
    finally:
        conn.close()
    return ChainResult(
        ok=True,
        total_rows=total,
        verified_rows=signed,
        first_broken_id=None,
        reason=f"resigned {signed} row(s) under {SIG_ALG_HMAC}",
    )


# ===================================================================== #
# INSERT helper (called by post_cascade_author_gate_capture.py on write)       #
# ===================================================================== #


def ensure_row_hash(conn: sqlite3.Connection, decision_id: str) -> str | None:
    """After INSERTing a decision row, compute and store its hashes.

    Caller must have already committed the INSERT. Returns the row_hash on
    success, None on any error (fail-open: we never block the write on
    integrity bookkeeping).
    """
    try:
        cur = conn.execute("SELECT * FROM decisions WHERE decision_id = ?", (decision_id,))
        row = cur.fetchone()
        if row is None:
            return None

        # Determine the prev_hash from the most recent sealed row (strictly earlier)
        cur2 = conn.execute(
            """
            SELECT row_hash FROM decisions
             WHERE row_hash IS NOT NULL
               AND (created_at < ?
                    OR (created_at = ? AND decision_id < ?))
             ORDER BY created_at DESC, decision_id DESC
             LIMIT 1
            """,
            (row["created_at"], row["created_at"], decision_id),
        )
        prev_row = cur2.fetchone()
        prev_hash = prev_row[0] if prev_row else GENESIS_PREV_HASH

        row_dict = dict(row)
        new_hash = compute_row_hash(row_dict, prev_hash)
        key = _get_signing_key()
        if key is not None:
            sig_alg_val = SIG_ALG_HMAC
            sig_val: str | None = compute_signature(new_hash, key)
        else:
            sig_alg_val = SIG_ALG_NONE
            sig_val = None
        conn.execute(
            """
            UPDATE decisions
               SET prev_hash = ?, row_hash = ?, sig_alg = ?, signature = ?
             WHERE decision_id = ?
            """,
            (prev_hash, new_hash, sig_alg_val, sig_val, decision_id),
        )
        conn.commit()
        return new_hash
    except sqlite3.Error:
        return None


# ===================================================================== #
# CLI                                                                   #
# ===================================================================== #


def _print_result(label: str, res: ChainResult) -> int:
    if res.ok:
        print(
            f"[{label}] OK — total={res.total_rows} verified={res.verified_rows} {res.reason or ''}".rstrip()
        )
        return 0
    print(
        f"[{label}] FAIL — broke at {res.first_broken_id} after {res.verified_rows} "
        f"verified row(s) of {res.total_rows}",
        file=sys.stderr,
    )
    if res.reason:
        print(f"  reason: {res.reason}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Author-Gate ledger hash-chain tool.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--verify", action="store_true", help="Walk chain; exit 1 on break")
    mode.add_argument("--backfill", action="store_true", help="Seal NULL-hash rows in place")
    mode.add_argument("--backfill-dry-run", action="store_true", help="Report what backfill would seal")
    mode.add_argument(
        "--resign",
        action="store_true",
        help=f"Resign sealed rows under ${SIGNING_KEY_ENV} (for initial enablement / key rotation)",
    )
    mode.add_argument("--report", action="store_true", help="Verify + print chain summary")
    args = parser.parse_args()

    if args.verify or args.report:
        res = verify_chain()
        rc = _print_result("ledger_integrity", res)
        if args.report:
            print(f"  db: {DB_PATH}")
            print(f"  total_rows: {res.total_rows}")
            print(f"  verified_rows: {res.verified_rows}")
            if res.total_rows > res.verified_rows:
                print(f"  unsealed_rows: {res.total_rows - res.verified_rows} — run --backfill")
        return rc

    if args.backfill or args.backfill_dry_run:
        res = backfill_chain(dry_run=args.backfill_dry_run)
        return _print_result("ledger_backfill", res)

    if args.resign:
        res = resign_chain()
        return _print_result("ledger_resign", res)

    return 0


if __name__ == "__main__":
    sys.exit(main())
