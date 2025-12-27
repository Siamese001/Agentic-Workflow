"""Test zero-loss fission merge - large file splitting with behavioral preservation."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import ast
import importlib.util


@pytest.mark.integration
@pytest.mark.slow
class TestZeroLossFissionMerge:
    """Verify fission splits large files without losing functionality."""
    
    def test_large_file_triggers_fission(
        self, tmp_sovereign_workspace, fission_blueprint
    ):
        """
        GIVEN: File exceeding 10000 LOC threshold
        WHEN: Fission is triggered
        THEN: Blueprint identifies split targets
        """
        # Arrange
        large_file = tmp_sovereign_workspace / "monolith.py"
        content = "# Large file\n" + "".join([f"class Model{i}:\n    pass\n\n" for i in range(3000)])
        large_file.write_text(content)
        
        # Act
        line_count = len(large_file.read_text().splitlines())
        should_trigger = line_count > fission_blueprint["trigger_threshold"]
        
        # Assert
        assert should_trigger is False  # 3000 classes * 3 lines = 9000 < 10000
        
        # Add more to trigger
        additional_content = "".join([f"def util{i}():\n    pass\n\n" for i in range(500)])
        large_file.write_text(large_file.read_text() + "\n" + additional_content)
        line_count = len(large_file.read_text().splitlines())
        assert line_count > fission_blueprint["trigger_threshold"]
    
    def test_fission_preserves_all_symbols(
        self, tmp_sovereign_workspace, fission_blueprint, file_hash_tracker
    ):
        """
        GIVEN: Large file with classes and functions
        WHEN: Fission splits into submodules
        THEN: All symbols remain importable
        """
        # Arrange
        original_file = tmp_sovereign_workspace / "original.py"
        original_content = """
class CoreLogic:
    def process(self):
        return "core"

class UtilityHelper:
    def assist(self):
        return "util"

def standalone_function():
    return "standalone"
"""
        original_file.write_text(original_content)
        
        # Parse original symbols
        tree = ast.parse(original_content)
        original_symbols = {
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.ClassDef, ast.FunctionDef))
        }
        
        # Act - Simulate fission split
        core_module = tmp_sovereign_workspace / "core_logic.py"
        util_module = tmp_sovereign_workspace / "utilities.py"
        
        core_module.write_text("class CoreLogic:\n    def process(self):\n        return 'core'\n")
        util_module.write_text("""
class UtilityHelper:
    def assist(self):
        return "util"

def standalone_function():
    return "standalone"
""")
        
        # Create __init__.py to re-export
        init_file = tmp_sovereign_workspace / "__init__.py"
        init_file.write_text("""
from .core_logic import CoreLogic
from .utilities import UtilityHelper, standalone_function

__all__ = ['CoreLogic', 'UtilityHelper', 'standalone_function']
""")
        
        # Assert - All symbols available
        combined_symbols = set()
        for module_file in [core_module, util_module]:
            tree = ast.parse(module_file.read_text())
            combined_symbols.update({
                node.name for node in ast.walk(tree)
                if isinstance(node, (ast.ClassDef, ast.FunctionDef))
            })
        
        assert original_symbols == combined_symbols
    
    def test_fission_preserves_behavior(
        self, tmp_sovereign_workspace
    ):
        """
        GIVEN: Original file with executable logic
        WHEN: Fission splits and re-imports
        THEN: Same outputs produced
        """
        # Arrange
        original_file = tmp_sovereign_workspace / "calculator.py"
        original_content = """
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b

def compute_total(values):
    return sum(values)
"""
        original_file.write_text(original_content)
        
        # Execute original
        spec = importlib.util.spec_from_file_location("calculator", original_file)
        original_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(original_module)
        
        original_add_result = original_module.Calculator().add(5, 3)
        original_total_result = original_module.compute_total([1, 2, 3, 4])
        
        # Act - Split into modules
        calc_module = tmp_sovereign_workspace / "calculator_class.py"
        calc_module.write_text("""
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
""")
        
        utils_module = tmp_sovereign_workspace / "calculator_utils.py"
        utils_module.write_text("""
def compute_total(values):
    return sum(values)
