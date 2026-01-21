"""
file: tests/maintenance/test_utility_relocation_safety.py
description: Safety tests for utility relocation to apps_shared.
             Verifies dependency isolation and circular dependency prevention.
"""

import ast
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def disable_path_shield():
    """Marker fixture to disable path shield in conftest."""
    pass


class TestDependencyIsolation:
    """
    Tests to verify that relocated utilities don't have forbidden dependencies.
    """

    def test_apps_shared_no_apps_lic_imports(self, disable_path_shield):
        """
        TC-001: Verify apps_shared utilities don't import from apps_lic.
        This prevents circular dependencies after relocation.
        """
        apps_shared_dir = PROJECT_ROOT / "apps_shared"
        if not apps_shared_dir.exists():
            pytest.skip("apps_shared directory not found")

        violations = []

        # Phase 6.8: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery import get_python_files

        for py_file in get_python_files(apps_shared_dir):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("apps_lic"):
                                violations.append((str(py_file), f"import {alias.name}"))
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("apps_lic"):
                            violations.append((str(py_file), f"from {node.module} import ..."))
            except SyntaxError:
                continue

        if violations:
            msg = "\n".join([f"  {v[0]}: {v[1]}" for v in violations])
            pytest.fail(f"apps_shared has forbidden imports from apps_lic:\n{msg}")

    def test_apps_shared_no_apps_rg_imports(self, disable_path_shield):
        """
        TC-002: Verify apps_shared utilities don't import from apps_rg.
        apps_shared should only depend on agentic_core and stdlib.
        """
        apps_shared_dir = PROJECT_ROOT / "apps_shared"
        if not apps_shared_dir.exists():
            pytest.skip("apps_shared directory not found")

        violations = []

        # Phase 6.8: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery import get_python_files

        for py_file in get_python_files(apps_shared_dir):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name.startswith("apps_rg"):
                                violations.append((str(py_file), f"import {alias.name}"))
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("apps_rg"):
                            violations.append((str(py_file), f"from {node.module} import ..."))
            except SyntaxError:
                continue

        if violations:
            msg = "\n".join([f"  {v[0]}: {v[1]}" for v in violations])
            pytest.fail(f"apps_shared has forbidden imports from apps_rg:\n{msg}")


class TestCircularDependencyPrevention:
    """
    Tests to detect and prevent circular dependencies in the codebase.
    """

    def _extract_imports(self, file_path: Path) -> set[str]:
        """Extract all import module roots from a Python file."""
        imports = set()
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root = alias.name.split(".")[0]
                        imports.add(root)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        root = node.module.split(".")[0]
                        imports.add(root)
        except SyntaxError:
            pass
        return imports

    def _get_territory_dependencies(self, territory: str) -> dict[str, set[str]]:
        """Get all external dependencies for files in a territory."""
        territory_dir = PROJECT_ROOT / territory
        if not territory_dir.exists():
            return {}

        deps = {}
        known_territories = {
            "agentic_core",
            "apps_shared",
            "apps_rg",
            "apps_lic",
            "tests",
            "scripts",
        }

        # Phase 6.8: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery import get_python_files

        for py_file in get_python_files(territory_dir):
            imports = self._extract_imports(py_file)
            external = imports & known_territories
            if external:
                deps[str(py_file.relative_to(PROJECT_ROOT))] = external

        return deps

    def test_no_circular_apps_shared_to_apps_lic(self):
        """
        TC-003: Verify no circular dependency: apps_shared -> apps_lic -> apps_shared.
        """
        apps_shared_deps = self._get_territory_dependencies("apps_shared")

        # Check if any apps_shared file imports apps_lic
        circular_risk = []
        for file_path, deps in apps_shared_deps.items():
            if "apps_lic" in deps:
                circular_risk.append(file_path)

        if circular_risk:
            pytest.fail(
                "Circular dependency risk: apps_shared files importing apps_lic:\n"
                + "\n".join(f"  - {f}" for f in circular_risk)
            )

    def test_gravity_compliance(self):
        """
        TC-004: Verify gravity compliance - downstream can import upstream, not vice versa.

        Allowed: apps_lic -> apps_shared -> agentic_core
        Forbidden: agentic_core -> apps_* (except via dynamic import)
        """
        agentic_core_deps = self._get_territory_dependencies("agentic_core")

        # Check if agentic_core imports from apps_*
        gravity_violations = []
        for file_path, deps in agentic_core_deps.items():
            forbidden = deps & {"apps_shared", "apps_rg", "apps_lic"}
            if forbidden:
                gravity_violations.append((file_path, forbidden))

        if gravity_violations:
            msg = "\n".join([f"  {v[0]}: imports {v[1]}" for v in gravity_violations])
            pytest.fail(f"Gravity violations (agentic_core importing downstream):\n{msg}")


class TestRelocationCandidate:
    """
    Tests to validate if a file is a valid candidate for relocation to apps_shared.
    """

    def test_duplicate_code_detector_isolation(self, disable_path_shield):
        """
        TC-005: Verify DuplicateCodeDetectorAgent can run with only agentic_core dependencies.
        """
        detector_path = PROJECT_ROOT / "apps_shared" / "utils" / "DuplicateCodeDetectorAgent.py"

        if not detector_path.exists():
            pytest.skip("DuplicateCodeDetectorAgent not found in apps_shared/utils/")

        # Check its imports
        imports = set()
        try:
            content = detector_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split(".")[0])
        except SyntaxError as e:
            pytest.fail(f"Syntax error in DuplicateCodeDetectorAgent: {e}")

        # Allowed dependencies
        allowed = {
            "agentic_core",
            "apps_shared",
            "typing",
            "pathlib",
            "os",
            "sys",
            "ast",
            "re",
            "json",
            "logging",
            "dataclasses",
            "collections",
            "functools",
            "itertools",
            "hashlib",
            "difflib",
            "abc",
            "enum",
        }

        forbidden = imports - allowed
        # Filter out stdlib modules
        stdlib_prefixes = {
            "typing",
            "pathlib",
            "os",
            "sys",
            "ast",
            "re",
            "json",
            "logging",
            "dataclasses",
            "collections",
            "functools",
            "itertools",
            "hashlib",
            "difflib",
            "abc",
            "enum",
            "datetime",
            "time",
            "copy",
            "io",
            "warnings",
            "traceback",
            "inspect",
            "importlib",
            "contextlib",
            "threading",
            "subprocess",
            "shutil",
        }

        forbidden = forbidden - stdlib_prefixes

        if "apps_lic" in forbidden or "apps_rg" in forbidden:
            pytest.fail(f"DuplicateCodeDetectorAgent has forbidden dependencies: {forbidden}")


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))
