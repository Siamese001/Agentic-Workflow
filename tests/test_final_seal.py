import pytest
import os
from pathlib import Path


class TestFinalSeal:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Verifies that 'legacy' directories are extinct.
    """

    def test_no_legacy_directories_exist(self):
        """
        Recursively scan the entire project. Fail if 'legacy' dir is found.
        """
        root = Path.cwd()
        legacy_found = []

        # Whitelist: .git history and .venv might have 'legacy' in paths, ignore them
        for dirpath, dirnames, filenames in os.walk(root):
            if ".git" in dirpath or ".venv" in dirpath or "venv" in dirpath:
                continue

            if "legacy" in dirnames:
                full_path = Path(dirpath) / "legacy"
                legacy_found.append(str(full_path.relative_to(root)))

        if legacy_found:
            pytest.fail(f"CRITICAL: Legacy pockets survived the purge!\n{legacy_found}")

    def test_legacy_artifacts_registry_intact(self):
        """Ensure we didn't delete the registry while deleting legacy folders."""
        # Import the registry to verify it exists and is accessible
        try:
            from agentic_core.domain.legacy_artifacts import LegacyArtifacts

            # Verify Phase 29 artifacts were added
            assert hasattr(LegacyArtifacts, "COMPANY_PLACEHOLDER_PATTERN")
            assert hasattr(LegacyArtifacts, "WEAK_OPENING_PATTERN")
            assert hasattr(LegacyArtifacts, "EXECUTIVE_MESSAGE_TEMPLATE")
        except ImportError as e:
            pytest.fail(f"The Legacy Artifacts Registry could not be imported: {e}")
