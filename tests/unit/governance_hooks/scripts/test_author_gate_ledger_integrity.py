# pylint: disable=protected-access
"""Unit tests for .claude/governance/scripts/author_gate_ledger_integrity.py.

Coverage:
    canonicalize_row    - excludes mutable + self-referential columns,
                          deterministic across field order
    compute_row_hash    - deterministic, prev_hash-dependent
    compute_signature   - HMAC-SHA256 round-trip
    verify_signature    - sig_alg=none pass, hmac pass/fail, unknown pass
    verify_chain        - empty db, sealed chain, prev_hash break, row_hash break
    backfill_chain      - seals NULL-hash rows, idempotent
    ensure_row_hash     - assigns hash after INSERT, fail-open on missing row
    resign_chain        - rotates signatures under new key
    _get_signing_key    - raw / hex: / file: formats; rejects <32 bytes
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parents[4] / ".claude" / "governance/scripts"
sys.path.insert(0, str(_SCRIPTS_DIR))

import author_gate_ledger_integrity as _m  # noqa: E402

from author_gate_ledger_integrity import (  # noqa: E402
    GENESIS_PREV_HASH,
    SIG_ALG_HMAC,
    SIG_ALG_NONE,
    SIGNING_KEY_ENV,
    _get_signing_key,
    backfill_chain,
    canonicalize_row,
    compute_row_hash,
    compute_signature,
    ensure_row_hash,
    resign_chain,
    verify_chain,
    verify_signature,
)


# --------------------------------------------------------------------- #
# Fixtures
# --------------------------------------------------------------------- #


_LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY,
    cascade_id TEXT,
    decision_type TEXT,
    selected_option TEXT,
    rationale TEXT,
    created_at TEXT,
    status TEXT,
    prev_hash TEXT,
    row_hash TEXT,
    sig_alg TEXT DEFAULT 'none',
    signature TEXT
);
"""


