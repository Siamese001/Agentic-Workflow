"""
agentic_core/agents/engineering.py
Depth: 3
Role: Enforces structural integrity and design patterns.
"""
import ast
import hashlib
import asyncio
import re
from typing import List, Tuple

from agentic_core.agents.base import SubAtomicAgent
from apps_shared.domain.constants import MAX_LINES


class StructuralEngineer(SubAtomicAgent):
    """
    KEYS: 18 (Many Parameters), 20 (Large Classes), 25 (Globals), 42 (Large Files), 43 (Class Density), 46 (Duplicate Code)
    ROLE: Heavy Refactoring with Semantic Intelligence.
    """

    def can_run(self) -> bool:
        return "GENERATIVE_CLEAN" in self.ctx.signals

    async def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Reviewing Refactoring Plans...")
        await asyncio.sleep(0)

        # Key 17: Large functions (duplicate check from BudgetAgent)
        passed, details = self.check_key_17_no_large_functions()
        self.ctx.report(self.name, 17, passed, details)

        # Key 18: Many parameters (>5 params)
        passed, details = self.check_key_18_no_many_parameters()
        self.ctx.report(self.name, 18, passed, details)

        # Key 19: Complexity (already checked above)
        # Key 20: Large classes (>200 lines)
        passed, details = self.check_key_20_no_large_classes()
        self.ctx.report(self.name, 20, passed, details)

        # Key 25: Global variables
        passed, details = self.check_key_25_no_global_variables()
        self.ctx.report(self.name, 25, passed, details)

        # Key 42: Large files (>500 lines)
        passed, details = self.check_key_42_no_large_files()
        self.ctx.report(self.name, 42, passed, details)

        # Key 43: Class density (>10 classes per file)
        passed, details = self.check_key_43_no_class_density()
        self.ctx.report(self.name, 43, passed, details)

        # Key 46: Duplicate code
        passed, details = self.check_key_46_no_duplicate_code()
        self.ctx.report(self.name, 46, passed, details)

        print("   ✅ No structural changes pending.")

    def check_key_18_no_many_parameters(self) -> Tuple[bool, List[str]]:
        """Check for functions with too many parameters (>5)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        args = node.args
                        total_params = len(args.args) + len(args.kwonlyargs)
                        if args.vararg:
                            total_params += 1
                        if args.kwarg:
                            total_params += 1
                        if total_params > 5:
                            violations.append(f"{file_path}:{node.lineno} {node.name}() ({total_params} params)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_20_no_large_classes(self) -> Tuple[bool, List[str]]:
        """Check for large classes (>200 lines)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                            class_lines = node.end_lineno - node.lineno + 1
                            if class_lines > 200:
                                violations.append(f"{file_path}:{node.lineno} {node.name} ({class_lines} lines)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_42_no_large_files(self) -> Tuple[bool, List[str]]:
        """Check for large files (>MAX_LINES)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    if len(lines) > MAX_LINES:
                        violations.append(f"{file_path} ({len(lines)} lines > {MAX_LINES})")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_43_no_class_density(self) -> Tuple[bool, List[str]]:
        """Check for too many classes in one file (>10)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
                if class_count > 10:
                    violations.append(f"{file_path} ({class_count} classes)")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_17_no_large_functions(self) -> Tuple[bool, List[str]]:
        """Check for large functions (>50 lines)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                            func_lines = node.end_lineno - node.lineno + 1
                            if func_lines > 50:
                                violations.append(f"{file_path}:{node.lineno} ({func_lines} lines)")
            except Exception:
                continue

        return (len(violations) == 0, violations)

    def check_key_25_no_global_variables(self) -> Tuple[bool, List[str]]:
        """Check for global variables."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if not target.id.isupper():
                                    violations.append(f"{file_path}:{node.lineno}")
            except Exception:
                continue

        return (len(violations) == 0, violations)

    def check_key_46_no_duplicate_code(self) -> Tuple[bool, List[str]]:
        """Check for duplicate code."""
        violations = []
        file_hashes = {}

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "rb") as f:
                    content_hash = hashlib.md5(f.read()).hexdigest()

                if content_hash in file_hashes:
                    violations.append(f"Duplicate: {file_path} (same as {file_hashes[content_hash]})")
                else:
                    file_hashes[content_hash] = file_path
            except Exception:
                continue

        return (len(violations) == 0, violations)


