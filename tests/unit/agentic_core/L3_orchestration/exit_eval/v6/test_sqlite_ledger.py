"""Tests for SqliteLedger durable UWG ledger."""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.v6 import SqliteLedger
from agentic_core.L3_orchestration.exit_eval.v6.uwg import LedgerAppendResult


def test_init_creates_schema(tmp_path: Path) -> None:
    p = tmp_path / "ledger.sqlite"
    ledger = SqliteLedger(p)
    assert p.exists()
    assert ledger.count() == 0
    assert ledger.head_seq() == -1
    assert ledger.head_hash() == ""


def test_invalid_table_name_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="invalid table name"):
        SqliteLedger(tmp_path / "x.sqlite", table="bad-name with spaces")


def test_append_returns_result(tmp_path: Path) -> None:
    ledger = SqliteLedger(tmp_path / "x.sqlite")
    result = ledger.append(commit_request_id="crq-1", payload={"foo": 1})
    assert isinstance(result, LedgerAppendResult)
    assert result.seq == 0
    assert len(result.hash_chain_tip) == 64


def test_append_chains_hashes(tmp_path: Path) -> None:
    ledger = SqliteLedger(tmp_path / "x.sqlite")
    r1 = ledger.append(commit_request_id="crq-1", payload={"a": 1})
    r2 = ledger.append(commit_request_id="crq-2", payload={"a": 2})
    r3 = ledger.append(commit_request_id="crq-3", payload={"a": 3})
    assert r1.seq == 0 and r2.seq == 1 and r3.seq == 2
    assert r1.hash_chain_tip != r2.hash_chain_tip != r3.hash_chain_tip
    assert ledger.head_hash() == r3.hash_chain_tip


def test_append_idempotent_on_collision(tmp_path: Path) -> None:
    ledger = SqliteLedger(tmp_path / "x.sqlite")
    r1 = ledger.append(commit_request_id="crq-1", payload={"v": 1})
    r2 = ledger.append(commit_request_id="crq-1", payload={"v": 2})
    assert r1.seq == r2.seq
    assert r1.hash_chain_tip == r2.hash_chain_tip
    assert ledger.count() == 1


def test_persistence_survives_restart(tmp_path: Path) -> None:
    p = tmp_path / "x.sqlite"
    ledger = SqliteLedger(p)
    ledger.append(commit_request_id="crq-1", payload={"v": 1})
    ledger.append(commit_request_id="crq-2", payload={"v": 2})
    head_before = ledger.head_hash()
    del ledger

    reopened = SqliteLedger(p)
    assert reopened.count() == 2
    assert reopened.head_hash() == head_before
    # Append after restart continues the chain.
    r3 = reopened.append(commit_request_id="crq-3", payload={"v": 3})
    assert r3.seq == 2


def test_get_returns_entry(tmp_path: Path) -> None:
    ledger = SqliteLedger(tmp_path / "x.sqlite")
    ledger.append(commit_request_id="crq-1", payload={"v": 1})
    entry = ledger.get("crq-1")
    assert entry is not None
    assert entry["seq"] == 0
    assert entry["payload"] == {"v": 1}


def test_get_missing_returns_none(tmp_path: Path) -> None:
    ledger = SqliteLedger(tmp_path / "x.sqlite")
    assert ledger.get("nope") is None


def test_entries_returns_all_in_order(tmp_path: Path) -> None:
    ledger = SqliteLedger(tmp_path / "x.sqlite")
    for i in range(5):
        ledger.append(commit_request_id=f"crq-{i}", payload={"v": i})
    entries = ledger.entries()
    assert len(entries) == 5
    assert [e["seq"] for e in entries] == [0, 1, 2, 3, 4]


def test_verify_chain_passes_clean(tmp_path: Path) -> None:
    ledger = SqliteLedger(tmp_path / "x.sqlite")
    for i in range(3):
        ledger.append(commit_request_id=f"crq-{i}", payload={"v": i})
    assert ledger.verify_chain() is True


def test_verify_chain_detects_tampered_hash(tmp_path: Path) -> None:
    p = tmp_path / "x.sqlite"
    ledger = SqliteLedger(p)
    ledger.append(commit_request_id="crq-1", payload={"v": 1})
    ledger.append(commit_request_id="crq-2", payload={"v": 2})
    # Tamper directly via raw SQL.
    import sqlite3

    conn = sqlite3.connect(str(p))
    conn.execute("UPDATE uwg_ledger SET hash = 'tampered' WHERE seq = 1")
    conn.commit()
    conn.close()
    assert ledger.verify_chain() is False


def test_custom_table_name(tmp_path: Path) -> None:
    ledger = SqliteLedger(tmp_path / "x.sqlite", table="my_audit_log")
    ledger.append(commit_request_id="crq-1", payload={"x": 1})
    assert ledger.table == "my_audit_log"
    assert ledger.count() == 1


def test_uwg_backends_accept_sqlite_ledger(tmp_path: Path) -> None:
    """SqliteLedger plugs into UwgBackends without changes."""
    from agentic_core.L3_orchestration.exit_eval.v6.uwg import (
        InMemoryCatalog,
        InMemoryLockStore,
        NoopReadSurfaceRefresher,
        UwgBackends,
    )

    ledger = SqliteLedger(tmp_path / "x.sqlite")
    backends = UwgBackends(
        catalog=InMemoryCatalog(),
        lock_store=InMemoryLockStore(),
        ledger=ledger,
        refresher=NoopReadSurfaceRefresher(),
    )
    # Append directly through the protocol surface.
    result = backends.ledger.append(commit_request_id="crq-pkt", payload={"y": 1})
    assert result.seq == 0
