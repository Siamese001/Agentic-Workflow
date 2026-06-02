"""Unit tests for cross_section_signal_guards (shared resume-rigor detectors)."""

from __future__ import annotations

from apps_rg.runtime.sections.cross_section_signal_guards import (
    base_archive_ngram_overlap,
    detect_generic_consulting_phrases,
    detect_jd_only_phrases,
    is_flat_skill_only_graph_packet,
    seniority_floor_score,
    technical_specificity_score,
)


def test_seniority_floor_counts_strong_verbs() -> None:
    assert seniority_floor_score("Architected and scaled the platform") >= 1
    assert seniority_floor_score("helped with delivery") < seniority_floor_score(
        "Directed enterprise platform modernization"
    )


def test_technical_specificity_counts_mechanism_tokens() -> None:
    assert technical_specificity_score("deterministic routing and GraphRAG retrieval") >= 2
    assert technical_specificity_score("partnered with stakeholders on outcomes") == 0


def test_detect_generic_consulting_phrases() -> None:
    hits = detect_generic_consulting_phrases(
        "Led stakeholder management and cross-functional collaboration programs."
    )
    assert "stakeholder management" in hits or "cross-functional collaboration" in hits


def test_detect_jd_only_phrases_requires_long_shared_run() -> None:
    jd = "We need alpha beta gamma delta epsilon zeta for this role."
    out = "Candidate brings alpha beta gamma delta epsilon zeta to delivery."
    assert detect_jd_only_phrases(out, jd, min_run=6)
    assert not detect_jd_only_phrases("Unrelated prose only here.", jd, min_run=6)


def test_is_flat_skill_only_graph_packet_bundle_keys() -> None:
    assert is_flat_skill_only_graph_packet({"graph_skill_node_ids": ["skill_x"]})
    assert not is_flat_skill_only_graph_packet(
        {"headline_positioning_bundle_id": "hpb_agentic_ai_platforms"}
    )
    assert not is_flat_skill_only_graph_packet({"role_episode_bundles": [{"id": "reb_1"}]})
    assert not is_flat_skill_only_graph_packet({"competency_bundle_id": "ccb_runtime"})


def test_base_archive_ngram_overlap_empty_refs() -> None:
    assert base_archive_ngram_overlap("any text", []) == 0.0
    assert base_archive_ngram_overlap(
        "architected deterministic routing for enterprise scale",
        ["architected deterministic routing for regulated banks"],
    ) > 0.0
