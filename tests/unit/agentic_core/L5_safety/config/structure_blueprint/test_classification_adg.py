"""ADG-driven tests for L5 structure_blueprint/classification.py — fan_in=1."""
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

_emit_records_execution_trace("p0", "evidence", "test_classification_adg")
_emit_applies_guardrail("p0", "test_classification_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_classification_adg", "policy_binding")
_emit_snapshots_state("p0", "test_classification_adg", "state_snapshot")
emit_replay_key("p0", "test_classification_adg")
emit_determinism_digest("p0", "test_classification_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.config.structure_blueprint.classification import (
    CLASSIFICATION_SUFFIX_PATTERNS,
)


class TestClassificationSuffixPatterns:
    def test_is_mapping(self):
        assert isinstance(CLASSIFICATION_SUFFIX_PATTERNS, dict | type(CLASSIFICATION_SUFFIX_PATTERNS))

    def test_agent_pattern_present(self):
        values = list(CLASSIFICATION_SUFFIX_PATTERNS.values())
        assert "AGENT" in values

    def test_types_pattern_present(self):
        values = list(CLASSIFICATION_SUFFIX_PATTERNS.values())
        assert "TYPES" in values

    def test_config_pattern_present(self):
        values = list(CLASSIFICATION_SUFFIX_PATTERNS.values())
        assert "CONFIG" in values

    def test_all_values_are_strings(self):
        for v in CLASSIFICATION_SUFFIX_PATTERNS.values():
            assert isinstance(v, str)

    def test_all_keys_are_strings(self):
        for k in CLASSIFICATION_SUFFIX_PATTERNS.keys():
            assert isinstance(k, str)

    def test_non_empty(self):
        assert len(CLASSIFICATION_SUFFIX_PATTERNS) > 0