@pytest.fixture
def tmp_ledger(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a fresh ledger db and point the module at it."""
    db = tmp_path / "test_ledger.sqlite"
    conn = sqlite3.connect(str(db))
    conn.executescript(_LEDGER_DDL)
    conn.commit()
    conn.close()
    monkeypatch.setattr(_m, "DB_PATH", db)
    return db


def _insert_row(
    db: Path,
    decision_id: str,
    created_at: str = "2026-04-21T10:00:00+00:00",
    decision_type: str = "refactor_scope",
    selected_option: str = "Option-A",
    status: str = "surfaced",
) -> None:
    conn = sqlite3.connect(str(db))
    conn.execute(
        """
        INSERT INTO decisions
            (decision_id, cascade_id, decision_type, selected_option, rationale,
             created_at, status, prev_hash, row_hash, sig_alg, signature)
        VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, 'none', NULL)
        """,
        (decision_id, "cascade_test", decision_type, selected_option, "test rationale", created_at, status),
    )
    conn.commit()
    conn.close()


def _ensure_clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(SIGNING_KEY_ENV, raising=False)


# --------------------------------------------------------------------- #
# canonicalize_row
# --------------------------------------------------------------------- #


class TestCanonicalizeRow:
    def test_excludes_self_referential_columns(self):
        row = {
            "decision_id": "d1",
            "decision_type": "refactor_scope",
            "prev_hash": "abc123",
            "row_hash": "def456",
            "sig_alg": SIG_ALG_HMAC,
            "signature": "sig",
        }
        canonical = canonicalize_row(row)
        assert "prev_hash" not in canonical
        assert "row_hash" not in canonical
        assert "sig_alg" not in canonical
        assert "signature" not in canonical
        assert "decision_id" in canonical
        assert "decision_type" in canonical

    def test_excludes_mutable_status(self):
        """`status` is intentionally excluded so surfaced->executed flip doesn't
        invalidate the chain."""
        row1 = {"decision_id": "d1", "status": "surfaced"}
        row2 = {"decision_id": "d1", "status": "executed"}
        assert canonicalize_row(row1) == canonicalize_row(row2)

    def test_deterministic_regardless_of_field_order(self):
        row_a = {"decision_id": "d1", "decision_type": "refactor", "rationale": "x"}
        row_b = {"rationale": "x", "decision_type": "refactor", "decision_id": "d1"}
        assert canonicalize_row(row_a) == canonicalize_row(row_b)

    def test_null_values_serialized_consistently(self):
        row = {"decision_id": "d1", "cascade_id": None}
        out = canonicalize_row(row)
        assert "d1" in out
        # Should not crash on None


# --------------------------------------------------------------------- #
# compute_row_hash
# --------------------------------------------------------------------- #


class TestComputeRowHash:
    def test_deterministic(self):
        row = {"decision_id": "d1", "decision_type": "refactor_scope"}
        h1 = compute_row_hash(row, GENESIS_PREV_HASH)
        h2 = compute_row_hash(row, GENESIS_PREV_HASH)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex

    def test_prev_hash_propagates(self):
        row = {"decision_id": "d1", "decision_type": "refactor_scope"}
        h_genesis = compute_row_hash(row, GENESIS_PREV_HASH)
        h_other = compute_row_hash(row, "a" * 64)
        assert h_genesis != h_other

    def test_content_change_changes_hash(self):
        row1 = {"decision_id": "d1", "decision_type": "refactor_scope"}
        row2 = {"decision_id": "d1", "decision_type": "deletion_strategy"}
        assert compute_row_hash(row1, GENESIS_PREV_HASH) != compute_row_hash(row2, GENESIS_PREV_HASH)


# --------------------------------------------------------------------- #
# compute_signature + verify_signature
# --------------------------------------------------------------------- #


class TestSigning:
    KEY_A = b"this-is-a-32-plus-byte-test-key-material-1"
    KEY_B = b"different-32-plus-byte-test-key-material-xx"

    def test_hmac_roundtrip(self):
        row_hash = "f" * 64
        sig = compute_signature(row_hash, self.KEY_A)
        assert verify_signature(row_hash, SIG_ALG_HMAC, sig, self.KEY_A) is True

    def test_hmac_detects_wrong_key(self):
        row_hash = "f" * 64
        sig = compute_signature(row_hash, self.KEY_A)
        assert verify_signature(row_hash, SIG_ALG_HMAC, sig, self.KEY_B) is False

    def test_sig_alg_none_always_passes(self):
        assert verify_signature("any", SIG_ALG_NONE, None, self.KEY_A) is True
        assert verify_signature("any", None, None, self.KEY_A) is True

    def test_hmac_without_key_passes_opt_in_semantic(self):
        """Without the key, consumers can't verify — pass to allow partial audits."""
        assert verify_signature("f" * 64, SIG_ALG_HMAC, "anysig", None) is True

    def test_hmac_with_key_but_no_signature_fails(self):
        assert verify_signature("f" * 64, SIG_ALG_HMAC, None, self.KEY_A) is False
        assert verify_signature("f" * 64, SIG_ALG_HMAC, "", self.KEY_A) is False

    def test_unknown_sig_alg_passes_with_info(self, capsys: pytest.CaptureFixture):
        """Forward-compat: future ed25519 etc. do not break verification."""
        assert verify_signature("f" * 64, "ed25519", "any", self.KEY_A) is True


# --------------------------------------------------------------------- #
# _get_signing_key
# --------------------------------------------------------------------- #


