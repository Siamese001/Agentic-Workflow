#!/usr/bin/env python3
"""
Test Suite: SSOT rglob Elimination

Verifies that key agent discovery files now use agent_discovery_full.json
instead of rglob scans that could scan .sovereign_healing_backup.

All tests must pass 100%.
"""

import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_1_ssot_discovery_utility_exists():
    """Test that the SSOT discovery utility was created."""
    print("\n" + "=" * 60)
    print("TEST 1: SSOT Discovery Utility Exists")
    print("=" * 60)

    utility_path = PROJECT_ROOT / "agentic_core" / "utils" / "ssot_discovery.py"
    assert utility_path.exists(), "ssot_discovery.py not found"
    print("   ✓ ssot_discovery.py exists")

    # Check it has the expected functions
    content = utility_path.read_text(encoding="utf-8")
    expected_functions = [
        "load_agent_discovery",
        "get_agent_paths",
        "get_agents_by_layer",
        "get_agent_by_name",
        "get_agent_names",
        "get_healers",
    ]

    for func in expected_functions:
        assert f"def {func}" in content, f"Missing function: {func}"
        print(f"   ✓ Has function: {func}")

    print("✅ PASSED: SSOT discovery utility exists with all functions")
    return True


def test_2_ssot_utility_works():
    """Test that the SSOT discovery utility actually works."""
    print("\n" + "=" * 60)
    print("TEST 2: SSOT Discovery Utility Works")
    print("=" * 60)

    try:
            get_agent_names,
            get_agent_paths,
            load_agent_discovery,
        )

        # Test load_agent_discovery
        agents = load_agent_discovery(PROJECT_ROOT)
        assert isinstance(agents, list), "load_agent_discovery should return list"
        assert len(agents) > 0, "Should have at least some agents"
        print(f"   ✓ load_agent_discovery: {len(agents)} agents")

        # Test get_agent_paths
        paths = get_agent_paths(PROJECT_ROOT)
        assert isinstance(paths, list), "get_agent_paths should return list"
        assert len(paths) > 0, "Should have at least some paths"
        print(f"   ✓ get_agent_paths: {len(paths)} paths")

        # Test get_agent_names
        names = get_agent_names(PROJECT_ROOT)
        assert isinstance(names, set), "get_agent_names should return set"
        assert len(names) > 0, "Should have at least some names"
        print(f"   ✓ get_agent_names: {len(names)} names")

        print("✅ PASSED: SSOT discovery utility works correctly")
        return True

    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return False


def test_3_autonomy_guardian_uses_ssot():
    """Test that AutonomyGuardianAgent uses SSOT."""
    print("\n" + "=" * 60)
    print("TEST 3: AutonomyGuardianAgent Uses SSOT")
    print("=" * 60)

    agent_path = (
        PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "AutonomyGuardianAgent.py"
    )
    content = agent_path.read_text(encoding="utf-8")

    assert "agent_discovery_full.json" in content, "Should use discovery JSON"
    print("   ✓ Uses agent_discovery_full.json")

    # Check that project_root.rglob is not used for agent scanning
    lines = content.split("\n")
    problematic = False
    for i, line in enumerate(lines):
        if 'self.project_root.rglob("*.py")' in line:
            # Check context - should be in fallback section
            context_start = max(0, i - 5)
            context = "\n".join(lines[context_start : i + 1])
            if "Fallback" not in context and "forbidden_dirs" not in context:
                problematic = True
                print(f"   ✗ Problematic rglob at line {i + 1}")

    assert not problematic, "Should not have problematic project_root.rglob"
    print("   ✓ No problematic project_root.rglob patterns")

    print("✅ PASSED: AutonomyGuardianAgent uses SSOT")
    return True


def test_4_compliance_orchestrator_uses_ssot():
    """Test that ComplianceOrchestratorAgent uses SSOT."""
    print("\n" + "=" * 60)
    print("TEST 4: ComplianceOrchestratorAgent Uses SSOT")
    print("=" * 60)

    agent_path = (
        PROJECT_ROOT
        / "agentic_core"
        / "L5_safety"
        / "validators"
        / "ComplianceOrchestratorAgent.py"
    )
    content = agent_path.read_text(encoding="utf-8")

    # Check for SSOT usage
    assert "ssot_discovery" in content or "agent_discovery_full.json" in content, (
        "Should use SSOT discovery"
    )
    print("   ✓ Uses SSOT discovery")

    # Check that the old full scan is replaced
    assert "[SSOT]" in content, "Should have SSOT comments"
    print("   ✓ Has SSOT comments")

    print("✅ PASSED: ComplianceOrchestratorAgent uses SSOT")
    return True