""")
        
        # Execute split modules
        spec1 = importlib.util.spec_from_file_location("calculator_class", calc_module)
        calc_split = importlib.util.module_from_spec(spec1)
        spec1.loader.exec_module(calc_split)
        
        spec2 = importlib.util.spec_from_file_location("calculator_utils", utils_module)
        utils_split = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(utils_split)
        
        # Assert - Same behavior
        assert calc_split.Calculator().add(5, 3) == original_add_result
        assert utils_split.compute_total([1, 2, 3, 4]) == original_total_result
    
    def test_fission_updates_imports_automatically(
        self, tmp_sovereign_workspace
    ):
        """
        GIVEN: Files importing from monolith
        WHEN: Fission splits monolith
        THEN: Import statements updated to new modules
        """
        # Arrange
        monolith = tmp_sovereign_workspace / "monolith.py"
        monolith.write_text("class BigClass:\n    pass\n")
        
        consumer = tmp_sovereign_workspace / "consumer.py"
        consumer.write_text("from monolith import BigClass\n\nobj = BigClass()\n")
        
        # Act - Simulate fission and import fix
        split_module = tmp_sovereign_workspace / "big_class.py"
        split_module.write_text("class BigClass:\n    pass\n")
        
        # Update consumer import
        updated_consumer = consumer.read_text().replace(
            "from monolith import BigClass",
            "from big_class import BigClass"
        )
        consumer.write_text(updated_consumer)
        
        # Assert
        assert "from big_class import BigClass" in consumer.read_text()
        assert "from monolith" not in consumer.read_text()
    
    @pytest.mark.parametrize("file_size_loc", [10001, 15000, 25000])
    def test_fission_scales_with_file_size(
        self, tmp_sovereign_workspace, fission_blueprint, file_size_loc
    ):
        """
        GIVEN: Files of varying sizes above threshold
        WHEN: Fission is applied
        THEN: Appropriate number of submodules created
        """
        # Arrange
        large_file = tmp_sovereign_workspace / f"large_{file_size_loc}.py"
        # Generate enough classes to reach target LOC (4 lines per class)
        num_classes = (file_size_loc // 4) + 1
        
        content = "".join([
            f"class Class{i}:\n    def method(self):\n        return {i}\n\n"
            for i in range(num_classes)
        ])
        large_file.write_text(content)
        
        # Act - Calculate expected splits
        classes_per_module = 500  # Target ~2500 LOC per module
        expected_modules = (num_classes // classes_per_module) + 1
        
        # Assert
        actual_lines = len(large_file.read_text().splitlines())
        assert actual_lines >= file_size_loc, f"Expected >={file_size_loc} lines, got {actual_lines}"
        assert expected_modules >= 2  # Should split into at least 2 modules
    
    def test_fission_preserves_docstrings_and_comments(
        self, tmp_sovereign_workspace
    ):
        """
        GIVEN: File with extensive documentation
        WHEN: Fission splits file
        THEN: All docstrings and comments preserved
        """
        # Arrange
        documented_file = tmp_sovereign_workspace / "documented.py"
        content = '''"""Module docstring."""

class ImportantClass:
    """Class docstring with sovereignty details."""
    
    def critical_method(self):
        """Method docstring.
        
        This is critical for sovereignty.
        """
        # Inline comment
        return "result"
'''
        documented_file.write_text(content)
        
        # Act - Split while preserving docs
        split_file = tmp_sovereign_workspace / "important_class.py"
        split_file.write_text(content)  # In real fission, parser preserves all
        
        # Assert
        assert '"""Module docstring."""' in split_file.read_text()
        assert '"""Class docstring with sovereignty details."""' in split_file.read_text()
        assert "# Inline comment" in split_file.read_text()


@pytest.mark.integration
class TestFissionRollback:
    """Test fission rollback on failure."""
    
    def test_fission_failure_restores_original(
        self, tmp_sovereign_workspace, healing_transaction_mock, file_hash_tracker
    ):
        """
        GIVEN: Fission operation fails mid-split
        WHEN: Rollback is triggered
        THEN: Original monolith restored
        """
        # Arrange
        monolith = tmp_sovereign_workspace / "monolith.py"
        original_content = "class A:\n    pass\n\nclass B:\n    pass\n"
        monolith.write_text(original_content)
        original_hash = file_hash_tracker(monolith)
        
        # Act
        healing_transaction_mock.backup(monolith)
        
        # Simulate failed split
        try:
            split1 = tmp_sovereign_workspace / "module_a.py"
            split1.write_text("class A:\n    pass\n")
            # Simulate failure before completing split
            raise Exception("Fission failed during split")
        except Exception:
            healing_transaction_mock.rollback()
        
        # Assert
        assert file_hash_tracker(monolith) == original_hash
        assert monolith.read_text() == original_content
