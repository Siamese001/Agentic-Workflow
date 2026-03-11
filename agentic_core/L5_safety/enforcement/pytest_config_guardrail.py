from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.L2_execution.tools import write_gateway as _wg

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Pytest Configuration Enforcement Guard
====================================

Validates pytest configuration against hardening rules learned from RCA.
Ensures conftest hooks are transparent and marker behavior is documented.
"""

import ast
import sys
from pathlib import Path


class PytestEnforcementGuard:
    """Enforces pytest configuration hardening rules."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_pytest_configuration(self) -> tuple[list[str], list[str]]:
        """Validate entire pytest configuration setup."""
        self.errors.clear()
        self.warnings.clear()

        # Check pytest.ini
        pytest_ini = self.repo_root / "pytest.ini"
        if pytest_ini.exists():
            self._validate_pytest_ini(pytest_ini)
        else:
            self.errors.append("pytest.ini not found")

        # Check conftest.py files
        for conftest in self.repo_root.rglob("conftest.py"):
            # Skip .venv and other non-repo directories
            if ".venv" in str(conftest) or "__pycache__" in str(conftest):
                continue
            self._validate_conftest(conftest)

        # Check test marker consistency
        self._validate_marker_consistency()

        return self.errors, self.warnings

    def _validate_pytest_ini(self, pytest_ini: Path) -> None:
        """Validate pytest.ini configuration."""
        content = pytest_ini.read_text()

        # Check for testpaths
        if "testpaths" not in content:
            self.errors.append("pytest.ini missing testpaths configuration")

        # Check for markers section
        if "[tool:pytest]" not in content and "[pytest]" not in content:
            self.errors.append("pytest.ini missing [pytest] section")

        # Check for strict-markers
        if "--strict-markers" not in content:
            self.warnings.append("pytest.ini missing --strict-markers (recommended)")

        # Parse markers
        markers = self._extract_markers_from_ini(content)
        self._validate_markers(markers)

    def _extract_markers_from_ini(self, content: str) -> set[str]:
        """Extract marker names from pytest.ini."""
        markers = set()
        in_markers = False

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("markers"):
                in_markers = True
                continue
            elif in_markers:
                if not line or line.startswith("["):
                    break
                # Extract marker name before ':'
                if ":" in line:
                    marker_name = line.split(":")[0].strip()
                    markers.add(marker_name)

        return markers

    def _validate_markers(self, markers: set[str]) -> None:
        """Validate marker configuration."""
        required_markers = {"governance", "integration_full_deps", "constitutional", "guardian", "asyncio"}

        missing = required_markers - markers
        if missing:
            self.errors.append(f"Missing required markers in pytest.ini: {missing}")

    def _validate_conftest(self, conftest: Path) -> None:
        """Validate conftest.py for hook transparency."""
        try:
            tree = ast.parse(conftest.read_text(encoding="utf-8"))
        except SyntaxError as e:
            self.errors.append(f"Syntax error in {conftest}: {e}")
            return
        except UnicodeDecodeError:
            self.errors.append(f"Unicode error in {conftest}: file must be UTF-8 encoded")
            return

        # Check for pytest_collection_modifyitems
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "pytest_collection_modifyitems":
                self._validate_collection_modifyitems(conftest, node)

    def _validate_collection_modifyitems(self, conftest: Path, node: ast.FunctionDef) -> None:
        """Validate pytest_collection_modifyitems hook."""
        # Check if hook logs deselection
        try:
            source = ast.get_source_segment(conftest.read_text(encoding="utf-8"), node)
        except UnicodeDecodeError:
            self.warnings.append(f"{conftest}: Cannot read file for hook validation (encoding issue)")
            return

        if source and "deselected" not in source:
            self.warnings.append(f"{conftest}: pytest_collection_modifyitems doesn't log deselection count")

        # Check for documentation comment
        if not ast.get_docstring(node):
            self.warnings.append(f"{conftest}: pytest_collection_modifyitems missing docstring")

        # Check for brittle getoption("-m") marker access (AST-based detection)
        self._check_brittle_marker_access(conftest, node)

        # Check for hardcoded marker logic
        if source and "integration_full_deps" in source:
            # This is expected but should be documented
            if "default_markers" not in source:
                self.warnings.append(f"{conftest}: Consider using default_markers tuple for clarity")

    def _check_brittle_marker_access(self, conftest: Path, node: ast.FunctionDef) -> None:
        """Check for brittle config.getoption("-m") marker access patterns.

        Flags any use of getoption("-m") or getoption('-m') with or without default arg.
        Robust alternative: getattr(config.option, "markexpr", "")
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                # Check if this is a getoption call
                if self._is_getoption_call(child):
                    # Check if first argument is "-m" or '-m'
                    if child.args and isinstance(child.args[0], ast.Constant):
                        if child.args[0].value == "-m":
                            self.errors.append(
                                f"{conftest}: Brittle marker access detected: "
                                f'config.getoption("-m") should be replaced with '
                                f'getattr(config.option, "markexpr", "")'
                            )

    def _is_getoption_call(self, node: ast.Call) -> bool:
        """Check if a Call node is a getoption method call."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr == "getoption"
        return False

    def _validate_marker_consistency(self) -> None:
        """Validate marker usage across test files."""
        pytest_markers = self._get_pytest_ini_markers()
        test_markers = self._get_used_test_markers()

        # Check for unregistered markers
        unregistered = test_markers - pytest_markers
        if unregistered:
            self.errors.append(f"Tests use unregistered markers: {unregistered}")

        # Check for unused markers
        unused = pytest_markers - test_markers
        if unused:
            self.warnings.append(f"Registered but unused markers: {unused}")

    def _get_pytest_ini_markers(self) -> set[str]:
        """Get markers from pytest.ini."""
        pytest_ini = self.repo_root / "pytest.ini"
        if not pytest_ini.exists():
            return set()
        return self._extract_markers_from_ini(pytest_ini.read_text())

    def _get_used_test_markers(self) -> set[str]:
        """Get markers actually used in test files."""
        markers = set()

        # Built-in pytest markers that don't need registration
        builtin_markers = {
            "skipif",
            "filterwarnings",
            "usefixtures",
            "skip",
            "parametrize",
            "xfail",
            "fixture",
            "yield_fixture",
            "tryfirst",
            "trylast",
        }

        for test_file in self.repo_root.rglob("test_*.py"):
            # Skip .venv and other non-repo directories
            if ".venv" in str(test_file) or "__pycache__" in str(test_file):
                continue

            try:
                content = test_file.read_text(encoding="utf-8")
                # Look for @pytest.mark.xxx patterns
                import re

                found = re.findall(r"@pytest\.mark\.(\w+)", content)
                for marker in found:
                    if marker not in builtin_markers:
                        markers.add(marker)
            except (UnicodeDecodeError, PermissionError, OSError) as e:
                # Log specific errors but continue processing other files
                self.warnings.append(f"Error processing {test_file}: {e}")
                continue

        return markers


