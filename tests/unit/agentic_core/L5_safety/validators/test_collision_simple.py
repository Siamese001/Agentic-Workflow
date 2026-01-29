#!/usr/bin/env python3
"""
Simplified test for PascalSovereigntyAgent collision handling fixes
Tests the core logic without triggering sovereign lock
"""

import sys
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def test_collision_logic_directly():
    """Test collision resolution logic directly without full agent initialization"""
    print("=== Testing Collision Resolution Logic ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test 1: Identical files
        print("Test 1: Identical file collision")
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

        # Test the collision resolution logic directly
        from agentic_core.L5_safety.validators.PascalSovereigntyAgent import PascalSovereigntyAgent

        # Create agent in test mode to avoid sovereign lock
        agent = object.__new__(PascalSovereigntyAgent)
        agent.dry_run = False
        agent.verbose = True

        # Test the method
        result = agent.resolve_collision_and_rename(violator, "HealerProtocol.py")

        assert result == True, "Should resolve identical collision"
        assert not violator.exists(), "Violator should be deleted"
        assert target.exists(), "Target should still exist"

        print("✅ Identical file collision handled correctly")

        # Test 2: Different files
        print("Test 2: Different file collision")
        target2 = temp_path / "TestAgent.py"
        violator2 = temp_path / "test_agent.py"

        target2.write_text("class TestAgent: pass  # Version 1")
        violator2.write_text("class TestAgent: pass  # Version 2")

        result2 = agent.resolve_collision_and_rename(violator2, "TestAgent.py")

        assert result2 == True, "Should resolve divergent collision"
        assert not violator2.exists(), "Violator should be moved"
        assert target2.exists(), "Target should still exist"

        # Check for conflict file
        conflicts = list(temp_path.glob("TestAgent.py.CONFLICT_*"))
        assert len(conflicts) == 1, "Should create exactly one conflict file"

        print("✅ Different file collision handled correctly")

        # Test 3: Standard rename
        print("Test 3: Standard rename")
        src = temp_path / "OldName.py"
        src.write_text("class OldName: pass")

        result3 = agent.resolve_collision_and_rename(src, "NewName.py")

        assert result3 == True, "Should perform standard rename"
        assert not src.exists(), "Source should be renamed"
        assert (temp_path / "NewName.py").exists(), "Target should exist"

        print("✅ Standard rename handled correctly")

        # Test 4: Dry run mode
        print("Test 4: Dry run mode")
        agent.dry_run = True
        src2 = temp_path / "DryRunTest.py"
        src2.write_text("class DryRunTest: pass")

        result4 = agent.resolve_collision_and_rename(src2, "DryRunTarget.py")

        assert result4 == True, "Should return success in dry run"
        assert src2.exists(), "Source should still exist in dry run"
        assert not (temp_path / "DryRunTarget.py").exists(), "Target should not exist in dry run"

        print("✅ Dry run mode handled correctly")

        print("\n🎉 All collision resolution tests passed!")
        return True


if __name__ == "__main__":
    try:
        success = test_collision_logic_directly()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
