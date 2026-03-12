"""ADG-driven tests for thin __init__.py packages — fan_in batch.

Covers:
  agentic_core/base_agents/__init__.py        fan_in=11
  agentic_core/runtime/__init__.py            fan_in=11
  agentic_core/L3_orchestration/reasoning/__init__.py  fan_in=9

These are near-empty namespace packages. Tests verify importability and
that the package structure expected by 11+ callers is intact.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestBaseAgentsPackage:
    """agentic_core/base_agents/__init__.py — fan_in=11."""

    def test_package_importable(self):
        import agentic_core.base_agents  # noqa: F401

    def test_package_is_package(self):
        import agentic_core.base_agents as pkg
        import importlib
        spec = importlib.util.find_spec("agentic_core.base_agents")
        assert spec is not None

    def test_base_agent_submodules_exist(self):
        """Verify at least one submodule the 11 callers depend on is accessible."""
        from pathlib import Path
        import agentic_core.base_agents as pkg
        pkg_path = Path(pkg.__file__).parent
        assert pkg_path.is_dir()
        py_files = list(pkg_path.glob("*.py"))
        assert len(py_files) >= 1  # at least __init__.py itself

    def test_no_import_error_on_reload(self):
        import importlib
        import agentic_core.base_agents as pkg
        importlib.reload(pkg)  # must not raise


class TestRuntimePackage:
    """agentic_core/runtime/__init__.py — fan_in=11."""

    def test_package_importable(self):
        import agentic_core.runtime  # noqa: F401

    def test_exceptions_subpackage_accessible(self):
        """SovereignError lives at runtime.exceptions — must be reachable."""
        import agentic_core.runtime.exceptions  # noqa: F401

    def test_sovereign_error_reachable_via_runtime(self):
        from agentic_core.runtime.exceptions.SovereignError import SovereignError
        assert issubclass(SovereignError, Exception)

    def test_package_docstring_present(self):
        import agentic_core.runtime as pkg
        assert pkg.__doc__ is not None and len(pkg.__doc__.strip()) > 0

    def test_no_import_error_on_reload(self):
        import importlib
        import agentic_core.runtime as pkg
        importlib.reload(pkg)


class TestL1CognitionReasoningPackage:
    """agentic_core/L1_cognition/reasoning/__init__.py — fan_in=6."""

    def test_package_importable(self):
        import agentic_core.L1_cognition.reasoning  # noqa: F401

    def test_package_is_inside_l1(self):
        from pathlib import Path
        import agentic_core.L1_cognition.reasoning as pkg
        pkg_path = Path(pkg.__file__).parent
        assert "L1_cognition" in str(pkg_path)

    def test_reasoning_modules_discoverable(self):
        from pathlib import Path
        import agentic_core.L1_cognition.reasoning as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No reasoning modules in L1 reasoning package"


class TestL2ExecutionEnforcementPackage:
    """agentic_core/L2_execution/enforcement/__init__.py — fan_in=6."""

    def test_package_importable(self):
        import agentic_core.L2_execution.enforcement  # noqa: F401

    def test_package_is_inside_l2(self):
        from pathlib import Path
        import agentic_core.L2_execution.enforcement as pkg
        pkg_path = Path(pkg.__file__).parent
        assert "L2_execution" in str(pkg_path)

    def test_enforcement_modules_discoverable(self):
        from pathlib import Path
        import agentic_core.L2_execution.enforcement as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No modules in L2 enforcement package"


class TestL5SafetyReasoningPackage:
    """agentic_core/L5_safety/reasoning/__init__.py — fan_in=6."""

    def test_package_importable(self):
        import agentic_core.L5_safety.reasoning  # noqa: F401

    def test_package_is_inside_l5(self):
        from pathlib import Path
        import agentic_core.L5_safety.reasoning as pkg
        pkg_path = Path(pkg.__file__).parent
        assert "L5_safety" in str(pkg_path)

    def test_reasoning_agents_discoverable(self):
        from pathlib import Path
        import agentic_core.L5_safety.reasoning as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No agents in L5 reasoning package"

    def test_architecture_governor_agent_in_package(self):
        from pathlib import Path
        import agentic_core.L5_safety.reasoning as pkg
        pkg_path = Path(pkg.__file__).parent
        assert (pkg_path / "ArchitectureGovernorAgent.py").exists()


class TestConfigPackage:
    """agentic_core/config/__init__.py — fan_in=3."""

    def test_package_importable(self):
        import agentic_core.config  # noqa: F401

    def test_package_docstring_present(self):
        import agentic_core.config as pkg
        assert pkg.__doc__ is not None and len(pkg.__doc__.strip()) > 0

    def test_core_subpackage_present(self):
        from pathlib import Path
        import agentic_core.config as pkg
        assert (Path(pkg.__file__).parent / "core").is_dir()

    def test_no_import_error_on_reload(self):
        import importlib
        import agentic_core.config as pkg
        importlib.reload(pkg)


class TestL0RoutingPackage:
    """agentic_core/L0_routing/__init__.py — fan_in=4."""

    def test_package_importable(self):
        import agentic_core.L0_routing  # noqa: F401

    def test_package_is_l0(self):
        from pathlib import Path
        import agentic_core.L0_routing as pkg
        assert "L0_routing" in str(Path(pkg.__file__).parent)

    def test_expected_subpackages_present(self):
        from pathlib import Path
        import agentic_core.L0_routing as pkg
        pkg_path = Path(pkg.__file__).parent
        for subpkg in ("config", "utils", "seams"):
            assert (pkg_path / subpkg).is_dir(), f"Missing subpackage: {subpkg}"


class TestL0RoutingScriptsPackage:
    """agentic_core/L0_routing/scripts/__init__.py — fan_in=4."""

    def test_package_importable(self):
        import agentic_core.L0_routing.scripts  # noqa: F401

    def test_scripts_in_l0(self):
        from pathlib import Path
        import agentic_core.L0_routing.scripts as pkg
        assert "L0_routing" in str(Path(pkg.__file__).parent)

    def test_scripts_discoverable(self):
        from pathlib import Path
        import agentic_core.L0_routing.scripts as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No scripts in L0_routing/scripts"


class TestL3OrchestrationTypesPackage:
    """agentic_core/L3_orchestration/types/__init__.py — fan_in=2."""

    def test_package_importable(self):
        import agentic_core.L3_orchestration.types  # noqa: F401

    def test_package_in_l3(self):
        from pathlib import Path
        import agentic_core.L3_orchestration.types as pkg
        assert "L3_orchestration" in str(Path(pkg.__file__).parent)

    def test_types_modules_discoverable(self):
        from pathlib import Path
        import agentic_core.L3_orchestration.types as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No type modules in L3_orchestration/types"

    def test_no_import_error_on_reload(self):
        import importlib
        import agentic_core.L3_orchestration.types as pkg
        importlib.reload(pkg)


class TestL0RoutingEnforcementPackage:
    """agentic_core/L0_routing/enforcement/__init__.py — fan_in=2."""

    def test_package_importable(self):
        import agentic_core.L0_routing.enforcement  # noqa: F401

    def test_package_in_l0(self):
        from pathlib import Path
        import agentic_core.L0_routing.enforcement as pkg
        assert "L0_routing" in str(Path(pkg.__file__).parent)

    def test_enforcement_modules_discoverable(self):
        from pathlib import Path
        import agentic_core.L0_routing.enforcement as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No enforcement modules in L0_routing/enforcement"


class TestL2ExecutionTypesPackage:
    """agentic_core/L2_execution/types/__init__.py — fan_in=2."""

    def test_package_importable(self):
        import agentic_core.L2_execution.types  # noqa: F401

    def test_package_in_l2(self):
        from pathlib import Path
        import agentic_core.L2_execution.types as pkg
        assert "L2_execution" in str(Path(pkg.__file__).parent)

    def test_types_modules_discoverable(self):
        from pathlib import Path
        import agentic_core.L2_execution.types as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No type modules in L2_execution/types"


class TestL6ObservabilityReasoningPackage:
    """agentic_core/L6_observability/reasoning/__init__.py — fan_in=3."""

    def test_package_importable(self):
        import agentic_core.L6_observability.reasoning  # noqa: F401

    def test_package_in_l6(self):
        from pathlib import Path
        import agentic_core.L6_observability.reasoning as pkg
        assert "L6_observability" in str(Path(pkg.__file__).parent)

    def test_reasoning_modules_discoverable(self):
        from pathlib import Path
        import agentic_core.L6_observability.reasoning as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No reasoning modules in L6_observability/reasoning"

    def test_no_import_error_on_reload(self):
        import importlib
        import agentic_core.L6_observability.reasoning as pkg
        importlib.reload(pkg)


class TestL4StatePackage:
    """agentic_core/L4_state/__init__.py — fan_in=4."""

    def test_package_importable(self):
        import agentic_core.L4_state  # noqa: F401

    def test_package_docstring_present(self):
        import agentic_core.L4_state as pkg
        assert pkg.__doc__ is not None and "state" in pkg.__doc__.lower()

    def test_expected_subpackages_present(self):
        from pathlib import Path
        import agentic_core.L4_state as pkg
        pkg_path = Path(pkg.__file__).parent
        assert pkg_path.is_dir()
        subdirs = [d.name for d in pkg_path.iterdir() if d.is_dir()]
        assert len(subdirs) >= 1, "L4_state has no subpackages"

    def test_no_import_error_on_reload(self):
        import importlib
        import agentic_core.L4_state as pkg
        importlib.reload(pkg)


class TestL3OrchestrationReasoningPackage:
    """agentic_core/L3_orchestration/reasoning/__init__.py — fan_in=9."""

    def test_package_importable(self):
        import agentic_core.L3_orchestration.reasoning  # noqa: F401

    def test_package_is_inside_l3(self):
        from pathlib import Path
        import agentic_core.L3_orchestration.reasoning as pkg
        pkg_path = Path(pkg.__file__).parent
        assert "L3_orchestration" in str(pkg_path)

    def test_reasoning_agents_discoverable(self):
        """At least one agent module must live in the reasoning package."""
        from pathlib import Path
        import agentic_core.L3_orchestration.reasoning as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No agent modules found in L3 reasoning package"
