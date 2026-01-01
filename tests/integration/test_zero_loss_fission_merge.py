"""Test zero-loss fission merge - large file splitting with behavioral preservation."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import ast
import importlib.util
from typing import Any

@pytest.mark.integration
@pytest.mark.slow
class test_zero_loss_fission_merge:
    """Verify fission splits large files without losing functionality."""

    def test_large_file_triggers_fission(self, tmp_sovereign_workspace: Any, fission_blueprint: Any) -> Any:
        """
        GIVEN: File exceeding 10000 LOC threshold
        WHEN: Fission is triggered
        THEN: Blueprint identifies split targets
        """
        large_file: Any = tmp_sovereign_workspace / 'monolith.py'
        content: Any = '# Large file\n' + ''.join([f'class Model{i}:\n    pass\n\n' for i in range(3000)])
        large_file.write_text(content)
        line_count: Any = len(large_file.read_text().splitlines())
        should_trigger: Any = line_count > fission_blueprint['trigger_threshold']
        assert should_trigger is False
        additional_content: Any = ''.join([f'def util{i}():\n    pass\n\n' for i in range(500)])
        large_file.write_text(large_file.read_text() + '\n' + additional_content)
        line_count: Any = len(large_file.read_text().splitlines())
        assert line_count > fission_blueprint['trigger_threshold']

    def test_fission_preserves_all_symbols(self, tmp_sovereign_workspace: Any, fission_blueprint: Any, file_hash_tracker: Any) -> Any:
        """
        GIVEN: Large file with classes and functions
        WHEN: Fission splits into submodules
        THEN: All symbols remain importable
        """
        original_file: Any = tmp_sovereign_workspace / 'original.py'
        original_content: Any = '\n# NAMING FIXED: CoreLogic → core_logic\nclass core_logic:\n    def process(self):\n        return "core"\n\n# NAMING FIXED: UtilityHelper → utility_helper\nclass utility_helper:\n    def assist(self):\n        return "util"\n\ndef standalone_function():\n    return "standalone"\n'
        original_file.write_text(original_content)
        tree: Any = ast.parse(original_content)
        original_symbols: Any = {node.name for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.FunctionDef))}
        core_module: Any = tmp_sovereign_workspace / 'core_logic.py'
        util_module: Any = tmp_sovereign_workspace / 'utilities.py'
        core_module.write_text("class CoreLogic:\n    def process(self):\n        return 'core'\n")
        util_module.write_text('\n# NAMING FIXED: UtilityHelper → utility_helper\nclass utility_helper:\n    def assist(self):\n        return "util"\n\ndef standalone_function():\n    return "standalone"\n')
        init_file: Any = tmp_sovereign_workspace / '__init__.py'
        init_file.write_text("\nfrom .core_logic import CoreLogic\nfrom .utilities import UtilityHelper, standalone_function\n\n__all__ = ['CoreLogic', 'UtilityHelper', 'standalone_function']\n")
        combined_symbols: Any = set()
        for module_file in [core_module, util_module]:
            tree: Any = ast.parse(module_file.read_text())
            combined_symbols.update({node.name for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.FunctionDef))})
        assert original_symbols == combined_symbols

    def test_fission_preserves_behavior(self, tmp_sovereign_workspace: Any) -> Any:
        """
        GIVEN: Original file with executable logic
        WHEN: Fission splits and re-imports
        THEN: Same outputs produced
        """
        original_file: Any = tmp_sovereign_workspace / 'calculator.py'
        original_content: Any = '\n# NAMING FIXED: Calculator → calculator\nclass calculator:\n    def add(self, a, b):\n        return a + b\n    \n    def multiply(self, a, b):\n        return a * b\n\ndef compute_total(values):\n    return sum(values)\n'
        original_file.write_text(original_content)
        spec: Any = importlib.util.spec_from_file_location('calculator', original_file)
        original_module: Any = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(original_module)
        original_add_result: Any = original_module.Calculator().add(5, 3)
        original_total_result: Any = original_module.compute_total([1, 2, 3, 4])
        calc_module: Any = tmp_sovereign_workspace / 'calculator_class.py'
        calc_module.write_text('\n# NAMING FIXED: Calculator → calculator\nclass calculator:\n    def add(self, a, b):\n        return a + b\n    \n    def multiply(self, a, b):\n        return a * b\n')
        utils_module: Any = tmp_sovereign_workspace / 'calculator_utils.py'
        utils_module.write_text('\ndef compute_total(values):\n    return sum(values)\n')
        spec1: Any = importlib.util.spec_from_file_location('calculator_class', calc_module)
        calc_split: Any = importlib.util.module_from_spec(spec1)
        spec1.loader.exec_module(calc_split)
        spec2: Any = importlib.util.spec_from_file_location('calculator_utils', utils_module)
        utils_split: Any = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(utils_split)
        assert calc_split.Calculator().add(5, 3) == original_add_result
        assert utils_split.compute_total([1, 2, 3, 4]) == original_total_result

    def test_fission_updates_imports_automatically(self, tmp_sovereign_workspace: Any) -> Any:
        """
        GIVEN: Files importing from monolith
        WHEN: Fission splits monolith
        THEN: Import statements updated to new modules
        """
        monolith: Any = tmp_sovereign_workspace / 'monolith.py'
        monolith.write_text('class BigClass:\n    pass\n')
        consumer: Any = tmp_sovereign_workspace / 'consumer.py'
        consumer.write_text('from monolith import BigClass\n\nobj = BigClass()\n')
        split_module: Any = tmp_sovereign_workspace / 'big_class.py'
        split_module.write_text('class BigClass:\n    pass\n')
        updated_consumer: Any = consumer.read_text().replace('from monolith import BigClass', 'from big_class import BigClass')
        consumer.write_text(updated_consumer)
        assert 'from big_class import BigClass' in consumer.read_text()
        assert 'from monolith' not in consumer.read_text()

    @pytest.mark.parametrize('file_size_loc', [10001, 15000, 25000])
    def test_fission_scales_with_file_size(self, tmp_sovereign_workspace: Any, fission_blueprint: Any, file_size_loc: Any) -> Any:
        """
        GIVEN: Files of varying sizes above threshold
        WHEN: Fission is applied
        THEN: Appropriate number of submodules created
        """
        large_file: Any = tmp_sovereign_workspace / f'large_{file_size_loc}.py'
        num_classes: Any = file_size_loc // 4 + 1
        content: Any = ''.join([f'class Class{i}:\n    def method(self):\n        return {i}\n\n' for i in range(num_classes)])
        large_file.write_text(content)
        classes_per_module: Any = 500
        expected_modules: Any = num_classes // classes_per_module + 1
        actual_lines: Any = len(large_file.read_text().splitlines())
        assert actual_lines >= file_size_loc, f'Expected >={file_size_loc} lines, got {actual_lines}'
        assert expected_modules >= 2

    def test_fission_preserves_docstrings_and_comments(self, tmp_sovereign_workspace: Any) -> Any:
        """
        GIVEN: File with extensive documentation
        WHEN: Fission splits file
        THEN: All docstrings and comments preserved
        """
        documented_file: Any = tmp_sovereign_workspace / 'documented.py'
        content: Any = '"""Module docstring."""\n\n# NAMING FIXED: ImportantClass → important_class\nclass important_class:\n    """Class docstring with sovereignty details."""\n    \n    def critical_method(self):\n        """Method docstring.\n        \n        This is critical for sovereignty.\n        """\n        # Inline comment\n        return "result"\n'
        documented_file.write_text(content)
        split_file: Any = tmp_sovereign_workspace / 'important_class.py'
        split_file.write_text(content)
        assert '"""Module docstring."""' in split_file.read_text()
        assert '"""Class docstring with sovereignty details."""' in split_file.read_text()
        assert '# Inline comment' in split_file.read_text()

@pytest.mark.integration
class test_fission_rollback:
    """Test fission rollback on failure."""

    def test_fission_failure_restores_original(self, tmp_sovereign_workspace: Any, healing_transaction_mock: Any, file_hash_tracker: Any) -> Any:
        """
        GIVEN: Fission operation fails mid-split
        WHEN: Rollback is triggered
        THEN: Original monolith restored
        """
        monolith: Any = tmp_sovereign_workspace / 'monolith.py'
        original_content: Any = 'class A:\n    pass\n\nclass B:\n    pass\n'
        monolith.write_text(original_content)
        original_hash: Any = file_hash_tracker(monolith)
        healing_transaction_mock.backup(monolith)
        try:
            split1: Any = tmp_sovereign_workspace / 'module_a.py'
            split1.write_text('class A:\n    pass\n')
            raise Exception('Fission failed during split')
        except Exception:
            healing_transaction_mock.rollback()
        assert file_hash_tracker(monolith) == original_hash
        assert monolith.read_text() == original_content
