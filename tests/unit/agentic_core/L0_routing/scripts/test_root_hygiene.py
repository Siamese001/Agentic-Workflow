"""
File: tests/L0/test_root_hygiene.py
Rationale:
    Verifies that the RootHygieneEnforcer correctly cleans the environment.
"""

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    L0_ROUTING_DIR,
    OPS_SCRIPTS_DIR,
)
from agentic_core.L0_routing.scripts.root_hygiene_util import enforce_root_hygiene
from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR
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

_emit_records_execution_trace("p0", "evidence", "test_root_hygiene")
_emit_applies_guardrail("p0", "test_root_hygiene", "p0_governance")
_emit_reads_policy_state("p0", "test_root_hygiene", "policy_binding")
_emit_snapshots_state("p0", "test_root_hygiene", "state_snapshot")
emit_replay_key("p0", "test_root_hygiene")
emit_determinism_digest("p0", "test_root_hygiene")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_root_hygiene", "execution_auth")
_emit_validates_capability("p2", "test_root_hygiene", "capability_check")
_emit_routes_to_capability("p2", "test_root_hygiene", "capability_route")
_emit_writes_via_uwg("p2", "test_root_hygiene", "uwg_write")
_emit_blocks_direct_write("p2", "test_root_hygiene", "direct_write_block")
_emit_records_tool_invocation("p2", "test_root_hygiene", "tool_invocation")
_emit_captures_execution_output("p2", "test_root_hygiene", "exec_output")
_emit_dispatches_agent("p3", "test_root_hygiene", "agent_dispatch")
_emit_coordinates_agents("p3", "test_root_hygiene", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_root_hygiene", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_root_hygiene", "healing_outcome")
_emit_escalates_failure("p3", "test_root_hygiene", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_root_hygiene", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_root_hygiene", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_root_hygiene", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_root_hygiene", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_root_hygiene", "eval_metric")
_emit_stores_embedding("p4", "test_root_hygiene", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_root_hygiene", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_root_hygiene", "exec_snapshot_link")


@pytest.fixture
def dirty_repo(tmp_path):
    """Creates a dirty mock repo with illegal root folders."""
    # Setup Markers
    (tmp_path / AGENTIC_CORE_DIR).mkdir()
    (tmp_path / "pyproject.toml").touch()

    # Create Illegal Root Scripts
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "standalone_tool.py").write_text("print('hello')")
    (scripts / "core_tool.py").write_text("import agentic_core\nprint('core')")

    # Create Illegal Coverage
    cov = tmp_path / "coverage_html"
    cov.mkdir()
    (cov / "index.html").touch()

    return tmp_path


def test_hygiene_enforcement(dirty_repo, monkeypatch):
    """Test that scripts are moved to correct locations and root is cleaned."""
    monkeypatch.chdir(dirty_repo)
    monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")

    # Run Enforcer
    enforce_root_hygiene()

    # Assertions
    # 1. Illegal dirs gone
    assert not (dirty_repo / "scripts").exists()
    assert not (dirty_repo / "coverage_html").exists()

    # 2. Standalone script -> ops_scripts
    assert (dirty_repo / OPS_SCRIPTS_DIR / "standalone_tool.py").exists()

    # 3. Core script -> agentic_core/L0_routing/scripts
    assert (dirty_repo / L0_ROUTING_DIR / "scripts" / "core_tool.py").exists()

    # 4. Coverage -> reports
    assert (dirty_repo / REPORTS_DIR / "coverage_html" / "index.html").exists()


def test_purge_cache_refiling(dirty_repo, monkeypatch):
    """Test the specific rule for purge_cache.py reorganization."""
    monkeypatch.chdir(dirty_repo)
    monkeypatch.setenv("AGENTIC_ALLOW_MUTATION_FOR_TESTS", "1")

    # Setup purge_cache in illegal scripts folder
    (dirty_repo / "scripts" / "purge_cache.py").write_text("print('clean')")

    enforce_root_hygiene()

    # Should end up nested in maintenance
    assert (dirty_repo / OPS_SCRIPTS_DIR / "maintenance" / "purge_cache.py").exists()
