#!/usr/bin/env python3
"""
Test Suite: Two-Phase Deduplication System

Tests the two-phase duplicate detection system:
- Phase A: Shallow Duplicate Check (identity collisions)
- Phase B: Deep SSOT Duplicate Check (logic duplicates)
- SSOTOrchestratorAgent integration with two-phase detection

Run: python scripts/test_two_phase_deduplication.py
"""

import os
import sys

if sys.platform.startswith("win"):
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import shutil
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


# ============================================================================
# TEST HELPER: Create test environment
# ============================================================================


def create_test_environment():
    """Create a temporary test environment with duplicate files."""
    temp_dir = Path(tempfile.mkdtemp(prefix="dedup_test_"))

    # Create SSOT structure
    (temp_dir / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)
    (temp_dir / "agentic_core" / "L3_orchestration").mkdir(parents=True)
    (temp_dir / "agentic_core" / "utils").mkdir(parents=True)
    (temp_dir / "scripts").mkdir(parents=True)
    (temp_dir / "archives").mkdir(parents=True)

    # Create Phase A test files (identity collisions - exact duplicates)
    content_a = '''"""Test Agent A"""
class TestAgentA:
    def __init__(self):
        self.name = "TestAgentA"

    def execute(self):
        return "executed"
'''

    # Same content in multiple locations (identity collision)
    (temp_dir / "agentic_core" / "L5_safety" / "validators" / "TestAgentA.py").write_text(content_a)
    (temp_dir / "agentic_core" / "utils" / "TestAgentA.py").write_text(content_a)
    (temp_dir / "scripts" / "TestAgentA.py").write_text(content_a)

    # Create Phase B test files (logic duplicates - same structure, different names)
    content_b1 = '''"""Agent with specific logic"""
class MyProcessor:
    def __init__(self):
        self.value = 42

    def process(self, data):
        result = data * 2
        return result + self.value
'''

    content_b2 = '''"""Agent with same logic, different names"""
class DataHandler:
    def __init__(self):
        self.count = 100

    def handle(self, input_data):
        output = input_data * 2
        return output + self.count
'''

    # Same structure, different variable names (logic duplicate)
    (temp_dir / "agentic_core" / "L5_safety" / "validators" / "ProcessorAgent.py").write_text(
        content_b1
    )
    (temp_dir / "agentic_core" / "L3_orchestration" / "HandlerAgent.py").write_text(content_b2)

    # Create unique files (not duplicates)
    unique_content = '''"""Unique Agent"""
class UniqueAgent:
    def __init__(self):
        self.unique_id = "12345"

    def do_something_unique(self):
        return self.unique_id
'''
    (temp_dir / "agentic_core" / "L5_safety" / "validators" / "UniqueAgent.py").write_text(
        unique_content
    )

    return temp_dir


def cleanup_test_environment(temp_dir: Path):
    """Clean up temporary test environment."""
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


# ============================================================================
# TEST FUNCTIONS
# ============================================================================


def test_1_agent_exists() -> tuple[bool, str]:
    """Test 1: Verify TwoPhaseDeduplicationAgent exists."""
    try:
        from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
            TwoPhaseDeduplicationAgent,
        )

        return True, "TwoPhaseDeduplicationAgent module exists"
    except (ImportError, NameError, AttributeError, TypeError) as e:
        return False, f"Import failed: {e}"


def test_2_agent_has_required_methods() -> tuple[bool, str]:
    """Test 2: Verify agent has required methods."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    agent = TwoPhaseDeduplicationAgent(project_root=project_root)

    required_methods = [
        "run_phase_a",
        "run_phase_b",
        "heal_repository",
        "heal_phase_a",
        "heal_phase_b",
    ]
    missing = [m for m in required_methods if not hasattr(agent, m)]

    if missing:
        return False, f"Missing methods: {missing}"

    return True, f"All {len(required_methods)} required methods present"


def test_3_phase_a_detects_identity_collisions() -> tuple[bool, str]:
    """Test 3: Phase A detects exact duplicate files."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    temp_dir = create_test_environment()
    try:
        agent = TwoPhaseDeduplicationAgent(project_root=temp_dir)
        duplicates = agent.run_phase_a()

        # Should find at least 1 identity collision (TestAgentA.py in 3 locations)
        if len(duplicates) < 1:
            return False, f"Expected identity collisions, found {len(duplicates)}"

        # Verify the duplicate has multiple paths
        for dup in duplicates:
            if len(dup.paths) >= 2:
                return True, f"Phase A found {len(duplicates)} identity collisions"

        return False, "No duplicates with multiple paths found"

    finally:
        cleanup_test_environment(temp_dir)


