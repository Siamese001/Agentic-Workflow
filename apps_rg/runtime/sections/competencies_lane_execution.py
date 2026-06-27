"""Canonical competencies lane runtime execution (W11-M4C / legacy burndown Phase D).

``apps_rg.runtime.sections.competencies_lane_runtime`` retains shared compile/repair helpers and
compat re-exports; product entry is ``python -m apps_rg --section competencies``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.offline_contract_status import OFFLINE_CONTRACT_STUB_RUNTIME_STATUS
from apps_rg.runtime.section_judge_policy import get_section_judge_policy


def _hydrate_dispatch_helpers() -> None:
    import apps_rg.runtime.sections.competencies_lane_runtime as _cd

    _skip = frozenset({
        "run_competencies_execution",
        "run_competencies_lane_execution",
        "run_dispatch",
        "main",
        "build_parser",
    })
    g = globals()
    for name in dir(_cd):
        if name.startswith("__") or name in _skip:
            continue
        g.setdefault(name, getattr(_cd, name))


_helpers_hydrated = False


def _ensure_helpers_hydrated() -> None:
    global _helpers_hydrated
    if _helpers_hydrated:
        return
    _hydrate_dispatch_helpers()
    _helpers_hydrated = True


def _format_sample_ids(values: Any, *, limit: int = 6) -> str:
    ids = [str(x).strip() for x in (values or []) if str(x).strip()]
    sample = ids[:limit]
    suffix = f" (+{len(ids) - limit} more)" if len(ids) > limit else ""
    return ", ".join(sample) + suffix if sample else "none"


def _format_competencies_graph_sourcing_assessment(
    graph_sufficiency_receipt: dict[str, Any],
    *,
    x2_gates: list[dict[str, Any]] | None = None,
    traversal_receipt_ref: str = "",
) -> list[str]:
    traversal = graph_sufficiency_receipt.get("traversal_sufficiency_receipt")
    traversal = traversal if isinstance(traversal, dict) else {}
    frontier = traversal.get("frontier_size_by_hop_depth")
    frontier = frontier if isinstance(frontier, dict) else {}
    comparison = traversal.get("selected_vs_rejected_candidate_comparison")
    comparison = comparison if isinstance(comparison, dict) else {}
    axes = traversal.get("role_specific_axis_coverage")
    axes = axes if isinstance(axes, dict) else {}

    gate_map = {
        str(g.get("gate_id") or ""): bool(g.get("pass"))
        for g in (x2_gates or [])
        if isinstance(g, dict)
    }
    required_gate_ids = (
        "x2_competencies_graph_traversal_sufficiency",
        "x2_competencies_graph_granularity_gates",
    )
    missing_gate_ids = [gid for gid in required_gate_ids if gid not in gate_map]
    failed_gate_ids = [gid for gid in required_gate_ids if gate_map.get(gid) is False]
    derived_ok = (
        str(traversal.get("graph_evidence_depth_status") or "").lower() == "judge_grade"
        and not (axes.get("missing_axes") or [])
        and int(traversal.get("rejected_sibling_skill_count") or 0) > 0
        and bool(graph_sufficiency_receipt.get("confidence_nonconstant"))
    )
    acceptable = (
        not failed_gate_ids and not missing_gate_ids
        if gate_map
        else derived_ok
    )
    verdict_reason = (
        "required_graph_gates_passed"
        if acceptable and gate_map
        else ("derived_receipt_signals_passed" if acceptable else "failed_or_missing_graph_gates")
    )

    return [
        "",
        "GRAPH_SOURCING_ASSESSMENT:",
        "SCHEMA_ORDER: role -> role_episode_roots -> skills -> metrics -> rejected_siblings -> confidence -> verdict",
        (
            "ROLE: "
            f"profile={traversal.get('target_role_profile') or 'unknown'} "
            f"selection_method={traversal.get('selection_method') or 'unknown'} "
            f"depth_status={traversal.get('graph_evidence_depth_status') or 'unknown'}"
        ),
        (
            "ROLE_EPISODE_ROOTS: "
            f"selected={traversal.get('selected_role_episode_root_count') or 0} "
            f"source_facts={traversal.get('selected_source_fact_count') or 0} "
            f"root_ids=[{_format_sample_ids(traversal.get('selected_role_episode_root_ids'))}] "
            f"source_fact_ids=[{_format_sample_ids(traversal.get('selected_source_fact_ids'))}]"
        ),
        (
            "SKILLS: "
            f"selected_unique={traversal.get('selected_unique_leaf_skill_count') or 0} "
            f"candidate_frontier={frontier.get('1_leaf_skill_candidates') or 0} "
            f"selected_ids=[{_format_sample_ids(traversal.get('selected_leaf_skill_ids'))}]"
        ),
        (
            "METRICS: "
            f"selected_unique={traversal.get('selected_unique_metric_count') or 0} "
            f"candidate_frontier={frontier.get('2_metric_outcome_candidates') or 0} "
            f"selected_ids=[{_format_sample_ids(traversal.get('selected_metric_outcome_ids'))}]"
        ),
        (
            "REJECTED_SIBLINGS: "
            f"skills={traversal.get('rejected_sibling_skill_count') or 0} "
            f"metrics={traversal.get('rejected_sibling_metric_count') or 0} "
            f"skill_ids=[{_format_sample_ids(traversal.get('rejected_sibling_skill_ids'))}] "
            f"metric_ids=[{_format_sample_ids(traversal.get('rejected_sibling_metric_ids'))}]"
        ),
        (
            "SELECTED_VS_REJECTED: "
            f"graph_selected_leaf_skills={comparison.get('graph_selected_leaf_skill_count') or 0} "
            f"graph_rejected_sibling_skills={comparison.get('graph_rejected_sibling_skill_count') or 0} "
            f"selector_candidates={comparison.get('selector_candidate_label_count') or 0} "
            f"selector_rejected={comparison.get('selector_rejected_neighbor_count') or 0}"
        ),
        (
            "ROLE_AXIS_COVERAGE: "
            f"covered=[{_format_sample_ids(axes.get('covered_axes'), limit=8)}] "
            f"missing=[{_format_sample_ids(axes.get('missing_axes'), limit=8)}]"
        ),
        (
            "CONFIDENCE: "
            f"nonconstant={str(bool(graph_sufficiency_receipt.get('confidence_nonconstant'))).lower()} "
            f"values=[{_format_sample_ids(graph_sufficiency_receipt.get('category_confidence_values'), limit=8)}]"
        ),
        (
            "ASSESSMENT: "
            f"{'ACCEPTABLE' if acceptable else 'NOT_ACCEPTABLE'} "
            f"reason={verdict_reason} "
            f"failed_gates=[{_format_sample_ids(failed_gate_ids, limit=4)}] "
            f"missing_gates=[{_format_sample_ids(missing_gate_ids, limit=4)}]"
        ),
        (
            "GRAPH_RECEIPT: "
            f"{traversal_receipt_ref or 'competencies_graph_traversal_sufficiency_receipt.json'}"
        ),
    ]


def run_competencies_lane_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane",
    print_output: bool = True,
) -> dict[str, Any]:
    _ensure_helpers_hydrated()
    import time as _time
    from datetime import datetime as _dt, timezone as _tz

    # W5: lane-level phase timing board. Checkpoint deltas across the major phases so a stuck or
    # failed competencies run can answer "did it die before the provider, on a generation path, on
    # the selector, on X2, on X3, or in L6?" without guessing from a console trickle. Best-effort;
    # never affects control flow.
    _phase_timings: list[dict[str, Any]] = []
    _phase_clock = {"t": _time.monotonic()}

    def _mark_phase(name: str) -> None:
        now = _time.monotonic()
        _phase_timings.append(
            {
                "phase": name,
                "duration_s": round(now - _phase_clock["t"], 4),
                "at": _dt.now(_tz.utc).isoformat(),
            }
        )
        _phase_clock["t"] = now

    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane

    pool, base, base_path, base_hash, front_spine = load_section_proof_for_lane(
        section_id="competencies",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    _mark_phase("load_section_proof_for_lane")
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
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
    )
    runtime_payload["proof_pool_metadata"] = pp_meta
    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override)
        artifact_dir.mkdir(parents=True, exist_ok=True)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    from apps_rg.runtime.section_repair_lane_integration import (
        record_deterministic_rewrite,
        record_mechanical,
        record_parse_json_retry,
        record_regen_llm,
        start_lane_repair_ledger,
    )

    start_lane_repair_ledger(
        artifact_dir, section_id="competencies", run_id=str(runtime_payload["run_id"])
    )
    (artifact_dir / "companion_generated_sections.txt").write_text(companion_context or "(none)\n", encoding="utf-8")

    from apps_rg.runtime.sections.section_generation import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )
    from apps_rg.runtime.spine.c0_fec_compose import (
        merge_compiled_prompt_artifact_fec_fields,
    )
    from apps_rg.runtime.sections.upstream_evidence_block import wire_spine_c0_fec_or_block

    blocked = wire_spine_c0_fec_or_block(
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        section_id="competencies",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
        provider=str(args.provider),
        temperature=float(args.temperature),
        max_tokens=COMPETENCIES_MAX_OUTPUT_TOKENS,
        output_filename="competencies_display.txt",
    )
    if blocked is not None:
        return blocked

    fact_lines = "\n".join(
        f"- {row['fact_id']}: {row['claim_text']}"
        + (f" | tech: {', '.join(row['technologies'])}" if row.get("technologies") else "")
        for row in bullet_rows
    )
    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_competencies_prompt(
        runtime_payload,
        companion_context=companion_context,
        fact_lines=fact_lines,
        run_id=runtime_payload["run_id"],
    )
    _mark_phase("compile_prompt")
    messages = section_compiled.artifact.messages
    compiled_prompt = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    prompt_hash = sha16(compiled_prompt)
    write_json(artifact_dir / "runtime_payload.json", runtime_payload)
    native_c03 = (pp_meta or {}).get("native_c03_final_evidence")
    if isinstance(native_c03, dict):
        write_json(artifact_dir / "native_c03_final_evidence.json", native_c03)
    c03_local = (pp_meta or {}).get("c03_graphrag_bound")
    if isinstance(c03_local, dict):
        write_json(artifact_dir / "c03_graphrag_bound.json", c03_local)
    (artifact_dir / "compiled_prompt.txt").write_text(
        json.dumps(messages, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_json(
        artifact_dir / "compiled_prompt_artifact.json",
        merge_compiled_prompt_artifact_fec_fields(
            {
                "section_id": section_compiled.section_id,
                "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "compiler_template_id": section_compiled.artifact.template_id,
                "pa_prompt_hash": section_compiled.artifact.prompt_hash,
                "dispatch_sha256_prompt16": prompt_hash,
                "slot_count": section_compiled.artifact.slot_count,
                "allowed_fact_ids": sorted(str(x) for x in allowed_fact_ids),
            },
            runtime_payload,
        ),
    )

    provider_raw_output: str | None = None
    provider_request_data = None
    provider_result_data = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "BLOCKED"
    live_preflight_blocked = False
    visible_graph_surface_receipt: dict[str, Any] | None = None
    visible_graph_surface_receipt_ref = ""

    from apps_rg.runtime.spine.exit_lane_hooks import finalize_section_exit_after_l2
    from apps_rg.runtime.section_l2_lane_integration import (
        finalize_section_l2_after_output,
        prepare_section_l2_before_provider,
    )
    from apps_rg.runtime.section_runtime_exhaust_lane_integration import (
        finalize_section_runtime_exhaust_before_l6,
        gate_section_l6_shadow_after_exhaust,
    )

    prepare_section_l2_before_provider(
        artifact_dir,
        "competencies",
        runtime_payload,
        provider_lane=str(args.provider),
    )

    from apps_rg.runtime.section_model_limits import (
        external_openai_generation_model,
        resolve_section_generation_model,
    )

    section_model = (
        external_openai_generation_model()
        if str(args.provider) == "external_openai"
        else resolve_section_generation_model("competencies")
    )
    provider_req, provider_payload = build_section_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=COMPETENCIES_MAX_OUTPUT_TOKENS,
        timeout_seconds=competencies_provider_chat_timeout_s(),
        model=section_model,
        provider_requested=str(args.provider),
    )
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_request_data.get("model") or SECTION_MODEL_ID)
    _run_id = str(runtime_payload.get("run_id") or "")
    base_url = str(provider_request_data.get("provider_url") or "")
    pre_timeout = competencies_provider_preflight_timeout_s()
    print(
        f"[competencies] provider preflight: shared HTTP /v1/models probe base_url={base_url!r} "
        f"model={req_model!r} timeout_s={pre_timeout}",
        file=sys.stderr,
        flush=True,
    )
    if competencies_provider_preflight_disabled():
        print(
            "[competencies] WARNING: APPS_RG_COMPETENCIES_PROVIDER_PREFLIGHT_DISABLE is set - "
            "skipping HTTP models preflight in slice (not recommended for unattended runs).",
            file=sys.stderr,
            flush=True,
        )
    from apps_rg.runtime.reasoning.bullet_lane_generation import generate_bullet_lane_with_sc_and_claude
    from apps_rg.runtime.reasoning.competencies_graph_pool import build_competencies_targeting_context

    skill_ids: set[str] = set()
    for row in pp_meta.get("selected_skill_rows") or []:
        if isinstance(row, dict):
            sid = str(row.get("skill_id") or "").strip()
            if sid:
                skill_ids.add(sid)
    targeting_context = build_competencies_targeting_context(
        runtime_payload,
        allowed_fact_ids=allowed_fact_ids,
        allowed_skill_ids=skill_ids,
    )
    targeting_context["allowed_fact_ids"] = sorted(str(x) for x in allowed_fact_ids)
    targeting_context["resume_support_blob_lower"] = c0_proof_blob

    judge_mode = "mocked" if getattr(args, "mock_judges", False) else "blocked_if_unavailable"
    _mark_phase("prepare_l2_before_provider")
    result, raw_output, parsed, parse_error, gen_meta = generate_bullet_lane_with_sc_and_claude(
        section_lane=LANE_KEY,
        slot_kind="competencies",
        provider_payload=provider_payload,
        parse_model_json=parse_model_json,
        normalize_parsed=lambda p: normalize_parsed_output(p, runtime_payload, allowed_fact_ids),
        artifact_dir=artifact_dir,
        run_id=_run_id or None,
        temperature_bounds=(0.30, 0.50),
        base_temperature=float(args.temperature),
        required_bullet_ids=None,
        targeting_context=targeting_context,
        judge_mode=judge_mode,
        provider_profile=str(args.provider),
        use_sc_path=True,
    )
    write_json(artifact_dir / "bullet_lane_generation.json", gen_meta)
    _mark_phase("self_consistency_generation_and_selector")
    raw_model_output_original = raw_output
    provider_raw_output = raw_output
    if getattr(result, "apps_rg_provider_preflight_blocked", False) if result else False:
        live_preflight_blocked = True
        snap = getattr(result, "apps_rg_last_probe_snapshot", None)
        write_json(
            artifact_dir / "competencies_live_provider_gate.json",
            live_provider_gate_audit_payload_failure(
                provider_base_url=base_url,
                preflight_detail=str(result.exact_provider_error or "http_models_preflight_failed"),
                timeout_s=pre_timeout,
                probe_snapshot=dict(snap) if isinstance(snap, dict) else None,
            ),
        )
        print(
            f"{STATUS_BLOCKED_LIVE_PROVIDER}: {REASON_PROVIDER_UNAVAILABLE} — "
            f"HTTP /v1/models preflight blocked for {base_url!r}",
            file=sys.stderr,
            flush=True,
        )
    provider_result_data = result.to_dict() if result else {}
    if live_preflight_blocked:
        provider_result_data = {
            **provider_result_data,
            "live_provider_gate_status": STATUS_BLOCKED_LIVE_PROVIDER,
            "provider_unreachable_reason": REASON_PROVIDER_UNAVAILABLE,
            "live_provider_gate_artifact": "competencies_live_provider_gate.json",
        }
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    runtime_generation_status = result.runtime_generation_status if result else "BLOCKED"
    if runtime_generation_status in ("REAL_LLM", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS):
        if parsed is None:
            raw_model_output_original, parsed, parse_error = retry_provider_for_parse(
                messages,
                provider_payload,
                raw_model_output_original,
                parse_error,
                artifact_dir=artifact_dir,
                run_id=_run_id or None,
            )
            if parsed is not None:
                record_parse_json_retry(artifact_dir, reason=parse_error or "parse_retry")
        if parsed is not None:
            parsed = normalize_parsed_output(parsed, runtime_payload, allowed_fact_ids)
            comps = parsed.get("competencies") or []
            if isinstance(comps, list) and len(comps) >= 6 and not parsed.get("claim_ledger"):
                rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)
                clog = list(parsed.get("change_log") or [])
                clog.append(
                    {
                        "operation": "rebuild_claim_ledger_after_length_truncation",
                        "reason": "deterministic",
                    }
                )
                parsed["change_log"] = clog
            raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
            bad_term = find_bullet_restatement_term(parsed.get("competencies") or [], bullet_lowers)
            if bad_term:
                raw_output, parsed = retry_provider_competency_restatement(
                    messages,
                    provider_payload,
                    raw_output,
                    parsed,
                    bad_term,
                    runtime_payload,
                    allowed_fact_ids,
                    artifact_dir=artifact_dir,
                    run_id=_run_id or None,
                )
                if parsed is not None:
                    record_regen_llm(
                        artifact_dir,
                        operation="competency_restatement_regen",
                        reason=f"bullet_restatement:{bad_term}"[:240],
                        replaced_l2=True,
                    )
                    raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        else:
            raw_output = raw_model_output_original
    else:
        parsed = None
        parse_error = result.exact_provider_error or "provider blocked"

    if parsed is not None:
        _pre_finalize = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        from apps_rg.runtime.sections.competencies_v3_contract import sync_categories_competencies

        sync_categories_competencies(parsed)
        record_mechanical(artifact_dir, operation="competencies_pre_x2_deterministic_pipeline", reason="sync_and_coerce")
        collapse_duplicate_competency_terms(parsed, bullet_rows, resume_blob)
        repair_structured_competencies_source_facts(
            parsed,
            allowed_fact_ids=allowed_fact_ids,
            resume_support_blob_lower=c0_proof_blob,
        )
        coerce_structured_competencies_resume_support(
            parsed,
            bullet_rows,
            c0_proof_blob,
            bullet_lowers,
            allowed_fact_ids=allowed_fact_ids,
        )
        dedupe_structured_competency_terms(parsed)
        reduce_competency_keyword_stuffing(parsed)
        canonicalize_competency_terms_for_proof(parsed, allowed_fact_ids=allowed_fact_ids)
        coerce_structured_competencies_resume_support(
            parsed,
            bullet_rows,
            c0_proof_blob,
            bullet_lowers,
            allowed_fact_ids=allowed_fact_ids,
        )
        dedupe_structured_competency_terms(parsed)
        from apps_rg.runtime.sections.competencies_lane_runtime import (
            expand_structured_competencies_min_two_terms,
        )

        expand_structured_competencies_min_two_terms(
            parsed,
            bullet_rows=bullet_rows,
            allowed_fact_ids=allowed_fact_ids,
            resume_support_blob_lower=c0_proof_blob,
            bullet_texts_lower=bullet_lowers,
        )
        rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)
        prune_claim_ledger_bullet_paste(parsed)
        from apps_rg.runtime.sections.competencies_capability_projection import (
            finalize_competencies_v3_output,
        )

        skill_rows_by_id: dict[str, dict[str, Any]] = {}
        allowed_skill_ids: set[str] = set()
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
            from apps_rg.runtime.sections.competencies_lane_runtime import (
                backfill_graph_bundle_min_terms,
            )
            from apps_rg.runtime.sections.competency_capability_evidence import (
                augment_bound_category_family_terms,
                enrich_competencies_visible_graph_surface,
                hydrate_competency_bundle_graph_evidence,
                stamp_competency_bundle_bindings,
            )

            packet = pp_meta.get("competency_capability_section_packet")
            _pkt = packet if isinstance(packet, dict) else None
            stamp_competency_bundle_bindings(
                parsed.get("categories") or [],
                packet=_pkt,
            )
            stamp_competency_bundle_bindings(
                parsed.get("competencies") or [],
                packet=_pkt,
            )
            augment_bound_category_family_terms(
                parsed.get("categories") or [],
                packet=_pkt,
                allowed_fact_ids=allowed_fact_ids,
            )
            augment_bound_category_family_terms(
                parsed.get("competencies") or [],
                packet=_pkt,
                allowed_fact_ids=allowed_fact_ids,
            )
            hydrate_competency_bundle_graph_evidence(
                parsed.get("categories") or [],
                packet=_pkt,
                allowed_fact_ids=allowed_fact_ids,
                selected_graph_evidence_plan=pp_meta.get("selected_graph_evidence_plan"),
            )
            hydrate_competency_bundle_graph_evidence(
                parsed.get("competencies") or [],
                packet=_pkt,
                allowed_fact_ids=allowed_fact_ids,
                selected_graph_evidence_plan=pp_meta.get("selected_graph_evidence_plan"),
            )
            # W2.2 (typed-edge-role-facet-guardrails-a6f3d2): final floor-filler for
            # graph-bundle categories that augment_bound_category_family_terms could NOT
            # top up because the bound bundle has no linked fact in the allowed pool
            # (e.g. platform_productization's only linked fact, fact_engineering_platform_006,
            # was not selected for this target). This backfill runs AFTER bundle stamping, so
            # categories carry competency_bundle_id + graph_skill_node_ids; it appends the
            # bundle's vocabulary_anchors backed by the category's OWN allowed source_fact_ids
            # plus the bundle's graph_skill_node_ids — graph-backed proof under the GraphDB-SSOT
            # model, no fact-provenance stretch. Only fires for bundle-bound categories below floor.
            backfill_graph_bundle_min_terms(parsed)
            visible_graph_surface_receipt = enrich_competencies_visible_graph_surface(
                parsed,
                packet=_pkt,
                allowed_fact_ids=allowed_fact_ids,
                selected_graph_evidence_plan=pp_meta.get("selected_graph_evidence_plan"),
            )
            if visible_graph_surface_receipt:
                visible_graph_surface_receipt_ref = _artifact_repo_rel(
                    artifact_dir / "competencies_visible_graph_surface_enrichment_receipt.json",
                    REPO_ROOT,
                )
                write_json(
                    artifact_dir / "competencies_visible_graph_surface_enrichment_receipt.json",
                    visible_graph_surface_receipt,
                )
            # Injected anchor terms need claim_ledger rows so x2_all_terms_source_fact_ids holds.
            rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)
        _post_finalize = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        if _post_finalize != _pre_finalize:
            record_deterministic_rewrite(
                artifact_dir,
                operation="finalize_competencies_v3_output",
                reason="capability_projection",
            )
        raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))

    _mark_phase("deterministic_repairs")
    competencies = list((parsed or {}).get("competencies") or [])
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    display_text = competencies_display_text(competencies)
    model_name = None
    if provider_result_data:
        model_name = provider_result_data.get("model")
    elif provider_request_data:
        model_name = provider_request_data.get("model")

    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed,
        parse_error=parse_error,
        raw_output=raw_output or "",
        lane_profile="competencies",
    )
    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger) if parse_status == "OK" else []
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
        claim_id_prefix="competencies_claim",
    )
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)
    coverage = build_sentence_claim_coverage(display_text, claim_ledger, allowed_fact_ids)
    write_json(artifact_dir / "text_claim_coverage.json", coverage)
    effective_sfp_c = (parsed or {}).get("selected_fact_plan") if isinstance(parsed, dict) else None
    if not isinstance(effective_sfp_c, dict):
        effective_sfp_c = selected_fact_plan
    write_json(artifact_dir / "selected_fact_plan.json", effective_sfp_c)
    competency_group_fact_support: list[dict[str, Any]] = []
    for cat in competencies:
        if isinstance(cat, dict):
            competency_group_fact_support.append(
                {
                    "category_label": cat.get("category_label"),
                    "source_fact_ids": list(cat.get("source_fact_ids") or []),
                }
            )
    req_id_c = str(
        (provider_request_data or {}).get("request_id")
        or (provider_request_data or {}).get("id")
        or runtime_payload["run_id"]
    )
    jd_alignment_final = merge_jd_alignment((parsed or {}).get("jd_alignment") if isinstance(parsed, dict) else None)
    trace_rr_c = artifact_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    usage_doc = build_section_input_usage_ledger_v1(
        section_id="competencies",
        run_id=str(runtime_payload["run_id"]),
        request_id=req_id_c,
        trace_root=trace_rr_c,
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        runtime_payload=runtime_payload,
        selected_fact_plan=effective_sfp_c,
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
        jd_text=str(runtime_payload.get("jd_text") or ""),
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        briefing_text=str(runtime_payload.get("briefing") or ""),
        jd_alignment=jd_alignment_final,
        extra_section_fields={"competency_group_fact_support": competency_group_fact_support},
    )
    from apps_rg.runtime.c0.section_proof_loader import apply_proof_pool_to_usage_ledger

    write_json(
        artifact_dir / "section_input_usage_ledger.json",
        apply_proof_pool_to_usage_ledger(usage_doc, pool),
    )

    from apps_rg.runtime.reasoning.employment_bullet_pool import competencies_pool_x1d_judge_rows
    from apps_rg.runtime.judges.competencies_x1d import run_competencies_judges

    judge_allowed_mock = bool(args.mock_judges and getattr(args, "allow_test_mock_judges", False))
    judge_mode = "mocked" if judge_allowed_mock else "blocked_if_unavailable"
    selector_receipt = competencies_pool_x1d_judge_rows(
        artifact_dir=artifact_dir,
        section_id=LANE_KEY,
        gen_meta=gen_meta,
    )
    write_json(
        artifact_dir / "competencies_graph_pool_selector_receipt.json",
        {"judges": selector_receipt},
    )
    judge_keys = [j.strip() for j in str(getattr(args, "x1d_judges", "") or "").split(",") if j.strip()]
    if not judge_keys:
        from apps_rg.runtime.section_cli_defaults import COMPETENCIES_DEFAULT_X1D_JUDGES

        judge_keys = [j.strip() for j in COMPETENCIES_DEFAULT_X1D_JUDGES.split(",") if j.strip()]
    x1d_outputs = run_competencies_judges(
        competencies=competencies,
        claim_ledger=claim_ledger,
        judge_keys=judge_keys,
        companion_context=companion_context,
        mode=judge_mode,
        artifact_base=artifact_dir,
    )
    x1d = [j.to_dict() if hasattr(j, "to_dict") else dict(j) for j in x1d_outputs]
    write_json(
        artifact_dir / "x1d_llm_judge_outputs.json",
        {"judges": x1d, "requested_judges": judge_keys},
    )
    _mark_phase("x1d")

    from apps_rg.runtime.product_evidence_authority import x2_proof_pool_gate_flags

    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active, srfs_slice_x2_active = x2_proof_pool_gate_flags(pp_x2)

    x2 = [
        g.to_dict()
        for g in run_competencies_x2_gates(
            competencies=competencies,
            parsed_output=parsed,
            claim_ledger=claim_ledger,
            jd_text=args.jd_text,
            briefing_text=getattr(args, "briefing", "") or "",
            bullet_texts_lower=bullet_lowers,
            resume_support_blob=resume_blob,
            c0_proof_blob=c0_proof_blob,
            allowed_fact_ids=allowed_fact_ids,
            runtime_generation_status=runtime_generation_status,
            cli_provider=args.provider,
            live_preflight_blocked=live_preflight_blocked,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
            artifacts_dir=artifact_dir,
            text_claim_coverage=coverage,
            srfs_source_fact_slice_gate_active=srfs_slice_x2_active,
            proof_pool_metadata=pp_x2,
            proof_pool_ref=str(pool.proof_pool_ref or ""),
            proof_pool_digest=str(pool.proof_pool_digest or ""),
        )
    ]
    # X2 severity SSOT (plan x2-gate-slimdown-b4e8d2): demote adversarially-verified STYLE gates
    # to WARN (record-don't-block) without touching detection. No-op for correctness gates.
    from apps_rg.runtime.validators.x2_severity import soften_warn_only

    x2 = soften_warn_only(x2)
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        write_x2_source_fact_pool_receipt,
    )

    for g in x2:
        obs = g.get("observed_value")
        if isinstance(obs, dict) and obs.get("x2_source_fact_pool_status"):
            write_x2_source_fact_pool_receipt(artifact_dir, obs)
            break

    from apps_rg.runtime.validators.competencies_quality_x2 import (
        build_competencies_graph_sufficiency_receipt,
    )

    graph_sufficiency_receipt = build_competencies_graph_sufficiency_receipt(
        competencies,
        proof_pool_metadata=pp_x2,
        parsed_output=parsed,
        jd_text=args.jd_text,
        briefing_text=getattr(args, "briefing", "") or "",
        x1d_judges=x1d,
    )
    graph_sufficiency_receipt_ref = _artifact_repo_rel(
        artifact_dir / "competencies_graph_sufficiency_receipt.json",
        REPO_ROOT,
    )
    graph_traversal_receipt_ref = _artifact_repo_rel(
        artifact_dir / "competencies_graph_traversal_sufficiency_receipt.json",
        REPO_ROOT,
    )
    write_json(
        artifact_dir / "competencies_graph_sufficiency_receipt.json",
        graph_sufficiency_receipt,
    )
    write_json(
        artifact_dir / "competencies_graph_traversal_sufficiency_receipt.json",
        graph_sufficiency_receipt.get("traversal_sufficiency_receipt") or {},
    )
    write_json(
        artifact_dir / "traversal_sufficiency_receipt.json",
        graph_sufficiency_receipt.get("traversal_sufficiency_receipt") or {},
    )
    graph_candidate_receipt = {}
    if isinstance(pp_x2, dict):
        graph_candidate_receipt = pp_x2.get("graph_candidate_receipt") or {}
    write_json(artifact_dir / "graph_candidate_receipt.json", graph_candidate_receipt)

    def _x2_gate(gate_id: str) -> dict[str, Any]:
        for row in x2:
            if row.get("gate_id") == gate_id:
                return row
        return {}

    granularity_gate = _x2_gate("x2_competencies_graph_granularity_gates")
    graph_granularity_gate_receipt = {
        "schema_version": "graph_granularity_gate_receipt_v1",
        "producer": "apps_rg.runtime.sections.competencies_lane_execution",
        "section_id": "competencies",
        "input_artifact_paths": [
            graph_sufficiency_receipt_ref,
            graph_traversal_receipt_ref,
        ],
        "deterministic_gate_id": "x2_competencies_graph_granularity_gates",
        "deterministic_gate_verdict": "PASS" if granularity_gate.get("pass") else "FAIL",
        "observed_value": granularity_gate.get("observed_value") or {},
        "failure_reason": granularity_gate.get("failure_reason"),
        "pass": bool(granularity_gate.get("pass")),
        "human_readable_explanation": (
            "Validates per-category graph leaf/source lineage, source concentration, "
            "and role-critical axis coverage for competencies."
        ),
    }
    write_json(artifact_dir / "graph_granularity_gate_receipt.json", graph_granularity_gate_receipt)

    concentration_gate = _x2_gate("x2_competencies_source_fact_concentration_limit")
    graph_fact_concentration_receipt = {
        "schema_version": "graph_fact_concentration_receipt_v1",
        "producer": "apps_rg.runtime.sections.competencies_lane_execution",
        "section_id": "competencies",
        "input_artifact_paths": [graph_sufficiency_receipt_ref],
        "source_fact_usage": graph_sufficiency_receipt.get("source_fact_usage") or {},
        "dominant_source_fact_id": graph_sufficiency_receipt.get("dominant_source_fact_id"),
        "dominant_source_fact_category_share": graph_sufficiency_receipt.get(
            "dominant_source_fact_category_share"
        ),
        "threshold": graph_sufficiency_receipt.get("source_fact_concentration_threshold"),
        "deterministic_gate_id": "x2_competencies_source_fact_concentration_limit",
        "deterministic_gate_verdict": "PASS" if concentration_gate.get("pass") else "FAIL",
        "failure_reason": concentration_gate.get("failure_reason"),
        "pass": bool(concentration_gate.get("pass")),
    }
    write_json(artifact_dir / "graph_fact_concentration_receipt.json", graph_fact_concentration_receipt)

    runtime_graph_sourcing_assessment = {
        "schema_version": "runtime_graph_sourcing_assessment_v1",
        "producer": "apps_rg.runtime.sections.competencies_lane_execution",
        "section_id": "competencies",
        "selected_candidates": graph_candidate_receipt.get("selected_candidate_count"),
        "rejected_candidates": graph_candidate_receipt.get("rejected_candidate_count"),
        "traversal": graph_sufficiency_receipt.get("traversal_sufficiency_receipt") or {},
        "granularity_gate": graph_granularity_gate_receipt,
        "fact_concentration_gate": graph_fact_concentration_receipt,
        "confidence_decomposition": {
            "confidence_nonconstant": graph_sufficiency_receipt.get("confidence_nonconstant"),
            "category_confidence_values": graph_sufficiency_receipt.get("category_confidence_values") or [],
            "missing_confidence_category_labels": graph_sufficiency_receipt.get(
                "missing_confidence_category_labels"
            )
            or [],
        },
        "pass": bool(granularity_gate.get("pass")) and bool(concentration_gate.get("pass")),
        "human_readable_explanation": (
            "Human-auditable graph sourcing summary for competencies; deterministic "
            "graph gates remain authoritative over selector or judge agreement."
        ),
    }
    write_json(artifact_dir / "runtime_graph_sourcing_assessment.json", runtime_graph_sourcing_assessment)

    l2_output = {
        "run_id": runtime_payload["run_id"],
        "section_id": "competencies",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "competencies": competencies,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": jd_alignment_final,
        "excluded_jd_skills": (parsed or {}).get("excluded_jd_skills") or [],
        "removed_or_rewritten_terms": (parsed or {}).get("removed_or_rewritten_terms") or [],
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
        "text_claim_coverage": coverage,
        "competencies_graph_sufficiency_receipt_ref": graph_sufficiency_receipt_ref,
        "competencies_graph_traversal_sufficiency_receipt_ref": graph_traversal_receipt_ref,
        "competencies_visible_graph_surface_enrichment_receipt_ref": visible_graph_surface_receipt_ref,
    }
    write_json(artifact_dir / "competencies_output.json", competencies)
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        attach_reasoning_to_prompt_trace(
            {
                "runtime_path": trace_runtime_path,
                "prompt_id": PROMPT_ID,
                "provider": args.provider,
                "temperature": args.temperature,
                "section_prompt_adapter": True,
                "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
                "compiler_template_id": section_compiled.artifact.template_id,
            },
            provider=args.provider,
            lane_key=LANE_KEY,
            provider_result_data=provider_result_data if isinstance(provider_result_data, dict) else None,
        ),
    )

    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2, section_id="competencies")
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )
    _mark_phase("x2")

    from apps_rg.runtime.section_repair_lane_integration import finalize_lane_product_quality

    product_quality_status, product_quality_reason = finalize_lane_product_quality(
        artifact_dir,
        runtime_generation_status=runtime_generation_status,
        x2_gates=x2,
        pass_reason="REAL_LLM output passed all deterministic competencies gates.",
        l2_output=l2_output,
        regen_authoritative_on_x2_pass=True,
    )

    from apps_rg.runtime.exit import competencies_x3 as _competencies_x3_mod
    from apps_rg.runtime.spine.section_x3_finalize import finalize_section_lane_x3

    x3 = _competencies_x3_mod.aggregate_x3(
        resume_display_text=display_text or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
        judge_required_for_allow=(
            get_section_judge_policy("competencies").x1d_required_for_x3_allow
        ),
    )
    x3 = clarify_x3_for_competencies_live_provider_preflight(
        x3,
        live_preflight_blocked=live_preflight_blocked,
    )
    bundle = compute_lane_proof_bundle(
        args,
        section_id="competencies",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
    )
    x3 = finalize_section_lane_x3(
        artifact_dir=artifact_dir,
        section_id="competencies",
        runtime_payload=runtime_payload,
        x3_result=x3,
        x3_doc_extra={
            "proof_eligible": bool(bundle.get("proof_eligible")),
            "judge_proof_eligible": bundle.get("judge_proof_eligible"),
        },
    )
    finalize_section_l2_after_output(
        artifact_dir,
        "competencies",
        runtime_payload,
        section_output_ref="competencies_section_output.json",
    )
    finalize_section_runtime_exhaust_before_l6(
        artifact_dir, "competencies", runtime_payload, repo_root=REPO_ROOT
    )
    _mark_phase("x3_and_l2_finalize")
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    graph_gate_ids = {
        "x2_competencies_rejected_neighbor_audit_present",
        "x2_competencies_graph_traversal_sufficiency",
        "x2_competencies_graph_granularity_gates",
        "x2_competencies_source_fact_concentration_limit",
        "x2_competencies_per_category_confidence_nonconstant",
        "x2_competencies_selected_graph_evidence_depth_sufficient",
    }
    graph_gate_rows = [row for row in x2 if row.get("gate_id") in graph_gate_ids]
    deterministic_graph_failures = [
        str(row.get("gate_id") or "")
        for row in graph_gate_rows
        if not bool(row.get("pass"))
    ]
    judge_rows = [
        {
            "provider_key": row.get("provider_key"),
            "provider_status": row.get("provider_status"),
            "evaluator_mode": row.get("evaluator_mode"),
            "score": row.get("normalized_score"),
            "pass": bool(row.get("pass")),
            "decisive_failure": bool(row.get("decisive_failure")),
        }
        for row in (x1d or [])
        if isinstance(row, dict)
    ]
    judge_failures = [
        str(row.get("provider_key") or row.get("provider_status") or "judge")
        for row in judge_rows
        if not bool(row.get("pass")) or bool(row.get("decisive_failure"))
    ]
    selector_pass = bool(graph_candidate_receipt.get("candidate_conservation_pass"))
    final_disposition = (
        "BLOCK"
        if deterministic_graph_failures or not selector_pass
        else ("REVIEW" if judge_failures else "ALLOW")
    )
    arbitration_receipt = {
        "schema_version": "graph_selector_judge_arbitration_receipt_v1",
        "producer": "apps_rg.runtime.sections.competencies_lane_execution",
        "section_id": "competencies",
        "plan_id": graph_candidate_receipt.get("plan_id"),
        "plan_digest": graph_candidate_receipt.get("plan_digest"),
        "selector": {
            "candidate_conservation_pass": selector_pass,
            "selected_candidate_count": graph_candidate_receipt.get("selected_candidate_count"),
            "rejected_candidate_count": graph_candidate_receipt.get("rejected_candidate_count"),
        },
        "deterministic_graph_gates": graph_gate_rows,
        "deterministic_graph_failures": deterministic_graph_failures,
        "judge_rows": judge_rows,
        "judge_failures": judge_failures,
        "precedence_rule": "deterministic_graph_failure_blocks; judge_failure_reviews; all_clear_allows",
        "final_disposition": final_disposition,
        "x3_code": x3.x3_code,
        "pass": final_disposition == "ALLOW",
        "human_readable_explanation": (
            "Selector and judge agreement cannot override deterministic graph proof gaps; "
            "any graph authority/traversal/granularity/concentration/confidence failure blocks."
        ),
    }
    write_json(artifact_dir / "graph_selector_judge_arbitration_receipt.json", arbitration_receipt)
    jd_al_out = jd_alignment_final
    section_agg: dict[str, Any] = {
        "schema_version": "1",
        "section_id": "competencies",
        "canonical_aggregation_note": (
            "CANONICAL_DOWNSTREAM_AGGREGATION_INPUT — use this file as the sole bundle-shaped join surface "
            "for competencies (display_lines, competencies[], claim_ledger, proof-boundary flags, X2/X3 refs). "
            "competencies_output.json is legacy competencies[] only; provider_response.json is transport-only diagnostic."
        ),
        "artifact_role_bundle": {
            "competencies_section_output.json": "canonical_downstream_aggregation_input",
            "competencies_output.json": "legacy_competencies_array_only",
            "provider_response.json": "diagnostic_transport_metadata_only",
            "l2_output.json": "rich_runtime_section_object_with_refs",
        },
        "display_lines": [ln for ln in (display_text or "").split("\n") if str(ln).strip()],
        "competencies": competencies,
        "categories": (parsed or {}).get("categories") or [],
        "claim_ledger": claim_ledger,
        "selected_fact_ids": sorted(str(x) for x in allowed_fact_ids),
        "targeting_only": bool(jd_al_out.get("targeting_only")),
        "jd_used_as_proof": bool(jd_al_out.get("jd_used_as_proof")),
        "briefing_used_as_proof": bool(jd_al_out.get("briefing_used_as_proof")),
        "companion_context_used_as_proof": bool(jd_al_out.get("companion_context_used_as_proof")),
        "runtime_generation_status": runtime_generation_status,
        "x2_gate_outputs_ref": _artifact_repo_rel(artifact_dir / "x2_gate_outputs.json", REPO_ROOT),
        "x3_disposition_ref": _artifact_repo_rel(artifact_dir / "x3_disposition.json", REPO_ROOT),
        "section_input_usage_ledger_ref": _artifact_repo_rel(
            artifact_dir / "section_input_usage_ledger.json",
            REPO_ROOT,
        ),
        "competencies_graph_sufficiency_receipt_ref": graph_sufficiency_receipt_ref,
        "competencies_graph_traversal_sufficiency_receipt_ref": graph_traversal_receipt_ref,
        "competencies_visible_graph_surface_enrichment_receipt_ref": visible_graph_surface_receipt_ref,
        "graph_selector_judge_arbitration_receipt_ref": _artifact_repo_rel(
            artifact_dir / "graph_selector_judge_arbitration_receipt.json",
            REPO_ROOT,
        ),
        "proof_eligible": bool(bundle.get("proof_eligible")),
        "proof_scope": bundle.get("proof_scope"),
        "product_quality_status": product_quality_status,
        "x3_code": x3.x3_code,
    }
    write_json(artifact_dir / "competencies_section_output.json", section_agg)
    l2_output["competencies_section_output_ref"] = _artifact_repo_rel(
        artifact_dir / "competencies_section_output.json",
        REPO_ROOT,
    )
    write_json(artifact_dir / "l2_output.json", l2_output)

    l6_temp = float(args.temperature)
    l6_max = COMPETENCIES_MAX_OUTPUT_TOKENS
    gate_section_l6_shadow_after_exhaust(artifact_dir, runtime_payload)
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)
    _mark_phase("l6_shadow")
    # W5: emit the phase timing board. lane_phases = surrounding-phase deltas; generation_selector
    # _phases = per-round generation/selector durations surfaced from the bullet-lane orchestrator.
    write_json(
        artifact_dir / "competencies_runtime_timing.json",
        {
            "section_id": "competencies",
            "run_id": str(runtime_payload.get("run_id") or ""),
            "runtime_generation_status": runtime_generation_status,
            "e2e_closeout_mode": bool((gen_meta or {}).get("e2e_closeout_mode")),
            "max_regen_rounds_allowed": (gen_meta or {}).get("max_regen_rounds_allowed"),
            "lane_phases": _phase_timings,
            "generation_selector_phases": (gen_meta or {}).get("phase_timings") or [],
        },
    )

    section_agg["l6_shadow_eval_package_ref"] = _artifact_repo_rel(
        artifact_dir / "l6_shadow_eval_package.json",
        REPO_ROOT,
    )
    section_agg["l6_shadow_learning_ref"] = _artifact_repo_rel(
        artifact_dir / "l6_shadow_learning.json",
        REPO_ROOT,
    )
    _prop_path = artifact_dir / "l6_future_run_proposals.json"
    if _prop_path.is_file():
        section_agg["l6_future_run_proposals_ref"] = _artifact_repo_rel(_prop_path, REPO_ROOT)
    _rca_path = artifact_dir / "l6_shadow_rca_sketch.json"
    if _rca_path.is_file():
        section_agg["l6_shadow_rca_sketch_ref"] = _artifact_repo_rel(_rca_path, REPO_ROOT)
    write_json(artifact_dir / "competencies_section_output.json", section_agg)

    l2_output["l6_shadow_eval_package_ref"] = section_agg["l6_shadow_eval_package_ref"]
    l2_output["l6_shadow_learning_ref"] = section_agg["l6_shadow_learning_ref"]
    if section_agg.get("l6_future_run_proposals_ref"):
        l2_output["l6_future_run_proposals_ref"] = section_agg["l6_future_run_proposals_ref"]
    if section_agg.get("l6_shadow_rca_sketch_ref"):
        l2_output["l6_shadow_rca_sketch_ref"] = section_agg["l6_shadow_rca_sketch_ref"]
    write_json(artifact_dir / "l2_output.json", l2_output)

    rl2 = {
        "provider_attempted": args.provider,
        "runtime_generation_status": runtime_generation_status,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "raw_model_output": raw_output,
        "raw_model_output_provider": provider_raw_output,
        "product_quality_status": product_quality_status,
        "x3_code": x3.x3_code,
    }
    attach_lane_proof_bundle_fields(
        rl2,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )

    _smr_co = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "competencies",
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": None,
        "claim_ledger_hash": None,
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": product_quality_status,
        "x2_failed_gates": [g["gate_id"] for g in x2 if not g["pass"]],
        "x3_code": x3.x3_code,
        "proof_eligible": bundle["proof_eligible"],
        "judge_proof_eligible": bundle["judge_proof_eligible"],
        "proof_authority_receipt": {
            "proof_authority": "graph_skills_plus_linked_source_facts",
            "base_resume_usage": "calibration_only",
            "jd_usage": "targeting_only",
            "e0_usage": "style_only",
            "new_gates_wired": [
                "x2_competencies_capability_family_coverage",
                "x2_competencies_no_default_fid_proof",
                "x2_competencies_generic_category_blocked_without_graph",
                "x2_competencies_e0_ngram_overlap",
                "x2_competencies_base_ngram_overlap",
            ],
        },
    }
    merge_graph_evidence_reporting_into_dict(
        _smr_co,
        section_id="competencies",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    write_json(artifact_dir / "section_metric_receipt.json", _smr_co)

    write_json(
        artifact_dir / "real_l2_generation_result.json",
        rl2,
    )

    comp_json = json.dumps(competencies, separators=(",", ":"), ensure_ascii=False)
    lines = [
        "COMPETENCIES_OUTPUT:",
        comp_json,
        "",
        "X1D_LLM_JUDGE_OUTPUTS:",
        "| Provider | Mode | Status | Score | Pass | Decisive Failure |",
        "|---|---|---|---:|---|---|",
    ]
    for judge in x1d:
        lines.append(
            f"| {judge['provider_name']} | {judge['evaluator_mode']} | {judge.get('provider_status')} | "
            f"{judge.get('score')} | {judge.get('pass')} | {judge.get('decisive_failure')} |"
        )
    lines.extend(["", "X2_DETERMINISTIC_GATE_OUTPUTS:"])
    for gate in x2:
        lines.append(f"- {gate['gate_id']}: {'PASS' if gate['pass'] else 'FAIL'}")
    lines.extend(
        _format_competencies_graph_sourcing_assessment(
            graph_sufficiency_receipt,
            x2_gates=x2,
            traversal_receipt_ref=graph_traversal_receipt_ref,
        )
    )
    status_hint = (
        "PASS_RUNTIME_PROOF_ELIGIBLE" if bundle["proof_eligible"] else "PASS_NONCERTIFYING_RUNTIME_PROOF"
    )
    lines.extend(
        [
            "",
            "RUNTIME_PROOF_SUMMARY:",
            f"RUNTIME_GENERATION_STATUS: {runtime_generation_status}",
            f"STATUS: {status_hint}",
            f"PRODUCT_STATUS: {x3.x3_code}",
            f"PROOF_ELIGIBLE: {str(bundle['proof_eligible']).lower()}",
            "NOTE: STATUS PASS alone never implies X3 ALLOW or certification — check PRODUCT_STATUS and PROOF_ELIGIBLE.",
            f"CANONICAL_AGGREGATION_INPUT: competencies_section_output.json ({_artifact_repo_rel(artifact_dir / 'competencies_section_output.json', REPO_ROOT)})",
            "",
            "L6_SHADOW_EVAL_PACKAGE:",
            str(artifact_dir / "l6_shadow_eval_package.json"),
            "offline_only=true",
            "l6_shadow_learning=" + str(artifact_dir / "l6_shadow_learning.json"),
        ]
    )
    output_text = "\n".join(lines)
    (artifact_dir / "command_output.txt").write_text(output_text + "\n", encoding="utf-8")
    (artifact_dir / "competencies_display.txt").write_text(display_text + "\n", encoding="utf-8")
    if print_output:
        print(output_text)
    prq = str((provider_request_data or {}).get("provider_requested", args.provider))
    pratt = (provider_request_data or {}).get("provider_attempted", args.provider)
    from apps_rg.runtime.section_one_spine_certification_lane_integration import (
        finalize_section_one_spine_certification,
    )

    finalize_section_one_spine_certification(
        artifact_dir,
        "competencies",
        runtime_payload,
        proof_bundle=bundle,
        runtime_generation_status=runtime_generation_status,
    )
    finalize_runtime_proof_run(
        REPO_ROOT,
        LANE_KEY,
        args.provider,
        artifact_dir,
        run_id=runtime_payload["run_id"],
        section_id="competencies",
        runtime_generation_status=runtime_generation_status,
        provider_requested=prq,
        provider_attempted=pratt,
        command=" ".join(sys.argv),
        proof_eligible=bundle["proof_eligible"],
        proof_scope=bundle["proof_scope"],
        test_only_mock_provider=bundle["test_only_mock_provider"],
        runtime_certification=bundle["runtime_certification"],
        x1d_runtime_status=bundle["x1d_runtime_status"],
        judge_proof_eligible=bundle["judge_proof_eligible"],
        provider_proof_eligible=bundle["provider_proof_eligible"],
        test_only_mock_judges=bundle["test_only_mock_judges"],
        proof_closeout_note=bundle["proof_closeout_note"] if bundle.get("proof_closeout_note") else None,
    )
    if allow_non_allow_exit_zero_ok(args):
        exit_code = 0
    else:
        exit_code = 0 if x3.x3_code == "X3_ALLOW" else 2
    return {
        "artifact_dir": artifact_dir,
        "repo_root": REPO_ROOT,
        "lane_key": LANE_KEY,
        "runtime_payload": runtime_payload,
        "x3": x3,
        "output_text": output_text,
        "exit_code": exit_code,
        "runtime_generation_status": runtime_generation_status,
        "competencies": competencies,
    }




def run_competencies_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane_runtime",
    print_output: bool = True,
) -> dict[str, Any]:
    """Compat alias — canonical trace path is sections.competencies_lane."""
    return run_competencies_lane_execution(
        args,
        artifact_dir_override=artifact_dir_override,
        trace_runtime_path=trace_runtime_path,
        print_output=print_output,
    )


__all__ = ["run_competencies_lane_execution", "run_competencies_execution"]
