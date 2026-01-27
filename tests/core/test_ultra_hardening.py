import pytest
import re
from agentic_core.L5_safety.validators.structure_blueprint import is_path_allowed, SOVEREIGN_TERRITORIES

class TestUltraHardening:
    def test_legacy_prefix_rejection(self):
        """Test that legacy L3_ prefixes are blocked in prompt_governance."""
        legacy_path = "agentic_core/prompt_governance/L3_templates/meta_prompts.py"
        assert is_path_allowed(legacy_path) is False
        
        # Test lowercase variant
        legacy_path_lower = "agentic_core/prompt_governance/l3_templates/meta_prompts.py"
        assert is_path_allowed(legacy_path_lower) is False

    def test_weight_hierarchy_dominance(self):
        """Test that prompt_governance script weight is higher than generic L0 scripts."""
        pg_script_weight = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/scripts"]["weight"]
        l0_script_weight = 9  # Generic L0 maintenance script weight
        assert pg_script_weight > l0_script_weight
        
        # Verify meta_prompts has highest weight
        pg_meta_weight = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]["agentic_core/prompt_governance/meta_prompts"]["weight"]
        assert pg_meta_weight > pg_script_weight

    def test_l4_specialization_depth_integrity(self):
        """Test that L4 specialization paths are allowed."""
        valid_manifest = "agentic_core/prompt_governance/version_registry/manifests/active.json"
        assert is_path_allowed(valid_manifest) is True
        
        # Test other valid L4 paths
        valid_lock = "agentic_core/prompt_governance/version_registry/locks/current.lock"
        assert is_path_allowed(valid_lock) is True
        
        valid_lineage = "agentic_core/prompt_governance/version_registry/lineage/history.json"
        assert is_path_allowed(valid_lineage) is True

    def test_forbidden_extension_leak_protection(self):
        """Test that forbidden extensions are blocked in scripts."""
        from agentic_core.L5_safety.validators.structure_blueprint import ARTIFACT_ROUTING_MAP
        script_rules = ARTIFACT_ROUTING_MAP["agentic_core/L0_maintenance/scripts"]
        assert "class Test" in script_rules["forbidden_keywords"]
        assert "def test_" in script_rules["forbidden_keywords"]
        
        # Test that .py files are blocked from docs
        docs_rules = ARTIFACT_ROUTING_MAP["docs/reports"]
        assert ".py" in docs_rules["forbidden_extensions"]

    def test_prompt_governance_forbidden_patterns(self):
        """Test that forbidden patterns are properly configured in prompt_governance."""
        pg_config = SOVEREIGN_TERRITORIES["agentic_core"]["subfolders"]["prompt_governance"]
        assert "forbidden_patterns" in pg_config
        assert "L3_" in pg_config["forbidden_patterns"]
        assert "l3_" in pg_config["forbidden_patterns"]

    def test_gravity_well_shielding_signals(self):
        """Test that ast_signals include gravity well shielding with proper weights."""
        ast_signals = SOVEREIGN_TERRITORIES["agentic_core"]["ast_signals"]
        
        # Check meta_prompts has highest weight
        meta_weight = ast_signals["agentic_core/prompt_governance/meta_prompts"]["weight"]
        assert meta_weight == 15
        
        # Check scripts weight beats L0
        scripts_weight = ast_signals["agentic_core/prompt_governance/scripts"]["weight"]
        assert scripts_weight == 12
        
        # Check version registry weight
        version_weight = ast_signals["agentic_core/prompt_governance/version_registry"]["weight"]
        assert version_weight == 11

    def test_is_l4_approved_type_safety(self):
        """Test that is_l4_approved handles TypeError gracefully."""
        from agentic_core.L5_safety.validators.structure_blueprint import is_l4_approved
        
        # Test with invalid path (should not crash)
        assert is_l4_approved("invalid") is False
        assert is_l4_approved("only/two/parts") is False
        
        # Test with valid L4 path
        valid_l4 = "agentic_core/prompt_governance/version_registry/manifests/test.json"
        assert is_l4_approved(valid_l4) is True

    def test_required_dirs_configuration(self):
        """Test that required directories are properly configured."""
        pg_config = SOVEREIGN_TERRITORIES["agentic_core"]["subfolders"]["prompt_governance"]
        assert "required_dirs" in pg_config
        assert "agentic_core/prompt_governance/meta_prompts" in pg_config["required_dirs"]
        assert "agentic_core/prompt_governance/version_registry" in pg_config["required_dirs"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
