from __future__ import annotations

from agentic_core.L6_observability.shadow_eval.microsteps import (
    EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF,
    EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY,
    build_apps_eval_alignment,
    build_future_run_proposals,
    build_microstep_coverage,
    build_microstep_patterns,
    build_microstep_rca,
    build_observations_from_eval_rows,
    build_orphan_observation,
)
from agentic_core.L6_observability.shadow_eval.grain_parity import (
    build_l6_apps_eval_grain_parity,
)


def _row(microstep_id: str, verdict: str = "PASS") -> dict[str, object]:
    return {
        "row_id": f"row-{microstep_id}",
        "microstep_id": microstep_id,
        "stage_id": "X2",
        "component_id": "component",
        "subcomponent_id": "subcomponent",
        "lane_id": "headline",
        "gate_id": "gate",
        "artifact_role": "lane_x2_gate_outputs",
        "artifact_ref": f"artifacts/{microstep_id}.json",
        "evidence_digest": "sha256:abc",
        "verdict": verdict,
        "required": True,
        "decisive_reason": "reason",
    }


def test_l6_observations_join_apps_eval_rows_without_authority() -> None:
    rows = [_row("headline.X2.gates.pass"), _row("headline.X1D.judge_result.pass", "FAIL")]

    observations = build_observations_from_eval_rows(rows, runtime_exhaust_bundle_id="reb-1")
    payloads = [observation.to_dict() for observation in observations]
    alignment = build_apps_eval_alignment(
        run_id="run-1",
        runtime_exhaust_bundle_id="reb-1",
        microstep_contract_digest="sha256:contract",
        apps_eval_scorecard_ref="scorecard_rows.jsonl",
        l6_observation_ref="l6_microstep_observations.jsonl",
        apps_eval_rows=rows,
        l6_observations=payloads,
    )

    assert alignment["rows_expected"] == 2
    assert alignment["evidence_class"] == EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF
    assert alignment["missing_in_l6"] == []
    assert alignment["missing_in_apps_eval"] == []
    assert alignment["verdict_mismatches"] == []
    assert alignment["authority_mismatch"] is False
    assert all(row["current_run_mutation_assertion"] is False for row in payloads)
    assert all(row["l4_write_assertion"] is False for row in payloads)
    assert all(row["future_run_only"] is True for row in payloads)


def test_orphan_observation_is_reported_as_missing_in_apps_eval() -> None:
    rows = [_row("headline.X2.gates.pass")]
    observations = build_observations_from_eval_rows(rows, runtime_exhaust_bundle_id="reb-1")
    observations.append(
        build_orphan_observation(
            microstep_id="headline.X2.extra_shadow_probe",
            runtime_exhaust_bundle_id="reb-1",
            source_ref="shadow-extra.json",
        )
    )

    alignment = build_apps_eval_alignment(
        run_id="run-1",
        runtime_exhaust_bundle_id="reb-1",
        microstep_contract_digest="sha256:contract",
        apps_eval_scorecard_ref="scorecard_rows.jsonl",
        l6_observation_ref="l6_microstep_observations.jsonl",
        apps_eval_rows=rows,
        l6_observations=[observation.to_dict() for observation in observations],
    )
    coverage = build_microstep_coverage(observations)

    assert alignment["missing_in_apps_eval"] == []
    assert alignment["orphan_observations"] == ["headline.X2.extra_shadow_probe"]
    assert coverage["orphan_observations"] == 1


def _parity(rows: list[dict[str, object]], observations: list[dict[str, object]], alignment_source: str = "apps_eval_scorecard_rows") -> dict[str, object]:
    return build_l6_apps_eval_grain_parity(
        run_id="run-1",
        runtime_exhaust_bundle_id="reb-1",
        microstep_contract_digest="sha256:contract",
        apps_eval_scorecard_ref="scorecard_rows.jsonl",
        l6_observation_ref="l6_microstep_observations.jsonl",
        apps_eval_rows=rows,
        l6_observations=observations,
        alignment_source=alignment_source,
    )


