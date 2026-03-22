"""ADG-driven tests for thin app-layer __init__.py packages — fan_in batch.

Covers:
  apps_lic/utils/__init__.py          fan_in=4
  apps_rg/types/__init__.py           fan_in=4
  agentic_core/L4_state/reasoning/__init__.py  fan_in=3
  agentic_core/L4_state/utils/__init__.py      fan_in=3
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


class TestAppsLicUtils:
    """apps_lic/utils/__init__.py — fan_in=4."""

    def test_package_importable(self):
        import apps_lic.utils  # noqa: F401

    def test_package_is_in_apps_lic(self):
        from pathlib import Path

        import apps_lic.utils as pkg
        assert "apps_lic" in str(Path(pkg.__file__).parent)

    def test_utils_modules_discoverable(self):
        from pathlib import Path

        import apps_lic.utils as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No utility modules in apps_lic/utils"

    def test_no_import_error_on_reimport(self):
        import importlib

        import apps_lic.utils as pkg
        importlib.reload(pkg)


class TestAppsRgTypes:
    """apps_rg/types/__init__.py — fan_in=4."""

    def test_package_importable(self):
        import apps_rg.types  # noqa: F401

    def test_package_is_in_apps_rg(self):
        from pathlib import Path

        import apps_rg.types as pkg
        assert "apps_rg" in str(Path(pkg.__file__).parent)

    def test_types_modules_discoverable(self):
        from pathlib import Path

        import apps_rg.types as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No type modules in apps_rg/types"

    def test_no_import_error_on_reimport(self):
        import importlib

        import apps_rg.types as pkg
        importlib.reload(pkg)


class TestL4StateReasoningPackage:
    """agentic_core/L4_state/reasoning/__init__.py — fan_in=3."""

    def test_package_importable(self):
        import agentic_core.L4_state.reasoning  # noqa: F401

    def test_package_in_l4(self):
        from pathlib import Path

        import agentic_core.L4_state.reasoning as pkg
        assert "L4_state" in str(Path(pkg.__file__).parent)

    def test_reasoning_modules_discoverable(self):
        from pathlib import Path

        import agentic_core.L4_state.reasoning as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No reasoning modules in L4_state/reasoning"


class TestL4StateUtilsPackage:
    """agentic_core/L4_state/utils/__init__.py — fan_in=3."""

    def test_package_importable(self):
        import agentic_core.L4_state.utils  # noqa: F401

    def test_package_in_l4(self):
        from pathlib import Path

        import agentic_core.L4_state.utils as pkg
        assert "L4_state" in str(Path(pkg.__file__).parent)

    def test_utils_modules_discoverable(self):
        from pathlib import Path

        import agentic_core.L4_state.utils as pkg
        pkg_path = Path(pkg.__file__).parent
        py_files = [f for f in pkg_path.glob("*.py") if f.name != "__init__.py"]
        assert len(py_files) >= 1, "No utility modules in L4_state/utils"
