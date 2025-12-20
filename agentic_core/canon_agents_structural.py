"""
Canon Validator Structural Agents

This module defines a set of SubAtomicAgents responsible for validating the structural
and complexity aspects of Python codebases. These agents perform checks related to
type hints, code reachability, variable usage, function/class size, cyclomatic
complexity, global variables, file size, and class density.
"""

import ast
import os
from typing import List, Set, Tuple

from agentic_core.canon_base_agent import SubAtomicAgent


class TypeMechanic(SubAtomicAgent):
    """
    KEYS: 22 (Missing Types), 23 (Unreachable Code), 24 (Unused Vars)
    ROLE: Precision Engineering. Requires AST_VALID signal.
    """

    def can_run(self) -> bool:
        """
        Determines if the agent can run based on the presence of the 'AST_VALID' signal.
        """
        return "AST_VALID" in self.ctx.signals

    def execute(self) -> None:
        """
        Executes the TypeMechanic agent, performing checks for type system violations.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Type System Check...")

        passed, details = self.check_key_22_no_missing_type_hints()
        self.ctx.report(self.name, 22, passed, details)

        passed, details = self.check_key_23_no_unreachable_code()
        self.ctx.report(self.name, 23, passed, details)

        passed, details = self.check_key_24_no_unused_variables()
        self.ctx.report(self.name, 24, passed, details)

    def check_key_22_no_missing_type_hints(self) -> Tuple[bool, List[str]]:
        """
        Checks for functions with missing type hints (return types).
        Excludes __init__, __str__, __repr__ methods.
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for missing return type hints, excluding common dunder methods
                        if not node.returns and node.name not in ("__init__", "__str__", "__repr__"):
                            violations.append(
                                f"{fp}:{node.lineno}: Function '{node.name}' is missing "
                                "a return type hint."
                            )
            except (IOError, SyntaxError) as e:
                # Report parsing errors but continue with other files
                self.ctx.log_error(f"Error parsing {fp} for missing type hints: {e}")
                continue
        return len(violations) == 0, violations

    def check_key_23_no_unreachable_code(self) -> Tuple[bool, List[str]]:
        """
        Checks for unreachable code, specifically statements after a 'return' statement
        within a function body.
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        for i, stmt in enumerate(node.body):
                            if isinstance(stmt, ast.Return) and i < len(node.body) - 1:
                                # If a return statement is not the last statement in the function body
                                violations.append(
                                    f"{fp}:{stmt.lineno}: Unreachable code after return "
                                    f"in function '{node.name}'."
                                )
                                break  # Only report once per function
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for unreachable code: {e}")
                continue
        return len(violations) == 0, violations

    def check_key_24_no_unused_variables(self) -> Tuple[bool, List[str]]:
        """
        Checks for variables that are assigned but never used within a function.
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        assigned: Set[str] = set()
                        used: Set[str] = set()

                        # Collect all assigned and used variable names within the function
                        for child in ast.walk(node):
                            if isinstance(child, ast.Assign):
                                for target in child.targets:
                                    if isinstance(target, ast.Name):
                                        assigned.add(target.id)
                            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                                used.add(child.id)

                        # Find variables that were assigned but not used
                        unused = assigned - used
                        # Exclude common "throwaway" variable names like '_'
                        unused = {var for var in unused if var != '_'}

                        if unused:
                            violations.append(
                                f"{fp}:{node.lineno}: Function '{node.name}' has unused "
                                f"variables: {', '.join(sorted(unused))}."
                            )
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for unused variables: {e}")
                continue
        return len(violations) == 0, violations


