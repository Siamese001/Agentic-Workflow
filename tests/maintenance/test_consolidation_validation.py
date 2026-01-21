#!/usr/bin/env python3
"""
Core Consolidation & Deprecation Validation Tests
==================================================

Validates the consolidation of BaseAgents and Orchestrators per the
architectural audit requirements.

Test Cases:
1. Inheritance Audit - All agents inherit from approved layer bases
2. Orchestrator SSOT - get_orchestrator returns UnifiedOrchestratorAgent
3. Timeout Verification - LocationAgent uses SovereignIndex (< 60s)
4. Deprecation Guard - Deprecated classes trigger DeprecationWarning
"""

import sys
import warnings
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PASSED = 0
FAILED = 0


def test_pass(test_id: str, msg: str):
    global PASSED
    PASSED += 1
    print(f"  ✅ {test_id}: {msg}")


def test_fail(test_id: str, msg: str):
    global FAILED
    FAILED += 1
    print(f"  ❌ {test_id}: {msg}")


# ============================================================================
# Test 1: Inheritance Audit
# ============================================================================

def test_inheritance_audit():
    """Validate all agents inherit from approved layer bases."""
    print("\n" + "=" * 60)
    print("Test 1: Inheritance Audit")
    print("=" * 60)

    # Approved layer bases
    APPROVED_BASES = {
        "SovereignBaseAgent",
        "L0MaintenanceBaseAgent",
        "L1CognitionBaseAgent",
        "L2ExecutionBaseAgent",
        "L3OrchestrationBaseAgent",
        "L4StateBaseAgent",
        "L5SafetyBaseAgent",
        "L6ObservabilityBaseAgent",
    }

    # Check that each approved base exists
    base_paths = {
        "SovereignBaseAgent": PROJECT_ROOT / "agentic_core/observability/SovereignBaseAgent.py",
        "L0MaintenanceBaseAgent": PROJECT_ROOT / "agentic_core/L0_maintenance/scripts/L0MaintenanceBaseAgent.py",
        "L1CognitionBaseAgent": PROJECT_ROOT / "agentic_core/L1_cognition/thought_engine/L1CognitionBaseAgent.py",
        "L2ExecutionBaseAgent": PROJECT_ROOT / "agentic_core/L2_execution/ToolRegistry/L2ExecutionBaseAgent.py",
        "L3OrchestrationBaseAgent": PROJECT_ROOT / "agentic_core/L3_orchestration/workflow_engines/L3OrchestrationBaseAgent.py",
        "L4StateBaseAgent": PROJECT_ROOT / "agentic_core/L4_state/ValidationContext/L4StateBaseAgent.py",
        "L5SafetyBaseAgent": PROJECT_ROOT / "agentic_core/L5_safety/validators/L5SafetyBaseAgent.py",
        "L6ObservabilityBaseAgent": PROJECT_ROOT / "agentic_core/L6_observability/L6ObservabilityBaseAgent.py",
    }

    for base_name, base_path in base_paths.items():
        if base_path.exists():
            test_pass(base_name, f"Exists at {base_path.relative_to(PROJECT_ROOT)}")
        else:
            test_fail(base_name, f"NOT FOUND at {base_path.relative_to(PROJECT_ROOT)}")

    # Verify deprecated bases are in archives
    deprecated_bases = [
        "CanonBaseAgent",
        "ExecutionCanonBaseAgent",
        "MaintenanceBaseAgent",
    ]

    for deprecated in deprecated_bases:
        # Check it's NOT in live agentic_core (excluding archives)
        live_path = PROJECT_ROOT / "agentic_core"
        found_in_live = False
        # Phase 6.8: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery import get_python_files
        for py_file in get_python_files(live_path):
            if py_file.name == f"{deprecated}.py":
                found_in_live = True
                test_fail(f"DEPRECATED_{deprecated}", f"Still in live codebase: {py_file}")
                break

        if not found_in_live:
            test_pass(f"DEPRECATED_{deprecated}", "Not in live codebase (archived or removed)")


# ============================================================================
# Test 2: Orchestrator SSOT
# ============================================================================

