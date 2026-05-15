"""Deterministic X2 gates for DOCX manifest evidence (filesystem-only manifest; no docx emission)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.assembly.final_resume_x2 import (
    CANONICAL_ASSEMBLED_SECTION_ORDER,
    GENERATED_LANE_IDS,
    LOCKED_EMBEDDED_ORDER_IDS,
    LOCKED_INVARIANT_IDS,
    GateResult,
)


def _add(
    out: list[GateResult],
    gate_id: str,
    ok: bool,
    observed: Any,
    thresh: Any = None,
    fail: str | None = None,
) -> None:
    out.append(
        GateResult(
            gate_id=gate_id,
            gate_type="deterministic",
            pass_=ok,
            observed_value=observed,
            threshold=thresh,
            failure_reason=None if ok else fail,
        ),
    )


def run_docx_manifest_x2_gates(
    *,
    repo_root: Path,
    manifest_blob: dict[str, Any],
    final_resume_blob: dict[str, Any],
    final_resume_json_path: Path,
    planned_docx_abs: Path,
) -> list[GateResult]:
    _ = repo_root
    gates: list[GateResult] = []

    _add(
        gates,
        "x2_docx_manifest_source_final_resume_present",
        final_resume_json_path.is_file(),
        str(final_resume_json_path),
        "path exists",
    )

    src = manifest_blob.get("sources")
    mf_hash = src.get("final_resume_hash") if isinstance(src, dict) else None
    fr_hash = final_resume_blob.get("final_resume_hash")
    _add(gates, "x2_docx_manifest_final_resume_hash_matches", mf_hash == fr_hash, mf_hash, fr_hash)

    blob_order = [
        str(s.get("section_id"))
        for s in (final_resume_blob.get("sections") or [])
        if isinstance(s, dict)
    ]
    mo_raw = manifest_blob.get("section_render_order")
    mo_raw = mo_raw if isinstance(mo_raw, list) else []
    mo = [str(x) for x in mo_raw]
    canon = list(CANONICAL_ASSEMBLED_SECTION_ORDER)
    _add(gates, "x2_docx_manifest_section_order_matches_final_resume", mo == blob_order and mo == canon, mo, canon)

    profiles_raw = manifest_blob.get("section_profiles")
    profiles = profiles_raw if isinstance(profiles_raw, list) else []
    by_sid = {str(p.get("section_id")): p for p in profiles if isinstance(p, dict) and p.get("section_id")}
    set_ok = set(by_sid.keys()) == set(canon)
    _add(gates, "x2_docx_manifest_all_sections_mapped", set_ok, sorted(by_sid.keys()), canon)

    gen_refs_raw = manifest_blob.get("generated_sections_render_refs")
    gen_refs = gen_refs_raw if isinstance(gen_refs_raw, dict) else {}
    gen_ok = True
    gd = ""
    for sid in GENERATED_LANE_IDS:
        ref = gen_refs.get(sid)
        if not isinstance(ref, dict) or not ref:
            gen_ok = False
            gd = f"missing refs for generated {sid}"
            break
    _add(gates, "x2_docx_manifest_generated_refs_present", gen_ok, gd or "ok")

    lock_refs_raw = manifest_blob.get("locked_sections_render_refs")
    inv_refs_raw = manifest_blob.get("locked_invariants_render_refs")
    lock_refs = lock_refs_raw if isinstance(lock_refs_raw, dict) else {}
    inv_refs = inv_refs_raw if isinstance(inv_refs_raw, dict) else {}

    lk_ok = True
    lx = ""
    for sid in LOCKED_EMBEDDED_ORDER_IDS:
        ref = lock_refs.get(sid)
        if not isinstance(ref, dict) or not ref:
            lk_ok = False
            lx = f"missing refs for locked narrative {sid}"
            break
    for inv in LOCKED_INVARIANT_IDS:
        ref = inv_refs.get(inv)
        if not isinstance(ref, dict) or not ref:
            lk_ok = False
            lx = f"missing refs for invariant {inv}"
            break
    _add(gates, "x2_docx_manifest_locked_refs_present", lk_ok, lx or "ok")

    guar = manifest_blob.get("guarantees")
    g_ok = isinstance(guar, dict)
    nr = g_ok and guar.get("no_rewrite") is True
    _add(gates, "x2_docx_manifest_no_rewrite", nr, guar)

    pcm = guar.get("provider_calls_made") if isinstance(guar, dict) else None
    _add(gates, "x2_docx_manifest_no_provider_calls", pcm is False, pcm, False)

    qm = guar.get("qwen_calls_made") if isinstance(guar, dict) else None
    _add(gates, "x2_docx_manifest_no_qwen_calls", qm is False, qm, False)

    jm = guar.get("judge_calls_made") if isinstance(guar, dict) else None
    _add(gates, "x2_docx_manifest_no_judge_calls", jm is False, jm, False)

    pr_raw = manifest_blob.get("planned_output_docx")
    pr = pr_raw if isinstance(pr_raw, dict) else {}
    docx_created = pr.get("docx_created")
    _add(
        gates,
        "x2_docx_manifest_docx_not_created",
        docx_created is False,
        {"docx_created": docx_created, "path_exists_on_disk": planned_docx_abs.exists()},
        False,
        None if docx_created is False else "manifest must not claim docx emission",
    )

    pop = pr.get("output_docx_planned_path")
    sd = isinstance(pop, str) and len(pop.strip()) > 0
    _add(gates, "x2_docx_manifest_output_path_declared", sd, pop, "non-empty posix path string")

    sm_ok = True
    sx = ""
    for sid in CANONICAL_ASSEMBLED_SECTION_ORDER:
        prof = by_sid.get(sid) or {}
        sm = prof.get("style_mapping") if isinstance(prof, dict) else None
        if not isinstance(sm, dict):
            sm_ok = False
            sx = f"{sid}: missing style_mapping dict"
            break
        if not str(sm.get("paragraph_primary_style") or "").strip():
            sm_ok = False
            sx = f"{sid}: missing paragraph_primary_style"
            break
        if "bullet_list_style_external_id" not in sm:
            sm_ok = False
            sx = f"{sid}: missing bullet_list_style_external_id"
            break
        h = sm.get("section_heading_outline_level")
        if not isinstance(h, int) or not 1 <= h <= 6:
            sm_ok = False
            sx = f"{sid}: invalid section_heading_outline_level {h}"
            break

    bm_raw = manifest_blob.get("bullet_style_mapping_registry")
    bm = bm_raw if isinstance(bm_raw, dict) else {}
    for ref_key in ("resume_standard_bullet", "competencies_category_bullet", "skills_inline_plain"):
        if ref_key not in bm:
            sm_ok = False
            sx = f"bullet_style_mapping_registry missing {ref_key}"
            break
    _add(
        gates,
        "x2_docx_manifest_style_mapping_complete",
        sm_ok,
        sx or "ok",
        "profiles + bullet registry",
    )

    return gates


def gates_all_pass(results: list[GateResult]) -> bool:
    return all(r.pass_ for r in results)


def failures(results: list[GateResult]) -> list[str]:
    return [r.gate_id for r in results if not r.pass_]


def gate_records_to_blob(
    gates: list[GateResult],
    *,
    evaluated_at_utc: str,
    all_pass_res: bool,
    failed_gate_ids_res: list[str],
) -> dict[str, Any]:
    return {
        "gate_family": "docx_manifest_x2",
        "evaluated_at_utc": evaluated_at_utc,
        "all_pass": all_pass_res,
        "failed_gate_ids": failed_gate_ids_res,
        "gates": [g.to_dict() for g in gates],
    }
