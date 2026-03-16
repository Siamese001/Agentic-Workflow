"""ADG-driven tests for L0_routing/legacy_agent_name_allowlist.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_legacy_agent_name_allowlist_adg")
_emit_applies_guardrail("p0", "test_legacy_agent_name_allowlist_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_legacy_agent_name_allowlist_adg", "policy_binding")
_emit_snapshots_state("p0", "test_legacy_agent_name_allowlist_adg", "state_snapshot")
emit_replay_key("p0", "test_legacy_agent_name_allowlist_adg")
emit_determinism_digest("p0", "test_legacy_agent_name_allowlist_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.legacy_agent_name_allowlist import LEGACY_AGENT_NAME_ALLOWLIST


class TestLegacyAgentNameAllowlist:
    def test_is_dict(self):
        assert isinstance(LEGACY_AGENT_NAME_ALLOWLIST, dict)

    def test_non_empty(self):
        assert len(LEGACY_AGENT_NAME_ALLOWLIST) >= 1

    def test_values_are_strings(self):
        for key, val in LEGACY_AGENT_NAME_ALLOWLIST.items():
            assert isinstance(key, str)
            assert isinstance(val, str)

    def test_values_have_justification(self):
        for val in LEGACY_AGENT_NAME_ALLOWLIST.values():
            assert len(val) >= 12, f"Justification too short: {val!r}"