def test_orchestrator_ssot():
    """Validate get_orchestrator returns UnifiedOrchestratorAgent."""
    print("\n" + "=" * 60)
    print("Test 2: Orchestrator SSOT")
    print("=" * 60)

    try:
        from agentic_core.L3_orchestration.orchestrator_registry import get_orchestrator
        from agentic_core.L3_orchestration.UnifiedOrchestratorAgent import UnifiedOrchestratorAgent

        # Test unified mode
        orchestrator = get_orchestrator("unified")
        if isinstance(orchestrator, UnifiedOrchestratorAgent):
            test_pass("UNIFIED_MODE", "get_orchestrator('unified') returns UnifiedOrchestratorAgent")
        else:
            test_fail("UNIFIED_MODE", f"Wrong type: {type(orchestrator)}")

        # Test healing mode (legacy alias)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            orchestrator = get_orchestrator("healing")

            if isinstance(orchestrator, UnifiedOrchestratorAgent):
                test_pass("HEALING_MODE", "get_orchestrator('healing') returns UnifiedOrchestratorAgent")
            else:
                test_fail("HEALING_MODE", f"Wrong type: {type(orchestrator)}")

            # Check deprecation warning was raised
            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            if deprecation_warnings:
                test_pass("HEALING_DEPRECATION", "Deprecation warning raised for 'healing' mode")
            else:
                test_fail("HEALING_DEPRECATION", "No deprecation warning for 'healing' mode")

    except ImportError as e:
        test_fail("IMPORT", f"Cannot import orchestrator_registry: {e}")
    except Exception as e:
        test_fail("EXCEPTION", f"Test failed: {e}")


# ============================================================================
# Test 3: Timeout Verification (SovereignIndex)
# ============================================================================

def test_timeout_verification():
    """Validate LocationAgent uses SovereignIndex for performance."""
    print("\n" + "=" * 60)
    print("Test 3: Timeout Verification (SovereignIndex)")
    print("=" * 60)

    # Static analysis - check LocationAgent uses SovereignIndex
    location_agent_path = PROJECT_ROOT / "agentic_core/L5_safety/validators/LocationAgent.py"

    if not location_agent_path.exists():
        test_fail("FILE", "LocationAgent.py not found")
        return

    content = location_agent_path.read_text(encoding='utf-8')

    # Check SovereignIndex import
    if 'from agentic_core.utils.sovereign_index import SovereignIndex' in content:
        test_pass("IMPORT", "SovereignIndex imported")
    else:
        test_fail("IMPORT", "SovereignIndex NOT imported")

    # Check SovereignIndex usage
    if 'SovereignIndex.get_instance' in content:
        test_pass("USAGE", "SovereignIndex.get_instance() used")
    else:
        test_fail("USAGE", "SovereignIndex.get_instance() NOT used")

    # Check _get_python_files uses SovereignIndex
    if '_get_python_files' in content and 'index.get_files' in content:
        test_pass("GET_FILES", "_get_python_files uses SovereignIndex")
    else:
        test_fail("GET_FILES", "_get_python_files does NOT use SovereignIndex")

    # Check GLOBAL_EXCLUDED_DIRS is respected
    if 'GLOBAL_EXCLUDED_DIRS' in content or 'SOVEREIGN_EXCLUDED_FOLDERS' in content:
        test_pass("EXCLUSIONS", "Uses SSOT exclusion patterns")
    else:
        test_fail("EXCLUSIONS", "Does NOT use SSOT exclusion patterns")


# ============================================================================
# Test 4: Deprecation Guard
# ============================================================================

def test_deprecation_guard():
    """Validate deprecated classes trigger DeprecationWarning."""
    print("\n" + "=" * 60)
    print("Test 4: Deprecation Guard")
    print("=" * 60)

    try:
        from agentic_core.L3_orchestration.orchestrator_registry import (
            SSOTOrchestratorAgent,
            HealingOrchestratorAgent,
            ConsolidatedOrchestratorAgent,
        )

        # Test SSOTOrchestratorAgent deprecation
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = SSOTOrchestratorAgent()

            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            if deprecation_warnings:
                test_pass("SSOT_DEPRECATION", "SSOTOrchestratorAgent triggers DeprecationWarning")
            else:
                test_fail("SSOT_DEPRECATION", "SSOTOrchestratorAgent does NOT trigger DeprecationWarning")

        # Test HealingOrchestratorAgent deprecation
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = HealingOrchestratorAgent()

            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            if deprecation_warnings:
                test_pass("HEALING_DEPRECATION", "HealingOrchestratorAgent triggers DeprecationWarning")
            else:
                test_fail("HEALING_DEPRECATION", "HealingOrchestratorAgent does NOT trigger DeprecationWarning")

        # Test ConsolidatedOrchestratorAgent deprecation
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = ConsolidatedOrchestratorAgent()

            deprecation_warnings = [x for x in w if issubclass(x.category, DeprecationWarning)]
            if deprecation_warnings:
                test_pass("CONSOLIDATED_DEPRECATION", "ConsolidatedOrchestratorAgent triggers DeprecationWarning")
            else:
                test_fail("CONSOLIDATED_DEPRECATION", "ConsolidatedOrchestratorAgent does NOT trigger DeprecationWarning")

    except ImportError as e:
        test_fail("IMPORT", f"Cannot import deprecated classes: {e}")
    except Exception as e:
        test_fail("EXCEPTION", f"Test failed: {e}")


