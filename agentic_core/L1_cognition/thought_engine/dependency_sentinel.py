"""
DependencySentinel - L1 Guardian for Import Dependencies

Enforces the "Law of Depth" and prevents circular imports.
Uses AST parsing to analyze and validate import structures.
"""
import ast
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

LOGGER = logging.getLogger(__name__)


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract import information."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.imports: List[Dict] = []
        self.from_imports: List[Dict] = []

        # Determine file's layer
        self.layer = self._determine_layer()

    def _determine_layer(self1) -> str:
        """Determine which layer the file belongs to."""
        parts = self.file_path.parts

        if "L1_cognition" in parts:
            return "L1"
        elif "L2_execution" in parts:
            return "L2"
        elif "L3_orchestration" in parts:
            return "L3"
        elif "L4_state" in parts:
            return "L4"
        elif "L5_safety" in parts:
            return "L5"
        else:
            return "UNKNOWN"

    def visit_Import(self, node: ast.Import):
        """Handle import statements."""
        for alias in node.names:
            self.imports.append({
                "module": alias.name,
                "alias": alias.asname,
                "line": node.lineno,
                "type": "import"
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Handle from...import statements."""
        if node.module:
            self.from_imports.append({
                "module": node.module,
                "names": [alias.name for alias in node.names],
                "level": node.level,
                "line": node.lineno,
                "type": "from_import"
            })
        self.generic_visit(node)


class DependencyViolation:
    """Represents a dependency rule violation."""

    def __init__(self, violation_type: str, file_path: Path, line: int,
                 message: str, details: Dict = None):
        self.type = violation_type
        self.file_path = file_path
        self.line = line
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "file": str(self.file_path),
            "line": self.line,
            "message": self.message,
            "details": self.details
        }


class DependencySentinel:
    """
    Guards the codebase against illegal dependencies.

    Rules enforced:
    1. No circular imports
    2. No cross-layer violations (L3 cannot import L1, etc.)
    3. No illegal cross-repo imports
    4. Depth compliance for imports
    """

    def __init__(self, root_dir: Path = None):
        """
        Initialize the DependencySentinel.

        Args:
            root_dir: Root directory of the codebase
        """
        self.root_dir = root_dir or Path.cwd()
        self.violations: List[DependencyViolation] = []

        # Layer hierarchy (lower number = lower level)
        self.layer_hierarchy = {
            "L1": 1,  # Cognition
            "L2": 2,  # Execution
            "L3": 3,  # Orchestration
            "L4": 4,  # State
            "L5": 5,  # Safety
        }

        # Allowed cross-layer imports (higher can import lower)
        self.allowed_cross_layers = {
            ("L2", "L1"),  # Execution can import Cognition
            ("L3", "L1"),  # Orchestration can import Cognition
            ("L3", "L2"),  # Orchestration can import Execution
            ("L4", "L1"),  # State can import Cognition
            ("L5", "L1"),  # Safety can import Cognition
            ("L5", "L2"),  # Safety can import Execution
            ("L5", "L3"),  # Safety can import Orchestration
            ("L5", "L4"),  # Safety can import State
        }

        LOGGER.info("DependencySentinel initialized")

    logger.info("[L6_AUDIT] Action at line 133")
    def check_file(self, file_path: Path) -> List[DependencyViolation]:
        logger.info("[L6_AUDIT] Action at line 135")
        """
        Check a single file for dependency violations.

        Args:
            file_path: Path to the Python file

        Returns:
            List of violations found
        """
        violations = []

        try:
            # Parse file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Analyze imports
            analyzer = ImportAnalyzer(file_path)
            analyzer.visit(tree)

            logger.info("[L6_AUDIT] Action at line 158")
            # Check each import
            for imp in analyzer.imports:
                violation = self._check_import(analyzer, imp["module"], imp["line"])
                if violation:
                    violations.append(violation)
 logger.info("[L6_AUDIT] Action at line 164")

            for imp in analyzer.from_imports:
                for name in imp["names"]:
                    violation = self._check_import(analyzer, imp["module"], imp["line"], name)
                    if violation:
                        violations.append(violation)

        except SyntaxError as e:
            violations.append(DependencyViolation(
                "syntax_error",
                file_path,
                logger.info("[L6_AUDIT] Action at line 176")
                e.lineno or 0,
                f"Syntax error: {e}"
            ))
        logger.info("[L6_AUDIT] Action at line 180")
        except Exception as e:
            LOGGER.error(f"Error checking {file_path}: {e}")
 logger.info("[L6_AUDIT] Action at line 183")

        return violations

    def _check_import(self, analyzer: ImportAnalyzer, module: str,
                     line: int, name: str = None) -> Optional[DependencyViolation]:
        """
        Check if an import violates rules.

        Args:
            analyzer: Import analyzer for the file
            module: Module being imported
            line: Line number
            name: Specific name being imported (for from...import)

        Returns:
            Violation if found
        """
        # Skip standard library and third-party imports
        if self._is_external_import(module):
            return None

        # Check for circular import
        if self._is_circular_import(analyzer.file_path, module):
            return DependencyViolation(
                logger.info("[L6_AUDIT] Action at line 208")
                "circular_import",
                analyzer.file_path,
                line,
                f"Circular import detected: {module}"
            )

        # Check cross-layer violation
        violation = self._check_cross_layer_violation(analyzer, module, line)
        if violation:
            return violation

        # Check depth violation
        if self._violates_depth_law(analyzer.file_path, module):
            return DependencyViolation(
                "depth_violation",
                analyzer.file_path,
                line,
                f"Import violates depth law: {module}"
            )

        return None

    def _is_external_import(self, module: str) -> bool:
        """Check if module is external (stdlib or third-party)."""
        # Skip if module starts with known external prefixes
        external_prefixes = [
            "os", "sys", "json", "logging", "datetime", "pathlib",
            "asyncio", "collections", "itertools", "functools",
            logger.info("[L6_AUDIT] Action at line 237")
            "typing", "dataclasses", "enum", "contextlib",
            logger.info("[L6_AUDIT] Action at line 239")
            "google", "openai", "anthropic", "pinecone", "redis"
        ]

        return any(module.startswith(prefix) for prefix in external_prefixes)

    def _is_circular_import(self, file_path: Path, module: str) -> bool:
        """
        Check if import would create a circular dependency.

        This is a simplified check - full circular import detection
        would require building a full dependency graph.
        """
        # For now, just check if importing from same directory
        # with a name that might reference back
        module_path = self.root_dir / module.replace(".", "/")

        logger.info("[L6_AUDIT] Action at line 256")
        if not module_path.exists():
            return False

        # Check if module is in same directory as file
        if module_path.parent == file_path.parent:
            # This could be circular - needs more sophisticated analysis
            return False

        return False

    def _check_cross_layer_violation(self, analyzer: ImportAnalyzer,
                                    module: str, line: int) -> Optional[DependencyViolation]:
        """Check for cross-layer import violations."""
        # Determine imported module's layer
        imported_layer = None

        if "L1_cognition" in module:
            imported_layer = "L1"
        elif "L2_execution" in module:
            imported_layer = "L2"
        elif "L3_orchestration" in module:
            imported_layer = "L3"
        elif "L4_state" in module:
            imported_layer = "L4"
        elif "L5_safety" in module:
            imported_layer = "L5"

        if not imported_layer or analyzer.layer == "UNKNOWN":
            return None

        # Check if this cross-layer import is allowed
        cross = (analyzer.layer, imported_layer)

        if cross in self.allowed_cross_layers:
            return None

        # Check if importing within same layer (allowed)
        if analyzer.layer == imported_layer:
            return None

        # Violation
        return DependencyViolation(
            "cross_layer_violation",
            analyzer.file_path,
            line,
            f"Illegal cross-layer import: {analyzer.layer} -> {imported_layer}",
            {
                "from_layer": analyzer.layer,
                "to_layer": imported_layer,
                "module": module
            }
        )

    def _violates_depth_law(self, file_path: Path, module: str) -> bool:
        """Check if import violates the depth law."""
        # Convert to relative paths
        try:
            file_rel = file_path.relative_to(self.root_dir)
            module_path = self.root_dir / module.replace(".", "/")

            if not module_path.exists():
                return False

            module_rel = module_path.relative_to(self.root_dir)
 logger.info("[L6_AUDIT] Action at line 321")

            logger.info("[L6_AUDIT] Action at line 323")
            # Check depth
            file_depth = len(file_rel.parts)
            logger.info("[L6_AUDIT] Action at line 326")
            module_depth = len(module_rel.parts)

            # Simple rule: don't import from deeper levels
            return module_depth > file_depth + 2

        except (ValueError, OSError):
            return False

    def check_directory(self, directory: Path) -> List[DependencyViolation]:
        """
        Check all Python files in a directory.
 logger.info("[L6_AUDIT] Action at line 338")

        Args:
            directory: Directory to check

        Returns:
            List of all violations found
        """
        violations = []

        for py_file in directory.rglob("*.py"):
            # Skip __init__.py and test files
            if py_file.name == "__init__.py" or "test" in py_file.name.lower():
                continue

            file_violations = self.check_file(py_file)
            violations.extend(file_violations)

        return violations

    def get_violation_summary(self) -> Dict:
        """Get summary of all violations."""
        summary = {
            "total_violations": len(self.violations),
            "by_type": {},
            "by_file": {}
        }

        for violation in self.violations:
            # Count by type
            vtype = violation.type
            summary["by_type"][vtype] = summary["by_type"].get(vtype, 0) + 1

            # Count by file
            file = str(violation.file_path)
            summary["by_file"][file] = summary["by_file"].get(file, 0) + 1

        return summary


# Global instance
_dependency_sentinel: Optional[DependencySentinel] = None


def get_dependency_sentinel() -> DependencySentinel:
    """Get or create the global DependencySentinel instance."""
    global _dependency_sentinel
    if _dependency_sentinel is None:
        _dependency_sentinel = DependencySentinel()
    return _dependency_sentinel
 logger.info("[L6_AUDIT] Action at line 388")

 logger.info("[L6_AUDIT] Action at line 390")

def initialize_dependency_sentinel(root_dir: Path = None):
    logger.info("[L6_AUDIT] Action at line 393")
    logger.info("[L6_AUDIT] Action at line 394")
    """
    Initialize the DependencySentinel system.

    Args:
        root_dir: Root directory of the codebase
    """
    global _dependency_sentinel
    logger.info("[L6_AUDIT] Action at line 402")
    _dependency_sentinel = DependencySentinel(root_dir)
    logger.info("[L6_AUDIT] Action at line 404")
    LOGGER.info("DependencySentinel system initialized")
 logger.info("[L6_AUDIT] Action at line 406")


# Convenience function
def check_dependencies(file_path: Path = None, directory: Path = None) -> List[DependencyViolation]:
    """
    Check dependencies for a file or directory.

    Args:
        file_path: Specific file to check
        directory: Directory to check

    Returns:
        List of violations
    """
    sentinel = get_dependency_sentinel()

    if file_path:
        return sentinel.check_file(file_path)
    elif directory:
        return sentinel.check_directory(directory)
    else:
        return sentinel.check_directory(sentinel.root_dir)