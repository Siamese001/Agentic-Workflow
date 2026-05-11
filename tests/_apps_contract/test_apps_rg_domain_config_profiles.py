"""
W3 acceptance tests: apps_rg domain config profile files.

Verifies:
  - All required profile files exist on disk
  - JSON profiles parse without error and have required top-level fields
  - YAML profiles parse without error and have required top-level fields
  - No runtime imports of quarantined modules in any profile file
  - Candidate gates reference valid gate_ids
  - Provider profiles contain no secrets or API keys
  - Meta feedback profile has all required learning_parameters
"""
import json
import os
from pathlib import Path

import pytest
import yaml

_APPS_RG_CONFIG = Path(__file__).resolve().parents[2] / "apps_rg" / "config"
_DOMAIN_CONTRACT = _APPS_RG_CONFIG / "domain_contract"

# ── File existence ─────────────────────────────────────────────────────────

class TestW3ProfileFilesExist:
    def test_runtime_gate_profile_exists(self):
        p = _DOMAIN_CONTRACT / "runtime_gate_profile.resume_generation.v1.json"
        assert p.exists(), f"Missing: {p}"

    def test_exit_profile_exists(self):
        p = _DOMAIN_CONTRACT / "exit_profile.resume_generation.v1.json"
        assert p.exists(), f"Missing: {p}"

    def test_judge_profile_exists(self):
        p = _DOMAIN_CONTRACT / "judge_profile.resume_generation.v1.json"
        assert p.exists(), f"Missing: {p}"

    def test_meta_feedback_profile_exists(self):
        p = _DOMAIN_CONTRACT / "meta_feedback_profile.resume_generation.v1.json"
        assert p.exists(), f"Missing: {p}"

    def test_provider_profiles_exists(self):
        p = _APPS_RG_CONFIG / "provider_profiles.yaml"
        assert p.exists(), f"Missing: {p}"

    def test_candidate_gates_exists(self):
        p = _APPS_RG_CONFIG / "candidate_gates.yaml"
        assert p.exists(), f"Missing: {p}"

    def test_workflow_manifest_exists(self):
        p = _APPS_RG_CONFIG / "workflow_manifest.resume_generation.v1.yaml"
        assert p.exists(), f"Missing: {p}"

    def test_section_prompts_dir_exists(self):
        p = _APPS_RG_CONFIG / "section_prompts"
        assert p.is_dir(), f"Missing directory: {p}"

    @pytest.mark.parametrize("fname", [
        "header_block.yaml",
        "professional_summary.yaml",
        "skills_block.yaml",
        "experience_block.yaml",
        "education_block.yaml",
        "certifications_block.yaml",
        "selected_projects_block.yaml",
        "final_render.yaml",
    ])
    def test_section_prompt_file_exists(self, fname):
        p = _APPS_RG_CONFIG / "section_prompts" / fname
        assert p.exists(), f"Missing: {p}"


# ── JSON parse + top-level fields ─────────────────────────────────────────

class TestRuntimeGateProfileStructure:
    def _load(self):
        p = _DOMAIN_CONTRACT / "runtime_gate_profile.resume_generation.v1.json"
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    def test_parses_clean(self):
        data = self._load()
        assert isinstance(data, dict)

    def test_required_top_level_fields(self):
        data = self._load()
        for field in ("runtime_gate_profile_id", "app_id", "task_class", "version", "status", "stages", "gate_laws"):
            assert field in data, f"Missing field: {field}"

    def test_app_id_correct(self):
        assert self._load()["app_id"] == "apps_rg"

    def test_stages_present(self):
        data = self._load()
        assert "stages" in data
        for stage in ("U0", "L1", "L0", "C0", "PA", "L2", "Exit"):
            assert stage in data["stages"], f"Missing stage: {stage}"

    def test_each_stage_has_required_gates(self):
        data = self._load()
        for stage, stage_data in data["stages"].items():
            gates = stage_data.get("required_gates", [])
            assert isinstance(gates, list), f"Stage {stage}: required_gates not a list"
            for gate in gates:
                assert "gate_id" in gate, f"Stage {stage}: gate missing gate_id"
                assert "severity" in gate, f"Stage {stage}: gate missing severity"

    def test_gate_laws_non_empty(self):
        data = self._load()
        assert len(data["gate_laws"]) >= 5

    def test_conditional_gate_triggers_present(self):
        data = self._load()
        assert "conditional_gate_triggers" in data
        assert "G25" in data["conditional_gate_triggers"]
        assert "G27" in data["conditional_gate_triggers"]


