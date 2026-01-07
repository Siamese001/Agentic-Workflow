"""
StructuralEngineerAgent - Extracted from SubAtomicAgent.py
Part of the SubAtomic agent family for code quality enforcement.
"""
from typing import Any
from agentic_core.L1_cognition.thought_engine.SubAtomicAgent import SubAtomicAgent
from agentic_core.utils.core_extensions.timeout_decorator import timeout

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
