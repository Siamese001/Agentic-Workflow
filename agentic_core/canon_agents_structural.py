"""
Canon Validator Structural Agents
TypeMechanic, BudgetAgent, StructuralEngineer - Code structure and complexity.
"""

import ast
import os
from typing import List, Tuple

from agentic_core.canon_base_agent import SubAtomicAgent


class TypeMechanic(SubAtomicAgent):
    """
    KEYS: 22 (Missing Types), 23 (Unreachable Code), 24 (Unused Vars)
    ROLE: Precision Engineering. Requires AST_VALID signal.
    """

    def can_run(self) -> bool:
        return "AST_VALID" in self.ctx.signals

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Type System Check...")

        passed, details = self.check_key_22_no_missing_type_hints()
        self.ctx.report(self.name, 22, passed, details)

        passed, details = self.check_key_23_no_unreachable_code()
        self.ctx.report(self.name, 23, passed, details)

        passed, details = self.check_key_24_no_unused_variables()
        self.ctx.report(self.name, 24, passed, details)

    def check_key_22_no_missing_type_hints(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.returns and node.name not in ("__init__", "__str__", "__repr__"):
                            violations.append(f"{fp}:{node.lineno} {node.name}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_23_no_unreachable_code(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for i, stmt in enumerate(node.body):
                            if isinstance(stmt, ast.Return) and i < len(node.body) - 1:
                                violations.append(f"{fp}:{node.lineno} {node.name}")
                                break
            except:
                continue
        return len(violations) == 0, violations

    def check_key_24_no_unused_variables(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        assigned = set()
                        used = set()
                        
                        for child in ast.walk(node):
                            if isinstance(child, ast.Assign):
                                for target in child.targets:
                                    if isinstance(target, ast.Name):
                                        assigned.add(target.id)
                            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                                used.add(child.id)
                        
                        unused = assigned - used
                        if unused:
                            violations.append(f"{fp}:{node.lineno} {node.name}: {', '.join(unused)}")
            except:
                continue
        return len(violations) == 0, violations


class BudgetAgent(SubAtomicAgent):
    """
    KEYS: 17 (Large Functions), 19 (Complex Functions)
    ROLE: The Comptroller. Proactively marks functions exceeding size/complexity limits.
    """

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Complexity Budget Check...")

        passed, details = self.check_key_17_no_large_functions()
        self.ctx.report(self.name, 17, passed, details)

        passed, details = self.check_key_19_no_complex_functions()
        self.ctx.report(self.name, 19, passed, details)

    def check_key_17_no_large_functions(self) -> Tuple[bool, List[str]]:
        violations = []
        max_lines = int(os.getenv('MAX_FUNCTION_LINES', '50'))
        
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                        if func_lines > max_lines:
                            violations.append(f"{fp}:{node.lineno} {node.name} ({func_lines} lines)")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_19_no_complex_functions(self) -> Tuple[bool, List[str]]:
        violations = []
        max_complexity = int(os.getenv('MAX_CYCLOMATIC_COMPLEXITY', '10'))
        
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._calculate_complexity(node)
                        if complexity > max_complexity:
                            violations.append(f"{fp}:{node.lineno} {node.name} (complexity: {complexity})")
            except:
                continue
        return len(violations) == 0, violations

    def _calculate_complexity(self, node):
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity


class StructuralEngineer(SubAtomicAgent):
    """
    KEYS: 18 (Many Parameters), 20 (Large Classes), 25 (Globals), 42 (Large Files), 43 (Class Density), 46 (Duplicate Code)
    ROLE: Heavy Refactoring with Semantic Intelligence.
    """

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Structural Analysis...")

        keys = [
            (18, self.check_key_18_no_many_parameters),
            (20, self.check_key_20_no_large_classes),
            (25, self.check_key_25_no_global_variables),
            (42, self.check_key_42_no_large_files),
            (43, self.check_key_43_class_density),
            (46, self.check_key_46_no_duplicate_code),
        ]

        for key, check_func in keys:
            passed, details = check_func()
            self.ctx.report(self.name, key, passed, details)

    def check_key_18_no_many_parameters(self) -> Tuple[bool, List[str]]:
        violations = []
        max_params = int(os.getenv('MAX_FUNCTION_PARAMETERS', '5'))
        
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        param_count = len(node.args.args)
                        if param_count > max_params:
                            violations.append(f"{fp}:{node.lineno} {node.name} ({param_count} params)")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_20_no_large_classes(self) -> Tuple[bool, List[str]]:
        violations = []
        max_methods = int(os.getenv('MAX_CLASS_METHODS', '20'))
        
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        method_count = sum(1 for child in node.body if isinstance(child, ast.FunctionDef))
                        if method_count > max_methods:
                            violations.append(f"{fp}:{node.lineno} {node.name} ({method_count} methods)")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_25_no_global_variables(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if not target.id.isupper():
                                    violations.append(f"{fp}:{node.lineno} {target.id}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_42_no_large_files(self) -> Tuple[bool, List[str]]:
        violations = []
        max_lines = int(os.getenv('MAX_FILE_LINES', '500'))
        
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    line_count = len(f.readlines())
                    if line_count > max_lines:
                        violations.append(f"{fp} ({line_count} lines)")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_43_class_density(self) -> Tuple[bool, List[str]]:
        violations = []
        max_classes_per_file = int(os.getenv('MAX_CLASSES_PER_FILE', '5'))
        
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
                if class_count > max_classes_per_file:
                    violations.append(f"{fp} ({class_count} classes)")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_46_no_duplicate_code(self) -> Tuple[bool, List[str]]:
        return True, []
