from __future__ import annotations

from copy import deepcopy

from agentic_core.L6_observability.shadow_eval.independent_parity import (
    SEALED_APPS_RG_OBSERVATION_ORIGIN,
    build_independent_apps_eval_parity,
)


def _eval_row() -> dict[str, object]:
    return {
        "row_id": "row-1",
        "microstep_id": "headline.X2.gates.pass",
        "stage_id": "X2",
        "lane_id": "headline",
        "gate_id": "x2_gates_pass",
        "artifact_role": "lane_x2_gate_outputs",
        "component_id": "apps_rg.generated_lane",
        "subcomponent_id": "lane_x2_deterministic_gates",
        "artifact_ref": "lanes/headline/x2_gate_outputs.json",
        "evidence_digest": "sha256:artifact",
        "verdict": "PASS",
        "required": True,
    }


def _observation() -> dict[str, object]:
    return {
        "record_type": "L6MicrostepObservation",
        "microstep_id": "headline.X2.gates.pass",
        "stage_id": "X2",
        "lane_id": "headline",
        "gate_id": "x2_gates_pass",
        "artifact_role": "lane_x2_gate_outputs",
        "component_id": "apps_rg.generated_lane",
        "subcomponent_id": "lane_x2_deterministic_gates",
        "runtime_exhaust_bundle_id": "reb-1",
        "source_ref": "lanes/headline/x2_gate_outputs.json",
        "artifact_digest": "sha256:artifact",
        "observed_status": "OBSERVED",
        "eval_verdict_seen": "NOT_RUN",
        "required": True,
        "orphan_observation": False,
        "current_run_mutation_assertion": False,
        "l4_write_assertion": False,
        "future_run_only": True,
    }


def _build(eval_rows, observations, **kwargs):
    return build_independent_apps_eval_parity(
        run_id="eval-1",
        runtime_exhaust_bundle_id="reb-1",
        microstep_contract_digest="sha256:contract",
        apps_eval_scorecard_ref="scorecard_rows.jsonl",
        l6_observation_ref="l6_microstep_observations.jsonl",
        apps_eval_rows=eval_rows,
        l6_observations=observations,
        observation_origin=kwargs.pop(
            "observation_origin", SEALED_APPS_RG_OBSERVATION_ORIGIN
        ),
        expected_observation_bundle_id="reb-1",
        **kwargs,
    )


def test_independent_persisted_observation_can_bind_external_verdict() -> None:
    parity = _build([_eval_row()], [_observation()])
    assert parity["grain_parity_status"] == "PASS"
    assert parity["apps_eval_rows_bound"] is True
    assert parity["evidence_class"] == "APPS_EVAL_BOUND_PROOF"
    assert parity["independent_observations"] is True
    assert parity["verdict_mismatches"] == []
    assert parity["verdict_bindings"][0]["binding_mode"] == (
        "external_eval_bound_to_immutable_observation"
    )


def test_projection_origin_cannot_claim_bound_proof() -> None:
    parity = _build(
        [_eval_row()],
        [_observation()],
        observation_origin="apps_eval_projection_rows",
    )
    assert parity["grain_parity_status"] == "FAIL"
    assert parity["apps_eval_rows_bound"] is False
    assert parity["evidence_class"] == "CONTRACT_ONLY_ADVISORY"


def test_duplicate_join_keys_fail_closed() -> None:
    parity = _build([_eval_row(), deepcopy(_eval_row())], [_observation()])
    assert parity["grain_parity_status"] == "FAIL"
    assert parity["duplicate_join_keys"][0]["side"] == "apps_eval"
    assert parity["duplicate_join_keys"][0]["count"] == 2


def test_source_and_digest_mismatch_fail_closed() -> None:
    observation = _observation()
    observation["source_ref"] = "lanes/headline/other.json"
    observation["artifact_digest"] = "sha256:other"
    parity = _build(
        [_eval_row()],
        [observation],
        compare_artifact_digests=True,
    )
    assert parity["grain_parity_status"] == "FAIL"
    assert parity["source_ref_mismatches"]
    assert parity["artifact_digest_mismatches"]


def test_concrete_l6_verdict_mismatch_fails() -> None:
    observation = _observation()
    observation["eval_verdict_seen"] = "FAIL"
    parity = _build([_eval_row()], [observation])
    assert parity["grain_parity_status"] == "FAIL"
    assert parity["verdict_mismatches"][0]["apps_eval_verdict"] == "PASS"
