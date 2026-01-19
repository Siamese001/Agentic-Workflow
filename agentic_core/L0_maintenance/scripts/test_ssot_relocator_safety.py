"""
Test script to verify SSOTRelocator safety blocks.

Tests:
1. Protected path whitelist (knowledge, coordinators, L0_maintenance)
2. Active dependency scanning
3. Dry-run mode validation
"""
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from archives.location_violations.ssot_relocator import SSOTRelocator


def test_protected_paths():
    """Test that protected paths are blocked from archival."""
    print("\n" + "="*70)
    print("TEST 1: Protected Path Whitelist")
    print("="*70)
    
    relocator = SSOTRelocator(project_root=project_root, dry_run=True)
    
    # Test cases: paths that should be blocked
    protected_test_cases = [
        project_root / "agentic_core" / "knowledge",
        project_root / "agentic_core" / "L3_orchestration" / "coordinators",
        project_root / "agentic_core" / "L0_maintenance",
        project_root / "agentic_core" / "bases",
    ]
    
    results = []
    for test_path in protected_test_cases:
        archive_path = project_root / "archives" / "test" / test_path.name
        result = relocator._relocate_folder(
            source=test_path,
            target=archive_path,
            action='ARCHIVED'
        )
        
        is_blocked = result.action == 'BLOCKED'
        status = "✅ BLOCKED" if is_blocked else "❌ NOT BLOCKED"
        print(f"{status}: {test_path.name}")
        print(f"   Action: {result.action}")
        print(f"   Error: {result.error}")
        results.append(is_blocked)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Protection Rate: {success_rate:.1f}% ({sum(results)}/{len(results)} blocked)")
    
    return all(results)


def test_active_dependency_scan():
    """Test that folders with active imports are blocked."""
    print("\n" + "="*70)
    print("TEST 2: Active Dependency Scanning")
    print("="*70)
    
    relocator = SSOTRelocator(project_root=project_root, dry_run=True)
    
    # Test cases: modules that should have active imports
    active_modules = [
        "knowledge",
        "coordinators",
        "strategic_recommendation",
    ]
    
    results = []
    for module in active_modules:
        has_deps = relocator._is_active_dependency(module)
        status = "✅ DETECTED" if has_deps else "❌ NOT DETECTED"
        print(f"{status}: {module} has active imports")
        results.append(has_deps)
    
    detection_rate = sum(results) / len(results) * 100
    print(f"\n📊 Detection Rate: {detection_rate:.1f}% ({sum(results)}/{len(results)} detected)")
    
    return all(results)


def test_dry_run_mode():
    """Test that dry-run mode prevents actual operations."""
    print("\n" + "="*70)
    print("TEST 3: Dry-Run Mode Validation")
    print("="*70)
    
    relocator = SSOTRelocator(project_root=project_root, dry_run=True)
    
    # Create a temporary test folder (safe to test with)
    test_folder = project_root / "temp_test_folder_for_ssot"
    test_folder.mkdir(exist_ok=True)
    (test_folder / "test.txt").write_text("test content")
    
    archive_path = project_root / "archives" / "test" / "temp_test_folder_for_ssot"
    
    result = relocator._relocate_folder(
        source=test_folder,
        target=archive_path,
        action='ARCHIVED'
    )
    
    # Check that folder still exists (dry-run didn't move it)
    still_exists = test_folder.exists()
    is_dry_run = "(DRY-RUN)" in result.action or result.action == 'BLOCKED'
    
    # Cleanup
    if test_folder.exists():
        (test_folder / "test.txt").unlink()
        test_folder.rmdir()
    
    status = "✅ PASSED" if (still_exists and is_dry_run) else "❌ FAILED"
    print(f"{status}: Dry-run mode preserved original folder")
    print(f"   Folder still exists: {still_exists}")
    print(f"   Action was dry-run: {is_dry_run}")
    print(f"   Result action: {result.action}")
    
    return still_exists and is_dry_run


def test_knowledge_folder_protection():
    """Comprehensive test specifically for knowledge/ folder protection."""
    print("\n" + "="*70)
    print("TEST 4: Knowledge Folder Comprehensive Protection")
    print("="*70)
    
    relocator = SSOTRelocator(project_root=project_root, dry_run=True)
    
    knowledge_path = project_root / "agentic_core" / "knowledge"
    archive_path = project_root / "archives" / "test" / "knowledge"
    
    # Test 1: Whitelist protection
    result = relocator._relocate_folder(
        source=knowledge_path,
        target=archive_path,
        action='ARCHIVED'
    )
    
    whitelist_blocked = result.action == 'BLOCKED' and 'Protected' in result.error
    print(f"{'✅' if whitelist_blocked else '❌'} Whitelist Protection: {result.error}")
    
    # Test 2: Active dependency detection
    has_active_deps = relocator._is_active_dependency("knowledge")
    print(f"{'✅' if has_active_deps else '❌'} Active Dependencies Detected: {has_active_deps}")
    
    # Test 3: Folder still exists
    still_exists = knowledge_path.exists()
    print(f"{'✅' if still_exists else '❌'} Folder Still Exists: {still_exists}")
    
    all_passed = whitelist_blocked and has_active_deps and still_exists
    print(f"\n📊 Knowledge Folder Protection: {'✅ FULLY PROTECTED' if all_passed else '❌ VULNERABLE'}")
    
    return all_passed


def main():
    """Run all safety verification tests."""
    print("\n" + "="*70)
    print("SSOT Relocator Safety Verification Suite")
    print("="*70)
    
    tests = [
        ("Protected Path Whitelist", test_protected_paths),
        ("Active Dependency Scanning", test_active_dependency_scan),
        ("Dry-Run Mode Validation", test_dry_run_mode),
        ("Knowledge Folder Protection", test_knowledge_folder_protection),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    success_rate = total_passed / total_tests * 100
    
    print(f"\n📊 Overall Success Rate: {success_rate:.1f}% ({total_passed}/{total_tests} tests passed)")
    
    if all(results.values()):
        print("\n✅ ALL SAFETY CHECKS PASSED - SSOTRelocator is properly hardened")
        return 0
    else:
        print("\n❌ SOME SAFETY CHECKS FAILED - Review implementation")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
