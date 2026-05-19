"""P1-W5 track-balanced exec summary + competencies grouping projections."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import pytest

from apps_rg.fact_inventory.track_balanced_section_projection import (
    P1_W4_CLOSEOUT_RECEIPT_REF,
    P1_W5_RECEIPT_JSON,
    build_p1_w5_track_balanced_sections,
    detect_cross_track_causal_prose,
    project_competencies_grouped_by_track,
    project_track_balanced_executive_summary,
    validate_competencies_grouped_by_track,
    validate_track_balanced_executive_summary,
    write_p1_w5_receipts,
    TrackBalancedProjectionError,
)
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    HYBRID_JD_FIXTURE,
    ROOT,
    build_track_weighted_expansion,
    infer_projection_role_family_key,
    load_augmented_skills_graph,
)
from apps_rg.fact_inventory.validate_p1_w4_track_weighted_closeout import (
    validate_p1_w4_track_weighted_closeout,
)

REPO = ROOT


@pytest.fixture(scope="module")
def hybrid_expansion() -> dict:
    graph = load_augmented_skills_graph(repo_root=REPO)
    role_key = infer_projection_role_family_key(
        target_role="SVP Engineering Agentic AI",
        jd_text=HYBRID_JD_FIXTURE,
    )
    return build_track_weighted_expansion(
        graph=graph,
        role_family_key=role_key,
        jd_text=HYBRID_JD_FIXTURE,
        enforce_hybrid_contract=True,
        bind_c03=True,
        repo_root=REPO,
    )


def test_p1_w4_closeout_receipt_exists_and_bound() -> None:
    path = REPO / P1_W4_CLOSEOUT_RECEIPT_REF
    assert path.is_file(), "P1-W4 closeout receipt must exist before P1-W5"
    closeout = json.loads(path.read_text(encoding="utf-8"))
    proof = closeout.get("c03_binding_proof") or {}
    assert proof.get("c03_graph_bound_status") == "BOUND"


def test_exec_projection_max_one_sentence_per_track(hybrid_expansion: dict) -> None:
    proj = project_track_balanced_executive_summary(hybrid_expansion, repo_root=REPO)
    validate_track_balanced_executive_summary(proj)
    counts = proj["sentence_count_by_track"]
    assert all(int(v) <= 1 for v in counts.values())
    assert proj["max_one_sentence_per_track"] is True
    assert proj["same_track_fact_support_only"] is True
    assert proj["broad_skills_ledger_used_as_authority"] is False


def test_exec_projection_same_track_facts_only(hybrid_expansion: dict) -> None:
    proj = project_track_balanced_executive_summary(hybrid_expansion, repo_root=REPO)
    facts_by_track: dict[str, set[str]] = defaultdict(set)
    for f in hybrid_expansion.get("selected_facts") or []:
        track = str(f.get("career_track") or "")
        fid = str(f.get("fact_id") or "")
        if track and fid:
            facts_by_track[track].add(fid)
    for track_id, entry in (proj.get("executive_summary_projection_by_track") or {}).items():
        if not entry.get("track_available"):
            continue
        src = set(entry.get("source_fact_ids") or [])
        assert src, f"{track_id} must cite facts"
        assert src.issubset(facts_by_track.get(track_id, set())), (
            f"{track_id} cites facts outside same-track graph selection: {src}"
        )


def test_causal_prose_detection_fails_validation() -> None:
    bad = {
        "projection_present": True,
        "sentence_count_by_track": {"track_genai_agentic": 1},
        "cross_track_causal_prose_detected": True,
        "broad_skills_ledger_used_as_authority": False,
        "executive_summary_projection_by_track": {},
    }
    with pytest.raises(TrackBalancedProjectionError):
        validate_track_balanced_executive_summary(bad)


def test_detect_cross_track_causal_prose() -> None:
    assert detect_cross_track_causal_prose("A leading to B across tracks")
    assert not detect_cross_track_causal_prose("Governed agentic runtime with policy gates.")


def test_competencies_grouped_by_track(hybrid_expansion: dict) -> None:
    proj = project_competencies_grouped_by_track(hybrid_expansion, repo_root=REPO)
    validate_competencies_grouped_by_track(proj)
    assert proj["grouped_by_career_track_id"] is True
    assert proj["broad_skills_ledger_used_as_authority"] is False
    assert proj["live_competencies_runtime_modified"] is False
    for bucket in (proj.get("competencies_grouped_by_track") or {}).values():
        for skill in bucket.get("skills") or []:
            assert skill.get("skill_id")
            assert skill.get("label")
            assert skill.get("fact_id_links")
            assert skill.get("graph_hop_path")


def test_broad_skills_ledger_authority_fails() -> None:
    bad = {
        "grouped_by_career_track_id": True,
        "live_competencies_runtime_modified": False,
        "broad_skills_ledger_used_as_authority": True,
        "competencies_grouped_by_track": {},
    }
    with pytest.raises(TrackBalancedProjectionError):
        validate_competencies_grouped_by_track(bad)


def test_p1_w5_receipt_write_and_fields() -> None:
    out = write_p1_w5_receipts(repo_root=REPO)
    assert P1_W5_RECEIPT_JSON.is_file()
    payload = out["payload"]
    assert payload.get("p1_w4_c03_graph_bound_status") == "BOUND"
    assert payload.get("p1_w4_closeout_receipt_ref") == P1_W4_CLOSEOUT_RECEIPT_REF
    assert payload.get("every_skill_has_fact_id_links") is True
    assert payload.get("every_skill_has_graph_hop_path") is True
    assert payload.get("live_competencies_runtime_modified") is False


def test_build_p1_w5_preserves_p1_w4_validator(hybrid_expansion: dict) -> None:
    validate_p1_w4_track_weighted_closeout(hybrid_expansion)
    built = build_p1_w5_track_balanced_sections(repo_root=REPO)
    assert built["executive_summary_projection"]["projection_present"] is True
    assert built["competencies_projection"]["projection_present"] is True
