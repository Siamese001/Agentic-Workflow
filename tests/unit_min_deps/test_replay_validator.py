"""Unit tests for system_learning.validators.replay_validator."""

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.validators.replay_validator import (
    DeterminismViolation,
    replay_validate,
)

_emit_records_execution_trace("p0", "evidence", "test_replay_validator")
_emit_applies_guardrail("p0", "test_replay_validator", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_validator", "policy_binding")
_emit_snapshots_state("p0", "test_replay_validator", "state_snapshot")
emit_replay_key("p0", "test_replay_validator")
emit_determinism_digest("p0", "test_replay_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestReplayValidator:
    def test_deterministic_engine_passes(self):
        """Deterministic engine produces same hash on both runs."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 5}
        hash_result = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        # Should return a valid SHA-256 hex digest
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_nondeterministic_engine_fails(self):
        """Non-deterministic engine raises DeterminismViolation."""
        call_count = 0

        def nondeterministic_engine(snapshot):
            nonlocal call_count
            call_count += 1
            return {"value": snapshot["input"] * call_count}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 5}

        with pytest.raises(DeterminismViolation, match="DETERMINISM_VIOLATION"):
            replay_validate(snapshot, nondeterministic_engine, canonicalize_fn=canonicalize)

    def test_error_includes_both_hashes(self):
        """DeterminismViolation error includes both hashes."""
        call_count = 0

        def nondeterministic_engine(snapshot):
            nonlocal call_count
            call_count += 1
            return {"value": call_count}

        def canonicalize(output):
            return str(output).encode("utf-8")

        snapshot = {"input": 5}

        with pytest.raises(DeterminismViolation) as exc_info:
            replay_validate(snapshot, nondeterministic_engine, canonicalize_fn=canonicalize)

        error_msg = str(exc_info.value)
        assert "Run 1 hash:" in error_msg
        assert "Run 2 hash:" in error_msg

    def test_same_output_twice_produces_same_hash(self):
        """Running replay_validate twice with same engine produces same hash."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 5}

        hash1 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)
        hash2 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 == hash2

    def test_different_snapshots_produce_different_hashes(self):
        """Different snapshots produce different hashes."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot1 = {"input": 5}
        snapshot2 = {"input": 10}

        hash1 = replay_validate(snapshot1, deterministic_engine, canonicalize_fn=canonicalize)
        hash2 = replay_validate(snapshot2, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 != hash2


class TestDeterminism:
    def test_replay_validate_deterministic(self):
        """replay_validate itself is deterministic."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2, "extra": "data"}

        def canonicalize(output):
            # Canonical: sorted items
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 42}

        # Run replay_validate multiple times
        hash1 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)
        hash2 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)
        hash3 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 == hash2 == hash3
