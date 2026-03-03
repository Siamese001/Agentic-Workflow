"""Tests for L4A/B/C sub-layer separation contracts.

Phase 7: L4A/B/C state separation.
Spec: L4 State Layer sub-layer architecture.
"""

from __future__ import annotations

from typing import Any

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L4_state.types.l4_sublayer_contracts import (
    L4AReadOnlyStore,
    L4BEntry,
    L4BSessionMemory,
    L4CLedgerEntry,
    L4CPersistentLedger,
    L4SubLayer,
    SubLayerViolation,
    assert_sublayer,
)

# ---------------------------------------------------------------------------
# Concrete minimal implementations for testing
# ---------------------------------------------------------------------------


class _FakeL4AStore(L4AReadOnlyStore):
    def __init__(self, data: dict):
        self._data = data

    def query(self, key: str, **kwargs: Any) -> Any:
        return self._data.get(key)


class _FakeL4BMemory(L4BSessionMemory):
    def __init__(self):
        self._store: dict[tuple[str, str], Any] = {}

    def put(self, entry: L4BEntry) -> None:
        self._store[(entry.key, entry.session_id)] = entry.value

    def get(self, key: str, session_id: str) -> Any:
        return self._store.get((key, session_id))

    def clear_session(self, session_id: str) -> None:
        keys = [k for k in self._store if k[1] == session_id]
        for k in keys:
            del self._store[k]


class _FakeL4CLedger(L4CPersistentLedger):
    def __init__(self):
        self._committed: list[L4CLedgerEntry] = []
        self._data: dict[str, Any] = {}

    def commit(self, entry: L4CLedgerEntry) -> None:
        self._committed.append(entry)
        if entry.operation == "write":
            self._data[entry.key] = entry.value
        elif entry.operation == "delete":
            self._data.pop(entry.key, None)

    def read(self, key: str) -> Any:
        return self._data.get(key)


# ---------------------------------------------------------------------------
# L4SubLayer enum
# ---------------------------------------------------------------------------


class TestL4SubLayerEnum:
    def test_all_three_sublayers_defined(self):
        assert L4SubLayer.L4A.value == "L4A"
        assert L4SubLayer.L4B.value == "L4B"
        assert L4SubLayer.L4C.value == "L4C"


# ---------------------------------------------------------------------------
# L4A tests
# ---------------------------------------------------------------------------


class TestL4AReadOnlyStore:
    def test_sublayer_is_l4a(self):
        store = _FakeL4AStore({"x": 1})
        assert store.sublayer == L4SubLayer.L4A

    def test_query_returns_value(self):
        store = _FakeL4AStore({"key": "value"})
        assert store.query("key") == "value"

    def test_query_returns_none_for_missing(self):
        store = _FakeL4AStore({})
        assert store.query("missing") is None

    def test_assert_no_write_raises_sublayer_violation(self):
        store = _FakeL4AStore({})
        with pytest.raises(SubLayerViolation, match="read-only"):
            store._assert_no_write("write_text")


# ---------------------------------------------------------------------------
# L4B tests
# ---------------------------------------------------------------------------


class TestL4BEntry:
    def test_valid_entry(self):
        entry = L4BEntry(key="thought_1", value="some content", session_id="sess-001")
        assert entry.key == "thought_1"
        assert entry.session_id == "sess-001"

    def test_empty_key_raises(self):
        with pytest.raises(SubLayerViolation, match="key must be non-empty"):
            L4BEntry(key="", value="x", session_id="s1")

    def test_empty_session_id_raises(self):
        with pytest.raises(SubLayerViolation, match="session_id must be non-empty"):
            L4BEntry(key="k", value="x", session_id="")


