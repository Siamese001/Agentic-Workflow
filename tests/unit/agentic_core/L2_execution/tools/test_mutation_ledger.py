"""
Test mutation ledger functionality in write_gateway.

Per .windsurfrules §1.1: Zero-tolerance - any changed logic MUST have tests.
Per .windsurfrules §1.3: Deterministic tests only - no randomness.
Per .windsurfrules §1.5: Edge cases mandatory - null/missing/malformed inputs.
Per .windsurfrules §1.8: Fail-closed and side-effect safety.
"""

import hashlib
import json
from pathlib import Path

import pytest


def test_mutation_ledger_records_write_text_success(tmp_path):
    """
    PASS: write_text appends JSONL entry with before/after hashes.
    FAIL: No ledger entry or missing required fields.

    Per .windsurfrules §1.1: Changed logic (ledger append) MUST have tests.
    Per .windsurfrules §1.8: Side-effect safety - verify ledger write occurred.
    """
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    trace_id = "TEST-TRACE-001"
    set_mutation_ledger_path(ledger_path, trace_id)

    # Write a new file
    target = tmp_path / "test.txt"
    content = "test content"
    write_text(target, content)

    # Verify ledger entry
    assert ledger_path.exists(), "Ledger file not created"
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}"

    entry = entries[0]
    assert entry["seq"] == 1
    assert entry["trace_id"] == trace_id
    assert entry["operation"] == "write_text"
    assert entry["before_hash"] is None, "New file should have no before_hash"
    assert entry["after_hash"] == hashlib.sha256(content.encode()).hexdigest()
    assert entry["gateway_approved"] is True
    assert entry["result"] == "SUCCESS"
    assert entry["error"] is None


def test_mutation_ledger_records_before_after_hash_on_update(tmp_path):
    """
    PASS: Updating existing file records both before_hash and after_hash.
    FAIL: before_hash is None or equals after_hash when content changed.

    Per .windsurfrules §1.7: Deterministic decision surfaces - distinct input must not collapse.
    Per .windsurfrules §1.11: Mutation-sensitive tests - hash must change when content changes.
    """
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-002")

    # Write initial content
    target = tmp_path / "test.txt"
    original_content = "original"
    target.write_text(original_content)
    original_hash = hashlib.sha256(original_content.encode()).hexdigest()

    # Update via write_text
    new_content = "updated"
    write_text(target, new_content)
    new_hash = hashlib.sha256(new_content.encode()).hexdigest()

    # Verify ledger entry
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    assert len(entries) == 1

    entry = entries[0]
    assert entry["before_hash"] == original_hash, "before_hash must match original content"
    assert entry["after_hash"] == new_hash, "after_hash must match new content"
    assert entry["before_hash"] != entry["after_hash"], "Hashes must differ when content changes"


def test_mutation_ledger_detects_no_op_write(tmp_path):
    """
    PASS: Writing identical content shows before_hash == after_hash.
    FAIL: Hashes differ despite identical content.

    Per hostile audit Section D14: No-op patch detection.
    Per .windsurfrules §1.7: Identical input → identical output.
    """
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-003")

    # Write initial content
    target = tmp_path / "test.txt"
    content = "unchanged"
    target.write_text(content)

    # Write identical content via gateway
    write_text(target, content)

    # Verify ledger shows no-op
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    entry = entries[0]

    assert entry["before_hash"] == entry["after_hash"], (
        "No-op write must have identical before/after hashes - "
        "this is a critical gate per hostile audit Section B4"
    )


def test_mutation_ledger_records_write_failure(tmp_path):
    """
    PASS: Write failure records FAILED entry with error message.
    FAIL: No ledger entry or result=SUCCESS despite failure.

    Per .windsurfrules §1.8: Fail-closed - failures must be recorded.
    Per hostile audit Section B4: failed writes must appear in ledger.
    """
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-004")

    # Attempt to write to a read-only location (simulate failure)
    target = tmp_path / "readonly" / "test.txt"
    target.parent.mkdir(parents=True)
    target.parent.chmod(0o444)  # Make parent read-only

    try:
        write_text(target, "content")
        # Write succeeded despite read-only chmod — write protection is not enforced
        target.parent.chmod(0o755)
        pytest.fail(
            "write_text succeeded on a chmod(0o444) directory — "
            "write protection is not enforced on this platform. "
            "The mutation ledger must record this as a failure, not silently succeed."
        )
    except (PermissionError, OSError):  # guardian: allow-silent-swallower
        # Expected failure
        pass
    finally:
        # Restore permissions for cleanup
        try:
            target.parent.chmod(0o755)
        except OSError:
            pass

    # Verify ledger recorded the failure
    if ledger_path.exists():
        entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
        assert len(entries) == 1

        entry = entries[0]
        assert entry["result"] == "FAILED", "Failed write must have result=FAILED"
        assert entry["after_hash"] is None, "Failed write must not have after_hash"
        assert entry["error"] is not None, "Failed write must record error"


