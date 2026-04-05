"""Parallel test for monolithic vs modular functions - direct import."""
import ast
import sys
from pathlib import Path

# Add the agentic_core directory to sys.path to import directly
sys.path.insert(0, str(Path(__file__).parent / "agentic_core" / "L5_safety" / "reasoning" / "file_classification"))

# Import modular functions directly from files
import classification_core
import naming_policy
import validation_rules

print("=== MODULAR FUNCTIONS TEST (DIRECT IMPORT) ===\n")

# Test 1: Test patterns
code1 = "import unittest\nclass MyTestCase(unittest.TestCase):\n    def test_something(self):\n        self.assertTrue(True)"
tree1 = ast.parse(code1)
path1 = Path("test_example.py")
result1 = classification_core._detect_test_patterns(tree1, path1)
print(f"Test detection: {result1}")
assert result1["is_test"] is True, "Test detection failed"

# Test 2: Script patterns
code2 = "if __name__ == '__main__':\n    print('Hello')"
tree2 = ast.parse(code2)
path2 = Path("script.py")
result2 = classification_core._detect_script_patterns(tree2, path2)
print(f"Script detection: {result2}")
assert result2["is_script"] is True, "Script detection failed"

# Test 3: Type patterns
code3 = "from enum import Enum\nclass Status(Enum):\n    ACTIVE = 1"
tree3 = ast.parse(code3)
path3 = Path("types.py")
result3 = classification_core._detect_type_patterns(tree3, path3)
print(f"Type detection: {result3}")
assert result3["is_types"] is True, "Type detection failed"

# Test 4: normalize_filename
name = "s_s_o_t_consolidation_analyzer.py"
result4 = naming_policy.normalize_filename(name)
print(f"Normalize filename: {result4}")
assert result4 == "ssot_consolidation_analyzer.py", "Normalize failed"

# Test 5: check_fake_config
code5 = "class Config:\n    def do_something(self):\n        pass"
path5 = Path("fake_config.py")
result5 = validation_rules.check_fake_config(path5, code5)
print(f"Fake config check: {result5}")
assert result5 is not None, "Fake config detection failed"
assert result5.type == "FAKE_CONFIG", "Wrong violation type"

# Test 6: check_domain_root_purity
path6 = Path("knowledge/test_file.py")
result6 = validation_rules.check_domain_root_purity(path6)
print(f"Domain root purity: {result6}")
assert result6 is not None, "Domain root purity check failed"

print("\n=== ALL MODULAR FUNCTION TESTS PASSED ===")
print("\nThe modular files contain the extracted logic and work independently.")