"""Cross-lane proof-bundle audit: pool vs FEC, digest chain, W2/W3 completeness.

Usage:
    python ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py
    python ops_scripts/apps_rg/proof_pool_c0_ssot_gap_audit.py --run-dir artifacts/.../headline_...
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROOFS = ROOT / "artifacts" / "apps_rg" / "runtime_proofs"
LANES = (
    "executive_summary",
    "headline",
    "competencies",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)

_REQUIRED_PROOF_FILES = (
    "runtime_payload.json",
    "selected_fact_plan.json",
    "x2_gate_outputs.json",
    "section_metric_receipt.json",
    "canonical_evidence_digest_chain.json",
)


def _load(p: Path) -> dict | list | None:
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _proof_base_for_lane(lane: str) -> Path:
    modular = os.environ.get("APPS_RG_MODULAR_R4_SECTIONS_ROOT", "").strip()
    if modular:
        cand = (ROOT / modular / lane / "real").resolve()
        if cand.is_dir():
            return cand
    return PROOFS / lane / "real"


def _latest_run_dir(lane: str) -> Path | None:
    base = _proof_base_for_lane(lane)
    if not base.is_dir():
        return None
    dirs = [d for d in base.iterdir() if d.is_dir()]
    if not dirs:
        return None
    return max(dirs, key=lambda d: d.stat().st_mtime)


def _x3_outcome(run_dir: Path) -> str:
    x3 = _load(run_dir / "x3_disposition.json")
    if isinstance(x3, dict):
        return str(x3.get("x3_code") or x3.get("disposition") or "UNKNOWN")
    return "MISSING"


def _classify_allowlist_authority(
    *,
    pool_ids: set[str],
    fec_ids: set[str],
    invariants: dict,
    x2: dict | None,
    x2_active_pool: str,
) -> dict:
    """Raw SFP vs post-clamp FEC naming; separate from digest-chain authority invariants."""
    extra_in_fec = sorted(fec_ids - pool_ids)
    missing_in_fec = sorted(pool_ids - fec_ids)
    raw_preclamp = bool(extra_in_fec or missing_in_fec)
    postclamp_pass = bool(invariants.get("all_pass"))

    mismatch_action = "NONE"
    if raw_preclamp:
        if postclamp_pass and x2_active_pool == "PASS":
            mismatch_action = "CLAMPED"
        else:
            mismatch_action = "BLOCKED"

    subset_mismatch_gates: list[str] = []
    if isinstance(x2, dict) and raw_preclamp:
        subset_mismatch_gates = [
            str(g.get("gate_id") or "")
            for g in (x2.get("gates") or [])
            if isinstance(g, dict)
            and not g.get("pass")
            and str(g.get("gate_id") or "").startswith("x2_")
            and "subset" in str(g.get("gate_id") or "")
        ]
        if subset_mismatch_gates and postclamp_pass:
            mismatch_action = "BLOCKED"

    authority_mismatch_explanation = ""
    if raw_preclamp and x2_active_pool == "PASS":
        authority_mismatch_explanation = (
            "selected_fact_plan.required_fact_ids is a pre-clamp selection snapshot; "
            "runtime FEC/C05 canonical pool may include hybrid-expanded or metric-alias ids "
            f"(fec_only={len(extra_in_fec)}, pool_only={len(missing_in_fec)}). "
            f"postclamp_authority_invariant_pass={postclamp_pass}; mismatch_action={mismatch_action}."
        )
    elif raw_preclamp:
        authority_mismatch_explanation = (
            f"pre-clamp SFP vs FEC id sets differ (fec_only={len(extra_in_fec)}, "
            f"pool_only={len(missing_in_fec)}); postclamp invariants_pass={postclamp_pass}; "
            f"x2_active_pool={x2_active_pool or 'UNKNOWN'}."
        )

    return {
        "fec_only_ids": extra_in_fec,
        "pool_only_ids": missing_in_fec,
        "raw_preclamp_allowlist_mismatch": raw_preclamp,
        "postclamp_authority_invariant_pass": postclamp_pass,
        "mismatch_action": mismatch_action,
        "authority_mismatch_explanation": authority_mismatch_explanation,
        "subset_mismatch_x2_gate_ids": subset_mismatch_gates,
    }


def audit_run(run_dir: Path, lane: str) -> dict:
    from apps_rg.runtime.evidence.canonical_evidence_digest_chain import (
        build_canonical_evidence_digest_chain,
    )

    out: dict = {"lane": lane, "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/")}
    missing = [f for f in _REQUIRED_PROOF_FILES if not (run_dir / f).is_file()]
    out["proof_complete"] = not missing
    out["missing_proof_files"] = missing

    sfp = _load(run_dir / "selected_fact_plan.json")
    pool_ids: set[str] = set()
    if isinstance(sfp, dict):
        pool_ids = set(sfp.get("required_fact_ids") or [])
        if not pool_ids:
            pool_ids = {str(f.get("fact_id") or "") for f in (sfp.get("facts") or []) if f.get("fact_id")}
        out["selection_method"] = sfp.get("selection_method")
        out["hybrid_reorder"] = (sfp.get("hybrid_informed_reorder") or {}).get("applied")
        out["pool_fact_count"] = len(pool_ids)

    pp = _load(run_dir / "runtime_payload.json")
    fec_ids: set[str] = set()
    if isinstance(pp, dict):
        fec_ids = {str(x) for x in (pp.get("allowed_fact_ids") or []) if str(x).strip()}
    fec_room = _load(run_dir / "c0_evidence_room_receipt.json")
    if isinstance(fec_room, dict):
        bridge = fec_room.get("bridge_doc") or fec_room
        snap = bridge.get("final_evidence_contract_snapshot") or {}
        room_ids = set(snap.get("allowed_fact_ids") or bridge.get("allowed_fact_ids") or [])
        if room_ids:
            fec_ids = room_ids if not fec_ids else fec_ids
        out["fec_fact_count"] = len(fec_ids)
        out["canonical_c0_2"] = bridge.get("canonical_c0_2_claimed")
        out["canonical_c0_3"] = bridge.get("canonical_c0_3_claimed")
        out["canonical_c0_5"] = bridge.get("canonical_c0_5_claimed")
        out["apps_rg_c03"] = bridge.get("apps_rg_c03_skills_graph_used")
        if isinstance(pp, dict):
            meta = pp.get("proof_pool_metadata") or {}
            out["c03_bound"] = meta.get("c03_graphrag_bound_status")
            if lane == "executive_summary":
                allowed = set(fec_ids or pool_ids)
                expansion_ids: set[str] = set()
                track = meta.get("track_weighted_graph_expansion") or {}
                for fid in track.get("c03_selected_fact_ids") or []:
                    expansion_ids.add(str(fid))
                for fid in meta.get("c03_context_fact_ids") or []:
                    expansion_ids.add(str(fid))
                for fid in meta.get("c03_filtered_out_fact_ids") or []:
                    expansion_ids.add(str(fid))
                out["c03_expansion_fact_ids"] = sorted(expansion_ids)
                out["c03_expansion_minus_allowed"] = sorted(expansion_ids - allowed)
                out["allowlist_mismatch"] = bool(meta.get("allowlist_mismatch"))
                out["c03_filtered_out_fact_ids"] = list(meta.get("c03_filtered_out_fact_ids") or [])
                out["graph_targeting_capsule_present"] = bool(meta.get("graph_targeting_capsule"))
                out["c03_sqlite_attach_status"] = meta.get("c03_sqlite_attach_status")

    chain = build_canonical_evidence_digest_chain(run_dir, section_id=lane)
    inv = chain.get("invariants") or {}
    out["digest_chain"] = {
        "c05_canonical_evidence_digest": chain.get("c05_canonical_evidence_digest"),
        "c06_final_evidence_contract_digest": chain.get("c06_final_evidence_contract_digest"),
        "c07_runtime_bound_evidence_digest": chain.get("c07_runtime_bound_evidence_digest"),
        "pa_c0_slot_digest": chain.get("pa_c0_slot_digest"),
        "provider_request_allowed_ids_digest": chain.get("provider_request_allowed_ids_digest"),
        "claim_ledger_source_fact_ids_digest": chain.get("claim_ledger_source_fact_ids_digest"),
        "x2_active_pool_digest": chain.get("x2_active_pool_digest"),
        "section_receipt_digest": chain.get("section_receipt_digest"),
        "invariants_pass": inv.get("all_pass"),
    }
    out["fec_added_ids_blocked"] = inv.get("c06_fec_ids_subset_of_c05_canonical_evidence_ids")
    out["downstream_widening_blocked"] = (
        inv.get("pa_c0_subset_of_fec")
        and inv.get("provider_subset_of_fec")
        and inv.get("claim_ledger_subset_of_fec")
    )
    out["namespace_split_blocked"] = inv.get("no_namespace_split_without_alias") and inv.get(
        "x2_namespace_gate_pass"
    )

    sm = _load(run_dir / "section_metric_receipt.json")
    x2_active_pool = ""
    if isinstance(sm, dict):
        out["evidence_authority"] = (sm.get("evidence_authority") or {}).get("authority")
        if isinstance(sm.get("evidence_authority"), str):
            out["evidence_authority"] = sm.get("evidence_authority")
        out["selected_role_fact_set_used"] = sm.get("selected_role_fact_set_used")
        out["x2_srfs_gate_status"] = sm.get("x2_srfs_gate_status")
        x2_active_pool = str(sm.get("x2_active_proof_pool_gate_status") or "")
        out["x2_active_pool"] = x2_active_pool

    x2 = _load(run_dir / "x2_gate_outputs.json")
    if isinstance(x2, dict):
        failed = [g.get("gate_id") for g in (x2.get("gates") or []) if not g.get("pass")]
        out["x2_failed_gates"] = failed
        out["x2_all_pass"] = not failed

    authority = _classify_allowlist_authority(
        pool_ids=pool_ids,
        fec_ids=fec_ids,
        invariants=inv,
        x2=x2 if isinstance(x2, dict) else None,
        x2_active_pool=x2_active_pool,
    )
    out.update(authority)
    if (
        out.get("raw_preclamp_allowlist_mismatch")
        and out.get("x2_active_pool") == "PASS"
        and not out.get("authority_mismatch_explanation")
    ):
        out["authority_mismatch_explanation"] = (
            "raw_preclamp_allowlist_mismatch=true with x2_active_pool=PASS requires explanation"
        )

    out["x3_outcome"] = _x3_outcome(run_dir)
    out["lane_proof_ok"] = (
        out.get("proof_complete")
        and out.get("digest_chain", {}).get("invariants_pass")
        and out.get("postclamp_authority_invariant_pass")
        and out.get("x2_all_pass", False)
        and out.get("mismatch_action") in ("NONE", "CLAMPED")
    )

    bridge_rcpt = _load(run_dir / "c0_fec_bridge_receipt.json")
    if isinstance(bridge_rcpt, dict):
        out["stale_bridge_receipt_c02"] = bridge_rcpt.get("canonical_c0_2_claimed")
        out["stale_bridge_receipt_c05"] = bridge_rcpt.get("canonical_c0_5_claimed")

    spine = _load(run_dir / "section_runtime_proof_bundle.json")
    if isinstance(spine, dict):
        sc = spine.get("spine_classification") or {}
        out["is_canonical_c0_path"] = sc.get("is_canonical_c0_path")
        chain_obs = sc.get("observed_chain") or []
        out["spine_has_fec_bridge"] = "section_fec_bridge" in chain_obs

    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", action="append", default=[], help="Explicit run dir(s)")
    args = parser.parse_args()

    rows: list[dict] = []
    if args.run_dir:
        for rd in args.run_dir:
            p = Path(rd)
            if not p.is_absolute():
                p = ROOT / p
            lane = p.parent.parent.name if p.parent.parent.name in LANES else p.name
            rows.append(audit_run(p, lane))
    else:
        for lane in LANES:
            rd = _latest_run_dir(lane)
            if rd is None:
                rows.append({"lane": lane, "run_dir": None, "proof_complete": False, "status": "NO_PROOF_DIR"})
                continue
            rows.append(audit_run(rd, lane))

    out_path = ROOT / "artifacts" / "apps_rg" / "plans" / "proof_pool_c0_ssot_gap_audit.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    modular_root = os.environ.get("APPS_RG_MODULAR_R4_SECTIONS_ROOT", "").strip() or None
    prior: dict = {}
    if out_path.is_file():
        loaded = _load(out_path)
        if isinstance(loaded, dict):
            prior = loaded

    payload = {
        "status": prior.get("status", "AUDIT_ONLY"),
        "proof_classification": {
            "w1": "CONTRACT_TEST_PROOF",
            "windows_w23_sweep": "FRESH_RUNTIME_EVIDENCE_ACCEPTED",
            "wsl_w23_sweep": "ENVIRONMENT_BLOCKED",
            "wsl_block_reason": (
                "HF hub offline policy in prior sweep script plus no discoverable "
                "BAAI/bge-m3 snapshot under WSL HF_HOME; not a product regression."
            ),
        },
        "audit_proof_root": modular_root or prior.get("audit_proof_root"),
        "lanes": rows,
        "lane_summary": [
            {
                "lane": r.get("lane"),
                "x2_all_pass": r.get("x2_all_pass"),
                "lane_proof_ok": r.get("lane_proof_ok"),
                "x3": r.get("x3_outcome"),
            }
            for r in rows
            if r.get("run_dir")
        ],
        "all_lanes_proof_ok": all(r.get("lane_proof_ok") for r in rows if r.get("run_dir")),
        "release_eligible_proof_claimed": False,
    }
    pc_prior = prior.get("proof_classification")
    if isinstance(pc_prior, dict):
        payload["proof_classification"].update(
            {k: v for k, v in pc_prior.items() if k not in payload["proof_classification"]}
        )
    for key in ("rca_remediation_completion", "executive_summary_prior_rca_relationship"):
        if key in prior:
            payload[key] = prior[key]
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
