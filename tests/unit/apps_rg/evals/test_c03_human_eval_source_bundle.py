from __future__ import annotations

import copy
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from apps_rg.evals.c03_human_eval._io import (
    file_digest,
    record_with_digest,
    stable_digest,
)
from apps_rg.evals.c03_human_eval._safety import unsafe_reviewer_keys
from apps_rg.evals.c03_human_eval.packet import assess_source_bundle_readiness
from apps_rg.evals.c03_human_eval import source_bundle
from apps_rg.evals.c03_human_eval.source_bundle import (
    SourceBundleFreezeError,
    freeze_allocation_source_bundle,
)
from apps_rg.runtime.c0.resume_graph_allocation import (
    DEFAULT_MAX_CANDIDATES_PER_SLOT,
)

REPO = Path(__file__).resolve().parents[4]
TARGET_MANIFEST = REPO / "apps_rg/evals/c03_human_eval/target_cases.v1.yaml"
SECTION_COUNTS = {
    "competencies": 8,
    "unify_bullets": 6,
    "ibm_bullets": 5,
    "insurtech_bullets": 3,
    "ey_bullets": 3,
    "unify_narrative": 6,
    "ibm_narrative": 5,
    "insurtech_narrative": 3,
    "ey_narrative": 3,
    "executive_summary": 3,
    "headline": 2,
}
RANKED_SECTIONS = {
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "insurtech_bullets",
    "ey_bullets",
    "executive_summary",
    "headline",
}