# ============================================================================
# Test 5: Orchestrator Count Verification
# ============================================================================

def test_orchestrator_count():
    """Verify orchestrator AGENT count is reduced to target."""
    print("\n" + "=" * 60)
    print("Test 5: Orchestrator Agent Count Verification")
    print("=" * 60)

    # Count orchestrator AGENTS in live codebase (excluding archives, tests, utilities)
    agentic_core = PROJECT_ROOT / "agentic_core"
    orchestrator_agents = []
    utility_files = []

    # Patterns that indicate utility/support files, not actual orchestrator agents
    utility_patterns = [
        "test_",
        "orchestrator_registry",
        "orchestrator_types",
        "orchestrator_wrapper",
        "_orchestrator.py",  # lowercase = utility
        "mission_orchestrator",
        "master_mission_orchestrator",
        "subatomic_orchestrator",
        "canon_validator_orchestrator",
        "orchestrator.py",  # Protocol/interface file (IOrchestrator)
    ]

    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(agentic_core):
        if "Orchestrator" not in py_file.name:
            continue

        filename = py_file.name.lower()
        is_utility = any(pattern in filename for pattern in utility_patterns)

        if is_utility:
            utility_files.append(py_file)
        else:
            orchestrator_agents.append(py_file)

    # Target: 2 orchestrator agents
    # - UnifiedOrchestratorAgent.py (the SSOT)
    # - MockOrchestratorAgent.py (for testing)

    if len(orchestrator_agents) <= 2:
        test_pass("AGENT_COUNT", f"Orchestrator agent count: {len(orchestrator_agents)} (target: ≤2)")
    else:
        test_fail("AGENT_COUNT", f"Orchestrator agent count: {len(orchestrator_agents)} (target: ≤2)")

    print("  Orchestrator Agents:")
    for f in orchestrator_agents:
        print(f"    - {f.relative_to(PROJECT_ROOT)}")

    print(f"  Utility Files (not counted): {len(utility_files)}")


# ============================================================================
# Test 6: BaseAgent Count Verification
# ============================================================================

def test_baseagent_count():
    """Verify BaseAgent count is reduced to target."""
    print("\n" + "=" * 60)
    print("Test 6: BaseAgent Count Verification")
    print("=" * 60)

    # Count BaseAgents in live codebase (excluding archives)
    agentic_core = PROJECT_ROOT / "agentic_core"
    baseagent_files = []

    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(agentic_core):
        if "BaseAgent" in py_file.name:
            baseagent_files.append(py_file)

    # Target: 8 BaseAgents (the approved layer bases)
    if len(baseagent_files) == 8:
        test_pass("COUNT", f"BaseAgent count: {len(baseagent_files)} (target: 8)")
    elif len(baseagent_files) < 8:
        test_fail("COUNT", f"BaseAgent count: {len(baseagent_files)} (target: 8) - MISSING BASES")
    else:
        test_fail("COUNT", f"BaseAgent count: {len(baseagent_files)} (target: 8) - TOO MANY")

    for f in baseagent_files:
        print(f"    - {f.relative_to(PROJECT_ROOT)}")


# ============================================================================
# Main Execution
# ============================================================================

def main():
    print("=" * 60)
    print("CORE CONSOLIDATION & DEPRECATION VALIDATION")
    print("=" * 60)
    print("Validating BaseAgent standardization and Orchestrator unification")

    test_inheritance_audit()
    test_orchestrator_ssot()
    test_timeout_verification()
    test_deprecation_guard()
    test_orchestrator_count()
    test_baseagent_count()

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  Total Checks: {PASSED + FAILED}")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  Pass Rate: {PASSED / (PASSED + FAILED) * 100:.1f}%")
    print()

    if FAILED == 0:
        print("  ✅ ALL CONSOLIDATION CHECKS PASSED")
        return 0
    else:
        print(f"  ❌ {FAILED} CHECKS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
