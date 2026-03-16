"""ADG-driven tests for L5_safety/enforcement/hierarchy_validator_enforcer.py — fan_in=1."""
from __future__ import annotations

import json

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

_emit_records_execution_trace("p0", "evidence", "test_hierarchy_validator_enforcer_adg")
_emit_applies_guardrail("p0", "test_hierarchy_validator_enforcer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_hierarchy_validator_enforcer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_hierarchy_validator_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_hierarchy_validator_enforcer_adg")
emit_determinism_digest("p0", "test_hierarchy_validator_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.hierarchy_validator_enforcer import HierarchyValidator

_MINIMAL_CONFIG = {
    "version": "1.0",
    "layers": {
        "agentic_core.L0_routing*": 0,
        "agentic_core.L1_cognition*": 1,
        "agentic_core.L5_safety*": 5,
    },
    "forbidden_cross_imports": {},
    "allowed_cross_imports": {},
}


@pytest.fixture
def config_file(tmp_path):
    p = tmp_path / "layer_hierarchy.json"
    p.write_text(json.dumps(_MINIMAL_CONFIG), encoding="utf-8")
    return p


class TestHierarchyValidator:
    def test_creates_from_valid_config(self, config_file):
        v = HierarchyValidator(config_file)
        assert v is not None

    def test_config_hash_is_string(self, config_file):
        v = HierarchyValidator(config_file)
        assert isinstance(v.config_hash, str)
        assert len(v.config_hash) == 64  # sha256 hex

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            HierarchyValidator(tmp_path / "nonexistent.json")

    def test_raises_on_missing_required_fields(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text(json.dumps({"version": "1.0"}), encoding="utf-8")
        with pytest.raises(ValueError, match="missing required fields"):
            HierarchyValidator(p)

    def test_get_layer_level_known_module(self, config_file):
        v = HierarchyValidator(config_file)
        level = v.get_layer_level("agentic_core.L0_routing.utils")
        assert level == 0

    def test_get_layer_level_unknown_module(self, config_file):
        v = HierarchyValidator(config_file)
        level = v.get_layer_level("external_lib.foo")
        assert level == -1

    def test_is_import_allowed_downward(self, config_file):
        v = HierarchyValidator(config_file)
        # L5 (level 5) importing L0 (level 0) is allowed (higher can import lower)
        assert v.is_import_allowed(
            "agentic_core.L5_safety.foo",
            "agentic_core.L0_routing.bar",
        ) is True
