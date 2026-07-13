"""v40 RuntimeExhaust adapter for L6 shadow evaluation.

The functions in this module are pure normalizers. They read sealed runtime
evidence and produce the raw exhaust mapping consumed by
``agentic_core.L6_observability.shadow_eval.pipeline.run_6a``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

REQUIRED_V40_FIELDS: tuple[str, ...] = (
    "runtime_boundary_crossed",
    "completed_at",
    "request_id",
    "run_id",
    "parent_run_id",
    "child_run_id",
    "section_attempt_id",
    "session_id",
    "tenant_id",
    "trace_root",
    "exit_disposition_ref",
    "exit_disposition",
    "route_id",
    "execution_form",
    "terminal_class",
    "outcome_class",
    "policy_hash",
    "blueprint_hash",
    "replay_key",
    "route_contract_ref",
    "l5_certification_ref",
)


STAGE_ORDER: dict[str, int] = {
    "U0": 0,
    "L1": 1,
    "L0": 2,
    "C0": 3,
    "PA": 4,
    "L3": 5,
    "L2": 6,
    "EXIT": 7,
    "UWG": 8,
}


DEFAULT_SECTION_STAGE_BY_FILE: dict[str, str] = {
    "runtime_exhaust_bundle.json": "EXIT",
    "exit_disposition_receipt.json": "EXIT",
    "x3_disposition.json": "EXIT",
    "x2_gate_outputs.json": "EXIT",
    "x1d_llm_judge_outputs.json": "EXIT",
    "l2_output.json": "L2",
    "provider_request.json": "L2",
    "provider_response.json": "L2",
    "route_contract.json": "L0",
    "compiled_prompt_artifact.json": "PA",
    "final_evidence_contract_bridge.json": "C0",
    "l6_shadow_eval_package.json": "EXIT",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mapping(value: object) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "as_dict"):
        data = value.as_dict()
        if isinstance(data, Mapping):
            return dict(data)
    if is_dataclass(value):
        return asdict(value)
    return {
        name: getattr(value, name)
        for name in dir(value)
        if not name.startswith("_") and not callable(getattr(value, name))
    }


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def _repo_rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _first_str(*values: object) -> str:
    for value in values:
        if value not in (None, "", [], {}):
            return str(value)
    return ""


def _status_outcome(exit_doc: Mapping[str, Any], x3_doc: Mapping[str, Any]) -> tuple[str, str]:
    code = _first_str(
        x3_doc.get("x3_code"),
        x3_doc.get("disposition"),
        exit_doc.get("x3_code"),
        exit_doc.get("exit_disposition"),
        exit_doc.get("disposition"),
        "UNKNOWN",
    )
    if "ALLOW" in code or code in {"PASS", "OK"}:
        return code, "normal_success"
    if "ABSTAIN" in code:
        return code, "safe_abstain"
    if "DENY" in code or "BLOCK" in code or "FAIL" in code:
        return code, "policy_failure"
    return code, "unresolved_unknown"


def validate_v40_shadow_exhaust(raw_exhaust: Mapping[str, object]) -> tuple[bool, list[str]]:
    gaps: list[str] = []
    for field in REQUIRED_V40_FIELDS:
        value = raw_exhaust.get(field)
        if value in (None, "", [], {}):
            gaps.append(f"MISSING_{field.upper()}")
    if raw_exhaust.get("runtime_boundary_crossed") is not True:
        gaps.append("RUNTIME_BOUNDARY_NOT_CROSSED")
    if not raw_exhaust.get("exit_disposition_ref"):
        gaps.append("EXIT_DISPOSITION_MISSING")
    l5_ref = str(raw_exhaust.get("l5_certification_ref") or "").strip()
    if not l5_ref or l5_ref == "l5-cert-ref:MISSING":
        gaps.append("L5_CERT_REF_MISSING")
    artifacts = raw_exhaust.get("artifacts")
    if not isinstance(artifacts, Mapping) or not artifacts.get("sealed"):
        gaps.append("SEALED_ARTIFACTS_MISSING")
    if not raw_exhaust.get("source_lineage_manifest_ref") and not raw_exhaust.get("events"):
        gaps.append("SOURCE_LINEAGE_OR_RECORDS_MISSING")
    return not gaps, gaps


def from_core_runtime_exhaust_bundle(
    bundle: object,
    *,
    session_id: str,
    tenant_id: str,
    l5_certification_ref: str,
    policy_hash: str = "",
    blueprint_hash: str = "",
    replay_key: str = "",
    source_exhaust: list[dict[str, object]] | None = None,
    events: list[dict[str, object]] | None = None,
    artifacts: Mapping[str, object] | None = None,
) -> dict[str, object]:
    data = _mapping(bundle)
    exit_ref = _first_str(data.get("exit_disposition_ref"))
    run_id = _first_str(data.get("run_id"), "run-unknown")
    request_id = _first_str(data.get("request_id"), run_id)
    trace_root = _first_str(data.get("trace_root"), f"trace:{run_id}")
    route_contract_ref = _first_str(data.get("route_contract_ref"))
    sealed_result_ref = _first_str(data.get("sealed_result_ref"))
    gate_mesh_result_ref = _first_str(data.get("gate_mesh_result_ref"))
    runtime_refs = [str(ref) for ref in data.get("runtime_receipt_refs", []) or []]

    src = list(source_exhaust or [])
    if not src:
        refs = [
            ("route_contract", route_contract_ref, "L0"),
            ("sealed_result", sealed_result_ref, "L2"),
            ("gate_mesh", gate_mesh_result_ref, "EXIT"),
            ("exit_disposition", exit_ref, "EXIT"),
        ]
        refs.extend(("runtime_receipt", ref, "EXIT") for ref in runtime_refs)
        src = [
            {
                "source_type": source_type,
                "source_ref": ref,
                "source_hash": "sha256:"
                + hashlib.sha256(ref.encode("utf-8")).hexdigest(),
                "source_schema_version": "v40",
                "observed_stage": stage,
                "expected_stage_order": STAGE_ORDER.get(stage, -1),
                "lineage_parent_refs": [trace_root],
                "completeness_status": "COMPLETE",
                "trust_status": "TRUSTED",
            }
            for source_type, ref, stage in refs
            if ref
        ]

    ev = list(events or [])
    if not ev:
        ev = [
            {
                "event_type": "runtime_exhaust_bundle",
                "stage": "EXIT",
                "source_ref": _first_str(data.get("bundle_id"), data.get("deterministic_digest"), run_id),
                "payload_ref": _first_str(data.get("deterministic_digest"), data.get("bundle_id"), run_id),
                "trace_id": trace_root,
                "span_id": f"span:{run_id}:exit",
                "parent_span_id": None,
                "provider_lane": "code",
                "prompt_hash": "",
                "context_hash": "",
                "artifact_digest": _first_str(data.get("deterministic_digest")),
                "eval_readiness_hint": "READY",
            }
        ]

    art = dict(artifacts or {})
    if not art:
        sealed = [ref for ref in (sealed_result_ref, exit_ref) if ref]
        art = {
            "generated": sealed,
            "sealed": sealed,
            "file_hashes": {
                ref: "sha256:" + hashlib.sha256(ref.encode("utf-8")).hexdigest()
                for ref in sealed
            },
            "artifact_lineage": {ref: [trace_root] for ref in sealed},
            "missing": [],
            "orphans": [],
        }

    exit_disposition, outcome_class = _status_outcome(
        {"exit_disposition": exit_ref},
        {},
    )
    return {
        "runtime_boundary_crossed": bool(
            data.get("created_after_exit", True) and data.get("current_run_closed", True)
        ),
        "completed_at": _first_str(data.get("created_at"), _now_iso()),
        "request_id": request_id,
        "run_id": run_id,
        "parent_run_id": _first_str(data.get("parent_run_id")),
        "child_run_id": _first_str(data.get("child_run_id"), run_id),
        "section_attempt_id": _first_str(data.get("section_attempt_id")),
        "session_id": session_id,
        "tenant_id": tenant_id,
        "trace_root": trace_root,
        "exit_disposition_ref": exit_ref,
        "exit_disposition": exit_disposition,
        "route_id": _first_str(data.get("route_id"), route_contract_ref, "route:unknown"),
        "execution_form": "core_runtime_exhaust",
        "terminal_class": outcome_class,
        "outcome_class": outcome_class,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "route_contract_ref": route_contract_ref,
        "l1_plan_ref": "",
        "c0_evidence_contract_refs": [],
        "prompt_envelope_refs": [],
        "l2_artifact_refs": [sealed_result_ref] if sealed_result_ref else [],
        "source_lineage_manifest_ref": _first_str(data.get("deterministic_digest"), data.get("bundle_id")),
        "l5_certification_ref": l5_certification_ref,
        "source_exhaust": src,
        "events": ev,
        "artifacts": art,
    }


def from_section_artifacts(
    artifact_dir: Path,
    repo_root: Path,
    *,
    section_id: str,
    stage_by_file: Mapping[str, str] | None = None,
    provider_lane: str = "section_lane",
    session_id: str = "",
    tenant_id: str = "",
    l5_certification_ref: str = "",
) -> dict[str, object]:
    ad = artifact_dir.resolve()
    rr = repo_root.resolve()
    runtime_path = ad / "runtime_exhaust_bundle.json"
    if not runtime_path.is_file():
        raise FileNotFoundError(f"missing runtime_exhaust_bundle.json in {ad}")

    file_stage_map = dict(stage_by_file or DEFAULT_SECTION_STAGE_BY_FILE)
    docs = {
        name: _load_json(ad / name)
        for name in file_stage_map
        if (ad / name).is_file()
    }
    runtime_doc = docs.get("runtime_exhaust_bundle.json", {})
    exit_doc = docs.get("exit_disposition_receipt.json", {})
    x3_doc = docs.get("x3_disposition.json", {})
    route_doc = docs.get("route_contract.json", {})
    l2_doc = docs.get("l2_output.json", {})

    exit_disposition, outcome_class = _status_outcome(exit_doc, x3_doc)
    run_id = _first_str(runtime_doc.get("run_id"), exit_doc.get("run_id"), route_doc.get("run_id"))
    parent_run_id = _first_str(
        runtime_doc.get("parent_run_id"),
        exit_doc.get("parent_run_id"),
        route_doc.get("parent_run_id"),
    )
    child_run_id = _first_str(runtime_doc.get("child_run_id"), run_id)
    section_attempt_id = _first_str(
        runtime_doc.get("section_attempt_id"),
        exit_doc.get("section_attempt_id"),
        route_doc.get("section_attempt_id"),
    )
    request_id = _first_str(runtime_doc.get("request_id"), route_doc.get("request_id"))
    trace_root = _first_str(runtime_doc.get("trace_root"), exit_doc.get("trace_root"))
    policy_hash = _first_str(runtime_doc.get("policy_hash"), route_doc.get("policy_hash"), exit_doc.get("policy_hash"))
    blueprint_hash = _first_str(
        runtime_doc.get("blueprint_hash"),
        route_doc.get("blueprint_hash"),
        exit_doc.get("blueprint_hash"),
    )
    replay_key = _first_str(runtime_doc.get("replay_key"), route_doc.get("replay_key"), exit_doc.get("replay_key"))

    file_hashes = {
        _repo_rel(rr, ad / name): _sha256_file(ad / name)
        for name in docs
        if (ad / name).is_file()
    }
    generated = sorted(file_hashes)
    sealed_names = [
        "exit_disposition_receipt.json",
        "x3_disposition.json",
        "x2_gate_outputs.json",
        "x1d_llm_judge_outputs.json",
        "l2_output.json",
        "runtime_exhaust_bundle.json",
    ]
    sealed = [_repo_rel(rr, ad / name) for name in sealed_names if (ad / name).is_file()]
    missing = [_repo_rel(rr, ad / name) for name in sealed_names if not (ad / name).is_file()]

    source_exhaust: list[dict[str, object]] = []
    events: list[dict[str, object]] = []
    parent_ref = trace_root
    for name, stage in file_stage_map.items():
        path = ad / name
        if not path.is_file():
            continue
        ref = _repo_rel(rr, path)
        source_exhaust.append(
            {
                "source_type": "section_artifact",
                "source_ref": ref,
                "source_hash": file_hashes[ref],
                "source_schema_version": "v40",
                "observed_stage": stage,
                "expected_stage_order": STAGE_ORDER.get(stage, -1),
                "lineage_parent_refs": [parent_ref] if parent_ref else [],
                "completeness_status": "COMPLETE",
                "trust_status": "TRUSTED",
            }
        )
        events.append(
            {
                "event_type": f"artifact:{name}",
                "stage": stage,
                "source_ref": ref,
                "payload_ref": ref,
                "trace_id": trace_root,
                "span_id": f"{section_id}:{name}",
                "parent_span_id": parent_ref,
                "provider_lane": provider_lane,
                "prompt_hash": file_hashes.get(_repo_rel(rr, ad / "compiled_prompt_artifact.json"), ""),
                "context_hash": file_hashes.get(_repo_rel(rr, ad / "final_evidence_contract_bridge.json"), ""),
                "artifact_digest": file_hashes[ref],
                "eval_readiness_hint": "READY",
            }
        )
        parent_ref = f"{section_id}:{name}"

    return {
        "runtime_boundary_crossed": True,
        "completed_at": _first_str(
            runtime_doc.get("generated_at_utc"),
            exit_doc.get("generated_at_utc"),
            runtime_doc.get("created_at"),
            _now_iso(),
        ),
        "request_id": request_id,
        "run_id": run_id,
        "parent_run_id": parent_run_id,
        "child_run_id": child_run_id,
        "section_attempt_id": section_attempt_id,
        "session_id": session_id,
        "tenant_id": tenant_id,
        "trace_root": trace_root,
        "exit_disposition_ref": _repo_rel(rr, ad / "exit_disposition_receipt.json")
        if (ad / "exit_disposition_receipt.json").is_file()
        else "",
        "exit_disposition": exit_disposition,
        "route_id": _first_str(route_doc.get("route_id"), runtime_doc.get("route_id"), section_id),
        "execution_form": "section_lane",
        "terminal_class": outcome_class,
        "outcome_class": outcome_class,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "replay_key": replay_key,
        "route_contract_ref": _repo_rel(rr, ad / "route_contract.json") if (ad / "route_contract.json").is_file() else "",
        "l1_plan_ref": _first_str(runtime_doc.get("l1_plan_ref")),
        "c0_evidence_contract_refs": [
            _repo_rel(rr, ad / "final_evidence_contract_bridge.json")
        ]
        if (ad / "final_evidence_contract_bridge.json").is_file()
        else [],
        "prompt_envelope_refs": [
            _repo_rel(rr, ad / "compiled_prompt_artifact.json")
        ]
        if (ad / "compiled_prompt_artifact.json").is_file()
        else [],
        "l2_artifact_refs": [_repo_rel(rr, ad / "l2_output.json")] if (ad / "l2_output.json").is_file() else [],
        "source_lineage_manifest_ref": _repo_rel(rr, runtime_path),
        "l5_certification_ref": l5_certification_ref,
        "source_exhaust": source_exhaust,
        "events": events,
        "artifacts": {
            "generated": generated,
            "sealed": sealed,
            "file_hashes": file_hashes,
            "artifact_lineage": {ref: [trace_root] for ref in generated},
            "missing": missing,
            "orphans": [],
        },
        "section_context": {
            "section_id": section_id,
            "artifact_dir": _repo_rel(rr, ad),
            "l6_current_run_mutation_allowed": False,
            "l6_direct_l4_write_allowed": False,
        },
        "l2_snapshot": {
            "section_id": _first_str(l2_doc.get("section_id"), section_id),
            "status": _first_str(l2_doc.get("status"), l2_doc.get("runtime_generation_status")),
        },
    }


__all__ = [
    "DEFAULT_SECTION_STAGE_BY_FILE",
    "from_core_runtime_exhaust_bundle",
    "from_section_artifacts",
    "validate_v40_shadow_exhaust",
]
