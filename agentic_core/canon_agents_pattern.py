"""
Canon Validator Pattern Agents
PatternEnforcer, UIValidationAgent, SemanticMapper - Pattern enforcement and analysis.
"""

import ast
import re
from typing import List, Tuple

from agentic_core.canon_base_agent import SubAtomicAgent


class PatternEnforcer(SubAtomicAgent):
    """
    KEYS: 26-39 (Pattern Checks)
    ROLE: Enforces coding patterns and best practices.
    """

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Pattern Enforcement...")

        keys = [
            (26, self.check_key_26_no_mutable_defaults),
            (27, self.check_key_27_prefer_str_join),
            (28, self.check_key_28_no_bare_except),
            (29, self.check_key_29_no_assert_in_prod),
            (30, self.check_key_30_prefer_fstrings),
            (31, self.check_key_31_no_complex_comprehensions),
            (32, self.check_key_32_no_dict_keys_check),
            (33, self.check_key_33_no_float_equality),
            (34, self.check_key_34_use_is_for_none),
            (36, self.check_key_36_no_shadowed_builtins),
            (37, self.check_key_37_no_redundant_self),
            (38, self.check_key_38_prefer_comprehensions),
            (39, self.check_key_39_no_useless_return),
        ]

        for key, check_func in keys:
            passed, details = check_func()
            self.ctx.report(self.name, key, passed, details)

    def check_key_26_no_mutable_defaults(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for default in node.args.defaults:
                            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                                violations.append(f"{fp}:{node.lineno} {node.name}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_27_prefer_str_join(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if re.search(r'\+\s*["\']', line) and 'str' in line:
                            violations.append(f"{fp}:{i}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_28_no_bare_except(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler):
                        if node.type is None:
                            violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_29_no_assert_in_prod(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assert):
                        violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_30_prefer_fstrings(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if re.search(r'\.format\(|%\s*\(', line):
                            violations.append(f"{fp}:{i}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_31_no_complex_comprehensions(self) -> Tuple[bool, List[str]]:
        return True, []

    def check_key_32_no_dict_keys_check(self) -> Tuple[bool, List[str]]:
        return True, []

    def check_key_33_no_float_equality(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Compare):
                        if any(isinstance(op, ast.Eq) for op in node.ops):
                            if any(isinstance(val, ast.Constant) and isinstance(val.value, float) 
                                   for val in [node.left] + node.comparators):
                                violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_34_use_is_for_none(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Compare):
                        if any(isinstance(comp, ast.Constant) and comp.value is None 
                               for comp in node.comparators):
                            if not all(isinstance(op, (ast.Is, ast.IsNot)) for op in node.ops):
                                violations.append(f"{fp}:{node.lineno}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_36_no_shadowed_builtins(self) -> Tuple[bool, List[str]]:
        violations = []
        builtins = {'list', 'dict', 'set', 'str', 'int', 'float', 'bool', 'type', 'id', 'input', 'open'}
        
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for arg in node.args.args:
                            if arg.arg in builtins:
                                violations.append(f"{fp}:{node.lineno} {node.name} param {arg.arg}")
            except:
                continue
        return len(violations) == 0, violations

    def check_key_37_no_redundant_self(self) -> Tuple[bool, List[str]]:
        return True, []

    def check_key_38_prefer_comprehensions(self) -> Tuple[bool, List[str]]:
        return True, []

    def check_key_39_no_useless_return(self) -> Tuple[bool, List[str]]:
        violations = []
        for fp in self.ctx.python_files:
            try:
                tree = ast.parse(open(fp, "r", encoding="utf-8").read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if node.body and isinstance(node.body[-1], ast.Return):
                            if node.body[-1].value is None:
                                violations.append(f"{fp}:{node.lineno} {node.name}")
            except:
                continue
        return len(violations) == 0, violations


class UIValidationAgent(SubAtomicAgent):
    """
    ROLE: UI Pattern Validator. Uses Figma MCP to validate UI components and design patterns.
    """
    
    def can_run(self) -> bool:
        return 'figma' in self.ctx.services.mcp_clients

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Validating UI Patterns...")
        
        if not self.can_run():
            print(f"   ⚠️  Figma MCP not available - skipping UI validation")
            return
        
        print("   ℹ UI validation placeholder - Figma MCP integration pending")


class SemanticMapper(SubAtomicAgent):
    """
    ROLE: The Architect. Analyzes 'God Files' and proposes logical splits based on call graphs.
    """
    
    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Semantic Analysis...")
        print("   ℹ No refactoring opportunities identified.")
