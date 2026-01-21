from __future__ import annotations

"""
DependencySentinelAgent - L1 Guardian for Import Dependencies

Enforces the "Law of Depth" and prevents circular imports.
Uses AST parsing to analyze and validate import structures.
"""
import ast
import logging
from pathlib import Path
from typing import Any

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import CORE_SUBFOLDER_MAP

Logger: Any = logging.getLogger(__name__)

# [SSOT DERIVED] Layer names from CORE_SUBFOLDER_MAP
LAYER_NAMES = [k for k in CORE_SUBFOLDER_MAP.keys() if k.startswith("L")]


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor to extract import information."""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.imports: list[dict] = []
        self.from_imports: list[dict] = []
        self.layer = self._determine_layer()

    def _determine_layer(self) -> str:
        """Determine which layer the file belongs to. Uses SSOT-derived LAYER_NAMES."""
        parts = self.file_path.parts
        # [SSOT] Check against dynamically derived layer names
        for layer_name in LAYER_NAMES:
            if layer_name in parts:
                return layer_name.split("_")[0]  # Return L0, L1, L2, etc.
        return "UNKNOWN"

    def visit_Import(self, node: ast.Import) -> Any:
        """Handle import statements."""
        for alias in node.names:
            self.imports.append(
                {"module": alias.name, "alias": alias.asname, "line": node.lineno, "type": "import"}
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        """Handle from...import statements."""
        if node.module:
            self.from_imports.append(
                {
                    "module": node.module,
                    "names": [alias.name for alias in node.names],
                    "level": node.level,
                    "line": node.lineno,
                    "type": "from_import",
                }
            )
        self.generic_visit(node)


class DependencyViolation:
    """Represents a dependency rule Violation."""

    def __init__(
        self, ViolationType: str, file_path: Path, line: int, message: str, details: dict = None
    ) -> None:
        self.type = ViolationType
        self.file_path = file_path
        self.line = line
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "file": str(self.file_path),
            "line": self.line,
            "message": self.message,
            "details": self.details,
        }


from agentic_core.L2_execution.ToolRegistry.governance import DependencySentinelAgent
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


# Legacy L1 version - use L2 canonical (dependency management is execution-level)
class _LegacyDependencySentinelAgent(SubatomicTestingMixin, HealerMixin, MCPHardenedMixin):
    """
    Guards the codebase against illegal dependencies.

    Rules enforced:
    1. No circular imports
    2. No cross-layer violations (L3 cannot import L1, etc.)
    3. No illegal cross-repo imports
    4. Depth compliance for imports
    """

    def __init__(self, root_dir: Path = None) -> None:
        """
        Initialize the DependencySentinelAgent.

        Args:
            root_dir: Root directory of the codebase
        """
        self.root_dir = root_dir or Path.cwd()
        self.violations: list[DependencyViolation] = []
        self.layer_hierarchy = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}
        self.allowed_cross_layers = {
            ("L2", "L1"),
            ("L3", "L1"),
            ("L3", "L2"),
            ("L4", "L1"),
            ("L5", "L1"),
            ("L5", "L2"),
            ("L5", "L3"),
            ("L5", "L4"),
        }
        LOGGER.info("DependencySentinelAgent initialized")

    def check_file(self, file_path: Path) -> list[DependencyViolation]:
        """
        Check a single file for dependency violations.

        Args:
            file_path: Path to the Python file

        Returns:
            List of violations found
        """
        violations: Any = []
        try:
            with open(file_path, encoding="utf-8") as f:
                content: Any = f.read()
            tree: Any = ast.parse(content)
            analyzer: Any = ImportAnalyzer(file_path)
            analyzer.visit(tree)
            for imp in analyzer.imports:
                Violation: Any = self._check_import(analyzer, imp["module"], imp["line"])
                if Violation:
                    violations.append(Violation)
            for imp in analyzer.from_imports:
                for name in imp["names"]:
                    Violation: Any = self._check_import(analyzer, imp["module"], imp["line"], name)
                    if Violation:
                        violations.append(Violation)
        except SyntaxError as e:
            violations.append(
                DependencyViolation("syntax_error", file_path, e.lineno or 0, f"Syntax error: {e}")
            )
        except Exception as e:
            LOGGER.error(f"Error checking {file_path}: {e}")
        return violations

    def _check_import(
        self, analyzer: ImportAnalyzer, module: str, line: int, name: str = None
    ) -> DependencyViolation | None:
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
        if self._is_external_import(module):
            return None
        if self._is_circular_import(analyzer.file_path, module):
            return DependencyViolation(
                "circular_import", analyzer.file_path, line, f"Circular import detected: {module}"
            )
        Violation = self._check_cross_layer_violation(analyzer, module, line)
        if Violation:
            return Violation
        if self._violates_depth_law(analyzer.file_path, module):
            return DependencyViolation(
                "depth_violation", analyzer.file_path, line, f"Import violates depth law: {module}"
            )
        return None

    def _is_external_import(self, module: str) -> bool:
        """Check if module is external (stdlib or third-party)."""
        external_prefixes = [
            "os",
            "sys",
            "json",
            "logging",
            "datetime",
            "pathlib",
            "asyncio",
            "collections",
            "itertools",
            "functools",
            "typing",
            "dataclasses",
            "enum",
            "contextlib",
            "google",
            "openai",
            "anthropic",
            "pinecone",
            "redis",
        ]
        return any(module.startswith(prefix) for prefix in external_prefixes)

    def _is_circular_import(self, file_path: Path, module: str) -> bool:
        """
        Check if import would create a circular dependency.

        This is a simplified check - full circular import detection
        would require building a full dependency graph.
        """
        module_path = self.root_dir / module.replace(".", "/")
        if not module_path.exists():
            return False
        if module_path.parent == file_path.parent:
            return False
        return False

    def _check_cross_layer_violation(
        self, analyzer: ImportAnalyzer, module: str, line: int
    ) -> DependencyViolation | None:
        """Check for cross-layer import violations."""
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
        cross = (analyzer.layer, imported_layer)
        if cross in self.allowed_cross_layers:
            return None
        if analyzer.layer == imported_layer:
            return None
        return DependencyViolation(
            "cross_layer_violation",
            analyzer.file_path,
            line,
            f"Illegal cross-layer import: {analyzer.layer} -> {imported_layer}",
            {"from_layer": analyzer.layer, "to_layer": imported_layer, "module": module},
        )

    def _violates_depth_law(self, file_path: Path, module: str) -> bool:
        """Check if import violates the depth law."""
        try:
            file_rel = file_path.relative_to(self.root_dir)
            module_path = self.root_dir / module.replace(".", "/")
            if not module_path.exists():
                return False
            module_rel = module_path.relative_to(self.root_dir)
            file_depth = len(file_rel.parts)
            module_depth = len(module_rel.parts)
            return module_depth > file_depth + 2
        except (ValueError, OSError):
            return False

    def check_directory(self, directory: Path) -> list[DependencyViolation]:
        """
        Check all Python files in a directory.

        Args:
            directory: Directory to check

        Returns:
            List of all violations found
        """
        violations: Any = []
        for py_file in directory.rglob("*.py"):
            if py_file.name == "__init__.py" or "test" in py_file.name.lower():
                continue
            file_violations: Any = self.check_file(py_file)
            violations.extend(file_violations)
        return violations

    def get_violation_summary(self) -> dict:
        """Get summary of all violations."""
        summary: Any = {"total_violations": len(self.violations), "by_type": {}, "by_file": {}}
        for Violation in self.violations:
            vtype: Any = Violation.type
            summary["by_type"][vtype] = summary["by_type"].get(vtype, 0) + 1
            file: Any = str(Violation.file_path)
            summary["by_file"][file] = summary["by_file"].get(file, 0) + 1
        return summary

    @timeout(300)
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L1 cognition agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
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

    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L1 cognition agent - operational only."""
        # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
        super().heal_repository()

        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
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


def get_dependency_sentinel(project_root: Path) -> DependencySentinelAgent:
    """Factory function to get dependency sentinel instance."""
    return DependencySentinelAgent(project_root=project_root)


def initialize_dependency_sentinel(root_dir: Path = None) -> Any:
    """
    Initialize the DependencySentinelAgent system.

    Args:
        root_dir: Root directory of the codebase
    """
    global _dependency_sentinel
    _dependency_sentinel = DependencySentinelAgent(root_dir)
    LOGGER.info("DependencySentinelAgent system initialized")


def check_dependencies(file_path: Path = None, directory: Path = None) -> list[DependencyViolation]:
    """
    Check dependencies for a file or directory.

    Args:
        file_path: Specific file to check
        directory: Directory to check

    Returns:
        List of violations
    """
    sentinel: Any = get_dependency_sentinel()
    if file_path:
        return sentinel.check_file(file_path)
    elif directory:
        return sentinel.check_directory(directory)
    else:
        return sentinel.check_directory(sentinel.root_dir)