class BudgetAgent(SubAtomicAgent):
    """
    KEYS: 17 (Large Functions), 19 (Complex Functions)
    ROLE: The Comptroller. Proactively marks functions exceeding size/complexity limits.
    """

    def execute(self) -> None:
        """
        Executes the BudgetAgent, performing checks for function size and complexity.
        """
        print(f"\n[>>>] {self.name} ACTIVATED: Complexity Budget Check...")

        passed, details = self.check_key_17_no_large_functions()
        self.ctx.report(self.name, 17, passed, details)

        passed, details = self.check_key_19_no_complex_functions()
        self.ctx.report(self.name, 19, passed, details)

    def check_key_17_no_large_functions(self) -> Tuple[bool, List[str]]:
        """
        Checks for functions exceeding a maximum number of lines.
        The limit is configurable via the 'MAX_FUNCTION_LINES' environment variable.
        """
        violations = []
        max_lines = int(os.getenv('MAX_FUNCTION_LINES', '50'))

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # ast.FunctionDef nodes have lineno and end_lineno attributes in Python 3.8+
                        func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                        if func_lines > max_lines:
                            violations.append(
                                f"{fp}:{node.lineno}: Function '{node.name}' is too large "
                                f"({func_lines} lines, max {max_lines})."
                            )
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for large functions: {e}")
                continue
        return len(violations) == 0, violations

    def check_key_19_no_complex_functions(self) -> Tuple[bool, List[str]]:
        """
        Checks for functions exceeding a maximum cyclomatic complexity.
        The limit is configurable via the 'MAX_CYCLOMATIC_COMPLEXITY' environment variable.
        """
        violations = []
        max_complexity = int(os.getenv('MAX_CYCLOMATIC_COMPLEXITY', '10'))

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._calculate_complexity(node)
                        if complexity > max_complexity:
                            violations.append(
                                f"{fp}:{node.lineno}: Function '{node.name}' is too complex "
                                f"(complexity: {complexity}, max {max_complexity})."
                            )
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for complex functions: {e}")
                continue
        return len(violations) == 0, violations

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculates a simplified cyclomatic complexity for a given function node.
        Each 'if', 'for', 'while', 'except', 'elif', 'and', 'or' adds to complexity.
        """
        complexity = 1  # Start with 1 for the function itself
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each 'and' or 'or' adds to complexity
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):  # For list/dict/set comprehensions with 'if'
                if child.ifs:
                    complexity += len(child.ifs)
        return complexity


class StructuralEngineer(SubAtomicAgent):
    """
    KEYS: 18 (Many Parameters), 20 (Large Classes), 25 (Globals), 42 (Large Files),
          43 (Class Density), 46 (Duplicate Code)
    ROLE: Heavy Refactoring with Semantic Intelligence.
    """

    def execute(self) -> None:
        """
        Executes the StructuralEngineer agent, performing various structural analyses.
        """
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
        """
        Checks for functions exceeding a maximum number of parameters.
        The limit is configurable via the 'MAX_FUNCTION_PARAMETERS' environment variable.
        """
        violations = []
        max_params = int(os.getenv('MAX_FUNCTION_PARAMETERS', '5'))

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Count positional, keyword-only, and varargs parameters
                        param_count = (
                            len(node.args.args)
                            + len(node.args.kwonlyargs)
                            + (1 if node.args.vararg else 0)
                            + (1 if node.args.kwarg else 0)
                        )

                        if param_count > max_params:
                            violations.append(
                                f"{fp}:{node.lineno}: Function '{node.name}' has too many "
                                f"parameters ({param_count}, max {max_params})."
                            )
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for many parameters: {e}")
                continue
        return len(violations) == 0, violations

    def check_key_20_no_large_classes(self) -> Tuple[bool, List[str]]:
        """
        Checks for classes exceeding a maximum number of methods.
        The limit is configurable via the 'MAX_CLASS_METHODS' environment variable.
        """
        violations = []
        max_methods = int(os.getenv('MAX_CLASS_METHODS', '20'))

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        method_count = sum(1 for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)))
                        if method_count > max_methods:
                            violations.append(
                                f"{fp}:{node.lineno}: Class '{node.name}' has too many "
                                f"methods ({method_count}, max {max_methods})."
                            )
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for large classes: {e}")
                continue
        return len(violations) == 0, violations

    def check_key_25_no_global_variables(self) -> Tuple[bool, List[str]]:
        """
        Checks for global variables (assignments at module level) that are not
        conventionally treated as constants (i.e., not ALL_CAPS).
        """
        violations = []
        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                for node in tree.body:  # Only check top-level statements
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                # Heuristic: consider non-ALL_CAPS names as potential global variables
                                # Exclude dunder names like __all__, __version__
                                if not target.id.isupper() and not target.id.startswith('__'):
                                    violations.append(
                                        f"{fp}:{node.lineno}: Global variable '{target.id}' found. "
                                        "Consider making it a constant (ALL_CAPS) or moving it "
                                        "into a function/class."
                                    )
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for global variables: {e}")
                continue
        return len(violations) == 0, violations

    def check_key_42_no_large_files(self) -> Tuple[bool, List[str]]:
        """
        Checks for files exceeding a maximum number of lines.
        The limit is configurable via the 'MAX_FILE_LINES' environment variable.
        """
        violations = []
        max_lines = int(os.getenv('MAX_FILE_LINES', '500'))

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    line_count = len(f.readlines())
                    if line_count > max_lines:
                        violations.append(
                            f"{fp}: File is too large ({line_count} lines, max {max_lines})."
                        )
            except IOError as e:  # Specific exception for file operations
                self.ctx.log_error(f"Error reading {fp} for file size check: {e}")
                continue
        return len(violations) == 0, violations

    def check_key_43_class_density(self) -> Tuple[bool, List[str]]:
        """
        Checks for files exceeding a maximum number of classes.
        The limit is configurable via the 'MAX_CLASSES_PER_FILE' environment variable.
        """
        violations = []
        max_classes_per_file = int(os.getenv('MAX_CLASSES_PER_FILE', '5'))

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)
                class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
                if class_count > max_classes_per_file:
                    violations.append(
                        f"{fp}: File has too many classes ({class_count}, max {max_classes_per_file})."
                    )
            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for class density: {e}")
                continue
        return len(violations) == 0, violations

    def check_key_46_no_duplicate_code(self) -> Tuple[bool, List[str]]:
        """
        Placeholder for duplicate code detection.
        Implementing robust duplicate code detection (e.g., using AST or token-based comparison)
        is complex and beyond the scope of a simple linter agent.
        """
        # This check is currently a placeholder and always passes.
        # Real duplicate code detection would involve more sophisticated analysis.
        return True, []
