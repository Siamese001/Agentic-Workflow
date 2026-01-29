#!/usr/bin/env python3
"""
Test case for PascalSovereigntyFixer collision handling fix
"""

import sys
import tempfile
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L0_maintenance.scripts.PascalSovereigntyFixer import PascalSovereigntyFixer


def test_collision_handling():
    """Test that collision handling works correctly for identical and different content"""

    print("=== Testing PascalSovereigntyFixer Collision Handling ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files with identical content
        test_file1 = temp_path / "TestMixin.py"
        test_file2 = temp_path / "test_mixin.py"

        identical_content = '''"""
Test mixin for collision testing
"""
class TestMixin:
    pass
'''

        test_file1.write_text(identical_content)
        test_file2.write_text(identical_content)

        # Test collision with identical content
        fixer = PascalSovereigntyFixer(dry_run=False)
        result = fixer.safe_rename_windows(test_file1, "test_mixin.py")

        assert result == True, "Should handle identical content collision correctly"
        assert not test_file1.exists(), "Source file should be removed"
        assert test_file2.exists(), "Target file should still exist"

        # Create files with different content
        test_file3 = temp_path / "AnotherMixin.py"
        test_file4 = temp_path / "another_mixin.py"

        test_file3.write_text("class AnotherMixin: pass")
        test_file4.write_text("class AnotherMixin: pass  # Different content")

        # Test collision with different content
        result2 = fixer.safe_rename_windows(test_file3, "another_mixin.py")

        assert result2 == False, "Should not overwrite different content"
        assert test_file3.exists(), "Source file should remain when content differs"
        assert test_file4.exists(), "Target file should remain when content differs"

        print("✅ All collision handling tests passed!")
        return True


if __name__ == "__main__":
    try:
        success = test_collision_handling()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
