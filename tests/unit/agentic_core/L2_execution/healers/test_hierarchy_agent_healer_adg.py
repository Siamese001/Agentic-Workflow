"""ADG-driven tests for L2 execution hierarchy_agent_healer — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_hierarchy_agent_healer_adg")
_emit_applies_guardrail("p0", "test_hierarchy_agent_healer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_hierarchy_agent_healer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_hierarchy_agent_healer_adg", "state_snapshot")
emit_replay_key("p0", "test_hierarchy_agent_healer_adg")
emit_determinism_digest("p0", "test_hierarchy_agent_healer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.healers.hierarchy_agent_healer import (
    CHECK_ID,
    heal_hierarchy_violations,
)
from agentic_core.L2_execution.types.heal_contract_types import HealCheckResult, HealStatus


class TestHierarchyAgentHealer:
    def test_check_id_string(self):
        assert isinstance(CHECK_ID, str)

    def test_heal_callable(self):
        assert callable(heal_hierarchy_violations)

    def test_no_violations_returns_healed(self):
        result = heal_hierarchy_violations({"violations_count": 0}, apply=False)
        assert isinstance(result, HealCheckResult)
        assert result.status == HealStatus.HEALED

    def test_dry_run_with_violations_returns_result(self):
        result = heal_hierarchy_violations(
            {"violations_count": 2, "territory": "agentic_core"},
            apply=False,
        )
        assert isinstance(result, HealCheckResult)

    def test_check_id_matches(self):
        result = heal_hierarchy_violations({"violations_count": 0})
        assert result.check_id == CHECK_ID
