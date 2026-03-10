"""
Layer Sovereignty Enforcer — Wave 1 Phase 1

AST-based enforcement of the L0-L6 layer hierarchy.
Upward imports (lower layer number importing higher layer number) are violations.
Allowed cross-layer exceptions are explicitly enumerated below.

Usage:
    python -m agentic_core.L5_safety.enforcement.layer_sovereignty_enforcer
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
    APPS_SHARED_DIR,
)

# ---------------------------------------------------------------------------
# Layer hierarchy: higher number = higher authority.
# A module at layer N MUST NOT import from layer M where M > N.
# ---------------------------------------------------------------------------
LAYER_HIERARCHY: dict[str, int] = {
    "L0_routing": 0,
    "L1_cognition": 1,
    "L2_execution": 2,
    "L3_orchestration": 3,
    "L4_state": 4,
    "L5_safety": 5,
    "L6_observability": 6,
}

# Modules explicitly allowed to cross upward (string-prefix match on importer).
# Format: (importer_prefix, imported_prefix)
ALLOWED_UPWARD_EXCEPTIONS: frozenset[tuple[str, str]] = frozenset(
    {
        # L0 scripts may inspect L5 SSOT for path validation
        ("agentic_core.L0_routing.scripts", "agentic_core.L5_safety.config"),
        # L2 execution seams may reference L5 safety gates
        ("agentic_core.L2_execution.seams", "agentic_core.L5_safety"),
        # Shared interfaces live outside layer numbering
        ("agentic_core.L0_routing", "agentic_core.interfaces"),
        ("agentic_core.L1_cognition", "agentic_core.interfaces"),
        ("agentic_core.L2_execution", "agentic_core.interfaces"),
        ("agentic_core.L3_orchestration", "agentic_core.interfaces"),
        ("agentic_core.L4_state", "agentic_core.interfaces"),
    }
)

SCAN_ROOTS_DEFAULT: tuple[str, ...] = (
    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
    APPS_SHARED_DIR,
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SovereigntyViolation:
    """A single detected upward-import violation."""

    file_path: str
    importer_module: str
    importer_layer: int
    imported_module: str
    imported_layer: int

    def __str__(self) -> str:
        return (
            f"VIOLATION L{self.importer_layer}→L{self.imported_layer}: "
            f"{self.importer_module} imports {self.imported_module}"
        )


@dataclass
class EnforcementReport:
    """Aggregated result of a sovereignty scan."""

    violations: list[SovereigntyViolation] = field(default_factory=list)
    files_scanned: int = 0
    files_skipped: int = 0
    parse_errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    def summary(self) -> str:
        lines = [
            f"Files scanned : {self.files_scanned}",
            f"Files skipped : {self.files_skipped}",
            f"Parse errors  : {len(self.parse_errors)}",
            f"Violations    : {len(self.violations)}",
            f"Result        : {'PASS' if self.passed else 'FAIL'}",
        ]
        if self.violations:
            lines.append("")
            for v in self.violations:
                lines.append(f"  {v}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core enforcer
# ---------------------------------------------------------------------------


class LayerSovereigntyEnforcer:
    """
    AST-based layer sovereignty enforcer.

    Scans Python source files and detects any import from a layer with a
    higher authority number than the importing file's own layer.
    """

    def __init__(
        self,
        repo_root: Path,
        scan_roots: tuple[str, ...] | None = None,
        allowed_exceptions: frozenset[tuple[str, str]] | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.scan_roots = scan_roots or SCAN_ROOTS_DEFAULT
        self.allowed_exceptions = (
            allowed_exceptions
            if allowed_exceptions is not None
            else ALLOWED_UPWARD_EXCEPTIONS
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> EnforcementReport:
        """Run the full sovereignty scan and return an EnforcementReport."""
        report = EnforcementReport()
        for root_name in self.scan_roots:
            root_path = self.repo_root / root_name
            if not root_path.is_dir():
                continue
            for py_file in sorted(root_path.rglob("*.py")):
                if "__pycache__" in py_file.parts:
                    continue
                self._scan_file(py_file, report)
        return report

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _scan_file(self, file_path: Path, report: EnforcementReport) -> None:
        """Parse one file and append any violations to report."""
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as exc:
            report.parse_errors.append(f"{file_path}: SyntaxError: {exc}")
            report.files_skipped += 1
            return
        except OSError as exc:
            report.parse_errors.append(f"{file_path}: OSError: {exc}")
            report.files_skipped += 1
            return

        report.files_scanned += 1
        importer_module = self._path_to_module(file_path)
        importer_layer = self.extract_layer_from_module(importer_module)
        if importer_layer is None:
            return

        for imported_module in self._collect_imports(tree):
            imported_layer = self.extract_layer_from_module(imported_module)
            if imported_layer is None:
                continue
            if imported_layer <= importer_layer:
                continue  # Downward or same-layer import — allowed
            if self._is_allowed_exception(importer_module, imported_module):
                continue
            report.violations.append(
                SovereigntyViolation(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    importer_module=importer_module,
                    importer_layer=importer_layer,
                    imported_module=imported_module,
                    imported_layer=imported_layer,
                )
            )

    def _path_to_module(self, file_path: Path) -> str:
        """Convert a filesystem path to a dotted module name."""
        rel = file_path.relative_to(self.repo_root)
        parts = list(rel.with_suffix("").parts)
        return ".".join(parts)

    def _collect_imports(self, tree: ast.Module) -> list[str]:
        """Return all imported module names from an AST tree."""
        modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    modules.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    modules.append(node.module)
        return modules

    def _is_allowed_exception(self, importer: str, imported: str) -> bool:
        """Return True if this upward import pair is explicitly whitelisted."""
        for imp_prefix, target_prefix in self.allowed_exceptions:
            if importer.startswith(imp_prefix) and imported.startswith(target_prefix):
                return True
        return False

    # ------------------------------------------------------------------
    # Static helpers (usable without an instance)
    # ------------------------------------------------------------------

    @staticmethod
    def extract_layer_from_module(module_path: str) -> int | None:
        """
        Return the layer number for a dotted module path, or None if not
        part of the layer hierarchy.

        Examples
        --------
        >>> LayerSovereigntyEnforcer.extract_layer_from_module("agentic_core.L2_execution.foo")
        2
        >>> LayerSovereigntyEnforcer.extract_layer_from_module("agentic_core.base_agents.Foo") is None
        True
        """
        for layer_name, level in LAYER_HIERARCHY.items():
            if (
                f".{layer_name}." in module_path
                or module_path.startswith(f"{layer_name}.")
                or f".{layer_name}" == module_path[-len(layer_name) - 1 :]
            ):
                return level
        return None

    @staticmethod
    def check_upward_mutation(importer_layer: int, imported_layer: int) -> bool:
        """
        Return True if importing ``imported_layer`` from ``importer_layer``
        is an upward mutation (violation).

        A violation occurs when ``imported_layer > importer_layer``.
        """
        return imported_layer > importer_layer

    def analyze_file_imports(self, file_path: Path) -> list[SovereigntyViolation]:
        """
        Analyse a single file and return any violations found.
        Does NOT mutate any shared state.
        """
        violations: list[SovereigntyViolation] = []
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(file_path))
        except (SyntaxError, OSError):
            return violations

        importer_module = self._path_to_module(file_path)
        importer_layer = self.extract_layer_from_module(importer_module)
        if importer_layer is None:
            return violations

        for imported_module in self._collect_imports(tree):
            imported_layer = self.extract_layer_from_module(imported_module)
            if imported_layer is None:
                continue
            if not self.check_upward_mutation(importer_layer, imported_layer):
                continue
            if self._is_allowed_exception(importer_module, imported_module):
                continue
            violations.append(
                SovereigntyViolation(
                    file_path=str(file_path.relative_to(self.repo_root)),
                    importer_module=importer_module,
                    importer_layer=importer_layer,
                    imported_module=imported_module,
                    imported_layer=imported_layer,
                )
            )
        return violations

    def detect_circular_imports(self) -> list[tuple[str, str]]:
        """
        Detect mutually circular imports between any two modules in scan roots.
        Returns a list of (module_a, module_b) pairs that import each other.
        """
        import_map: dict[str, set[str]] = {}

        for root_name in self.scan_roots:
            root_path = self.repo_root / root_name
            if not root_path.is_dir():
                continue
            for py_file in sorted(root_path.rglob("*.py")):
                if "__pycache__" in py_file.parts:
                    continue
                try:
                    source = py_file.read_text(encoding="utf-8", errors="replace")
                    tree = ast.parse(source)
                except (SyntaxError, OSError):
                    continue
                mod = self._path_to_module(py_file)
                import_map[mod] = set(self._collect_imports(tree))

        cycles: list[tuple[str, str]] = []
        seen: set[frozenset[str]] = set()
        for mod_a, imports_a in import_map.items():
            for mod_b in imports_a:
                if mod_b in import_map and mod_a in import_map[mod_b]:
                    key = frozenset({mod_a, mod_b})
                    if key not in seen:
                        seen.add(key)
                        cycles.append((mod_a, mod_b))
        return cycles


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def main() -> int:
    repo_root = Path(__file__).resolve().parents[4]
    enforcer = LayerSovereigntyEnforcer(repo_root)
    report = enforcer.run()
    print(report.summary())
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
