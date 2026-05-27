"""Unit tests for exec-summary-rc-structural-repair-f4a8c2.

Validates four structural root-cause fixes:
  W1: E0 SVP IT example S1 no longer contains 'commercialization' thread
  W2: fragment gate catches noun-phrase-fragment sentences; preferred_c0_display_text is a complete sentence
  W3: FACT_C0_DISPLAY_OVERRIDES forward-projection for fact_engineering_platform_002
  W4: scratch template connective tissue requirement
"""
from __future__ import annotations

import re
import yaml
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES_YAML = REPO_ROOT / "apps_rg/prompt_assembly/examples/executive_summary_examples.yaml"
SCRATCH_TEMPLATE = REPO_ROOT / "apps_rg/prompt_assembly/templates/executive_summary.generate_scratch_v1.yaml"


# ─────────────────────────────────────────────────────────────────
# W1: E0 SVP IT example S1 — no commercialization thread
# ─────────────────────────────────────────────────────────────────

def _get_svp_it_example() -> dict:
    data = yaml.safe_load(EXAMPLES_YAML.read_text(encoding="utf-8"))
    for ex in data.get("examples", []):
        if ex.get("id") == "exec_summary_pos_svp_it_strategy_001":
            return ex
    pytest.fail("exec_summary_pos_svp_it_strategy_001 not found in examples")


def test_e0_svp_it_s1_no_commercialization():
    """W1 RC-A: E0 SVP IT example S1 must not contain 'commercialization' as a thesis thread."""
    ex = _get_svp_it_example()
    after_text = str(ex.get("after", ""))
    s1 = after_text.strip().split("\n")[0].strip()
    assert "commercialization" not in s1.lower(), (
        f"E0 SVP IT S1 still contains 'commercialization': {s1!r}\n"
        "Root cause RC-A: model pattern-matches this to produce undelivered S1 thesis thread."
    )


def test_e0_svp_it_s1_uses_governance_innovation_framing():
    """W1: E0 SVP IT S1 should use IT governance / digital innovation framing."""
    ex = _get_svp_it_example()
    after_text = str(ex.get("after", ""))
    s1 = after_text.strip().split("\n")[0].strip().lower()
    assert any(kw in s1 for kw in ("governance", "innovation", "digital", "strategy")), (
        f"E0 SVP IT S1 should use governance/innovation framing: {s1!r}"
    )


def test_e0_svp_it_s6_forward_modal():
    """W1: E0 SVP IT example S6 (last sentence) should use forward-modal language."""
    ex = _get_svp_it_example()
    after_text = str(ex.get("after", ""))
    sentences = [s.strip() for s in after_text.strip().split("\n") if s.strip()]
    assert sentences, "No sentences in example"
    s6 = sentences[-1].lower()
    forward_modal_verbs = ("enables", "can ", "positions", "delivers", "scales", "preserving", "allows")
    has_forward = any(vm in s6 for vm in forward_modal_verbs)
    assert has_forward, (
        f"E0 SVP IT S6 should use forward-modal language, got: {s6!r}"
    )


def test_e0_svp_it_s6_not_past_tense_opener():
    """W1: E0 SVP IT S6 must not open with past-tense verb."""
    ex = _get_svp_it_example()
    after_text = str(ex.get("after", ""))
    sentences = [s.strip() for s in after_text.strip().split("\n") if s.strip()]
    s6 = sentences[-1].strip() if sentences else ""
    past_openers = ("Built", "Applied", "Directed", "Designed", "Implemented", "Scaled", "Developed")
    for opener in past_openers:
        assert not s6.startswith(opener), (
            f"E0 SVP IT S6 opens with past-tense verb '{opener}': {s6!r}"
        )


# ─────────────────────────────────────────────────────────────────
# W2a: preferred_c0_display_text for fact_quant_hpc_003 is complete sentence
# ─────────────────────────────────────────────────────────────────

