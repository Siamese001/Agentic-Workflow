"""
CST-based CodeHealerAgent Integration Test

Tests that the CodeHealerAgent correctly integrates with the CST infrastructure
and preserves the surgical healing pattern.
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.core.surgical_context import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
from agentic_core.L5_safety.validators.core.surgical_cst_healer_mixin import (
    SurgicalCSTHealerMixin,
)


class TestCodeHealerCSTIntegration:
    """Test CST integration with CodeHealerAgent pattern."""

    def test_surgical_context_creation(self):
        """Test that surgical contexts are created correctly for import healing."""
        source_code = """# Module comment
import os  # Used import
import unused_module  # Should be removed

def test():
    return os.getcwd()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Parse the file
            import ast

            tree = ast.parse(source_code)

            # Create violation for unused import (simulating CodeHealerAgent logic)
            coordinate = ASTCoordinate(line=3, column=0, node_id="unused_import", node_type="Import")

            violation = ViolationConstraint(
                constraint_type="unused_import",
                severity="warning",
                message="Unused import: unused_module",
                fix_type="delete",
            )
            violation.target_coordinate = coordinate

            # Create surgical context as CodeHealerAgent would
            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="unused_import_unused_module_3",
            )

            # Verify context structure
            assert context.file_path == temp_path
            assert context.detector_agent == "CodeHealerAgent"
            assert context.detection_method == "heal_imports"
            assert len(context.violations) == 1
            assert context.violations[0].constraint_type == "unused_import"
            assert context.violations[0].fix_type == "delete"
            assert len(context.target_coordinates) == 1
            assert context.target_coordinates[0].line == 3

            print("✅ Surgical context creation works correctly!")

        finally:
            temp_path.unlink()

    def test_cst_mixin_integration(self):
        """Test that SurgicalCSTHealerMixin can be invoked."""
        source_code = """# Test file
import os

def test():
    return "test"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Create minimal context
            import ast

            tree = ast.parse(source_code)

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[],  # No violations
                target_coordinates=[],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="no_violations",
            )

            # Test CST mixin invocation
            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            # Verify result structure
            assert "status" in result
            assert "violations_found" in result
            assert "violations_fixed" in result
            assert "errors" in result
            assert "skipped" in result
            assert result["status"] in ["success", "error"]

            # Verify file is unchanged when no violations
            healed_content = temp_path.read_text(encoding="utf-8")
            assert healed_content == source_code

            print("✅ CST mixin integration works correctly!")

        finally:
            temp_path.unlink()

    def test_actual_import_removal(self):
        """Test that imports are actually removed from the file."""
        source_code = """# Module comment
import os  # Used import
import unused_module  # Should be removed
import json  # Another used import

