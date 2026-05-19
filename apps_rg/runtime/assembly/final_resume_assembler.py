"""Assemble final_resume.json from rollup + locked copy manifest + canonical base resume (no LLM/registry)."""

from __future__ import annotations



from datetime import datetime, timezone

import json

from pathlib import Path

from typing import Any



from apps_rg.runtime.aggregation.cross_section_x2 import (

    cross_section_fail_gate_ids,

    cross_section_gates_all_pass,

    run_cross_section_x2_gates,

)

from apps_rg.runtime.aggregation.preflight import (

    AggregationPreflightError,

    assert_preflight_pass,

    run_aggregation_preflight,

)

from apps_rg.runtime.aggregation.coherent_rollup_policy import evaluate_coherent_rollup_policy
from apps_rg.runtime.aggregation.review_lane_policy import evaluate_review_lane_policy
from apps_rg.runtime.aggregation.run_fingerprint import build_fingerprint_from_rollup
from apps_rg.runtime.aggregation.warn_policy import (
    cross_section_product_pass,
    evaluate_warn_policy,
)

from apps_rg.runtime.aggregation.section_sealed_index import (

    build_extended_source_artifact_refs,

    build_section_sealed_index,

)

from apps_rg.runtime.assembly.final_resume_manifest import (

    FinalResumePaths,

    build_assembly_manifest,

    resolve_default_paths,

)

from apps_rg.runtime.assembly.final_resume_x2 import (

    CANONICAL_ASSEMBLED_SECTION_ORDER,

    GENERATED_LANE_IDS,

    LOCKED_EMBEDDED_ORDER_IDS,

    LOCKED_INVARIANT_IDS,

    canonical_json_sorted,

    failures,

    gates_all_pass,

    run_final_resume_x2_gates,

    sha256_utf8,

)

from apps_rg.runtime.locked_copy.locked_copy_manifest import find_repo_root, sha256_hex

from apps_rg.runtime.render.resume_export_enrich import verbatim_identity_from_base_resume





ASSEMBLER_OBJECT_ID = "final_resume_assembled_v2"

RECEIPT_ID = "final_resume_assembly_receipt_v2"





def _resolved_run_dir(repo: Path, rel: str) -> Path:

    rel_norm = rel.replace("\\", "/")

    while rel_norm.startswith("./"):

        rel_norm = rel_norm[2:]

    return (repo / rel_norm).resolve()





def _sha256_file_digest(path: Path) -> str:

    return sha256_hex(path.read_text(encoding="utf-8"))





