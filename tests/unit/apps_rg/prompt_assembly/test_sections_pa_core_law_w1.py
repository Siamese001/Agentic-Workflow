"""W1: shared pa_core_law markers on w7 shell and section template headers."""

from __future__ import annotations

from pathlib import Path

import yaml

from apps_rg.prompt_assembly.pa_core_law import (
    core_law_marker_for_section,
    d0_untrusted_fence_reference_line,
)
from apps_rg.runtime.dispatch.unify_ibm_pa_common import load_w7_shell_slot_bodies

REPO = Path(__file__).resolve().parents[4]
TEMPLATES = REPO / "apps_rg" / "prompt_assembly" / "templates"


def test_core_law_markers_stable():
    assert core_law_marker_for_section("headline") == "HEADLINE_PROMPT_CORE_LAW_V3"
    assert core_law_marker_for_section("competencies") == "COMPETENCIES_PROMPT_CORE_LAW_V3"
    assert core_law_marker_for_section("unify_ibm") == "UNIFY_IBM_PROMPT_CORE_LAW_V3"


def test_w7_shell_yaml_references_pa_core_law():
    path = TEMPLATES / "w7_strategic_tailor_shell_slots.yaml"
    raw = path.read_text(encoding="utf-8")
    assert "UNIFY_IBM_PROMPT_CORE_LAW_V3" in raw
    assert "pa_core_law_v1.yaml" in raw
    assert "forbidden_slot_body_source: strategic_tailor_v1" in raw
    assert "pa_truth_oath_v1" in raw
    assert "pa_untrusted_data_fence_v1" in raw
    assert "PRODUCT_SHAPE" in raw
    assert raw.count("NO FABRICATION") == 1
    data = yaml.safe_load(raw)
    s0 = data["slot_bodies"]["S0"]
    assert "pa_proof_binding_v1" in s0
    assert "pa_targeting_only_v1" in s0
    d0 = data["slot_bodies"]["D0"]
    assert d0_untrusted_fence_reference_line().split(".")[0] in d0


def test_w7_shell_runtime_loader_matches_yaml():
    slots = load_w7_shell_slot_bodies()
    assert "S0" in slots and "pa_truth_oath_v1" in slots["S0"]
    assert "D0" in slots and "pa_untrusted_data_fence_v1" in slots["D0"]


def test_headline_template_w1_header_contract():
    raw = (TEMPLATES / "headline_tailor_v1.yaml").read_text(encoding="utf-8")
    assert "HEADLINE_PROMPT_CORE_LAW_V3" in raw
    assert "pa_core_law_ref:" in raw
    assert "forbidden_slot_body_source: strategic_tailor_v1" in raw


def test_competencies_pa_slots_w1_header_contract():
    raw = (TEMPLATES / "competency_selector_v2.pa_slots.yaml").read_text(encoding="utf-8")
    assert "COMPETENCIES_PROMPT_CORE_LAW_V3" in raw
    assert "pa_core_law_ref:" in raw
    assert "forbidden_slot_body_source: strategic_tailor_v1" in raw


def test_unify_ibm_spec_headers_w1_contract():
    for name in (
        "unify_bullet_tailor_v1.yaml",
        "unify_position_narrative_v1.yaml",
        "ibm_bullet_tailor_v1.yaml",
        "ibm_position_narrative_v1.yaml",
    ):
        raw = (TEMPLATES / name).read_text(encoding="utf-8")
        assert "UNIFY_IBM_PROMPT_CORE_LAW_V3" in raw, name
        assert "pa_core_law_ref:" in raw, name
        assert "forbidden_slot_body_source: strategic_tailor_v1" in raw, name


def test_w7_shell_s0_satisfies_no_fabrication_validator_token():
    """S0 must include NO FABRICATION literal for PromptAssemblyInput contract."""
    slots = load_w7_shell_slot_bodies()
    assert "NO FABRICATION" in slots["S0"]
    assert "governed by pa_truth_oath_v1" in slots["S0"]
