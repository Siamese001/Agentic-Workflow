"""W2/W3 canonical evidence digest chain — cross-surface digest proof for live lane runs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.evidence.canonical_section_evidence_set import (
    X2_BLOCK_ID_NAMESPACE_SPLIT,
    build_id_alias_map_from_plan,
    canonical_evidence_set_digest,
    collect_claim_ledger_source_fact_ids,
    collect_prompt_c0_fact_ids,
    detect_id_namespace_split_without_alias,
    validate_downstream_subset,
)

DIGEST_CHAIN_ARTIFACT = "canonical_evidence_digest_chain.json"


def _load_json(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _digest_ids(ids: set[str] | list[str]) -> str:
    return canonical_evidence_set_digest(ids)


def _claim_ledger_from_run(run_dir: Path) -> list[dict[str, Any]]:
    led = _load_json(run_dir / "claim_ledger.json")
    if isinstance(led, list):
        return [r for r in led if isinstance(r, dict)]
    l2 = _load_json(run_dir / "l2_output.json")
    if isinstance(l2, dict):
        cl = l2.get("claim_ledger")
        if isinstance(cl, list):
            return [r for r in cl if isinstance(r, dict)]
    return []


def _provider_allowed_ids(run_dir: Path, runtime_payload: dict[str, Any]) -> set[str]:
    pr = _load_json(run_dir / "provider_request.json")
    if isinstance(pr, dict):
        for key in ("allowed_fact_ids", "allowed_source_fact_ids"):
            vals = pr.get(key)
            if isinstance(vals, list) and vals:
                return {str(x).strip() for x in vals if str(x).strip()}
    return {str(x).strip() for x in (runtime_payload.get("allowed_fact_ids") or []) if str(x).strip()}


def _x2_active_pool_digest(run_dir: Path, runtime_payload: dict[str, Any]) -> str:
    x2 = _load_json(run_dir / "x2_gate_outputs.json")
    if isinstance(x2, dict):
        for g in x2.get("gates") or []:
            if not isinstance(g, dict):
                continue
            gid = str(g.get("gate_id") or "")
            if gid.endswith("_active_proof_pool_source_fact_ids"):
                obs = g.get("observed_value")
                if isinstance(obs, dict):
                    d = str(obs.get("canonical_evidence_set_digest") or obs.get("proof_pool_digest") or "")
                    if d:
                        return d
    return str(
        runtime_payload.get("canonical_evidence_set_digest")
        or (runtime_payload.get("proof_pool_metadata") or {}).get("canonical_evidence_set_digest")
        or ""
    )


def _section_receipt_digest(run_dir: Path) -> str:
    sm = _load_json(run_dir / "section_metric_receipt.json")
    if not isinstance(sm, dict):
        return ""
    stable = {
        "lane_id": sm.get("lane_id"),
        "canonical_evidence_set_digest": sm.get("canonical_evidence_set_digest"),
        "fec_allowed_fact_ids_digest": sm.get("fec_allowed_fact_ids_digest"),
        "x2_active_proof_pool_gate_status": sm.get("x2_active_proof_pool_gate_status"),
    }
    payload = json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_canonical_evidence_digest_chain(
    run_dir: Path,
    *,
    section_id: str,
) -> dict[str, Any]:
    """Assemble digest chain + subset invariants from a completed lane artifact dir."""
    runtime_payload = _load_json(run_dir / "runtime_payload.json")
    if not isinstance(runtime_payload, dict):
        runtime_payload = {}

    canon_doc = runtime_payload.get("canonical_section_evidence_set") or {}
    c05_ids = {str(x).strip() for x in (canon_doc.get("pool_ids_ordered") or []) if str(x).strip()}
    plan = runtime_payload.get("selected_fact_plan")
    if not c05_ids and isinstance(plan, dict):
        c05_ids = {str(x) for x in (plan.get("required_fact_ids") or []) if str(x).strip()}
        if not c05_ids:
            c05_ids = {
                str(f.get("fact_id") or "").strip()
                for f in (plan.get("facts") or [])
                if isinstance(f, dict) and f.get("fact_id")
            }
    if not c05_ids:
        sfp = _load_json(run_dir / "selected_fact_plan.json")
        if isinstance(sfp, dict):
            c05_ids = {str(x) for x in (sfp.get("required_fact_ids") or []) if str(x).strip()}
            if not c05_ids:
                c05_ids = {
                    str(f.get("fact_id") or "").strip()
                    for f in (sfp.get("facts") or [])
                    if isinstance(f, dict) and f.get("fact_id")
                }

    c06_ids = {str(x).strip() for x in (runtime_payload.get("allowed_fact_ids") or []) if str(x).strip()}
    bridge = runtime_payload.get("section_fec_bridge")
    if isinstance(bridge, dict) and bridge.get("allowed_fact_ids"):
        c06_ids = {str(x).strip() for x in bridge.get("allowed_fact_ids") if str(x).strip()}

    c07 = _load_json(run_dir / "c0_evidence_room_receipt.json")
    c07_ids = set(c06_ids)
    if isinstance(c07, dict):
        c07_doc = c07.get("c07") or {}
        if isinstance(c07_doc, dict):
            pass
        room_bridge = c07.get("bridge_doc") or c07
        if isinstance(room_bridge, dict):
            snap = room_bridge.get("final_evidence_contract_snapshot") or {}
            if isinstance(snap, dict) and snap.get("allowed_fact_ids"):
                c07_ids = {str(x) for x in snap.get("allowed_fact_ids") if str(x).strip()}

    c05_digest = str(
        runtime_payload.get("canonical_evidence_set_digest")
        or canon_doc.get("canonical_evidence_set_digest")
        or _digest_ids(c05_ids)
    )
    c06_digest = str(
        runtime_payload.get("fec_allowed_fact_ids_digest") or _digest_ids(c06_ids)
    )
    c07_digest = c06_digest if c07_ids == c06_ids else _digest_ids(c07_ids)

    pa_ids = collect_prompt_c0_fact_ids(runtime_payload)
    provider_ids = _provider_allowed_ids(run_dir, runtime_payload)
    ledger_ids = collect_claim_ledger_source_fact_ids(_claim_ledger_from_run(run_dir))

    alias_map = dict(canon_doc.get("id_alias_map") or {})
    if not alias_map:
        plan = runtime_payload.get("selected_fact_plan")
        if isinstance(plan, dict):
            alias_map = build_id_alias_map_from_plan(plan)

    mat = runtime_payload.get("fec_materialization_receipt") or {}
    narrowed = bool(mat.get("fec_narrowed_from_pool"))

    fec_subset_ok, fec_violations = validate_downstream_subset(c06_ids, c05_ids, label="fec", alias_map=alias_map)
    c07_subset_ok, c07_violations = validate_downstream_subset(c07_ids, c06_ids, label="c07", alias_map=alias_map)
    pa_ok, pa_bad = validate_downstream_subset(pa_ids, c06_ids, label="pa", alias_map=alias_map)
    prov_ok, prov_bad = validate_downstream_subset(provider_ids, c06_ids, label="provider", alias_map=alias_map)
    led_ok, led_bad = validate_downstream_subset(ledger_ids, c06_ids, label="ledger", alias_map=alias_map)

    split, split_ids = detect_id_namespace_split_without_alias(
        pool_ids=c05_ids, fec_ids=c06_ids, alias_map=alias_map
    )

    x2_digest = _x2_active_pool_digest(run_dir, runtime_payload)
    digest_match = bool(c05_digest and c06_digest and c05_digest == c06_digest)
    digest_aligned = digest_match or (narrowed and bool(mat.get("explicit_narrowing")))

    x2 = _load_json(run_dir / "x2_gate_outputs.json")
    namespace_gate_pass = True
    if isinstance(x2, dict):
        for g in x2.get("gates") or []:
            if isinstance(g, dict) and g.get("gate_id") == X2_BLOCK_ID_NAMESPACE_SPLIT:
                namespace_gate_pass = bool(g.get("pass"))

    invariants_pass = (
        fec_subset_ok
        and c07_subset_ok
        and pa_ok
        and prov_ok
        and led_ok
        and digest_aligned
        and not split
        and namespace_gate_pass
    )

    return {
        "schema_version": "canonical_evidence_digest_chain_v1",
        "section_id": section_id,
        "run_dir": str(run_dir).replace("\\", "/"),
        "c05_canonical_evidence_digest": c05_digest,
        "c06_final_evidence_contract_digest": c06_digest,
        "c07_runtime_bound_evidence_digest": c07_digest,
        "pa_c0_slot_digest": _digest_ids(pa_ids),
        "provider_request_allowed_ids_digest": _digest_ids(provider_ids),
        "claim_ledger_source_fact_ids_digest": _digest_ids(ledger_ids),
        "x2_active_pool_digest": x2_digest or c05_digest,
        "section_receipt_digest": _section_receipt_digest(run_dir),
        "c05_canonical_evidence_ids": sorted(c05_ids),
        "c06_fec_ids": sorted(c06_ids),
        "c07_bound_ids": sorted(c07_ids),
        "invariants": {
            "c06_fec_ids_subset_of_c05_canonical_evidence_ids": fec_subset_ok,
            "c07_bound_ids_subset_of_c06_fec_ids": c07_subset_ok,
            "pa_c0_subset_of_fec": pa_ok,
            "provider_subset_of_fec": prov_ok,
            "claim_ledger_subset_of_fec": led_ok,
            "digest_match_or_explicit_narrowing_receipt": digest_aligned,
            "no_namespace_split_without_alias": not split,
            "x2_namespace_gate_pass": namespace_gate_pass,
            "violations": {
                "fec_widening": fec_violations,
                "c07_widening": c07_violations,
                "pa_widening": pa_bad,
                "provider_widening": prov_bad,
                "ledger_widening": led_bad,
                "namespace_split_ids": split_ids,
            },
            "fec_narrowed_from_pool": narrowed,
            "all_pass": invariants_pass,
        },
    }


def emit_canonical_evidence_digest_chain(
    artifact_dir: Path,
    *,
    section_id: str,
) -> dict[str, Any]:
    """Write ``canonical_evidence_digest_chain.json`` and merge digests into section_metric_receipt."""
    doc = build_canonical_evidence_digest_chain(artifact_dir, section_id=section_id)
    out_path = artifact_dir / DIGEST_CHAIN_ARTIFACT
    out_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sm_path = artifact_dir / "section_metric_receipt.json"
    sm = _load_json(sm_path)
    if isinstance(sm, dict):
        sm.update(
            {
                "canonical_evidence_set_digest": doc.get("c05_canonical_evidence_digest"),
                "fec_allowed_fact_ids_digest": doc.get("c06_final_evidence_contract_digest"),
                "c07_runtime_bound_evidence_digest": doc.get("c07_runtime_bound_evidence_digest"),
                "pa_c0_slot_digest": doc.get("pa_c0_slot_digest"),
                "provider_request_allowed_ids_digest": doc.get("provider_request_allowed_ids_digest"),
                "claim_ledger_source_fact_ids_digest": doc.get("claim_ledger_source_fact_ids_digest"),
                "x2_active_pool_digest": doc.get("x2_active_pool_digest"),
                "section_receipt_digest": doc.get("section_receipt_digest"),
                "canonical_evidence_digest_chain_ref": DIGEST_CHAIN_ARTIFACT,
                "canonical_evidence_invariants_pass": doc.get("invariants", {}).get("all_pass"),
            }
        )
        sm_path.write_text(json.dumps(sm, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return doc


__all__ = [
    "DIGEST_CHAIN_ARTIFACT",
    "build_canonical_evidence_digest_chain",
    "emit_canonical_evidence_digest_chain",
]