def test_fsa_fact_display_override_is_complete_sentence():
    """W2a RC-B: FACT_C0_DISPLAY_OVERRIDES for fact_quant_hpc_003 must be a grammatically complete sentence."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        FACT_C0_DISPLAY_OVERRIDES,
        FSA_CREDENTIAL_FACT_ID,
    )
    text = FACT_C0_DISPLAY_OVERRIDES.get(FSA_CREDENTIAL_FACT_ID, "")
    assert text, f"No display override found for {FSA_CREDENTIAL_FACT_ID}"
    # A complete sentence has at least one finite verb token
    finite_verb_re = re.compile(
        r"\b(is|are|was|were|has|have|had|does|do|did|[a-z]{3,}s\b|[a-z]{3,}ed\b)\b",
        re.IGNORECASE,
    )
    assert finite_verb_re.search(text), (
        f"FSA fact display override appears to be a fragment (no finite verb): {text!r}"
    )


def test_fsa_fact_display_override_no_fragment_pattern():
    """W2a: FSA fact display override must not match the participial fragment pattern."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        FACT_C0_DISPLAY_OVERRIDES,
        FSA_CREDENTIAL_FACT_ID,
    )
    text = FACT_C0_DISPLAY_OVERRIDES.get(FSA_CREDENTIAL_FACT_ID, "")
    participial_re = re.compile(
        r"^[A-Z][^.!?]*,\s+(built|established|formed|developed|grounded|rooted|founded)\s+through\b",
        re.IGNORECASE,
    )
    assert not participial_re.search(text), (
        f"FSA fact display override still matches fragment pattern: {text!r}"
    )


# ─────────────────────────────────────────────────────────────────
# W2b: x2_exec_summary_no_sentence_fragment gate
# ─────────────────────────────────────────────────────────────────

def test_fragment_gate_catches_old_fsa_text():
    """W2b RC-B: Fragment gate must flag the old FSA-chartered fragment text."""
    from apps_rg.runtime.validators.executive_summary_x2 import check_exec_summary_no_sentence_fragment

    fragment_text = (
        "Enterprise technology leader who aligns governed AI platforms. "
        "Designs and operates platform runtime with deterministic controls. "
        "Through that foundation, platform modernization generated outcomes. "
        "FSA-chartered quantitative foundation, built through early-career capital modeling and portfolio stress analytics. "
        "That operating foundation directed large-scale transformations. "
        "Software dependency graph intelligence enables accelerated analysis."
    )
    ok, reason = check_exec_summary_no_sentence_fragment(fragment_text)
    assert not ok, "Fragment gate should have FAILED on noun-phrase fragment sentence"
    assert reason is not None
    assert "fragment" in reason.lower() or "participial" in reason.lower()


def test_fragment_gate_passes_complete_sentences():
    """W2b: Fragment gate must pass six grammatically complete sentences."""
    from apps_rg.runtime.validators.executive_summary_x2 import check_exec_summary_no_sentence_fragment

    complete_text = (
        "Enterprise technology leader who aligns governed AI platforms, regulatory lineage, and digital innovation into one IT strategy agenda. "
        "Designs and operates platform runtime with deterministic controls so innovation scales without sacrificing validation-ready delivery. "
        "Through that foundation, supply-chain platform modernization generated efficiency capture while growing the platform engineering team. "
        "Quantitative rigor was established through FSA-chartered actuarial work in capital modeling and portfolio stress analytics. "
        "That delivery foundation directed large-scale regulatory IT transformations for major financial institutions. "
        "Software dependency graph intelligence enables accelerated legacy-system analysis and transformation visibility across enterprise complexity."
    )
    ok, reason = check_exec_summary_no_sentence_fragment(complete_text)
    assert ok, f"Fragment gate should have PASSED all complete sentences, got: {reason}"


def test_fragment_gate_exported():
    """W2b: check_exec_summary_no_sentence_fragment must be importable from executive_summary_x2."""
    from apps_rg.runtime.validators import executive_summary_x2
    assert hasattr(executive_summary_x2, "check_exec_summary_no_sentence_fragment")


def test_fragment_gate_registered_in_x2_contract():
    """W2b: Fragment gate must be registered in SYNTHESIS_CHECK_TO_X2_GATE."""
    from apps_rg.runtime.sections.executive_summary_x2_x1d_contract import SYNTHESIS_CHECK_TO_X2_GATE
    assert "check_exec_summary_no_sentence_fragment" in SYNTHESIS_CHECK_TO_X2_GATE
    assert SYNTHESIS_CHECK_TO_X2_GATE["check_exec_summary_no_sentence_fragment"] == "x2_exec_summary_no_sentence_fragment"


