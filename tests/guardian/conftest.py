# Core pytest configuration
import pytest


# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    from pathlib import Path

    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"


# Test collection configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "data: marks tests as data-dependent")


# Core pytest configuration
import pytest


# Standard fixtures for path semantics
@pytest.fixture
def test_data_path():
    """Fixture for test data path."""
    from pathlib import Path

    return Path(__file__).parent / "test_data"


@pytest.fixture
def temp_project_dir(tmp_path):
    """Fixture for temporary project directory."""
    return tmp_path / "project"


# Test collection configuration
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "data: marks tests as data-dependent")


"""
Guardian Suite Configuration and Reporting (HARDENED)
======================================================
Zero-Trust Guardian Layer - Architectural Health Validation

MANIFESTO COMPLIANCE:
1. Static Stasis: DO NOT execute agent code. AST only.
2. Binary Output: PASS or BLOCK. No warnings.
3. Machine-Readable: JSON report to logs/guardian_report.json
4. Constitutional Lock: structure_blueprint.py enforcement
5. Subatomic Atomicity: Block files >800 LOC, >2 Mixins, >2 Methods
6. No AI Checking AI: Deterministic Python only
7. Idempotency: Stable target names for Healer

This conftest.py provides:
1. Guardian marker registration for all tests in this directory
2. JSON report builder with Ratchet mechanism
3. Violation tracking and categorization
4. Session-finish hook writes guardian_report.json

USAGE:
    pytest tests/guardian/ -v -m guardian
    ./run_guardian.sh

All tests in this directory are automatically marked with @pytest.mark.guardian
"""

import sys
import tempfile
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L0_ROUTING_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L6_OBSERVABILITY_DIR,
)

# REMOVED: _emit_authorize_and_execute("p2", "conftest", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "conftest", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "conftest", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "conftest", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "conftest", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "conftest", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "conftest", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "conftest", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "conftest", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "conftest", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "conftest", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "conftest", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "conftest", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "conftest", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "conftest", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "conftest", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "conftest", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "conftest", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "conftest", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "conftest", "exec_snapshot_link")
from tests.helpers.robust_fs import robust_rmtree

# REMOVED: _emit_records_execution_trace("p0", "evidence", "conftest_guardian")
# REMOVED: _emit_applies_guardrail("p0", "conftest_guardian", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "conftest_guardian", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "conftest_guardian", "state_snapshot")
# REMOVED: emit_replay_key("p0", "conftest_guardian")
# REMOVED: emit_determinism_digest("p0", "conftest_guardian")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.guardian.guardian_report import (
    GuardianReportBuilder,
    GuardianStatus,
    write_guardian_report,
)

# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("conftest", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("conftest", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("conftest", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("conftest", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("conftest", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("conftest", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("conftest", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("conftest", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("conftest", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("conftest", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("conftest", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("conftest", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("conftest", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("conftest", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("conftest", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("conftest", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("conftest", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("conftest", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("conftest", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("conftest", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("conftest", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("conftest", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("conftest", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "conftest", "context_pull")
# REMOVED: _emit_pulls_context("p1", "conftest", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "conftest", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "conftest", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "conftest", "write_through")
# REMOVED: _emit_writes_through("p1", "conftest", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "conftest", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "conftest", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "conftest", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "conftest", "human_escalation")
# REMOVED: _emit_routes_through("p1", "conftest", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "conftest", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "conftest", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "conftest", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "conftest", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "conftest", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "conftest", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "conftest", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "conftest", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "conftest", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "conftest")
# REMOVED: _emit_gated_by_confidence("p1", "conftest", "confidence_gate")

