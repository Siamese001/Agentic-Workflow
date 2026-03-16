"""ADG-driven tests for L2_execution/enforcement/capability_revoker.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_capability_revoker_adg")
_emit_applies_guardrail("p0", "test_capability_revoker_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_capability_revoker_adg", "policy_binding")
_emit_snapshots_state("p0", "test_capability_revoker_adg", "state_snapshot")
emit_replay_key("p0", "test_capability_revoker_adg")
emit_determinism_digest("p0", "test_capability_revoker_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.capability_revoker import (
    CapabilityRevoker,
    TokenRevocationError,
    VersionInvalidError,
)


class TestTokenRevocationError:
    def test_is_runtime_error(self):
        assert issubclass(TokenRevocationError, RuntimeError)


class TestVersionInvalidError:
    def test_is_runtime_error(self):
        assert issubclass(VersionInvalidError, RuntimeError)


class TestCapabilityRevoker:
    def test_creates(self):
        revoker = CapabilityRevoker()
        assert revoker is not None
        assert revoker._revoked_trace_ids == set()
        assert revoker._invalid_versions == set()

    def test_has_validate_token(self):
        assert hasattr(CapabilityRevoker, "validate_token")
