"""Unit tests for shared cross-section signal-loss guards (edge cases)."""

from __future__ import annotations

from apps_rg.runtime.sections.cross_section_signal_guards import (
    base_archive_ngram_overlap,
    detect_jd_only_phrases,
    is_flat_skill_only_graph_packet,
)


def test_base_archive_ngram_overlap_zero_without_references() -> None:
    assert base_archive_ngram_overlap("copied prose from archive", []) == 0.0
    assert base_archive_ngram_overlap("text", ["", "   "]) == 0.0


def test_base_archive_ngram_overlap_detects_shared_four_gram() -> None:
    prose = "owned platform delivery across regulated enterprise workflows"
    refs = ["prior owned platform delivery across regulated institutions"]
    overlap = base_archive_ngram_overlap(prose, refs, n=4)
    assert overlap > 0.2


def test_detect_jd_only_phrases_respects_min_run_and_deduplicates() -> None:
    jd = "seeking leader for agentic ai platform modernization programs"
    out = "leader for agentic ai platform modernization programs delivered"
    hits = detect_jd_only_phrases(out, jd, min_run=6)
    assert hits
    assert len(hits) == len(set(hits))


def test_detect_jd_only_phrases_empty_when_run_shorter_than_min_run() -> None:
    assert detect_jd_only_phrases("short output", "short jd", min_run=6) == []


def test_is_flat_skill_only_graph_packet_competency_bundle_id_counts() -> None:
    assert is_flat_skill_only_graph_packet(
        {"graph_skill_node_ids": ["s1"], "competency_bundle_id": "ccb_agentic_platforms"}
    ) is False
    assert is_flat_skill_only_graph_packet({"bundles": [{"competency_bundle_id": "x"}]}) is False
    assert is_flat_skill_only_graph_packet({"bound_skills": ["s1"]}) is True