# ---------------------------------------------------------------------------
# Collection exclusions — files with broken imports unrelated to guardian
# contract.  Managed here (not in CI workflow) so the workflow stays clean.
# TODO(#GUARD-01 owner=@guardian-team review_by=2026-06-01): fix test_comprehensive_structure.py (missing scripts.validate_structure)
# TODO(#GUARD-02 owner=@guardian-team review_by=2026-06-01): fix test_mro_integrity.py (missing core_integrity_util module)
# ---------------------------------------------------------------------------
collect_ignore_glob = [
    "test_comprehensive_structure.py",
    "test_mro_integrity.py",
]

# =============================================================================
# GUARDIAN MARKER - Auto-apply to all tests in this directory
# =============================================================================


def pytest_collection_modifyitems(config, items):
    """
    Automatically add the guardian marker to all tests in this directory.

    This hook only adds markers, no deselection occurs.
    All items are retained, so deselection count is 0.
    """
    guardian_marker = pytest.mark.guardian
    deselected_count = 0

    for item in items:
        if "guardian" in str(item.fspath):
            item.add_marker(guardian_marker)

    # Log that no deselection occurred (all items retained)
    config._guardian_deselected_count = deselected_count


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    RATCHET MECHANISM: Generate JSON Guardian report after test completion.

    Writes machine-readable guardian_report.json to logs/ directory.
    This report is consumed by the Symmetric Healer for automated remediation.
    """
    # Check if we're running guardian tests
    guardian_tests_found = False
    for _stat_name, stat_items in terminalreporter.stats.items():
        if hasattr(stat_items, "__iter__"):
            for item in stat_items:
                if hasattr(item, "nodeid") and "guardian" in item.nodeid:
                    guardian_tests_found = True
                    break
        if guardian_tests_found:
            break

    # Skip report generation if no guardian tests were found
    if not guardian_tests_found:
        return

    # Collect test results
    stats = terminalreporter.stats
    passed_tests = len(stats.get("passed", []))
    failed_items = stats.get("failed", [])
    error_items = stats.get("error", [])
    skipped_tests = len(stats.get("skipped", []))

    total_tests = passed_tests + len(failed_items) + len(error_items) + skipped_tests
    failed_tests = len(failed_items) + len(error_items)

    # Get or create the report builder singleton
    builder = GuardianReportBuilder.get_instance("guardian")

    # Set metadata
    builder.set_metadata("total_tests", total_tests)
    builder.set_metadata("passed_tests", passed_tests)
    builder.set_metadata("failed_tests", failed_tests)
    builder.set_metadata("skipped_tests", skipped_tests)
    builder.set_metadata("exit_status", exitstatus)

    # Categorize failed tests
    failed_by_category = {
        "mro_integrity": [],
        "import_safety": [],
        "ssot_alignment": [],
        "subatomic": [],
        "forensic": [],
        "other": [],
    }

    for failed_test in list(failed_items) + list(error_items):
        test_name = getattr(failed_test, "nodeid", str(failed_test))
        if "mro" in test_name.lower():
            failed_by_category["mro_integrity"].append(test_name)
        elif "import" in test_name.lower():
            failed_by_category["import_safety"].append(test_name)
        elif "ssot" in test_name.lower() or "alignment" in test_name.lower():
            failed_by_category["ssot_alignment"].append(test_name)
        elif "subatomic" in test_name.lower():
            failed_by_category["subatomic"].append(test_name)
        elif "forensic" in test_name.lower():
            failed_by_category["forensic"].append(test_name)
        else:
            failed_by_category["other"].append(test_name)

    builder.set_metadata("failed_by_category", failed_by_category)

    # Build and write JSON report
    report = builder.build()

    # Determine final status
    if exitstatus == 0 and not report.is_blocking():
        report.status = GuardianStatus.PASS.value
    else:
        report.status = GuardianStatus.BLOCK.value

    # Write JSON report to agentic_core/L0_routing/utils/guardian_report.json
    json_report_path = PROJECT_ROOT / L0_ROUTING_DIR / "logs" / "guardian_report.json"
    json_report_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        report_path = write_guardian_report(report, json_report_path)

        # Print minimal summary to terminal (JSON is the source of truth)
        print("\n" + "=" * 60)
        print(f"GUARDIAN SHIELD: {report.status}")
        print("=" * 60)
        print(f"JSON Report: {report_path}")
        print(f"Violations: {len(report.violations)}")
        if report.summary:
            for code, count in report.summary.items():
                print(f"  - {code}: {count}")
        print("=" * 60)

    except (OSError, TypeError, ValueError) as e:
        print(f"CRITICAL: Could not write guardian report: {e}")
        raise

    # Reset builder for next run (idempotency)
    GuardianReportBuilder.reset()


@pytest.fixture(autouse=True)
def _v15_default_off(monkeypatch):
    """Default V15 enforcement OFF for guardian tests.

    Most guardian tests validate structural/schema properties and do not
    exercise V15 enforcement semantics.  With the fail-closed default
    (is_v15_enforced() == True when env var is absent), unsigned
    GuardianResult.to_json() calls would raise V15EnforcementError.

    Tests that *do* exercise V15 semantics override this via
    ``monkeypatch.setenv`` or ``@patch.dict``.
    """
    monkeypatch.setenv("V15_ENFORCEMENT", "0")


@pytest.fixture
def robust_tmp_path(request: pytest.FixtureRequest) -> Path:
    """§Wave5.0.6: Temp directory with robust_rmtree cleanup.

    Replaces tmp_path for fixtures that create deep directory trees
    on Windows, where shutil.rmtree can transiently fail with
    WinError 2 / 32 during batch test runs.
    """
    d = Path(tempfile.mkdtemp(prefix=f"guardian_{request.node.name[:20]}_"))
    yield d
    robust_rmtree(d)


@pytest.fixture(scope="session", autouse=True)
def guardian_session_marker():
    """
    Automatically mark all guardian tests
    """
    pass


# =============================================================================
# SESSION-SCOPED FIXTURES - Shared across all Guardian tests
# =============================================================================


@pytest.fixture(scope="session")
def agent_registry():
    """
    Session-scoped agent registry for all tests.
    Caches agent discovery to improve test performance.
    """
    from tests.guardian.base import GuardianTestBase

    registry = {}

    for agent_file in GuardianTestBase.scan_agents():
        tree = GuardianTestBase.parse_ast(agent_file)
        if tree:
            agent_classes = GuardianTestBase.find_agent_classes(tree)
            registry[str(agent_file)] = {
                "file_path": agent_file,
                "agent_classes": [cls.name for cls in agent_classes],
                "layer": GuardianTestBase.check_layer_hierarchy(agent_file)["layer"],
            }

    return registry


@pytest.fixture(scope="session")
def layer_hierarchy():
    """Shared layer hierarchy data."""
    return {
        L0_ROUTING_DIR: 0,
        L1_COGNITION_DIR: 1,
        L2_EXECUTION_DIR: 2,
        L3_ORCHESTRATION_DIR: 3,
        L4_STATE_DIR: 4,
        "L5_safety": 5,
        L6_OBSERVABILITY_DIR: 6,
    }


@pytest.fixture(scope="session")
def guardian_performance_baseline():
    """Baseline performance metrics for Guardian tests."""
    return {
        "max_test_time_seconds": 30,
        "max_memory_mb": 100,
        "max_agents_to_scan": 800,
    }


@pytest.fixture(scope="session")
def critical_files():
    """List of critical files that must exist."""
    return [
        "agentic_core/L3_orchestration/reasoning/SovereignMcpRouterAgent.py",
        "agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py",
        "agentic_core/L2_execution/enforcement/SovereignPineconeMcpClientAgent.py",
        "agentic_core/L2_execution/enforcement/SovereignMCPGatewayAgent.py",
        "agentic_core/L2_execution/reasoning/WebSearchTools.py",
        "agentic_core/base_agents/SovereignBaseAgent.py",
    ]


@pytest.fixture(scope="session")
def territories():
    """List of code territories to scan."""
    return [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
