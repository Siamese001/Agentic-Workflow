"""Unit tests for deterministic replay engine."""

import pytest

from agentic_core.L3_orchestration.replay.deterministic_replay import (
    ReplayCommand,
    ReplayRecord,
    record_from_json,
    record_to_json,
    replay_and_compare,
    run_and_record,
)


@pytest.mark.unit_min_deps
def test_deterministic_json_output():
    """Test that JSON serialization is deterministic byte-for-byte."""
    # Create identical records
    record1 = ReplayRecord(
        commands=[
            ReplayCommand(
                argv=["python", "-c", "print('x')"],
                cwd="/test",
                env_allowlist={"PATH": "/bin"},
                timeout_s=60,
            )
        ],
        results=[ReplayResult(exit_code=0, stdout="x\n", stderr="")],
        hashes={"cmd_1": "hash123"},
    )

    record2 = ReplayRecord(
        commands=[
            ReplayCommand(
                argv=["python", "-c", "print('x')"],
                cwd="/test",
                env_allowlist={"PATH": "/bin"},
                timeout_s=60,
            )
        ],
        results=[ReplayResult(exit_code=0, stdout="x\n", stderr="")],
        hashes={"cmd_1": "hash123"},
    )

    # Serialize both
    json1 = record_to_json(record1)
    json2 = record_to_json(record2)

    # Should be byte-for-byte identical
    assert json1 == json2

    # Should deserialize to equivalent objects
    parsed1 = record_from_json(json1)
    parsed2 = record_from_json(json2)

    assert parsed1.commands[0].argv == parsed2.commands[0].argv
    assert parsed1.results[0].stdout == parsed2.results[0].stdout


@pytest.mark.unit_min_deps
def test_sha256_stable_and_correct():
    """Test that command hashes are stable and correct."""
    # Create a command and result
    command = ReplayCommand(
        argv=["python", "-c", "print('test')"],
        cwd="/test",
        env_allowlist={"PATH": "/bin"},
        timeout_s=60,
    )

    result = ReplayResult(exit_code=0, stdout="test\n", stderr="")

    # Compute hash twice
    from agentic_core.L3_orchestration.replay.deterministic_replay import _hash_command_result

    hash1 = _hash_command_result(command, result)
    hash2 = _hash_command_result(command, result)

    # Should be identical
    assert hash1 == hash2

    # Should be valid SHA256 (64 hex chars)
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)

    # Different content should produce different hash
    result2 = ReplayResult(exit_code=0, stdout="different\n", stderr="")
    hash3 = _hash_command_result(command, result2)
    assert hash1 != hash3


@pytest.mark.unit_min_deps
def test_env_redaction_works():
    """Test that non-allowlisted environment variables are not recorded."""
    # Set a non-allowlisted env var
    import os

    os.environ["SECRET_SHOULD_NOT_BE_RECORDED"] = "secret_value"

    try:
        # Record a command
        commands = [
            ReplayCommand(
                argv=["python", "-c", "print('test')"],
                cwd=".",
                env_allowlist={"TEST_VAR": "test_value"},
                timeout_s=60,
            )
        ]

        record = run_and_record(commands)

        # Check that only allowlisted vars are in the command
        env_in_record = record.commands[0].env_allowlist
        assert "SECRET_SHOULD_NOT_BE_RECORDED" not in env_in_record
        assert "TEST_VAR" in env_in_record
        assert env_in_record["TEST_VAR"] == "test_value"

    finally:
        # Clean up
        os.environ.pop("SECRET_SHOULD_NOT_BE_RECORDED", None)


@pytest.mark.unit_min_deps
def test_rejects_pwsh_argv0():
    """Test that pwsh/powershell in argv0 raises RuntimeError."""
    commands = [
        ReplayCommand(
            argv=["pwsh", "-c", "echo test"],
            cwd=".",
            env_allowlist={},
            timeout_s=60,
        )
    ]

    with pytest.raises(RuntimeError, match="PowerShell usage forbidden"):
        run_and_record(commands)

    # Test powershell.exe variant
    commands2 = [
        ReplayCommand(
            argv=["powershell.exe", "-c", "echo test"],
            cwd=".",
            env_allowlist={},
            timeout_s=60,
        )
    ]

    with pytest.raises(RuntimeError, match="PowerShell usage forbidden"):
        run_and_record(commands2)


@pytest.mark.unit_min_deps
def test_replay_match_deterministic_command():
    """Test replay matches for deterministic command."""
    # Record a deterministic command
    commands = [
        ReplayCommand(
            argv=["python", "-c", "print('x')"],
            cwd=".",
            env_allowlist={},
            timeout_s=60,
        )
    ]

    record = run_and_record(commands)

    # Replay should match
    result = replay_and_compare(record)
    assert result.is_match
    assert len(result.mismatches) == 0


@pytest.mark.unit_min_deps
def test_replay_detects_nondeterminism():
    """Test replay detects non-deterministic command."""
    # Record a non-deterministic command (time-based output)
    commands = [
        ReplayCommand(
            argv=["python", "-c", "import time; print(time.time())"],
            cwd=".",
            env_allowlist={},
            timeout_s=60,
        )
    ]

    record = run_and_record(commands)

    # Replay should detect mismatch
    result = replay_and_compare(record)
    assert not result.is_match
    assert len(result.mismatches) > 0
    assert "Stdout mismatch after normalization" in str(result.mismatches)


@pytest.mark.unit_min_deps
def test_normalize_output_strips_timestamps_and_paths():
    """Test output normalization strips timestamps and absolute paths."""
    from agentic_core.L3_orchestration.replay.deterministic_replay import _normalize_output

    # Test timestamp normalization
    input_with_timestamp = "2026-02-23T04:18:00.123Z INFO: Test message"
    normalized = _normalize_output(input_with_timestamp)
    assert "<TIMESTAMP> INFO: Test message" == normalized

    # Test path normalization
    import os

    repo_root = os.path.abspath(".")
    input_with_path = f"Processing file {repo_root}/test.py"
    normalized = _normalize_output(input_with_path)
    assert "Processing file <REPO_ROOT>/test.py" == normalized

    # Test Windows drive letter normalization
    input_with_drive = "C:/Users/test/file.py processed"
    normalized = _normalize_output(input_with_drive)
    assert "<ABSOLUTE_PATH> processed" == normalized