def test_fragment_gate_in_monotonic_waive_set():
    """W2b: Fragment gate must be in the monotonic waive set to allow regen to fix fragments."""
    from apps_rg.runtime.sections.executive_summary_synthesis_monotonic import JUDGE_X2_REPAIR_WAIVE_SHRINK_GATE_IDS
    assert "x2_exec_summary_no_sentence_fragment" in JUDGE_X2_REPAIR_WAIVE_SHRINK_GATE_IDS


# ─────────────────────────────────────────────────────────────────
# W3: FACT_C0_DISPLAY_OVERRIDES forward projection for fact_engineering_platform_002
# ─────────────────────────────────────────────────────────────────

def test_dependency_graph_fact_has_display_override():
    """W3 RC-C: FACT_C0_DISPLAY_OVERRIDES must contain fact_engineering_platform_002."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        DEPENDENCY_GRAPH_FACT_ID,
        FACT_C0_DISPLAY_OVERRIDES,
    )
    assert DEPENDENCY_GRAPH_FACT_ID == "fact_engineering_platform_002"
    assert DEPENDENCY_GRAPH_FACT_ID in FACT_C0_DISPLAY_OVERRIDES, (
        "fact_engineering_platform_002 must have a C0 display override for forward projection"
    )


def test_dependency_graph_display_override_forward_modal():
    """W3 RC-C: forward projection display text must use present-tense enabling verbs."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        DEPENDENCY_GRAPH_FACT_ID,
        FACT_C0_DISPLAY_OVERRIDES,
    )
    text = FACT_C0_DISPLAY_OVERRIDES[DEPENDENCY_GRAPH_FACT_ID]
    forward_verbs = ("enables", "exposes", "improves", "positions", "can ", "delivers")
    assert any(v in text.lower() for v in forward_verbs), (
        f"Dependency graph display override must use forward-modal verbs, got: {text!r}"
    )


def test_dependency_graph_display_override_no_past_tense_opener():
    """W3 RC-C: forward projection display text must NOT open with past-tense verb."""
    from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
        DEPENDENCY_GRAPH_FACT_ID,
        FACT_C0_DISPLAY_OVERRIDES,
    )
    text = FACT_C0_DISPLAY_OVERRIDES[DEPENDENCY_GRAPH_FACT_ID]
    past_openers = ("Built", "Applied", "Directed", "Designed", "Implemented")
    for opener in past_openers:
        assert not text.startswith(opener), (
            f"Dependency graph display override opens with past-tense '{opener}': {text!r}"
        )


def test_dependency_graph_fact_id_exported():
    """W3: DEPENDENCY_GRAPH_FACT_ID must be in __all__ of executive_summary_synthesis_contract."""
    from apps_rg.runtime.sections import executive_summary_synthesis_contract as mod
    assert "DEPENDENCY_GRAPH_FACT_ID" in mod.__all__


# ─────────────────────────────────────────────────────────────────
# W4: Connective tissue requirement in scratch template
# ─────────────────────────────────────────────────────────────────

def _load_scratch_template_text() -> str:
    return SCRATCH_TEMPLATE.read_text(encoding="utf-8")


def test_scratch_template_has_connective_tissue_requirement():
    """W4 RC-D: scratch template must contain connective tissue requirement for S2-S5."""
    text = _load_scratch_template_text()
    assert "thesis-referent connector" in text or "connective tissue" in text.lower(), (
        "Scratch template must contain connective tissue requirement for S2-S5"
    )


def test_scratch_template_bans_bare_achievement_openers():
    """W4 RC-D: scratch template must explicitly forbid bare achievement-verb S2-S5 openers."""
    text = _load_scratch_template_text()
    assert "achievement_inventory_stack" in text or "achievement bullet" in text.lower(), (
        "Scratch template must warn about achievement_inventory_stack critique tag for bare openers"
    )


def test_scratch_template_s4_completeness_requirement():
    """W2b (template side): scratch template must require S4 to be a complete sentence."""
    text = _load_scratch_template_text()
    assert "x2_exec_summary_no_sentence_fragment" in text or "complete sentence" in text.lower(), (
        "Scratch template must reference S4 sentence completeness requirement"
    )
