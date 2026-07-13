from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from agentic_core.L6_observability.shadow_eval.independent_parity import (
    SEALED_APPS_RG_OBSERVATION_ORIGIN,
    build_independent_apps_eval_parity,
)

_ARTIFACT_DIGEST = "sha256:" + "a" * 64
_OTHER_DIGEST = "sha256:" + "b" * 64
_CONTRACT_DIGEST = "sha256:" + "c" * 64
_SNAPSHOT_DIGEST = "sha256:" + "d" * 64
_REGISTRY_DIGEST = _CONTRACT_DIGEST


def _identity(*, eval_side: bool) -> dict[str, str]:
    result = {
        "parent_run_id": "parent-1",
        "child_run_id": "child-1",
        "section_attempt_id": "attempt-1",
        "runtime_exhaust_bundle_id": "reb-1",
        "microstep_contract_digest": _CONTRACT_DIGEST,
        "registry_digest": _REGISTRY_DIGEST,
    }
    if eval_side:
        result.update(
            run_id="eval-1",
            eval_record_id="eval-1",
            snapshot_digest=_SNAPSHOT_DIGEST,
        )
    return result


def _eval_row() -> dict[str, object]:
    return {
        **_identity(eval_side=True),
        "row_id": "row-1",
        "microstep_id": "headline.X2.gates.pass",
        "stage_id": "X2",
        "lane_id": "headline",
        "gate_id": "x2_gates_pass",
        "artifact_role": "lane_x2_gate_outputs",
        "component_id": "apps_rg.generated_lane",
        "subcomponent_id": "lane_x2_deterministic_gates",
        "artifact_ref": "lanes/headline/x2_gate_outputs.json",
        "evidence_ref": "lanes/headline/x2_gate_outputs.json",
        "evidence_digest": _ARTIFACT_DIGEST,
        "verdict": "PASS",
        "required": True,
    }


