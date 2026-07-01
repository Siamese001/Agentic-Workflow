import pytest

from apps_lic.engines import validation_exit as v
from scripts.apps_lic.run_post_w7_live_12_archetype_matrix import (
    _gate_metrics,
    _matrix_violations,
)


def _profile_threshold(judge_id: str) -> float:
    return v._judge_profile_for_id(judge_id, required_for_depth="two").threshold


def test_w0_c_level_x1d_thresholds_are_not_lower_than_evidence_support() -> None:
    evidence_threshold = _profile_threshold(v.JUDGE_EVIDENCE_SUPPORT)

    assert _profile_threshold(v.JUDGE_CEO_ORIGINALITY) >= evidence_threshold
    assert _profile_threshold(v.JUDGE_CEO_EVIDENCE_RISK) >= evidence_threshold


def test_w0_hiring_manager_trigger_based_insight_requires_live_judge_policy() -> None:
    judge_ids = v.required_x1d_judge_ids_for_context(
        recipient_class="HIRING_MANAGER",
        message_type="trigger_based_insight",
        proof_ids=("sp_platform_commercialization",),
    )

    assert v.JUDGE_EVIDENCE_SUPPORT in judge_ids
    assert v.JUDGE_LINKEDIN_TONE_NON_GENERIC in judge_ids or v.JUDGE_LINKEDIN_TONE in judge_ids


def test_w0_executive_trigger_with_commercial_proof_requires_evidence_judge() -> None:
    judge_ids = v.required_x1d_judge_ids_for_context(
        recipient_class="EXECUTIVE",
        message_type="trigger_based_insight",
        proof_ids=("sp_platform_commercialization",),
    )

    assert v.JUDGE_EVIDENCE_SUPPORT in judge_ids


def test_w0_matrix_flags_executive_archetype_x1d_not_required_clearance() -> None:
    row = {
        "profile_id": "fixture_exec_hiring_manager",
        "company": "Neo4j",
        "expected_mapped_archetype": "EXECUTIVE",
        "mapped_recipient_archetype": "EXECUTIVE",
        "expected_recipient_class": "HIRING_MANAGER",
        "derived_recipient_class": "HIRING_MANAGER",
        "outcome_authorized": True,
        "message_route": "INMAIL",
        "message_channel": "linkedin_inmail",
        "subject_line": "VP of Product Management, Agentic AI fit at Neo4j",
        "body_chars": 600,
        "proof_bundle_status": "PASS",
        "canonical_producer": "apps_lic.runtime.dispatch.canonical_dispatch",
        "no_send_assertion": True,
        "no_l4_write_assertion": True,
        "no_connector_post_assertion": True,
        "c0_recipient_class_status": "RECIPIENT_CLASS_DERIVED",
        "generation_generator": "claude_sonnet_5_primary",
        "generation_qa_notes": [],
        "draft_text": "Hi Firat, test draft.\n\nAmit",
        "proof_packet_id": "proof:test",
        "selected_candidate_id": "candidate:test",
        "x2_result": "X2_VALIDATION_PASS",
        "x1d_result": "X1D_NOT_REQUIRED",
    }

    violations = _matrix_violations((row,))

    assert any(
        item.get("reason") == "executive_archetype_x1d_not_required"
        for item in violations
    )


def test_w0_gate_metrics_make_x1d_score_and_x2_ratio_visibly_different(tmp_path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "w5_validation_exit.json").write_text(
        """
{
  "payload": {
    "exit_proof_bundle": {
      "x2": {
        "gate_results": [
          {"status": "pass"},
          {"status": "pass"}
        ]
      },
      "x1d": {
        "judge_results": [
            {
            "judge_id": "ceo_attention_originality_x1d",
            "score": 0.82,
            "threshold": 0.88,
            "passed": false
          }
        ]
      }
    }
  }
}
""".strip(),
        encoding="utf-8",
    )

    x1d_metrics = _gate_metrics(run_dir)

    (run_dir / "w5_validation_exit.json").write_text(
        """
{
  "payload": {
    "exit_proof_bundle": {
      "x2": {
        "gate_results": [
          {"status": "pass"},
          {"status": "pass"}
        ]
      },
      "x1d": {
        "judge_results": []
      }
    }
  }
}
""".strip(),
        encoding="utf-8",
    )

    x2_metrics = _gate_metrics(run_dir)

    assert x1d_metrics["gate_score_basis"] == "min_required_live_x1d_judge"
    assert x1d_metrics["gate_score_10"] == 8.2
    assert x1d_metrics["gate_threshold_10"] == 8.8
    assert x2_metrics["gate_score_basis"] == "x2_applicable_gate_pass_ratio"
    assert x2_metrics["gate_score_10"] == 10.0
    assert x2_metrics["gate_threshold_10"] is None
