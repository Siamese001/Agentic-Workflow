from __future__ import annotations

from agentic_core.L6_observability.shadow_eval.microsteps import (
    build_apps_eval_alignment,
    build_microstep_coverage,
    build_observations_from_eval_rows,
    build_orphan_observation,
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