class TestGetSigningKey:
    def test_no_env_returns_none(self, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        assert _get_signing_key() is None

    def test_raw_string_32_bytes_accepted(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv(SIGNING_KEY_ENV, "a" * 40)
        assert _get_signing_key() == b"a" * 40

    def test_short_key_rejected(self, monkeypatch: pytest.MonkeyPatch, capsys):
        monkeypatch.setenv(SIGNING_KEY_ENV, "short")
        assert _get_signing_key() is None

    def test_hex_prefix_decoded(self, monkeypatch: pytest.MonkeyPatch):
        # Construct the env value as 'hex:' + 64 hex chars = 32 bytes after decode
        monkeypatch.setenv(SIGNING_KEY_ENV, "hex:" + "deadbeef" * 8)
        key = _get_signing_key()
        assert key is not None
        assert key == bytes.fromhex("deadbeef" * 8)

    def test_file_prefix_reads_file(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
        key_file = tmp_path / "key.bin"
        key_file.write_bytes(b"file-based-key-material-32-bytes-long!!")
        monkeypatch.setenv(SIGNING_KEY_ENV, f"file:{key_file}")
        assert _get_signing_key() == b"file-based-key-material-32-bytes-long!!"


# --------------------------------------------------------------------- #
# verify_chain
# --------------------------------------------------------------------- #


class TestVerifyChain:
    def test_empty_db_passes(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        res = verify_chain(tmp_ledger)
        assert res.ok is True
        assert res.total_rows == 0

    def test_missing_db_file_passes_as_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        res = verify_chain(tmp_path / "does_not_exist.sqlite")
        assert res.ok is True
        assert res.total_rows == 0
        assert res.reason is not None and "not present" in res.reason

    def test_sealed_chain_verifies(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1", created_at="2026-04-21T10:00:00+00:00")
        _insert_row(tmp_ledger, "d2", created_at="2026-04-21T10:01:00+00:00")
        _insert_row(tmp_ledger, "d3", created_at="2026-04-21T10:02:00+00:00")

        seal_res = backfill_chain(tmp_ledger)
        assert seal_res.ok is True

        verify_res = verify_chain(tmp_ledger)
        assert verify_res.ok is True
        assert verify_res.total_rows == 3
        assert verify_res.verified_rows == 3

    def test_tampered_row_hash_detected(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1", created_at="2026-04-21T10:00:00+00:00")
        _insert_row(tmp_ledger, "d2", created_at="2026-04-21T10:01:00+00:00")
        backfill_chain(tmp_ledger)

        # Tamper: modify the decision_type of d2 in place (row_hash unchanged)
        conn = sqlite3.connect(str(tmp_ledger))
        conn.execute("UPDATE decisions SET decision_type='TAMPERED' WHERE decision_id='d2'")
        conn.commit()
        conn.close()

        res = verify_chain(tmp_ledger)
        assert res.ok is False
        assert res.first_broken_id == "d2"
        assert "row_hash mismatch" in (res.reason or "")

    def test_tampered_prev_hash_detected(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1", created_at="2026-04-21T10:00:00+00:00")
        _insert_row(tmp_ledger, "d2", created_at="2026-04-21T10:01:00+00:00")
        backfill_chain(tmp_ledger)

        # Tamper: rewrite d2's prev_hash to garbage
        conn = sqlite3.connect(str(tmp_ledger))
        conn.execute(
            "UPDATE decisions SET prev_hash=? WHERE decision_id='d2'",
            ("0" * 60 + "beef",),
        )
        conn.commit()
        conn.close()

        res = verify_chain(tmp_ledger)
        assert res.ok is False
        assert res.first_broken_id == "d2"
        assert "prev_hash mismatch" in (res.reason or "")

    def test_unsealed_row_does_not_break_chain(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        """A NULL-hash row is skipped by verify (backfill will seal it later)."""
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1")
        # no backfill — d1 stays unsealed
        res = verify_chain(tmp_ledger)
        assert res.ok is True
        assert res.total_rows == 1
        assert res.verified_rows == 0


# --------------------------------------------------------------------- #
# backfill_chain
# --------------------------------------------------------------------- #


class TestBackfillChain:
    def test_seals_null_hash_rows(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1")
        _insert_row(tmp_ledger, "d2", created_at="2026-04-21T10:01:00+00:00")

        res = backfill_chain(tmp_ledger)
        assert res.ok is True
        assert res.verified_rows == 2

        conn = sqlite3.connect(str(tmp_ledger))
        cur = conn.execute("SELECT decision_id, prev_hash, row_hash FROM decisions ORDER BY decision_id")
        rows = cur.fetchall()
        conn.close()
        assert all(r[1] is not None and r[2] is not None for r in rows)
        assert rows[0][1] == GENESIS_PREV_HASH  # first row points to genesis
        assert rows[1][1] == rows[0][2]  # second row's prev_hash == first's row_hash

    def test_idempotent(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1")
        backfill_chain(tmp_ledger)
        # Snapshot the row_hash after first seal
        conn = sqlite3.connect(str(tmp_ledger))
        h1 = conn.execute("SELECT row_hash FROM decisions WHERE decision_id='d1'").fetchone()[0]
        conn.close()

        # Second call — should not change hashes (it skips already-sealed rows)
        backfill_chain(tmp_ledger)
        conn = sqlite3.connect(str(tmp_ledger))
        h2 = conn.execute("SELECT row_hash FROM decisions WHERE decision_id='d1'").fetchone()[0]
        conn.close()
        assert h1 == h2

    def test_dry_run_does_not_mutate(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1")
        backfill_chain(tmp_ledger, dry_run=True)
        conn = sqlite3.connect(str(tmp_ledger))
        h = conn.execute("SELECT row_hash FROM decisions WHERE decision_id='d1'").fetchone()[0]
        conn.close()
        assert h is None  # not mutated


# --------------------------------------------------------------------- #
# ensure_row_hash
# --------------------------------------------------------------------- #


class TestEnsureRowHash:
    def test_assigns_hash_to_new_row(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1")
        conn = sqlite3.connect(str(tmp_ledger))
        conn.row_factory = sqlite3.Row  # required by ensure_row_hash (matches production)
        new_hash = ensure_row_hash(conn, "d1")
        conn.close()
        assert new_hash is not None
        assert len(new_hash) == 64

    def test_returns_none_for_unknown_row(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        conn = sqlite3.connect(str(tmp_ledger))
        conn.row_factory = sqlite3.Row
        result = ensure_row_hash(conn, "nonexistent_id")
        conn.close()
        assert result is None

    def test_signs_when_key_present(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv(SIGNING_KEY_ENV, "unit-test-key-material-40-bytes-long-abcd")
        _insert_row(tmp_ledger, "d1")
        conn = sqlite3.connect(str(tmp_ledger))
        conn.row_factory = sqlite3.Row
        ensure_row_hash(conn, "d1")
        sig_alg, signature = conn.execute(
            "SELECT sig_alg, signature FROM decisions WHERE decision_id='d1'"
        ).fetchone()
        conn.close()
        assert sig_alg == SIG_ALG_HMAC
        assert signature is not None and len(signature) == 64


# --------------------------------------------------------------------- #
# resign_chain
# --------------------------------------------------------------------- #


class TestResignChain:
    def test_resign_requires_key(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1")
        backfill_chain(tmp_ledger)
        res = resign_chain(tmp_ledger)
        assert res.ok is False
        assert res.reason is not None and "not set" in res.reason

    def test_resign_updates_signatures(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1")
        _insert_row(tmp_ledger, "d2", created_at="2026-04-21T10:01:00+00:00")
        backfill_chain(tmp_ledger)

        monkeypatch.setenv(SIGNING_KEY_ENV, "rotation-test-key-40-bytes-long-material!")
        res = resign_chain(tmp_ledger)
        assert res.ok is True
        assert res.verified_rows == 2

        # Verify all rows now have HMAC sigs
        conn = sqlite3.connect(str(tmp_ledger))
        rows = conn.execute("SELECT sig_alg, signature FROM decisions").fetchall()
        conn.close()
        assert all(r[0] == SIG_ALG_HMAC and r[1] is not None for r in rows)

    def test_resign_then_wrong_key_verify_fails(self, tmp_ledger: Path, monkeypatch: pytest.MonkeyPatch):
        _ensure_clean_env(monkeypatch)
        _insert_row(tmp_ledger, "d1")
        backfill_chain(tmp_ledger)

        monkeypatch.setenv(SIGNING_KEY_ENV, "correct-signing-key-40-bytes-long-material")
        resign_chain(tmp_ledger)
        res_correct = verify_chain(tmp_ledger)
        assert res_correct.ok is True

        monkeypatch.setenv(SIGNING_KEY_ENV, "wrongkey-signing-key-40-bytes-long-material")
        res_wrong = verify_chain(tmp_ledger)
        assert res_wrong.ok is False
        assert "signature mismatch" in (res_wrong.reason or "")
