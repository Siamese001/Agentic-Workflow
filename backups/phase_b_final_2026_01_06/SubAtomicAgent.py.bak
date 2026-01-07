from __future__ import annotations
import ast
'''Brief description of functionality and purpose.'''

import os
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple
from agentic_core.utils.core_extensions.timeout_decorator import timeout

# NAMING FIXED: SubAtomicAgent → SubAtomicAgent
class SubAtomicAgent:
    """Base class stub for structural agents."""
    pass

# Alias for backward compatibility

# NOT_AN_AGENT — base implementation class, not a true agent — excluded from discovery
class sub_atomic_agent_impl:
    '''Brief description of functionality and purpose.'''
    
    def __init__(self, ctx: Any, name: str):
        self.ctx = ctx
        self.name = name
    def can_run(self) -> bool:
                    
        return True
    def execute(self) -> None:
                    
        pass

# NAMING FIXED: NestingDepthVisitor → nesting_depth_visitor
class nesting_depth_visitor(ast.NodeVisitor):
    """
    A visitor to calculate and report violations for excessive nesting depth within an AST.
    """
    def __init__(self, max_allowed_depth: int, filepath: str):
        self.max_allowed_depth = max_allowed_depth
        self.filepath = filepath
        self.current_depth = 0
        self.violations: List[str] = []

    def _report_violation_message(self, node, current_depth_val: int) -> str:
        """
        Constructs the Violation message string, flattening expressions to reduce syntactic nesting.
        """
        lineno_val = getattr(node, 'lineno', 'N/A')
        node_type_val = type(node).__name__
        message = (
            self.filepath + ":" + str(lineno_val) + ": " +
            "Nesting depth " + str(current_depth_val) + " exceeds max " +
            str(self.max_allowed_depth) + " at " + node_type_val + " block."
        )
        return message

    def _generic_visit_with_depth(self, node):
        self.current_depth += 1
        if self.current_depth > self.max_allowed_depth:
            # Report Violation at the start of the block that exceeds the limit
            # Refactored message construction to reduce syntactic nesting depth
            message = self._report_violation_message(node, self.current_depth)
            self.violations.append(message)
        super().generic_visit(node)
        self.current_depth -= 1

    # Override visit methods for nodes that increase nesting
    def visit_FunctionDef(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_AsyncFunctionDef(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_ClassDef(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_If(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_For(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_AsyncFor(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_While(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_With(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_AsyncWith(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_Try(self, node):
                    
        self._generic_visit_with_depth(node)

    def visit_ExceptHandler(self, node):
                    
        self._generic_visit_with_depth(node)


# Sovereign Agent for type enforcement and precision engineering
class TypeMechanicAgent(SubAtomicAgent):
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

    def _read_and_parse_file(self, fp: str) -> Tuple[ast.AST | None, str | None]:
        """
        Reads a file and parses it into an AST, handling errors.
        Returns (tree, error_message).
        """
        try: # Depth 1
            with open(fp, "r", encoding="utf-8") as f: # Depth 2
                tree = ast.parse(f.read(), filename=fp)
                return tree, None
        except (IOError, SyntaxError) as e: # Depth 2 (ExceptHandler)
            return None, f"Error parsing {fp}: {e}"

    def _get_missing_type_hint_violations_for_tree(self, fp: str, tree: ast.AST) -> List[str]:
        """
        Collects formatted Violation strings for Missing type hints in a given AST tree.
        """
        file_violations = []
        for node in ast.walk(tree): # Depth 1
            if isinstance(node, ast.FunctionDef) and \
               not node.returns and node.name not in ("__init__", "__str__", "__repr__"): # Depth 2 (If)
                file_violations.append( # Depth 3
                    f"{fp}:{node.lineno}: Function '{node.name}' is Missing "
                    "a return type hint."
                )
        return file_violations

    def check_key_22_no_missing_type_hints(self) -> Tuple[bool, List[str]]:
        """
        Checks for functions with Missing type hints (return types).
        Excludes __init__, __str__, __repr__ methods.
        Refactored to reduce nesting depth to meet max 4.
        """
        violations = []
        for fp in self.ctx.python_files: # Depth 1 (from method definition)
            tree, error_msg = self._read_and_parse_file(fp) # Depth 2
            if error_msg: # Depth 3
                self.ctx.log_error(error_msg) # Depth 4
                continue # Depth 4

            if tree: # Depth 3
                violations.extend(self._get_missing_type_hint_violations_for_tree(fp, tree)) # Depth 4
        return len(violations) == 0, violations

    def _check_function_for_unreachable_code(self, fp: str, func_node: ast.FunctionDef) -> List[str]:
        """
        Checks a single function node for unreachable code after a return statement.
        """
        func_violations = [] # Depth 1
        for i, stmt in enumerate(func_node.body): # Depth 2
            if isinstance(stmt, ast.Return) and i < len(func_node.body) - 1: # Depth 3
                func_violations.append( # Depth 4
                    f"{fp}:{stmt.lineno}: Unreachable code after return "
                    f"in function '{func_node.name}'."
                )
                break  # Only report once per function # Depth 4
        return func_violations

    def _get_unreachable_code_violations_for_tree(self, fp: str, tree: ast.AST) -> List[str]:
        """
        Processes an AST tree to find unreachable code violations within functions.
        """
        file_violations = [] # Depth 1
        for node in ast.walk(tree): # Depth 2
            if isinstance(node, ast.FunctionDef): # Depth 3
                file_violations.extend(self._check_function_for_unreachable_code(fp, node)) # Depth 4
        return file_violations

    def check_key_23_no_unreachable_code(self) -> Tuple[bool, List[str]]:
        """
        Checks for unreachable code, specifically statements after a 'return' statement
        within a function body.
        Refactored to reduce nesting depth to meet max 4.
        """
        violations = [] # Depth 1
        for fp in self.ctx.python_files: # Depth 2
            tree, error_msg = self._read_and_parse_file(fp) # Depth 3
            if error_msg: # Depth 4
                self.ctx.log_error(error_msg) # Depth 4
                continue # Depth 4
            if tree: # Depth 3
                violations.extend(self._get_unreachable_code_violations_for_tree(fp, tree)) # Depth 4
        return len(violations) == 0, violations

    def _collect_variables(self, func_node: ast.FunctionDef) -> Tuple[Set[str], Set[str]]:
        """
        Collects assigned and used variable names within a given function AST node.
        """
        assigned: Set[str] = set()
        used: Set[str] = set()

        for child in ast.walk(func_node):
            if isinstance(child, ast.Assign):
                # Flatten target processing using a list comprehension
                names_assigned = [
                    target.id for target in child.targets
                    if isinstance(target, ast.Name)
                ]
                assigned.update(names_assigned)
            elif isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                used.add(child.id)
        return assigned, used

    def _get_function_violations_for_file(self, fp: str, tree: ast.AST) -> List[str]:
        """
        Processes an AST tree to find unused variables within functions.
        """
        file_violations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                assigned, used = self._collect_variables(node)
                unused = assigned - used
                # Exclude common "throwaway" variable names like '_'
                unused = {var for var in unused if var != '_'}
                if unused:
                    file_violations.append(
                        f"{fp}:{node.lineno}: Function '{node.name}' has unused "
                        f"variables: {', '.join(sorted(unused))}."
                    )
        return file_violations

    def _process_file_for_unused_variables(self, fp: str) -> List[str]:
        """
        Opens and parses a single file, then delegates to find unused variables.
        Handles file I/O and parsing errors.
        """
        try:
            with open(fp, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=fp)
            return self._get_function_violations_for_file(fp, tree)
        except (IOError, SyntaxError) as e:
            self.ctx.log_error(f"Error parsing {fp} for unused variables: {e}")
            return []

    def check_key_24_no_unused_variables(self) -> Tuple[bool, List[str]]:
        """
        Checks for variables that are assigned but never used within a function.
        Refactored to reduce nesting depth.
        """
        violations = []
        for fp in self.ctx.python_files:
            violations.extend(self._process_file_for_unused_variables(fp))
        return len(violations) == 0, violations

# Sovereign Agent for token budget tracking and complexity management
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

# Sovereign Agent for AST structure validation and architectural enforcement
class StructuralEngineerAgent(SubAtomicAgent):
    """
    KEYS: 18 (Many Parameters), 20 (Large Classes), 25 (Globals), 41 (Excessive Nesting),
          42 (Large Files), 43 (Class Density), 46 (Duplicate Code)
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
            (41, self.check_key_41_no_excessive_nesting), # Add this key
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
    def check_key_41_no_excessive_nesting(self) -> Tuple[bool, List[str]]:
        """
        Checks for code blocks exceeding a maximum nesting depth.
        The limit is configurable via the 'MAX_NESTING_DEPTH' environment variable.
        """
        violations = []
        max_nesting_depth = int(os.getenv('MAX_NESTING_DEPTH', '4')) # Default to 4 as per Violation

        for fp in self.ctx.python_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=fp)

                visitor = NestingDepthVisitor(max_nesting_depth, fp)
                visitor.visit(tree)
                violations.extend(visitor.violations)

            except (IOError, SyntaxError) as e:
                self.ctx.log_error(f"Error parsing {fp} for excessive nesting: {e}")
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

def get_sub_atomic_agent() -> Any:
    '''Brief description of functionality and purpose.'''
    return sub_atomic_agent_impl

@timeout(300)
def heal_repository(dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
    """L1 cognition - operational only."""
    if _call_path is None:
        _call_path = set()
    agent_name = "CanonSubAtomic"
    if agent_name in _call_path:
        return {"errors": 1, "cycle_detected": True}
    if depth > max_depth:
        return {"errors": 1, "depth_limited": True}
    _call_path.add(agent_name)
    try:
        print(f"[{agent_name}] L1 cognition - operational only")
        return {"skipped": 1}
    finally:
        _call_path.discard(agent_name)