class TestExitProfileStructure:
    def _load(self):
        p = _DOMAIN_CONTRACT / "exit_profile.resume_generation.v1.json"
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    def test_parses_clean(self):
        assert isinstance(self._load(), dict)

    def test_required_top_level_fields(self):
        data = self._load()
        for field in ("exit_profile_id", "app_id", "task_class", "version", "status",
                      "required_exit_gates", "conditional_exit_gates", "gate_definitions"):
            assert field in data, f"Missing field: {field}"

    def test_required_exit_gates_all_present(self):
        data = self._load()
        required = set(data["required_exit_gates"])
        assert required == {"G21", "G22", "G23", "G24", "G26", "G28"}

    def test_conditional_exit_gates(self):
        data = self._load()
        assert "G25" in data["conditional_exit_gates"]
        assert "G27" in data["conditional_exit_gates"]

    def test_all_required_gates_defined(self):
        data = self._load()
        defs = data["gate_definitions"]
        for gate_id in data["required_exit_gates"]:
            assert gate_id in defs, f"Gate {gate_id} in required_exit_gates but not defined"

    def test_g22_has_dimension_thresholds(self):
        data = self._load()
        g22 = data["gate_definitions"]["G22"]
        assert "dimension_thresholds" in g22
        dt = g22["dimension_thresholds"]
        assert dt["factual_grounding"] == 0.95
        assert dt["no_fabrication"] == 0.99

    def test_g27_default_verdict_not_applicable(self):
        data = self._load()
        g27 = data["gate_definitions"]["G27"]
        assert g27["default_verdict"] == "NOT_APPLICABLE"

    def test_g25_is_conditional(self):
        data = self._load()
        g25 = data["gate_definitions"]["G25"]
        assert g25.get("conditional") is True
        assert "trigger_conditions" in g25
        assert len(g25["trigger_conditions"]) >= 5


class TestJudgeProfileStructure:
    def _load(self):
        p = _DOMAIN_CONTRACT / "judge_profile.resume_generation.v1.json"
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    def test_parses_clean(self):
        assert isinstance(self._load(), dict)

    def test_required_top_level_fields(self):
        data = self._load()
        for field in ("judge_profile_id", "app_id", "task_class", "version", "status",
                      "dimensions", "enforcement_rules"):
            assert field in data, f"Missing field: {field}"

    def test_all_rubric_dimensions_present(self):
        data = self._load()
        dim_ids = {d["dimension_id"] for d in data["dimensions"]}
        expected = {
            "factual_grounding", "ats_readability", "format_compliance",
            "no_fabrication", "concision", "role_alignment",
            "specificity", "executive_positioning"
        }
        assert expected == dim_ids

    def test_executive_positioning_informational_only(self):
        data = self._load()
        ep = next(d for d in data["dimensions"] if d["dimension_id"] == "executive_positioning")
        assert ep["informational_only"] is True
        assert ep["fail_closed_if_unknown"] is False

    def test_no_fabrication_threshold_correct(self):
        data = self._load()
        nf = next(d for d in data["dimensions"] if d["dimension_id"] == "no_fabrication")
        assert nf["threshold"] == 0.99
        assert nf["fail_closed_if_unknown"] is True

    def test_enforcement_rules_non_empty(self):
        data = self._load()
        assert len(data["enforcement_rules"]) >= 5

    def test_all_dimensions_have_grader_ref(self):
        data = self._load()
        for dim in data["dimensions"]:
            assert "grader_ref" in dim, f"Dimension {dim['dimension_id']} missing grader_ref"


class TestMetaFeedbackProfileStructure:
    def _load(self):
        p = _DOMAIN_CONTRACT / "meta_feedback_profile.resume_generation.v1.json"
        with open(p, encoding="utf-8") as f:
            return json.load(f)

    def test_parses_clean(self):
        assert isinstance(self._load(), dict)

    def test_required_top_level_fields(self):
        data = self._load()
        for field in ("meta_feedback_profile_id", "app_id", "task_class", "version",
                      "status", "learning_parameters", "learning_signals", "promotion_gate"):
            assert field in data, f"Missing field: {field}"

    def test_learning_parameters_present(self):
        data = self._load()
        lp = data["learning_parameters"]
        assert lp["promotion_threshold"] == 0.65
        assert lp["min_n_each_arm"] == 30
        assert lp["holdout_required"] is True
        assert lp["judge_calibration_cadence_days"] == 14
        assert lp["regret_budget"] == 0.10
        assert lp["z_score"] == 1.96
        assert lp["uplift_required"] is True

    def test_learning_signals_non_empty(self):
        data = self._load()
        signals = data["learning_signals"]
        assert len(signals) >= 5
        for sig in signals:
            assert "signal_id" in sig
            assert "description" in sig

    def test_promotion_gate_present(self):
        data = self._load()
        pg = data["promotion_gate"]
        assert "requires" in pg
        assert len(pg["requires"]) >= 5


