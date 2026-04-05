"""Parallel test for monolithic vs modular functions."""
import ast
from pathlib import Path
from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationHealerAgent
from agentic_core.L5_safety.reasoning.file_classification.classification_core import (
    _detect_script_patterns,
    _detect_type_patterns,
)
from agentic_core.L5_safety.reasoning.file_classification.naming_policy import (
    normalize_filename,
)
from agentic_core.L5_safety.reasoning.file_classification.validation_rules import (
    check_fake_config,
    check_domain_root_purity,
)

agent = FileClassificationHealerAgent()

# Test 1: Script patterns
code1 = "if __name__ == '__main__':\n    print('Hello')"
tree1 = ast.parse(code1)
path1 = Path("script.py")

monolithic_script = agent._detect_script_patterns(tree1, path1)
modular_script = _detect_script_patterns(tree1, path1)
print(f"Script - Monolithic: {monolithic_script}")
print(f"Script - Modular: {modular_script}")
print(f"Script match: {monolithic_script == modular_script}")

# Test 2: Type patterns
code2 = "from enum import Enum\nclass Status(Enum):\n    ACTIVE = 1"
tree2 = ast.parse(code2)
path2 = Path("types.py")

monolithic_type = agent._detect_type_patterns(tree2, path2)
modular_type = _detect_type_patterns(tree2, path2)
print(f"Type - Monolithic: {monolithic_type}")
print(f"Type - Modular: {modular_type}")
print(f"Type match: {monolithic_type == modular_type}")

# Test 3: normalize_filename
name = "s_s_o_t_consolidation_analyzer.py"
monolithic_norm = agent.normalize_filename(name)
modular_norm = normalize_filename(name)
print(f"Normalize - Monolithic: {monolithic_norm}")
print(f"Normalize - Modular: {modular_norm}")
print(f"Normalize match: {monolithic_norm == modular_norm}")

# Test 4: check_fake_config
code3 = """
class Config:
    def do_something(self):
        pass
"""
path3 = Path("fake_config.py")
monolithic_fake = agent.check_fake_config(path3, code3)
modular_fake = check_fake_config(path3, code3)
print(f"Fake config - Monolithic: {monolithic_fake}")
print(f"Fake config - Modular: {modular_fake}")
# Convert Violation to dict for comparison
if modular_fake:
    modular_fake_dict = {
        "type": modular_fake.type,
        "message": modular_fake.message,
        "suggested_suffix": modular_fake.suggested_fix,
    }
    print(f"Fake config match: {monolithic_fake == modular_fake_dict}")
else:
    print(f"Fake config match: {monolithic_fake is None}")

# Test 5: check_domain_root_purity
path4 = Path("knowledge/test_file.py")
monolithic_domain = agent.check_domain_root_purity(path4)
modular_domain = check_domain_root_purity(path4)
print(f"Domain root - Monolithic: {monolithic_domain}")
print(f"Domain root - Modular: {modular_domain}")
if modular_domain:
    modular_domain_dict = {
        "type": modular_domain.type,
        "message": modular_domain.message,
        "suggested_destination": modular_domain.suggested_fix,
    }
    print(f"Domain root match: {monolithic_domain == modular_domain_dict}")
else:
    print(f"Domain root match: {monolithic_domain is None}")

print("\n=== ALL PARALLEL TESTS COMPLETE ===")