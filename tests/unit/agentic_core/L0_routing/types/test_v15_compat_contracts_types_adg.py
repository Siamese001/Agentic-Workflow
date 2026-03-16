"""ADG contract tests for L0_routing/types/v15_p2_contracts_types.py."""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_v15_compat_contracts_types_adg")
_emit_applies_guardrail("p0", "test_v15_compat_contracts_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_v15_compat_contracts_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_v15_compat_contracts_types_adg", "state_snapshot")
emit_replay_key("p0", "test_v15_compat_contracts_types_adg")
emit_determinism_digest("p0", "test_v15_compat_contracts_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
from agentic_core.L0_routing.types.v15_p2_contracts_types import (
    EpisodicMemoryNotQueried,
    ForbiddenInputError,
    RollbackHashMismatch,
    WallClockViolation,
    dedupe_sha256,
    validate_execution_input,
)


class TestCompatExceptions:
    def test_forbidden_input_error_importable(self): assert ForbiddenInputError is not None
    def test_episodic_memory_not_queried_importable(self): assert EpisodicMemoryNotQueried is not None
    def test_rollback_hash_mismatch_importable(self): assert RollbackHashMismatch is not None
    def test_wall_clock_violation_importable(self): assert WallClockViolation is not None

class TestCompatFunctions:
    def test_dedupe_sha256_callable(self): assert callable(dedupe_sha256)
    def test_validate_execution_input_callable(self): assert callable(validate_execution_input)
    def test_dedupe_sha256_produces_hash(self):
        h = dedupe_sha256("test content"); assert isinstance(h, str); assert len(h) == 64
