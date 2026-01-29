"""
Knowledge Base Integrity Tests
Ensures the "brain transplant" was successful and data is structurally sound.
"""

import pytest
from apps_rg.domain.knowledge_base import FROZEN_SNAPSHOT, get_node_config, get_prompt


def test_critical_prompt_variables():
    """
    SKEPTICAL CHECK: Ensure the Hyde Generation prompt contains ALL required variables.
    If this fails, the K.1 Engine will crash at runtime.
    """
    prompt_obj = FROZEN_SNAPSHOT.prompts["k1_hyde_generation"]
    template = prompt_obj.template

    required = ["{company_name}", "{job_title}", "{sparse_jd}", "{company_type}"]
    for req in required:
        assert req in template, f"Missing critical variable {req} in K.1 prompt!"


def test_knode_config_constraints():
    """
    VERIFICATION: Ensure K.10 (Cover Letter) has the strict thresholds defined in the JSON map.
    """
    k10_config = get_node_config("K.10")

    # Check RAG Weight
    assert k10_config.config.rag_recency_weight == 0.25

    # Check Specific Rules
    thresholds = k10_config.config.qa_thresholds
    assert ">=3 company-specific details" in thresholds.values()
    assert "Unique to this company" in thresholds.values()


def test_global_rule_integrity():
    """
    INTEGRITY: Verify critical global validation gates exist.
    """
    rules = FROZEN_SNAPSHOT.global_rules
    assert "VG_BULLET_PUNCTUATION" in rules
    assert "VG_COMPETENCY_BALANCE" in rules

    # Verify specific logic in rule description
    assert "22-28 words" in rules["VG_COMPETENCY_BALANCE"]


def test_no_magic_string_failures():
    """
    SAFETY: Ensure calling for a non-existent prompt raises a hard error,
    preventing silent failures in production.
    """
    with pytest.raises(KeyError):
        get_prompt("NON_EXISTENT_PROMPT_ID")


def test_config_bounds_safety():
    """
    BOUNDARIES: Ensure no weight is > 1.0 or < 0.0.
    """
    for node in FROZEN_SNAPSHOT.nodes.values():
        w = node.config.rag_recency_weight
        assert 0.0 <= w <= 1.0, f"Node {node.id} has invalid weight {w}"


def test_all_k_nodes_present():
    """
    COMPLETENESS: Verify all K-nodes from K.1 to K.11 are defined.
    """
    expected_nodes = [
        "K.1",
        "K.2",
        "K.2.5",
        "K.3",
        "K.4",
        "K.5",
        "K.6",
        "K.7",
        "K.8",
        "K.9",
        "K.10",
        "K.11",
    ]
    for node_id in expected_nodes:
        assert node_id in FROZEN_SNAPSHOT.nodes, f"Missing K-Node: {node_id}"


def test_k9_leadership_competencies_strict():
    """
    K.9 SPECIFIC: Leadership competencies have the most complex validation rules.
    Verify they are all present.
    """
    k9 = get_node_config("K.9")
    thresholds = k9.config.qa_thresholds

    # Must have exactly 6 competencies
    assert "Exactly 6" in thresholds.values()

    # Must have deduplication rules
    assert "dedup_k4" in thresholds
    assert "dedup_k5" in thresholds
    assert "dedup_k6" in thresholds

    # Must have no target products rule
    assert "no_target_products" in thresholds


def test_prompt_shorthand_mapping():
    """
    USABILITY: Verify shorthand prompt IDs work correctly.
    """
    # These should not raise
    assert get_prompt("hyde_gen") is not None
    assert get_prompt("input_jd") is not None
    assert get_prompt("fix_names") is not None

    # Full ID should also work
    assert get_prompt("k1_hyde_generation") is not None