# ── YAML profile structures ───────────────────────────────────────────────

class TestProviderProfilesStructure:
    def _load(self):
        p = _APPS_RG_CONFIG / "provider_profiles.yaml"
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_parses_clean(self):
        assert isinstance(self._load(), dict)

    def test_required_top_level_fields(self):
        data = self._load()
        for field in ("provider_profile_registry_id", "app_id", "profiles"):
            assert field in data, f"Missing field: {field}"

    def test_all_required_profiles_present(self):
        data = self._load()
        profiles = data["profiles"]
        for key in ("local_generator_stub", "local_qwen_generator", "deterministic_grader",
                    "llm_judge_stub", "executive_positioning_judge_stub"):
            assert key in profiles, f"Missing provider profile: {key}"

    def test_no_secrets_or_keys_in_profile(self):
        """Provider profiles must not contain literal secrets or API keys."""
        p = _APPS_RG_CONFIG / "provider_profiles.yaml"
        content = p.read_text(encoding="utf-8").lower()
        forbidden_patterns = [
            "sk-",          # OpenAI-style key prefix
            "bearer ",      # Authorization header
            "apikey=",      # inline key
            "password=",    # password
            "secret=",      # secret value
        ]
        for pattern in forbidden_patterns:
            assert pattern not in content, f"Possible secret pattern '{pattern}' found in provider_profiles.yaml"

    def test_local_qwen_uses_env_var_for_endpoint(self):
        data = self._load()
        qwen = data["profiles"]["local_qwen_generator"]
        assert qwen.get("endpoint_env_var") == "VLLM_BASE_URL"
        assert qwen.get("api_key_env_var") is None


class TestCandidateGatesStructure:
    def _load(self):
        p = _APPS_RG_CONFIG / "candidate_gates.yaml"
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_parses_clean(self):
        assert isinstance(self._load(), dict)

    def test_required_top_level_fields(self):
        data = self._load()
        for field in ("candidate_gate_profile_id", "app_id", "gates"):
            assert field in data, f"Missing field: {field}"

    def test_all_gates_have_required_fields(self):
        data = self._load()
        for gate in data["gates"]:
            for field in ("gate_id", "description", "threshold", "severity", "fail_closed"):
                assert field in gate, f"Gate {gate.get('gate_id', '?')} missing field: {field}"

    def test_no_fabrication_gate_is_hard_fail(self):
        data = self._load()
        nf_gate = next(g for g in data["gates"] if g["gate_id"] == "no_fabrication")
        assert nf_gate["severity"] == "hard_fail"
        assert nf_gate["fail_closed"] is True
        assert nf_gate["threshold"] == 0.99
        assert nf_gate["repair_allowed"] is False

    def test_all_gates_reference_runtime_gate_family(self):
        data = self._load()
        for gate in data["gates"]:
            assert "runtime_gate_family" in gate, f"Gate {gate['gate_id']} missing runtime_gate_family"


class TestWorkflowManifestStructure:
    def _load(self):
        p = _APPS_RG_CONFIG / "workflow_manifest.resume_generation.v1.yaml"
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_parses_clean(self):
        assert isinstance(self._load(), dict)

    def test_required_top_level_fields(self):
        data = self._load()
        for field in ("manifest_id", "owner_ref", "task_class", "execution_form",
                      "status", "nodes"):
            assert field in data, f"Missing field: {field}"

    def test_execution_form_is_managed_workflow(self):
        data = self._load()
        assert data["execution_form"] == "MANAGED_WORKFLOW"

    def test_required_cross_profile_refs_present(self):
        data = self._load()
        for field in ("orchestration_profile_ref", "output_schema_ref", "prompt_profile_ref",
                      "runtime_gate_profile_ref", "exit_profile_ref", "judge_profile_ref",
                      "provider_profile_ref", "candidate_gate_profile_ref",
                      "meta_feedback_profile_ref"):
            assert field in data, f"Missing ref: {field}"

    def test_required_nodes_present(self):
        data = self._load()
        node_ids = {n["node_id"] for n in data["nodes"]}
        for expected in ("profile_normalization", "role_analysis", "header_block",
                         "professional_summary", "skills_block", "experience_block",
                         "education_block", "final_render", "ats_validate",
                         "factual_grounding_check", "no_fabrication_guardrail"):
            assert expected in node_ids, f"Required node missing: {expected}"

    def test_all_nodes_have_required_fields(self):
        data = self._load()
        for node in data["nodes"]:
            for field in ("node_id", "node_type", "tier", "depends_on",
                          "selection_policy", "archive_policy", "required_runtime_gates"):
                assert field in node, f"Node {node.get('node_id', '?')} missing field: {field}"

    def test_no_python_imports_in_manifest(self):
        """Manifest must not contain Python import statements (comment references are OK)."""
        p = _APPS_RG_CONFIG / "workflow_manifest.resume_generation.v1.yaml"
        content = "\n" + p.read_text(encoding="utf-8")
        assert "\nimport apps_rg" not in content
        assert "\nfrom apps_rg" not in content
        assert "\nimport agentic_core" not in content


