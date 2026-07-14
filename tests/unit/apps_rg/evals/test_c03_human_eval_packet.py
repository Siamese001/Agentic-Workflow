from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import Any

import pytest
import yaml

from apps_rg.evals.c03_human_eval import _io as io_helpers
from apps_rg.evals.c03_human_eval._io import (
    ensure_private_directory,
    file_digest,
    read_json,
    read_jsonl,
    record_with_digest,
    stable_digest,
    write_json,
    write_jsonl,
    write_private_text,
)
from apps_rg.evals.c03_human_eval.__main__ import main
from apps_rg.evals.c03_human_eval.export import (
    export_adjudicated_evaluation as _export_adjudicated_evaluation,
)
from apps_rg.evals.c03_human_eval.packet import (
    DEFAULT_TARGET_MANIFEST,
    EXPECTED_CLAIM_ITEMS,
    EXPECTED_RETRIEVAL_QUERIES,
    EXPECTED_W9_PAIRS,
    PacketBuildError,
    _target_manifest,
    assess_source_bundle_readiness as _assess_source_bundle_readiness,
    build_packet as _build_packet,
)
from apps_rg.evals.c03_human_eval.source_bundle import build_source_freeze_receipt
from apps_rg.evals.c03_human_eval.validation import (
    build_prelabel_packet_receipt,
    human_review_authority_receipt_file_sha256,
    validate_completed_packet as _validate_completed_packet,
    validate_prelabel_packet as _validate_prelabel_packet,
)
from apps_rg.evals.resume_graph_evaluation import (
    PASS,
    build_sanitized_ci_receipt,
    evaluate_file,
)
from ops_scripts.ci.check_apps_rg_resume_graph_w6 import validate_artifact

REPO = Path(__file__).resolve().parents[4]
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
W9_DIMENSIONS = {
    "target_relevance": 4,
    "claim_naturalness": 4,
    "executive_readability": 4,
    "ats_keyword_coverage": 4,
    "authenticity_factuality": 4,
    "concision": 4,
    "hiring_manager_usefulness": 4,
}
TEST_BLINDING_NONCE = "ab" * 32


def _source_bundle(*, include_w9: bool = True) -> dict[str, Any]:
    target = yaml.safe_load(DEFAULT_TARGET_MANIFEST.read_text(encoding="utf-8"))
    cases: list[dict[str, Any]] = []
    for target_case in target["cases"]:
        case_id = target_case["case_id"]
        claims: list[dict[str, Any]] = []
        for section_id, count in SECTION_COUNTS.items():
            for index in range(1, count + 1):
                claim_unit_id = f"{section_id}:claim:{index:02d}"
                candidates = [
                    {
                        "candidate_id": f"{case_id}:{claim_unit_id}:candidate:{candidate_index}",
                        "candidate_text": f"Candidate {candidate_index} for {section_id}",
                        "proof_context": {
                            "evidence_text": f"Evidence {candidate_index}",
                            "path_text": f"skill to fact path {candidate_index}",
                            "metric_text": "not applicable",
                        },
                        "rank": candidate_index,
                        "selected": candidate_index == 1,
                        "system_fields": {
                            "retrieval_signal": 1.0 / candidate_index,
                            "binding": {
                                "metric_outcome_id": "",
                                "normalized_metric_signature": "",
                                "metric_text": "",
                                "metric_value": "",
                                "metric_unit": "",
                            },
                        },
                    }
                    for candidate_index in range(1, 11)
                ]
                claims.append(
                    {
                        "section_id": section_id,
                        "claim_unit_id": claim_unit_id,
                        "visible_claim_text": f"Claim {index} for {case_id} {section_id}",
                        "proof_context": {
                            "evidence_text": f"Source evidence for {case_id} {section_id} {index}",
                            "skill_text": f"Skill {index}",
                            "fact_text": f"Fact {index}",
                            "metric_text": "not applicable",
                            "path_text": "role to skill to fact",
                        },
                        "candidate_id": candidates[0]["candidate_id"],
                        "binding": {
                            "skill_id": f"skill:{case_id}:{section_id}:{index}",
                            "fact_id": f"fact:{case_id}:{section_id}:{index}",
                            "metric_outcome_id": "",
                            "normalized_metric_signature": "",
                            "metric_text": "",
                            "metric_value": "",
                            "metric_unit": "",
                            "graph_path_ids": [
                                f"path:{case_id}:{section_id}:{index}",
                                f"fact:{case_id}:{section_id}:{index}",
                            ]
                        },
                        "system_fields": {
                            "proof_strength_raw": 0.92,
                            "system_prediction": True,
                            "selection_margin": 0.15,
                        },
                        "candidate_frontier": candidates,
                        "candidate_frontier_metadata": {
                            "raw_eligible_candidate_count": 10,
                            "allocator_candidate_budget": 64,
                            "allocator_budget_truncated": False,
                            "candidate_universe_size": 10,
                            "frontier_k": 10,
                            "frontier_exhausted": True,
                            "judged_top_count": 10,
                            "judged_candidate_count": 10,
                            "candidate_judging_scope": "FULL_FINITE_UNIVERSE",
                            "selected_audit_extra_included": False,
                            "selected_audit_extra_rank": None,
                        },
                    }
                )
        source_case: dict[str, Any] = {
            "case_id": case_id,
            "run_id": f"run::{case_id}",
            "allocation_plan_digest": (case_id.encode("utf-8").hex() + "0" * 64)[:64],
            "claims": claims,
        }
        if include_w9:
            source_case["baseline_resume_text"] = f"Resume version one for {case_id}."
            source_case["hardened_resume_text"] = f"Resume version two for {case_id}."
        cases.append(source_case)
    return {
        "schema_version": "apps_rg.c03_human_eval.source_bundle.v1",
        "source_commit_sha": "1" * 40,
        "graph_digest": "2" * 64,
        "policy_digest": "3" * 64,
        "cases": cases,
    }


