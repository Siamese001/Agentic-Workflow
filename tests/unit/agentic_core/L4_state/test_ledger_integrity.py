"""Addendum 2.2: Ledger Integrity Validator tests."""

from __future__ import annotations

import pytest

from agentic_core.L4_state.ledger.integrity_validator import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    append_with_hash,
    validate_ledger_chain,
    validate_ledger_file,
)
from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation


class TestAppendWithHash:
    def test_appended_entry_has_hash(self):
        entries: list = []
        entry = append_with_hash(entries, {"op": "write", "file": "foo.py"})
        assert "_hash" in entry
        assert len(entry["_hash"]) == 64

    def test_chain_grows(self):
        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "a.py"})
        append_with_hash(entries, {"op": "delete", "file": "b.py"})
        assert len(entries) == 2

    def test_hashes_are_different_per_entry(self):
        entries: list = []
        e1 = append_with_hash(entries, {"op": "write", "file": "a.py"})
        e2 = append_with_hash(entries, {"op": "write", "file": "b.py"})
        assert e1["_hash"] != e2["_hash"]


class TestValidateLedgerChain:
    def test_valid_chain_passes(self):
        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "a.py"})
        append_with_hash(entries, {"op": "write", "file": "b.py"})
        validate_ledger_chain(entries)

    def test_empty_chain_passes(self):
        validate_ledger_chain([])

    def test_tampered_hash_raises(self):
        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "a.py"})
        entries[0]["_hash"] = "0" * 64
        with pytest.raises(LedgerIntegrityViolation, match="hash mismatch"):
            validate_ledger_chain(entries)

    def test_missing_hash_field_raises(self):
        entries = [{"op": "write", "file": "a.py"}]
        with pytest.raises(LedgerIntegrityViolation, match="missing '_hash'"):
            validate_ledger_chain(entries)

    def test_middle_tamper_detected(self):
        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "a.py"})
        append_with_hash(entries, {"op": "write", "file": "b.py"})
        append_with_hash(entries, {"op": "write", "file": "c.py"})
        entries[1]["_hash"] = "deadbeef" * 8
        with pytest.raises(LedgerIntegrityViolation):
            validate_ledger_chain(entries)

    def test_negative_untampered_chain_never_raises(self):
        entries: list = []
        for i in range(5):
            append_with_hash(entries, {"op": "write", "file": f"f{i}.py"})
        raised = False
        try:
            validate_ledger_chain(entries)
        except LedgerIntegrityViolation:  # guardian: allow-silent-swallower
            raised = True
        assert not raised


class TestValidateLedgerFile:
    def test_valid_file_passes(self, tmp_path):
        import json

        ledger_path = tmp_path / "ledger.jsonl"
        entries: list = []
        for i in range(3):
            append_with_hash(entries, {"op": "write", "file": f"f{i}.py"})
        with open(ledger_path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        validate_ledger_file(ledger_path)

    def test_nonexistent_file_passes_silently(self, tmp_path):
        validate_ledger_file(tmp_path / "nonexistent.jsonl")
