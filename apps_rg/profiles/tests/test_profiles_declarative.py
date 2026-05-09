"""
Profile Validation Tests for W3
Verifies apps_rg profile files are:
- Valid YAML/JSON syntax
- Declarative only (no Python imports)
- Properly structured per AG-RGGOV-6 classification
"""

import json
import pathlib

import pytest
import yaml


PROFILES_DIR = pathlib.Path(__file__).parent.parent


class TestProfileSyntax:
    """W3.1: Profile file syntax validation."""

    def test_rg_planning_profile_yaml(self):
        """rg_planning_profile.yaml loads as valid YAML."""
        path = PROFILES_DIR / "rg_planning_profile.yaml"
        assert path.exists(), f"Profile not found: {path}"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert "profile_metadata" in data
        assert "planning_constraints" in data

    def test_rg_evidence_profile_yaml(self):
        """rg_evidence_profile.yaml loads as valid YAML."""
        path = PROFILES_DIR / "rg_evidence_profile.yaml"
        assert path.exists(), f"Profile not found: {path}"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert "profile_metadata" in data
        assert "extraction_rules" in data

    def test_rg_prompt_profile_yaml(self):
        """rg_prompt_profile.yaml loads as valid YAML."""
        path = PROFILES_DIR / "rg_prompt_profile.yaml"
        assert path.exists(), f"Profile not found: {path}"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert "profile_metadata" in data
        assert "style_constraints" in data

    def test_rg_output_schema_json(self):
        """rg_output_schema.json loads as valid JSON."""
        path = PROFILES_DIR / "rg_output_schema.json"
        assert path.exists(), f"Profile not found: {path}"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data is not None
        assert "profile_metadata" in data
        assert "constraints" in data

    def test_rg_style_profile_yaml(self):
        """rg_style_profile.yaml loads as valid YAML."""
        path = PROFILES_DIR / "rg_style_profile.yaml"
        assert path.exists(), f"Profile not found: {path}"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert "profile_metadata" in data
        assert "voice_and_tone" in data

    def test_rg_capability_profile_yaml(self):
        """rg_capability_profile.yaml loads as valid YAML."""
        path = PROFILES_DIR / "rg_capability_profile.yaml"
        assert path.exists(), f"Profile not found: {path}"
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data is not None
        assert "profile_metadata" in data
        assert "declared_capabilities" in data


class TestProfileDeclarativeOnly:
    """W3.2: Profiles contain no runtime authority per AG-RGGOV-6."""

    def _load_yaml(self, filename: str) -> dict:
        path = PROFILES_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load_json(self, filename: str) -> dict:
        path = PROFILES_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f) or {}

    @pytest.mark.parametrize("filename", [
        "rg_planning_profile.yaml",
        "rg_evidence_profile.yaml",
        "rg_prompt_profile.yaml",
        "rg_style_profile.yaml",
        "rg_capability_profile.yaml",
    ])
    def test_yaml_no_runtime_keys(self, filename: str):
        """YAML profiles have no runtime authority keys."""
        data = self._load_yaml(filename)
        content = str(data)
        
        # Forbidden: runtime authority patterns
        forbidden_patterns = [
            "route_id",
            "execution_form",
            "provider",
            "model_authority",
            "prompt_artifact",
            "tool_call",
            "workflow_dag",
            "l2_work_order",
            "exit_disposition",
            "durable_write",
            "learning_proposal",
            "def _",  # No Python functions
            "def ",   # No Python functions
            "import ", # No Python imports
            "class ",  # No Python classes
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in content, f"{filename}: Found forbidden pattern '{pattern}'"

    def test_json_no_runtime_keys(self):
        """JSON profile has no runtime authority keys."""
        data = self._load_json("rg_output_schema.json")
        content = json.dumps(data)
        
        forbidden_patterns = [
            "route_id",
            "execution_form",
            "provider",
            "model_authority",
            "prompt_artifact",
            "tool_call",
            "workflow_dag",
            "l2_work_order",
            "exit_disposition",
            "durable_write",
            "learning_proposal",
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in content, f"rg_output_schema.json: Found forbidden pattern '{pattern}'"

    @pytest.mark.parametrize("filename", [
        "rg_planning_profile.yaml",
        "rg_evidence_profile.yaml",
        "rg_prompt_profile.yaml",
        "rg_style_profile.yaml",
        "rg_capability_profile.yaml",
    ])
    def test_yaml_advisory_flag_present(self, filename: str):
        """YAML profiles declare advisory_only: true per AG-RGGOV-6."""
        data = self._load_yaml(filename)
        metadata = data.get("profile_metadata", {})
        assert metadata.get("advisory_only") is True, f"{filename}: Must declare advisory_only: true"


class TestAG_RGGOV_6_Decisions:
    """W3.3: Profile content reflects AG-RGGOV-6a/6b/6c/6d decisions."""

    def _load_yaml(self, filename: str) -> dict:
        path = PROFILES_DIR / filename
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def test_ag_rggov_6a_duplicate_threshold_advisory(self):
        """AG-RGGOV-6a: duplicate_similarity_target is advisory (0.85)."""
        data = self._load_yaml("rg_evidence_profile.yaml")
        constraints = data.get("content_constraints", {})
        assert constraints.get("duplicate_similarity_target") == 0.85
        assert constraints.get("advisory_semantics") is True

    def test_ag_rggov_6b_target_gate_semantics(self):
        """AG-RGGOV-6b: TARGET/GATE semantics (0.7 target, 0.8 gate)."""
        data = self._load_yaml("rg_evidence_profile.yaml")
        thresholds = data.get("quality_thresholds", {})
        assert thresholds.get("min_quality_target") == 0.70
        assert thresholds.get("pass_gate_threshold") == 0.80
        assert thresholds.get("threshold_semantics") == "target_gate"

    def test_ag_rggov_6c_weights_advisory(self):
        """AG-RGGOV-6c: Scoring weights are advisory only."""
        data = self._load_yaml("rg_evidence_profile.yaml")
        dimensions = data.get("scoring_dimensions", {})
        assert dimensions.get("advisory_weighting") is True
        dims = dimensions.get("dimensions", {})
        # Verify weights sum to 1.0 (0.3+0.25+0.25+0.2)
        total = sum(d.get("weight", 0) for d in dims.values())
        assert abs(total - 1.0) < 0.001

    def test_ag_rggov_6d_power_verbs_advisory(self):
        """AG-RGGOV-6d: Power verbs are style preference (advisory)."""
        data = self._load_yaml("rg_style_profile.yaml")
        vocab = data.get("vocabulary", {})
        assert vocab.get("style_preference") is True
        power_verbs = vocab.get("power_verbs", [])
        assert len(power_verbs) > 0
        # Verify guidance text mentions advisory nature
        guidance = vocab.get("verb_guidance", "")
        assert "prefer" in guidance.lower() or "advisory" in guidance.lower() or "not hard constraint" in guidance.lower()
