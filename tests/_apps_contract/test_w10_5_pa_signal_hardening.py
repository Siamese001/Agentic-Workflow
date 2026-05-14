"""W10.5 PA Signal Hardening — Structural contract tests.

Verifies:
- All new YAML artifacts exist and parse with yaml.safe_load
- All 9 prompt templates (8 original + unify_v1) exist and parse
- Section contracts have required fields
- forbidden_ai_phrases.yaml has HARD_BLOCK and SOFT_WARN entries
- jd_calibration_contract.yaml has required calibration fields
- E3 templates contain XML instruction_hierarchy + naturalness_guidance blocks
- E4 templates contain naturalness_guidance blocks
- unify_v1 exists and has the correct allowed_stage
- prompt_registry.yaml references all section_contract_refs for E3 templates
- Zero agentic_core imports in all new W10.5 files
- No new runtime entrypoints or provider/model invocations in new files
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PA_ROOT = _REPO_ROOT / "apps_rg" / "prompt_assembly"
_TEMPLATES_ROOT = _PA_ROOT / "templates"
_SECTION_CONTRACTS_ROOT = _PA_ROOT / "section_contracts"
_EXAMPLES_ROOT = _PA_ROOT / "examples"
_RUBRICS_ROOT = _PA_ROOT / "rubrics"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# W10.5.8: Shared YAML artifacts
# ---------------------------------------------------------------------------

class TestForbiddenAiPhrasesYaml:
    _path = _PA_ROOT / "forbidden_ai_phrases.yaml"

    def test_file_exists(self):
        assert self._path.exists(), f"Missing: {self._path}"

    def test_parses_with_safe_load(self):
        data = _load_yaml(self._path)
        assert isinstance(data, dict)

    def test_has_hard_block_entries(self):
        data = _load_yaml(self._path)
        content = self._path.read_text(encoding="utf-8")
        assert "HARD_BLOCK" in content, "forbidden_ai_phrases.yaml must contain HARD_BLOCK entries"

    def test_has_soft_warn_entries(self):
        content = self._path.read_text(encoding="utf-8")
        assert "SOFT_WARN" in content, "forbidden_ai_phrases.yaml must contain SOFT_WARN entries"

    def test_has_top_level_key(self):
        data = _load_yaml(self._path)
        assert len(data) > 0, "forbidden_ai_phrases.yaml must have top-level keys"


class TestJdCalibrationContractYaml:
    _path = _PA_ROOT / "jd_calibration_contract.yaml"

    def test_file_exists(self):
        assert self._path.exists(), f"Missing: {self._path}"

    def test_parses_with_safe_load(self):
        data = _load_yaml(self._path)
        assert isinstance(data, dict)

    def test_has_calibration_rules(self):
        content = self._path.read_text(encoding="utf-8")
        assert "calibration" in content.lower(), "jd_calibration_contract.yaml must contain calibration rules"

    def test_has_authenticity_constraint(self):
        content = self._path.read_text(encoding="utf-8")
        assert any(kw in content.lower() for kw in ["authentic", "mirror", "overfitting", "gap"]), \
            "jd_calibration_contract.yaml must address authenticity/mirroring/gap concerns"


# ---------------------------------------------------------------------------
# W10.5.1: Section contracts
# ---------------------------------------------------------------------------

SECTION_CONTRACT_FILES = [
    "executive_summary_contract.yaml",
    "unify_contract.yaml",
    "competencies_contract.yaml",
]


@pytest.mark.parametrize("filename", SECTION_CONTRACT_FILES)
def test_section_contract_exists(filename: str):
    path = _SECTION_CONTRACTS_ROOT / filename
    assert path.exists(), f"Section contract missing: {path}"


@pytest.mark.parametrize("filename", SECTION_CONTRACT_FILES)
def test_section_contract_parses(filename: str):
    path = _SECTION_CONTRACTS_ROOT / filename
    data = _load_yaml(path)
    assert isinstance(data, dict), f"{filename} must parse to a dict"
    assert len(data) > 0


@pytest.mark.parametrize("filename", SECTION_CONTRACT_FILES)
def test_section_contract_has_schema_version(filename: str):
    path = _SECTION_CONTRACTS_ROOT / filename
    data = _load_yaml(path)
    assert "schema_version" in data or "version" in data, \
        f"{filename} must have schema_version or version field"


# ---------------------------------------------------------------------------
# W10.5.2: Example YAMLs
# ---------------------------------------------------------------------------

EXAMPLE_FILES = [
    "executive_summary_examples.yaml",
    "unify_examples.yaml",
    "competencies_examples.yaml",
]


@pytest.mark.parametrize("filename", EXAMPLE_FILES)
def test_example_yaml_exists(filename: str):
    path = _EXAMPLES_ROOT / filename
    assert path.exists(), f"Example YAML missing: {path}"


@pytest.mark.parametrize("filename", EXAMPLE_FILES)
def test_example_yaml_parses(filename: str):
    path = _EXAMPLES_ROOT / filename
    data = _load_yaml(path)
    assert isinstance(data, dict), f"{filename} must parse to a dict"


@pytest.mark.parametrize("filename", EXAMPLE_FILES)
def test_example_yaml_has_positive_and_negative(filename: str):
    path = _EXAMPLES_ROOT / filename
    content = path.read_text(encoding="utf-8")
    assert "positive" in content.lower() or "correct" in content.lower(), \
        f"{filename} must include positive/correct examples"
    assert "negative" in content.lower() or "incorrect" in content.lower() or "wrong" in content.lower(), \
        f"{filename} must include negative/incorrect examples"


# ---------------------------------------------------------------------------
# W10.5.3: Rubric YAML
# ---------------------------------------------------------------------------

class TestSectionQualityRubrics:
    _path = _RUBRICS_ROOT / "section_quality_rubrics.yaml"

    def test_file_exists(self):
        assert self._path.exists(), f"Missing: {self._path}"

    def test_parses_with_safe_load(self):
        data = _load_yaml(self._path)
        assert isinstance(data, dict)

    def test_has_rubric_dimensions(self):
        data = _load_yaml(self._path)
        content = self._path.read_text(encoding="utf-8")
        assert "weight" in content.lower(), "Rubric must include weight fields"

    def test_has_severity_labels(self):
        content = self._path.read_text(encoding="utf-8")
        assert any(kw in content for kw in ["HARD_BLOCK", "SOFT_WARN", "severity"]), \
            "Rubric must include severity labels"


# ---------------------------------------------------------------------------
# W10.5.4: E3 template XML blocks
# ---------------------------------------------------------------------------

E3_TEMPLATES = [
    "strategic_tailor_v1.yaml",
    "tailor_existing_v1.yaml",
    "generate_scratch_v1.yaml",
    "enhance_current_v1.yaml",
]


@pytest.mark.parametrize("filename", E3_TEMPLATES)
def test_e3_template_exists(filename: str):
    assert (_TEMPLATES_ROOT / filename).exists()


@pytest.mark.parametrize("filename", E3_TEMPLATES)
def test_e3_template_parses(filename: str):
    data = _load_yaml(_TEMPLATES_ROOT / filename)
    assert isinstance(data, dict)


@pytest.mark.parametrize("filename", E3_TEMPLATES)
def test_e3_template_has_instruction_hierarchy(filename: str):
    content = (_TEMPLATES_ROOT / filename).read_text(encoding="utf-8")
    assert "<instruction_hierarchy>" in content, \
        f"{filename} must contain <instruction_hierarchy> XML block in S0"


@pytest.mark.parametrize("filename", E3_TEMPLATES)
def test_e3_template_has_governing_contract(filename: str):
    content = (_TEMPLATES_ROOT / filename).read_text(encoding="utf-8")
    assert "<governing_contract>" in content, \
        f"{filename} must contain <governing_contract> block"


@pytest.mark.parametrize("filename", E3_TEMPLATES)
def test_e3_template_has_naturalness_guidance(filename: str):
    content = (_TEMPLATES_ROOT / filename).read_text(encoding="utf-8")
    assert "<naturalness_guidance>" in content, \
        f"{filename} must contain <naturalness_guidance> XML block in I0"


@pytest.mark.parametrize("filename", E3_TEMPLATES)
def test_e3_template_has_jd_calibration_guidance(filename: str):
    content = (_TEMPLATES_ROOT / filename).read_text(encoding="utf-8")
    assert "<jd_calibration_guidance>" in content, \
        f"{filename} must contain <jd_calibration_guidance> XML block in I0"


@pytest.mark.parametrize("filename", E3_TEMPLATES)
def test_e3_template_has_pre_output_checklist(filename: str):
    content = (_TEMPLATES_ROOT / filename).read_text(encoding="utf-8")
    assert "<pre_output_checklist>" in content, \
        f"{filename} must contain <pre_output_checklist> XML block in I0"


@pytest.mark.parametrize("filename", E3_TEMPLATES)
def test_e3_template_forbidden_opener_listed(filename: str):
    content = (_TEMPLATES_ROOT / filename).read_text(encoding="utf-8")
    assert "Seasoned" in content or "FORBIDDEN_OPENERS" in content, \
        f"{filename} must call out forbidden opener phrases"


@pytest.mark.parametrize("filename", E3_TEMPLATES)
def test_e3_template_no_fabrication_oath_preserved(filename: str):
    content = (_TEMPLATES_ROOT / filename).read_text(encoding="utf-8")
    assert "NO_FABRICATION" in content or "no-fabrication" in content.lower() or "fabricat" in content.lower(), \
        f"{filename} must preserve the no-fabrication oath"


# ---------------------------------------------------------------------------
# W10.5.4+8.3: E4 templates have naturalness_guidance
# ---------------------------------------------------------------------------

E4_TEMPLATES_WITH_NATURALNESS = [
    "bullet_diversity_repair_v1.yaml",
    "resume_fact_check_v1.yaml",
    "unsupported_claim_omission_v1.yaml",
]


@pytest.mark.parametrize("filename", E4_TEMPLATES_WITH_NATURALNESS)
def test_e4_template_exists(filename: str):
    assert (_TEMPLATES_ROOT / filename).exists()


@pytest.mark.parametrize("filename", E4_TEMPLATES_WITH_NATURALNESS)
def test_e4_template_parses(filename: str):
    data = _load_yaml(_TEMPLATES_ROOT / filename)
    assert isinstance(data, dict)


@pytest.mark.parametrize("filename", E4_TEMPLATES_WITH_NATURALNESS)
def test_e4_template_has_naturalness_guidance(filename: str):
    content = (_TEMPLATES_ROOT / filename).read_text(encoding="utf-8")
    assert "<naturalness_guidance>" in content, \
        f"{filename} must contain <naturalness_guidance> block"


# ---------------------------------------------------------------------------
# W10.5.5: unify_v1.yaml
# ---------------------------------------------------------------------------

class TestUnifyV1Template:
    _path = _TEMPLATES_ROOT / "unify_v1.yaml"

    def test_file_exists(self):
        assert self._path.exists(), f"Missing: {self._path}"

    def test_parses_with_safe_load(self):
        data = _load_yaml(self._path)
        assert isinstance(data, dict)

    def test_allowed_stage_is_e4_heal(self):
        data = _load_yaml(self._path)
        assert data.get("allowed_stage") == "E4_HEAL", "unify_v1 must have allowed_stage=E4_HEAL"

    def test_has_unify_oath(self):
        content = self._path.read_text(encoding="utf-8")
        assert "UNIFY OATH" in content, "unify_v1 must contain UNIFY OATH"

    def test_has_naturalness_guidance(self):
        content = self._path.read_text(encoding="utf-8")
        assert "<naturalness_guidance>" in content

    def test_has_pre_output_checklist(self):
        content = self._path.read_text(encoding="utf-8")
        assert "<pre_output_checklist>" in content

    def test_has_instruction_hierarchy(self):
        content = self._path.read_text(encoding="utf-8")
        assert "<instruction_hierarchy>" in content

    def test_has_required_slots(self):
        data = _load_yaml(self._path)
        slot_bodies = data.get("slot_bodies", {})
        for slot in ("S0", "I0", "C0", "U0", "D0", "R0"):
            assert slot in slot_bodies, f"unify_v1 must have slot {slot}"


# ---------------------------------------------------------------------------
# W10.5.1: Registry has section_contract_refs for all E3 templates
# ---------------------------------------------------------------------------

class TestRegistrySectionContractRefs:
    _registry_path = _PA_ROOT / "prompt_registry.yaml"

    @pytest.fixture(scope="class")
    def registry(self):
        return _load_yaml(self._registry_path)

    def test_registry_exists(self):
        assert self._registry_path.exists()

    def test_e3_templates_have_section_contract_refs(self, registry):
        e3_templates = ["strategic_tailor_v1", "tailor_existing_v1", "generate_scratch_v1", "enhance_current_v1"]
        templates = registry.get("templates", {})
        for tid in e3_templates:
            assert tid in templates, f"Template {tid} not in registry"
            refs = templates[tid].get("section_contract_refs", {})
            assert refs, f"Template {tid} must have section_contract_refs"
            assert "executive_summary" in refs, f"Template {tid} must reference executive_summary contract"
            assert "competencies" in refs, f"Template {tid} must reference competencies contract"
            assert "unify" in refs, f"Template {tid} must reference unify contract"

    def test_unify_v1_in_registry(self, registry):
        templates = registry.get("templates", {})
        assert "unify_v1" in templates, "unify_v1 must be registered in prompt_registry.yaml"

    def test_section_contract_files_referenced_exist(self, registry):
        templates = registry.get("templates", {})
        for tid, tdata in templates.items():
            refs = tdata.get("section_contract_refs", {})
            for section_name, ref_path in refs.items():
                full_path = _PA_ROOT / ref_path
                assert full_path.exists(), \
                    f"Template {tid} section_contract_ref '{ref_path}' does not exist on disk"


# ---------------------------------------------------------------------------
# Governance: no agentic_core imports in new W10.5 files
# ---------------------------------------------------------------------------

NEW_W10_5_FILES = [
    _PA_ROOT / "forbidden_ai_phrases.yaml",
    _PA_ROOT / "jd_calibration_contract.yaml",
    _SECTION_CONTRACTS_ROOT / "executive_summary_contract.yaml",
    _SECTION_CONTRACTS_ROOT / "unify_contract.yaml",
    _SECTION_CONTRACTS_ROOT / "competencies_contract.yaml",
    _EXAMPLES_ROOT / "executive_summary_examples.yaml",
    _EXAMPLES_ROOT / "unify_examples.yaml",
    _EXAMPLES_ROOT / "competencies_examples.yaml",
    _RUBRICS_ROOT / "section_quality_rubrics.yaml",
    _TEMPLATES_ROOT / "unify_v1.yaml",
]


@pytest.mark.parametrize("path", NEW_W10_5_FILES, ids=[p.name for p in NEW_W10_5_FILES])
def test_new_yaml_file_has_no_agentic_core_reference(path: Path):
    content = path.read_text(encoding="utf-8")
    assert "agentic_core" not in content, \
        f"{path.name} must not reference agentic_core (PA-only boundary)"


@pytest.mark.parametrize("path", NEW_W10_5_FILES, ids=[p.name for p in NEW_W10_5_FILES])
def test_new_yaml_file_has_no_runtime_entrypoint(path: Path):
    content = path.read_text(encoding="utf-8")
    forbidden_patterns = ["openai", "anthropic", "requests.post", "httpx", "model_call", "vllm"]
    for pattern in forbidden_patterns:
        assert pattern not in content.lower(), \
            f"{path.name} must not contain runtime/provider reference: {pattern}"


# ---------------------------------------------------------------------------
# All 9 templates parse cleanly
# ---------------------------------------------------------------------------

ALL_TEMPLATES = [
    "strategic_tailor_v1.yaml",
    "tailor_existing_v1.yaml",
    "generate_scratch_v1.yaml",
    "enhance_current_v1.yaml",
    "resume_fact_check_v1.yaml",
    "unsupported_claim_omission_v1.yaml",
    "bullet_diversity_repair_v1.yaml",
    "unify_v1.yaml",
    "docx_manifest_v1.yaml",
]


@pytest.mark.parametrize("filename", ALL_TEMPLATES)
def test_all_templates_parse_cleanly(filename: str):
    path = _TEMPLATES_ROOT / filename
    assert path.exists(), f"Template missing: {path}"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{filename} must parse to a dict"
    assert "template_id" in data, f"{filename} must have template_id"
    assert "allowed_stage" in data, f"{filename} must have allowed_stage"


@pytest.mark.parametrize("filename", ALL_TEMPLATES)
def test_all_templates_have_slot_bodies(filename: str):
    path = _TEMPLATES_ROOT / filename
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert "slot_bodies" in data, f"{filename} must have slot_bodies"
    slot_bodies = data["slot_bodies"]
    assert "S0" in slot_bodies, f"{filename} slot_bodies must contain S0"
    assert "I0" in slot_bodies, f"{filename} slot_bodies must contain I0"


# ---------------------------------------------------------------------------
# W10.5 unify_v1: BOM and registry registration (moved from test_apps_rg_prompt_bom_exists.py)
# ---------------------------------------------------------------------------

_BOM_PATH = _PA_ROOT / "prompt_bom.yaml"
_REGISTRY_PATH = _PA_ROOT / "prompt_registry.yaml"


class TestUnifyV1Registration:
    """Asserts unify_v1 is registered in BOM and registry — W10.5 additions only."""

    def test_unify_v1_in_bom_template_refs(self):
        data = yaml.safe_load(_BOM_PATH.read_text(encoding="utf-8"))
        refs = data.get("template_registry_refs", [])
        assert "unify_v1" in refs, "unify_v1 must appear in prompt_bom.yaml template_registry_refs"

    def test_unify_v1_in_registry(self):
        data = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))
        templates = data.get("templates", {})
        assert "unify_v1" in templates, "unify_v1 must appear in prompt_registry.yaml templates"

    def test_unify_v1_registry_entry_has_required_fields(self):
        data = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))
        entry = data["templates"]["unify_v1"]
        assert "allowed_stage" in entry, "unify_v1 registry entry must have allowed_stage"
        assert entry["allowed_stage"] == "E4_HEAL", \
            f"unify_v1 must be E4_HEAL, got {entry['allowed_stage']}"
        assert "required_slots" in entry, "unify_v1 registry entry must have required_slots"
        assert "section_contract_refs" in entry, \
            "unify_v1 registry entry must have section_contract_refs"

    def test_unify_v1_template_file_exists(self):
        assert (_TEMPLATES_ROOT / "unify_v1.yaml").exists(), \
            "unify_v1.yaml template file must exist on disk"
