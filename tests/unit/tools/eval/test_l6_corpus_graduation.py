from __future__ import annotations

import json
from pathlib import Path

from tools.eval.l6_corpus_graduation import (
    build_review_packet,
    decide_graduation,
    stage_candidates,
    validate_exhaust_package,
)


def _exhaust() -> dict:
    return {
        "runtime_exhaust_bundle_id": "rxb-1",
        "created_after_exit": True,
        "current_run_closed": True,
        "trace_refs": ["trace-1"],
        "gate_refs": ["x2-gates"],
        "judge_refs": ["x1d-judges"],
        "exit_disposition_ref": "x3.json",
        "no_l6_current_run_mutation_assertion": True,
        "l6_can_change_x3": False,
        "l6_can_change_exit_disposition": False,
        "findings": [
            {
                "finding_id": "token-truncation",
                "failure_family": "token_truncation",
                "scenario_seed": {"scenario_id": "l6-token-truncation"},
            }
        ],
    }


def test_validate_exhaust_requires_trace_gate_judge_and_exit_refs() -> None:
    exhaust = _exhaust()
    exhaust["judge_refs"] = []

    reasons = validate_exhaust_package(exhaust)

    assert "MISSING_JUDGE_REFS" in reasons


def test_stage_candidates_blocks_unsealed_exhaust() -> None:
    exhaust = _exhaust()
    exhaust["current_run_closed"] = False

    candidates = stage_candidates(exhaust)

    assert candidates[0].status == "BLOCKED"
    assert "CURRENT_RUN_NOT_CLOSED" in candidates[0].reason_codes


def test_stage_candidates_from_sealed_exhaust() -> None:
    candidates = stage_candidates(_exhaust())

    assert len(candidates) == 1
    assert candidates[0].status == "STAGED"
    assert candidates[0].candidate_id == "l6cand-rxb-1-token-truncation"
    assert candidates[0].source_hash


def test_review_packet_is_blind_and_excludes_runtime_authority_fields() -> None:
    candidate = stage_candidates(_exhaust())[0]

    packet = build_review_packet(candidate)

    assert packet.blind is True
    assert packet.required_reviewer_count == 2
    assert "judge_scores" in packet.excluded_fields
    assert packet.scenario_seed["scenario_id"] == "l6-token-truncation"


def test_graduation_requires_review_quorum_and_replay_pass() -> None:
    candidate = stage_candidates(_exhaust())[0]
    reviews = {
        "required_reviewer_count": 2,
        "reviews": [
            {"candidate_id": candidate.candidate_id, "reviewer_id": "r1", "decision": "APPROVE"},
            {"candidate_id": candidate.candidate_id, "reviewer_id": "r2", "decision": "APPROVE"},
        ],
    }
    replay = {
        "scenario_id": "l6-token-truncation",
        "passed": True,
        "baseline": {"status": "MATCH"},
    }

    decision = decide_graduation(
        candidate,
        reviews,
        replay,
        target_corpus_path="data/eval/golden/l6/l6-token-truncation.json",
    )

    assert decision.graduated is True
    assert decision.reason_codes == []


def test_graduation_blocks_baseline_regression() -> None:
    candidate = stage_candidates(_exhaust())[0]
    reviews = {
        "required_reviewer_count": 1,
        "reviews": [
            {"candidate_id": candidate.candidate_id, "reviewer_id": "r1", "decision": "APPROVE"}
        ],
    }
    replay = {
        "scenario_id": "l6-token-truncation",
        "passed": True,
        "baseline": {"status": "REGRESSION"},
    }

    decision = decide_graduation(
        candidate,
        reviews,
        replay,
        target_corpus_path="data/eval/golden/l6/l6-token-truncation.json",
    )

    assert decision.graduated is False
    assert "BASELINE_REGRESSION" in decision.reason_codes


def test_known_failure_seed_file_contains_required_cases() -> None:
    payload = json.loads(Path("data/eval/l6_corpus/known_failure_seeds.json").read_text())
    families = {row["failure_family"] for row in payload["seeds"]}

    assert {"token_truncation", "zero_judge_rows", "decimal_false_positive"} <= families