def _test_freeze_receipt(source: dict[str, Any]) -> dict[str, Any]:
    claims = [claim for case in source["cases"] for claim in case["claims"]]
    source_bytes = (
        json.dumps(source, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    return record_with_digest(
        {
            "schema_version": "apps_rg.c03_human_eval.source_freeze_receipt.v1",
            "freeze_mode": "TEST_ONLY_UNTRUSTED_FIXTURE",
            "official_provenance_eligible": False,
            "checkout_head_verified": False,
            "checkout_clean_verified": False,
            "source_bundle_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "source_bundle_canonical_digest": stable_digest(source),
            "source_commit_sha": source["source_commit_sha"],
            "target_manifest_digest": file_digest(TARGET_MANIFEST),
            "graph_digest": source["graph_digest"],
            "policy_digest": source["policy_digest"],
            "case_count": len(source["cases"]),
            "claim_count": len(claims),
            "retrieval_frontier_count": sum(
                "candidate_frontier" in claim for claim in claims
            ),
            "unknown_is_pass": False,
        },
        "receipt_digest",
    )


def _canonical_claim_units() -> dict[str, list[str]]:
    return {
        section: [f"{section}:claim:{index:02d}" for index in range(1, count + 1)]
        for section, count in SECTION_COUNTS.items()
        if section not in {
            "unify_narrative",
            "ibm_narrative",
            "insurtech_narrative",
            "ey_narrative",
        }
    }


def _candidate(
    claim_unit_id: str,
    *,
    ordinal: int,
    selected_ordinal: int,
    metric: bool,
) -> dict[str, Any]:
    section_id = claim_unit_id.split(":", 1)[0]
    metric_text = "20% joint revenue growth" if metric else ""
    return {
        "candidate_id": f"candidate::{claim_unit_id}::{ordinal:02d}",
        "section_id": section_id,
        "claim_unit_id": claim_unit_id,
        "skill_id": f"skill::{claim_unit_id}::{ordinal:02d}",
        "skill_label": f"Skill {ordinal}",
        "fact_id": f"fact::{claim_unit_id}::{ordinal:02d}",
        "metric_outcome_id": f"metric::{claim_unit_id}" if metric else "",
        "metric_text": metric_text,
        "metric_value": "20" if metric else "",
        "metric_unit": "PERCENT" if metric else "",
        "normalized_metric_signature": "20 pct joint revenue growth" if metric else "",
        "root_id": f"root::{claim_unit_id}::{ordinal:02d}",
        "employer_lane": "unify",
        "source_family": "unify",
        "authority_pass": True,
        "proof_strength_raw": float(100 - ordinal),
        "target_alignment_score": 1.0,
        "claim_entailment_score": 1.0,
        "metric_binding_score": 1.0 if metric else 0.0,
        "path_confidence_raw": 1.0,
        "source_independence_score": 1.0,
        "selection_margin": 0.0,
        "selection_margin_available": False,
        "selection_margin_basis": "",
        "graph_path_ids": [
            f"root::{claim_unit_id}::{ordinal:02d}",
            f"path::skill::{claim_unit_id}::{ordinal:02d}",
            f"path::fact::{claim_unit_id}::{ordinal:02d}",
        ],
        "edge_ids": [f"edge::{claim_unit_id}::{ordinal:02d}"],
        "citation_refs": [f"citation::{claim_unit_id}::{ordinal:02d}"],
        "root_claim_text": f"Frozen root claim {ordinal} for {claim_unit_id}.",
    }


def _fake_bundle() -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    canonical = _canonical_claim_units()
    candidate_sets: dict[str, list[dict[str, Any]]] = {}
    assignments: list[dict[str, Any]] = []
    candidate_decisions: list[dict[str, Any]] = []
    first_retrieval = "competencies:claim:01"
    for section_id, claim_units in canonical.items():
        for index, claim_unit_id in enumerate(claim_units, 1):
            selected_ordinal = 12 if claim_unit_id == first_retrieval else 1
            metric = section_id == "executive_summary" and index == 1
            candidate_count = (
                8
                if claim_unit_id == "headline:claim:01"
                else 70 if claim_unit_id == "headline:claim:02" else 12
            )
            rows = [
                _candidate(
                    claim_unit_id,
                    ordinal=ordinal,
                    selected_ordinal=selected_ordinal,
                    metric=metric,
                )
                for ordinal in range(1, candidate_count + 1)
            ]
            candidate_sets[claim_unit_id] = rows
            selected = dict(rows[selected_ordinal - 1])
            selected["selection_margin"] = 0.25
            selected["selection_margin_available"] = True
            selected["selection_margin_basis"] = "proof_strength_raw"
            selected["counts_toward_global_uniqueness"] = True
            assignments.append(selected)
            for ordinal, candidate in enumerate(rows, 1):
                if ordinal > 64:
                    reason = "allocation_candidate_budget"
                elif ordinal == selected_ordinal:
                    reason = "selected_by_global_allocation"
                else:
                    reason = "global_constraint_or_objective_not_selected"
                candidate_decisions.append(
                    {
                        "candidate_id": candidate["candidate_id"],
                        "section_id": section_id,
                        "claim_unit_id": claim_unit_id,
                        "decision": "selected" if ordinal == selected_ordinal else "rejected",
                        "reason_codes": [reason],
                    }
                )

    for narrative, bullet in (
        ("unify_narrative", "unify_bullets"),
        ("ibm_narrative", "ibm_bullets"),
        ("insurtech_narrative", "insurtech_bullets"),
        ("ey_narrative", "ey_bullets"),
    ):
        for index, source_claim_unit_id in enumerate(canonical[bullet], 1):
            source = next(
                row for row in assignments if row["claim_unit_id"] == source_claim_unit_id
            )
            derived = dict(source)
            derived["section_id"] = narrative
            derived["claim_unit_id"] = f"{narrative}:derived:{index:02d}"
            derived["candidate_id"] = f"derived:{narrative}:{source['candidate_id']}"
            derived["derived_from_claim_unit_id"] = source_claim_unit_id
            derived["counts_toward_global_uniqueness"] = False
            assignments.append(derived)

    assert len(assignments) == 47
    plan = {
        "allocation_plan_digest": "a" * 64,
        "graph_digest": "b" * 64,
        "policy_digest": "c" * 64,
        "assignments": assignments,
        "candidate_decisions": candidate_decisions,
        "solver_metadata": {
            "max_candidates_per_slot": DEFAULT_MAX_CANDIDATES_PER_SLOT,
        },
    }
    return {"allocation_plan": plan, "section_plans": {"fake": {}}}, candidate_sets


def test_freezer_builds_six_packet_ready_cases_without_score_leakage(monkeypatch: Any) -> None:
    calls: list[dict[str, Any]] = []
    fake_bundle, candidate_sets = _fake_bundle()

    def fake_build(**kwargs: Any) -> dict[str, Any]:
        calls.append(kwargs)
        tagged_bundle = copy.deepcopy(fake_bundle)
        tagged_candidates = copy.deepcopy(candidate_sets)
        tag = f"case-{len(calls):02d}"
        # The production six-target freeze has 57 distinct immutable binding
        # groups.  Keep this synthetic allocator realistic by returning
        # target-dependent selected facts/paths instead of cloning one
        # 30-group allocation into every case.  Binding groups remain the
        # leakage boundary; this fixture simply supplies enough genuinely
        # distinct groups to exercise the frozen 20-per-split floor.
        for assignment in tagged_bundle["allocation_plan"]["assignments"]:
            if assignment["claim_unit_id"] not in {
                "competencies:claim:01",
                "competencies:claim:02",
                "headline:claim:01",
                "headline:claim:02",
            }:
                continue
            assignment["fact_id"] = f"{assignment['fact_id']}::{tag}"
            assignment["graph_path_ids"] = [
                *assignment["graph_path_ids"],
                f"path::target-binding::{tag}",
            ]
        for rows in tagged_candidates.values():
            for row in rows:
                if row["section_id"] in {"competencies", "headline"}:
                    row["root_claim_text"] = f"{tag}: {row['root_claim_text']}"
        tagged_bundle["section_plans"] = {"_candidate_sets": tagged_candidates}
        return tagged_bundle

    monkeypatch.setattr(source_bundle, "build_whole_resume_graph_allocation", fake_build)
    monkeypatch.setattr(source_bundle, "_default_slot_specs", lambda _plans: [])
    monkeypatch.setattr(
        source_bundle,
        "_candidate_sets_from_section_plans",
        lambda plans, _slots: plans["_candidate_sets"],
    )
    all_skills = {
        row["skill_id"]
        for rows in candidate_sets.values()
        for row in rows
    }
    canonical_authority_skill = candidate_sets["competencies:claim:01"][-1]["skill_id"]
    monkeypatch.setattr(
        source_bundle,
        "_load_skill_evidence",
        lambda _root: {
            skill_id: {
                "source_snippets": (
                    []
                    if skill_id == canonical_authority_skill
                    else [f"Independent archive evidence for {skill_id}."]
                ),
                "fact_id_links": [f"ledger-fact::{skill_id}"],
                "source_resume_files": ["frozen-source-resume.docx"],
            }
            for skill_id in all_skills
        },
    )
    monkeypatch.setattr(
        source_bundle,
        "_frozen_text",
        lambda **kwargs: f"TARGETING_ONLY_{str(kwargs['kind']).upper()}_MARKER",
    )

    frozen = freeze_allocation_source_bundle(
        repo_root=REPO,
        target_cases_manifest=TARGET_MANIFEST,
        source_commit_sha="d" * 40,
    )

    assert len(calls) == 6
    assert all(call["repo_root"] == REPO for call in calls)
    assert all(call["jd_text"] and call["briefing_text"] for call in calls)
    assert frozen["source_commit_sha"] == "d" * 40
    assert frozen["graph_digest"] == "b" * 64
    assert frozen["policy_digest"] == "c" * 64
    assert "baseline_resume_text" not in str(frozen)
    assert "hardened_resume_text" not in str(frozen)

    evidence_modes: Counter[str] = Counter()
    for case in frozen["cases"]:
        assert len(case["claims"]) == 47
        assert Counter(row["section_id"] for row in case["claims"]) == SECTION_COUNTS
        frontier_claims = [row for row in case["claims"] if "candidate_frontier" in row]
        assert len(frontier_claims) == 14
        assert Counter(row["section_id"] for row in frontier_claims) == {
            section: 2 for section in RANKED_SECTIONS
        }
        for claim in case["claims"]:
            assert unsafe_reviewer_keys(claim["proof_context"]) == []
            assert claim["proof_context"]["evidence_text"] != claim["visible_claim_text"]
            evidence_modes[claim["proof_context"]["evidence_mode"]] += 1
            if claim["proof_context"]["evidence_mode"] == "CANONICAL_FACT_AUTHORITY":
                assert claim["proof_context"]["canonical_truth_input_assumption"] is True
                assert claim["proof_context"]["independent_corroboration"] is False
                assert "not independent corroboration" in claim["proof_context"][
                    "evidence_text"
                ]
            else:
                assert claim["proof_context"]["evidence_mode"] == (
                    "CANONICAL_SOURCE_SNIPPET"
                )
                assert claim["proof_context"]["canonical_truth_input_assumption"] is False
            assert "TARGETING_ONLY_JD_MARKER" not in claim["proof_context"][
                "evidence_text"
            ]
            assert "TARGETING_ONLY_BRIEF_MARKER" not in claim["proof_context"][
                "evidence_text"
            ]
            assert claim["binding"]["root_id"]
            assert claim["binding"]["fact_id"]
            assert claim["binding"]["graph_path_ids"]
            assert "proof_strength_raw" in claim["system_fields"]
            assert claim["system_fields"]["proof_score_raw"] == claim["system_fields"][
                "proof_strength_raw"
            ]
            assert "system_prediction" in claim["system_fields"]
            assert "selection_margin" in claim["system_fields"]
            for candidate in claim.get("candidate_frontier", []):
                assert unsafe_reviewer_keys(candidate["proof_context"]) == []
                assert candidate["proof_context"]["evidence_text"] != candidate[
                    "candidate_text"
                ]
                assert candidate["system_fields"]["binding"]["fact_id"]
                assert len(claim["candidate_frontier"]) <= 64
                assert sum(
                    bool(row["selected"]) for row in claim["candidate_frontier"]
                ) == 1
            if "candidate_frontier" in claim:
                metadata = claim["candidate_frontier_metadata"]
                assert metadata["allocator_candidate_budget"] == (
                    DEFAULT_MAX_CANDIDATES_PER_SLOT
                )
                assert metadata["candidate_universe_size"] == min(
                    metadata["raw_eligible_candidate_count"],
                    metadata["allocator_candidate_budget"],
                )
                assert metadata["allocator_budget_truncated"] is (
                    metadata["raw_eligible_candidate_count"]
                    > metadata["allocator_candidate_budget"]
                )
                assert metadata["frontier_k"] == 10
                assert metadata["judged_top_count"] == min(
                    10, metadata["candidate_universe_size"]
                )
                assert metadata["judged_candidate_count"] == metadata[
                    "candidate_universe_size"
                ]
                assert metadata["candidate_judging_scope"] == "FULL_FINITE_UNIVERSE"
                assert metadata["frontier_exhausted"] is (
                    metadata["candidate_universe_size"] <= 10
                )
                assert len(claim["candidate_frontier"]) == metadata[
                    "candidate_universe_size"
                ]
                assert [
                    row["rank"]
                    for row in claim["candidate_frontier"]
                ] == list(range(1, metadata["candidate_universe_size"] + 1))

        displaced = next(
            row
            for row in frontier_claims
            if row["claim_unit_id"] == "competencies:claim:01"
        )
        assert [row["rank"] for row in displaced["candidate_frontier"]] == list(
            range(1, 13)
        )
        assert displaced["candidate_frontier"][-1]["selected"] is True
        assert displaced["candidate_frontier"][-1]["system_fields"][
            "selection_margin"
        ] == 0.25
        assert displaced["candidate_frontier_metadata"] == {
            "candidate_universe_size": 12,
            "raw_eligible_candidate_count": 12,
            "allocator_candidate_budget": 64,
            "allocator_budget_truncated": False,
            "frontier_k": 10,
            "frontier_exhausted": False,
            "judged_top_count": 10,
            "judged_candidate_count": 12,
            "candidate_judging_scope": "FULL_FINITE_UNIVERSE",
            "selected_audit_extra_included": True,
            "selected_audit_extra_rank": 12,
        }
        exhausted = next(
            row
            for row in frontier_claims
            if row["claim_unit_id"] == "headline:claim:01"
        )
        assert [row["rank"] for row in exhausted["candidate_frontier"]] == list(
            range(1, 9)
        )
        assert exhausted["candidate_frontier_metadata"] == {
            "candidate_universe_size": 8,
            "raw_eligible_candidate_count": 8,
            "allocator_candidate_budget": 64,
            "allocator_budget_truncated": False,
            "frontier_k": 10,
            "frontier_exhausted": True,
            "judged_top_count": 8,
            "judged_candidate_count": 8,
            "candidate_judging_scope": "FULL_FINITE_UNIVERSE",
            "selected_audit_extra_included": False,
            "selected_audit_extra_rank": None,
        }
        budgeted = next(
            row
            for row in frontier_claims
            if row["claim_unit_id"] == "headline:claim:02"
        )
        assert budgeted["candidate_frontier_metadata"]["candidate_universe_size"] == 64
        assert budgeted["candidate_frontier_metadata"][
            "raw_eligible_candidate_count"
        ] == 70
        assert budgeted["candidate_frontier_metadata"][
            "allocator_budget_truncated"
        ] is True
        assert len(budgeted["candidate_frontier"]) == 64
        metric_claim = next(
            row
            for row in case["claims"]
            if row["claim_unit_id"] == "executive_summary:claim:01"
        )
        assert metric_claim["visible_claim_text"].endswith(
            "Exact metric: 20% joint revenue growth"
        )
        assert metric_claim["binding"]["metric_outcome_id"]

    assert evidence_modes == {
        "CANONICAL_SOURCE_SNIPPET": 276,
        "CANONICAL_FACT_AUTHORITY": 6,
    }

    freeze_receipt = _test_freeze_receipt(frozen)
    readiness = assess_source_bundle_readiness(
        source_bundle=frozen,
        source_freeze_receipt=freeze_receipt,
        trusted_source_freeze_receipt_digest=freeze_receipt["receipt_digest"],
        allow_test_only_provenance=True,
        blinding_nonce="ab" * 32,
        repo_root=REPO,
        require_w9=False,
    )
    assert readiness["status"] == "PASS_TEST_ONLY", readiness["errors"]
    assert readiness["prelabel_validation"]["status"] == "PASS_TEST_ONLY"
    assert readiness["prelabel_validation"]["checks"][
        "proof_identity_retrieval_overlap_count"
    ] > 0
    assert readiness["prelabel_validation"]["checks"][
        "proof_identity_split_disjoint"
    ] is True
    assert readiness["prelabel_validation"]["checks"][
        "proof_split_strata_complete"
    ] is True
    assert readiness["prelabel_validation"]["checks"][
        "retrieval_split_strata_complete"
    ] is True
    assert readiness["observed_counts"] == {
        "claim_items": 282,
        "retrieval_queries": 84,
        "w9_pairs": 0,
    }


def test_freezer_is_order_deterministic_and_requires_explicit_commit(monkeypatch: Any) -> None:
    fake_bundle, candidate_sets = _fake_bundle()
    monkeypatch.setattr(
        source_bundle, "build_whole_resume_graph_allocation", lambda **_kwargs: fake_bundle
    )
    monkeypatch.setattr(source_bundle, "_default_slot_specs", lambda _plans: [])
    monkeypatch.setattr(
        source_bundle,
        "_candidate_sets_from_section_plans",
        lambda _plans, _slots: candidate_sets,
    )
    monkeypatch.setattr(
        source_bundle,
        "_load_skill_evidence",
        lambda _root: {
            row["skill_id"]: {
                "source_snippets": [f"Independent archive evidence for {row['skill_id']}."],
                "fact_id_links": [row["fact_id"]],
                "source_resume_files": ["frozen-source-resume.docx"],
            }
            for rows in candidate_sets.values()
            for row in rows
        },
    )
    manifest = yaml.safe_load(TARGET_MANIFEST.read_text(encoding="utf-8"))
    reversed_manifest = {**manifest, "cases": list(reversed(manifest["cases"]))}
    forward = freeze_allocation_source_bundle(
        repo_root=REPO,
        target_cases_manifest=manifest,
        source_commit_sha="e" * 40,
    )
    reverse = freeze_allocation_source_bundle(
        repo_root=REPO,
        target_cases_manifest=reversed_manifest,
        source_commit_sha="e" * 40,
    )
    assert forward == reverse

    with pytest.raises(SourceBundleFreezeError, match="40-character"):
        freeze_allocation_source_bundle(
            repo_root=REPO,
            target_cases_manifest=manifest,
            source_commit_sha="HEAD",
        )


def test_freezer_fails_closed_without_canonical_skill_evidence(monkeypatch: Any) -> None:
    fake_bundle, candidate_sets = _fake_bundle()
    monkeypatch.setattr(
        source_bundle, "build_whole_resume_graph_allocation", lambda **_kwargs: fake_bundle
    )
    monkeypatch.setattr(source_bundle, "_default_slot_specs", lambda _plans: [])
    monkeypatch.setattr(
        source_bundle,
        "_candidate_sets_from_section_plans",
        lambda _plans, _slots: candidate_sets,
    )
    monkeypatch.setattr(source_bundle, "_load_skill_evidence", lambda _root: {})
    with pytest.raises(SourceBundleFreezeError, match="no canonical arsenal evidence row"):
        freeze_allocation_source_bundle(
            repo_root=REPO,
            target_cases_manifest=TARGET_MANIFEST,
            source_commit_sha="f" * 40,
        )


def test_freezer_rejects_allocator_candidate_budget_drift() -> None:
    fake_bundle, candidate_sets = _fake_bundle()
    plan = copy.deepcopy(fake_bundle["allocation_plan"])
    plan["solver_metadata"]["max_candidates_per_slot"] = 63
    assert DEFAULT_MAX_CANDIDATES_PER_SLOT == 64
    with pytest.raises(SourceBundleFreezeError, match="candidate budget disagrees"):
        source_bundle._allocator_bounded_candidate_sets(
            raw_candidate_sets=candidate_sets,
            allocation_plan=plan,
        )
