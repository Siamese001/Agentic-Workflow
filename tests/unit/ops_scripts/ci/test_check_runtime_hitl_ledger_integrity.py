"""Tests for ops_scripts/ci/check_runtime_hitl_ledger_integrity.py (W7)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_control.ledger_integrity import (
    AuditChain,
    AuditEventType,
)
from ops_scripts.ci.check_runtime_hitl_ledger_integrity import main


def _populate_clean_chain(path: Path) -> None:
    chain = AuditChain(path, now=lambda: 100.0)
    for i in range(3):
        chain.append(
            ledger_id=f"l{i}",
            run_id="r",
            event_type=AuditEventType.CREATED,
            payload={"i": i},
            event_ts=100.0 + i,
        )
    chain.close()


def _tamper(path: Path, *, audit_id: int, new_payload: str) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            "UPDATE hitl_audit_chain SET payload_json = ? WHERE audit_id = ?",
            (new_payload, audit_id),
        )
        conn.commit()
    finally:
        conn.close()


class TestCliExitCodes:
    def test_clean_chain_exits_zero(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        db = tmp_path / "audit.db"
        _populate_clean_chain(db)
        rc = main(["--audit-db", str(db)])
        assert rc == 0
        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload["ok"] is True
        assert payload["total_events"] == 3
        assert payload["verified_events"] == 3
        assert payload["violations"] == []

    def test_tampered_chain_exits_one(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        db = tmp_path / "audit.db"
        _populate_clean_chain(db)
        _tamper(db, audit_id=2, new_payload='{"i": 999}')
        rc = main(["--audit-db", str(db)])
        assert rc == 1
        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload["ok"] is False
        assert any(v["reason"] == "entry_hash_mismatch" for v in payload["violations"])

    def test_missing_db_exits_two(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        rc = main(["--audit-db", str(tmp_path / "nope.db")])
        assert rc == 2
        err = capsys.readouterr().err
        assert "audit-db not found" in err

    def test_empty_chain_exits_zero(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        # Create an empty but initialized chain (no rows)
        AuditChain(tmp_path / "audit.db").close()
        rc = main(["--audit-db", str(tmp_path / "audit.db")])
        assert rc == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["total_events"] == 0


class TestRequireSignaturesFlag:
    def test_require_signatures_fails_when_unsigned(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        db = tmp_path / "audit.db"
        _populate_clean_chain(db)  # unsigned
        rc = main(["--audit-db", str(db), "--require-signatures"])
        assert rc == 1
        err = capsys.readouterr().err
        assert "require-signatures" in err or "unsigned" in err


class TestInvalidPublicKey:
    def test_bad_hex_exits_two(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        db = tmp_path / "audit.db"
        _populate_clean_chain(db)
        with pytest.raises(SystemExit) as excinfo:
            main(["--audit-db", str(db), "--public-key", "not-hex-!!!"])
        assert excinfo.value.code == 2
        err = capsys.readouterr().err
        assert "not hex-decodable" in err or "not hex" in err

    def test_public_key_file_not_found_exits_two(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        db = tmp_path / "audit.db"
        _populate_clean_chain(db)
        with pytest.raises(SystemExit) as excinfo:
            main(["--audit-db", str(db), "--public-key-file", str(tmp_path / "nope.txt")])
        assert excinfo.value.code == 2
        err = capsys.readouterr().err
        assert "public-key-file not found" in err
