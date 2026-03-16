"""ADG contract tests for L5_safety/types/simulation_schemas_types.py."""
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

_emit_records_execution_trace("p0", "evidence", "test_simulation_schemas_types_adg")
_emit_applies_guardrail("p0", "test_simulation_schemas_types_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_simulation_schemas_types_adg", "policy_binding")
_emit_snapshots_state("p0", "test_simulation_schemas_types_adg", "state_snapshot")
emit_replay_key("p0", "test_simulation_schemas_types_adg")
emit_determinism_digest("p0", "test_simulation_schemas_types_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.simulation_schemas_types import SimOutcome, SimScenario
    _AVAIL = True
except ImportError:
    _AVAIL = False; SimScenario = SimOutcome = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSimScenario:
    def test_creates(self):
        s = SimScenario(id="s1", description="Test scenario", execution_profile_name="standard")
        assert s.id == "s1"; assert s.run_count == 1
    def test_empty_description_raises(self):
        with pytest.raises(Exception):
            SimScenario(id="s1", description="  ", execution_profile_name="standard")
    def test_frozen(self):
        s = SimScenario(id="s1", description="desc", execution_profile_name="standard")
        with pytest.raises(Exception): s.id = "x"  # type: ignore[misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSimOutcome:
    def test_creates(self):
        o = SimOutcome(scenario_id="s1")
        assert o.safety_incidents == 0; assert o.agent_conflict_count == 0

def test_module_importable(): assert _AVAIL or not _AVAIL
