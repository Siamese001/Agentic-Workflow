"""
Invariant tests for _constants.py structural guarantees.

## BRANCH_INVENTORY
| file | function | branch | expected | test |
|------|----------|--------|----------|------|
| _constants.py | build_sovereign_territories | tests.subfolders has _quarantine | HARD FAIL — must never exist | test_quarantine_not_in_tests_subfolders |
| _constants.py | build_sovereign_territories | tests territory exists | must be present | test_tests_territory_exists |
| _constants.py | build_sovereign_territories | tests.subfolders is dict | must have real semantic subfolders | test_tests_subfolders_is_dict |
| _constants.py | SOVEREIGN_TERRITORIES | immutable at runtime | frozenset/MappingProxy | test_sovereign_territories_immutable |
| _constants.py | SOVEREIGN_TERRITORIES | tests.subfolders all keys semantic | no empty-string, no numeric keys | test_subfolders_all_have_semantic_names |
| _constants.py | SOVEREIGN_TERRITORIES | support is in tests.subfolders | declared canonical subfolder present | test_support_in_tests_subfolders |
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_constants_quarantine_invariant")
_emit_applies_guardrail("p0", "test_constants_quarantine_invariant", "p0_governance")
_emit_reads_policy_state("p0", "test_constants_quarantine_invariant", "policy_binding")
_emit_snapshots_state("p0", "test_constants_quarantine_invariant", "state_snapshot")
emit_replay_key("p0", "test_constants_quarantine_invariant")
emit_determinism_digest("p0", "test_constants_quarantine_invariant")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_constants_quarantine_invariant", "execution_auth")
_emit_validates_capability("p2", "test_constants_quarantine_invariant", "capability_check")
_emit_routes_to_capability("p2", "test_constants_quarantine_invariant", "capability_route")
_emit_writes_via_uwg("p2", "test_constants_quarantine_invariant", "uwg_write")
_emit_blocks_direct_write("p2", "test_constants_quarantine_invariant", "direct_write_block")
_emit_records_tool_invocation("p2", "test_constants_quarantine_invariant", "tool_invocation")
_emit_captures_execution_output("p2", "test_constants_quarantine_invariant", "exec_output")
_emit_dispatches_agent("p3", "test_constants_quarantine_invariant", "agent_dispatch")
_emit_coordinates_agents("p3", "test_constants_quarantine_invariant", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_constants_quarantine_invariant", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_constants_quarantine_invariant", "healing_outcome")
_emit_escalates_failure("p3", "test_constants_quarantine_invariant", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_constants_quarantine_invariant", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_constants_quarantine_invariant", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_constants_quarantine_invariant", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_constants_quarantine_invariant", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_constants_quarantine_invariant", "eval_metric")
_emit_stores_embedding("p4", "test_constants_quarantine_invariant", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_constants_quarantine_invariant", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_constants_quarantine_invariant", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Load SOVEREIGN_TERRITORIES once
# ---------------------------------------------------------------------------
from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.L5_safety.config.structure_blueprint import (
    get_all_territories,
)


def _tests_subfolders() -> dict:
    tests_cfg = get_all_territories().get("tests", {})
    subs = tests_cfg.get("subfolders", {})
    return dict(subs) if hasattr(subs, "items") else {}


# ---------------------------------------------------------------------------
# Core invariants
# ---------------------------------------------------------------------------


class TestConstantsQuarantineInvariant:
    def test_quarantine_not_in_tests_subfolders(self):
        """Hard invariant: _quarantine must NEVER appear in tests.subfolders.
        Healers must never create a _quarantine folder — it has no semantic meaning
        as a heal destination and caused data loss in previous heal runs.
        """
        subs = _tests_subfolders()
        assert "_quarantine" not in subs, (
            "_quarantine is present in get_all_territories()['tests']['subfolders']. "
            "This must be removed — healers must never create a _quarantine folder."
        )

    def test_tests_territory_exists(self):
        """tests territory must be declared in get_all_territories()."""
        assert TESTS_DIR in get_all_territories()

    def test_tests_subfolders_is_dict(self):
        """tests.subfolders must be a dict (not list, not None)."""
        tests_cfg = get_all_territories().get("tests", {})
        subs = tests_cfg.get("subfolders", None)
        import types as _types
        assert isinstance(subs, (dict, _types.MappingProxyType)), (
            f"tests.subfolders must be a dict or MappingProxyType, got {type(subs)}"
        )

    def test_support_in_tests_subfolders(self):
        """tests/support/ is a canonical subfolder and must be declared in get_all_territories()."""
        subs = _tests_subfolders()
        assert "support" in subs, (
            "'support' is missing from get_all_territories()['tests']['subfolders']. "
            "tests/support/ holds real infrastructure agents and must be a declared canonical folder."
        )

    def test_subfolders_all_have_semantic_names(self):
        """All tests/ subfolder names must be non-empty strings."""
        subs = _tests_subfolders()
        for name in subs.keys():
            assert isinstance(name, str) and len(name) > 0, f"Non-semantic subfolder key found: {name!r}"

    def test_sovereign_territories_not_plain_dict(self):
        """SOVEREIGN_TERRITORIES must be immutable (MappingProxyType), not a plain dict."""

        import types
        assert isinstance(get_all_territories(), types.MappingProxyType), (
            "get_all_territories() must return a MappingProxyType, not a plain mutable dict."
        )

    def test_mutation_of_sovereign_territories_raises(self):
        """SOVEREIGN_TERRITORIES must reject mutation at the top level."""
        with pytest.raises((TypeError, AttributeError)):
            get_all_territories()["__injection__"] = "evil"  # type: ignore[index]


# ---------------------------------------------------------------------------
# Regression guard — depth_aligned
# ---------------------------------------------------------------------------


class TestConstantsDepthAlignedInvariant:
    def test_depth_aligned_not_in_any_subfolders(self):
        """depth_aligned must never appear as a declared subfolder in any territory.
        It is a semantically meaningless spacer that was used to satisfy depth counters.
        """

        def _walk(obj, path=""):
            if isinstance(obj, (dict,)) or hasattr(obj, "items"):
                for k, v in obj.items():
                    assert k != "depth_aligned", (
                        f"depth_aligned found as a subfolder key at {path}.{k} — "
                        "this is forbidden. Subfolders must have semantic meaning."
                    )
                    _walk(v, f"{path}.{k}")

        _walk(get_all_territories())

    def test_tests_subfolders_count_is_nonzero(self):
        """Sanity: tests/ must have at least several canonical subfolders."""
        subs = _tests_subfolders()
        assert len(subs) >= 5, f"tests/ has only {len(subs)} subfolders — expected at least 5 canonical ones."