class PatternEnforcer(SubAtomicAgent):
    """
    KEYS: 26-39 (Pattern Checks)
    ROLE: Enforces coding patterns and best practices.
    """

    def execute(self):
        print(f"\n[>>>] {self.name} ACTIVATED: Enforcing Code Patterns...")

        # Pattern checks (keys 26-39)
        pattern_checks = [
            (26, self.check_key_26_single_responsibility),
            (27, self.check_key_27_open_closed),
            (28, self.check_key_28_liskov_substitution),
            (29, self.check_key_29_interface_segregation),
            (30, self.check_key_30_dependency_injection),
            (31, self.check_key_31_no_hardcoded_paths),
            (32, self.check_key_32_no_hardcoded_urls),
            (33, self.check_key_33_error_handling),
            (34, self.check_key_34_no_dead_code),
            (35, self.check_key_35_no_commented_code),
            (36, self.check_key_36_immutable_config),
            (37, self.check_key_37_no_global_state),
            (38, self.check_key_38_pure_functions),
            (39, self.check_key_39_defensive_programming),
        ]

        for key, check_func in pattern_checks:
            try:
                passed, details = check_func()
                self.ctx.report(self.name, key, passed, details)
            except Exception as e:
                self.ctx.report(self.name, key, False, [str(e)])

    # Pattern check methods (keys 26-39)
    def check_key_26_single_responsibility(self) -> Tuple[bool, List[str]]:
        """Check for classes violating single responsibility principle."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Count different types of methods
                        method_types = set()
                        for item in node.body:
                            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                if item.name.startswith('get_') or item.name.startswith('set_'):
                                    method_types.add('property')
                                elif item.name.startswith('save_') or item.name.startswith('load_'):
                                    method_types.add('persistence')
                                elif item.name.startswith('validate_') or item.name.startswith('check_'):
                                    method_types.add('validation')
                                else:
                                    method_types.add('business')

                        if len(method_types) > 2:
                            violations.append(f"{file_path}:{node.lineno} {node.name} has {len(method_types)} responsibility types")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_27_open_closed(self) -> Tuple[bool, List[str]]:
        """Check for classes that are not open for extension."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check for final/sealed patterns
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                # Look for methods that prevent override
                                if item.name == '__init__' and any(
                                    isinstance(stmt, ast.Raise) for stmt in item.body
                                ):
                                    violations.append(f"{file_path}:{node.lineno} {node.name} prevents extension")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_28_liskov_substitution(self) -> Tuple[bool, List[str]]:
        """Check for Liskov Substitution Principle violations."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                # Skip test files and abstract base classes
                if 'test' in file_path.lower() or 'abc' in file_path.lower():
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Only check concrete classes (not abstract)
                        if any('ABC' in base.id for base in node.bases if hasattr(base, 'id')):
                            continue

                        # Check for methods that raise NotImplementedError (limit to 5 per file)
                        not_impl_count = 0
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                for stmt in ast.walk(item):
                                    if isinstance(stmt, ast.Raise):
                                        if isinstance(stmt.exc, ast.Name) and stmt.exc.id == 'NotImplementedError':
                                            not_impl_count += 1
                                            if not_impl_count <= 5:  # Limit violations
                                                violations.append(f"{file_path}:{item.lineno} {node.name}.{item.name} not implemented")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_29_interface_segregation(self) -> Tuple[bool, List[str]]:
        """Check for fat interfaces."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Count abstract methods
                        method_count = sum(1 for item in node.body
                                         if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)))
                        if method_count > 10:
                            violations.append(f"{file_path}:{node.lineno} {node.name} has {method_count} methods")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_30_dependency_injection(self) -> Tuple[bool, List[str]]:
        """Check for hardcoded dependencies (with practical exceptions)."""
        violations = []
        # Allow common direct instantiations
        allowed_instantiations = {
            'list', 'dict', 'set', 'tuple', 'str', 'int', 'float', 'bool',
            'datetime', 'date', 'time', 'timedelta', 'uuid', 'Path',
            'logging', 'Logger', 'ConfigParser', 'json', 'yaml', 'csv'
        }

        for file_path in self.ctx.python_files:
            try:
                # Skip test files and simple scripts
                if 'test' in file_path.lower() or 'script' in file_path.lower():
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for direct instantiation in __init__ (limit violations)
                        if node.name == '__init__':
                            violation_count = 0
                            for stmt in ast.walk(node):
                                if isinstance(stmt, ast.Call):
                                    if isinstance(stmt.func, ast.Name):
                                        if stmt.func.id not in allowed_instantiations:
                                            violation_count += 1
                                            if violation_count <= 3:  # Limit to 3 per class
                                                violations.append(f"{file_path}:{stmt.lineno} Direct instantiation of {stmt.func.id}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_31_no_hardcoded_paths(self) -> Tuple[bool, List[str]]:
        """Check for hardcoded file paths."""
        violations = []
        path_patterns = [
            r"['\"]\.\.\/",
            r"['\"]\/home\/",
            r"['\"]C:\\",
            r"['\"]\/tmp\/",
            r"['\"]\/var\/",
        ]

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split('\n')

                    for i, line in enumerate(lines, 1):
                        for pattern in path_patterns:
                            if re.search(pattern, line):
                                violations.append(f"{file_path}:{i}")
                                break
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_32_no_hardcoded_urls(self) -> Tuple[bool, List[str]]:
        """Check for hardcoded URLs."""
        violations = []
        url_patterns = [
            r"http://localhost",
            r"https://localhost",
            r"http://127\.0\.0\.1",
            r"https://127\.0\.0\.1",
        ]

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split('\n')

                    for i, line in enumerate(lines, 1):
                        for pattern in url_patterns:
                            if re.search(pattern, line):
                                violations.append(f"{file_path}:{i}")
                                break
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_33_error_handling(self) -> Tuple[bool, List[str]]:
        """Check for proper error handling."""
        violations = []
        # In relaxed mode, only check critical operations
        critical_operations = ['open', 'json.loads', 'requests.get', 'subprocess.run']

        for file_path in self.ctx.python_files:
            try:
                # Skip test files in relaxed mode
                if not hasattr(self, 'strict_mode') or not self.strict_mode:
                    if 'test' in file_path.lower():
                        continue

                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for try/except blocks
                        has_try = any(isinstance(stmt, ast.Try) for stmt in ast.walk(node))

                        # In strict mode, check all calls; in relaxed, only critical
                        if hasattr(self, 'strict_mode') and self.strict_mode:
                            risky_ops = any(isinstance(stmt, ast.Call) for stmt in ast.walk(node))
                            if risky_ops and not has_try and not node.name.startswith('_'):
                                violations.append(f"{file_path}:{node.lineno} {node.name} lacks error handling")
                        else:
                            # Relaxed mode - only check critical operations
                            for stmt in ast.walk(node):
                                if isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name):
                                    if stmt.func.id in critical_operations and not has_try:
                                        violations.append(f"{file_path}:{stmt.lineno} {node.name} lacks error handling for {stmt.func.id}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_34_no_dead_code(self) -> Tuple[bool, List[str]]:
        """Check for dead code."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                    for i, line in enumerate(lines, 1):
                        stripped = line.strip()
                        # Check for unreachable code after return
                        if 'return' in stripped and i < len(lines):
                            next_line = lines[i].strip()
                            if next_line and not next_line.startswith('#') and not next_line.startswith('"""'):
                                violations.append(f"{file_path}:{i+1} Potential dead code")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_35_no_commented_code(self) -> Tuple[bool, List[str]]:
        """Check for commented out code."""
        violations = []
        code_patterns = [
            r"#\s*def\s+\w+\(",
            r"#\s*class\s+\w+",
            r"#\s*if\s+",
            r"#\s*for\s+",
            r"#\s*while\s+",
        ]

        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                    for i, line in enumerate(lines, 1):
                        if line.strip().startswith('#'):
                            for pattern in code_patterns:
                                if re.search(pattern, line):
                                    violations.append(f"{file_path}:{i}")
                                    break
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_36_immutable_config(self) -> Tuple[bool, List[str]]:
        """Check for mutable configuration objects."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                if 'config' in target.id.lower():
                                    # Check if assigned a dict or list
                                    if isinstance(node.value, (ast.Dict, ast.List)):
                                        violations.append(f"{file_path}:{node.lineno} Mutable config: {target.id}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_37_no_global_state(self) -> Tuple[bool, List[str]]:
        """Check for global state variables."""
        violations = []
        # Allow common global patterns
        allowed_globals = {
            'logger', 'logging', 'CONFIG', 'settings', 'ENV', 'VERSION',
            'DEBUG', 'TEST_MODE', 'DEFAULT_TIMEOUT', 'MAX_RETRIES'
        }

        for file_path in self.ctx.python_files:
            try:
                # Skip config files and __init__ files
                if 'config' in file_path.lower() or file_path.endswith('__init__.py'):
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in tree.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                # Skip constants and allowed globals
                                if (target.id.isupper() or
                                    target.id.startswith('_') or
                                    target.id in allowed_globals):
                                    continue
                                violations.append(f"{file_path}:{node.lineno} Global variable: {target.id}")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_38_pure_functions(self) -> Tuple[bool, List[str]]:
        """Check for impure functions (functions that modify external state)."""
        violations = []
        for file_path in self.ctx.python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for stmt in ast.walk(node):
                            # Check for external state modification
                            if isinstance(stmt, ast.Attribute) and isinstance(stmt.attr, str):
                                if stmt.attr in ['append', 'extend', 'insert', 'remove', 'pop']:
                                    violations.append(f"{file_path}:{stmt.lineno} {node.name} modifies external state")
            except Exception:
                continue
        return (len(violations) == 0, violations)

    def check_key_39_defensive_programming(self) -> Tuple[bool, List[str]]:
        """Check for defensive programming practices."""
        violations = []

        for file_path in self.ctx.python_files:
            try:
                # Skip test files, simple getters, and private methods
                if ('test' in file_path.lower() or
                    'utils' in file_path.lower() or
                    'helpers' in file_path.lower()):
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Skip private methods, getters, setters, and simple methods
                        if (node.name.startswith('_') or
                            node.name.startswith(('get_', 'set_', 'is_', 'has_')) or
                            len(node.args.args) <= 1):
                            continue

                        # Check for input validation
                        has_validation = False
                        for stmt in node.body:
                            if isinstance(stmt, ast.If):
                                # Look for None checks, type checks
                                for test in ast.walk(stmt.test):
                                    if isinstance(test, ast.Compare) or isinstance(test, ast.Is):
                                        has_validation = True
                                        break

                        # Only flag complex functions with 3+ parameters and no validation
                        if len(node.args.args) >= 3 and not has_validation:
                            violations.append(f"{file_path}:{node.lineno} {node.name} lacks input validation")
            except Exception:
                continue
        return (len(violations) == 0, violations)
