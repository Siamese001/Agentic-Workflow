"""Assemble final_resume.json from rollup + locked copy manifest + canonical base resume (no LLM/registry)."""

from __future__ import annotations

if __name__ == "__main__":
    raise ImportError(
        "This module is not an operator CLI entrypoint. "
        "Use: python -m apps_rg or python -m apps_rg --section <lane>"
    )

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

from apps_rg.runtime.render.resume_export_enrich import verbatim_identity_from_static_profile

from apps_rg.runtime.resume_resolution import load_candidate_static_profile_json





ASSEMBLER_OBJECT_ID = "final_resume_assembled_v2"

RECEIPT_ID = "final_resume_assembly_receipt_v2"





def _resolved_run_dir(repo: Path, rel: str) -> Path:

    rel_norm = rel.replace("\\", "/")

    while rel_norm.startswith("./"):

        rel_norm = rel_norm[2:]

    return (repo / rel_norm).resolve()





def _sha256_file_digest(path: Path) -> str:

    return sha256_hex(path.read_text(encoding="utf-8"))


def _generated_lane_assembly_gap_snapshot(section_id: str, reason: str) -> dict[str, Any]:
    """Placeholder L2 for incomplete lanes — whole-résumé judges still receive explicit gaps."""
    return {
        "runtime_generation_status": "ASSEMBLY_GAP",
        "assembly_gap": True,
        "assembly_gap_reason": reason,
        "section_id": section_id,
    }


