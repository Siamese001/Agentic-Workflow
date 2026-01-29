from pathlib import Path

import pytest


# Disable path shield to see real files
@pytest.fixture
def disable_path_shield():
    return True


def test_renamed_files_exist(disable_path_shield):
    """Verify a random sample of manifest files were renamed."""
    # Sample from the provided manifest
    samples = [
        "apps_lic/domain/lic_archetypes.py",
        "apps_shared/common_utils/cache.py",
        "apps_lic/domain/models.py",
        "apps_rg/engines/resume_planner.py",
    ]

    root = Path(__file__).parent.parent

    for rel_path in samples:
        full_path = root / rel_path
        assert full_path.exists(), f"Renamed file missing: {rel_path}"


def test_old_files_gone(disable_path_shield):
    """Verify the old PascalCase files are removed."""
    # Test files that were actually renamed (not skipped due to existing targets)
    samples = [
        "apps_lic/domain/LicArchetypes.py",
        "apps_rg/engines/ResumePlanner.py",
        "apps_shared/common_utils/DagExecutorBasic.py",
    ]

    root = Path(__file__).parent.parent

    for rel_path in samples:
        full_path = root / rel_path
        assert not full_path.exists(), f"Old file still exists: {rel_path}"
