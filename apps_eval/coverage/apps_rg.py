"""apps_rg microstep scorecard extraction and coverage rollups."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from apps_eval.contracts import (
    AppOutputSnapshot,
    ComponentScorecard,
    CoverageSummary,
    ScorecardRow,
)
from apps_eval.artifacts.apps_rg_resolver import resolve_apps_rg_artifact

_REGISTRY_DIR = Path(__file__).resolve().parents[1] / "registries"
_STAGE_ORDER = {
    "U0": 0,
    "L1": 1,
    "L0": 2,
    "C0": 3,
    "PA": 4,
    "L2": 5,
    "X2": 6,
    "X1D": 7,
    "X3": 8,
    "EXIT": 9,
    "UWG": 10,
    "L6": 11,
    "PACKAGE": 12,
    "REGRESSION": 13,
}
_PASSISH = {"PASS", "NOT_APPLICABLE"}
_BLOCKING = {"FAIL", "UNKNOWN", "NOT_RUN"}
_ALLOW_X3 = {"X3_ALLOW", "X3D_ALLOW_FINISH", "X3D", "ALLOW", "ALLOW_FINISH"}
_PRESENCE_GATES = {
    "u0_run_bundle_index_present",
    "u0_runtime_package_present",
    "l1_static_plan_profile_present",
    "l0_managed_route_profile_present",
    "c0_evidence_manifest_present",
    "pa_compiled_prompt_present",
    "package_scorecard_rows_present",
    "package_component_scorecards_present",
    "package_coverage_matrix_present",
    "regression_outputs_present",
}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"expected object in {path}")
    return data


def _canonical_digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_apps_rg_contracts() -> dict[str, Any]:
    return {
        "artifact_contract": _load_json(_REGISTRY_DIR / "apps_rg_artifact_contract.json"),
        "component_taxonomy": _load_json(_REGISTRY_DIR / "apps_rg_component_taxonomy.json"),
        "lane_contract": _load_json(_REGISTRY_DIR / "apps_rg_lane_contract.json"),
        "microstep_contract": _load_json(_REGISTRY_DIR / "apps_rg_stage_microstep_contract.json"),
    }


def apps_rg_contract_digest() -> str:
    return _canonical_digest(load_apps_rg_contracts())


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _iter_microsteps(contracts: dict[str, Any]) -> list[dict[str, Any]]:
    microstep_contract = contracts["microstep_contract"]
    lane_contract = contracts["lane_contract"]
    rows: list[dict[str, Any]] = []
    rows.extend(dict(item) for item in microstep_contract.get("global_microsteps", []))
    lanes = [str(lane) for lane in lane_contract.get("generated_lanes", [])]
    for lane in lanes:
        for template in microstep_contract.get("lane_microstep_templates", []):
            item = dict(template)
            item["lane_id"] = lane
            item["microstep_id"] = str(item.pop("microstep_id_template")).format(lane=lane)
            item["gate_id"] = str(item.get("gate_id") or "").format(lane=lane)
            rows.append(item)
    rows.extend(dict(item) for item in microstep_contract.get("cross_run_microsteps", []))
    return sorted(rows, key=lambda row: (_STAGE_ORDER.get(str(row.get("stage_id")), 99), str(row.get("lane_id", "")), str(row.get("microstep_id"))))


def _path_digest(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _json_payload(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None


def _string_digest(value: Any) -> str:
    return _canonical_digest(value) if value not in (None, "") else ""


def _resolve_snapshot_index(snapshot: AppOutputSnapshot, role: str, lane: str) -> tuple[str, str, str, Any]:
    index = snapshot.artifact_index or {}
    keys = [role, f"{lane}:{role}" if lane else ""]
    for key in keys:
        if not key:
            continue
        value = index.get(key)
        if value in (None, "", [], {}):
            continue
        first = _as_list(value)[0]
        return str(first), str(first), _string_digest(value), value
    return "", "", "", None


def _resolve_planned_eval_artifact(planned: dict[str, Any], role: str) -> tuple[str, str, str, Any]:
    value = planned.get(role)
    if value in (None, "", [], {}):
        return "", "", "", None
    first = _as_list(value)[0]
    return str(first), "planned_apps_eval_emit", _string_digest(value), value


def _resolve_file_artifact(
    *,
    root: Path | None,
    role: str,
    lane: str,
    artifact_contract: dict[str, Any],
) -> tuple[str, str, str, Any]:
    if root is None:
        return "", "", "", None
    role_contract = artifact_contract.get("artifact_roles", {}).get(role, {})
    for rel_template in role_contract.get("relative_paths", []):
        rel = str(rel_template).format(lane=lane)
        candidate = (root / rel).resolve()
        if candidate.is_file():
            payload = _json_payload(candidate) if candidate.suffix.lower() == ".json" else None
            return candidate.as_posix(), rel, _path_digest(candidate), payload
    return "", "", "", None


def _resolve_artifact(
    *,
    snapshot: AppOutputSnapshot,
    role: str,
    lane: str,
    artifact_contract: dict[str, Any],
    planned_eval_artifacts: dict[str, Any],
) -> tuple[str, str, str, Any]:
    planned_ref, planned_evidence, planned_digest, planned_payload = _resolve_planned_eval_artifact(planned_eval_artifacts, role)
    if planned_ref:
        return planned_ref, planned_evidence, planned_digest, planned_payload

    index_ref, index_evidence, index_digest, index_payload = _resolve_snapshot_index(snapshot, role, lane)
    if index_ref:
        return index_ref, index_evidence, index_digest, index_payload

    root = Path(snapshot.run_root).resolve() if snapshot.run_root else None
    file_ref, file_evidence, file_digest, file_payload = _resolve_file_artifact(
        root=root,
        role=role,
        lane=lane,
        artifact_contract=artifact_contract,
    )
    if file_ref:
        return file_ref, file_evidence, file_digest, file_payload
    return "", "", "", None


def _x2_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    if payload is None:
        return "UNKNOWN", "x2 gate artifact exists but could not be parsed", None, "readable JSON with gate results"
    if isinstance(payload, list):
        gates = payload
        failed = [gate.get("gate_id") for gate in gates if isinstance(gate, dict) and gate.get("pass") is False]
        return ("FAIL", f"x2 failed gates: {failed}", failed, "no failed gates") if failed else ("PASS", "x2 gates passed", len(gates), "all pass")
    if isinstance(payload, dict):
        gates = payload.get("gates")
        failed = payload.get("failed_gates") or payload.get("x2_failed_gate_ids")
        if isinstance(gates, list):
            failed_from_gates = [gate.get("gate_id") for gate in gates if isinstance(gate, dict) and gate.get("pass") is False]
            failed = failed or failed_from_gates
        if isinstance(failed, list) and failed:
            return "FAIL", f"x2 failed gates: {failed}", failed, "no failed gates"
        if payload.get("all_pass") is False:
            return "FAIL", "x2 all_pass is false", payload.get("all_pass"), True
        if gates or payload.get("all_pass") is True or payload.get("x2_failed") == 0:
            return "PASS", "x2 gates passed", payload.get("x2_failed", 0), 0
    return "UNKNOWN", "x2 gate verdict could not be determined", payload, "deterministic pass/fail fields"


def _x1d_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    if payload is None:
        return "UNKNOWN", "x1d artifact exists but could not be parsed", None, "readable JSON with judge results"
    judges = payload
    if isinstance(payload, dict):
        overall = str(payload.get("overall") or payload.get("verdict") or payload.get("x1d_overall") or "").upper()
        if overall in {"PASS", "FAIL", "WARN", "UNKNOWN"}:
            return ("PASS", "x1d overall passed", overall, "PASS") if overall == "PASS" else ("FAIL", f"x1d overall {overall}", overall, "PASS")
        judges = payload.get("judges") or payload.get("judge_results") or payload.get("results")
    if isinstance(judges, list) and judges:
        failed = [
            row.get("provider_key") or row.get("judge_id") or idx
            for idx, row in enumerate(judges)
            if isinstance(row, dict) and row.get("pass") is False
        ]
        unknown = [
            row.get("provider_key") or row.get("judge_id") or idx
            for idx, row in enumerate(judges)
            if isinstance(row, dict) and row.get("pass") is None and not row.get("verdict")
        ]
        if failed:
            return "FAIL", f"x1d failed judges: {failed}", failed, "all judges pass"
        if unknown:
            return "UNKNOWN", f"x1d unknown judges: {unknown}", unknown, "all judges known"
        return "PASS", "x1d judge rows passed", len(judges), "all pass"
    return "UNKNOWN", "x1d judge verdict could not be determined", payload, "judge verdict rows"


def _x3_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    if payload is None:
        return "UNKNOWN", "x3 artifact exists but could not be parsed", None, "readable JSON with x3 code"
    code = ""
    if isinstance(payload, dict):
        code = str(payload.get("x3_code") or payload.get("disposition") or payload.get("x3_disposition") or "").strip()
    elif isinstance(payload, str):
        code = payload.strip()
    if not code or code.upper() == "UNKNOWN":
        return "UNKNOWN", "x3 code missing or UNKNOWN", code, "earned X3 code"
    if code in _ALLOW_X3:
        return "PASS", "x3 disposition evidence is allow/finish", code, sorted(_ALLOW_X3)
    return "WARN", f"x3 disposition is non-allow review/block code: {code}", code, sorted(_ALLOW_X3)


def _l6_non_mutating_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    if payload is None:
        return "UNKNOWN", "l6 artifact exists but could not be parsed", None, "readable JSON with non-mutation assertions"
    if not isinstance(payload, dict):
        return "UNKNOWN", "l6 artifact is not an object", payload, "object"
    mutation_flags = {
        "current_run_mutated": payload.get("current_run_mutated"),
        "current_run_mutation_assertion": payload.get("current_run_mutation_assertion"),
        "current_run_x3_mutation_assertion": payload.get("current_run_x3_mutation_assertion"),
        "direct_l4_write_attempted": payload.get("direct_l4_write_attempted"),
        "direct_l4_write_assertion": payload.get("direct_l4_write_assertion"),
        "durable_write_attempted": payload.get("durable_write_attempted"),
    }
    bad = {key: value for key, value in mutation_flags.items() if value is True}
    if bad:
        return "FAIL", f"l6 mutation/write assertions failed: {bad}", bad, "all false"
    if payload.get("offline_only") is True or payload.get("future_run_only") is True or payload.get("future_run_only_assertion") is True:
        return "PASS", "l6 package is non-mutating/future-run-only", mutation_flags, "non-mutating"
    return "UNKNOWN", "l6 package lacks non-mutation proof fields", mutation_flags, "non-mutating fields"


def _uwg_validation_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    if payload is None:
        return "UNKNOWN", "uwg validation artifact exists but could not be parsed", None, "validation_status PASS"
    if isinstance(payload, dict):
        inner = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
        status = str(inner.get("validation_status") or "").strip().upper()
        if status == "PASS":
            return "PASS", "uwg validation receipt passed", status, "PASS"
        if status:
            return "FAIL", f"uwg validation receipt status {status}", status, "PASS"
    return "UNKNOWN", "uwg validation status missing", payload, "validation_status PASS"


def _uwg_commit_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    if payload is None:
        return "UNKNOWN", "uwg commit artifact exists but could not be parsed", None, "committed receipt with output_hash"
    if isinstance(payload, dict):
        inner = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
        status = str(inner.get("commit_status") or "").strip().upper()
        output_hash = str(inner.get("output_hash") or inner.get("output_hash_sha256") or "").strip()
        receipt_id = str(inner.get("commit_receipt_id") or "").strip()
        validation_ref = str(inner.get("uwg_validation_receipt_ref") or "").strip()
        committed = status in {"COMMITTED", "ADMITTED"} and bool(output_hash and receipt_id and validation_ref)
        if committed:
            return (
                "PASS",
                "uwg commit receipt is bound to the generated resume artifact",
                {
                    "commit_status": status,
                    "commit_receipt_id": receipt_id,
                    "output_hash_present": bool(output_hash),
                    "uwg_validation_receipt_ref": validation_ref,
                },
                "COMMITTED with output_hash and validation ref",
            )
        return (
            "FAIL" if status else "UNKNOWN",
            "uwg commit receipt is missing required binding fields",
            {
                "commit_status": status,
                "commit_receipt_id": receipt_id,
                "output_hash_present": bool(output_hash),
                "uwg_validation_receipt_ref": validation_ref,
            },
            "COMMITTED with output_hash and validation ref",
        )
    return "UNKNOWN", "uwg commit artifact is not an object", payload, "object"


def _trace_reconciliation_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    if payload is None:
        return "UNKNOWN", "trace reconciliation artifact exists but could not be parsed", None, "readable JSON"
    if not isinstance(payload, dict):
        return "UNKNOWN", "trace reconciliation artifact is not an object", payload, "object"
    verdict = str(payload.get("trace_verdict") or "").strip()
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else {}
    observed = {
        "trace_verdict": verdict,
        "otel_snapshot_available": payload.get("otel_snapshot_available"),
        "local_provider_attempt_span_count": payload.get("local_provider_attempt_span_count"),
        "otel_provider_attempt_span_count": payload.get("otel_provider_attempt_span_count"),
        "fail_count": summary.get("fail_count"),
        "warn_count": summary.get("warn_count"),
    }
    if verdict == "TRACE_RECONCILED":
        return "PASS", "trace reconciliation completed without mismatch", observed, "TRACE_RECONCILED"
    if verdict in {"TRACE_PARTIAL", "TRACE_UNAVAILABLE"}:
        return "WARN", f"trace reconciliation is {verdict}", observed, "TRACE_RECONCILED"
    if verdict == "TRACE_MISMATCH":
        return "FAIL", "trace reconciliation found an OTel/local receipt mismatch", observed, "TRACE_RECONCILED"
    return "UNKNOWN", "trace reconciliation verdict missing or unknown", observed, "TRACE_RECONCILED"


def _dict_payload(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    inner = payload.get("payload")
    if isinstance(inner, dict):
        merged = dict(payload)
        merged.update(inner)
        return merged
    return payload


def _bool_field(data: dict[str, Any], *keys: str) -> bool | None:
    for key in keys:
        if key in data and isinstance(data.get(key), bool):
            return bool(data[key])
    return None


def _first_present(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _count_nonempty(value: Any) -> int:
    if isinstance(value, dict):
        return sum(1 for key, item in value.items() if key and item not in (None, "", [], {}))
    if isinstance(value, list):
        return sum(1 for item in value if item not in (None, "", [], {}))
    return 1 if value not in (None, "", [], {}) else 0


def _l1_schema_bound_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    data = _dict_payload(payload)
    if data is None:
        return "UNKNOWN", "l1 profile exists but could not be parsed as an object", payload, "schema-bound L1 profile object"
    explicit = _bool_field(data, "schema_bound", "profile_schema_bound", "l1_schema_bound")
    observed = {
        "schema_bound": explicit,
        "schema_version": data.get("schema_version"),
        "profile_verdict": data.get("profile_verdict") or data.get("verdict") or data.get("status"),
        "support_expectation_present": _first_present(data, "support_expectation", "support_expectations", "evidence_expectations") is not None,
        "action_expectation_present": _first_present(data, "action_expectation", "action_expectations", "route_expectations") is not None,
        "route_id_present": bool(str(data.get("route_id") or "").strip()),
        "task_spec_present": bool(str(data.get("task_spec") or "").strip()),
        "query_spec_present": bool(str(data.get("query_spec") or "").strip()),
    }
    if explicit is False:
        return "FAIL", "l1 profile explicitly reports schema_bound=false", observed, "schema_bound true"
    if explicit is True or str(observed["schema_version"] or "").startswith("apps_rg."):
        return "PASS", "l1 profile is schema-bound", observed, "schema version or schema_bound true"
    if observed["route_id_present"] and observed["task_spec_present"] and observed["query_spec_present"]:
        return "PASS", "l1 plan contract binds route, task, and query", observed, "schema-bound route/task/query contract"
    return "FAIL", "l1 profile is missing schema binding fields", observed, "schema version or schema_bound true"


def _l0_dispatch_canonical_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    data = _dict_payload(payload)
    if data is None:
        return "UNKNOWN", "l0 route profile exists but could not be parsed as an object", payload, "canonical dispatch profile object"
    explicit = _bool_field(data, "canonical_dispatch", "dispatch_profile_canonical", "route_profile_canonical")
    execution_form = str(data.get("execution_form") or data.get("route_execution_form") or "").lower()
    route_id = str(data.get("route_id") or data.get("canonical_route_id") or "").strip()
    bypass = _bool_field(data, "cache_bypass", "route_bypass", "dispatch_bypass")
    observed = {
        "canonical_dispatch": explicit,
        "execution_form": execution_form,
        "route_id_present": bool(route_id),
        "cache_bypass": bypass,
    }
    if explicit is False or bypass is True:
        return "FAIL", "l0 dispatch profile reports non-canonical dispatch or bypass", observed, "canonical dispatch with no bypass"
    if explicit is True or "single" in execution_form or "integrated" in execution_form or route_id:
        return "PASS", "l0 dispatch profile is canonical", observed, "canonical dispatch evidence"
    return "FAIL", "l0 dispatch profile is missing canonical dispatch evidence", observed, "canonical dispatch evidence"


def _c0_materiality_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    data = _dict_payload(payload)
    if data is None:
        return "UNKNOWN", "c0 evidence manifest exists but could not be parsed as an object", payload, "material evidence manifest object"
    explicit = _bool_field(data, "materiality_present", "evidence_materiality_present", "has_material_evidence")
    c0_required = _bool_field(data, "c0_required")
    bypass_reason = str(data.get("c0_bypass_reason") or "").strip()
    deterministic_digest = str(data.get("deterministic_digest") or "").strip()
    support = (
        _count_nonempty(data.get("selected_facts"))
        + _count_nonempty(data.get("selected_candidates"))
        + _count_nonempty(data.get("evidence_refs"))
        + _count_nonempty(data.get("claims"))
        + _count_nonempty(data.get("facts"))
    )
    materiality_count = data.get("materiality_count")
    try:
        support += int(materiality_count or 0)
    except (TypeError, ValueError):
        pass
    observed = {
        "materiality_present": explicit,
        "support_count": support,
        "materiality_count": materiality_count,
        "c0_required": c0_required,
        "c0_bypass_reason": bypass_reason,
        "deterministic_digest_present": bool(deterministic_digest),
    }
    if explicit is False:
        return "FAIL", "c0 evidence manifest explicitly reports missing materiality", observed, "material support count > 0"
    if explicit is True or support > 0:
        return "PASS", "c0 evidence materiality is present", observed, "material support count > 0"
    if c0_required is False and bypass_reason and deterministic_digest:
        return "PASS", "c0 receipt explicitly records deterministic preloaded-context bypass", observed, "material evidence or explicit deterministic bypass"
    return "FAIL", "c0 evidence manifest is missing material support fields", observed, "material support count > 0"


def _pa_evidence_as_data_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    data = _dict_payload(payload)
    if data is None:
        return "UNKNOWN", "compiled prompt artifact exists but could not be parsed as an object", payload, "prompt assembly receipt object"
    explicit = _bool_field(data, "evidence_as_data", "evidence_as_data_bound", "pa_evidence_as_data")
    wrong_slot = _bool_field(data, "evidence_in_instruction_slot", "evidence_in_system_slot", "evidence_as_instruction")
    prompt_required = _bool_field(data, "prompt_assembly_required")
    bypass_reason = str(data.get("prompt_assembly_bypass_reason") or "").strip()
    deterministic_digest = str(data.get("deterministic_digest") or "").strip()
    slots = data.get("slots") if isinstance(data.get("slots"), dict) else {}
    evidence_slot = _first_present(data, "evidence_slot", "evidence_data", "evidence_refs") or slots.get("evidence")
    authority_slot = str(data.get("evidence_authority_slot") or data.get("authority_slot") or "").lower()
    observed = {
        "evidence_as_data": explicit,
        "evidence_in_instruction_slot": wrong_slot,
        "evidence_slot_present": evidence_slot not in (None, "", [], {}),
        "authority_slot": authority_slot,
        "prompt_assembly_required": prompt_required,
        "prompt_assembly_bypass_reason": bypass_reason,
        "deterministic_digest_present": bool(deterministic_digest),
    }
    if wrong_slot is True or authority_slot in {"instruction", "instructions", "system"}:
        return "FAIL", "prompt assembly places evidence in an authority/instruction slot", observed, "evidence bound as data"
    if explicit is True or observed["evidence_slot_present"]:
        return "PASS", "prompt assembly binds evidence as data", observed, "evidence bound as data"
    if prompt_required is False and bypass_reason and deterministic_digest:
        return "PASS", "prompt assembly receipt explicitly records deterministic no-model bypass", observed, "evidence bound as data or explicit deterministic bypass"
    return "FAIL", "prompt assembly is missing evidence-as-data binding fields", observed, "evidence bound as data"


def _x2_graph_coherence_materiality_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    x2_verdict, x2_reason, x2_observed, x2_threshold = _x2_verdict(payload)
    data = _dict_payload(payload)
    if data is None:
        return x2_verdict, x2_reason, x2_observed, x2_threshold
    explicit = _bool_field(data, "graph_coherence_materiality", "material_graph_coherence", "graph_materiality_present")
    status = str(data.get("graph_coherence_status") or data.get("coherence_status") or "").upper()
    support = _count_nonempty(data.get("material_edges")) + _count_nonempty(data.get("overlap_facts")) + _count_nonempty(data.get("section_graph_links"))
    graph_gate_observed: dict[str, Any] = {}
    for gate in data.get("gates", []) if isinstance(data.get("gates"), list) else []:
        if isinstance(gate, dict) and gate.get("gate_id") == "x2_cross_section_graph_coherence":
            observed_payload = gate.get("observed")
            graph_gate_observed = observed_payload if isinstance(observed_payload, dict) else {}
            break
    if graph_gate_observed:
        status = status or str(graph_gate_observed.get("status") or "").upper()
        support += _count_nonempty(graph_gate_observed.get("unique_graph_skill_node_ids"))
        support += _count_nonempty(graph_gate_observed.get("unique_role_episode_bundle_ids"))
        support += _count_nonempty(graph_gate_observed.get("active_section_ids"))
    observed = {
        "x2_verdict": x2_verdict,
        "graph_coherence_materiality": explicit,
        "graph_coherence_status": status,
        "support_count": support,
    }
    if explicit is False or status in {"FAIL", "FAILED"}:
        return "FAIL", "cross-section graph coherence materiality failed", observed, "PASS with material graph support"
    if explicit is True or status in {"PASS", "WARN"} or support > 0 or x2_verdict == "PASS":
        return "PASS", "cross-section graph coherence materiality passed", observed, "PASS with material graph support"
    return "FAIL", "cross-section graph coherence materiality evidence is missing", observed, "PASS with material graph support"


def _l6_grain_parity_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    if payload is None:
        return "UNKNOWN", "l6 grain parity artifact exists but could not be parsed", None, "readable JSON"
    if not isinstance(payload, dict):
        return "UNKNOWN", "l6 grain parity artifact is not an object", payload, "object"
    status = str(payload.get("grain_parity_status") or "").strip().upper()
    alignment_source = str(payload.get("alignment_source") or "").strip()
    rows_bound = payload.get("apps_eval_rows_bound") is True
    observed = {
        "grain_parity_status": status,
        "alignment_source": alignment_source,
        "apps_eval_rows_bound": rows_bound,
        "missing_in_l6": payload.get("missing_in_l6"),
        "missing_in_apps_eval": payload.get("missing_in_apps_eval"),
        "verdict_mismatches": payload.get("verdict_mismatches"),
        "authority_mismatch": payload.get("authority_mismatch"),
    }
    if status == "PASS" and rows_bound:
        return "PASS", "l6 grain parity is bound to apps_eval scorecard rows", observed, "PASS with apps_eval_rows_bound"
    if alignment_source in {"contract_only_pseudo_rows", "failure_terminal_no_apps_eval_rows"}:
        return "WARN", f"l6 grain parity is {alignment_source}", observed, "apps_eval_scorecard_rows"
    if status == "FAIL":
        return "FAIL", "l6 grain parity failed", observed, "PASS"
    return "UNKNOWN", "l6 grain parity status missing or unbound", observed, "PASS with apps_eval_rows_bound"


_SEMANTIC_VALIDATORS = {
    "l1_static_plan_profile_schema_bound": _l1_schema_bound_verdict,
    "l0_dispatch_profile_canonical": _l0_dispatch_canonical_verdict,
    "c0_evidence_materiality_present": _c0_materiality_verdict,
    "pa_prompt_boundary_evidence_as_data": _pa_evidence_as_data_verdict,
    "x2_cross_section_graph_coherence_materiality": _x2_graph_coherence_materiality_verdict,
}


def _exit_verdict(payload: Any) -> tuple[str, str, Any, Any]:
    if payload is None:
        return "UNKNOWN", "exit artifact exists but could not be parsed", None, "readable JSON with whole-run exit"
    if not isinstance(payload, dict):
        return "UNKNOWN", "exit artifact is not an object", payload, "object"
    inner = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    if inner.get("exactly_one_x3") is False:
        return "FAIL", "whole-run exit exactly_one_x3 is false", inner.get("exactly_one_x3"), True
    disposition = str(
        inner.get("x3_disposition")
        or inner.get("x3_code")
        or payload.get("x3_disposition")
        or ""
    ).strip()
    if not disposition:
        return "UNKNOWN", "whole-run exit disposition missing", disposition, "non-empty disposition"
    return "PASS", "whole-run exit packet has a single disposition", {"exactly_one_x3": inner.get("exactly_one_x3"), "x3_disposition": disposition}, "single disposition"


def _evaluate_microstep(gate_id: str, artifact_ref: str, payload: Any, *, required: bool = True) -> tuple[str, float, str, str, Any, Any]:
    if not artifact_ref:
        return "FAIL", 0.0, "coverage.missing_required_artifact", "required artifact was not resolved", "", "artifact_ref"
    if gate_id in _SEMANTIC_VALIDATORS:
        verdict, reason, observed, threshold = _SEMANTIC_VALIDATORS[gate_id](payload)
    elif gate_id.endswith("_present") or gate_id in _PRESENCE_GATES:
        return "PASS", 1.0, "", "required artifact resolved", artifact_ref, "artifact_ref"
    elif "x2" in gate_id and gate_id.endswith("_pass"):
        verdict, reason, observed, threshold = _x2_verdict(payload)
    elif gate_id == "x1d_judge_result_pass":
        verdict, reason, observed, threshold = _x1d_verdict(payload)
    elif gate_id == "x3_disposition_earned":
        verdict, reason, observed, threshold = _x3_verdict(payload)
    elif gate_id == "l6_shadow_package_non_mutating":
        verdict, reason, observed, threshold = _l6_non_mutating_verdict(payload)
    elif gate_id == "exit_exactly_one_x3":
        verdict, reason, observed, threshold = _exit_verdict(payload)
    elif gate_id == "uwg_validation_receipt_pass":
        verdict, reason, observed, threshold = _uwg_validation_verdict(payload)
    elif gate_id == "uwg_commit_receipt_bound":
        verdict, reason, observed, threshold = _uwg_commit_verdict(payload)
    elif gate_id == "trace_reconciliation_consumed":
        verdict, reason, observed, threshold = _trace_reconciliation_verdict(payload)
    elif gate_id == "l6_apps_eval_grain_parity_verified":
        verdict, reason, observed, threshold = _l6_grain_parity_verdict(payload)
    else:
        verdict = "UNKNOWN" if required else "WARN"
        reason = f"no semantic validator registered for gate {gate_id}"
        observed = {"gate_id": gate_id, "artifact_ref": artifact_ref}
        threshold = "registered semantic validator or explicit presence gate"
    failure_mode = "" if verdict in {"PASS", "WARN"} else f"microstep.{gate_id}"
    return verdict, 1.0 if verdict == "PASS" else 0.5 if verdict == "WARN" else 0.0, failure_mode, reason, observed, threshold


def _row_id(suite_id: str, scenario_id: str, microstep_id: str) -> str:
    return hashlib.sha256(f"{suite_id}|{scenario_id}|{microstep_id}".encode("utf-8")).hexdigest()[:20]


def _failure_family(failure_mode: str) -> str:
    return failure_mode.split(".", 1)[0] if failure_mode else ""


def _scope_key(item: dict[str, Any]) -> str:
    lane = str(item.get("lane_id") or "")
    if lane:
        return f"lane:{lane}"
    component = str(item.get("component_id") or "")
    if component in {"apps_rg.eval_package", "apps_rg.whole_run_exit", "apps_rg.final_assembly", "apps_rg.cross_section", "apps_rg.uwg_commit"}:
        return "cross_run"
    return "global"


def _make_row(
    *,
    suite_id: str,
    app_id: str,
    scenario_id: str,
    run_id: str,
    created_at: str,
    item: dict[str, Any],
    artifact_ref: str,
    evidence_ref: str,
    evidence_digest: str,
    verdict: str,
    score: float,
    failure_mode: str,
    decisive_reason: str,
    observed_value: Any,
    threshold: Any,
    source_artifact_schema: str,
) -> ScorecardRow:
    microstep_id = str(item["microstep_id"])
    return ScorecardRow(
        suite_id=suite_id,
        scenario_id=scenario_id,
        app_id=app_id,
        row_id=_row_id(suite_id, scenario_id, microstep_id),
        microstep_id=microstep_id,
        stage_id=str(item.get("stage_id", "")),
        component_id=str(item.get("component_id", "")),
        subcomponent_id=str(item.get("subcomponent_id", "")),
        run_id=run_id,
        lane_id=str(item.get("lane_id", "")),
        gate_id=str(item.get("gate_id", "")),
        required=bool(item.get("required", True)),
        artifact_role=str(item.get("artifact_role", "")),
        artifact_ref=artifact_ref,
        evidence_ref=evidence_ref,
        evidence_digest=evidence_digest,
        verdict=verdict,
        score=round(score, 6),
        severity=str(item.get("severity", "BLOCK")),
        failure_mode=failure_mode,
        failure_family=_failure_family(failure_mode),
        observed_value=observed_value,
        threshold=threshold,
        decisive_reason=decisive_reason,
        source_system="apps_eval",
        source_artifact_schema=source_artifact_schema,
        created_at=created_at,
    )


def _rollup_group(rows: list[ScorecardRow], key: tuple[str, str, str, str]) -> ComponentScorecard:
    component_id, subcomponent_id, stage_id, lane_id = key
    required = [row for row in rows if row.required]
    pass_count = sum(1 for row in rows if row.verdict == "PASS")
    fail_count = sum(1 for row in rows if row.verdict == "FAIL")
    warn_count = sum(1 for row in rows if row.verdict == "WARN")
    unknown_count = sum(1 for row in rows if row.verdict == "UNKNOWN")
    not_run_count = sum(1 for row in rows if row.verdict == "NOT_RUN")
    blocking = sum(1 for row in rows if row.required and row.verdict in _BLOCKING)
    score = 1.0 if not required else sum(row.score for row in required) / len(required)
    return ComponentScorecard(
        suite_id=rows[0].suite_id,
        app_id=rows[0].app_id,
        scenario_id=rows[0].scenario_id,
        component_id=component_id,
        subcomponent_id=subcomponent_id,
        stage_id=stage_id,
        lane_id=lane_id,
        row_count=len(rows),
        required_count=len(required),
        pass_count=pass_count,
        fail_count=fail_count,
        warn_count=warn_count,
        unknown_count=unknown_count,
        not_run_count=not_run_count,
        blocking_failure_count=blocking,
        score=round(score, 6),
        verdict="pass" if blocking == 0 and fail_count == 0 and unknown_count == 0 and not_run_count == 0 else "fail",
    )


def _component_rollups(rows: list[ScorecardRow]) -> list[ComponentScorecard]:
    groups: dict[tuple[str, str, str, str], list[ScorecardRow]] = defaultdict(list)
    for row in rows:
        groups[(row.component_id, row.subcomponent_id, str(row.stage_id), row.lane_id)].append(row)
    return [_rollup_group(group_rows, key) for key, group_rows in sorted(groups.items())]


def _coverage_summary(rows: list[ScorecardRow], suite_id: str, app_id: str, scenario_id: str) -> CoverageSummary:
    required = [row for row in rows if row.required]
    missing = sum(1 for row in required if row.failure_mode == "coverage.missing_required_artifact")
    unknown = sum(1 for row in required if row.verdict == "UNKNOWN")
    not_run = sum(1 for row in required if row.verdict == "NOT_RUN")
    failed = sum(1 for row in required if row.verdict == "FAIL")
    passed = sum(1 for row in required if row.verdict == "PASS")
    release_blocked = any(row.verdict in _BLOCKING for row in required)
    coverage_complete = missing == 0 and unknown == 0 and not_run == 0
    return CoverageSummary(
        suite_id=suite_id,
        app_id=app_id,
        scenario_id=scenario_id,
        required_microsteps=len(required),
        emitted_rows=len(rows),
        passed_required=passed,
        failed_required=failed,
        missing_required_artifacts=missing,
        unknown_required=unknown,
        not_run_required=not_run,
        coverage_complete=coverage_complete,
        release_blocked=release_blocked,
        verdict="fail" if release_blocked or not coverage_complete else "pass",
    )


def build_apps_rg_microstep_evaluation(
    *,
    suite_id: str,
    scenario_id: str,
    snapshot: AppOutputSnapshot,
    run_id: str,
    created_at: str,
    planned_eval_artifacts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contracts = load_apps_rg_contracts()
    artifact_contract = contracts["artifact_contract"]
    planned = planned_eval_artifacts or {}
    rows: list[ScorecardRow] = []
    prior_blocked: dict[str, bool] = defaultdict(bool)

    for item in _iter_microsteps(contracts):
        role = str(item.get("artifact_role", ""))
        lane = str(item.get("lane_id", ""))
        role_contract = artifact_contract.get("artifact_roles", {}).get(role, {})
        resolved = resolve_apps_rg_artifact(
            snapshot=snapshot,
            role=role,
            lane_id=lane,
            artifact_contract=artifact_contract,
            planned_eval_artifacts=planned,
        )
        artifact_ref = resolved.artifact_ref
        evidence_ref = resolved.evidence_ref
        evidence_digest = resolved.evidence_digest
        payload = resolved.payload
        verdict, score, failure_mode, reason, observed, threshold = _evaluate_microstep(
            str(item.get("gate_id", "")),
            artifact_ref,
            payload,
            required=bool(item.get("required", True)),
        )
        scope = _scope_key(item)
        if not artifact_ref and prior_blocked[scope] and bool(item.get("required", True)):
            verdict = "NOT_RUN"
            score = 0.0
            failure_mode = "dependency.not_run"
            reason = "prior required dependency failed for this scope"
            observed = ""
            threshold = "prior dependency pass"
        if bool(item.get("required", True)) and verdict not in _PASSISH and str(item.get("severity", "BLOCK")) in {"BLOCK", "MAJOR"}:
            prior_blocked[scope] = True
        row = _make_row(
            suite_id=suite_id,
            app_id=snapshot.app_id,
            scenario_id=scenario_id,
            run_id=run_id,
            created_at=created_at,
            item=item,
            artifact_ref=artifact_ref,
            evidence_ref=evidence_ref,
            evidence_digest=evidence_digest,
            verdict=verdict,
            score=score,
            failure_mode=failure_mode,
            decisive_reason=reason,
            observed_value=observed,
            threshold=threshold,
            source_artifact_schema=str(role_contract.get("source_artifact_schema", "")),
        )
        rows.append(row)

    coverage = _coverage_summary(rows, suite_id, snapshot.app_id, scenario_id)
    components = _component_rollups(rows)
    evidence_index = [
        {
            "row_id": row.row_id,
            "microstep_id": row.microstep_id,
            "lane_id": row.lane_id,
            "artifact_role": row.artifact_role,
            "artifact_ref": row.artifact_ref,
            "evidence_ref": row.evidence_ref,
            "evidence_digest": row.evidence_digest,
            "verdict": row.verdict,
        }
        for row in rows
    ]
    return {
        "contracts": contracts,
        "contract_digest": _canonical_digest(contracts),
        "rows": rows,
        "component_scorecards": components,
        "coverage_summary": coverage,
        "evidence_index": evidence_index,
    }