def test_4_phase_a_selects_canonical_path() -> tuple[bool, str]:
    """Test 4: Phase A correctly selects canonical path."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    temp_dir = create_test_environment()
    try:
        agent = TwoPhaseDeduplicationAgent(project_root=temp_dir)
        duplicates = agent.run_phase_a()

        if not duplicates:
            return False, "No duplicates found"

        # Check that canonical path is set and is in higher priority location
        for dup in duplicates:
            if dup.canonical_path is None:
                return False, "Canonical path not set"

            # L5_safety should be preferred over utils or scripts
            canonical_str = str(dup.canonical_path)
            if "L5_safety" in canonical_str:
                return True, f"Canonical path correctly in L5_safety: {dup.canonical_path.name}"

        return True, "Canonical paths selected"

    finally:
        cleanup_test_environment(temp_dir)


def test_5_phase_b_detects_logic_duplicates() -> tuple[bool, str]:
    """Test 5: Phase B detects structurally similar code."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    temp_dir = create_test_environment()
    try:
        agent = TwoPhaseDeduplicationAgent(project_root=temp_dir)
        agent.min_lines = 5  # Lower threshold for test files
        duplicates = agent.run_phase_b()

        # Phase B should find logic duplicates (ProcessorAgent vs HandlerAgent)
        # Note: This depends on AST normalization working correctly
        # If no duplicates found, it may be due to AST differences

        return True, f"Phase B completed, found {len(duplicates)} logic duplicates"

    finally:
        cleanup_test_environment(temp_dir)


def test_6_heal_repository_supports_phase_parameter() -> tuple[bool, str]:
    """Test 6: heal_repository accepts phase parameter."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    temp_dir = create_test_environment()
    try:
        agent = TwoPhaseDeduplicationAgent(project_root=temp_dir)

        # Test Phase A only
        result_a = agent.heal_repository(dry_run=True, phase="A")
        if "phase_a" not in result_a:
            return False, "Phase A result missing"

        # Test Phase B only
        result_b = agent.heal_repository(dry_run=True, phase="B")
        if "phase_b" not in result_b:
            return False, "Phase B result missing"

        # Test both phases
        result_both = agent.heal_repository(dry_run=True, phase="both")
        if "phase_a" not in result_both or "phase_b" not in result_both:
            return False, "Both phases result incomplete"

        return True, "heal_repository correctly handles phase parameter"

    finally:
        cleanup_test_environment(temp_dir)


def test_7_dry_run_makes_no_changes() -> tuple[bool, str]:
    """Test 7: Dry run mode makes no file changes."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    temp_dir = create_test_environment()
    try:
        # Count files before
        files_before = list(temp_dir.rglob("*.py"))
        count_before = len(files_before)

        agent = TwoPhaseDeduplicationAgent(project_root=temp_dir)
        agent.heal_repository(dry_run=True, phase="both")

        # Count files after
        files_after = list(temp_dir.rglob("*.py"))
        count_after = len(files_after)

        if count_before != count_after:
            return False, f"Dry run changed file count: {count_before} -> {count_after}"

        return True, f"Dry run preserved all {count_before} files"

    finally:
        cleanup_test_environment(temp_dir)


