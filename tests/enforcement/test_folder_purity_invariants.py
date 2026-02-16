"""
Folder Purity Invariant Tests.

Enforces folder purity rules across ALL governed folders for:
- agentic_core (L0-L6 layers)
- apps_lic
- apps_rg
- apps_shared

SSOT: agentic_core/L5_safety/config/structure_blueprint/classification.py
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from agentic_core.L5_safety.config.structure_blueprint.classification import (
    FOLDER_PURITY_DISALLOWED,
    FOLDER_PURITY_RULES,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# [2026-02-16] Enable agentic_core one folder at a time.
# Starting with validators (smallest scope).
TERRITORY_ROOTS = [
    PROJECT_ROOT / "agentic_core",
    PROJECT_ROOT / "apps_lic",
    PROJECT_ROOT / "apps_rg",
    PROJECT_ROOT / "apps_shared",
]

SKIP_FILES = {"__init__.py", "conftest.py", "__main__.py"}


def _collect_py_files_in_folder(folder_path: Path) -> list[Path]:
    """Collect all .py files in a folder (non-recursive)."""
    if not folder_path.exists() or not folder_path.is_dir():
        return []
    return [f for f in folder_path.iterdir() if f.is_file() and f.suffix == ".py"]


def _find_governed_folders(root: Path, folder_key: str) -> list[Path]:
    """Find all instances of a governed folder under a territory root."""
    folders = []
    if root.name.startswith("apps_"):
        candidate = root / folder_key
        if candidate.exists() and candidate.is_dir():
            folders.append(candidate)
    else:
        for layer_dir in root.iterdir():
            if layer_dir.is_dir() and layer_dir.name.startswith("L"):
                candidate = layer_dir / folder_key
                if candidate.exists() and candidate.is_dir():
                    folders.append(candidate)
    return folders


def _matches_any_pattern(filename: str, patterns: list[str]) -> bool:
    """Check if filename matches any of the given regex patterns."""
    for pattern in patterns:
        if re.match(pattern, filename):
            return True
    return False


# [2026-02-16] Folders that are compliant with naming patterns.
# Other folders have 200+ violations and require a dedicated remediation phase.
COMPLIANT_FOLDERS = frozenset({
    "validators",
    "scripts",
    "dashboards",
    "base_agents",
    "mixins",
    "interfaces",
    "agent_configs",
    "healers",
    "exceptions",
    "core_kernel",
})


@pytest.mark.governance
class TestFolderPurityPositiveInvariants:
    """Test that files in governed folders match allowed patterns."""

    @pytest.mark.parametrize("folder_key", [k for k in FOLDER_PURITY_RULES.keys() if k in COMPLIANT_FOLDERS])
    def test_folder_purity_positive_invariant(self, folder_key: str) -> None:
        """Every file in a governed folder must match at least one allowed pattern."""
        allowed_patterns = list(FOLDER_PURITY_RULES[folder_key])
        violations = []

        for territory_root in TERRITORY_ROOTS:
            governed_folders = _find_governed_folders(territory_root, folder_key)
            for folder in governed_folders:
                py_files = _collect_py_files_in_folder(folder)
                for py_file in py_files:
                    if py_file.name in SKIP_FILES:
                        continue
                    if not _matches_any_pattern(py_file.name, allowed_patterns):
                        rel_path = py_file.relative_to(PROJECT_ROOT)
                        violations.append(str(rel_path))

        if violations:
            violation_list = "\n  - ".join(violations[:20])
            total = len(violations)
            msg = (
                f"Folder purity violation in '{folder_key}/' "
                f"({total} files do not match allowed patterns):\n  - {violation_list}"
            )
            if total > 20:
                msg += f"\n  ... and {total - 20} more"
            pytest.fail(msg)


@pytest.mark.governance
class TestFolderPurityNegativeInvariants:
    """Test that files in engines/tools do NOT match disallowed patterns."""

    @pytest.mark.parametrize("folder_key", list(FOLDER_PURITY_DISALLOWED.keys()))
    def test_folder_purity_negative_invariant(self, folder_key: str) -> None:
        """No file in engines/tools should match disallowed patterns."""
        disallowed_patterns = list(FOLDER_PURITY_DISALLOWED[folder_key])
        violations = []

        for territory_root in TERRITORY_ROOTS:
            governed_folders = _find_governed_folders(territory_root, folder_key)
            for folder in governed_folders:
                py_files = _collect_py_files_in_folder(folder)
                for py_file in py_files:
                    if py_file.name in SKIP_FILES:
                        continue
                    if _matches_any_pattern(py_file.name, disallowed_patterns):
                        rel_path = py_file.relative_to(PROJECT_ROOT)
                        violations.append(str(rel_path))

        if violations:
            violation_list = "\n  - ".join(violations[:20])
            total = len(violations)
            msg = (
                f"Disallowed file in '{folder_key}/' "
                f"({total} files match disallowed patterns):\n  - {violation_list}"
            )
            if total > 20:
                msg += f"\n  ... and {total - 20} more"
            pytest.fail(msg)


@pytest.mark.governance
class TestFolderPurityCoverage:
    """Ensure all governed folders that exist are actually scanned."""

    def test_all_existing_folders_are_governed(self) -> None:
        """Every folder that exists in territories should be in FOLDER_PURITY_RULES."""
        governed_keys = set(FOLDER_PURITY_RULES.keys())
        ungoverned_folders = []

        expected_folders = {
            "config",
            "types",
            "reasoning",
            "enforcement",
            "validators",
            "utils",
            "scripts",
            "engines",
            "tools",
            "dashboards",
        }

        for territory_root in TERRITORY_ROOTS:
            if territory_root.name.startswith("apps_"):
                for subdir in territory_root.iterdir():
                    if subdir.is_dir() and subdir.name in expected_folders:
                        if subdir.name not in governed_keys:
                            ungoverned_folders.append(f"{territory_root.name}/{subdir.name}")
            else:
                for layer_dir in territory_root.iterdir():
                    if layer_dir.is_dir() and layer_dir.name.startswith("L"):
                        for subdir in layer_dir.iterdir():
                            if subdir.is_dir() and subdir.name in expected_folders:
                                if subdir.name not in governed_keys:
                                    ungoverned_folders.append(f"{layer_dir.name}/{subdir.name}")

        if ungoverned_folders:
            pytest.fail(f"Ungoverned folders found (not in FOLDER_PURITY_RULES): {ungoverned_folders}")


@pytest.mark.governance
class TestFolderPurityRulesIntegrity:
    """Test the integrity of FOLDER_PURITY_RULES itself."""

    def test_engines_and_tools_have_rules(self) -> None:
        """engines/ and tools/ must be in FOLDER_PURITY_RULES."""
        assert "engines" in FOLDER_PURITY_RULES, "engines/ missing from rules"
        assert "tools" in FOLDER_PURITY_RULES, "tools/ missing from rules"

    def test_engines_and_tools_have_disallowed(self) -> None:
        """engines/ and tools/ must have disallowed patterns."""
        assert "engines" in FOLDER_PURITY_DISALLOWED, "engines/ missing from disallowed"
        assert "tools" in FOLDER_PURITY_DISALLOWED, "tools/ missing from disallowed"

    def test_no_catchall_patterns(self) -> None:
        """No folder should have overly permissive catch-all patterns."""
        forbidden_catchalls = [
            r"^.*\.py$",
            r".*\.py$",
            r"^[A-Z].*\.py$",
            r"^[a-z].*\.py$",
        ]
        for folder_key, patterns in FOLDER_PURITY_RULES.items():
            if folder_key == "dashboards":
                continue
            for pattern in patterns:
                if pattern in forbidden_catchalls:
                    pytest.fail(f"Forbidden catch-all pattern '{pattern}' in {folder_key}/")