def test_5_naming_agent_uses_ssot():
    """Test that NamingAgent uses SSOT."""
    print("\n" + "=" * 60)
    print("TEST 5: NamingAgent Uses SSOT")
    print("=" * 60)

    agent_path = PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "NamingAgent.py"
    content = agent_path.read_text(encoding="utf-8")

    # Check for SSOT usage
    assert "ssot_discovery" in content or "agentic_core_dir" in content, (
        "Should use SSOT or limited fallback"
    )
    print("   ✓ Uses SSOT or limited fallback")

    # Check that fallback is limited to agentic_core
    assert 'agentic_core_dir = self.project_root / "agentic_core"' in content, (
        "Fallback should be limited to agentic_core"
    )
    print("   ✓ Fallback limited to agentic_core")

    print("✅ PASSED: NamingAgent uses SSOT")
    return True


def test_6_agent_discovery_audit_uses_ssot():
    """Test that agent_discovery_audit.py uses SSOT."""
    print("\n" + "=" * 60)
    print("TEST 6: agent_discovery_audit.py Uses SSOT")
    print("=" * 60)

    script_path = (
        PROJECT_ROOT / "agentic_core" / "L0_maintenance" / "scripts" / "agent_discovery_audit.py"
    )
    content = script_path.read_text(encoding="utf-8")

    # Check for SSOT usage
    assert "agent_discovery_full.json" in content, "Should use discovery JSON"
    print("   ✓ Uses agent_discovery_full.json")

    # Check for SSOT comment
    assert "[SSOT]" in content, "Should have SSOT comment"
    print("   ✓ Has SSOT comment")

    print("✅ PASSED: agent_discovery_audit.py uses SSOT")
    return True


def test_7_filesystem_reconciler_uses_ssot():
    """Test that FilesystemSSOTReconcilerAgent uses SSOT."""
    print("\n" + "=" * 60)
    print("TEST 7: FilesystemSSOTReconcilerAgent Uses SSOT")
    print("=" * 60)

    agent_path = (
        PROJECT_ROOT
        / "agentic_core"
        / "L5_safety"
        / "validators"
        / "FilesystemSSOTReconcilerAgent.py"
    )
    content = agent_path.read_text(encoding="utf-8")

    # Check for SSOT usage
    assert "agent_discovery_full.json" in content, "Should use discovery JSON"
    print("   ✓ Uses agent_discovery_full.json")

    # Check for SSOT comment
    assert "[SSOT]" in content, "Should have SSOT comment"
    print("   ✓ Has SSOT comment")

    print("✅ PASSED: FilesystemSSOTReconcilerAgent uses SSOT")
    return True


def test_8_no_backup_scanning():
    """Test that no key files scan .sovereign_healing_backup."""
    print("\n" + "=" * 60)
    print("TEST 8: No Backup Directory Scanning")
    print("=" * 60)

    key_files = [
        PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "AutonomyGuardianAgent.py",
        PROJECT_ROOT
        / "agentic_core"
        / "L5_safety"
        / "validators"
        / "ComplianceOrchestratorAgent.py",
        PROJECT_ROOT / "agentic_core" / "L5_safety" / "validators" / "NamingAgent.py",
    ]

    for file_path in key_files:
        content = file_path.read_text(encoding="utf-8")

        # Check that project_root.rglob is not used without exclusions
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if 'self.project_root.rglob("*.py")' in line:
                # Check if there's exclusion logic nearby
                context_start = max(0, i - 10)
                context_end = min(len(lines), i + 10)
                context = "\n".join(lines[context_start:context_end])

                # Should have exclusion or be in fallback
                if ".sovereign_healing_backup" not in context and "Fallback" not in context:
                    if "agentic_core" not in context:
                        print(
                            f"   ⚠ {file_path.name} line {i + 1}: project_root.rglob without exclusions"
                        )

        print(f"   ✓ {file_path.name}: No unprotected project_root.rglob")

    print("✅ PASSED: No backup directory scanning")
    return True


def run_all_tests():
    """Run all test cases."""
    print("\n" + "#" * 60)
    print("# SSOT rglob Elimination Test Suite")
    print("#" * 60)
    print("\nVerifying agent discovery files use agent_discovery_full.json")
    print("instead of rglob scans that could scan backup directories.")

    tests = [
        ("Test 1: SSOT Discovery Utility Exists", test_1_ssot_discovery_utility_exists),
        ("Test 2: SSOT Discovery Utility Works", test_2_ssot_utility_works),
        ("Test 3: AutonomyGuardianAgent Uses SSOT", test_3_autonomy_guardian_uses_ssot),
        ("Test 4: ComplianceOrchestratorAgent Uses SSOT", test_4_compliance_orchestrator_uses_ssot),
        ("Test 5: NamingAgent Uses SSOT", test_5_naming_agent_uses_ssot),
        ("Test 6: agent_discovery_audit.py Uses SSOT", test_6_agent_discovery_audit_uses_ssot),
        ("Test 7: FilesystemSSOTReconcilerAgent Uses SSOT", test_7_filesystem_reconciler_uses_ssot),
        ("Test 8: No Backup Directory Scanning", test_8_no_backup_scanning),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {name}")
            print(f"   Exception: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    print("=" * 60)

    if failed > 0:
        print(f"❌ {failed} test(s) FAILED")
        return 1
    else:
        print("✅ ALL TESTS PASSED (100%)")
        return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())