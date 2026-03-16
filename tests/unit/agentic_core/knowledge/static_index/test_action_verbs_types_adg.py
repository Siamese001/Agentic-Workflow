"""ADG-driven tests for knowledge/static_index/action_verbs_types.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_action_verbs_types_adg")
_emit_applies_guardrail("p0", "test_action_verbs_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_action_verbs_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_action_verbs_types_adg", "state_snapshot")
emit_replay_key("p0", "test_action_verbs_types_adg")
emit_determinism_digest("p0", "test_action_verbs_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.knowledge.static_index.action_verbs_types import ACTION_VERBS


class TestActionVerbs:
    def test_is_dict(self):
        assert isinstance(ACTION_VERBS, dict)

    def test_has_engineering_category(self):
        assert "Engineering" in ACTION_VERBS

    def test_has_leadership_category(self):
        assert "Leadership" in ACTION_VERBS

    def test_has_analysis_category(self):
        assert "Analysis" in ACTION_VERBS

    def test_engineering_is_list(self):
        assert isinstance(ACTION_VERBS["Engineering"], list)

    def test_engineering_nonempty(self):
        assert len(ACTION_VERBS["Engineering"]) > 0

    def test_all_values_are_lists_of_strings(self):
        for category, verbs in ACTION_VERBS.items():
            assert isinstance(verbs, list), f"{category} should be a list"
            for v in verbs:
                assert isinstance(v, str), f"{v} in {category} should be str"