def _write_source(path: Path, source: dict[str, Any]) -> Path:
    path.write_text(json.dumps(source, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def _test_freeze_receipt(
    source: dict[str, Any],
    *,
    target_manifest_path: Path = DEFAULT_TARGET_MANIFEST,
) -> dict[str, Any]:
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
            "target_manifest_digest": file_digest(target_manifest_path),
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


def build_packet(*, source_bundle: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    receipt = _test_freeze_receipt(source_bundle)
    return _build_packet(
        source_bundle=source_bundle,
        source_freeze_receipt=receipt,
        trusted_source_freeze_receipt_digest=receipt["receipt_digest"],
        allow_test_only_provenance=True,
        **kwargs,
    )


def assess_source_bundle_readiness(
    *, source_bundle: dict[str, Any], **kwargs: Any
) -> dict[str, Any]:
    receipt = _test_freeze_receipt(
        source_bundle,
        target_manifest_path=kwargs.get(
            "target_manifest_path", DEFAULT_TARGET_MANIFEST
        ),
    )
    return _assess_source_bundle_readiness(
        source_bundle=source_bundle,
        source_freeze_receipt=receipt,
        trusted_source_freeze_receipt_digest=receipt["receipt_digest"],
        allow_test_only_provenance=True,
        **kwargs,
    )


def _packet_receipt_digest(packet: Path) -> str:
    return str(read_json(packet / "packet_manifest.json")["source_freeze_receipt_digest"])


def _packet_manifest_sha256(packet: Path) -> str:
    return file_digest(packet / "packet_manifest.json")


def _test_human_review_authority_receipt(packet: Path) -> dict[str, Any]:
    manifest = read_json(packet / "packet_manifest.json")
    participants: list[dict[str, Any]] = []
    cohorts = ["proof", "retrieval"]
    if manifest["w9_ready"]:
        cohorts.append("w9")
    for cohort in cohorts:
        for reviewer_number in (1, 2):
            identity_ref = f"human-reviewer://{cohort}-{reviewer_number}"
            participants.append(
                {
                    "cohort": cohort,
                    "identity_ref": identity_ref,
                    "identity_hash": hashlib.sha256(
                        identity_ref.encode("utf-8")
                    ).hexdigest(),
                    "roles": ["primary"],
                    "qualification_ref": (
                        "resume-coach://executive-resume-review"
                        if cohort == "w9"
                        else "qualification://semantic-proof-review"
                    ),
                }
            )
    return record_with_digest(
        {
            "schema_version": (
                "apps_rg.c03_human_eval.human_review_authority_receipt.v1"
            ),
            "authority_mode": "TEST_ONLY_UNTRUSTED_FIXTURE",
            "official_authority_eligible": False,
            "packet_id": manifest["packet_id"],
            "packet_manifest_digest": manifest["manifest_digest"],
            "prelabel_packet_manifest_sha256": _packet_manifest_sha256(packet),
            "source_freeze_receipt_digest": manifest[
                "source_freeze_receipt_digest"
            ],
            "cohort_manifest_digests": {
                cohort: details["manifest_digest"]
                for cohort, details in manifest["reviewer_distributions"].items()
            },
            "issuer_ref": "authority-issuer://test-evaluation-owner",
            "approval_ref": "approval://test-human-roster",
            "issued_at": "2026-07-13T00:00:00Z",
            "authorized_participants": participants,
            "unknown_is_pass": False,
        },
        "receipt_digest",
    )


def validate_prelabel_packet(
    packet: Path, *, require_w9: bool = False
) -> dict[str, Any]:
    return _validate_prelabel_packet(
        packet,
        require_w9=require_w9,
        trusted_source_freeze_receipt_digest=_packet_receipt_digest(packet),
        allow_test_only_provenance=True,
    )


def validate_completed_packet(
    packet: Path, labels: Path, *, require_w9: bool = False
) -> dict[str, Any]:
    authority = _test_human_review_authority_receipt(packet)
    return _validate_completed_packet(
        packet,
        labels,
        require_w9=require_w9,
        trusted_source_freeze_receipt_digest=_packet_receipt_digest(packet),
        trusted_prelabel_packet_manifest_sha256=_packet_manifest_sha256(packet),
        human_review_authority_receipt=authority,
        trusted_human_review_authority_receipt_sha256=(
            human_review_authority_receipt_file_sha256(authority)
        ),
        allow_test_only_provenance=True,
    )


def export_adjudicated_evaluation(
    *, packet_dir: Path, labels_dir: Path, **kwargs: Any
) -> dict[str, Any]:
    authority = _test_human_review_authority_receipt(packet_dir)
    return _export_adjudicated_evaluation(
        packet_dir=packet_dir,
        labels_dir=labels_dir,
        trusted_source_freeze_receipt_digest=_packet_receipt_digest(packet_dir),
        trusted_prelabel_packet_manifest_sha256=_packet_manifest_sha256(packet_dir),
        human_review_authority_receipt=authority,
        trusted_human_review_authority_receipt_sha256=(
            human_review_authority_receipt_file_sha256(authority)
        ),
        allow_test_only_provenance=True,
        **kwargs,
    )


def _claim_labels(
    *, metric_applicable: bool = False, proof_valid: bool = True
) -> dict[str, Any]:
    return {
        "authority_eligible": "PASS",
        "claim_entailment_grade": 3 if proof_valid else 1,
        "path_accuracy": True,
        "metric_binding": "EXACT" if metric_applicable else "NOT_APPLICABLE",
        "target_relevance_grade": 3,
        "overall_proof_valid": proof_valid,
    }


def _retrieval_labels(
    item: dict[str, Any],
    *,
    sealed_candidates: dict[str, dict[str, Any]] | None = None,
    respect_metric_applicability: bool = False,
) -> dict[str, Any]:
    return {
        "candidates": [
            {
                "candidate_blind_id": candidate["candidate_blind_id"],
                "relevance_grade": (
                    3
                    if (sealed_candidates or {})
                    .get(str(candidate["candidate_blind_id"]), {})
                    .get("rank")
                    == 1
                    else 1
                ),
                "path_valid": True,
                "metric_binding": (
                    "EXACT"
                    if (sealed_candidates or {})
                    .get(str(candidate["candidate_blind_id"]), {})
                    .get("metric_applicable")
                    is True
                    and respect_metric_applicability
                    else "NOT_APPLICABLE"
                ),
            }
            for candidate in item["candidates"]
        ]
    }


def _w9_labels() -> dict[str, Any]:
    return {
        "resume_a": dict(W9_DIMENSIONS),
        "resume_b": dict(W9_DIMENSIONS),
        "preference": "TIE",
    }


def _completed_labels(
    packet: Path,
    labels: Path,
    *,
    negative_claim_item_ids: set[str] | None = None,
    respect_metric_applicability: bool = False,
) -> Path:
    manifest = read_json(packet / "packet_manifest.json")
    rubric_digests = manifest["rubric_digests"]
    claim_metric_applicability = {
        str(row["item_id"]): bool(row["metric_applicable"])
        for row in read_jsonl(packet / "sealed_internal/claim_mapping.jsonl")
    }
    retrieval_sealed_candidates = {
        str(row["query_id"]): {
            str(candidate["candidate_blind_id"]): dict(candidate)
            for candidate in row["candidates"]
        }
        for row in read_jsonl(packet / "sealed_internal/retrieval_mapping.jsonl")
    }
    item_groups = (
        (
            "claim",
            "item_id",
            packet / "reviewer_proof/claim_items.jsonl",
            "claim_reviews.jsonl",
        ),
        (
            "retrieval",
            "query_id",
            packet / "reviewer_retrieval/retrieval_queries.jsonl",
            "retrieval_reviews.jsonl",
        ),
        (
            "w9_pair",
            "pair_id",
            packet / "reviewer_w9/w9_blind_pairs.jsonl",
            "w9_reviews.jsonl",
        ),
    )
    adjudications: list[dict[str, Any]] = []
    labels.mkdir(parents=True, exist_ok=True, mode=0o700)
    for item_type, id_key, item_path, review_name in item_groups:
        if not item_path.is_file():
            continue
        reviews: list[dict[str, Any]] = []
        for item in read_jsonl(item_path):
            item_id = item[id_key]
            if item_type == "claim":
                final_labels = _claim_labels(
                    metric_applicable=(
                        claim_metric_applicability[item_id]
                        and respect_metric_applicability
                    ),
                    proof_valid=item_id not in (negative_claim_item_ids or set()),
                )
            elif item_type == "retrieval":
                final_labels = _retrieval_labels(
                    item,
                    sealed_candidates=retrieval_sealed_candidates[item_id],
                    respect_metric_applicability=respect_metric_applicability,
                )
            else:
                final_labels = _w9_labels()
            item_reviews: list[dict[str, Any]] = []
            reviewer_cohort = {
                "claim": "proof",
                "retrieval": "retrieval",
                "w9_pair": "w9",
            }[item_type]
            for reviewer_number in (1, 2):
                reviewer_ref = (
                    f"human-reviewer://{reviewer_cohort}-{reviewer_number}"
                )
                reviewer_hash = hashlib.sha256(
                    reviewer_ref.encode("utf-8")
                ).hexdigest()
                qualification_ref = (
                    "resume-coach://executive-resume-review"
                    if item_type == "w9_pair"
                    else "qualification://semantic-proof-review"
                )
                review = record_with_digest(
                    {
                        "schema_version": "apps_rg.c03_human_eval.human_review.v1",
                        "review_id": f"review::{item_id}::{reviewer_number}",
                        "item_type": item_type,
                        "item_id": item_id,
                        "reviewer_type": "human",
                        "reviewer_id_hash": reviewer_hash,
                        "reviewer_identity_ref": reviewer_ref,
                        "qualification_ref": qualification_ref,
                        "human_attestation": True,
                        "independent_review": True,
                        "label_batch_id": f"batch-{reviewer_number}",
                        "labeled_at": "2026-07-14T00:00:00Z",
                        "blinded_payload_digest": item["content_digest"],
                        "rubric_digest": rubric_digests[item_type],
                        "labels": final_labels,
                        "notes": "",
                    },
                    "record_digest",
                )
                item_reviews.append(review)
                reviews.append(review)
            adjudications.append(
                record_with_digest(
                    {
                        "schema_version": "apps_rg.c03_human_eval.adjudication.v1",
                        "adjudication_id": f"adjudication::{item_id}",
                        "item_type": item_type,
                        "item_id": item_id,
                        "review_refs": [row["review_id"] for row in item_reviews],
                        "review_digests": [row["record_digest"] for row in item_reviews],
                        "status": "CONSENSUS_ACCEPTED",
                        "adjudicator_type": "deterministic_consensus",
                        "final_labels": final_labels,
                        "adjudicated_at": "2026-07-14T00:01:00Z",
                    },
                    "record_digest",
                )
            )
        write_jsonl(labels / review_name, reviews)
    write_jsonl(labels / "adjudications.jsonl", adjudications)
    return labels


def test_readiness_build_and_prelabel_validation_are_deterministic(tmp_path: Path) -> None:
    source = _source_bundle()
    readiness = assess_source_bundle_readiness(
        source_bundle=source,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    assert readiness["status"] == "PASS_TEST_ONLY"
    assert readiness["packet_build_ready"] is True
    assert readiness["prelabel_validation"]["status"] == "PASS_TEST_ONLY"
    assert readiness["observed_counts"] == {
        "claim_items": EXPECTED_CLAIM_ITEMS,
        "retrieval_queries": EXPECTED_RETRIEVAL_QUERIES,
        "w9_pairs": EXPECTED_W9_PAIRS,
    }

    first = tmp_path / "packet-one"
    second = tmp_path / "packet-two"
    manifest_one = build_packet(
        source_bundle=source,
        out_dir=first,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    manifest_two = build_packet(
        source_bundle=source,
        out_dir=second,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    assert manifest_one == manifest_two
    assert file_digest(first / "reviewer_proof/claim_items.jsonl") == file_digest(
        second / "reviewer_proof/claim_items.jsonl"
    )
    validation = validate_prelabel_packet(first, require_w9=True)
    assert validation["status"] == "PASS_TEST_ONLY", validation["errors"]
    assert validation["checks"]["claim_items"] == 282
    assert validation["checks"]["retrieval_queries"] == 84
    assert validation["checks"]["w9_pairs"] == 6
    assert validation["checks"]["proof_split_deterministic"] is True
    assert validation["checks"]["proof_identity_split_disjoint"] is True
    assert validation["checks"]["proof_split_strata_complete"] is True
    assert validation["checks"]["retrieval_split_strata_complete"] is True
    reviewer_pair = read_jsonl(first / "reviewer_w9/w9_blind_pairs.jsonl")[0]
    assert "baseline" not in reviewer_pair
    assert "hardened" not in reviewer_pair
    sealed_pair = read_jsonl(first / "sealed_internal/w9_variant_mapping.jsonl")[0]
    assert {sealed_pair["variant_a"], sealed_pair["variant_b"]} == {"baseline", "hardened"}
    reviewer_manifest = read_json(
        first / "reviewer_proof/reviewer_manifest.v1.json"
    )
    reviewer_paths = {row["path"] for row in reviewer_manifest["files"]}
    assert "reviewer_instructions.v1.md" in reviewer_paths
    assert "proof_label_rubric.v1.yaml" in reviewer_paths
    assert "retrieval_label_rubric.v1.yaml" not in reviewer_paths
    assert "w9_resume_coach_rubric.v1.yaml" not in reviewer_paths
    assert "human_review.v1.schema.json" in reviewer_paths
    assert "adjudication.v1.schema.json" in reviewer_paths
    assert "seal_records.py" in reviewer_paths
    assert not any("sealed" in path for path in reviewer_paths)
    assert (first / "reviewer_proof/SHA256SUMS").is_file()
    assert (first / "reviewer_retrieval/SHA256SUMS").is_file()
    assert (first / "reviewer_w9/SHA256SUMS").is_file()
    assert set(manifest_one["reviewer_distributions"]) == {
        "proof",
        "retrieval",
        "w9",
    }
    for cohort, expected_data_file in {
        "proof": "claim_items.jsonl",
        "retrieval": "retrieval_queries.jsonl",
        "w9": "w9_blind_pairs.jsonl",
    }.items():
        cohort_root = first / f"reviewer_{cohort}"
        cohort_manifest = read_json(cohort_root / "reviewer_manifest.v1.json")
        cohort_paths = {row["path"] for row in cohort_manifest["files"]}
        assert expected_data_file in cohort_paths
        assert not any("/" in path or path.startswith("..") for path in cohort_paths)
        assert cohort_manifest["other_reviewer_cohort_paths_included"] is False
        assert cohort_manifest["cross_cohort_distribution_forbidden"] is True
    proof_item = read_jsonl(first / "reviewer_proof/claim_items.jsonl")[0]
    retrieval_item = read_jsonl(
        first / "reviewer_retrieval/retrieval_queries.jsonl"
    )[0]
    assert proof_item["item_id"].startswith("proof-item-")
    assert retrieval_item["query_id"].startswith("retrieval-item-")
    assert not {"case_id", "claim_unit_id"} & set(proof_item)
    assert not {"case_id", "claim_unit_id"} & set(retrieval_item)
    assert "case_id" not in reviewer_pair
    assert retrieval_item["retrieval_target"] not in {
        candidate["candidate_text"] for candidate in retrieval_item["candidates"]
    }
    commitment = manifest_one["blinding_nonce_commitment"]
    split_commitment = manifest_one["retrieval_split_assignment_commitment"]
    for cohort in ("proof", "retrieval", "w9"):
        for path in (first / f"reviewer_{cohort}").iterdir():
            if path.is_file():
                content = path.read_text(encoding="utf-8")
                assert TEST_BLINDING_NONCE not in content
                assert commitment not in content
                assert split_commitment not in content
                assert "retrieval_split" not in content
                assert "proof_split_policy_salt" not in content


def test_non_w9_packet_omits_w9_reviewer_rubric(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    manifest = build_packet(
        # W6 scope is selected explicitly. Even dormant comparison inputs in
        # a test source must not cause W9 assets to enter a W6 packet.
        source_bundle=_source_bundle(include_w9=True),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=False,
    )
    assert manifest["w9_ready"] is False
    assert "reviewer_w9/w9_resume_coach_rubric.v1.yaml" not in manifest["reviewer_files"]
    assert "w9_pair" not in manifest["rubric_digests"]
    assert "sealed_internal/w9_variant_mapping.jsonl" not in manifest[
        "sealed_internal_files"
    ]
    assert all("w9" not in row["path"].lower() for row in manifest["files"])
    assert not (packet / "reviewer_w9").exists()
    assert not (packet / "sealed_internal/w9_variant_mapping.jsonl").exists()
    assert validate_prelabel_packet(packet)["status"] == "PASS_TEST_ONLY"


def test_reviewer_digest_tool_seals_and_validates_without_sealed_inputs(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(include_w9=False),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=False,
    )
    draft = tmp_path / "draft.jsonl"
    sealed = tmp_path / "claim_reviews.jsonl"
    draft.write_text(json.dumps({"review_id": "human-review-1"}) + "\n", encoding="utf-8")
    tool = packet / "reviewer_proof/seal_records.py"
    seal = subprocess.run(
        [sys.executable, str(tool), "seal", str(draft), "--out", str(sealed)],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert seal.returncode == 0, seal.stdout + seal.stderr
    rows = read_jsonl(sealed)
    assert len(rows) == 1
    assert rows[0]["record_digest"]
    assert stat.S_IMODE(sealed.stat().st_mode) == 0o600
    validate = subprocess.run(
        [sys.executable, str(tool), "validate", str(sealed)],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert validate.returncode == 0, validate.stdout + validate.stderr


def test_public_target_and_reviewer_files_cannot_reveal_split_assignments(
    tmp_path: Path,
) -> None:
    target_text = DEFAULT_TARGET_MANIFEST.read_text(encoding="utf-8")
    target = yaml.safe_load(target_text)
    assert "retrieval_split" not in target_text
    assert all("retrieval_split" not in case for case in target["cases"])

    packet = tmp_path / "packet"
    manifest = build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    assert manifest["retrieval_split_policy_id"] == (
        "secret-hmac-balanced-by-target-profile-v1"
    )
    for cohort in ("proof", "retrieval", "w9"):
        for path in (packet / f"reviewer_{cohort}").iterdir():
            if path.is_file():
                content = path.read_text(encoding="utf-8")
                assert "retrieval_split" not in content
                assert "proof_split" not in content


def test_sensitive_artifacts_are_owner_only_under_umask_022(tmp_path: Path) -> None:
    previous_umask = os.umask(0o022)
    try:
        packet = tmp_path / "packet"
        build_packet(
            source_bundle=_source_bundle(),
            out_dir=packet,
            blinding_nonce=TEST_BLINDING_NONCE,
            repo_root=REPO,
            require_w9=True,
        )
        controller = tmp_path / "controller"
        ensure_private_directory(controller)
        source_path = controller / "source_bundle.json"
        receipt_path = controller / "freeze_receipt.json"
        write_json(source_path, _source_bundle())
        write_json(receipt_path, _test_freeze_receipt(_source_bundle()))
    finally:
        os.umask(previous_umask)

    for directory in [packet, *(path for path in packet.rglob("*") if path.is_dir())]:
        assert not directory.is_symlink()
        assert stat.S_IMODE(directory.stat().st_mode) == 0o700
    for file_path in (path for path in packet.rglob("*") if path.is_file()):
        assert not file_path.is_symlink()
        assert stat.S_IMODE(file_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(controller.stat().st_mode) == 0o700
    assert stat.S_IMODE(source_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(receipt_path.stat().st_mode) == 0o600


def test_validation_rejects_packet_root_symlink_and_insecure_modes(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    alias = tmp_path / "packet-alias"
    alias.symlink_to(packet, target_is_directory=True)
    alias_result = validate_prelabel_packet(alias, require_w9=True)
    assert alias_result["status"] == "FAIL"
    assert any("symlink alias" in error for error in alias_result["errors"])

    packet_manifest = packet / "packet_manifest.json"
    packet_manifest.chmod(0o644)
    mode_result = validate_prelabel_packet(packet, require_w9=True)
    assert mode_result["status"] == "FAIL"
    assert any("owner-only (0600)" in error for error in mode_result["errors"])


def test_completed_validation_rejects_labels_symlink_and_insecure_modes(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    labels.chmod(0o755)
    insecure = validate_completed_packet(packet, labels, require_w9=True)
    assert insecure["status"] == "FAIL"
    assert any("owner-only (0700)" in error for error in insecure["errors"])
    labels.chmod(0o700)

    alias = tmp_path / "labels-alias"
    alias.symlink_to(labels, target_is_directory=True)
    aliased = validate_completed_packet(packet, alias, require_w9=True)
    assert aliased["status"] == "FAIL"
    assert any("symlink alias" in error for error in aliased["errors"])


def test_private_path_check_rejects_wrong_owner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controlled = tmp_path / "controlled"
    ensure_private_directory(controlled)
    monkeypatch.setattr(io_helpers.os, "getuid", lambda: os.stat(controlled).st_uid + 1)
    assert io_helpers.private_path_error(controlled, directory=True) == (
        "must be owned by the current user"
    )


def test_retrieval_packet_conserves_full_universe_and_selected_rank(tmp_path: Path) -> None:
    source = _source_bundle()
    frontier = source["cases"][0]["claims"][0]["candidate_frontier"]
    frontier[0]["selected"] = False
    for rank in range(11, 18):
        frontier.append(
            {
                "candidate_id": (
                    "selected-outside-top-ten"
                    if rank == 17
                    else f"finite-universe-candidate-{rank}"
                ),
                "candidate_text": f"Finite-universe candidate {rank}",
                "proof_context": {
                    "evidence_text": f"Independent evidence for candidate {rank}",
                    "path_text": f"skill to fact path {rank}",
                    "metric_text": "not applicable",
                },
                "rank": rank,
                "selected": rank == 17,
                "system_fields": {
                    "retrieval_signal": 1.0 / rank,
                    "binding": {
                        "metric_outcome_id": "",
                        "normalized_metric_signature": "",
                        "metric_text": "",
                        "metric_value": "",
                        "metric_unit": "",
                    },
                },
            }
        )
    source["cases"][0]["claims"][0]["candidate_frontier_metadata"] = {
        "raw_eligible_candidate_count": 17,
        "allocator_candidate_budget": 64,
        "allocator_budget_truncated": False,
        "candidate_universe_size": 17,
        "frontier_k": 10,
        "frontier_exhausted": False,
        "judged_top_count": 10,
        "judged_candidate_count": 17,
        "candidate_judging_scope": "FULL_FINITE_UNIVERSE",
        "selected_audit_extra_included": True,
        "selected_audit_extra_rank": 17,
    }
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=source,
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    validation = validate_prelabel_packet(packet, require_w9=True)
    assert validation["status"] == "PASS_TEST_ONLY", validation["errors"]
    mapping = next(
        row
        for row in read_jsonl(packet / "sealed_internal/retrieval_mapping.jsonl")
        if row["case_id"] == source["cases"][0]["case_id"]
        and row["claim_unit_id"] == source["cases"][0]["claims"][0]["claim_unit_id"]
    )
    assert [row["rank"] for row in mapping["candidates"]] == list(range(1, 18))
    assert mapping["candidates"][-1]["selected"] is True
    assert mapping["candidate_frontier_metadata"]["candidate_universe_size"] == 17
    assert mapping["candidate_frontier_metadata"]["frontier_exhausted"] is False
    assert mapping["candidate_frontier_metadata"]["judged_top_count"] == 10
    assert mapping["candidate_frontier_metadata"]["judged_candidate_count"] == 17
    assert mapping["candidate_judging_scope"] == "FULL_FINITE_UNIVERSE"
    assert mapping["selected_audit_extra"] == {
        "candidate_id": "selected-outside-top-ten",
        "rank": 17,
    }
    reviewer_query = next(
        row
        for row in read_jsonl(packet / "reviewer_retrieval/retrieval_queries.jsonl")
        if row["query_id"] == mapping["query_id"]
    )
    assert all("rank" not in row and "selected" not in row for row in reviewer_query["candidates"])


def test_builder_recursively_rejects_score_leakage(tmp_path: Path) -> None:
    source = _source_bundle()
    source["cases"][0]["claims"][0]["proof_context"]["nested"] = {
        "arbitrary": {"SystemConfidence": 0.99}
    }
    with pytest.raises(PacketBuildError, match="forbidden keys"):
        build_packet(
            source_bundle=source,
            out_dir=tmp_path / "packet",
            blinding_nonce=TEST_BLINDING_NONCE,
            repo_root=REPO,
            require_w9=True,
        )
    readiness = assess_source_bundle_readiness(
        source_bundle=source,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    assert readiness["packet_build_ready"] is False
    assert "SystemConfidence" in readiness["errors"][0]


def test_prelabel_validation_detects_tampering(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    claim_path = packet / "reviewer_proof/claim_items.jsonl"
    claims = read_jsonl(claim_path)
    claims[0]["proof_context"]["system_verdict"] = "PASS"
    write_jsonl(claim_path, claims)
    result = validate_prelabel_packet(packet, require_w9=True)
    assert result["status"] == "FAIL"
    assert any("digest mismatch" in error or "forbidden keys" in error for error in result["errors"])


def test_prelabel_validation_binds_top_level_checksum_inventory(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        blinding_nonce=TEST_BLINDING_NONCE,
        out_dir=packet,
        repo_root=REPO,
        require_w9=True,
    )
    (packet / "SHA256SUMS").write_text("0" * 64 + "  packet_manifest.json\n", encoding="utf-8")
    result = validate_prelabel_packet(packet, require_w9=True)
    assert result["status"] == "FAIL"
    assert result["checks"]["top_level_checksum_valid"] is False
    assert any("top-level SHA256SUMS differs" in error for error in result["errors"])


def test_identical_proof_identity_across_retrieval_splits_stays_in_one_proof_split(
    tmp_path: Path,
) -> None:
    source = _source_bundle()
    shared_binding = {
        "skill_id": "skill:shared-cross-target",
        "fact_id": "fact:shared-cross-target",
        "metric_outcome_id": "metric:shared-cross-target",
        "normalized_metric_signature": "20 pct growth",
        "metric_text": "20% growth",
        "metric_value": "20",
        "metric_unit": "PERCENT",
        "graph_path_ids": ["path:shared:skill", "path:shared:fact", "path:shared:metric"],
    }
    source["cases"][0]["claims"][0]["visible_claim_text"] = "  Shared PROOF claim.  "
    source["cases"][0]["claims"][0]["binding"] = shared_binding
    source["cases"][1]["claims"][0]["visible_claim_text"] = (
        "A distinct paraphrase grounded in the same immutable proof binding."
    )
    source["cases"][1]["claims"][0]["binding"] = dict(shared_binding)

    packet = tmp_path / "packet"
    build_packet(
        source_bundle=source,
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    validation = validate_prelabel_packet(packet, require_w9=True)
    assert validation["status"] == "PASS_TEST_ONLY", validation["errors"]
    mappings = read_jsonl(packet / "sealed_internal/claim_mapping.jsonl")
    shared = [
        row
        for row in mappings
        if row["binding"].get("skill_id") == "skill:shared-cross-target"
    ]
    assert len(shared) == 2
    assert {row["retrieval_split"] for row in shared} == {
        "calibration",
        "release_holdout",
    }
    assert len({row["proof_identity_digest"] for row in shared}) == 2
    assert len({row["proof_split_group_digest"] for row in shared}) == 1
    assert len({row["proof_split"] for row in shared}) == 1
    assert validation["checks"]["proof_split_group_retrieval_overlap_count"] >= 1


def test_readiness_runs_prelabel_target_input_leakage_validation(tmp_path: Path) -> None:
    manifest = yaml.safe_load(DEFAULT_TARGET_MANIFEST.read_text(encoding="utf-8"))
    calibration_case = manifest["cases"][0]
    holdout_case = manifest["cases"][1]
    for kind in ("jd", "brief"):
        holdout_case[f"{kind}_path"] = calibration_case[f"{kind}_path"]
        holdout_case[f"{kind}_sha256"] = calibration_case[f"{kind}_sha256"]
    manifest_path = tmp_path / "target_cases.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    readiness = assess_source_bundle_readiness(
        source_bundle=_source_bundle(),
        blinding_nonce=TEST_BLINDING_NONCE,
        target_manifest_path=manifest_path,
        repo_root=REPO,
        require_w9=True,
    )
    assert readiness["status"] == "FAIL"
    assert readiness["packet_build_ready"] is False
    assert readiness["prelabel_validation"]["status"] == "FAIL"
    assert any("retrieval target input leakage" in error for error in readiness["errors"])


def test_duplicate_heavy_proofs_cannot_fake_minimum_identity_support(tmp_path: Path) -> None:
    source = _source_bundle()
    for case in source["cases"]:
        section_ordinals: dict[str, int] = {}
        for claim in case["claims"]:
            section = claim["section_id"]
            ordinal = section_ordinals.get(section, 0)
            section_ordinals[section] = ordinal + 1
            group = ordinal % 2
            claim["visible_claim_text"] = f"Duplicate-heavy {section} proof group {group}"
            claim["binding"] = {
                "skill_id": f"skill:duplicate:{section}:{group}",
                "fact_id": f"fact:duplicate:{section}:{group}",
                "metric_outcome_id": "",
                "normalized_metric_signature": "",
                "metric_text": "",
                "metric_value": "",
                "metric_unit": "",
                "graph_path_ids": [
                    f"path:duplicate:{section}:{group}:skill",
                    f"path:duplicate:{section}:{group}:fact",
                ],
            }
    with pytest.raises(PacketBuildError, match="unable to allocate proof split"):
        build_packet(
            source_bundle=source,
            out_dir=tmp_path / "packet",
            blinding_nonce=TEST_BLINDING_NONCE,
            repo_root=REPO,
            require_w9=True,
        )


def test_completed_validation_and_sealed_export(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "PASS_TEST_ONLY", result["errors"]
    assert result["checks"]["review_count"] == 2 * (282 + 84 + 6)
    assert result["checks"]["adjudication_count"] == 282 + 84 + 6

    receipt = export_adjudicated_evaluation(
        packet_dir=packet,
        labels_dir=labels,
        require_w9=True,
    )
    assert receipt["status"] == "PASS_TEST_ONLY"
    assert receipt["row_count"] == 282
    assert receipt["retrieval_bearing_row_count"] == 84
    assert sum(receipt["claim_rows_by_split"].values()) == 282
    assert receipt["claim_rows_by_split"] == receipt["claim_rows_by_proof_split"]
    assert receipt["claim_rows_by_retrieval_split"] == {
        "calibration": 141,
        "holdout": 141,
    }
    rows = read_jsonl(Path(receipt["output_path"]))
    assert all(row["split"] == row["proof_split"] for row in rows)
    assert len(
        {
            (row["proof_split_group_digest"], row["proof_split"])
            for row in rows
        }
    ) == len({row["proof_split_group_digest"] for row in rows})
    retrieval_rows = [row for row in rows if row["retrieval_candidates"] is not None]
    assert len(retrieval_rows) == 84
    assert retrieval_rows[0]["proof_score_raw"] == 0.92
    assert retrieval_rows[0]["proof_score_source_field"] == "proof_strength_raw"
    assert retrieval_rows[0]["selection_margin"] == 0.15
    assert len(retrieval_rows[0]["reviewer_refs"]) == 2
    assert len(retrieval_rows[0]["retrieval_reviewer_refs"]) == 2
    assert retrieval_rows[0]["gold_path_ids"]
    assert retrieval_rows[0]["candidate_universe_size"] == 10
    assert retrieval_rows[0]["frontier_k"] == 10
    assert retrieval_rows[0]["frontier_exhausted"] is True
    assert retrieval_rows[0]["judged_top_count"] == 10
    assert retrieval_rows[0]["selected_audit_extra"] is None
    assert retrieval_rows[0]["retrieval_recall_scope"] == "FULL_FINITE_UNIVERSE"
    assert retrieval_rows[0]["candidate_judging_scope"] == "FULL_FINITE_UNIVERSE"
    assert retrieval_rows[0]["judged_candidate_count"] == 10
    assert retrieval_rows[0]["representation_mode"] in {
        "CANONICAL_VISIBLE",
        "DERIVED_ALTERNATIVE",
    }
    assert retrieval_rows[0]["metric_applicable"] is False
    assert all(
        candidate["metric_applicable"] is False
        for candidate in retrieval_rows[0]["retrieval_candidates"]
    )
    assert [row["rank"] for row in retrieval_rows[0]["retrieval_candidates"]] == list(
        range(1, 11)
    )


def test_official_packet_export_and_evaluator_pass_end_to_end(tmp_path: Path) -> None:
    source = _source_bundle(include_w9=False)
    for case in source["cases"]:
        for claim_index, claim in enumerate(case["claims"]):
            claim["system_fields"]["proof_strength_raw"] = (
                0.10 if claim_index < 2 else 0.92
            )
            metric_key = f"{case['case_id']}:{claim['section_id']}:{claim['claim_unit_id']}"
            claim_metric = {
                "metric_outcome_id": f"metric:{metric_key}",
                "normalized_metric_signature": f"{metric_key}:100:PERCENT",
                "metric_text": f"100 percent outcome for {metric_key}",
                "metric_value": "100",
                "metric_unit": "PERCENT",
            }
            claim["binding"].update(claim_metric)
            claim["proof_context"]["metric_text"] = claim_metric["metric_text"]
            for candidate_index, candidate in enumerate(
                claim["candidate_frontier"], 1
            ):
                candidate_metric = (
                    claim_metric
                    if candidate_index == 1
                    else {
                        "metric_outcome_id": f"metric:{metric_key}:candidate:{candidate_index}",
                        "normalized_metric_signature": (
                            f"{metric_key}:candidate:{candidate_index}:PERCENT"
                        ),
                        "metric_text": (
                            f"{candidate_index} percent candidate outcome for {metric_key}"
                        ),
                        "metric_value": str(candidate_index),
                        "metric_unit": "PERCENT",
                    }
                )
                candidate["system_fields"]["binding"].update(candidate_metric)

    source_path = _write_source(tmp_path / "official-source.json", source)
    freeze_receipt = build_source_freeze_receipt(
        source_bundle_path=source_path,
        source_bundle=source,
        target_manifest_path=DEFAULT_TARGET_MANIFEST,
    )
    freeze_receipt_path = tmp_path / "source-freeze-receipt.json"
    write_json(freeze_receipt_path, freeze_receipt)
    packet = tmp_path / "official-packet"
    _build_packet(
        source_bundle=source_path,
        source_freeze_receipt=freeze_receipt_path,
        trusted_source_freeze_receipt_digest=freeze_receipt["receipt_digest"],
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=False,
    )
    prelabel_manifest_sha = _packet_manifest_sha256(packet)
    mappings = read_jsonl(packet / "sealed_internal/claim_mapping.jsonl")
    negative_item_ids = {
        str(row["item_id"])
        for row in mappings
        if row["system_fields"]["proof_strength_raw"] == 0.10
    }
    assert {
        row["proof_split"]
        for row in mappings
        if str(row["item_id"]) in negative_item_ids
    } == {"calibration", "holdout"}
    labels = _completed_labels(
        packet,
        tmp_path / "official-labels",
        negative_claim_item_ids=negative_item_ids,
        respect_metric_applicability=True,
    )

    authority = _test_human_review_authority_receipt(packet)
    authority["authority_mode"] = "TRUSTED_HUMAN_ROSTER_APPROVAL"
    authority["official_authority_eligible"] = True
    authority = record_with_digest(authority, "receipt_digest")
    authority_path = tmp_path / "human-review-authority.json"
    write_json(authority_path, authority)
    authority_sha = file_digest(authority_path)
    dataset_path = tmp_path / "official-adjudicated.jsonl"
    export_receipt_path = tmp_path / "official-adjudicated.receipt.json"
    export_receipt = _export_adjudicated_evaluation(
        packet_dir=packet,
        labels_dir=labels,
        out_path=dataset_path,
        receipt_path=export_receipt_path,
        require_w9=False,
        trusted_source_freeze_receipt_digest=freeze_receipt["receipt_digest"],
        trusted_prelabel_packet_manifest_sha256=prelabel_manifest_sha,
        human_review_authority_receipt=authority_path,
        trusted_human_review_authority_receipt_sha256=authority_sha,
    )
    assert export_receipt["status"] == PASS
    assert export_receipt["official_pass"] is True

    profile = yaml.safe_load(
        (
            REPO
            / "apps_rg/config/domain_contract/resume_graph_evaluation_profile.yaml"
        ).read_text(encoding="utf-8")
    )
    report = evaluate_file(
        dataset_path,
        profile,
        export_receipt_path=export_receipt_path,
        trusted_export_receipt_sha256=file_digest(export_receipt_path),
        trusted_prelabel_packet_manifest_sha256=prelabel_manifest_sha,
        human_review_authority_receipt_path=authority_path,
        trusted_human_review_authority_receipt_sha256=authority_sha,
        packet_dir=packet,
        labels_dir=labels,
    )
    assert report["status"] == PASS, {
        key: value
        for key, value in report["gate_results"].items()
        if value["status"] == "FAIL"
    }
    assert report["evaluation_gate_pass"] is True
    assert report["official_evidence_chain_validated"] is True
    assert report["evidence_chain"]["prelabel_packet_manifest_sha256"] == (
        prelabel_manifest_sha
    )
    assert report["evidence_chain"][
        "human_review_authority_receipt_sha256"
    ] == authority_sha
    protected_report_path = tmp_path / "protected-official-report.json"
    write_json(protected_report_path, report)
    protected_report_sha = file_digest(protected_report_path)
    ci_receipt = build_sanitized_ci_receipt(
        report,
        protected_full_report_sha256=protected_report_sha,
    )
    ci_receipt_path = tmp_path / "official-ci-receipt.json"
    write_json(ci_receipt_path, ci_receipt)
    assert validate_artifact(
        ci_receipt_path,
        trusted_report_sha256=file_digest(ci_receipt_path),
        trusted_full_report_sha256=protected_report_sha,
    ) == []

    wrong_prelabel = evaluate_file(
        dataset_path,
        profile,
        export_receipt_path=export_receipt_path,
        trusted_export_receipt_sha256=file_digest(export_receipt_path),
        trusted_prelabel_packet_manifest_sha256="f" * 64,
        human_review_authority_receipt_path=authority_path,
        trusted_human_review_authority_receipt_sha256=authority_sha,
        packet_dir=packet,
        labels_dir=labels,
    )
    assert wrong_prelabel["status"] != PASS
    assert any(
        "TRUSTED_PRELABEL_PACKET_MANIFEST_SHA256_MISMATCH" in reason
        for reason in wrong_prelabel["reasons"]
    )

    wrong_authority = evaluate_file(
        dataset_path,
        profile,
        export_receipt_path=export_receipt_path,
        trusted_export_receipt_sha256=file_digest(export_receipt_path),
        trusted_prelabel_packet_manifest_sha256=prelabel_manifest_sha,
        human_review_authority_receipt_path=authority_path,
        trusted_human_review_authority_receipt_sha256="e" * 64,
        packet_dir=packet,
        labels_dir=labels,
    )
    assert wrong_authority["status"] != PASS
    assert any(
        "HUMAN_REVIEW_AUTHORITY_RECEIPT_SHA256_MISMATCH" in reason
        for reason in wrong_authority["reasons"]
    )


def test_completed_w6_packet_does_not_require_or_read_w9_distribution(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(include_w9=False),
        blinding_nonce=TEST_BLINDING_NONCE,
        out_dir=packet,
        repo_root=REPO,
        require_w9=False,
    )
    assert not (packet / "reviewer_w9").exists()
    labels = _completed_labels(packet, tmp_path / "labels")
    assert not (labels / "w9_reviews.jsonl").exists()
    result = validate_completed_packet(packet, labels, require_w9=False)
    assert result["status"] == "PASS_TEST_ONLY", result["errors"]
    assert result["checks"]["expected_item_count"] == 282 + 84
    assert result["checks"]["participant_cohorts_pairwise_disjoint"] is True
    export_receipt = export_adjudicated_evaluation(
        packet_dir=packet,
        labels_dir=labels,
        require_w9=False,
    )
    assert export_receipt["status"] == "PASS_TEST_ONLY"
    assert export_receipt["row_count"] == 282


def test_completed_validation_rejects_nonhuman_unknown_and_missing_adjudication(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    claim_reviews_path = labels / "claim_reviews.jsonl"
    reviews = read_jsonl(claim_reviews_path)
    reviews[0]["reviewer_type"] = "model"
    reviews[0]["labels"]["authority_eligible"] = "UNKNOWN"
    reviews[0] = record_with_digest(reviews[0], "record_digest")
    write_jsonl(claim_reviews_path, reviews)
    adjudication_path = labels / "adjudications.jsonl"
    adjudications = read_jsonl(adjudication_path)
    write_jsonl(adjudication_path, adjudications[1:])

    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any("reviewer_type must be human" in error for error in result["errors"])
    assert any("UNKNOWN/non-final is nonpass" in error for error in result["errors"])
    assert any("missing adjudication" in error for error in result["errors"])


@pytest.mark.parametrize("label_stage", ["primary", "final"])
def test_retrieval_invalid_proof_cannot_carry_positive_relevance(
    tmp_path: Path, label_stage: str
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    if label_stage == "primary":
        path = labels / "retrieval_reviews.jsonl"
        rows = read_jsonl(path)
        rows[0]["labels"]["candidates"][0]["path_valid"] = False
        rows[0]["labels"]["candidates"][0]["relevance_grade"] = 3
    else:
        path = labels / "adjudications.jsonl"
        rows = read_jsonl(path)
        target = next(row for row in rows if row["item_type"] == "retrieval")
        target["final_labels"]["candidates"][0]["path_valid"] = False
        target["final_labels"]["candidates"][0]["relevance_grade"] = 3
    write_jsonl(path, [record_with_digest(row, "record_digest") for row in rows])

    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any(
        "invalid path or inexact metric requires relevance_grade 0" in error
        for error in result["errors"]
    )


def test_metric_bearing_claim_cannot_evade_binding_review_with_na(tmp_path: Path) -> None:
    source = _source_bundle()
    source["cases"][0]["claims"][0]["binding"].update(
        {
            "metric_outcome_id": "metric:rendered-growth",
            "normalized_metric_signature": "20 pct growth",
            "metric_text": "20% growth",
            "metric_value": "20",
            "metric_unit": "PERCENT",
        }
    )
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=source,
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    review_path = labels / "claim_reviews.jsonl"
    reviews = read_jsonl(review_path)
    target_item_id = str(
        read_jsonl(packet / "sealed_internal/claim_mapping.jsonl")[0]["item_id"]
    )
    for index, review in enumerate(reviews):
        if str(review["item_id"]) != target_item_id:
            continue
        review["labels"]["metric_binding"] = "NOT_APPLICABLE"
        reviews[index] = record_with_digest(review, "record_digest")
    write_jsonl(review_path, reviews)
    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any(
        "metric-bearing claim cannot be NOT_APPLICABLE" in error
        for error in result["errors"]
    )


def test_metric_bearing_retrieval_candidate_cannot_be_labeled_na(tmp_path: Path) -> None:
    source = _source_bundle()
    source["cases"][0]["claims"][0]["candidate_frontier"][0][
        "system_fields"
    ]["binding"].update(
        {
            "metric_outcome_id": "metric:candidate-growth",
            "normalized_metric_signature": "20 pct candidate growth",
            "metric_text": "20% candidate growth",
            "metric_value": "20",
            "metric_unit": "PERCENT",
        }
    )
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=source,
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    review_path = labels / "retrieval_reviews.jsonl"
    reviews = read_jsonl(review_path)
    retrieval_mapping, metric_candidate = next(
        (mapping, candidate)
        for mapping in read_jsonl(
            packet / "sealed_internal/retrieval_mapping.jsonl"
        )
        for candidate in mapping["candidates"]
        if candidate["metric_applicable"] is True
    )
    target_query_id = str(retrieval_mapping["query_id"])
    target_candidate_id = str(metric_candidate["candidate_blind_id"])
    for index, review in enumerate(reviews):
        if str(review["item_id"]) != target_query_id:
            continue
        for candidate in review["labels"]["candidates"]:
            if str(candidate["candidate_blind_id"]) == target_candidate_id:
                candidate["metric_binding"] = "NOT_APPLICABLE"
        reviews[index] = record_with_digest(review, "record_digest")
    write_jsonl(review_path, reviews)
    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any(
        "metric-bearing candidate cannot be NOT_APPLICABLE" in error
        for error in result["errors"]
    )


def test_nonmetric_retrieval_candidate_cannot_inflate_metric_exactness(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    path = labels / "retrieval_reviews.jsonl"
    rows = read_jsonl(path)
    rows[0]["labels"]["candidates"][0]["metric_binding"] = "EXACT"
    write_jsonl(path, [record_with_digest(row, "record_digest") for row in rows])
    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any(
        "nonmetric candidate must be NOT_APPLICABLE" in error
        for error in result["errors"]
    )


def test_completed_validation_enforces_overall_proof_rubric_logic(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        blinding_nonce=TEST_BLINDING_NONCE,
        out_dir=packet,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    review_path = labels / "claim_reviews.jsonl"
    reviews = read_jsonl(review_path)
    target_item = str(reviews[0]["item_id"])
    target_reviews = [row for row in reviews if row["item_id"] == target_item]
    assert len(target_reviews) == 2
    for index, review in enumerate(reviews):
        if review["item_id"] != target_item:
            continue
        review["labels"]["authority_eligible"] = "FAIL"
        reviews[index] = record_with_digest(review, "record_digest")
    write_jsonl(review_path, reviews)

    adjudication_path = labels / "adjudications.jsonl"
    adjudications = read_jsonl(adjudication_path)
    for index, adjudication in enumerate(adjudications):
        if adjudication["item_type"] != "claim" or adjudication["item_id"] != target_item:
            continue
        adjudication["final_labels"]["authority_eligible"] = "FAIL"
        adjudication["review_digests"] = [
            row["record_digest"] for row in reviews if row["item_id"] == target_item
        ]
        adjudications[index] = record_with_digest(adjudication, "record_digest")
    write_jsonl(adjudication_path, adjudications)

    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any(
        "overall_proof_valid disagrees with the frozen proof rubric" in error
        for error in result["errors"]
    )


def test_completed_validation_rejects_proof_retrieval_reviewer_cohort_overlap(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        blinding_nonce=TEST_BLINDING_NONCE,
        out_dir=packet,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    review_path = labels / "retrieval_reviews.jsonl"
    reviews = read_jsonl(review_path)
    target_item = str(reviews[0]["item_id"])
    overlapping_ref = "human-reviewer://proof-1"
    reviews[0]["reviewer_identity_ref"] = overlapping_ref
    reviews[0]["reviewer_id_hash"] = hashlib.sha256(
        overlapping_ref.encode("utf-8")
    ).hexdigest()
    reviews[0] = record_with_digest(reviews[0], "record_digest")
    write_jsonl(review_path, reviews)

    adjudication_path = labels / "adjudications.jsonl"
    adjudications = read_jsonl(adjudication_path)
    for index, adjudication in enumerate(adjudications):
        if (
            adjudication["item_type"] != "retrieval"
            or adjudication["item_id"] != target_item
        ):
            continue
        adjudication["review_digests"] = [
            row["record_digest"] for row in reviews if row["item_id"] == target_item
        ]
        adjudications[index] = record_with_digest(adjudication, "record_digest")
    write_jsonl(adjudication_path, adjudications)

    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any(
        "proof and retrieval reviewer/adjudicator participant hash cohorts must be disjoint"
        in error
        for error in result["errors"]
    )
    assert any(
        "proof and retrieval reviewer/adjudicator participant identity-ref cohorts must be disjoint"
        in error
        for error in result["errors"]
    )


def test_completed_validation_enforces_pairwise_w9_participant_isolation(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        blinding_nonce=TEST_BLINDING_NONCE,
        out_dir=packet,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    review_path = labels / "w9_reviews.jsonl"
    reviews = read_jsonl(review_path)
    target_item = str(reviews[0]["item_id"])
    overlapping_ref = "human-reviewer://retrieval-1"
    reviews[0]["reviewer_identity_ref"] = overlapping_ref
    reviews[0]["reviewer_id_hash"] = hashlib.sha256(
        overlapping_ref.encode("utf-8")
    ).hexdigest()
    reviews[0] = record_with_digest(reviews[0], "record_digest")
    write_jsonl(review_path, reviews)

    adjudication_path = labels / "adjudications.jsonl"
    adjudications = read_jsonl(adjudication_path)
    for index, adjudication in enumerate(adjudications):
        if adjudication["item_type"] == "w9_pair" and adjudication["item_id"] == target_item:
            adjudication["review_digests"] = [
                row["record_digest"] for row in reviews if row["item_id"] == target_item
            ]
            adjudications[index] = record_with_digest(adjudication, "record_digest")
    write_jsonl(adjudication_path, adjudications)

    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any(
        "retrieval and W9 reviewer/adjudicator participant hash cohorts must be disjoint"
        in error
        for error in result["errors"]
    )


def test_human_adjudicator_is_included_in_cross_cohort_participant_boundary(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        blinding_nonce=TEST_BLINDING_NONCE,
        out_dir=packet,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    adjudication_path = labels / "adjudications.jsonl"
    adjudications = read_jsonl(adjudication_path)
    overlapping_ref = "human-reviewer://proof-1"
    for index, adjudication in enumerate(adjudications):
        if adjudication["item_type"] != "retrieval":
            continue
        adjudication.update(
            {
                "status": "ADJUDICATED",
                "adjudicator_type": "human",
                "adjudicator_id_hash": hashlib.sha256(
                    overlapping_ref.encode("utf-8")
                ).hexdigest(),
                "adjudicator_identity_ref": overlapping_ref,
                "qualification_ref": "qualification://semantic-proof-review",
                "human_attestation": True,
            }
        )
        adjudications[index] = record_with_digest(adjudication, "record_digest")
        break
    write_jsonl(adjudication_path, adjudications)

    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any(
        "proof and retrieval reviewer/adjudicator participant hash cohorts must be disjoint"
        in error
        for error in result["errors"]
    )


def test_completed_validation_requires_w9_resume_coach_qualification(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")

    reviews_path = labels / "w9_reviews.jsonl"
    reviews = read_jsonl(reviews_path)
    reviews[0]["qualification_ref"] = "qualification://generic-human-review"
    reviews[0] = record_with_digest(reviews[0], "record_digest")
    write_jsonl(reviews_path, reviews)

    adjudication_path = labels / "adjudications.jsonl"
    adjudications = read_jsonl(adjudication_path)
    first_id = str(reviews[0]["item_id"])
    second_id = str(reviews[2]["item_id"])
    for index, adjudication in enumerate(adjudications):
        if adjudication["item_type"] != "w9_pair":
            continue
        if adjudication["item_id"] == first_id:
            adjudication["review_digests"] = [
                row["record_digest"] for row in reviews if row["item_id"] == first_id
            ]
            adjudications[index] = record_with_digest(adjudication, "record_digest")
        elif adjudication["item_id"] == second_id:
            adjudication.update(
                {
                    "status": "ADJUDICATED",
                    "adjudicator_type": "human",
                    "adjudicator_identity_ref": "human-reviewer://independent-third-reviewer",
                    "adjudicator_id_hash": hashlib.sha256(
                        b"human-reviewer://independent-third-reviewer"
                    ).hexdigest(),
                    "qualification_ref": "qualification://generic-human-review",
                    "human_attestation": True,
                }
            )
            adjudications[index] = record_with_digest(adjudication, "record_digest")
    write_jsonl(adjudication_path, adjudications)

    result = validate_completed_packet(packet, labels, require_w9=True)
    qualification_errors = [
        error
        for error in result["errors"]
        if "W9 qualification_ref must use resume-coach://" in error
    ]
    assert result["status"] == "FAIL"
    assert len(qualification_errors) == 2
    assert any("review/" in error for error in qualification_errors)
    assert any("/adjudicator" in error for error in qualification_errors)


def test_cli_fabricated_fixture_cannot_receive_official_pass(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = _source_bundle()
    source_path = _write_source(tmp_path / "source.json", source)
    receipt = _test_freeze_receipt(source)
    receipt_path = _write_source(tmp_path / "freeze_receipt.json", receipt)
    nonce_path = tmp_path / "blinding_nonce.hex"
    nonce_path.write_text(TEST_BLINDING_NONCE + "\n", encoding="utf-8")
    nonce_path.chmod(0o600)
    code = main(
        [
            "readiness",
            "--source-bundle",
            str(source_path),
            "--freeze-receipt",
            str(receipt_path),
            "--expected-freeze-receipt-digest",
            receipt["receipt_digest"],
            "--blinding-nonce-file",
            str(nonce_path),
            "--repo-root",
            str(REPO),
            "--require-w9",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert payload["status"] == "FAIL"
    assert payload["packet_build_ready"] is False
    assert any("clean-checkout real-allocator" in error for error in payload["errors"])


def test_public_seed_cannot_be_used_as_a_blinding_nonce(tmp_path: Path) -> None:
    with pytest.raises(PacketBuildError, match="explicit lowercase 64-hex secret"):
        build_packet(
            source_bundle=_source_bundle(include_w9=True),
            out_dir=tmp_path / "packet",
            blinding_nonce="apps_rg-c03-human-eval-v1",
            repo_root=REPO,
            require_w9=True,
        )


def test_distinct_blinding_nonces_create_distinct_packets(tmp_path: Path) -> None:
    source = _source_bundle(include_w9=False)
    first_dir = tmp_path / "nonce-one"
    second_dir = tmp_path / "nonce-two"
    first = build_packet(
        source_bundle=source,
        out_dir=first_dir,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
    )
    second = build_packet(
        source_bundle=source,
        out_dir=second_dir,
        blinding_nonce="cd" * 32,
        repo_root=REPO,
    )
    assert first["blinding_nonce_commitment"] != second["blinding_nonce_commitment"]
    assert first["packet_id"] != second["packet_id"]
    assert first["manifest_digest"] != second["manifest_digest"]
    first_claim = read_jsonl(first_dir / "reviewer_proof/claim_items.jsonl")[0]
    second_claim = read_jsonl(second_dir / "reviewer_proof/claim_items.jsonl")[0]
    assert first_claim["item_id"] != second_claim["item_id"]


def test_cli_rejects_publicly_readable_nonce_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source_path = _write_source(tmp_path / "source.json", _source_bundle())
    receipt = _test_freeze_receipt(_source_bundle())
    receipt_path = _write_source(tmp_path / "freeze_receipt.json", receipt)
    nonce_path = tmp_path / "insecure_nonce.hex"
    nonce_path.write_text(TEST_BLINDING_NONCE + "\n", encoding="utf-8")
    nonce_path.chmod(0o644)
    code = main(
        [
            "readiness",
            "--source-bundle",
            str(source_path),
            "--freeze-receipt",
            str(receipt_path),
            "--expected-freeze-receipt-digest",
            receipt["receipt_digest"],
            "--blinding-nonce-file",
            str(nonce_path),
            "--repo-root",
            str(REPO),
            "--require-w9",
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert payload["status"] == "FAIL"
    assert "owner-only" in payload["errors"][0]


def test_official_build_rejects_in_memory_fixture_provenance(tmp_path: Path) -> None:
    source = _source_bundle()
    receipt = _test_freeze_receipt(source)
    with pytest.raises(PacketBuildError, match="official packet build requires source_bundle"):
        _build_packet(
            source_bundle=source,
            source_freeze_receipt=receipt,
            trusted_source_freeze_receipt_digest=receipt["receipt_digest"],
            out_dir=tmp_path / "packet",
            blinding_nonce=TEST_BLINDING_NONCE,
            repo_root=REPO,
            require_w9=True,
        )


def test_validation_requires_external_trusted_freeze_receipt_pin(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    missing = _validate_prelabel_packet(
        packet,
        require_w9=True,
        allow_test_only_provenance=True,
    )
    assert missing["status"] == "FAIL"
    assert any("trusted source freeze receipt digest is required" in error for error in missing["errors"])

    mismatched = _validate_prelabel_packet(
        packet,
        require_w9=True,
        trusted_source_freeze_receipt_digest="00" * 32,
        allow_test_only_provenance=True,
    )
    assert mismatched["status"] == "FAIL"
    assert any("differs from trusted digest" in error for error in mismatched["errors"])


def test_build_rejects_stale_source_after_freeze_receipt(tmp_path: Path) -> None:
    source = _source_bundle()
    source_path = _write_source(tmp_path / "source.json", source)
    receipt = _test_freeze_receipt(source)
    receipt_path = _write_source(tmp_path / "freeze_receipt.json", receipt)
    source["graph_digest"] = "f" * 64
    _write_source(source_path, source)

    with pytest.raises(PacketBuildError, match="source_bundle_sha256 binding mismatch"):
        _build_packet(
            source_bundle=source_path,
            source_freeze_receipt=receipt_path,
            trusted_source_freeze_receipt_digest=receipt["receipt_digest"],
            allow_test_only_provenance=True,
            out_dir=tmp_path / "packet",
            blinding_nonce=TEST_BLINDING_NONCE,
            repo_root=REPO,
            require_w9=True,
        )


def test_top_k_only_retrieval_pool_cannot_pass_full_universe_contract(
    tmp_path: Path,
) -> None:
    source = _source_bundle()
    claim = source["cases"][0]["claims"][0]
    claim["candidate_frontier_metadata"].update(
        {
            "raw_eligible_candidate_count": 12,
            "candidate_universe_size": 12,
            "frontier_exhausted": False,
            "judged_top_count": 10,
            "judged_candidate_count": 12,
        }
    )
    with pytest.raises(PacketBuildError, match="complete bounded finite universe"):
        build_packet(
            source_bundle=source,
            out_dir=tmp_path / "packet",
            blinding_nonce=TEST_BLINDING_NONCE,
            repo_root=REPO,
            require_w9=True,
        )


@pytest.mark.parametrize("intruder_kind", ["file", "directory", "symlink"])
def test_reviewer_roots_reject_every_unlisted_filesystem_entry(
    tmp_path: Path, intruder_kind: str
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    intruder = packet / "reviewer_proof" / "unlisted-entry"
    if intruder_kind == "file":
        intruder.write_text("must not be distributed\n", encoding="utf-8")
    elif intruder_kind == "directory":
        intruder.mkdir()
    else:
        intruder.symlink_to(packet / "packet_manifest.json")

    result = validate_prelabel_packet(packet, require_w9=True)
    assert result["status"] == "FAIL"
    assert any(
        "reviewer root filesystem inventory differs from allowlist" in error
        for error in result["errors"]
    )


def test_completed_validation_requires_original_prelabel_manifest_pin(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    authority = _test_human_review_authority_receipt(packet)
    result = _validate_completed_packet(
        packet,
        labels,
        require_w9=True,
        trusted_source_freeze_receipt_digest=_packet_receipt_digest(packet),
        trusted_prelabel_packet_manifest_sha256="00" * 32,
        human_review_authority_receipt=authority,
        trusted_human_review_authority_receipt_sha256=(
            human_review_authority_receipt_file_sha256(authority)
        ),
        allow_test_only_provenance=True,
    )
    assert result["status"] == "FAIL"
    assert any("differs from the trusted prelabel" in error for error in result["errors"])


def test_postlabel_split_rewrite_and_rehash_fails_out_of_band_prelabel_pin(
    tmp_path: Path,
) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    trusted_prelabel_sha = _packet_manifest_sha256(packet)
    labels = _completed_labels(packet, tmp_path / "labels")
    authority = _test_human_review_authority_receipt(packet)
    new_commitment = "f" * 64
    internal_paths = [
        packet / "sealed_internal/claim_mapping.jsonl",
        packet / "sealed_internal/retrieval_mapping.jsonl",
        packet / "sealed_internal/w9_variant_mapping.jsonl",
    ]
    claim_rows = read_jsonl(internal_paths[0])
    profile = claim_rows[0]["target_profile_id"]
    case_splits = {
        row["case_id"]: row["retrieval_split"]
        for row in claim_rows
        if row["target_profile_id"] == profile
    }
    assert len(case_splits) == 2
    swapped = {
        case_id: (
            "release_holdout" if split == "calibration" else "calibration"
        )
        for case_id, split in case_splits.items()
    }
    for path in internal_paths:
        rows = read_jsonl(path)
        for row in rows:
            if row["case_id"] in swapped:
                row["retrieval_split"] = swapped[row["case_id"]]
            row["retrieval_split_assignment_commitment"] = new_commitment
        write_jsonl(
            path,
            [record_with_digest(row, "record_digest") for row in rows],
        )

    manifest_path = packet / "packet_manifest.json"
    manifest = read_json(manifest_path)
    manifest["retrieval_split_assignment_commitment"] = new_commitment
    for row in manifest["files"]:
        file_path = packet / row["path"]
        row["sha256"] = file_digest(file_path)
    manifest = record_with_digest(manifest, "manifest_digest")
    write_json(manifest_path, manifest)
    checksum_rows = [
        (file_digest(packet / row["path"]), row["path"])
        for row in manifest["files"]
    ] + [(file_digest(manifest_path), "packet_manifest.json")]
    write_private_text(
        packet / "SHA256SUMS",
        "".join(
            f"{digest}  {path}\n"
            for digest, path in sorted(checksum_rows, key=lambda row: row[1])
        ),
    )
    postattack_prelabel = validate_prelabel_packet(packet, require_w9=True)
    assert postattack_prelabel["status"] == "PASS_TEST_ONLY", postattack_prelabel[
        "errors"
    ]

    result = _validate_completed_packet(
        packet,
        labels,
        require_w9=True,
        trusted_source_freeze_receipt_digest=_packet_receipt_digest(packet),
        trusted_prelabel_packet_manifest_sha256=trusted_prelabel_sha,
        human_review_authority_receipt=authority,
        trusted_human_review_authority_receipt_sha256=(
            human_review_authority_receipt_file_sha256(authority)
        ),
        allow_test_only_provenance=True,
    )
    assert result["status"] == "FAIL"
    assert any("differs from the trusted prelabel" in error for error in result["errors"])


def test_forged_self_attested_reviewer_is_not_authorized(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    labels = _completed_labels(packet, tmp_path / "labels")
    reviews_path = labels / "claim_reviews.jsonl"
    reviews = read_jsonl(reviews_path)
    forged_ref = "human-reviewer://self-minted-forged-reviewer"
    reviews[0]["reviewer_identity_ref"] = forged_ref
    reviews[0]["reviewer_id_hash"] = hashlib.sha256(
        forged_ref.encode("utf-8")
    ).hexdigest()
    reviews[0] = record_with_digest(reviews[0], "record_digest")
    write_jsonl(reviews_path, reviews)
    result = validate_completed_packet(packet, labels, require_w9=True)
    assert result["status"] == "FAIL"
    assert any("not authorized for this cohort/role" in error for error in result["errors"])


def test_prelabel_receipt_binds_split_and_manifest_before_review(tmp_path: Path) -> None:
    packet = tmp_path / "packet"
    build_packet(
        source_bundle=_source_bundle(),
        out_dir=packet,
        blinding_nonce=TEST_BLINDING_NONCE,
        repo_root=REPO,
        require_w9=True,
    )
    receipt = build_prelabel_packet_receipt(
        packet,
        trusted_source_freeze_receipt_digest=_packet_receipt_digest(packet),
        require_w9=True,
        allow_test_only_provenance=True,
    )
    manifest = read_json(packet / "packet_manifest.json")
    assert receipt["packet_manifest_sha256"] == _packet_manifest_sha256(packet)
    assert receipt["proof_split_policy_salt"] == manifest["proof_split_policy_salt"]
    assert receipt["retrieval_split_assignment_commitment"] == manifest[
        "retrieval_split_assignment_commitment"
    ]
    assert io_helpers.digest_matches(receipt, "receipt_digest")


def test_official_cli_rejects_controller_outputs_inside_git_checkout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main(
        [
            "freeze-source",
            "--source-commit-sha",
            "0" * 40,
            "--out",
            str(REPO / "forbidden-source-bundle.json"),
            "--receipt-out",
            str(REPO / "forbidden-freeze-receipt.json"),
            "--repo-root",
            str(REPO),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert any("outside the git checkout" in error for error in payload["errors"])

    source = _source_bundle()
    source_path = _write_source(tmp_path / "source.json", source)
    receipt = _test_freeze_receipt(source)
    receipt_path = _write_source(tmp_path / "freeze.json", receipt)
    nonce_path = tmp_path / "nonce.hex"
    nonce_path.write_text(TEST_BLINDING_NONCE + "\n", encoding="utf-8")
    nonce_path.chmod(0o600)
    code = main(
        [
            "build",
            "--source-bundle",
            str(source_path),
            "--freeze-receipt",
            str(receipt_path),
            "--expected-freeze-receipt-digest",
            receipt["receipt_digest"],
            "--blinding-nonce-file",
            str(nonce_path),
            "--out",
            str(REPO / "forbidden-packet"),
            "--repo-root",
            str(REPO),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 1
    assert any("outside the git checkout" in error for error in payload["errors"])


def test_target_manifest_rejects_path_escape_and_symlink_sources(tmp_path: Path) -> None:
    target = yaml.safe_load(DEFAULT_TARGET_MANIFEST.read_text(encoding="utf-8"))
    target["cases"][0]["jd_path"] = "../escaped-jd.txt"
    escaped_manifest = tmp_path / "escaped-target.yaml"
    escaped_manifest.write_text(yaml.safe_dump(target), encoding="utf-8")
    with pytest.raises(PacketBuildError, match="escapes repo_root"):
        _target_manifest(escaped_manifest, REPO)

    fixture_root = tmp_path / "fixture-root"
    fixture_root.mkdir(mode=0o700)
    target = yaml.safe_load(DEFAULT_TARGET_MANIFEST.read_text(encoding="utf-8"))
    for case_index, case in enumerate(target["cases"]):
        for kind in ("jd", "brief"):
            content = f"controlled {kind} content {case_index}\n"
            path = fixture_root / f"{case_index}-{kind}.txt"
            path.write_text(content, encoding="utf-8")
            case[f"{kind}_path"] = path.name
            case[f"{kind}_sha256"] = hashlib.sha256(content.encode("utf-8")).hexdigest()
    real_jd = fixture_root / "real-jd.txt"
    real_jd.write_text("symlinked content\n", encoding="utf-8")
    linked_jd = fixture_root / "linked-jd.txt"
    linked_jd.symlink_to(real_jd)
    target["cases"][0]["jd_path"] = linked_jd.name
    target["cases"][0]["jd_sha256"] = file_digest(real_jd)
    linked_manifest = tmp_path / "linked-target.yaml"
    linked_manifest.write_text(yaml.safe_dump(target), encoding="utf-8")
    with pytest.raises(PacketBuildError, match="must not use symlinks"):
        _target_manifest(linked_manifest, fixture_root)


def test_official_export_rejects_output_inside_git_checkout(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="export output must be outside the git checkout"):
        _export_adjudicated_evaluation(
            packet_dir=tmp_path / "packet",
            labels_dir=tmp_path / "labels",
            out_path=REPO / "forbidden-export.jsonl",
            receipt_path=tmp_path / "receipt.json",
        )


def test_controlled_path_rejects_existing_hardlink_alias(tmp_path: Path) -> None:
    original = tmp_path / "original.json"
    original.write_text("{}\n", encoding="utf-8")
    alias = tmp_path / "alias.json"
    os.link(original, alias)
    assert io_helpers.controlled_path_error(alias, repo_root=REPO) == (
        "must not be a hardlink alias"
    )


def test_all_json_schemas_parse() -> None:
    schema_dir = REPO / "apps_rg/evals/c03_human_eval/schemas"
    schemas = sorted(schema_dir.glob("*.schema.json"))
    assert len(schemas) >= 7
    for path in schemas:
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["$schema"].endswith("2020-12/schema")
        assert payload["$id"].startswith("apps_rg.c03_human_eval.")