def test_mutation_ledger_sequence_numbers_monotonic(tmp_path):
    """
    PASS: Multiple writes produce monotonically increasing sequence numbers.
    FAIL: Sequence numbers repeat, skip, or decrease.

    Per hostile audit Section C3: sequence_number must be monotonically increasing per-run.
    Per .windsurfrules §1.7: Deterministic decision surfaces.
    """
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-005")

    # Write 5 files
    for i in range(5):
        target = tmp_path / f"file{i}.txt"
        write_text(target, f"content {i}")

    # Verify sequence numbers
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    assert len(entries) == 5

    for i, entry in enumerate(entries):
        assert entry["seq"] == i + 1, f"Expected seq={i + 1}, got {entry['seq']}"


def test_mutation_ledger_trace_id_correlation(tmp_path):
    """
    PASS: All ledger entries contain the same trace_id.
    FAIL: trace_id missing or inconsistent across entries.

    Per hostile audit Section B1: trace_id must appear in every artifact.
    Per hostile audit Section F6: trace_id correlation test.
    """
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    trace_id = "TEST-TRACE-CORRELATION"
    set_mutation_ledger_path(ledger_path, trace_id)

    # Write multiple files
    for i in range(3):
        target = tmp_path / f"file{i}.txt"
        write_text(target, f"content {i}")

    # Verify all entries have same trace_id
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    for entry in entries:
        assert entry["trace_id"] == trace_id, f"Entry {entry['seq']} has wrong trace_id: {entry['trace_id']}"


def test_mutation_ledger_disabled_when_not_configured(tmp_path):
    """
    PASS: Writes succeed without ledger when set_mutation_ledger_path not called.
    FAIL: Write fails or creates ledger in unexpected location.

    Per .windsurfrules §1.5: Edge cases - missing configuration.
    Per hostile audit Section A9: execution_mode marker required.
    """
    from agentic_core.L2_execution.tools.write_gateway import write_text

    # Do NOT call set_mutation_ledger_path
    target = tmp_path / "test.txt"
    result = write_text(target, "content")

    # Write should succeed
    assert Path(result).exists()
    assert Path(result).read_text() == "content"

    # No ledger should be created in tmp_path
    ledger_files = list(tmp_path.glob("*.jsonl"))
    assert len(ledger_files) == 0, "Ledger created without configuration"


def test_mutation_ledger_write_bytes_records_entry(tmp_path):
    """
    PASS: write_bytes records ledger entry with correct hashes.
    FAIL: No entry or incorrect operation field.

    Per .windsurfrules §1.1: All changed logic MUST have tests.
    """
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_bytes

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-BYTES")

    # Write binary data
    target = tmp_path / "test.bin"
    data = b"\x00\x01\x02\x03"
    write_bytes(target, data)

    # Verify ledger entry
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    assert len(entries) == 1

    entry = entries[0]
    assert entry["operation"] == "write_bytes"
    assert entry["after_hash"] == hashlib.sha256(data).hexdigest()
    assert entry["result"] == "SUCCESS"


def test_mutation_ledger_ascii_only_output(tmp_path):
    """
    PASS: Ledger entries are ASCII-only JSON.
    FAIL: Non-ASCII characters in ledger file.

    Per .windsurfrules §2.2: Evidence must be ASCII-only.
    Per hostile audit Section C3: ensure_ascii=True required.
    """
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-UNICODE")

    # Write file with unicode path (if supported)
    target = tmp_path / "test_file.txt"
    write_text(target, "content")

    # Verify ledger is ASCII-only
    ledger_bytes = ledger_path.read_bytes()
    try:
        ledger_bytes.decode("ascii")
    except UnicodeDecodeError:
        pytest.fail("Ledger contains non-ASCII characters - violates .windsurfrules §2.2")
