"""apps_rg L6 microstep observability artifacts.

This adapter consumes the shared apps_rg microstep registry files and emits L6
shadow observations at the same join-key grain as apps_eval scorecard rows.
The records are post-run evidence only: no current-run mutation and no L4
write authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from agentic_core.L6_observability.shadow_eval.grain_parity import (
    build_l6_apps_eval_grain_parity,
)
from agentic_core.L6_observability.shadow_eval.microsteps import (
    L6MicrostepObservation,
    build_apps_eval_alignment,
    build_future_run_proposals,
    build_microstep_coverage,
    build_microstep_patterns,
    build_microstep_rca,
    build_observation_from_contract_row,
    canonical_digest,
    expand_microstep_contract,
)

L6_MICROSTEP_OBSERVATIONS_ARTIFACT = "l6_microstep_observations.jsonl"
L6_MICROSTEP_COVERAGE_ARTIFACT = "l6_microstep_coverage.json"
L6_MICROSTEP_RCA_ARTIFACT = "l6_microstep_rca.json"
L6_MICROSTEP_PATTERNS_ARTIFACT = "l6_microstep_patterns.json"
L6_MICROSTEP_FUTURE_RUN_PROPOSALS_ARTIFACT = "l6_microstep_future_run_proposals.json"
L6_APPS_EVAL_ALIGNMENT_ARTIFACT = "l6_apps_eval_alignment.json"
L6_APPS_EVAL_GRAIN_PARITY_ARTIFACT = "l6_apps_eval_grain_parity.json"

_REGISTRY_FILES = {
    "artifact_contract": "apps_rg_artifact_contract.json",
    "component_taxonomy": "apps_rg_component_taxonomy.json",
    "lane_contract": "apps_rg_lane_contract.json",
    "microstep_contract": "apps_rg_stage_microstep_contract.json",
}

_LOCAL_SECTION_ROLE_FILES = {
    "lane_l2_output": "l2_output.json",
    "lane_runtime_payload": "runtime_payload.json",
    "lane_x2_gate_outputs": "x2_gate_outputs.json",
    "lane_x1d_llm_judge_outputs": "x1d_llm_judge_outputs.json",
    "lane_x3_disposition": "x3_disposition.json",
    "lane_l6_shadow_eval_package": "l6_shadow_eval_package.json",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data


def load_apps_rg_microstep_contracts(repo_root: Path) -> dict[str, Any]:
    registry_dir = repo_root / "apps_eval" / "registries"
    if not registry_dir.is_dir():
        registry_dir = Path(__file__).resolve().parents[3] / "apps_eval" / "registries"
    return {
        name: _load_json(registry_dir / filename)
        for name, filename in _REGISTRY_FILES.items()
    }


def _repo_rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _path_digest(path: Path) -> str:
    try:
        return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _json_payload(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def _local_section_candidate(
    *,
    artifact_dir: Path,
    item: Mapping[str, Any],
    section_id: str,
) -> Path | None:
    lane = str(item.get("lane_id") or "")
    role = str(item.get("artifact_role") or "")
    if not section_id or lane != section_id:
        return None
    filename = _LOCAL_SECTION_ROLE_FILES.get(role)
    if not filename:
        return None
    candidate = artifact_dir / filename
    return candidate if candidate.is_file() else None


def _contract_candidates(
    *,
    run_root: Path,
    item: Mapping[str, Any],
    artifact_contract: Mapping[str, Any],
) -> Iterable[Path]:
    role = str(item.get("artifact_role") or "")
    lane = str(item.get("lane_id") or "")
    role_contract = artifact_contract.get("artifact_roles", {}).get(role, {})
    if not isinstance(role_contract, Mapping):
        return []
    return [
        run_root / str(rel_template).format(lane=lane)
        for rel_template in role_contract.get("relative_paths", [])
    ]


def _resolve_artifact(
    *,
    artifact_dir: Path,
    repo_root: Path,
    item: Mapping[str, Any],
    artifact_contract: Mapping[str, Any],
    section_id: str,
) -> tuple[str, str, Any]:
    local = _local_section_candidate(artifact_dir=artifact_dir, item=item, section_id=section_id)
    if local is not None:
        return _repo_rel(repo_root, local), _path_digest(local), _json_payload(local)
    for candidate in _contract_candidates(run_root=artifact_dir, item=item, artifact_contract=artifact_contract):
        if candidate.is_file():
            return _repo_rel(repo_root, candidate), _path_digest(candidate), _json_payload(candidate)
    return "", "", None


def _l6_observed_status(item: Mapping[str, Any], source_ref: str, payload: Any) -> tuple[str, str]:
    if not source_ref:
        return "MISSING", "required artifact was not resolved by L6 shadow"
    role = str(item.get("artifact_role") or "")
    if role != "lane_l6_shadow_eval_package" or not isinstance(payload, dict):
        return "OBSERVED", "artifact observed"
    mutation_keys = {
        "current_run_mutated",
        "current_run_mutation_assertion",
        "current_run_x3_mutation_assertion",
        "direct_l4_write_attempted",
        "direct_l4_write_assertion",
        "durable_write_attempted",
    }
    bad = [key for key in mutation_keys if payload.get(key) is True]
    if bad:
        return "VIOLATION", f"L6 package reported forbidden mutation/write flags: {bad}"
    return "OBSERVED", "L6 package observed as non-mutating"


def build_apps_rg_l6_microstep_observations(
    *,
    artifact_dir: Path,
    repo_root: Path,
    runtime_exhaust_bundle_id: str,
    section_id: str = "",
    parent_run_id: str = "",
    child_run_id: str = "",
    section_attempt_id: str = "",
    apps_eval_scorecard_rows: Iterable[Mapping[str, Any]] | None = None,
) -> tuple[list[L6MicrostepObservation], list[dict[str, Any]], str]:
    """Build observations and expected alignment rows for an apps_rg run."""
    contracts = load_apps_rg_microstep_contracts(repo_root)
    contract_rows = expand_microstep_contract(
        contracts["microstep_contract"],
        contracts["lane_contract"],
    )
    # This exact four-registry payload is shared with
    # apps_eval.coverage.apps_rg.apps_rg_contract_digest.  L6 uses the
    # canonical ``sha256:`` presentation while accepting no reduced subset.
    contract_digest = canonical_digest(contracts)
    eval_rows = [dict(row) for row in apps_eval_scorecard_rows or []]

    observations: list[L6MicrostepObservation] = []
    pseudo_eval_rows: list[dict[str, Any]] = []
    artifact_contract = contracts["artifact_contract"]
    for item in contract_rows:
        source_ref, digest, payload = _resolve_artifact(
            artifact_dir=artifact_dir,
            repo_root=repo_root,
            item=item,
            artifact_contract=artifact_contract,
            section_id=section_id,
        )
        status, reason = _l6_observed_status(item, source_ref, payload)
        observations.append(
            build_observation_from_contract_row(
                item,
                runtime_exhaust_bundle_id=runtime_exhaust_bundle_id,
                source_ref=source_ref,
                artifact_digest=digest,
                eval_verdict_seen="NOT_RUN",
                observed_status=status,
                decisive_reason_seen=reason,
                parent_run_id=parent_run_id,
                child_run_id=child_run_id,
                section_attempt_id=section_attempt_id,
                microstep_contract_digest=contract_digest,
                registry_digest=contract_digest,
            )
        )
        pseudo_eval_rows.append(
            {
                **dict(item),
                "row_id": "",
                "verdict": "NOT_RUN",
                "artifact_ref": source_ref,
                "evidence_digest": digest,
                "decisive_reason": reason,
                "parent_run_id": parent_run_id,
                "child_run_id": child_run_id,
                "section_attempt_id": section_attempt_id,
                "runtime_exhaust_bundle_id": runtime_exhaust_bundle_id,
                "microstep_contract_digest": contract_digest,
                "registry_digest": contract_digest,
            }
        )
    # apps_eval rows may be compared with these observations, but they may
    # never manufacture the authoritative L6 observation set.  This preserves
    # independent provenance and keeps projection-only rows advisory.
    return observations, (eval_rows or pseudo_eval_rows), contract_digest


def _write_json(path: Path, payload: Mapping[str, Any]) -> Path:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return path


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> Path:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, default=str) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )
    return path


def emit_apps_rg_l6_microstep_artifacts(
    *,
    output_dir: Path,
    artifact_dir: Path,
    repo_root: Path,
    run_id: str,
    runtime_exhaust_bundle_id: str,
    section_id: str = "",
    parent_run_id: str = "",
    child_run_id: str = "",
    section_attempt_id: str = "",
    apps_eval_scorecard_rows: Iterable[Mapping[str, Any]] | None = None,
    apps_eval_scorecard_ref: str = "",
) -> dict[str, Path]:
    """Emit L6 microstep artifacts and the apps_eval/L6 alignment file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    scorecard_rows = [dict(row) for row in apps_eval_scorecard_rows or []]
    alignment_source = "apps_eval_projection_rows" if scorecard_rows else "contract_only_pseudo_rows"
    apps_eval_rows_bound = False
    observations, eval_rows, contract_digest = build_apps_rg_l6_microstep_observations(
        artifact_dir=artifact_dir,
        repo_root=repo_root,
        runtime_exhaust_bundle_id=runtime_exhaust_bundle_id,
        section_id=section_id,
        parent_run_id=parent_run_id,
        child_run_id=child_run_id,
        section_attempt_id=section_attempt_id,
        apps_eval_scorecard_rows=scorecard_rows,
    )
    observation_dicts = [obs.to_dict() for obs in observations]
    observation_path = _write_jsonl(output_dir / L6_MICROSTEP_OBSERVATIONS_ARTIFACT, observation_dicts)
    coverage_path = _write_json(output_dir / L6_MICROSTEP_COVERAGE_ARTIFACT, build_microstep_coverage(observation_dicts))
    rca_path = _write_json(output_dir / L6_MICROSTEP_RCA_ARTIFACT, build_microstep_rca(observation_dicts))
    patterns_path = _write_json(output_dir / L6_MICROSTEP_PATTERNS_ARTIFACT, build_microstep_patterns(observation_dicts))
    proposals_path = _write_json(
        output_dir / L6_MICROSTEP_FUTURE_RUN_PROPOSALS_ARTIFACT,
        build_future_run_proposals(observation_dicts),
    )
    alignment_path = _write_json(
        output_dir / L6_APPS_EVAL_ALIGNMENT_ARTIFACT,
        build_apps_eval_alignment(
            run_id=run_id,
            runtime_exhaust_bundle_id=runtime_exhaust_bundle_id,
            microstep_contract_digest=contract_digest,
            apps_eval_scorecard_ref=apps_eval_scorecard_ref,
            l6_observation_ref=_repo_rel(repo_root, observation_path),
            apps_eval_rows=eval_rows,
            l6_observations=observation_dicts,
            alignment_source=alignment_source,
            apps_eval_rows_bound=apps_eval_rows_bound,
            registry_digest=contract_digest,
        ),
    )
    parity_path = _write_json(
        output_dir / L6_APPS_EVAL_GRAIN_PARITY_ARTIFACT,
        build_l6_apps_eval_grain_parity(
            run_id=run_id,
            runtime_exhaust_bundle_id=runtime_exhaust_bundle_id,
            microstep_contract_digest=contract_digest,
            apps_eval_scorecard_ref=apps_eval_scorecard_ref,
            l6_observation_ref=_repo_rel(repo_root, observation_path),
            apps_eval_rows=eval_rows,
            l6_observations=observation_dicts,
            alignment_source=alignment_source,
            registry_digest=contract_digest,
        ),
    )
    return {
        "l6_microstep_observations": observation_path,
        "l6_microstep_coverage": coverage_path,
        "l6_microstep_rca": rca_path,
        "l6_microstep_patterns": patterns_path,
        "l6_microstep_future_run_proposals": proposals_path,
        "l6_apps_eval_alignment": alignment_path,
        "l6_apps_eval_grain_parity": parity_path,
    }


__all__ = [
    "L6_APPS_EVAL_ALIGNMENT_ARTIFACT",
    "L6_APPS_EVAL_GRAIN_PARITY_ARTIFACT",
    "L6_MICROSTEP_COVERAGE_ARTIFACT",
    "L6_MICROSTEP_FUTURE_RUN_PROPOSALS_ARTIFACT",
    "L6_MICROSTEP_OBSERVATIONS_ARTIFACT",
    "L6_MICROSTEP_PATTERNS_ARTIFACT",
    "L6_MICROSTEP_RCA_ARTIFACT",
    "build_apps_rg_l6_microstep_observations",
    "emit_apps_rg_l6_microstep_artifacts",
    "load_apps_rg_microstep_contracts",
]