class TestSectionPromptProfiles:
    @pytest.mark.parametrize("fname,expected_node_id", [
        ("header_block.yaml", "header_block"),
        ("professional_summary.yaml", "professional_summary"),
        ("skills_block.yaml", "skills_block"),
        ("experience_block.yaml", "experience_block"),
        ("education_block.yaml", "education_block"),
        ("certifications_block.yaml", "certifications_block"),
        ("selected_projects_block.yaml", "selected_projects_block"),
        ("final_render.yaml", "final_render"),
    ])
    def test_section_prompt_structure(self, fname, expected_node_id):
        p = _APPS_RG_CONFIG / "section_prompts" / fname
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)
        assert data.get("node_id") == expected_node_id, f"{fname}: node_id mismatch"
        assert "prompt_id" in data
        assert "slot_requirements" in data
        assert "required" in data["slot_requirements"]
        assert "output_schema_ref" in data
        assert "prompt_boundary_rules" in data
        assert len(data["prompt_boundary_rules"]) >= 2


# ── No runtime imports in config files ───────────────────────────────────

QUARANTINE_SENTINEL = "DO_NOT_IMPORT_FROM_CORE_RUNTIME"
QUARANTINE_MODULE_PREFIXES = [
    "apps_rg.integrations.hops",
    "apps_rg.integrations.gates",
    "apps_rg.prompt_assembly.rg_pa_compiler",
    "apps_rg.engines.judges.executive_positioning_judge",
    "apps_rg.prompt_assembly.contracts",
]

class TestNoRuntimeImportsInConfigFiles:
    @pytest.mark.parametrize("config_file", [
        "workflow_manifest.resume_generation.v1.yaml",
        "provider_profiles.yaml",
        "candidate_gates.yaml",
    ])
    def test_no_quarantine_module_import_in_yaml(self, config_file):
        p = _APPS_RG_CONFIG / config_file
        lines = p.read_text(encoding="utf-8").splitlines()
        for module in QUARANTINE_MODULE_PREFIXES:
            for line in lines:
                stripped = line.strip()
                if module in stripped and not stripped.startswith("#"):
                    raise AssertionError(
                        f"{config_file}: non-comment line contains quarantined module "
                        f"reference '{module}': {line!r}"
                    )

    @pytest.mark.parametrize("json_file", [
        "runtime_gate_profile.resume_generation.v1.json",
        "exit_profile.resume_generation.v1.json",
        "judge_profile.resume_generation.v1.json",
        "meta_feedback_profile.resume_generation.v1.json",
    ])
    def test_no_quarantine_module_import_in_json(self, json_file):
        p = _DOMAIN_CONTRACT / json_file
        content = p.read_text(encoding="utf-8")
        for module in QUARANTINE_MODULE_PREFIXES:
            assert module not in content, (
                f"{json_file}: contains quarantined module reference '{module}'"
            )

    @pytest.mark.parametrize("section_file", [
        "header_block.yaml",
        "professional_summary.yaml",
        "skills_block.yaml",
        "experience_block.yaml",
        "education_block.yaml",
        "certifications_block.yaml",
        "selected_projects_block.yaml",
        "final_render.yaml",
    ])
    def test_no_quarantine_module_import_in_section_prompt(self, section_file):
        p = _APPS_RG_CONFIG / "section_prompts" / section_file
        content = p.read_text(encoding="utf-8")
        for module in QUARANTINE_MODULE_PREFIXES:
            assert module not in content, (
                f"{section_file}: contains quarantined module reference '{module}'"
            )
