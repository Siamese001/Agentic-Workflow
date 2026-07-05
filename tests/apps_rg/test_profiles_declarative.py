"""apps-test-model: APP CONTRACT.

Validation tests for current apps_rg declarative profile files.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml


REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

PROFILE_PATHS = {
    "rg_evidence_profile.yaml": REPO_ROOT / "apps_rg" / "rg_evidence_profile.yaml",
    "rg_prompt_profile.yaml": REPO_ROOT / "apps_rg" / "rg_prompt_profile.yaml",
    "rg_style_profile.yaml": REPO_ROOT / "apps_rg" / "rg_style_profile.yaml",
    "rg_planning_profile.yaml": REPO_ROOT
    / "apps_rg"
    / "profiles"
    / "rg_planning_profile.yaml",
}

ADVISORY_PROFILE_SECTIONS = {
    "rg_evidence_profile.yaml": "extraction_rules",
    "rg_prompt_profile.yaml": "style_constraints",
    "rg_style_profile.yaml": "voice_and_tone",
}

FORBIDDEN_RUNTIME_PATTERNS = (
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
    "def _",
    "def ",
    "import ",
    "class ",
)


def _load_yaml(filename: str) -> dict:
    path = PROFILE_PATHS[filename]
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@pytest.mark.parametrize("filename", sorted(PROFILE_PATHS))
def test_current_profile_file_loads_as_yaml(filename: str) -> None:
    path = PROFILE_PATHS[filename]

    assert path.exists(), f"Profile not found: {path}"
    assert _load_yaml(filename)


@pytest.mark.parametrize("filename, section", sorted(ADVISORY_PROFILE_SECTIONS.items()))
def test_advisory_profiles_have_expected_section(filename: str, section: str) -> None:
    data = _load_yaml(filename)

    assert data.get("profile_metadata", {}).get("advisory_only") is True
    assert section in data


def test_planning_profile_is_planning_prior_only() -> None:
    data = _load_yaml("rg_planning_profile.yaml")

    assert data["schema_version"] == "apps_rg_l1_planning_profile.v1"
    assert data["profile_id"] == "rg_planning_profile"
    assert data["authority_class"] == "PLANNING_PRIOR_ONLY"
    assert set(data["generation_modes"]) == {
        "strategic_tailor",
        "tailor_existing",
        "generate_scratch",
        "section_regen",
        "healing_fact_check",
    }
    assert data["ambiguity_rules"]
    assert data["work_unit_profiles"]


@pytest.mark.parametrize("filename", sorted(PROFILE_PATHS))
def test_profiles_do_not_contain_runtime_authority_patterns(filename: str) -> None:
    content = str(_load_yaml(filename))

    for pattern in FORBIDDEN_RUNTIME_PATTERNS:
        assert pattern not in content, f"{filename}: found forbidden pattern {pattern!r}"


def test_ag_rggov_6a_duplicate_threshold_is_advisory() -> None:
    constraints = _load_yaml("rg_evidence_profile.yaml").get("content_constraints", {})
    duplicate_detection = constraints.get("duplicate_detection", {})

    assert duplicate_detection.get("duplicate_similarity_target") == 0.85
    assert duplicate_detection.get("advisory_semantics") is True


def test_ag_rggov_6b_target_gate_semantics() -> None:
    constraints = _load_yaml("rg_evidence_profile.yaml").get("content_constraints", {})
    thresholds = constraints.get("quality_thresholds", {})

    assert thresholds.get("min_quality_target") == 0.70
    assert thresholds.get("pass_gate_threshold") == 0.80
    assert thresholds.get("threshold_semantics") == "target_gate"


def test_ag_rggov_6c_weights_are_advisory() -> None:
    dimensions = _load_yaml("rg_evidence_profile.yaml").get("scoring_dimensions", {})

    assert dimensions.get("advisory_weighting") is True
    total = sum(row.get("weight", 0) for row in dimensions.get("dimensions", {}).values())
    assert total == pytest.approx(1.0)


def test_ag_rggov_6d_power_verbs_are_advisory() -> None:
    vocab = _load_yaml("rg_prompt_profile.yaml").get("vocabulary", {})

    assert vocab.get("style_preference") is True
    assert vocab.get("power_verbs_executive")
    guidance = vocab.get("verb_guidance", "").lower()
    assert "advisory" in guidance or "not a hard constraint" in guidance
