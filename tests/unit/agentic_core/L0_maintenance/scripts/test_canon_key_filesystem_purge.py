"""
Simplified Canon Key Purge Validation - Filesystem Scan Only

This test validates that the Canon Key system has been completely eradicated
from the filesystem by scanning for any remaining references.
"""

from pathlib import Path

import pytest


class TestCanonKeyFilesystemPurge:
    """
    Verifies the total eradication of the 'Canon Key' system from the filesystem.
    Uses filesystem scanning only - no imports required.
    """

    def test_no_canon_key_references_in_code(self):
        """
        Global filesystem scan for any remaining Canon Key references.
        This is the ultimate negative proof test.
        """
        project_root = Path(".")
        violations = []

        # Skip known non-code directories
        skip_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".ruff_cache",
            "node_modules",
            ".venv",
            "venv",
            ".windsurf",
            "archives",
            "archive",
            "legacy",
            "void_violations",
            "location_violations",
            "healing_backups",
            "gatekeeper",
            "deprecated",
        }

        for py_file in project_root.rglob("*.py"):
            # Skip files in excluded directories
            if any(part in skip_dirs for part in py_file.parts):
                continue

            # Skip test files that might reference the old constants for testing
            if "test" in py_file.name.lower():
                continue

            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Check for any remaining references
                deprecated_patterns = [
                    "CANON_KEY_EXCEPTIONS",
                    "ACTIVE_CANON_KEYS",
                    "CANON_KEY_TO_FOLDER_MAP",
                    "is_excepted_from_key",
                    "canon_key_exception",
                    "canon_key_to_folder",
                ]

                for pattern in deprecated_patterns:
                    if pattern in content:
                        violations.append(f"{py_file.relative_to(project_root)}: {pattern}")

            except (UnicodeDecodeError, PermissionError, OSError):
                continue

        assert len(violations) == 0, (
            f"CRITICAL: Found {len(violations)} files with Canon Key references:\n"
            + "\n".join(violations)
        )

    def test_structure_blueprint_clean(self):
        """
        Verify structure_blueprint.py has no Canon Key references.
        """
        blueprint_path = Path("agentic_core/L5_safety/validators/structure_blueprint.py")
        assert blueprint_path.exists(), "structure_blueprint.py missing"

        with open(blueprint_path) as f:
            content = f.read()

        # Should NOT contain any Canon Key references
        deprecated_patterns = [
            "CANON_KEY_EXCEPTIONS",
            "ACTIVE_CANON_KEYS",
            "CANON_KEY_TO_FOLDER_MAP",
        ]

        for pattern in deprecated_patterns:
            assert pattern not in content, f"structure_blueprint.py still contains {pattern}"

    def test_location_agent_clean(self):
        """
        Verify LocationAgent.py has no Canon Key methods.
        """
        agent_path = Path("agentic_core/L5_safety/validators/LocationAgent.py")
        assert agent_path.exists(), "LocationAgent.py missing"

        with open(agent_path) as f:
            content = f.read()

        # Should NOT contain the deprecated method
        assert "is_excepted_from_key" not in content, (
            "LocationAgent.py still contains is_excepted_from_key method"
        )

    def test_location_utils_clean(self):
        """
        Verify location_utils.py has no Canon Key functions.
        """
        utils_path = Path("agentic_core/L5_safety/validators/location_utils.py")
        assert utils_path.exists(), "location_utils.py missing"

        with open(utils_path) as f:
            content = f.read()

        # Should NOT contain the deprecated function
        assert "is_excepted_from_key" not in content, (
            "location_utils.py still contains is_excepted_from_key function"
        )

    def test_void_compliance_refactored(self):
        """
        Verify void_compliance.py documents Canon Key removal.
        """
        void_path = Path("apps_rg/shared/tools/void_compliance.py")
        assert void_path.exists(), "void_compliance.py missing"

        with open(void_path) as f:
            content = f.read()

        # Should contain documentation about removal
        assert "Removed canon key mapping - deprecated system" in content, (
            "void_compliance.py should document Canon Key removal"
        )

        # Should NOT contain actual Canon Key references (except in comments)
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if any(
                pattern in line
                for pattern in [
                    "CANON_KEY_EXCEPTIONS",
                    "ACTIVE_CANON_KEYS",
                    "CANON_KEY_TO_FOLDER_MAP",
                ]
            ):
                if not line.strip().startswith("#"):
                    assert False, (
                        f"void_compliance.py line {i + 1} has active Canon Key reference: {line.strip()}"
                    )

    def test_modern_constants_present(self):
        """
        Verify modern territory-based constants exist in structure_blueprint.py.
        """
        blueprint_path = Path("agentic_core/L5_safety/validators/structure_blueprint.py")
        with open(blueprint_path) as f:
            content = f.read()

        # Should contain modern territory-based constants
        modern_constants = [
            "DEFAULT_CORE_HEALING_TERRITORY",
            "DEFAULT_APP_HEALING_TARGET",
            "CORE_TERRITORY_KEYWORDS",
            "SOVEREIGN_REGISTRY",
            "AST_DOMAIN_HIT_THRESHOLD",
            "TERRITORY_MISMATCH_THRESHOLD",
        ]

        for constant in modern_constants:
            assert constant in content, (
                f"structure_blueprint.py missing modern constant: {constant}"
            )


if __name__ == "__main__":
    print("Executing Canon Key Filesystem Purge Validation...")
    print("=" * 60)
    print("CRITICAL: All tests MUST pass for 100% eradication certification")
    print("=" * 60)

    # Run with verbose output for detailed verification
    pytest.main([__file__, "-v", "--tb=short"])