def test_grain_parity_passes_with_real_apps_eval_rows() -> None:
    rows = [_row("headline.X2.gates.pass")]
    observations = [observation.to_dict() for observation in build_observations_from_eval_rows(rows, runtime_exhaust_bundle_id="reb-1")]

    parity = _parity(rows, observations)

    assert parity["alignment_source"] == "apps_eval_scorecard_rows"
    assert parity["evidence_class"] == EVIDENCE_CLASS_APPS_EVAL_BOUND_PROOF
    assert parity["apps_eval_rows_bound"] is True
    assert parity["grain_parity_status"] == "PASS"
    assert parity["missing_in_l6"] == []
    assert parity["missing_in_apps_eval"] == []


def test_grain_parity_warns_for_contract_only_pseudo_rows() -> None:
    rows = [_row("headline.X2.gates.pass", "NOT_RUN")]
    observations = [observation.to_dict() for observation in build_observations_from_eval_rows(rows, runtime_exhaust_bundle_id="reb-1")]

    parity = _parity(rows, observations, alignment_source="contract_only_pseudo_rows")

    assert parity["apps_eval_rows_bound"] is False
    assert parity["evidence_class"] == EVIDENCE_CLASS_CONTRACT_ONLY_ADVISORY
    assert parity["grain_parity_status"] == "WARN"


def test_microstep_rca_patterns_and_proposals_are_actionable_but_inert() -> None:
    rows = [_row("headline.X2.gates.pass", "FAIL"), _row("headline.X2.gate_artifact.present", "FAIL")]
    observations = [
        observation.to_dict()
        for observation in build_observations_from_eval_rows(rows, runtime_exhaust_bundle_id="reb-1")
    ]

    rca = build_microstep_rca(observations)
    patterns = build_microstep_patterns(observations)
    proposals = build_future_run_proposals(observations)

    assert rca["gap_groups_by_stage"]["X2"] == 2
    assert rca["gap_groups_by_lane"]["headline"] == 2
    assert rca["gap_groups_by_shadow_classification"]["QUALITY_GAP"] == 2
    assert rca["first_blocking_gap"]["microstep_id"] == "headline.X2.gates.pass"
    assert rca["top_repeated_gap_candidates"][0]["recurrence_count"] == 2
    assert patterns["pattern_status"] == "REGRESSION_CANDIDATE"
    assert patterns["recurrence_count"] == 2
    assert proposals["proposal_count"] == 2
    assert proposals["proposals"][0]["blocked_current_run_mutation"] is True
    assert proposals["proposals"][0]["uwg_required_for_activation"] is True
    assert proposals["current_run_mutation_assertion"] is False


def test_grain_parity_warns_on_unbound_extra_l6_observation() -> None:
    rows = [_row("headline.X2.gates.pass", "NOT_RUN")]
    observations = [
        observation.to_dict()
        for observation in build_observations_from_eval_rows(
            [*rows, _row("headline.L6.trace_reconciliation.present", "NOT_RUN")],
            runtime_exhaust_bundle_id="reb-1",
        )
    ]

    parity = _parity(rows, observations, alignment_source="contract_only_pseudo_rows")

    assert parity["apps_eval_rows_bound"] is False
    assert parity["missing_in_apps_eval"][0]["microstep_id"] == "headline.L6.trace_reconciliation.present"
    assert parity["grain_parity_status"] == "WARN"


def test_grain_parity_fails_on_missing_l6_observation() -> None:
    parity = _parity([_row("headline.X2.gates.pass")], [])

    assert parity["grain_parity_status"] == "FAIL"
    assert parity["missing_in_l6"][0]["microstep_id"] == "headline.X2.gates.pass"


def test_grain_parity_fails_on_verdict_mismatch() -> None:
    rows = [_row("headline.X2.gates.pass", "FAIL")]
    observations = [observation.to_dict() for observation in build_observations_from_eval_rows([_row("headline.X2.gates.pass", "PASS")], runtime_exhaust_bundle_id="reb-1")]

    parity = _parity(rows, observations)

    assert parity["grain_parity_status"] == "FAIL"
    assert parity["verdict_mismatches"][0]["apps_eval_verdict"] == "FAIL"


def test_grain_parity_fails_on_authority_mismatch() -> None:
    rows = [_row("headline.X2.gates.pass")]
    observations = [observation.to_dict() for observation in build_observations_from_eval_rows(rows, runtime_exhaust_bundle_id="reb-1")]
    observations[0]["current_run_mutation_assertion"] = True

    parity = _parity(rows, observations)

    assert parity["grain_parity_status"] == "FAIL"
    assert parity["authority_mismatch"] is True