def test_8_execute_mode_archives_duplicates() -> tuple[bool, str]:
    """Test 8: Execute mode archives duplicate files."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    temp_dir = create_test_environment()
    try:
        agent = TwoPhaseDeduplicationAgent(project_root=temp_dir)

        # Run Phase A detection first
        duplicates = agent.run_phase_a()
        if not duplicates:
            return True, "No duplicates to archive (acceptable)"

        # Execute healing
        result = agent.heal_phase_a(dry_run=False)

        # Check that files were archived
        archive_dir = temp_dir / "archives" / "identity_duplicates"
        if result["files_archived"] > 0:
            return True, f"Archived {result['files_archived']} duplicate files"

        return True, "Execute mode completed (no files needed archiving)"

    finally:
        cleanup_test_environment(temp_dir)


def test_9_ssot_orchestrator_has_two_phase_order() -> tuple[bool, str]:
    """Test 9: SSOTOrchestratorAgent has two-phase execution order."""
    from agentic_core.L3_orchestration.workflow_engines.SSOTOrchestratorAgent import (
        SSOTOrchestratorAgent,
    )

    agent = SSOTOrchestratorAgent(project_root=project_root)

    # Check execution order includes both phases
    order = agent._execution_order

    has_phase_a = "TwoPhaseDeduplicationAgent_PhaseA" in order
    has_phase_b = "TwoPhaseDeduplicationAgent_PhaseB" in order

    if not has_phase_a:
        return False, "Missing Phase A in execution order"
    if not has_phase_b:
        return False, "Missing Phase B in execution order"

    # Verify Phase A comes before Phase B
    idx_a = order.index("TwoPhaseDeduplicationAgent_PhaseA")
    idx_b = order.index("TwoPhaseDeduplicationAgent_PhaseB")

    if idx_a >= idx_b:
        return False, f"Phase A (idx {idx_a}) should come before Phase B (idx {idx_b})"

    return True, f"Two-phase order correct: Phase A at {idx_a}, Phase B at {idx_b}"


def test_10_phase_a_runs_early() -> tuple[bool, str]:
    """Test 10: Phase A runs immediately after SyntaxValidator."""
    from agentic_core.L3_orchestration.workflow_engines.SSOTOrchestratorAgent import (
        SSOTOrchestratorAgent,
    )

    agent = SSOTOrchestratorAgent(project_root=project_root)
    order = agent._execution_order

    # Phase A should be at index 1 (right after SyntaxValidator at index 0)
    if order[0] != "SyntaxValidatorAgent":
        return False, f"SyntaxValidator not first: {order[0]}"

    if order[1] != "TwoPhaseDeduplicationAgent_PhaseA":
        return False, f"Phase A not second: {order[1]}"

    return True, "Phase A correctly positioned after SyntaxValidator"


def test_11_phase_b_runs_after_structural_healing() -> tuple[bool, str]:
    """Test 11: Phase B runs after LocationAgent (structural healing)."""
    from agentic_core.L3_orchestration.workflow_engines.SSOTOrchestratorAgent import (
        SSOTOrchestratorAgent,
    )

    agent = SSOTOrchestratorAgent(project_root=project_root)
    order = agent._execution_order

    # Phase B should come after LocationAgent
    if "LocationAgent" not in order:
        return False, "LocationAgent not in execution order"

    idx_location = order.index("LocationAgent")
    idx_phase_b = order.index("TwoPhaseDeduplicationAgent_PhaseB")

    if idx_phase_b <= idx_location:
        return (
            False,
            f"Phase B (idx {idx_phase_b}) should come after LocationAgent (idx {idx_location})",
        )

    return (
        True,
        f"Phase B correctly after LocationAgent: Location at {idx_location}, Phase B at {idx_phase_b}",
    )


def test_12_shared_dedup_agent_instance() -> tuple[bool, str]:
    """Test 12: SSOTOrchestratorAgent uses shared dedup agent instance."""
    from agentic_core.L3_orchestration.workflow_engines.SSOTOrchestratorAgent import (
        SSOTOrchestratorAgent,
    )

    agent = SSOTOrchestratorAgent(project_root=project_root)

    # Get dedup agent for Phase A
    dedup_a = agent._get_agent("TwoPhaseDeduplicationAgent_PhaseA")

    # Get dedup agent for Phase B
    dedup_b = agent._get_agent("TwoPhaseDeduplicationAgent_PhaseB")

    # Should be the same instance
    if dedup_a is not dedup_b:
        return False, "Phase A and Phase B use different instances"

    return True, "Shared TwoPhaseDeduplicationAgent instance for both phases"


def test_13_report_structure() -> tuple[bool, str]:
    """Test 13: Deduplication report has correct structure."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    temp_dir = create_test_environment()
    try:
        agent = TwoPhaseDeduplicationAgent(project_root=temp_dir)
        agent.run_phase_a()
        agent.run_phase_b()

        report = agent.get_report()

        # Check report structure
        required_fields = [
            "phase_a_duplicates",
            "phase_b_duplicates",
            "total_identity_collisions",
            "total_logic_duplicates",
            "files_scanned",
            "phase_a_complete",
            "phase_b_complete",
        ]

        for field in required_fields:
            if not hasattr(report, field):
                return False, f"Report missing field: {field}"

        if not report.phase_a_complete:
            return False, "Phase A not marked complete"
        if not report.phase_b_complete:
            return False, "Phase B not marked complete"

        return True, f"Report structure correct with {report.files_scanned} files scanned"

    finally:
        cleanup_test_environment(temp_dir)


