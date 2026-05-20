"""Canonical competencies lane runtime execution (W11-M4C / legacy burndown Phase D).

``apps_rg.runtime.sections.competencies_lane_api`` retains shared compile/repair helpers and
compat re-exports; product entry is ``python -m apps_rg --section competencies``.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def _hydrate_dispatch_helpers() -> None:
    import apps_rg.runtime.sections.competencies_lane_api as _cd

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


def run_competencies_lane_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane",
    print_output: bool = True,
) -> dict[str, Any]:
    _ensure_helpers_hydrated()
    from apps_rg.runtime.proof_pool_lane_integration import load_section_proof_for_lane

    pool, base, base_path, base_hash, front_spine = load_section_proof_for_lane(
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
    (artifact_dir / "companion_generated_sections.txt").write_text(companion_context or "(none)\n", encoding="utf-8")

    from apps_rg.runtime.qwen_transport_diag import merge_transport_context

    merge_transport_context(
        artifact_dir=str(artifact_dir.resolve()),
        run_id=str(runtime_payload.get("run_id") or ""),
    )
    from apps_rg.runtime.section_fec_bridge import (
        merge_compiled_prompt_artifact_fec_fields,
        wire_section_fec_bridge_for_lane,
    )

    wire_section_fec_bridge_for_lane(
        artifact_dir=artifact_dir,
        section_id="competencies",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
    )

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
    messages = section_compiled.artifact.messages
    compiled_prompt = json.dumps(messages, ensure_ascii=False, separators=(",", ":"))
    prompt_hash = sha16(compiled_prompt)
    write_json(artifact_dir / "runtime_payload.json", runtime_payload)
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

    from apps_rg.runtime.section_exit_lane_integration import finalize_section_exit_after_l2
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

    provider_req, provider_payload = build_qwen_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=COMPETENCIES_QWEN_MAX_TOKENS,
        timeout_seconds=competencies_vllm_chat_timeout_s(),
    )
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_request_data.get("model") or DEFAULT_QWEN_MODEL)
    _run_id = str(runtime_payload.get("run_id") or "")
    if effective_offline_contract_stub_enabled():
        stub_raw = json.dumps(build_mock_output(runtime_payload), sort_keys=True, separators=(",", ":"))
        result = synthetic_qwen_provider_result(raw_model_output=stub_raw, requested_model=req_model)
    elif str(args.provider).strip().lower() == "qwen_vllm":
        base_url = str(provider_request_data.get("provider_url") or "")
        pre_timeout = competencies_vllm_preflight_timeout_s()
        print(
            f"[competencies] live qwen_vllm: shared HTTP /v1/models preflight base_url={base_url!r} "
            f"model={req_model!r} timeout_s={pre_timeout}",
            file=sys.stderr,
            flush=True,
        )
        if competencies_vllm_preflight_disabled():
            print(
                "[competencies] WARNING: APPS_RG_COMPETENCIES_VLLM_PREFLIGHT_DISABLE is set — "
                "skipping HTTP models preflight in slice (not recommended for unattended runs).",
                file=sys.stderr,
                flush=True,
            )
        result = call_qwen_vllm(
            tag_reasoning_lane(provider_payload, LANE_KEY),
            artifact_dir=artifact_dir,
            run_id=_run_id or None,
        )
        if getattr(result, "apps_rg_qwen_preflight_blocked", False):
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
    else:
        result = call_qwen_vllm(
            tag_reasoning_lane(provider_payload, LANE_KEY),
            artifact_dir=artifact_dir,
            run_id=_run_id or None,
        )
    provider_result_data = result.to_dict()
    if live_preflight_blocked:
        provider_result_data = {
            **provider_result_data,
            "live_provider_gate_status": STATUS_BLOCKED_LIVE_PROVIDER,
            "provider_unreachable_reason": REASON_PROVIDER_UNAVAILABLE,
            "live_provider_gate_artifact": "competencies_live_provider_gate.json",
        }
    raw_output = result.raw_model_output
    provider_raw_output = raw_output
    raw_model_output_original = raw_output
    write_json(artifact_dir / "provider_response.json", provider_result_data)
    runtime_generation_status = result.runtime_generation_status
    if result.runtime_generation_status in ("REAL_LLM", OFFLINE_CONTRACT_STUB_RUNTIME_STATUS):
        parsed, parse_error = parse_model_json(raw_model_output_original)
        if parsed is None:
            raw_model_output_original, parsed, parse_error = retry_qwen_for_parse(
                messages,
                provider_payload,
                raw_model_output_original,
                parse_error,
                artifact_dir=artifact_dir,
                run_id=_run_id or None,
            )
        if parsed is not None:
            parsed = normalize_parsed_output(parsed, runtime_payload, allowed_fact_ids)
            comps = parsed.get("competencies") or []
            if isinstance(comps, list) and len(comps) >= 8 and not parsed.get("claim_ledger"):
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
                raw_output, parsed = retry_qwen_competency_restatement(
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
                    raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))
        else:
            raw_output = raw_model_output_original
    else:
        parsed = None
        parse_error = result.exact_provider_error or "provider blocked"

    if parsed is not None:
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
        expand_structured_competencies_min_two_terms(
            parsed,
            bullet_rows=bullet_rows,
            allowed_fact_ids=allowed_fact_ids,
            resume_support_blob_lower=c0_proof_blob,
            bullet_texts_lower=bullet_lowers,
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
        rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)
        prune_claim_ledger_bullet_paste(parsed)
        expand_structured_competencies_min_two_terms(
            parsed,
            bullet_rows=bullet_rows,
            allowed_fact_ids=allowed_fact_ids,
            resume_support_blob_lower=c0_proof_blob,
            bullet_texts_lower=bullet_lowers,
        )
        dedupe_structured_competency_terms(parsed)
        rebuild_claim_ledger_from_competencies(parsed, allowed_fact_ids)
        raw_output = json.dumps(parsed, sort_keys=True, separators=(",", ":"))

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
    from apps_rg.runtime.proof_pool_lane_integration import apply_proof_pool_to_usage_ledger

    write_json(
        artifact_dir / "section_input_usage_ledger.json",
        apply_proof_pool_to_usage_ledger(usage_doc, pool),
    )

    judge_keys = [j.strip() for j in args.x1d_judges.split(",") if j.strip()]
    judge_allowed_mock = bool(args.mock_judges and getattr(args, "allow_test_mock_judges", False))
    judge_mode = "mocked" if judge_allowed_mock else "blocked_if_unavailable"
    x1d = [
        j.to_dict()
        for j in run_competencies_judges(
            competencies=competencies,
            claim_ledger=claim_ledger,
            judge_keys=judge_keys,
            companion_context=companion_context,
            mode=judge_mode,
            artifact_base=artifact_dir,
        )
    ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active = bool(str(pp_x2.get("proof_pool_type") or "").strip())

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
            srfs_source_fact_slice_gate_active=proof_pool_x2_active,
            proof_pool_metadata=pp_x2,
            proof_pool_ref=str(pool.proof_pool_ref or ""),
            proof_pool_digest=str(pool.proof_pool_digest or ""),
        )
    ]
    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        write_x2_source_fact_pool_receipt,
    )

    for g in x2:
        obs = g.get("observed_value")
        if isinstance(obs, dict) and obs.get("x2_source_fact_pool_status"):
            write_x2_source_fact_pool_receipt(artifact_dir, obs)
            break

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

    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2)
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )

    product_quality_status, product_quality_reason = infer_product_quality(runtime_generation_status, x2)

    x3 = aggregate_x3(
        resume_display_text=display_text or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
        judge_required_for_allow=False,
    )
    x3 = clarify_x3_for_competencies_live_provider_preflight(
        x3,
        live_preflight_blocked=live_preflight_blocked,
    )
    write_json(artifact_dir / "x3_disposition.json", x3.to_dict())
    finalize_section_l2_after_output(
        artifact_dir,
        "competencies",
        runtime_payload,
        section_output_ref="competencies_section_output.json",
    )
    finalize_section_exit_after_l2(artifact_dir, "competencies", runtime_payload)
    finalize_section_runtime_exhaust_before_l6(
        artifact_dir, "competencies", runtime_payload, repo_root=REPO_ROOT
    )

    bundle = compute_lane_proof_bundle(
        args,
        section_id="competencies",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
    )
    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
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
    l6_max = COMPETENCIES_QWEN_MAX_TOKENS
    gate_section_l6_shadow_after_exhaust(artifact_dir, runtime_payload)
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

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
    }
    merge_normalized_srfs_reporting_into_dict(
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
    trace_runtime_path: str = "apps_rg.runtime.sections.competencies_lane_api",
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