def _sweep_undeclared_assembly_artifacts(output_dir: Path) -> None:
    """Start each assembly pass from the declared artifact contract.

    Everything in the assembly dir is derived per pass. Top-level files outside
    ASSEMBLY_ALLOWED_ARTIFACT_FILES (the same contract the X2 provider/judge
    scans enforce) and the per-pass coherence_judge_providers/ raws are removed
    so leftovers from a prior pass can never fail — or masquerade as evidence
    for — the current one. Stale run-15 provider raws failing patch_run_17's
    scans (2026-06-11) are the precedent.
    """
    import shutil

    from apps_rg.runtime.assembly.final_resume_x2 import ASSEMBLY_ALLOWED_ARTIFACT_FILES

    if not output_dir.is_dir():
        return
    for f in output_dir.iterdir():
        if f.is_file() and f.name.lower() not in ASSEMBLY_ALLOWED_ARTIFACT_FILES:
            f.unlink()
    providers_dir = output_dir / "coherence_judge_providers"
    if providers_dir.is_dir():
        shutil.rmtree(providers_dir)


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

    if paths.candidate_static_profile is not None:
        static_profile_path = paths.candidate_static_profile
        static_profile_raw = static_profile_path.read_text(encoding="utf-8")
        static_profile_blob: dict[str, Any] = json.loads(static_profile_raw)
        static_profile_digest = sha256_hex(static_profile_raw)
    else:
        static_profile_blob, static_profile_path, static_profile_digest = load_candidate_static_profile_json(
            repo_root=repo
        )

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

            gap_reason: str | None = None

            run_dir: Path | None = None

            l2_path: Path | None = None

            if not isinstance(lane, dict):

                gap_reason = f"rollup missing lane {sid}"

            else:

                rd = lane.get("latest_successful_real_artifact_path") or lane.get("rollup_source_run_dir")

                if not isinstance(rd, str) or not rd.strip():

                    gap_reason = f"lane {sid} missing latest_successful_real_artifact_path"

                else:

                    run_dir = _resolved_run_dir(repo, rd)

                    l2_path = run_dir / "l2_output.json"

                    if not l2_path.is_file():

                        gap_reason = f"lane {sid} missing l2_output.json"

            if gap_reason:

                snapshot = _generated_lane_assembly_gap_snapshot(sid, gap_reason)

                sec_hash = sha256_utf8(canonical_json_sorted(snapshot))

                section_digest = sha256_utf8(gap_reason)

                source_refs = {

                    "generated_lane_rollup_json": rollup_rel,

                    "assembly_gap_reason": gap_reason,

                }

                disp_gen = {

                    "rollup_lane_key": str(sid),

                    "assembly_gap": True,

                    "assembly_gap_reason": gap_reason,

                }

            else:

                assert run_dir is not None and l2_path is not None and isinstance(lane, dict)

                snapshot = json.loads(l2_path.read_text(encoding="utf-8"))

                sec_hash = sha256_utf8(canonical_json_sorted(snapshot))

                section_digest = _sha256_file_digest(l2_path)

            raw_refs = (lane or {}).get("artifact_refs") or {}

            if not isinstance(raw_refs, dict):

                raw_refs = {}

            if not gap_reason:

                source_refs = build_extended_source_artifact_refs(

                    repo,

                    run_dir=run_dir,

                    rollup_refs={str(k): str(v) for k, v in raw_refs.items() if v},

                    rollup_json_rel=rollup_rel,

                )

                x3_disp = source_refs.get("x3_disposition.json") or paths.rel(run_dir / "x3_disposition.json")

                disp_gen = {

                    "rollup_lane_key": str(sid),

                    "accepted_real_evidence_resolution": str(

                        lane.get("accepted_real_evidence_resolution") or "",

                    ),

                    "latest_successful_real_artifact_dir": paths.rel(run_dir),

                    "x3_disposition_json": x3_disp,

                    "rollup_artifact_refs": {

                        k: v for k, v in source_refs.items() if k != "generated_lane_rollup_json"

                    },

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



    candidate_identity = verbatim_identity_from_static_profile(static_profile_blob)



    final_resume: dict[str, Any] = {

        "assembled_object_id": ASSEMBLER_OBJECT_ID,

        "assembled_at_utc": datetime.now(timezone.utc).isoformat(),

        "assembler_module": "apps_rg.runtime.assembly.final_resume_assembler",

        "orchestration_id": fingerprint.get("orchestration_id"),

        "inputs": {

            "generated_lane_rollup_json": paths.rel(paths.rollup_json),

            "locked_copy_manifest_json": paths.rel(paths.locked_manifest),

            "canonical_base_resume_json": paths.rel(paths.base_resume),

            "candidate_static_profile_json": paths.rel(static_profile_path),

        },

        "rollup_id": str(rollup_blob.get("rollup_id") or ""),

        "locked_manifest_id": str(locked_blob.get("manifest_id") or ""),

        "canonical_base_resume_sha256_hex": base_digest,

        "candidate_static_profile_sha256_hex": static_profile_digest,

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

    from apps_rg.runtime.assembly.full_resume_llm_coherence import (
        assembly_product_release_mode,
        assembly_structural_only_mode,
        emit_full_resume_llm_coherence_review,
        full_resume_coherence_review_enabled,
    )

    import os

    product_release_mode = assembly_product_release_mode()
    coherence_required = full_resume_coherence_review_enabled()
    coherence_review: dict[str, Any] | None = None

    paths.output_dir.mkdir(parents=True, exist_ok=True)
    _sweep_undeclared_assembly_artifacts(paths.output_dir)

    if coherence_required:
        target_company = os.environ.get("APPS_RG_TARGET_COMPANY", "").strip()
        target_role = os.environ.get("APPS_RG_TARGET_ROLE", "").strip()
        lanes_raw = rollup_blob.get("lanes")
        lane_iter: list[Any] = []
        if isinstance(lanes_raw, dict):
            lane_iter = list(lanes_raw.values())
        elif isinstance(lanes_raw, list):
            lane_iter = lanes_raw
        for lane in lane_iter:
            if not isinstance(lane, dict):
                continue
            if not target_company:
                target_company = str(lane.get("target_company") or "").strip()
            if not target_role:
                target_role = str(lane.get("target_role") or "").strip()
        judge_mode = os.environ.get("APPS_RG_FULL_RESUME_COHERENCE_JUDGE_MODE", "blocked_if_unavailable").strip()
        coherence_review = emit_full_resume_llm_coherence_review(
            final_resume=final_resume,
            final_resume_path=paths.output_dir / "final_resume.json",
            output_dir=paths.output_dir,
            target_company=target_company,
            target_role=target_role,
            mode=judge_mode or "blocked_if_unavailable",
        )
        final_resume["calls"]["judge_calls_made"] = True
        final_resume["calls"]["provider_calls_made"] = True

    coherence_pass = bool(
        coherence_review and coherence_review.get("full_resume_coherence_pass") is True
    )
    final_resume["assembly_proof_semantics"] = {
        "assembly_mode": (
            "product_release_candidate" if product_release_mode else "structural_package_only"
        ),
        "structural_only": assembly_structural_only_mode(),
        "aggregate_judge_required": coherence_required,
        "aggregate_judge_executed": coherence_review is not None,
        "aggregate_judge_artifacts": {
            "full_resume_llm_coherence_review_json": (
                "full_resume_llm_coherence_review.json" if coherence_review else None
            ),
            "x1d_full_resume_judge_outputs_json": (
                "x1d_full_resume_judge_outputs.json" if coherence_review else None
            ),
        },
        "full_resume_coherence_pass": coherence_pass if coherence_review else None,
        "product_release_eligible": False,
        "explicit_non_claims": [
            "Section-level X2/X3 pass is necessary but not sufficient for product release.",
            "structural_package_only assembly may emit final_resume.json without product authorization.",
            "product_release_eligible is set false here and updated only when all product gates pass.",
        ],
    }

    gate_results = run_final_resume_x2_gates(
        repo=repo,
        paths=paths,
        final_resume_blob=final_resume,
        rollup_blob=rollup_blob,
        locked_manifest_blob=locked_blob,
        coherence_review=coherence_review,
        product_release_mode=product_release_mode,
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

    from apps_rg.runtime.aggregation.cross_section_x2 import VERDICT_FAIL
    from apps_rg.runtime.assembly.full_resume_llm_coherence import assembly_structural_only_mode

    if assembly_structural_only_mode():
        cross_all_pass = not any(g.verdict == VERDICT_FAIL for g in cross_gates)
    else:
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
        and (coherence_pass if coherence_required else False)
    )
    if isinstance(final_resume.get("assembly_proof_semantics"), dict):
        final_resume["assembly_proof_semantics"]["product_release_eligible"] = product_allow_claimed

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

        "full_resume_llm_coherence_review_json": (
            paths.rel(paths.output_dir / "full_resume_llm_coherence_review.json")
            if coherence_review is not None
            else None
        ),

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

            "Section-level X3 pass is necessary but not sufficient; full-resume aggregate judge quorum required for product_release_eligible.",

            "REVIEW and MOCK/plumbing-only lanes are labeled in review_lane_policy.json; not hidden.",

            "JD/briefing digests are targeting coherence only; not runtime proof.",

            "final_resume.json with judge_calls_made=false is structural-only or pre-aggregate-review — not product release.",

        ],

        "assembly_proof_semantics": final_resume.get("assembly_proof_semantics"),

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

        "structural_x2_all_pass": gates_all_pass(gate_results),

        "cross_section_x2_all_pass": cross_all_pass,

        "failed_gate_ids": failed,

        "orchestration_fingerprint": fingerprint,

        "kept_claims": kept_claims,

        "removed_claims": removed_claims,

        "preflight_results": [r.to_dict() for r in preflight_results],

    }