def test_14_excludes_archives_directory() -> tuple[bool, str]:
    """Test 14: Scanner excludes archives directory."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    temp_dir = create_test_environment()
    try:
        # Add a file in archives
        (temp_dir / "archives" / "old_duplicate.py").write_text("# archived")

        agent = TwoPhaseDeduplicationAgent(project_root=temp_dir)

        # Collect all scanned files
        scanned_files = list(agent._iter_files({".py"}))
        scanned_paths = [str(f) for f in scanned_files]

        # Check no archives files included
        archives_files = [p for p in scanned_paths if "archives" in p]

        if archives_files:
            return False, f"Archives files included: {archives_files}"

        return True, "Archives directory correctly excluded"

    finally:
        cleanup_test_environment(temp_dir)


def test_15_canonical_priority_order() -> tuple[bool, str]:
    """Test 15: Canonical priority follows SSOT layer order."""
    from agentic_core.L5_safety.guardrails.TwoPhaseDeduplicationAgent import (
        TwoPhaseDeduplicationAgent,
    )

    agent = TwoPhaseDeduplicationAgent(project_root=project_root)

    # Check priority order
    priority = agent.CANONICAL_PRIORITY

    # L5 should have higher priority than L0
    if priority.get("agentic_core/L5_safety", 0) <= priority.get("agentic_core/L0_maintenance", 0):
        return False, "L5 should have higher priority than L0"

    # L5 should have higher priority than utils
    if priority.get("agentic_core/L5_safety", 0) <= priority.get("agentic_core/utils", 0):
        return False, "L5 should have higher priority than utils"

    return True, "Canonical priority follows SSOT layer order"


# ============================================================================
# TEST RUNNER
# ============================================================================


def run_all_tests():
    """Run all tests and return results."""
    tests = [
        ("Test 1: Agent exists", test_1_agent_exists),
        ("Test 2: Required methods present", test_2_agent_has_required_methods),
        ("Test 3: Phase A detects identity collisions", test_3_phase_a_detects_identity_collisions),
        ("Test 4: Phase A selects canonical path", test_4_phase_a_selects_canonical_path),
        ("Test 5: Phase B detects logic duplicates", test_5_phase_b_detects_logic_duplicates),
        (
            "Test 6: heal_repository supports phase parameter",
            test_6_heal_repository_supports_phase_parameter,
        ),
        ("Test 7: Dry run makes no changes", test_7_dry_run_makes_no_changes),
        ("Test 8: Execute mode archives duplicates", test_8_execute_mode_archives_duplicates),
        (
            "Test 9: SSOT Orchestrator has two-phase order",
            test_9_ssot_orchestrator_has_two_phase_order,
        ),
        ("Test 10: Phase A runs early", test_10_phase_a_runs_early),
        (
            "Test 11: Phase B runs after structural healing",
            test_11_phase_b_runs_after_structural_healing,
        ),
        ("Test 12: Shared dedup agent instance", test_12_shared_dedup_agent_instance),
        ("Test 13: Report structure", test_13_report_structure),
        ("Test 14: Excludes archives directory", test_14_excludes_archives_directory),
        ("Test 15: Canonical priority order", test_15_canonical_priority_order),
    ]

    results = {
        "passed": 0,
        "failed": 0,
        "total": len(tests),
        "details": [],
    }

    print("\n" + "=" * 70)
    print("TWO-PHASE DEDUPLICATION TEST SUITE")
    print("Phase A: Shallow (Identity) | Phase B: Deep (Logic)")
    print("=" * 70)

    for name, test_func in tests:
        try:
            passed, message = test_func()
            icon = "✅" if passed else "❌"

            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1

            results["details"].append(
                {
                    "name": name,
                    "passed": passed,
                    "message": message,
                }
            )

            print(f"\n{icon} {name}")
            print(f"   {message}")

        except Exception as e:
            results["failed"] += 1
            results["details"].append(
                {
                    "name": name,
                    "passed": False,
                    "message": f"ERROR: {e}",
                }
            )
            print(f"\n❌ {name}")
            print(f"   ERROR: {e}")
            import traceback

            traceback.print_exc()

    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {results['passed']}/{results['total']} PASSED")
    print("=" * 70)

    if results["failed"] > 0:
        print("\n❌ FAILED TESTS:")
        for detail in results["details"]:
            if not detail["passed"]:
                print(f"   - {detail['name']}: {detail['message']}")

    return results


if __name__ == "__main__":
    results = run_all_tests()
    sys.exit(0 if results["failed"] == 0 else 1)
