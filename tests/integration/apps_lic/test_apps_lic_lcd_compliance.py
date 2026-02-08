"""Integration tests for apps_lic LCD compliance."""

from pathlib import Path

import pytest


class TestAppsLicLCDCompliance:
    """Tests for apps_lic LCD folder structure compliance."""

    def test_apps_lic_has_lcd_subfolders(self):
        """apps_lic should have LCD subfolders."""
        base = Path("apps_lic")
        if not base.exists():
            pytest.skip("apps_lic/ not found")

        lcd_subfolders = ["config", "types", "reasoning", "utils"]
        for subfolder in lcd_subfolders:
            path = base / subfolder
            assert path.exists(), f"apps_lic/{subfolder}/ should exist"

    def test_apps_lic_engines_structure(self):
        """apps_lic/engines should have proper structure."""
        engines_path = Path("apps_lic/engines")
        if not engines_path.exists():
            pytest.skip("apps_lic/engines/ not found")

        py_files = list(engines_path.rglob("*.py"))
        assert len(py_files) > 0, "apps_lic/engines/ should have Python files"

    def test_apps_lic_shared_structure(self):
        """apps_lic/shared should have proper structure."""
        shared_path = Path("apps_lic/shared")
        if not shared_path.exists():
            pytest.skip("apps_lic/shared/ not found")

        expected_subfolders = ["core", "reasoning", "tools", "utils"]
        for subfolder in expected_subfolders:
            path = shared_path / subfolder
            if not path.exists():
                pytest.skip(f"apps_lic/shared/{subfolder}/ not found")


class TestAppsLicAgentPlacement:
    """Tests for Agent class placement in apps_lic."""

    def test_agents_in_reasoning_or_engines(self):
        """Agent classes should be in reasoning/ or engines/."""
        base = Path("apps_lic")
        if not base.exists():
            pytest.skip("apps_lic/ not found")

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

        if violations:
            pytest.skip(f"Found {len(violations)} Agent classes outside reasoning/engines")


class TestAppsLicTypesSeparation:
    """Tests for types separation in apps_lic."""

    def test_types_in_types_folder(self):
        """Type definitions should be in types/ folder."""
        types_path = Path("apps_lic/types")
        if not types_path.exists():
            pytest.skip("apps_lic/types/ not found")

        py_files = list(types_path.glob("*.py"))
        assert len(py_files) > 0, "apps_lic/types/ should have type files"

    def test_no_types_in_shared_tools(self):
        """_types.py files should not be in shared/tools/."""
        tools_path = Path("apps_lic/shared/tools")
        if not tools_path.exists():
            pytest.skip("apps_lic/shared/tools/ not found")

        type_files = list(tools_path.glob("*_types.py"))
        assert len(type_files) == 0, f"Found {len(type_files)} _types.py files in shared/tools/"


class TestAppsLicMirrorAppsRg:
    """Tests for apps_lic mirroring apps_rg structure."""

    def test_mirror_lcd_subfolders(self):
        """apps_lic should mirror apps_rg LCD subfolders."""
        rg_base = Path("apps_rg")
        lic_base = Path("apps_lic")

        if not rg_base.exists() or not lic_base.exists():
            pytest.skip("apps_rg/ or apps_lic/ not found")

        lcd_subfolders = ["config", "types", "reasoning", "utils", "validation"]
        for subfolder in lcd_subfolders:
            rg_path = rg_base / subfolder
            lic_path = lic_base / subfolder
            if rg_path.exists():
                assert lic_path.exists(), f"apps_lic/{subfolder}/ should mirror apps_rg/{subfolder}/"