def _observation() -> dict[str, object]:
    return {
        **_identity(eval_side=False),
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
        "artifact_digest": _ARTIFACT_DIGEST,
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
        microstep_contract_digest=kwargs.pop(
            "microstep_contract_digest", _CONTRACT_DIGEST
        ),
        apps_eval_scorecard_ref="scorecard_rows.jsonl",
        l6_observation_ref="l6_microstep_observations.jsonl",
        apps_eval_rows=eval_rows,
        l6_observations=observations,
        observation_origin=kwargs.pop(
            "observation_origin", SEALED_APPS_RG_OBSERVATION_ORIGIN
        ),
        expected_observation_bundle_id="reb-1",
        parent_run_id="parent-1",
        child_run_id="child-1",
        section_attempt_id="attempt-1",
        eval_record_id="eval-1",
        snapshot_digest=kwargs.pop("snapshot_digest", _SNAPSHOT_DIGEST),
        registry_digest=kwargs.pop("registry_digest", _REGISTRY_DIGEST),
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
    observation["artifact_digest"] = _OTHER_DIGEST
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


def test_missing_source_ref_fails_closed() -> None:
    observation = _observation()
    observation["source_ref"] = ""
    parity = _build([_eval_row()], [observation])
    assert parity["grain_parity_status"] == "FAIL"
    assert parity["source_ref_mismatches"]


def test_suffix_only_source_ref_fails_closed() -> None:
    observation = _observation()
    observation["source_ref"] = "x2_gate_outputs.json"
    parity = _build([_eval_row()], [observation])
    assert parity["grain_parity_status"] == "FAIL"
    assert parity["source_ref_mismatches"]


def test_missing_digest_fails_even_if_legacy_flag_is_false() -> None:
    observation = _observation()
    observation["artifact_digest"] = ""
    parity = _build(
        [_eval_row()],
        [observation],
        compare_artifact_digests=False,
    )
    assert parity["grain_parity_status"] == "FAIL"
    assert parity["artifact_digest_comparison_required"] is True
    assert parity["artifact_digest_mismatches"][0]["reason"] == "missing_or_invalid_sha256"


def test_missing_observation_bundle_id_fails_closed() -> None:
    observation = _observation()
    observation["runtime_exhaust_bundle_id"] = ""
    parity = _build([_eval_row()], [observation])
    assert parity["grain_parity_status"] == "FAIL"
    assert parity["runtime_exhaust_bundle_mismatches"][0]["reason"] == (
        "missing_bundle_identity"
    )


def test_missing_top_level_identity_fails_closed() -> None:
    parity = build_independent_apps_eval_parity(
        run_id="",
        runtime_exhaust_bundle_id="reb-1",
        microstep_contract_digest=_CONTRACT_DIGEST,
        apps_eval_scorecard_ref="scorecard_rows.jsonl",
        l6_observation_ref="l6_microstep_observations.jsonl",
        apps_eval_rows=[_eval_row()],
        l6_observations=[_observation()],
        observation_origin=SEALED_APPS_RG_OBSERVATION_ORIGIN,
        expected_observation_bundle_id="reb-1",
        parent_run_id="parent-1",
        child_run_id="child-1",
        section_attempt_id="attempt-1",
        eval_record_id="eval-1",
        snapshot_digest=_SNAPSHOT_DIGEST,
        registry_digest=_REGISTRY_DIGEST,
    )
    assert parity["grain_parity_status"] == "FAIL"
    assert parity["identity_gaps"] == ["run_id"]


def test_bare_apps_eval_digests_are_canonicalized_at_binding_boundary() -> None:
    eval_row = _eval_row()
    eval_row["evidence_digest"] = _ARTIFACT_DIGEST.removeprefix("sha256:")
    eval_row["microstep_contract_digest"] = _CONTRACT_DIGEST.removeprefix("sha256:")
    eval_row["registry_digest"] = _REGISTRY_DIGEST.removeprefix("sha256:")
    eval_row["snapshot_digest"] = _SNAPSHOT_DIGEST.removeprefix("sha256:")

    parity = _build(
        [eval_row],
        [_observation()],
        microstep_contract_digest=_CONTRACT_DIGEST.removeprefix("sha256:"),
        registry_digest=_REGISTRY_DIGEST.removeprefix("sha256:"),
        snapshot_digest=_SNAPSHOT_DIGEST.removeprefix("sha256:"),
    )

    assert parity["grain_parity_status"] == "PASS"
    assert parity["microstep_contract_digest"] == _CONTRACT_DIGEST
    assert parity["registry_digest"] == _REGISTRY_DIGEST
    assert parity["snapshot_digest"] == _SNAPSHOT_DIGEST


def test_absolute_eval_and_repo_relative_l6_refs_bind_to_one_relative_ref(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    source_root = repo_root / "artifacts" / "run-1"
    source = source_root / "lanes" / "headline" / "x2_gate_outputs.json"
    source.parent.mkdir(parents=True)
    source.write_text("{}\n", encoding="utf-8")
    eval_row = _eval_row()
    eval_row["artifact_ref"] = source.as_posix()
    eval_row["evidence_ref"] = source.relative_to(source_root).as_posix()
    observation = _observation()
    observation["source_ref"] = source.relative_to(repo_root).as_posix()

    parity = _build(
        [eval_row],
        [observation],
        source_run_root=source_root.as_posix(),
        repository_root=repo_root.as_posix(),
    )

    assert parity["grain_parity_status"] == "PASS"
    assert parity["source_ref_mismatches"] == []


def test_eval_absolute_and_relative_ref_aliases_must_resolve_to_same_bytes(
    tmp_path: Path,
) -> None:
    source_root = tmp_path / "run"
    source_root.mkdir()
    eval_row = _eval_row()
    eval_row["artifact_ref"] = (source_root / "different.json").as_posix()
    eval_row["evidence_ref"] = "lanes/headline/x2_gate_outputs.json"

    parity = _build(
        [eval_row],
        [_observation()],
        source_run_root=source_root.as_posix(),
    )

    assert parity["grain_parity_status"] == "FAIL"
    assert any(
        row["reason"] == "apps_eval_ref_alias_mismatch"
        for row in parity["source_ref_mismatches"]
    )


@pytest.mark.parametrize(
    ("side", "field", "bad_value"),
    [
        ("apps_eval", "parent_run_id", "parent-other"),
        ("apps_eval", "child_run_id", "child-other"),
        ("apps_eval", "section_attempt_id", "attempt-other"),
        ("apps_eval", "eval_record_id", "eval-other"),
        ("apps_eval", "runtime_exhaust_bundle_id", "reb-other"),
        ("apps_eval", "microstep_contract_digest", _OTHER_DIGEST),
        ("apps_eval", "registry_digest", _OTHER_DIGEST),
        ("apps_eval", "snapshot_digest", _OTHER_DIGEST),
        ("l6", "parent_run_id", "parent-other"),
        ("l6", "child_run_id", "child-other"),
        ("l6", "section_attempt_id", "attempt-other"),
        ("l6", "runtime_exhaust_bundle_id", "reb-other"),
        ("l6", "microstep_contract_digest", _OTHER_DIGEST),
        ("l6", "registry_digest", _OTHER_DIGEST),
    ],
)
def test_every_bound_identity_mismatch_fails_closed(
    side: str,
    field: str,
    bad_value: str,
) -> None:
    eval_row = _eval_row()
    observation = _observation()
    target = eval_row if side == "apps_eval" else observation
    target[field] = bad_value

    parity = _build([eval_row], [observation])

    assert parity["grain_parity_status"] == "FAIL"
    assert any(
        mismatch["side"] == side and mismatch["field"] == field
        for mismatch in parity["row_identity_mismatches"]
    )


def test_contract_and_registry_digest_mismatch_fails_top_level() -> None:
    parity = _build(
        [_eval_row()],
        [_observation()],
        registry_digest=_OTHER_DIGEST,
    )

    assert parity["grain_parity_status"] == "FAIL"
    assert parity["top_level_identity_mismatches"][0]["field"] == (
        "microstep_contract_digest/registry_digest"
    )
