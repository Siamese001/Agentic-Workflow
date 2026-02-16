"""
Test Pytest Configuration Enforcement Guard
==========================================

Tests the pytest configuration enforcement rules.
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from tools.enforcement.pytest_config_guard import PytestEnforcementGuard

pytestmark = pytest.mark.unit_min_deps


class TestPytestEnforcementGuard:
    """Test pytest configuration enforcement."""

    def test_missing_pytest_ini(self):
        """Test error when pytest.ini is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            guard = PytestEnforcementGuard(Path(tmpdir))
            errors, warnings = guard.validate_pytest_configuration()

            assert any("pytest.ini not found" in e for e in errors)
            assert len(errors) > 0

    def test_valid_pytest_configuration(self):
        """Test valid pytest configuration passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create valid pytest.ini
            pytest_ini = tmpdir / "pytest.ini"
            pytest_ini.write_text("""
[pytest]
testpaths = tests/unit tests/integration
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    -v
    --tb=short
    --strict-markers
    --color=yes

markers =
    governance: Governance audit tests
    integration_full_deps: Integration tests with full dependencies
    constitutional: Constitutional rule tests
    guardian: Guardian layer tests
    asyncio: Async tests
""")

            # Create valid conftest.py
            conftest = tmpdir / "tests" / "conftest.py"
            conftest.parent.mkdir(parents=True)
            conftest.write_text("""
'''Test configuration with documented hook.'''

import pytest

def pytest_collection_modifyitems(config, items):
    '''Default to integration_full_deps + governance when no marker specified.

    This hook ensures both integration and governance tests run by default.
    Logs deselection count for transparency.
    '''
    marker_expr = config.getoption("-m", default="")

    if not marker_expr:
        default_markers = ("integration_full_deps", "governance")
        deselected = []
        selected = []
        for item in items:
            if any(item.get_closest_marker(m) for m in default_markers):
                selected.append(item)
            else:
                deselected.append(item)

        items[:] = selected
        config._deselected_count = len(deselected)
""")

            # Create test file with proper markers
            test_file = tmpdir / "tests" / "test_example.py"
            test_file.write_text("""
import pytest

@pytest.mark.governance
class TestGovernance:
    def test_governance_check(self):
        assert True

@pytest.mark.integration_full_deps
class TestIntegration:
    def test_integration_check(self):
        assert True
""")

            guard = PytestEnforcementGuard(tmpdir)
            errors, warnings = guard.validate_pytest_configuration()

            assert len(errors) == 0, f"Expected no errors, got: {errors}"
            # May have warnings, that's OK

    def test_missing_required_markers(self):
        """Test error when required markers are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            pytest_ini = tmpdir / "pytest.ini"
            pytest_ini.write_text("""
[pytest]
testpaths = tests
markers =
    asyncio: Async tests
""")

            guard = PytestEnforcementGuard(tmpdir)
            errors, warnings = guard.validate_pytest_configuration()

            assert any("Missing required markers" in e for e in errors)
            assert "governance" in str(errors)

    def test_unregistered_markers_in_tests(self):
        """Test error when tests use unregistered markers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create pytest.ini with limited markers
            pytest_ini = tmpdir / "pytest.ini"
            pytest_ini.write_text("""
[pytest]
testpaths = tests
markers =
    governance: Governance tests
""")

            # Create test with unregistered marker
            test_file = tmpdir / "tests" / "test_example.py"
            test_file.parent.mkdir(parents=True)
            test_file.write_text("""
import pytest

@pytest.mark.really_unregistered_marker
class TestExample:
    def test_something(self):
        assert True
""")

            guard = PytestEnforcementGuard(tmpdir)
            errors, warnings = guard.validate_pytest_configuration()

            assert any("unregistered markers" in e for e in errors)
            assert "really_unregistered_marker" in str(errors)

    def test_conftest_hook_without_docstring(self):
        """Test warning when conftest hook lacks documentation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            pytest_ini = tmpdir / "pytest.ini"
            pytest_ini.write_text("""
[pytest]
testpaths = tests
markers =
    governance: Governance tests
    integration_full_deps: Integration tests with full dependencies
    asyncio: Async tests
    guardian: Guardian tests
    constitutional: Constitutional tests
""")

            conftest = tmpdir / "tests" / "conftest.py"
            conftest.parent.mkdir(parents=True)
            conftest.write_text("""
import pytest

def pytest_collection_modifyitems(config, items):
    marker_expr = config.getoption("-m", default="")
    # No docstring - should generate warning
""")

            guard = PytestEnforcementGuard(tmpdir)
            errors, warnings = guard.validate_pytest_configuration()

            assert len(errors) == 0
            assert any("missing docstring" in w for w in warnings)


if __name__ == "__main__":
    pytest.main([__file__])
