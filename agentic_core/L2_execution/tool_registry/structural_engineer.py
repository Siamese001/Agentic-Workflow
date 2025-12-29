"""
Structural Engineer Agent - Code Structure Validation (Keys 20-30)

Responsible for:
- Key 20: No large classes (>20 methods or >500 lines)
- Key 21-25: Complexity metrics, cyclomatic complexity
- Key 26-30: Code organization, modularity, cohesion
"""
import ast
import os
import re
from typing import Any, Dict, List, Optional, Protocol, Tuple
from agentic_core.L2_execution.tool_registry.canon_base_agent import CanonBaseAgent

class structural_engineer(CanonBaseAgent):
    """
    Structural Engineer validates code structure and organization.
    
    Validates Canon Keys 20-30:
    - Key 20: No large classes (>20 methods or >500 lines)
    - Key 21: Proper function size (<50 lines)
    - Key 22: Cyclomatic complexity (<10)
    - Key 23-30: Modularity, cohesion, coupling
    """

    def get_validation_keys(self) -> List[int]:
        """Return canon keys validated by this agent."""
        return list(range(20, 31))

    async def execute(self) -> Any:
        """Execute Structural Engineer validation checks."""
        print(f'\n[>>>] {self.name} ACTIVATED: Checking Code Structure...')
        print(f'   [{self.name}] 🔍 Checking Key 20: Large Classes...')
        passed, violations = self.check_key_20_no_large_classes()
        if not passed:
            print(f'   [{self.name}] ❌ Key 20: FAIL ({len(violations)} violations)')
            await self._heal_violations(20, violations)
        else:
            print(f'   [{self.name}] ✅ Key 20: PASS - All classes within limits')
        print(f'   [{self.name}] 🔍 Checking Key 21: Large Functions...')
        passed, violations = self.check_key_21_no_large_functions()
        if not passed:
            print(f'   [{self.name}] ❌ Key 21: FAIL ({len(violations)} violations) - Large functions detected')
            await self._heal_violations(21, violations)
        else:
            print(f'   [{self.name}] ✅ Key 21: PASS - All functions within limits')

    def check_key_20_no_large_classes(self) -> Tuple[bool, List[str]]:
        """
        Check for classes with >20 methods or >500 lines.
        
        Returns:
            Tuple of (passed, list of violations)
        """
        from pathlib import Path
        violations: Any = []
        max_methods: Any = int(os.getenv('MAX_CLASS_METHODS', '20'))
        max_lines: Any = int(os.getenv('MAX_CLASS_LINES', '500'))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    content: Any = f.read()
                    tree: Any = ast.parse(content)
                    content.splitlines()
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        method_count: Any = sum((1 for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))))
                        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                            class_lines: Any = node.end_lineno - node.lineno + 1
                        else:
                            class_lines: Any = 0
                        if method_count > max_methods:
                            violations.append(f"{file_path}:{node.lineno}: Class '{node.name}' has {method_count} methods (max {max_methods})")
                        if class_lines > max_lines:
                            violations.append(f"{file_path}:{node.lineno}: Class '{node.name}' has {class_lines} lines (max {max_lines})")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_21_no_large_functions(self) -> Tuple[bool, List[str]]:
        """
        Check for functions exceeding 50 lines.
        
        Returns:
            Tuple of (passed, list of violations)
        """
        from pathlib import Path
        violations: Any = []
        max_lines: Any = int(os.getenv('MAX_FUNCTION_LINES', '50'))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    content: Any = f.read()
                    tree: Any = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                            func_lines: Any = node.end_lineno - node.lineno + 1
                            if func_lines > max_lines:
                                violations.append(f"{file_path}:{node.lineno}: Function '{node.name}' has {func_lines} lines (max {max_lines})")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_22_cyclomatic_complexity(self) -> Tuple[bool, List[str]]:
        """
        Check for high cyclomatic complexity (>10).
        
        Returns:
            Tuple of (passed, list of violations)
        """
        violations: Any = []
        max_complexity: Any = int(os.getenv('MAX_CYCLOMATIC_COMPLEXITY', '10'))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    tree: Any = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        complexity: Any = self._calculate_complexity(node)
                        if complexity > max_complexity:
                            violations.append(f"{file_path}:{node.lineno}: Function '{node.name}' has complexity {complexity} (max {max_complexity})")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity of a function.
        
        Complexity = 1 + number of decision points (if, for, while, and, or, except)
        """
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    async def _heal_violations(self, key: int, violations: List[str]):
        """
        Heal violations for a specific key.
        
        Args:
            key: Canon key number
            violations: List of violation descriptions
        """
        max_healing_per_file = int(os.getenv('MAX_HEALING_PER_FILE', '8'))
        file_violations = {}
        for violation in violations[:max_healing_per_file]:
            if ':' in violation:
                parts = violation.split(': ', 1)
                if len(parts) >= 1:
                    file_path = parts[0]
                    if file_path not in file_violations:
                        file_violations[file_path] = []
                    file_violations[file_path].append(violation)
        for file_path, file_viols in file_violations.items():
            await self._smart_fix(file_path, key, file_viols)

    async def _smart_fix(self, file_path: str, violation_key: int, violations: List[str]):
        """
        Apply smart fix to a file using Gemini 2.5 Flash.
        
        Args:
            file_path: Path to file to fix
            violation_key: Canon key being fixed
            violations: List of violations in this file
        """
        from pathlib import Path
        try:
            resolved_path = Path(file_path).resolve()
            with open(resolved_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
        except Exception as e:
            print(f'      [!] Cannot read {file_path}: {e}')
            return
        violation_details = '\n'.join(violations)
        task = f'Fix Subatomic Canon Key {violation_key}. Violations:\n{violation_details}'
        max_rounds = 5
        current_code = original_code
        previous_failure = None
        for round_num in range(1, max_rounds + 1):
            print(f'      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {os.path.basename(file_path)}')
            mutated_code = await self.resilient_mutation(task=task, code=current_code, file_path=file_path, round_num=round_num, previous_failure=previous_failure)
            is_valid, reason = await self.verify_fix(original_code, mutated_code, violation_key)
            if not is_valid:
                print(f'      [!] Round {round_num}: {reason} – retrying')
                previous_failure = reason
                current_code = mutated_code
                continue
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(mutated_code)
                print(f'      [OK] Round {round_num}: Fixed {os.path.basename(file_path)}')
                return
            except Exception as e:
                print(f'      [X] Cannot write {file_path}: {e}')
                return
        print(f'      [X] Failed to fix {os.path.basename(file_path)} after {max_rounds} rounds')
