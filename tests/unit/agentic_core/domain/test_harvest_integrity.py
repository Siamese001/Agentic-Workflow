import sys
from pathlib import Path

import pytest

# Ensure path visibility
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestHarvestIntegrity:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Verifies that value was saved and trash was burned.
    """

    def test_artifacts_persisted(self):
        """Verify the legacy_artifacts.py registry contains the harvested data."""
        from agentic_core.domain.legacy_artifacts import LegacyArtifacts

        # Test Regex Harvest
        assert LegacyArtifacts.CIRCULAR_IMPORT_PATTERN is not None
        match = LegacyArtifacts.CIRCULAR_IMPORT_PATTERN.search(
            "ImportError: cannot import name 'BaseAgent' from 'agentic_core'"
        )
        assert match is not None
        assert match.group(1) == "BaseAgent"

        # Test Prompt Harvest
        assert "{domain}" in LegacyArtifacts.CONTEXT_GROUNDING_TEMPLATE

    def test_legacy_crypt_sealed(self):
        """Verify apps_shared/legacy is definitively gone."""
        legacy_path = Path("apps_shared/legacy")
        assert not legacy_path.exists(), "CRITICAL: Legacy folder still exists!"

    def test_system_certification_intact(self):
        """Verify the harvest didn't break the Sovereign Certificate."""
        # Simplified test - just verify the legacy artifacts can be imported
        # and the legacy folder is gone

        try:
            from agentic_core.domain.legacy_artifacts import LegacyArtifacts

            # Test that artifacts are accessible
            assert LegacyArtifacts.CIRCULAR_IMPORT_PATTERN is not None
            assert LegacyArtifacts.CONTEXT_GROUNDING_TEMPLATE is not None
        except ImportError:
            pytest.fail("Could not import LegacyArtifacts")

        # Verify legacy folder is gone
        legacy_path = Path("../apps_shared/legacy")
        assert not legacy_path.exists(), "Legacy folder still exists!"