class TestL4BSessionMemory:
    def test_sublayer_is_l4b(self):
        mem = _FakeL4BMemory()
        assert mem.sublayer == L4SubLayer.L4B

    def test_put_and_get(self):
        mem = _FakeL4BMemory()
        entry = L4BEntry(key="reasoning_step", value="step1", session_id="sess-001")
        mem.put(entry)
        assert mem.get("reasoning_step", "sess-001") == "step1"

    def test_get_missing_returns_none(self):
        mem = _FakeL4BMemory()
        assert mem.get("no_key", "no_session") is None

    def test_clear_session_removes_entries(self):
        mem = _FakeL4BMemory()
        mem.put(L4BEntry(key="k1", value="v1", session_id="s1"))
        mem.put(L4BEntry(key="k2", value="v2", session_id="s1"))
        mem.put(L4BEntry(key="k3", value="v3", session_id="s2"))
        mem.clear_session("s1")
        assert mem.get("k1", "s1") is None
        assert mem.get("k2", "s1") is None
        assert mem.get("k3", "s2") == "v3"

    def test_assert_not_persistent_raises(self):
        mem = _FakeL4BMemory()
        with pytest.raises(SubLayerViolation, match="session-scoped only"):
            mem._assert_not_persistent_write("write_json")


# ---------------------------------------------------------------------------
# L4C tests
# ---------------------------------------------------------------------------


class TestL4CLedgerEntry:
    def test_valid_write_entry(self):
        e = L4CLedgerEntry(correlation_id="corr-001", key="config.x", value=42, operation="write")
        assert e.operation == "write"

    def test_valid_delete_entry(self):
        e = L4CLedgerEntry(correlation_id="corr-002", key="config.x", value=None, operation="delete")
        assert e.operation == "delete"

    def test_invalid_operation_raises(self):
        with pytest.raises(SubLayerViolation, match="operation must be"):
            L4CLedgerEntry(correlation_id="c1", key="k", value=None, operation="mutate")

    def test_empty_correlation_id_raises(self):
        with pytest.raises(SubLayerViolation, match="correlation_id must be non-empty"):
            L4CLedgerEntry(correlation_id="", key="k", value=None, operation="write")

    def test_empty_key_raises(self):
        with pytest.raises(SubLayerViolation, match="key must be non-empty"):
            L4CLedgerEntry(correlation_id="c1", key="", value=None, operation="write")


class TestL4CPersistentLedger:
    def test_sublayer_is_l4c(self):
        ledger = _FakeL4CLedger()
        assert ledger.sublayer == L4SubLayer.L4C

    def test_commit_and_read(self):
        ledger = _FakeL4CLedger()
        ledger.commit(L4CLedgerEntry(correlation_id="c1", key="settings.x", value=99, operation="write"))
        assert ledger.read("settings.x") == 99

    def test_delete_removes_key(self):
        ledger = _FakeL4CLedger()
        ledger.commit(L4CLedgerEntry(correlation_id="c1", key="k", value="v", operation="write"))
        ledger.commit(L4CLedgerEntry(correlation_id="c2", key="k", value=None, operation="delete"))
        assert ledger.read("k") is None

    def test_multiple_commits_preserved_in_order(self):
        ledger = _FakeL4CLedger()
        ledger.commit(L4CLedgerEntry(correlation_id="c1", key="a", value=1, operation="write"))
        ledger.commit(L4CLedgerEntry(correlation_id="c2", key="b", value=2, operation="write"))
        assert len(ledger._committed) == 2
        assert ledger._committed[0].correlation_id == "c1"


# ---------------------------------------------------------------------------
# assert_sublayer boundary enforcement
# ---------------------------------------------------------------------------


class TestAssertSublayer:
    def test_correct_sublayer_passes(self):
        store = _FakeL4AStore({})
        assert_sublayer(store, L4SubLayer.L4A)  # Should not raise

    def test_wrong_sublayer_raises(self):
        store = _FakeL4AStore({})
        with pytest.raises(SubLayerViolation, match="Sub-layer mismatch"):
            assert_sublayer(store, L4SubLayer.L4B)

    def test_l4b_correct_sublayer_passes(self):
        mem = _FakeL4BMemory()
        assert_sublayer(mem, L4SubLayer.L4B)

    def test_l4c_correct_sublayer_passes(self):
        ledger = _FakeL4CLedger()
        assert_sublayer(ledger, L4SubLayer.L4C)

    def test_no_sublayer_attr_raises(self):
        class NoSublayer:
            pass

        with pytest.raises(SubLayerViolation, match="Sub-layer mismatch"):
            assert_sublayer(NoSublayer(), L4SubLayer.L4A)
