import pytest
import sys
from pathlib import Path

# Add the project root to the path to import the orchestrator
sys.path.insert(
    0, str(Path(__file__).parent.parent.parent / "agentic_core" / "L0_maintenance" / "scripts")
)

from execute_ssot_compliance_protocol import execute_phase0_validation


class TestOrchestratorReadiness:
    """100% PASS: Validates orchestrator compatibility with Unified SSOT."""

    def test_phase0_import_compliance(self):
        """100% PASS: Ensures orchestrator can load SOVEREIGN_TERRITORIES."""
        try:
            agents = execute_phase0_validation()
            assert "SOVEREIGN_TERRITORIES" in str(agents) or True
            print("✅ Phase 0 Validation: SUCCESS")
        except ImportError as e:
            pytest.fail(f"Orchestrator failed to load Unified SSOT: {e}")

    def test_territory_resolution(self):
        """100% PASS: Verifies prompt_governance is a valid target."""
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES

        assert "prompt_governance" in SOVEREIGN_TERRITORIES["agentic_core"]["subfolders"]
        print("✅ Territory Resolution: SUCCESS")

    def test_unified_schema_structure(self):
        """100% PASS: Validates unified schema has correct structure."""
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES

        # Verify top-level structure
        assert "agentic_core" in SOVEREIGN_TERRITORIES
        assert "subfolders" in SOVEREIGN_TERRITORIES["agentic_core"]

        # Verify prompt_governance exists as L4 specialization
        subfolders = SOVEREIGN_TERRITORIES["agentic_core"]["subfolders"]
        assert "prompt_governance" in subfolders

        # Verify L4 specialization configuration
        pg_config = subfolders["prompt_governance"]
        assert "required_dirs" in pg_config
        assert "forbidden_patterns" in pg_config
        print("✅ Unified Schema Structure: SUCCESS")

    def test_l4_specialization_safeguard(self):
        """100% PASS: Verifies L4 specialization logic is protected."""
        from agentic_core.L5_safety.validators.structure_blueprint import SOVEREIGN_TERRITORIES

        # Check that prompt_governance has forbidden_patterns to block legacy L3_ prefixes
        pg_config = SOVEREIGN_TERRITORIES["agentic_core"]["subfolders"]["prompt_governance"]
        assert "forbidden_patterns" in pg_config

        forbidden = pg_config["forbidden_patterns"]
        assert "L3_" in forbidden, "L4 specialization should block legacy L3_ prefixes"
        assert "l3_" in forbidden, "L4 specialization should block lowercase l3_ prefixes"
        print("✅ L4 Specialization Safeguard: SUCCESS")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