def main():
    """Run pytest enforcement validation."""
    repo_root = Path(__file__).parent.parent.parent
    guard = PytestEnforcementGuard(repo_root)

    errors, warnings = guard.validate_pytest_configuration()

    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print(f"\n{len(errors)} enforcement errors found")
        sys.exit(1)
    elif warnings:
        print(f"\n{len(warnings)} warnings found")
    else:
        print("\nPytest configuration passes all enforcement checks")


class TestPytestConfigGuardBrittleMarkerDetection:
    """Unit tests for brittle marker access detection."""

    def test_detects_brittle_getoption_m(self):
        """Test that getoption("-m") is flagged as brittle."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create pytest.ini
            pytest_ini = tmpdir / "pytest.ini"
            _wg.write_text(
                pytest_ini,
                "[pytest]\ntestpaths = tests\nmarkers =\n    governance: Governance tests\n    integration_full_deps: Integration tests\n",
            )

            # Create conftest with brittle pattern
            conftest = tmpdir / TESTS_DIR / "conftest.py"
            _wg.ensure_dir(conftest.parent)
            _wg.write_text(
                conftest,
                "import pytest\n\ndef pytest_collection_modifyitems(config, items):\n    '''Hook with brittle marker access.'''\n    marker_expr = config.getoption(\"-m\", default=\"\")\n",
            )

            guard = PytestEnforcementGuard(tmpdir)
            errors, warnings = guard.validate_pytest_configuration()

            assert any("Brittle marker access" in e for e in errors), (
                f"Expected brittle marker error, got: {errors}"
            )

    def test_allows_robust_getattr_pattern(self):
        """Test that getattr(config.option, 'markexpr', '') is NOT flagged."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create pytest.ini
            pytest_ini = tmpdir / "pytest.ini"
            _wg.write_text(
                pytest_ini,
                "[pytest]\ntestpaths = tests\nmarkers =\n    governance: Governance tests\n    integration_full_deps: Integration tests\n",
            )

            # Create conftest with robust pattern
            conftest = tmpdir / TESTS_DIR / "conftest.py"
            _wg.ensure_dir(conftest.parent)
            _wg.write_text(
                conftest,
                "import pytest\n\ndef pytest_collection_modifyitems(config, items):\n    '''Hook with robust marker access.'''\n    marker_expr = getattr(config.option, \"markexpr\", \"\")\n",
            )

            guard = PytestEnforcementGuard(tmpdir)
            errors, warnings = guard.validate_pytest_configuration()

            # Should NOT have brittle marker error
            brittle_errors = [e for e in errors if "Brittle marker access" in e]
            assert len(brittle_errors) == 0, f"Robust pattern should not be flagged, got: {brittle_errors}"


if __name__ == "__main__":
    main()
