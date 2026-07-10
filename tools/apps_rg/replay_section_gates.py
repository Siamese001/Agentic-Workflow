#!/usr/bin/env python3
"""Offline replay of the competencies deterministic post-LLM tail + X2 gates — ZERO API.

Plan: typed-edge-role-facet-guardrails-a6f3d2 (the "#1 unlock").

WHY: validating a *post-generation* fix (bundle binding, min-term backfill, keyword
budget, X2 gate logic) does NOT require a new live generation. The slow, billed,
non-deterministic step is the LLM call; everything after the raw model output is
deterministic Python. This harness replays a SAVED ``raw_model_output.txt`` through
the real repair functions + the real ``run_competencies_x2_gates`` in seconds, with
no API calls.

SCOPE: validates the *deterministic tail* (parse -> repairs -> X2 gates). It does NOT
exercise X1D judges or the X3 disposition, and it does NOT validate *pre-generation*
changes (prompt text, evidence-pack contents, selection) — those change the LLM input
and need one live regen. The final batched live regen remains authoritative; this
harness is the fast inner loop that gets the post-gen code correct before spending it.

The repair sequence mirrors ``competencies_lane_execution.run_competencies_lane_execution``
lines ~338-441 (minus audit-file ``record_*`` writes). If that sequence changes, update
here — a one-line divergence is caught by the authoritative live regen.

USAGE:
    python tools/apps_rg/replay_section_gates.py \\
      --section competencies \\
      --raw-output artifacts/w2_comp_fix5/raw_model_output.txt \\
      --target-company "Anthropic" \\
      --target-role "Manager of Applied AI Architecture, Partnerships" \\
      --jd apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt \\
      --manual-brief tests/fixtures/apps_rg/anthropic_manager_applied_ai_architecture_partnerships_briefing.md

Exit code 0 = all X2 gates pass; 1 = one or more fail (gate list printed).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _read_text(path: str) -> str:
    p = Path(path)
    if not p.is_absolute():
        p = REPO_ROOT / p
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def replay_competencies(args: argparse.Namespace, raw_output_path: str) -> int:
    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane
    from apps_rg.runtime.sections.companion_lane_context import (
        build_c0_proof_support_blob,
        build_resume_support_blob,
        load_companion_context,
    )
    from apps_rg.runtime.sections.competencies_capability_projection import (
        finalize_competencies_v3_output,
    )
    from apps_rg.runtime.sections.competencies_lane_runtime import (
        backfill_graph_bundle_min_terms,
        build_runtime_payload,
        canonicalize_competency_terms_for_proof,
        coerce_structured_competencies_resume_support,
        collapse_duplicate_competency_terms,
        collect_employment_bullets,
        dedupe_structured_competency_terms,
        expand_structured_competencies_min_two_terms,
        normalize_parsed_output,
        parse_model_json,
        prune_claim_ledger_bullet_paste,
        rebuild_claim_ledger_from_competencies,
        reduce_competency_keyword_stuffing,
        repair_structured_competencies_source_facts,
    )
    from apps_rg.runtime.sections.competencies_v3_contract import sync_categories_competencies
    from apps_rg.runtime.sections.competency_capability_evidence import (
        augment_bound_category_family_terms,
        stamp_competency_bundle_bindings,
    )
    from apps_rg.runtime.validators.competencies_x2 import run_competencies_x2_gates

    # Load JD/brief file CONTENT into the args fields the front-spine U0 reads
    # (args.jd_text / args.briefing) — the CLI does this during U0 intake; the harness
    # must too or briefing_validate_or_raise rejects the section_regen front spine.
    jd_text = _read_text(args.jd) if getattr(args, "jd", "") else ""
    briefing = _read_text(args.manual_brief) if getattr(args, "manual_brief", "") else ""
    args.jd_text = jd_text
    args.briefing = briefing

    # 1. Reconstruct context deterministically (same as lane_execution; local, no API).
    pool, _base, base_path, base_hash, _front = load_section_proof_for_lane(
        section_id="competencies",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    bullet_rows = pool.bullet_rows
    allowed_fact_ids = pool.allowed_fact_ids
    selected_fact_plan = pool.selected_fact_plan
    pp_meta = pool.proof_pool_metadata
    bullet_lowers = [str(r.get("claim_text") or "").lower() for r in bullet_rows]
    companion_context = load_companion_context()
    resume_blob = build_resume_support_blob(bullet_rows, companion_context)
    c0_proof_blob = build_c0_proof_support_blob(bullet_rows)
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        target_title=str(args.target_role or ""),
        target_company=str(args.target_company or ""),
        jd_text=jd_text,
        briefing=briefing,
    )

    # 2. Parse the SAVED raw output (no API call).
    raw = _read_text(raw_output_path)
    if not raw.strip():
        print(f"REPLAY_ERROR: empty/missing raw output at {raw_output_path}")
        return 2
    parsed, parse_err = parse_model_json(raw)
    if parsed is None:
        print(f"REPLAY_ERROR: raw output did not parse: {parse_err}")
        return 2
    parsed = normalize_parsed_output(parsed, runtime_payload, allowed_fact_ids)

    # 3. Deterministic repair sequence (mirrors lane_execution 338-441, minus record_* audit writes).
    sync_categories_competencies(parsed)
    collapse_duplicate_competency_terms(parsed, bullet_rows, resume_blob)
    repair_structured_competencies_source_facts(
        parsed, allowed_fact_ids=allowed_fact_ids, resume_support_blob_lower=c0_proof_blob
    )
    coerce_structured_competencies_resume_support(
        parsed, bullet_rows, c0_proof_blob, bullet_lowers, allowed_fact_ids=allowed_fact_ids
    )
    dedupe_structured_competency_terms(parsed)
    reduce_competency_keyword_stuffing(parsed)
    canonicalize_competency_terms_for_proof(parsed, allowed_fact_ids=allowed_fact_ids)
    coerce_structured_competencies_resume_support(
        parsed, bullet_rows, c0_proof_blob, bullet_lowers, allowed_fact_ids=allowed_fact_ids
    )
    dedupe_structured_competency_terms(parsed)
    expand_structured_competencies_min_two_terms(
        parsed,
        bullet_rows=bullet_rows,
        allowed_fact_ids=allowed_fact_ids,
        resume_support_blob_lower=c0_proof_blob,
        bullet_texts_lower=bullet_lowers,
    )
    rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)
    prune_claim_ledger_bullet_paste(parsed)

    skill_rows_by_id: dict = {}
    allowed_skill_ids: set = set()
    for sid in pp_meta.get("c03_selected_skill_ids") or []:
        if str(sid).strip():
            allowed_skill_ids.add(str(sid).strip())
    for row in pp_meta.get("selected_skill_rows") or []:
        if isinstance(row, dict):
            sk = str(row.get("skill_id") or "").strip()
            if sk:
                skill_rows_by_id[sk] = row
                allowed_skill_ids.add(sk)
    parsed = finalize_competencies_v3_output(
        parsed,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=allowed_skill_ids,
        skill_rows_by_id=skill_rows_by_id,
        resume_support_blob_lower=c0_proof_blob,
    )
    if pp_meta.get("competency_capability_bundle_consumption"):
        packet = pp_meta.get("competency_capability_section_packet")
        _pkt = packet if isinstance(packet, dict) else None
        stamp_competency_bundle_bindings(parsed.get("categories") or [], packet=_pkt)
        stamp_competency_bundle_bindings(parsed.get("competencies") or [], packet=_pkt)
        augment_bound_category_family_terms(
            parsed.get("categories") or [], packet=_pkt, allowed_fact_ids=allowed_fact_ids
        )
        augment_bound_category_family_terms(
            parsed.get("competencies") or [], packet=_pkt, allowed_fact_ids=allowed_fact_ids
        )
        backfill_graph_bundle_min_terms(parsed)
        rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)

    # 4. Run the real X2 gates (deterministic).
    competencies = list((parsed or {}).get("competencies") or [])
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    gates = run_competencies_x2_gates(
        competencies=competencies,
        parsed_output=parsed,
        claim_ledger=claim_ledger,
        jd_text=jd_text,
        briefing_text=briefing,
        bullet_texts_lower=bullet_lowers,
        resume_support_blob=resume_blob,
        c0_proof_blob=c0_proof_blob,
        allowed_fact_ids=allowed_fact_ids,
        runtime_generation_status="REAL_LLM",
        proof_pool_metadata=pp_meta,
        raw_output=json.dumps(parsed, sort_keys=True, separators=(",", ":")),
    )

    # 5. Report.
    # These gates depend on artifacts the offline harness does NOT build (the section
    # input-usage ledger, the FEC active-pool digest, the full provider request record).
    # They are provenance/plumbing gates, not competency-content gates, and they pass in
    # the live run. The harness cannot model them faithfully without re-running the lane's
    # artifact-emission, so they are reported separately and EXCLUDED from the verdict.
    # The authoritative live regen validates them.
    HARNESS_UNMODELED_GATES = {
        "x2_section_input_usage_ledger_present",
        "x2_jd_used_as_required_targeting_input",
        "x2_briefing_used_as_required_context_input",
        "x2_title_company_used_as_required_positioning_input",
        "x2_no_non_evidence_inputs_as_claim_evidence",
        "x2_input_usage_accounting_consistent",
        "x2_active_pool_digest_matches_fec_digest",
    }
    modeled = [g for g in gates if g.gate_id not in HARNESS_UNMODELED_GATES]
    fails = [g for g in modeled if not getattr(g, "pass_", True)]
    unmodeled_fails = [
        g for g in gates if g.gate_id in HARNESS_UNMODELED_GATES and not getattr(g, "pass_", True)
    ]
    print(f"\n=== REPLAY competencies X2 gates ({len(modeled)} modeled / {len(gates)} total) ===")
    print("category term counts: ", end="")
    for c in competencies:
        if isinstance(c, dict):
            print(f"{(c.get('category_label') or '?')[:24]}={len(c.get('terms') or [])} ", end="")
    print()
    if unmodeled_fails:
        print(
            f"(not modeled offline — confirm via live regen: "
            f"{', '.join(g.gate_id for g in unmodeled_fails)})"
        )
    if not fails:
        print(
            f"RESULT: ALL {len(modeled)} MODELED CONTENT/STRUCTURE GATES PASS ✓ "
            "(offline; confirm end-to-end with one live regen)"
        )
        return 0
    print(f"RESULT: {len(fails)} MODELED GATE(S) FAIL:")
    for g in fails:
        print(f"  - {g.gate_id}: {str(g.observed_value)[:140]}")
    return 1


def main() -> int:
    from apps_rg.__main__ import _build_parser

    pre = argparse.ArgumentParser(add_help=False)
    pre.add_argument("--raw-output", required=True, help="Path to a saved raw_model_output.txt to replay")
    known, rest = pre.parse_known_args()

    parser = _build_parser()
    args = parser.parse_args(rest)
    section = getattr(args, "section", "") or "competencies"
    if section != "competencies":
        print(f"REPLAY_ERROR: only --section competencies supported so far (got {section!r})")
        return 2
    return replay_competencies(args, known.raw_output)


if __name__ == "__main__":
    raise SystemExit(main())
