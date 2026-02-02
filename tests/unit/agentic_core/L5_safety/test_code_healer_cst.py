"""
Test CST-based CodeHealerAgent - Zero-Loss Healing Verification

Tests that the CodeHealerAgent uses LibCST for surgical healing while
preserving comments, docstrings, and formatting.
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L5_safety.policy_engine.code_healer_agent import CodeHealerAgent


class TestCodeHealerCSTIntegration:
    """Test CST-based healing in CodeHealerAgent."""

    def test_preserves_comments_and_docstrings(self):
        """
        Critical test: Verify CST healing preserves all metadata.

        Tests the scenario described in the mission brief:
        - Broken import
        - Complex docstring
        - Comment inside function body
        """
        # Create test file with broken import, complex docstring, and inner comment
        source_code = '''#!/usr/bin/env python3
"""
This is a complex module docstring with multiple lines.
It contains important information about the module purpose.
Author: Test Author
Version: 1.0.0
"""

# Standard library imports
import os  # OS operations
import sys  # System-specific parameters and functions
import json  # JSON encoding/decoding
import unused_module  # This should be removed

# Third-party imports
import requests  # HTTP library

class TestClass:
    """
    This is a complex class docstring.
    
    It has multiple paragraphs and formatting:
    
    Args:
        param1: First parameter
        param2: Second parameter
    
    Returns:
        Something useful
    
    Example:
        >>> obj = TestClass()
        >>> obj.method()
    """
    
    def method_with_comment(self):
        # This comment should be preserved during healing
        return os.getcwd()
    
    def another_method(self):
        """Simple docstring."""
        return "test"

# End of file comment
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Create CodeHealerAgent with dry_run=False to apply healing
            healer = CodeHealerAgent()
            healer._agent_config.dry_run = False

            # Apply healing
            actions = healer.heal_imports(temp_path)

            # Verify unused import was detected
            unused_import_actions = [a for a in actions if "unused_module" in a.description]
            assert len(unused_import_actions) >= 1

            # Read the healed file
            healed_content = temp_path.read_text(encoding="utf-8")

            # CRITICAL: Verify all comments are preserved
            assert "#!/usr/bin/env python3" in healed_content
            assert '"""' in healed_content  # Module docstring
            assert "Author: Test Author" in healed_content
            assert "Version: 1.0.0" in healed_content
            assert "# Standard library imports" in healed_content
            assert "# OS operations" in healed_content
            assert "# System-specific parameters and functions" in healed_content
            assert "# JSON encoding/decoding" in healed_content
            assert "# Third-party imports" in healed_content
            assert "# HTTP library" in healed_content
            assert "# This comment should be preserved during healing" in healed_content
            assert "# End of file comment" in healed_content

            # Verify complex class docstring is preserved
            assert "This is a complex class docstring." in healed_content
            assert "Args:" in healed_content
            assert "param1: First parameter" in healed_content
            assert "Returns:" in healed_content
            assert "Example:" in healed_content

            # Verify unused import was removed
            assert "import unused_module" not in healed_content

            # Verify other imports are preserved
            assert "import os" in healed_content
            assert "import sys" in healed_content
            assert "import json" in healed_content
            assert "import requests" in healed_content

            # Verify function with inner comment is preserved
            assert "def method_with_comment(self):" in healed_content
            assert "# This comment should be preserved during healing" in healed_content
            assert "return os.getcwd()" in healed_content

            print("✅ CST-based CodeHealerAgent preserves all metadata!")

        finally:
            temp_path.unlink()

    def test_cst_engine_invoked(self):
        """Verify that the CST engine is actually invoked for healing."""
        source_code = """# Module comment
import os
import unused_import  # Should be removed

def test_function():
    # Inner comment
    return os.path.join("path", "file")
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            healer = CodeHealerAgent()
            healer._agent_config.dry_run = False

            # Mock the CST healing method to verify it's called
            original_heal_surgical_cst = healer.heal_surgical_cst
            cst_called = False

            def mock_heal_surgical_cst(context):
                nonlocal cst_called
                cst_called = True
                return original_heal_surgical_cst(context)

            healer.heal_surgical_cst = mock_heal_surgical_cst

            # Apply healing
            actions = healer.heal_imports(temp_path)

            # Verify CST method was called
            assert cst_called, "CST healing method was not invoked"

            # Verify healing worked
            healed_content = temp_path.read_text(encoding="utf-8")
            assert "import unused_import" not in healed_content
            assert "# Module comment" in healed_content
            assert "# Inner comment" in healed_content

            print("✅ CST engine successfully invoked!")

        finally:
            temp_path.unlink()

    def test_zero_loss_verification(self):
        """Verify no unintended changes are made during CST healing."""
        source_code = '''# Important header comment
import os  # OS import

def function_with_docstring():
    """
    This is a function docstring.
    
    It contains multiple lines and formatting.
    """
    # Important implementation comment
    return os.path.join("a", "b")

# Footer comment
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            healer = CodeHealerAgent()
            healer._agent_config.dry_run = False

            # Apply healing (no unused imports in this case)
            actions = healer.heal_imports(temp_path)

            # File should be unchanged (no unused imports to fix)
            healed_content = temp_path.read_text(encoding="utf-8")

            # Verify everything is preserved exactly
            assert healed_content == source_code

            # Verify no actions were taken
            applied_actions = [a for a in actions if a.applied]
            assert len(applied_actions) == 0

            print("✅ Zero-loss verification passed!")

        finally:
            temp_path.unlink()

    def test_multiple_unused_imports(self):
        """Test handling multiple unused imports in one file."""
        source_code = """# Module header
import os  # Used
import sys  # Used  
import unused1  # Not used
import json  # Used
import unused2  # Not used
import requests  # Not used

def test():
    return os.path.join(sys.path[0], "file.json")
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            healer = CodeHealerAgent()
            healer._agent_config.dry_run = False

            # Apply healing
            actions = healer.heal_imports(temp_path)

            # Read healed content
            healed_content = temp_path.read_text(encoding="utf-8")

            # Verify unused imports are removed
            assert "import unused1" not in healed_content
            assert "import unused2" not in healed_content
            assert "import requests" not in healed_content

            # Verify used imports are preserved
            assert "import os" in healed_content
            assert "import sys" in healed_content
            assert "import json" in healed_content

            # Verify comments are preserved
            assert "# Module header" in healed_content
            assert "# Used" in healed_content
            assert (
                "# Not used" not in healed_content
            )  # These comments should be removed with imports

            print("✅ Multiple unused imports handled correctly!")

        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
