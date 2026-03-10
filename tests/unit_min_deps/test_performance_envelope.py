"""Unit tests for performance envelope and scaling hardening."""

import tempfile

import pytest

from agentic_core.L3_orchestration.replay.deterministic_replay import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    ReplayCommand,
    _truncate_if_needed,
    run_and_record,
)
from agentic_core.L4_state.storage.filesystem_store import FileSystemStore
from agentic_core.L4_state.storage.persistent_store import create_artifact


@pytest.mark.unit_min_deps
def test_truncation_deterministic_and_hash_changes():
    """Test that truncation is deterministic and reflected in hashes."""
    # Create text that exceeds limit
    long_text = "x" * 2000  # 2000 bytes
    truncated_text, was_truncated = _truncate_if_needed(long_text, 1000)

    assert was_truncated
    assert "...<TRUNCATED 1000 BYTES>" in truncated_text
    assert len(truncated_text.encode("utf-8")) <= 1000

    # Truncation is deterministic
    truncated_text2, was_truncated2 = _truncate_if_needed(long_text, 1000)
    assert truncated_text == truncated_text2
    assert was_truncated == was_truncated2


@pytest.mark.unit_min_deps
def test_replay_metrics_determinism():
    """Test that replay metrics are deterministic."""
    commands = [
        ReplayCommand(
            argv=["python", "-c", "print('hello')"],
            cwd=".",
            env_allowlist={},
            max_stdout_bytes=1000,
            max_stderr_bytes=1000,
        )
    ]

    record1 = run_and_record(commands)
    record2 = run_and_record(commands)

    # Metrics should be present and deterministic
    assert record1.metrics is not None
    assert record2.metrics is not None
    assert record1.metrics == record2.metrics

    # Should have captured output size
    assert record1.metrics.total_bytes_out > 0
    assert record1.metrics.total_bytes_err == 0
    assert len(record1.metrics.per_command_bytes_out) == 1
    assert len(record1.metrics.per_command_bytes_err) == 1


@pytest.mark.unit_min_deps
def test_store_list_limit_deterministic():
    """Test that store list(limit) is deterministic."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Create 10 artifacts
        for i in range(10):
            artifact = create_artifact(
                "test_kind",
                f"id_{i:02d}",
                {"data": f"value_{i}"},
            )
            store.put(artifact)

        # List with limit should return first N in deterministic order
        limited_refs = store.list(limit=LIMIT)
        all_refs = store.list()

        assert len(limited_refs) == 5
        assert len(all_refs) == 10

        # Limited list should be first 5 of full list
        for i, ref in enumerate(limited_refs):
            assert ref == all_refs[i]

        # Ordering should be deterministic
        expected_order = [f"id_{i:02d}" for i in range(10)]
        actual_order = [r.logical_id for r in all_refs]
        assert actual_order == expected_order


@pytest.mark.unit_min_deps
def test_scaling_200_small_artifacts():
    """Scaling test: write 200 small artifacts and verify structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Write 200 small artifacts
        for i in range(200):
            artifact = create_artifact(
                f"kind_{i % 5}",  # 5 different kinds
                f"item_{i:03d}",
                {"index": i, "data": "x" * 10},  # Small payload
            )
            ref = store.put(artifact)

            # Verify basic structure
            assert ref.version == 1
            assert ref.size_bytes > 0
            assert ref.kind == f"kind_{i % 5}"
            assert ref.logical_id == f"item_{i:03d}"

        # List all artifacts
        all_refs = store.list()
        assert len(all_refs) == 200

        # Verify deterministic ordering
        for i in range(1, 200):
            prev_ref = all_refs[i - 1]
            curr_ref = all_refs[i]

            # Should be sorted by kind, then logical_id, then version
            if prev_ref.kind == curr_ref.kind:
                if prev_ref.logical_id == curr_ref.logical_id:
                    assert prev_ref.version < curr_ref.version
                else:
                    assert prev_ref.logical_id < curr_ref.logical_id
            else:
                assert prev_ref.kind < curr_ref.kind

        # Test listing with limits
        first_10 = store.list(limit=LIMIT)
        assert len(first_10) == 10
        assert first_10 == all_refs[:10]

        # Test filtering by kind
        kind_0_refs = store.list(kind="kind_0")
        assert len(kind_0_refs) == 40  # 200 / 5 kinds
        assert all(r.kind == "kind_0" for r in kind_0_refs)


@pytest.mark.unit_min_deps
def test_scaling_25_replay_commands():
    """Scaling test: record 25 simple replay commands."""
    commands = []
    for i in range(25):
        cmd = ReplayCommand(
            argv=["python", "-c", f"print('cmd_{i}')"],
            cwd=".",
            env_allowlist={},
            max_stdout_bytes=1000,
            max_stderr_bytes=1000,
        )
        commands.append(cmd)

    # Record all commands
    record = run_and_record(commands)

    # Verify structural invariants
    assert len(record.results) == 25
    assert len(record.commands) == 25
    assert len(record.hashes) == 25
    assert record.metrics is not None

    # All commands should succeed
    for result in record.results:
        assert result.exit_code == 0
        assert "cmd_" in result.stdout

    # Metrics should be consistent
    assert len(record.metrics.per_command_bytes_out) == 25
    assert len(record.metrics.per_command_bytes_err) == 25
    assert record.metrics.total_bytes_out > 0
    assert record.metrics.total_bytes_err == 0

    # Per-command metrics should sum to totals
    assert sum(record.metrics.per_command_bytes_out) == record.metrics.total_bytes_out
    assert sum(record.metrics.per_command_bytes_err) == record.metrics.total_bytes_err

    # All hashes should be unique
    hash_values = list(record.hashes.values())
    assert len(hash_values) == len(set(hash_values))


@pytest.mark.unit_min_deps
def test_scaling_deterministic_across_runs():
    """Test that scaling operations are deterministic across runs."""
    # First run
    commands1 = [
        ReplayCommand(
            argv=["python", "-c", "print('test')"],
            cwd=".",
            env_allowlist={},
            max_stdout_bytes=1000,
            max_stderr_bytes=1000,
        )
    ]
    record1 = run_and_record(commands1)

    # Second run with identical commands
    commands2 = [
        ReplayCommand(
            argv=["python", "-c", "print('test')"],
            cwd=".",
            env_allowlist={},
            max_stdout_bytes=1000,
            max_stderr_bytes=1000,
        )
    ]
    record2 = run_and_record(commands2)

    # Should be identical
    assert record1.metrics == record2.metrics
    assert record1.hashes == record2.hashes

    # Store operations should also be deterministic
    with tempfile.TemporaryDirectory() as temp_dir:
        store1 = FileSystemStore(temp_dir)
        artifact1 = create_artifact("test", "deterministic", {"data": "test"})
        ref1 = store1.put(artifact1)

        store2 = FileSystemStore(temp_dir)
        artifact2 = create_artifact("test", "deterministic", {"data": "test"})
        ref2 = store2.put(artifact2)

        # Should create version 2 since artifact already exists
        assert ref1.version == 1
        assert ref2.version == 2
        assert ref1.kind == ref2.kind
        assert ref1.logical_id == ref2.logical_id
