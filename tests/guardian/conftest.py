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

from tests.helpers.robust_fs import robust_rmtree

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tests.guardian.guardian_report import (
    GuardianReportBuilder,
    GuardianStatus,
    write_guardian_report,
)

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
    json_report_path = PROJECT_ROOT / "agentic_core" / "L0_routing" / "logs" / "guardian_report.json"
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

    except Exception as e:
        print(f"CRITICAL: Could not write guardian report: {e}")

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
        "L0_routing": 0,
        "L1_cognition": 1,
        "L2_execution": 2,
        "L3_orchestration": 3,
        "L4_state": 4,
        "L5_safety": 5,
        "L6_observability": 6,
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
        "agentic_core/L5_safety/enforcement/mcp_sovereign_authority.py",
        "agentic_core/L2_execution/enforcement/SovereignPineconeMcpClientAgent.py",
        "agentic_core/L2_execution/enforcement/SovereignMCPGatewayAgent.py",
        "agentic_core/L2_execution/reasoning/WebSearchTools.py",
        "agentic_core/base_agents/SovereignBaseAgent.py",
    ]


@pytest.fixture(scope="session")
def territories():
    """List of code territories to scan."""
    return ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]
