from __future__ import annotations

import json
from pathlib import Path

from apps_eval.coverage import apps_rg_contract_digest
from apps_rg.runtime.shadow.l6_microstep_observability import (
    build_apps_rg_l6_microstep_observations,
    emit_apps_rg_l6_microstep_artifacts,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _write(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_apps_rg_l6_microsteps_expand_contract_and_observe_section_lane(tmp_path: Path) -> None:
    _write(tmp_path / "l2_output.json", {"runtime_generation_status": "REAL_LLM"})
    _write(tmp_path / "runtime_payload.json", {"proof_pool_metadata": {}})
    _write(tmp_path / "x2_gate_outputs.json", {"gates": [{"gate_id": "g", "pass": True}]})
    _write(tmp_path / "x1d_llm_judge_outputs.json", {"judges": [{"provider_key": "openai", "pass": True}]})
    _write(tmp_path / "x3_disposition.json", {"x3_code": "X3_ALLOW"})
    _write(tmp_path / "l6_shadow_eval_package.json", {"offline_only": True, "current_run_mutated": False})

    observations, eval_rows, contract_digest = build_apps_rg_l6_microstep_observations(
        artifact_dir=tmp_path,
        repo_root=_repo_root(),
        runtime_exhaust_bundle_id="reb-1",
        section_id="headline",
    )
    rows = [observation.to_dict() for observation in observations]
    headline_rows = [row for row in rows if row["lane_id"] == "headline"]

    assert len(rows) == 136
    assert len(eval_rows) == 136
    assert contract_digest.startswith("sha256:")
    assert contract_digest.removeprefix("sha256:") == apps_rg_contract_digest().removeprefix(
        "sha256:"
    )
    assert len(headline_rows) == 10
    assert all(row["observed_status"] == "OBSERVED" for row in headline_rows)
    assert all(row["current_run_mutation_assertion"] is False for row in rows)
    assert all(row["l4_write_assertion"] is False for row in rows)
    assert all(row["future_run_only"] is True for row in rows)
    assert all(row["microstep_contract_digest"] == contract_digest for row in rows)
    assert all(row["registry_digest"] == contract_digest for row in rows)


def test_apps_rg_l6_microstep_artifacts_include_alignment(tmp_path: Path) -> None:
    paths = emit_apps_rg_l6_microstep_artifacts(
        output_dir=tmp_path,
        artifact_dir=tmp_path,
        repo_root=_repo_root(),
        run_id="run-1",
        runtime_exhaust_bundle_id="reb-1",
        section_id="headline",
    )

    alignment = json.loads(paths["l6_apps_eval_alignment"].read_text(encoding="utf-8"))
    coverage = json.loads(paths["l6_microstep_coverage"].read_text(encoding="utf-8"))

    assert alignment["rows_expected"] == 134
    assert alignment["missing_in_l6"] == []
    assert alignment["authority_mismatch"] is False
    assert alignment["registry_digest"] == alignment["microstep_contract_digest"]
    assert coverage["required_rows_seen"] == 134
    assert coverage["coverage_complete"] is False
    assert coverage["missing_required"] == 134
