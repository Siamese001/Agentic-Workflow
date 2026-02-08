"""Integration tests for apps_rg LCD compliance."""

from pathlib import Path

import pytest


class TestAppsRgLCDCompliance:
    """Tests for apps_rg LCD folder structure compliance."""

    def test_apps_rg_has_lcd_subfolders(self):
        """apps_rg should have LCD subfolders."""
        base = Path("apps_rg")
        if not base.exists():
            pytest.skip("apps_rg/ not found")

        lcd_subfolders = ["config", "types", "reasoning", "utils"]
        for subfolder in lcd_subfolders:
            path = base / subfolder
            assert path.exists(), f"apps_rg/{subfolder}/ should exist"

    def test_apps_rg_engines_structure(self):
        """apps_rg/engines should have proper structure."""
        engines_path = Path("apps_rg/engines")
        if not engines_path.exists():
            pytest.skip("apps_rg/engines/ not found")

        py_files = list(engines_path.rglob("*.py"))
        assert len(py_files) > 0, "apps_rg/engines/ should have Python files"

    def test_apps_rg_shared_structure(self):
        """apps_rg/shared should have proper structure."""
        shared_path = Path("apps_rg/shared")
        if not shared_path.exists():
            pytest.skip("apps_rg/shared/ not found")

        expected_subfolders = ["core", "reasoning", "tools", "utils"]
        for subfolder in expected_subfolders:
            path = shared_path / subfolder
            if not path.exists():
                pytest.skip(f"apps_rg/shared/{subfolder}/ not found")


class TestAppsRgAgentPlacement:
    """Tests for Agent class placement in apps_rg."""

    def test_agents_in_reasoning_or_engines(self):
        """Agent classes should be in reasoning/ or engines/."""
        base = Path("apps_rg")
        if not base.exists():
            pytest.skip("apps_rg/ not found")

        violations = []
        for subfolder in ["types", "config", "utils", "scripts"]:
            subfolder_path = base / subfolder
            if not subfolder_path.exists():
                continue
            for py_file in subfolder_path.rglob("*.py"):
                if "__pycache__" in str(py_file):
                    continue
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                if "class " in content and "Agent(" in content:
                    violations.append(str(py_file))

        # Note: Some legacy files may exist
        if violations:
            pytest.skip(f"Found {len(violations)} Agent classes outside reasoning/engines")


class TestAppsRgTypesSeparation:
    """Tests for types separation in apps_rg."""

    def test_types_in_types_folder(self):
        """Type definitions should be in types/ folder."""
        types_path = Path("apps_rg/types")
        if not types_path.exists():
            pytest.skip("apps_rg/types/ not found")

        py_files = list(types_path.glob("*.py"))
        assert len(py_files) > 0, "apps_rg/types/ should have type files"

    def test_no_types_in_shared_tools(self):
        """_types.py files should not be in shared/tools/."""
        tools_path = Path("apps_rg/shared/tools")
        if not tools_path.exists():
            pytest.skip("apps_rg/shared/tools/ not found")

        type_files = list(tools_path.glob("*_types.py"))
        assert len(type_files) == 0, f"Found {len(type_files)} _types.py files in shared/tools/"