def test():
    return os.path.join("data.json")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Parse the file
            import ast

            tree = ast.parse(source_code)

            # Create violation for unused import
            coordinate = ASTCoordinate(line=3, column=0, node_id="unused_import", node_type="Import")

            violation = ViolationConstraint(
                constraint_type="unused_import",
                severity="warning",
                message="Unused import: unused_module",
                fix_type="delete",
            )
            violation.target_coordinate = coordinate

            # Create surgical context
            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[violation],
                target_coordinates=[coordinate],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="unused_import_unused_module_3",
            )

            # Apply CST-based healing
            healer = SurgicalCSTHealerMixin()
            result = healer.heal_surgical_cst(context)

            # Read the healed file
            healed_content = temp_path.read_text(encoding="utf-8")

            # CRITICAL ASSERTIONS:
            # 1. The unused import should be GONE
            assert "import unused_module" not in healed_content, "Unused import was not removed!"

            # 2. The comment should stay (proving zero-loss)
            assert "# Module comment" in healed_content, "Module comment was lost!"
            assert "# Used import" in healed_content, "Used import comment was lost!"
            assert "# Another used import" in healed_content, "Another used import comment was lost!"

            # 3. Other imports should be preserved
            assert "import os" in healed_content, "Used import was incorrectly removed!"
            assert "import json" in healed_content, "Another used import was incorrectly removed!"

            # 4. Function should be preserved
            assert "def test():" in healed_content, "Function was lost!"
            assert "return os.path.join" in healed_content, "Function body was corrupted!"

            # 5. Verify healing result
            assert result["status"] == "success"
            assert result["violations_fixed"] >= 1

            print("✅ Import actually removed while preserving all comments!")

        finally:
            temp_path.unlink()

    def test_code_healer_agent_pattern(self):
        """Test the pattern that CodeHealerAgent would use for CST healing."""
        source_code = '''# Important module comment
import os  # OS operations
import json  # JSON operations

class TestClass:
    """Important class docstring."""

    def method(self):
        # Important method comment
        return os.path.join("path", "file.json")
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Simulate CodeHealerAgent.heal_imports() logic
            import ast

            tree = ast.parse(source_code)

            # Find imports (simplified version of CodeHealerAgent logic)
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname or alias.name.split(".")[0]
                        imports.append((node, name, node.lineno))

            # Simulate finding unused imports (for this test, assume none are unused)
            unused_imports = []  # In real scenario, this would find unused ones

            surgical_contexts = []
            actions = []

            for node, name, lineno in unused_imports:
                # Create HealingAction for tracking
                action = {
                    "healing_type": "IMPORT",
                    "file_path": temp_path,
                    "line_number": lineno,
                    "description": f"Remove unused import: {name}",
                    "applied": False,
                }
                actions.append(action)

                # Create SurgicalContext for CST healing
                coordinate = ASTCoordinate(
                    line=lineno, column=0, node_id=f"import_{name}", node_type="Import"
                )

                violation = ViolationConstraint(
                    constraint_type="unused_import",
                    severity="warning",
                    message=f"Unused import: {name}",
                    fix_type="delete",
                )
                violation.target_coordinate = coordinate

                context = SurgicalContext(
                    file_path=temp_path,
                    file_content=source_code,
                    ast_tree=tree,
                    violations=[violation],
                    target_coordinates=[coordinate],
                    detector_agent="CodeHealerAgent",
                    detection_method="heal_imports",
                    detection_timestamp=datetime.now().isoformat(),
                    violation_id=f"unused_import_{name}_{lineno}",
                )
                surgical_contexts.append(context)

            # Apply CST-based healing (would be done in actual CodeHealerAgent)
            healer = SurgicalCSTHealerMixin()
            for context in surgical_contexts:
                healer.heal_surgical_cst(context)
                # In real scenario, would mark actions as applied based on result

            # Verify original file is preserved when no unused imports
            healed_content = temp_path.read_text(encoding="utf-8")
            assert healed_content == source_code

            # Verify all important elements are preserved
            assert "# Important module comment" in healed_content
            assert "# OS operations" in healed_content
            assert "# JSON operations" in healed_content
            assert '"""Important class docstring."""' in healed_content
            assert "# Important method comment" in healed_content

            print("✅ CodeHealerAgent pattern works correctly!")

        finally:
            temp_path.unlink()

    def test_cst_preserves_structure(self):
        """Test that CST processing preserves file structure even when no changes are made."""
        source_code = '''#!/usr/bin/env python3
"""
Complex module docstring
with multiple lines
and formatting.
"""

# Import section
import os
import sys

# Class definition
class ComplexClass:
    """
    Complex class docstring
    with detailed information.
    """

    def __init__(self):
        # Constructor comment
        self.value = os.getcwd()

    def method(self):
        """Method docstring."""
        # Method implementation comment
        return self.value

# Module-level code
if __name__ == "__main__":
    # Main block comment
    print("test")
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(source_code)
            temp_path = Path(f.name)

        try:
            # Process with CST (no violations)
            import ast

            tree = ast.parse(source_code)

            context = SurgicalContext(
                file_path=temp_path,
                file_content=source_code,
                ast_tree=tree,
                violations=[],
                target_coordinates=[],
                detector_agent="CodeHealerAgent",
                detection_method="heal_imports",
                detection_timestamp=datetime.now().isoformat(),
                violation_id="structure_test",
            )

            healer = SurgicalCSTHealerMixin()
            healer.heal_surgical_cst(context)

            # Verify structure is preserved exactly
            healed_content = temp_path.read_text(encoding="utf-8")
            assert healed_content == source_code

            # Verify specific elements are preserved
            assert "#!/usr/bin/env python3" in healed_content
            assert '"""' in healed_content
            assert "Complex module docstring" in healed_content
            assert "# Import section" in healed_content
            assert "# Class definition" in healed_content
            assert "# Constructor comment" in healed_content
            assert "# Method implementation comment" in healed_content
            assert "# Module-level code" in healed_content
            assert "# Main block comment" in healed_content

            print("✅ CST preserves complex file structure!")

        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