def assemble_final_resume(

    paths: FinalResumePaths | None = None,

    *,

    skip_preflight: bool = False,

) -> dict[str, Any]:

    paths = paths or resolve_default_paths()

    repo = paths.repo_root



    rollup_raw = paths.rollup_json.read_text(encoding="utf-8")

    rollup_blob: dict[str, Any] = json.loads(rollup_raw)



    locked_manifest_raw = paths.locked_manifest.read_text(encoding="utf-8")

    locked_blob: dict[str, Any] = json.loads(locked_manifest_raw)



    base_raw = paths.base_resume.read_text(encoding="utf-8")

    base_digest = sha256_hex(base_raw)

    base_blob: dict[str, Any] = json.loads(base_raw)

    expected_locked = str(locked_blob.get("base_resume_json_hash") or "")

    if expected_locked and base_digest != expected_locked:

        msg = (

            "canonical base resume sha256 does not match locked_copy_manifest.base_resume_json_hash; "

            f"expected={expected_locked} actual={base_digest}"

        )

        raise ValueError(msg)



    fingerprint, sealed_index = build_fingerprint_from_rollup(

        repo=repo,

        rollup_blob=rollup_blob,

        base_resume_digest=base_digest,

    )



    preflight_results = run_aggregation_preflight(

        repo=repo,

        rollup_blob=rollup_blob,

        fingerprint=fingerprint,

        sealed_index=sealed_index,

    )

    if not skip_preflight:

        assert_preflight_pass(preflight_results)

    coherent_policy = evaluate_coherent_rollup_policy(
        repo=repo,
        rollup_blob=rollup_blob,
        base_resume_digest=base_digest,
    )
    if not skip_preflight and not coherent_policy.get("structural_assembly_eligible"):
        sr = coherent_policy.get("same_run_policy") or {}
        raise AggregationPreflightError(
            [
                {
                    "gate_id": "coherent_rollup_policy",
                    "pass": False,
                    "decisive_reason": str(sr.get("coherent_rollup_policy_reason") or "coherent rollup policy failed"),
                    "observed": coherent_policy,
                },
            ],
        )

    by_manifest = {

        str(s.get("section_id")): s

        for s in (locked_blob.get("sections") or [])

        if isinstance(s, dict) and s.get("section_id")

    }



    sections_out: list[dict[str, Any]] = []

    lanes = rollup_blob.get("lanes") or {}

    if not isinstance(lanes, dict):

        raise ValueError("generated_lane_rollup.lanes must be an object")



    per_lane_claim_ledger_digests: dict[str, str] = {}

    rollup_rel = paths.rel(paths.rollup_json)



    assemble_idx = 0

    for sid in CANONICAL_ASSEMBLED_SECTION_ORDER:

        if sid in GENERATED_LANE_IDS:

            lane = lanes.get(sid)

            if not isinstance(lane, dict):

                raise ValueError(f"rollup missing lane {sid}")

            rd = lane.get("latest_successful_real_artifact_path") or lane.get("rollup_source_run_dir")

            if not isinstance(rd, str) or not rd.strip():

                raise ValueError(f"lane {sid} missing latest_successful_real_artifact_path")

            run_dir = _resolved_run_dir(repo, rd)

            l2_path = run_dir / "l2_output.json"

            snapshot = json.loads(l2_path.read_text(encoding="utf-8"))

            raw_refs = lane.get("artifact_refs") or {}

            if not isinstance(raw_refs, dict):

                raw_refs = {}

            source_refs = build_extended_source_artifact_refs(

                repo,

                run_dir=run_dir,

                rollup_refs={str(k): str(v) for k, v in raw_refs.items() if v},

                rollup_json_rel=rollup_rel,

            )

            sec_hash = sha256_utf8(canonical_json_sorted(snapshot))

            section_digest = _sha256_file_digest(l2_path)

            x3_disp = source_refs.get("x3_disposition.json") or paths.rel(run_dir / "x3_disposition.json")

            disp_gen = {

                "rollup_lane_key": str(sid),

                "accepted_real_evidence_resolution": str(

                    lane.get("accepted_real_evidence_resolution") or "",

                ),

                "latest_successful_real_artifact_dir": paths.rel(run_dir),

                "x3_disposition_json": x3_disp,

                "rollup_artifact_refs": {k: v for k, v in source_refs.items() if k != "generated_lane_rollup_json"},

            }

            canon_path = run_dir / "canonical_claim_ledger_v2.json"

            if canon_path.is_file():

                per_lane_claim_ledger_digests[sid] = _sha256_file_digest(canon_path)

            elif (run_dir / "claim_ledger.json").is_file():

                per_lane_claim_ledger_digests[sid] = _sha256_file_digest(run_dir / "claim_ledger.json")



            sections_out.append(

                {

                    "assemble_order": assemble_idx,

                    "section_id": sid,

                    "section_kind": "generated_lane",

                    "l2_output_snapshot": snapshot,

                    "section_hash": sec_hash,

                    "section_digest": section_digest,

                    "source_artifact_refs": source_refs,

                    "disposition_refs": {"generated_lane": disp_gen},

                },

            )

        elif sid in LOCKED_EMBEDDED_ORDER_IDS:

            mf = by_manifest.get(sid)

            if not isinstance(mf, dict):

                raise ValueError(f"locked_copy_manifest missing section {sid}")

            copied = mf.get("copied_text")

            if not isinstance(copied, str):

                raise ValueError(f"locked section {sid} copied_text invalid")

            sec_hash = sha256_utf8(copied)

            section_digest = sec_hash

            locked_disp = {

                "locked_copy_manifest_json": paths.rel(paths.locked_manifest),

                "locked_copy_x2_gate_outputs_json": paths.rel(paths.locked_x2),

            }

            sections_out.append(

                {

                    "assemble_order": assemble_idx,

                    "section_id": sid,

                    "section_kind": "locked_copy_inline",

                    "copied_text_exact": copied,

                    "section_hash": sec_hash,

                    "section_digest": section_digest,

                    "source_artifact_refs": {

                        "locked_copy_manifest_json": paths.rel(paths.locked_manifest),

                        "canonical_base_resume_json": paths.rel(paths.base_resume),

                        "locked_manifest_section_id": sid,

                    },

                    "disposition_refs": {"locked_copy": locked_disp},

                },

            )

        else:

            raise ValueError(f"unhandled canonical section id {sid}")



        assemble_idx += 1



    locked_invariants: dict[str, Any] = {}

    for inv_id in LOCKED_INVARIANT_IDS:

        mf = by_manifest.get(inv_id)

        if not isinstance(mf, dict):

            raise ValueError(f"locked_copy_manifest missing invariant {inv_id}")

        copied = mf.get("copied_text")

        if not isinstance(copied, str):

            raise ValueError(f"invariant {inv_id} copied_text invalid")

        sec_hash = sha256_utf8(copied)

        locked_disp = {

            "locked_copy_manifest_json": paths.rel(paths.locked_manifest),

            "locked_copy_x2_gate_outputs_json": paths.rel(paths.locked_x2),

        }

        locked_invariants[inv_id] = {

            "manifest_section_id": inv_id,

            "copied_text_exact": copied,

            "section_hash": sec_hash,

            "section_digest": sec_hash,

            "source_artifact_refs": {

                "locked_copy_manifest_json": paths.rel(paths.locked_manifest),

                "canonical_base_resume_json": paths.rel(paths.base_resume),

            },

            "disposition_refs": {"locked_copy": locked_disp},

        }



    recomputed_lines: list[str] = []

    for s in sections_out:

        recomputed_lines.append(f"{s.get('section_id')}:{s.get('section_hash')}")

    for ik in LOCKED_INVARIANT_IDS:

        sub = locked_invariants.get(ik) or {}

        recomputed_lines.append(f"invariant_{ik}:{sub.get('section_hash')}")

    final_hash = sha256_utf8("\n".join(recomputed_lines))



    candidate_identity = verbatim_identity_from_base_resume(base_blob)



    final_resume: dict[str, Any] = {

        "assembled_object_id": ASSEMBLER_OBJECT_ID,

        "assembled_at_utc": datetime.now(timezone.utc).isoformat(),

        "assembler_module": "apps_rg.runtime.assembly.final_resume_assembler",

        "orchestration_id": fingerprint.get("orchestration_id"),

        "inputs": {

            "generated_lane_rollup_json": paths.rel(paths.rollup_json),

            "locked_copy_manifest_json": paths.rel(paths.locked_manifest),

            "canonical_base_resume_json": paths.rel(paths.base_resume),

        },

        "rollup_id": str(rollup_blob.get("rollup_id") or ""),

        "locked_manifest_id": str(locked_blob.get("manifest_id") or ""),

        "canonical_base_resume_sha256_hex": base_digest,

        "verified_base_resume_hash_matches_locked_manifest": bool(expected_locked) and base_digest == expected_locked,

        "candidate_identity": candidate_identity,

        "sections": sections_out,

        "locked_copy_invariants": locked_invariants,

        "final_resume_hash": final_hash,

        "calls": {

            "provider_calls_made": False,

            "qwen_calls_made": False,

            "judge_calls_made": False,

            "docx_rendered": False,

        },

    }



    gate_results = run_final_resume_x2_gates(

        repo=repo,

        paths=paths,

        final_resume_blob=final_resume,

        rollup_blob=rollup_blob,

        locked_manifest_blob=locked_blob,

    )



    cross_gates, kept_claims, removed_claims, rewritten_claims, overlap_decisions = run_cross_section_x2_gates(

        repo=repo,

        final_resume_blob=final_resume,

        fingerprint=fingerprint,

        sealed_index=sealed_index,

    )



    paths.output_dir.mkdir(parents=True, exist_ok=True)



    fp_path = paths.output_dir / "orchestration_fingerprint.json"

    fp_path.write_text(json.dumps(fingerprint, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



    cross_x2_path = paths.output_dir / "cross_section_x2_gate_outputs.json"

    cross_all_pass = cross_section_gates_all_pass(cross_gates)

    cross_failed = cross_section_fail_gate_ids(cross_gates)

    warn_policy = evaluate_warn_policy(cross_gates=cross_gates)

    review_policy = evaluate_review_lane_policy(
        repo=repo,
        rollup_blob=rollup_blob,
        sealed_index=sealed_index,
    )

    product_allow_claimed = bool(
        review_policy.get("summary", {}).get("product_allow_claimed")
        and gates_all_pass(gate_results)
        and cross_section_product_pass(cross_gates)
    )

    cross_x2_blob = {

        "gate_family": "final_resume_cross_section_x2",

        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),

        "all_pass": cross_all_pass,

        "failed_gate_ids": cross_failed,

        "gates": [g.to_dict() for g in cross_gates],

        "warn_policy": warn_policy,

    }

    cross_x2_path.write_text(json.dumps(cross_x2_blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    coherent_policy_path = paths.output_dir / "coherent_rollup_policy.json"

    coherent_policy_path.write_text(
        json.dumps(coherent_policy, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    review_policy_path = paths.output_dir / "review_lane_policy.json"

    review_policy_path.write_text(
        json.dumps(review_policy, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )



    kept_path = paths.output_dir / "kept_removed_claims.json"

    kept_blob = {

        "schema": "apps_rg.aggregation_kept_removed_claims.v1",

        "kept_claims": kept_claims,

        "removed_claims": removed_claims,

        "rewritten_claims": rewritten_claims,

    }

    kept_path.write_text(json.dumps(kept_blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



    overlap_path = paths.output_dir / "overlap_decisions.json"

    overlap_path.write_text(

        json.dumps(

            {"schema": "apps_rg.overlap_decisions.v1", "decisions": overlap_decisions},

            ensure_ascii=False,

            indent=2,

        )

        + "\n",

        encoding="utf-8",

    )

    from apps_rg.runtime.aggregation.cross_section_x2 import build_cross_section_warn_resolution_report

    warn_resolution = build_cross_section_warn_resolution_report(
        cross_gates=cross_gates,
        kept_claims=kept_claims,
        removed_claims=removed_claims,
        rewritten_claims=rewritten_claims,
        overlap_decisions=overlap_decisions,
    )

    (paths.output_dir / "cross_section_warn_resolution.json").write_text(
        json.dumps(warn_resolution, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )



    final_fp = paths.output_dir / "final_resume.json"

    final_fp.write_text(

        json.dumps(final_resume, ensure_ascii=False, indent=2, sort_keys=False) + "\n",

        encoding="utf-8",

    )



    gates_pass = gates_all_pass(gate_results) and cross_all_pass

    failed = failures(gate_results) + cross_failed



    manifest_fp = paths.output_dir / "final_resume_manifest.json"

    manifest_body = build_assembly_manifest(

        paths=paths,

        rollup_id=str(rollup_blob.get("rollup_id") or ""),

        rollup_generated_at_utc=str(rollup_blob.get("generated_at_utc") or ""),

        gates_passed=sum(1 for g in gate_results if g.pass_),

        gates_total=len(gate_results),

        failed_gate_ids=failed,

        final_resume_hash=final_hash,

    )

    manifest_body["orchestration_fingerprint"] = paths.rel(fp_path)

    manifest_body["cross_section_x2_gate_outputs"] = paths.rel(cross_x2_path)

    manifest_fp.write_text(

        json.dumps(manifest_body, ensure_ascii=False, indent=2, sort_keys=False) + "\n",

        encoding="utf-8",

    )



    x2_fp = paths.output_dir / "final_resume_x2_gate_outputs.json"

    x2_blob = {

        "gate_family": "final_resume_assembly_x2",

        "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),

        "all_pass": gates_all_pass(gate_results),

        "failed_gate_ids": failures(gate_results),

        "gates": [g.to_dict() for g in gate_results],

    }

    x2_fp.write_text(

        json.dumps(x2_blob, ensure_ascii=False, indent=2, sort_keys=False) + "\n",

        encoding="utf-8",

    )



    preflight_fp = paths.output_dir / "aggregation_preflight.json"

    preflight_fp.write_text(

        json.dumps(

            {

                "schema": "apps_rg.aggregation_preflight.v1",

                "results": [r.to_dict() for r in preflight_results],

                "all_pass": all(r.pass_ for r in preflight_results),

            },

            ensure_ascii=False,

            indent=2,

        )

        + "\n",

        encoding="utf-8",

    )



    receipt_fp = paths.output_dir / "final_resume_receipt.json"

    receipt_blob = {

        "receipt_id": RECEIPT_ID,

        "emitted_at_utc": datetime.now(timezone.utc).isoformat(),

        "final_resume_json": paths.rel(final_fp),

        "final_resume_manifest_json": paths.rel(manifest_fp),

        "final_resume_x2_gate_outputs_json": paths.rel(x2_fp),

        "cross_section_x2_gate_outputs_json": paths.rel(cross_x2_path),

        "orchestration_fingerprint_json": paths.rel(fp_path),

        "kept_removed_claims_json": paths.rel(kept_path),

        "overlap_decisions_json": paths.rel(overlap_path),

        "aggregation_preflight_json": paths.rel(preflight_fp),

        "coherent_rollup_policy_json": paths.rel(coherent_policy_path),

        "review_lane_policy_json": paths.rel(review_policy_path),

        "final_resume_hash": final_hash,

        "gates_all_pass": gates_pass,

        "failed_gate_ids": failed,

        "structural_x2_all_pass": gates_all_pass(gate_results),

        "cross_section_x2_all_pass": cross_all_pass,

        "cross_section_x2_structural_only": cross_all_pass,

        "cross_section_x2_product_pass": cross_section_product_pass(cross_gates),

        "warn_policy": warn_policy,

        "coherent_rollup_policy": {
            "same_run_policy": coherent_policy.get("same_run_policy"),
            "digest_coherence": coherent_policy.get("digest_coherence"),
            "structural_assembly_eligible": coherent_policy.get("structural_assembly_eligible"),
        },

        "review_lane_policy_summary": review_policy.get("summary"),

        "orchestration_fingerprint": fingerprint,

        "kept_claims": kept_claims,

        "removed_claims": removed_claims,

        "rewritten_claims": rewritten_claims,

        "overlap_decisions": overlap_decisions,

        "per_lane_claim_ledger_digests": per_lane_claim_ledger_digests,

        "product_allow_claimed": product_allow_claimed,

        "product_review_required": bool(review_policy.get("summary", {}).get("product_review_required")),

        "explicit_non_claims": [

            "Structural final_resume_x2 and cross_section WARN-permitted pass do not constitute product ALLOW.",

            "REVIEW and MOCK/plumbing-only lanes are labeled in review_lane_policy.json; not hidden.",

            "JD/briefing digests are targeting coherence only; not runtime proof.",

        ],

    }

    receipt_fp.write_text(

        json.dumps(receipt_blob, ensure_ascii=False, indent=2, sort_keys=False) + "\n",

        encoding="utf-8",

    )



    return {

        "paths": {

            "final_resume": final_fp,

            "manifest": manifest_fp,

            "x2": x2_fp,

            "receipt": receipt_fp,

            "orchestration_fingerprint": fp_path,

            "cross_section_x2": cross_x2_path,

            "kept_removed_claims": kept_path,

            "overlap_decisions": overlap_path,

        },

        "final_resume_blob": final_resume,

        "gates_all_pass": gates_pass,

        "failed_gate_ids": failed,

        "orchestration_fingerprint": fingerprint,

        "kept_claims": kept_claims,

        "removed_claims": removed_claims,

        "preflight_results": [r.to_dict() for r in preflight_results],

    }





def main() -> None:

    root = find_repo_root()

    try:

        res = assemble_final_resume(resolve_default_paths(root))

    except AggregationPreflightError as exc:

        print(f"ASSEMBLY_BLOCKED preflight:{exc}")

        raise SystemExit(1) from exc

    print(

        f"ASSEMBLY_DONE gates_all_pass={res['gates_all_pass']} "

        f"final_resume_hash={res['final_resume_blob']['final_resume_hash']} "

        f"orchestration_id={res['orchestration_fingerprint'].get('orchestration_id')}"

    )

    if not res["gates_all_pass"]:

        print(f"FAILED_GATES:{','.join(res['failed_gate_ids'])}")

        raise SystemExit(1)





if __name__ == "__main__":

    main()

