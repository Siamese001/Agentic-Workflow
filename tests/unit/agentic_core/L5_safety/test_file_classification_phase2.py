"""
Unit tests for FileClassificationAgent Phase 2 fixes.

Tests:
1. heal() method uses unified classification logic (classify_file + get_compliant_name)
2. Dead code removed (duplicate TEST handling, redundant UTILITY check)
3. Detection and healing logic are consistent
"""

import ast
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))


class TestPhase2UnifiedHealLogic:
    """Test that heal() uses same logic as classify_file() and get_compliant_name()."""

    def test_heal_method_calls_classify_file(self):
        """Verify heal() method contains call to classify_file()."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find the heal method
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "FileClassificationAgent":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "heal":
                        # Check for classify_file call in method body
                        method_source = ast.unparse(item)
                        assert "classify_file" in method_source, (
                            "heal() should call classify_file() for unified logic"
                        )
                        return

        pytest.fail("Could not find heal() method in FileClassificationAgent")

    def test_heal_method_calls_get_compliant_name(self):
        """Verify heal() method contains call to get_compliant_name()."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find the heal method
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "FileClassificationAgent":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "heal":
                        # Check for get_compliant_name call in method body
                        method_source = ast.unparse(item)
                        assert "get_compliant_name" in method_source, (
                            "heal() should call get_compliant_name() for unified logic"
                        )
                        return

        pytest.fail("Could not find heal() method in FileClassificationAgent")

    def test_heal_no_crude_string_matching(self):
        """Verify heal() doesn't use crude 'class ' and 'Agent' string matching."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find the heal method
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "FileClassificationAgent":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "heal":
                        method_source = ast.unparse(item)
                        # Should NOT have crude string matching pattern
                        assert '"class " in content and "Agent" in content' not in method_source, (
                            "heal() should NOT use crude string matching"
                        )
                        return

        pytest.fail("Could not find heal() method in FileClassificationAgent")


class TestPhase2DeadCodeRemoval:
    """Test that dead code has been removed."""

    def test_no_duplicate_test_handling(self):
        """Verify duplicate TEST handling logic is removed."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")

        # Count occurrences of TEST handling in get_compliant_name
        # Should only have ONE TEST handling block, not two
        test_handling_count = content.count('if file_type == "TEST":')

        assert test_handling_count == 1, (
            f"Expected 1 TEST handling block, found {test_handling_count}. "
            "Duplicate TEST logic should be removed."
        )

    def test_no_redundant_utility_check(self):
        """Verify redundant UTILITY check after MIXIN handling is removed."""
        file_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "agentic_core/L5_safety/validators/FileClassificationAgent.py"
        )

        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        # Find get_compliant_name method
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "FileClassificationAgent":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "get_compliant_name":
                        method_source = ast.unparse(item)
                        # Count standalone UTILITY checks (not in the initial set)
                        # The pattern 'if file_type == "UTILITY":' should NOT appear
                        # after the initial set check
                        lines = method_source.split("\n")
                        utility_standalone_checks = sum(
                            1
                            for line in lines
                            if 'file_type == "UTILITY"' in line
                            and "IGNORE" not in line
                            and "TYPES" not in line
                        )
                        assert utility_standalone_checks == 0, (
                            "Redundant standalone UTILITY check should be removed"
                        )
                        return

        pytest.fail("Could not find get_compliant_name() in FileClassificationAgent")


class TestPhase2ConsistentBehavior:
    """Test that detection and healing behave consistently."""

    @pytest.fixture
    def agent(self, tmp_path):
        """Create agent instance for testing."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = tmp_path.resolve()
        agent.dry_run = True
        agent.verbose = False
        agent.validate_only = False
        agent.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "collisions_resolved": 0,
            "violations": {
                "AGENT": 0,
                "CLASS": 0,
                "MIXIN": 0,
                "UTILITY": 0,
                "PROTOCOL": 0,
                "ENGINE": 0,
                "STUB": 0,
                "TEST": 0,
                "SCRIPT": 0,
                "TYPES": 0,
                "GATEWAY": 0,
            },
        }
        agent.file_registry = []
        return agent

    def test_classify_and_heal_consistency_for_agent(self, agent, tmp_path):
        """Test that classification and healing agree on AGENT files."""
        # Create a test file in agents directory
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()
        test_file = agents_dir / "MyClass.py"
        test_file.write_text("class MyClass:\n    pass\n")

        # Classification should identify as AGENT (structural)
        file_type = agent.classify_file(test_file)
        assert file_type == "AGENT", f"Expected AGENT, got {file_type}"

        # get_compliant_name should suggest Agent suffix
        new_name = agent.get_compliant_name(test_file, file_type)
        assert new_name is not None, "Should suggest a new name"
        assert "Agent" in new_name, f"New name should have Agent suffix: {new_name}"

    def test_classify_and_heal_consistency_for_script(self, agent, tmp_path):
        """Test that classification and healing agree on SCRIPT files."""
        # Create a test file in scripts directory
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        test_file = scripts_dir / "MyScript.py"
        test_file.write_text("def main():\n    pass\n")

        # Classification should identify as SCRIPT
        file_type = agent.classify_file(test_file)
        assert file_type == "SCRIPT", f"Expected SCRIPT, got {file_type}"

        # get_compliant_name should suggest snake_case
        new_name = agent.get_compliant_name(test_file, file_type)
        if new_name:
            assert new_name.islower() or "_" in new_name, f"Script should be snake_case: {new_name}"

    def test_heal_uses_classify_file_result(self, agent, tmp_path):
        """Test that heal() properly uses classify_file() result."""
        # Create a test file
        test_file = tmp_path / "test_something.py"
        test_file.write_text("def test_foo():\n    pass\n")

        # Call heal with the file
        result = agent.heal({"type": "naming", "path": str(test_file)})

        # Should return valid result dict
        assert isinstance(result, dict)
        assert "violations_found" in result or "skipped" in result


class TestPhase2Integration:
    """Integration tests for Phase 2 fixes."""

    def test_heal_method_returns_standard_format(self):
        """Verify heal() returns standard result format."""
        from agentic_core.L5_safety.validators.FileClassificationAgent import (
            FileClassificationAgent,
        )

        agent = object.__new__(FileClassificationAgent)
        agent.project_root = Path.cwd().resolve()
        agent.dry_run = True
        agent.verbose = False
        agent.validate_only = False
        agent.stats = {
            "analyzed": 0,
            "compliant": 0,
            "renamed": 0,
            "imports_fixed": 0,
            "collisions_resolved": 0,
            "violations": {
                "AGENT": 0,
                "CLASS": 0,
                "MIXIN": 0,
                "UTILITY": 0,
                "PROTOCOL": 0,
                "ENGINE": 0,
                "STUB": 0,
                "TEST": 0,
                "SCRIPT": 0,
                "TYPES": 0,
                "GATEWAY": 0,
            },
        }
        agent.file_registry = []

        # Call heal with nonexistent file
        result = agent.heal({"type": "naming", "path": "/nonexistent/file.py"})

        # Should have standard keys
        assert "violations_found" in result
        assert "violations_fixed" in result
        assert "errors" in result
        assert "skipped" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
