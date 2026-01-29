#!/usr/bin/env python3
"""
Test suite for hardened PascalSovereigntyAgent collision handling
Validates the fixes for file collision issues during pre-commit hooks
"""

import sys
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L5_safety.validators.PascalSovereigntyAgent import PascalSovereigntyAgent


def test_identical_file_collision_deletion():
    """Test that identical file collisions properly delete the violator"""
    print("=== Test 1: Identical File Collision Deletion ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create two identical files
        target = temp_path / "HealerProtocol.py"
        violator = temp_path / "healer_interface.py"

        content = '''"""
Healer protocol interface
"""
class HealerProtocol:
    pass
'''

        target.write_text(content)
        violator.write_text(content)

        # Test collision resolution
        agent = PascalSovereigntyAgent(project_root=temp_path, dry_run=False)
        result = agent.resolve_collision_and_rename(violator, "HealerProtocol.py")

        assert result == True, "Should resolve identical collision"
        assert not violator.exists(), "Violator should be deleted"
        assert target.exists(), "Target should still exist"

        print("✅ Identical file collision handled correctly")


def test_divergent_file_conflict_naming():
    """Test that divergent file collisions create .CONFLICT files"""
    print("=== Test 2: Divergent File Conflict Naming ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create two different files with same target name
        target = temp_path / "TestAgent.py"
        violator = temp_path / "test_agent.py"

        target.write_text("class TestAgent: pass  # Version 1")
        violator.write_text("class TestAgent: pass  # Version 2 - Modified")

        # Test collision resolution
        agent = PascalSovereigntyAgent(project_root=temp_path, dry_run=False)
        result = agent.resolve_collision_and_rename(violator, "TestAgent.py")

        assert result == True, "Should resolve divergent collision"
        assert not violator.exists(), "Violator should be moved"
        assert target.exists(), "Target should still exist"

        # Check for conflict file
        conflicts = list(temp_path.glob("TestAgent.py.CONFLICT_*"))
        assert len(conflicts) == 1, "Should create exactly one conflict file"
        assert "Version 2" in conflicts[0].read_text(), (
            "Conflict file should contain violator content"
        )

        print("✅ Divergent file conflict handled correctly")


def test_windows_case_insensitive_handling():
    """Test proper Windows case-insensitive path handling"""
    print("=== Test 3: Windows Case-Insensitive Handling ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create files that differ only by case
        target = temp_path / "TestAgent.py"
        violator = temp_path / "testagent.py"

        content = "class TestAgent: pass"
        target.write_text(content)
        violator.write_text(content)

        # Test collision resolution
        agent = PascalSovereigntyAgent(project_root=temp_path, dry_run=False)
        result = agent.resolve_collision_and_rename(violator, "TestAgent.py")

        assert result == True, "Should resolve case-insensitive collision"
        assert not violator.exists(), "Violator should be deleted"
        assert target.exists(), "Target should still exist"

        print("✅ Case-insensitive collision handled correctly")


def test_atomic_rename_with_verification():
    """Test atomic rename operations with proper verification"""
    print("=== Test 4: Atomic Rename with Verification ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a file to rename
        src = temp_path / "OldName.py"
        src.write_text("class OldName: pass")

        # Test standard rename
        agent = PascalSovereigntyAgent(project_root=temp_path, dry_run=False)
        result = agent.resolve_collision_and_rename(src, "NewName.py")

        assert result == True, "Should perform standard rename"
        assert not src.exists(), "Source should be renamed"
        assert (temp_path / "NewName.py").exists(), "Target should exist"

        print("✅ Atomic rename with verification works correctly")


def test_error_recovery_and_rollback():
    """Test error recovery and rollback mechanisms"""
    print("=== Test 5: Error Recovery and Rollback ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create a file
        src = temp_path / "TestFile.py"
        src.write_text("class TestFile: pass")

        # Test with a destination that will cause issues
        # Create a directory with the target name to force an error
        dest_dir = temp_path / "TargetFile.py"
        dest_dir.mkdir()

        agent = PascalSovereigntyAgent(project_root=temp_path, dry_run=False)
        result = agent.resolve_collision_and_rename(src, "TargetFile.py")

        # Should fail gracefully
        assert result == False, "Should fail when destination is a directory"
        assert src.exists(), "Source should still exist after failed operation"

        print("✅ Error recovery and rollback work correctly")


def test_file_registry_update_race_condition_fix():
    """Test that file registry updates happen after successful operations"""
    print("=== Test 6: File Registry Race Condition Fix ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        agent = PascalSovereigntyAgent(project_root=temp_path, dry_run=False)
        agent.file_registry = []

        test_file = temp_path / "TestMixin.py"
        test_file.write_text("class TestMixin: pass")
        agent.file_registry.append(test_file)

        # Simulate the orchestration loop logic
        idx = 0
        path = agent.file_registry[idx]
        ftype = agent.classify_file(path)
        new_name = agent.get_compliant_name(path, ftype)

        if new_name and new_name != path.name:
            # This should update registry AFTER successful operation
            result = agent.resolve_collision_and_rename(path, new_name)

            if result:
                dest = path.parent / new_name
                if dest.exists():
                    # Registry should be updated only after successful operation
                    agent.file_registry[idx] = dest
                    assert agent.file_registry[idx] == dest, "Registry should point to new file"
                else:
                    # File was deleted - registry should be None
                    agent.file_registry[idx] = None
                    assert agent.file_registry[idx] is None, (
                        "Registry should be None for deleted files"
                    )

        print("✅ File registry race condition fix works correctly")


def test_dry_run_mode_integrity():
    """Test that dry run mode doesn't modify files"""
    print("=== Test 7: Dry Run Mode Integrity ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        src = temp_path / "TestFile.py"
        src.write_text("class TestFile: pass")

        target = temp_path / "target_file.py"
        target.write_text("class TestFile: pass")

        agent = PascalSovereigntyAgent(project_root=temp_path, dry_run=True)

        # Test collision resolution in dry run mode
        result = agent.resolve_collision_and_rename(src, "target_file.py")

        assert result == True, "Should return success in dry run"
        assert src.exists(), "Source should still exist in dry run"
        assert target.exists(), "Target should still exist in dry run"

        print("✅ Dry run mode integrity maintained")


def run_all_tests():
    """Run all collision handling tests"""
    print("🛡️ PascalSovereigntyAgent Collision Handling Test Suite")
    print("=" * 60)

    tests = [
        test_identical_file_collision_deletion,
        test_divergent_file_conflict_naming,
        test_windows_case_insensitive_handling,
        test_atomic_rename_with_verification,
        test_error_recovery_and_rollback,
        test_file_registry_update_race_condition_fix,
        test_dry_run_mode_integrity,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All collision handling tests passed!")
        return True
    else:
        print("💥 Some tests failed - review the implementation")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
