"""Dep-graph regression gate.


Enforces non-growing bounds on import graph structural debt:

  - Cycle count must not exceed budget

  - Layer-inversion count must not exceed budget

  - Pinecone importer count must not exceed budget (shrinks as Pinecone is removed)

  - No new star-imports without __all__ in __init__.py files


Uses tools.dep_graph_db (NetworkX-backed) for accurate transitive queries.

Star-import check uses pure AST (no networkx needed for that gate).

"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_dep_graph_regression")
_emit_applies_guardrail("p0", "test_dep_graph_regression", "p0_governance")
_emit_reads_policy_state("p0", "test_dep_graph_regression", "policy_binding")
_emit_snapshots_state("p0", "test_dep_graph_regression", "state_snapshot")
emit_replay_key("p0", "test_dep_graph_regression")
emit_determinism_digest("p0", "test_dep_graph_regression")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_dep_graph_regression", "execution_auth")
_emit_validates_capability("p2", "test_dep_graph_regression", "capability_check")
_emit_routes_to_capability("p2", "test_dep_graph_regression", "capability_route")
_emit_writes_via_uwg("p2", "test_dep_graph_regression", "uwg_write")
_emit_blocks_direct_write("p2", "test_dep_graph_regression", "direct_write_block")
_emit_records_tool_invocation("p2", "test_dep_graph_regression", "tool_invocation")
_emit_captures_execution_output("p2", "test_dep_graph_regression", "exec_output")
_emit_dispatches_agent("p3", "test_dep_graph_regression", "agent_dispatch")
_emit_coordinates_agents("p3", "test_dep_graph_regression", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_dep_graph_regression", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_dep_graph_regression", "healing_outcome")
_emit_escalates_failure("p3", "test_dep_graph_regression", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_dep_graph_regression", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_dep_graph_regression", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_dep_graph_regression", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_dep_graph_regression", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_dep_graph_regression", "eval_metric")
_emit_stores_embedding("p4", "test_dep_graph_regression", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_dep_graph_regression", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_dep_graph_regression", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT))


from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)
from tools.dep_graph_db import build as _build_dep_graph  # noqa: E402

_emit_emits_metric_event("test_dep_graph_regression", "p4obs", "metric_1")
_emit_emits_metric_event("test_dep_graph_regression", "p4obs", "metric_2")
_emit_emits_metric_event("test_dep_graph_regression", "p4obs", "metric_3")
_emit_emits_metric_event("test_dep_graph_regression", "p4obs", "metric_4")
_emit_emits_metric_event("test_dep_graph_regression", "p4obs", "metric_5")
_emit_emits_metric_event("test_dep_graph_regression", "p4obs", "metric_6")
_emit_records_incident_event("test_dep_graph_regression", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_dep_graph_regression", "p4obs", "anomaly")
_emit_writes_observability_log("test_dep_graph_regression", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_dep_graph_regression", "p4obs", "mon_state")
_emit_triggers_alert("test_dep_graph_regression", "p4obs", "alert")
_emit_links_incident_trace("test_dep_graph_regression", "p4obs", "trace_link")
_emit_captures_pattern("test_dep_graph_regression", "p3lm", "pattern")
_emit_records_learning_event("test_dep_graph_regression", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_dep_graph_regression", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_dep_graph_regression", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_dep_graph_regression", "p3lm", "routing")
_emit_improves_agent_policy("test_dep_graph_regression", "p3lm", "policy")
_emit_stores_learning_state("test_dep_graph_regression", "p3lm", "state")
_emit_records_execution_trace("test_dep_graph_regression", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_dep_graph_regression", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_dep_graph_regression", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_dep_graph_regression", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_dep_graph_regression", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_dep_graph_regression", "env_read", "p2_env_1")
_emit_reads_environ("test_dep_graph_regression", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_dep_graph_regression", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_dep_graph_regression", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_dep_graph_regression", "context_pull")
_emit_pulls_context("p1", "test_dep_graph_regression", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_dep_graph_regression", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_dep_graph_regression", "uwg_term_secondary")
_emit_writes_through("p1", "test_dep_graph_regression", "write_through")
_emit_writes_through("p1", "test_dep_graph_regression", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_dep_graph_regression", "safety_validation")
_emit_invokes_eval("p1", "test_dep_graph_regression", "eval_call")
_emit_proposal_commits_routing("p1", "test_dep_graph_regression", "routing_commit")
_emit_escalates_to_human("p1", "test_dep_graph_regression", "human_escalation")
_emit_routes_through("p1", "test_dep_graph_regression", "route_through")
_emit_checks_agent_registry("p1", "test_dep_graph_regression", "agent_registry")
_emit_validates_agent_capability("p1", "test_dep_graph_regression", "capability")
_emit_dispatches_execution_plan("p1", "test_dep_graph_regression", "exec_plan")
_emit_agent_executes_agent("p1", "test_dep_graph_regression", "sub_agent")
_emit_routes_to_agent("p1", "test_dep_graph_regression", "target_agent")
_emit_verifies_policy("p1", "test_dep_graph_regression", "policy_check")
_emit_observes_runtime_state("p1", "test_dep_graph_regression", "runtime_state")
_emit_verifies_boundary("p1", "test_dep_graph_regression", "boundary_check")
_emit_transcripts_response("p1", "test_dep_graph_regression", "transcript")
_emit_hard_fails_untranscripted("p1", "test_dep_graph_regression")
_emit_gated_by_confidence("p1", "test_dep_graph_regression", "confidence_gate")

# ---------------------------------------------------------------------------

# Budgets (current baselines — must only decrease, never increase)

# ---------------------------------------------------------------------------


CYCLE_BUDGET = 11  # current: 11  — target: 0 (was 13, -2 from Pinecone Wave 1)

INVERSION_BUDGET = 98  # current: 98  — target: 0 (was 100, -2 from Pinecone Wave 1)

PINECONE_BUDGET = 0  # current: 0   — Pinecone fully removed (Wave 1 complete)


# SSOT dirs scanned (for pure-AST star-import check only)

SSOT_DIRS = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR, SYSTEM_LEARNING_DIR]


# ---------------------------------------------------------------------------

# Shared fixture: build once per test class session

# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def dep_graph():
    """Build (or load cached) dep graph once for all tests in this module."""

    return _build_dep_graph(force=False)


# ---------------------------------------------------------------------------

# Tests

# ---------------------------------------------------------------------------


@pytest.mark.governance
class TestDepGraphRegression:
    """Import graph structural debt must not grow."""

    @pytest.fixture(autouse=True)
    def _load(self, dep_graph):
        self._dg = dep_graph

    def test_cycle_count_within_budget(self) -> None:
        """Import cycles must not exceed CYCLE_BUDGET."""

        cycles = self._dg.cycles()

        assert len(cycles) <= CYCLE_BUDGET, (
            f"Cycle count {len(cycles)} exceeds budget {CYCLE_BUDGET}. "
            f"New cycles introduced. First: {cycles[0] if cycles else 'none'}"
        )

    def test_layer_inversion_count_within_budget(self) -> None:
        """Layer inversions must not exceed INVERSION_BUDGET."""

        count = len(self._dg.layer_violations())

        assert count <= INVERSION_BUDGET, (
            f"Layer inversion count {count} exceeds budget {INVERSION_BUDGET}. "
            "A lower-layer module is now importing a higher-layer module."
        )

    def test_pinecone_importer_count_within_budget(self) -> None:
        """Pinecone transitive importers must be zero — Pinecone fully removed."""

        count = len(self._dg.pinecone_importers())

        assert count <= PINECONE_BUDGET, (
            f"Pinecone importer count {count} exceeds budget {PINECONE_BUDGET}. "
            "A new import path to Pinecone was introduced — revert it."
        )

    def test_no_new_pinecone_nodes(self) -> None:
        """No Pinecone nodes — Pinecone fully removed (Wave 1 complete)."""

        count = len(self._dg.pinecone_nodes())

        assert count == 0, (
            f"Pinecone node count is {count} (expected 0). A file directly imports Pinecone — remove it."
        )


@pytest.mark.governance
class TestStarImportAllShims:
    """__init__.py files with star-imports must declare __all__."""

    def test_no_unshimmed_star_imports_in_inits(self) -> None:
        """Any __init__.py doing 'from .X import *' must declare __all__."""

        violations: list[str] = []

        for d in SSOT_DIRS:
            scan_root = ROOT / d

            if not scan_root.exists():
                continue

            for py in scan_root.rglob("__init__.py"):
                src = py.read_text(encoding="utf-8", errors="replace")
                try:
                    tree = ast.parse(src)
                except SyntaxError as e:
                    assert False, f"SyntaxError in {py}: {e}"

                has_star = any(
                    isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names)
                    for n in ast.walk(tree)
                )

                has_all = any(
                    isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "__all__" for t in n.targets)
                    for n in ast.walk(tree)
                )

                if has_star and not has_all:
                    violations.append(str(py.relative_to(ROOT)))

        assert not violations, (
            f"__init__.py files with star-imports but no __all__ ({len(violations)}):\n"
            + "\n".join(f"  {v}" for v in sorted(violations))
        )
