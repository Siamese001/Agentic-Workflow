"""Canonical IBM narrative lane runtime execution (legacy burndown Phase D).

``apps_rg.runtime.sections.ibm_narrative_lane_runtime`` retains shared helpers and compat re-exports;
product entry is ``python -m apps_rg --section ibm_narrative``.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any


def _hydrate_dispatch_helpers() -> None:
    import apps_rg.runtime.sections.ibm_narrative_lane_runtime as _cd

    _skip = frozenset({
        "run_ibm_narrative_execution",
        "run_ibm_narrative_lane_execution",
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


def run_ibm_narrative_lane_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.sections.ibm_narrative_lane",
    print_output: bool = False,
) -> dict[str, Any]:
    """Single end-to-end ibm_narrative run: artifacts + X1D/X2/X3/L6."""
    _ensure_helpers_hydrated()
    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane
    from apps_rg.runtime.sections import selected_role_fact_set as _srfs

    pool, base, base_path, base_hash, front_spine = load_section_proof_for_lane(
        section_id="ibm_narrative",
        args=args,
        repo_root=REPO_ROOT,
        collect_employment_bullets_fn=collect_employment_bullets,
    )
    candidate_name = str(
        base.get("candidate_name") or (base.get("header") or {}).get("name") or ""
    ).strip()
    ibm_header, _, canon_allowed = extract_ibm_employment(base)
    ibm_facts = [_srfs.plan_fact_to_employment_bullet_row(f) for f in pool.selected_fact_plan.get("facts", [])]
    ibm_facts.sort(
        key=lambda r: IBM_BULLET_IDS.index(r["fact_id"]) if r["fact_id"] in IBM_BULLET_IDS else 99,
    )
    selected_fact_plan = {**pool.selected_fact_plan, "facts": ibm_facts}
    allowed_fact_ids = set(pool.allowed_fact_ids) | set(canon_allowed)
    proof_pool_metadata = pool.proof_pool_metadata
    companion_context = load_companion_ibm_bullets_context()
    companion_text = str(companion_context.get("text") or "")
    ibm_bullets_l2 = resolve_effective_lane_l2_path(REPO_ROOT, "ibm_bullets")
    companion_ref = (
        str(ibm_bullets_l2.relative_to(REPO_ROOT))
        if ibm_bullets_l2 is not None and companion_text
        else companion_context.get("l2_ref")
    )
    runtime_payload = build_runtime_payload(
        base_json_path=base_path,
        base_hash=base_hash,
        ibm_header=ibm_header,
        selected_fact_plan=selected_fact_plan,
        allowed_fact_ids=allowed_fact_ids,
        companion_bullets_ref=companion_ref,
        companion_bullets_status=str(companion_context.get("status") or "UNKNOWN"),
        companion_bullets_reason=str(companion_context.get("reason") or ""),
        target_title=args.target_title,
        target_company=args.target_company,
        jd_text=args.jd_text,
        briefing=args.briefing,
        candidate_name=candidate_name,
    )
    runtime_payload["proof_pool_metadata"] = proof_pool_metadata
    if artifact_dir_override is not None:
        artifact_dir = Path(artifact_dir_override)
        artifact_dir.mkdir(parents=True, exist_ok=True)
    else:
        artifact_dir = prepare_runtime_proof_run_dir(REPO_ROOT, LANE_KEY, args.provider, runtime_payload["run_id"])
    from apps_rg.runtime.section_repair_ledger import init_ledger

    init_ledger(
        artifact_dir,
        section_id="ibm_narrative",
        run_id=str(runtime_payload["run_id"]),
    )
    write_json(artifact_dir / "companion_ibm_bullets_context.json", companion_context)
    (artifact_dir / "companion_ibm_bullets_context.txt").write_text(
        companion_text or "(none)\n", encoding="utf-8"
    )
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
        section_id="ibm_narrative",
        front_spine=front_spine,
        pool=pool,
        runtime_payload=runtime_payload,
        provider=str(args.provider),
        temperature=float(args.temperature),
        max_tokens=NARRATIVE_MAX_OUTPUT_TOKENS,
        output_filename="ibm_narrative_output.txt",
    )
    if blocked is not None:
        return blocked

    input_payload_hash = sha16(json.dumps(runtime_payload, sort_keys=True))
    section_compiled = compile_ibm_narrative_prompt(
        runtime_payload,
        companion_text,
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
                "allowed_fact_ids": list(runtime_payload.get("allowed_fact_ids") or []),
            },
            runtime_payload,
        ),
    )

    provider_request_data = None
    provider_result_data = None
    raw_output = ""
    parsed: dict[str, Any] | None = None
    parse_error = ""
    runtime_generation_status = "BLOCKED"

    judge_keys = [j.strip() for j in str(getattr(args, "x1d_judges", "") or "").split(",") if j.strip()]
    judge_allowed_mock = bool(args.mock_judges and getattr(args, "allow_test_mock_judges", False))
    if judge_allowed_mock:
        preflight_art = {"skipped": True, "reason": "mock_judge_cli_flags"}
    else:
        preflight_art = dict(run_ibm_narrative_judge_credentials_preflight(judge_keys, os.environ))
    preflight_blocked = bool(preflight_art.get("preflight_blocked"))
    write_json(artifact_dir / "ibm_narrative_judge_preflight.json", preflight_art)

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
        "ibm_narrative",
        runtime_payload,
        provider_lane=str(args.provider),
    )

    provider_req, provider_payload = build_section_request(
        messages=messages,
        prompt_hash=prompt_hash,
        input_payload_hash=input_payload_hash,
        temperature=args.temperature,
        max_tokens=NARRATIVE_MAX_OUTPUT_TOKENS,
    )
    provider_request_data = provider_req.to_dict()
    write_json(artifact_dir / "provider_request.json", provider_request_data)
    req_model = str(provider_request_data.get("model") or SECTION_MODEL_ID)

    from apps_rg.runtime.validators.companion_bullet_finalization import (
        UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS,
        companion_blocks_narrative_llm,
    )

    upstream_companion_blocked = companion_blocks_narrative_llm(companion_context)
    if upstream_companion_blocked:
        preflight_blocked = False

    if upstream_companion_blocked:
        parse_error = (
            f"upstream ibm_bullets not finalized: "
            f"{companion_context.get('status')}; {companion_context.get('reason')}"
        )
        result = ProviderResult(
            provider_requested=str(provider_req.provider_requested),
            provider_attempted=False,
            provider_available=False,
            exact_provider_error=parse_error,
            runtime_generation_status=UPSTREAM_NOT_FINALIZED_RUNTIME_STATUS,
            model=str(req_model),
            raw_model_output="",
            provider_response={"upstream_companion_blocked": True, "companion": companion_context},
            reasoning_execution_receipt=None,
        )
        provider_result_data = result.to_dict()
        raw_output = result.raw_model_output
        runtime_generation_status = result.runtime_generation_status
        write_json(artifact_dir / "provider_response.json", provider_result_data)
        parsed = None
    elif preflight_blocked and not judge_allowed_mock:
        result = ProviderResult(
            provider_requested=str(provider_req.provider_requested),
            provider_attempted=bool(provider_req.provider_attempted),
            provider_available=False,
            exact_provider_error="IBM narrative X1D judge credential preflight blocked narrative generation.",
            runtime_generation_status="BLOCKED",
            model=str(req_model),
            raw_model_output="",
            provider_response={"preflight_blocked": True, "preflight": preflight_art},
            reasoning_execution_receipt=None,
        )
        provider_result_data = result.to_dict()
        raw_output = result.raw_model_output
        runtime_generation_status = result.runtime_generation_status
        write_json(artifact_dir / "provider_response.json", provider_result_data)
        parsed = None
        parse_error = result.exact_provider_error or "preflight_blocked"
    elif not upstream_companion_blocked:
        from apps_rg.runtime.providers.section_provider_call import call_section_model_provider

        result = call_section_model_provider(
            str(args.provider),
            tag_reasoning_lane(provider_payload, LANE_KEY),
            artifact_dir=artifact_dir,
            run_id=str(runtime_payload.get("run_id") or ""),
        )
        provider_result_data = result.to_dict()
        raw_output = result.raw_model_output
        runtime_generation_status = result.runtime_generation_status
        write_json(artifact_dir / "provider_response.json", provider_result_data)
        if _generation_status_allows_structure_parse(result.runtime_generation_status):
            parsed, parse_error = parse_model_json(raw_output)
            if parsed is None and str(args.provider) == "external_claude":
                raw_output, parsed, parse_error = retry_qwen_for_parse(
                    messages, provider_payload, raw_output, parse_error
                )
                if parsed is not None:
                    from apps_rg.runtime.section_repair_ledger import KIND_MECHANICAL, record_repair

                    record_repair(
                        artifact_dir,
                        kind=KIND_MECHANICAL,
                        operation="parse_json_retry",
                        reason=parse_error or "parse_retry",
                        replaced_l2=False,
                    )
            if parsed is not None:
                parsed = normalize_parsed_output(parsed, runtime_payload)
                _pre_metric_raw = raw_output
                raw_output, parsed = retry_qwen_for_metric_budget(
                    messages,
                    provider_payload,
                    raw_output,
                    parsed,
                    companion_text,
                    runtime_payload,
                )
                if raw_output != _pre_metric_raw:
                    from apps_rg.runtime.section_repair_ledger import KIND_REGEN_LLM, record_repair

                    record_repair(
                        artifact_dir,
                        kind=KIND_REGEN_LLM,
                        operation="companion_metric_budget_regen",
                        reason="metric_budget",
                        replaced_l2=True,
                    )
                _pre_trim = str(parsed.get("narrative_sentence") or "")
                apply_companion_metric_budget_trim(
                    parsed, companion_text, runtime_payload=runtime_payload
                )
                if str(parsed.get("narrative_sentence") or "") != _pre_trim:
                    from apps_rg.runtime.section_repair_ledger import KIND_MECHANICAL, record_repair

                    record_repair(
                        artifact_dir,
                        kind=KIND_MECHANICAL,
                        operation="companion_metric_budget_deterministic_trim",
                        reason="deterministic_pre_x2",
                        replaced_l2=False,
                    )
                parsed = normalize_parsed_output(parsed, runtime_payload)
                remap_ibm_narrative_claim_ledger_to_fact_pool(parsed, runtime_payload)
                from apps_rg.runtime.sections.ibm_canonical_hydration import (
                    decompose_ibm_narrative_claim_ledger_by_clause,
                )

                decompose_ibm_narrative_claim_ledger_by_clause(
                    parsed,
                    narrative_sentence=str(parsed.get("narrative_sentence") or ""),
                    allowed_fact_ids={str(x) for x in (runtime_payload.get("allowed_fact_ids") or [])},
                )
        else:
            parsed = None
            parse_error = result.exact_provider_error or "provider blocked"

    narrative = str((parsed or {}).get("narrative_sentence") or "").strip()
    if narrative:
        from apps_rg.runtime.sections.section_authority_repairs import (
            sanitize_ibm_narrative_display_text,
        )

        narrative, _sanitized = sanitize_ibm_narrative_display_text(narrative)
        if parsed is not None and isinstance(parsed, dict):
            parsed["narrative_sentence"] = narrative
            if _sanitized:
                from apps_rg.runtime.section_repair_ledger import KIND_MECHANICAL, record_repair

                record_repair(
                    artifact_dir,
                    kind=KIND_MECHANICAL,
                    operation="sanitize_meta_disclaimer_tail",
                    reason="x2_ibm_narrative_no_meta_disclaimer_in_display",
                    replaced_l2=False,
                )
                clog = list(parsed.get("change_log") or [])
                clog.append(
                    {
                        "operation": "sanitize_meta_disclaimer_tail",
                        "reason": "x2_ibm_narrative_no_meta_disclaimer_in_display",
                    }
                )
                parsed["change_log"] = clog
    claim_ledger = list((parsed or {}).get("claim_ledger") or [])
    model_name = None
    if provider_result_data:
        model_name = provider_result_data.get("model")
    elif provider_request_data:
        model_name = provider_request_data.get("model")

    judge_mode = "mocked" if judge_allowed_mock else "blocked_if_unavailable"
    if preflight_blocked and not judge_allowed_mock:
        blocker_detail = "; ".join(preflight_art.get("preflight_decisive_blockers") or [])
        x1d = _preflight_blocked_synthetic_judges(
            judge_keys,
            blocker_detail or "judge credential preflight failed before narrative generation",
        )
    else:
        x1d = [
            j.to_dict()
            for j in run_ibm_narrative_judges(
                narrative_sentence=narrative,
                claim_ledger=claim_ledger,
                judge_keys=judge_keys,
                companion_bullets_context=companion_text,
                mode=judge_mode,
                artifact_base=artifact_dir,
            )
        ]
    write_json(artifact_dir / "x1d_llm_judge_outputs.json", {"judges": x1d})

    parse_status, invalid_reason = classify_ledger_parse_state(
        parsed,
        parse_error=parse_error,
        raw_output=raw_output or "",
        lane_profile="ibm_narrative",
    )
    norm_rows = normalize_exec_summary_claim_ledger(claim_ledger) if parse_status == "OK" else []
    canon_doc = build_canonical_claim_ledger_v2_payload(
        norm_rows,
        parse_status=parse_status,
        invalid_reason=invalid_reason if parse_status != "OK" else None,
        claim_id_prefix="ibm_narrative_claim",
    )
    (artifact_dir / "raw_model_output.txt").write_text(raw_output or "", encoding="utf-8")
    write_json(
        artifact_dir / "parsed_output.json",
        {"parsed": parsed, "parse_error": parse_error, "parse_status": parse_status},
    )
    write_json(artifact_dir / "canonical_claim_ledger_v2.json", canon_doc)
    coverage = build_sentence_claim_coverage(narrative, claim_ledger, allowed_fact_ids)
    write_json(artifact_dir / "text_claim_coverage.json", coverage)
    write_json(artifact_dir / "selected_fact_plan.json", (parsed or {}).get("selected_fact_plan") or selected_fact_plan)
    req_id_n = str(
        (provider_request_data or {}).get("request_id")
        or (provider_request_data or {}).get("id")
        or runtime_payload["run_id"]
    )
    trace_rr_n = artifact_dir.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    usage_doc = build_section_input_usage_ledger_v1(
        section_id="ibm_narrative",
        run_id=str(runtime_payload["run_id"]),
        request_id=req_id_n,
        trace_root=trace_rr_n,
        repo_root=REPO_ROOT,
        artifact_dir=artifact_dir,
        runtime_payload=runtime_payload,
        selected_fact_plan=(parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        claim_ledger=claim_ledger,
        allowed_fact_ids=allowed_fact_ids,
        jd_text=str(runtime_payload.get("jd_text") or ""),
        target_title=str(runtime_payload.get("target_title") or ""),
        target_company=str(runtime_payload.get("target_company") or ""),
        briefing_text=str(runtime_payload.get("briefing") or ""),
        jd_alignment=(parsed or {}).get("jd_alignment") if isinstance(parsed, dict) else None,
    )
    from apps_rg.runtime.c0.section_proof_loader import apply_proof_pool_to_usage_ledger

    write_json(
        artifact_dir / "section_input_usage_ledger.json",
        apply_proof_pool_to_usage_ledger(usage_doc, pool),
    )
    parsed_for_x2: dict[str, Any] = {**(parsed or {}), "text_claim_coverage": coverage}

    mock_provider_cli = str(getattr(args, "provider", "") or "").strip().lower() == "mock"
    plumbing_waiver_cli = bool(getattr(args, "allow_non_allow_exit_zero", False))
    hatch_mp = bool(getattr(args, "allow_test_mock_provider", False)) or (
        plumbing_waiver_cli and mock_provider_cli
    )
    test_only_mock_provider_eff = mock_provider_cli and hatch_mp

    allowed_ids_list = list(runtime_payload.get("allowed_fact_ids") or [])
    from apps_rg.runtime.product_evidence_authority import x2_proof_pool_gate_flags

    pp_x2 = runtime_payload.get("proof_pool_metadata") or {}
    proof_pool_x2_active, srfs_slice_x2_active = x2_proof_pool_gate_flags(pp_x2)
    x2 = [
        g.to_dict()
        for g in run_ibm_narrative_x2_gates(
            narrative_sentence=narrative,
            parsed_output=parsed_for_x2,
            claim_ledger=claim_ledger,
            jd_text=args.jd_text,
            runtime_generation_status=runtime_generation_status,
            companion_bullet_texts=companion_text or None,
            companion_bullets_status=str(companion_context.get("status") or "UNKNOWN"),
            companion_bullets_reason=str(companion_context.get("reason") or ""),
            companion_aware=not test_only_mock_provider_eff,
            candidate_name=candidate_name,
            provider_requested=args.provider,
            provider_attempted=args.provider,
            model_name=model_name,
            raw_output=raw_output,
            x1d_judges=x1d,
            allowed_fact_ids=allowed_ids_list,
            test_only_mock_provider=test_only_mock_provider_eff,
            artifacts_dir=artifact_dir,
            text_claim_coverage=coverage,
            srfs_source_fact_slice_gate_active=srfs_slice_x2_active,
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
        "section_id": "ibm_narrative",
        "runtime_generation_status": runtime_generation_status,
        "product_quality_status": "PENDING",
        "ibm_header": ibm_header,
        "narrative_sentence": narrative,
        "selected_fact_plan": (parsed or {}).get("selected_fact_plan") or selected_fact_plan,
        "claim_ledger": claim_ledger,
        "jd_alignment": (parsed or {}).get("jd_alignment") or {"targeting_only": True},
        "gap_notes": (parsed or {}).get("gap_notes") or [],
        "change_log": (parsed or {}).get("change_log") or [],
        "self_check": (parsed or {}).get("self_check") or {"parse_error": parse_error},
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "section_prompt_adapter": True,
        "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
        "compiler_template_id": section_compiled.artifact.template_id,
        "input_payload_hash": input_payload_hash,
        "judge_preflight_blocked": bool(preflight_blocked),
        "text_claim_coverage": coverage,
    }
    (artifact_dir / "ibm_narrative_output.txt").write_text(narrative + "\n", encoding="utf-8")
    write_json(artifact_dir / "claim_ledger.json", claim_ledger)

    write_json(
        artifact_dir / "prompt_selection_trace.json",
        {
            "runtime_path": trace_runtime_path,
            "prompt_id": PROMPT_ID,
            "provider": args.provider,
            "temperature": args.temperature,
            "section_prompt_adapter": True,
            "apps_rg_prompt_template_ref": section_compiled.apps_rg_prompt_template_ref,
            "compiler_template_id": section_compiled.artifact.template_id,
        },
    )

    write_x2_gate_outputs(artifact_dir / "x2_gate_outputs.json", x2, section_id="ibm_narrative")
    from apps_rg.runtime.section_repair_ledger import load_ledger, record_x2_run

    _ibm_ledger = load_ledger(artifact_dir) or {}
    record_x2_run(
        artifact_dir,
        run_number=len(list(_ibm_ledger.get("x2_runs") or [])) + 1,
        after_l2_source=str(_ibm_ledger.get("authoritative_l2_source") or "initial_llm"),
        x2_gates=x2,
    )
    write_json(
        artifact_dir / "fact_check_result.json",
        {"passed": not [g for g in x2 if not g["pass"]], "failed_gates": [g["gate_id"] for g in x2 if not g["pass"]]},
    )

    product_quality_status, product_quality_reason = infer_product_quality(
        runtime_generation_status, x2, artifact_dir=artifact_dir
    )

    from apps_rg.runtime.exit.ibm_narrative_x3 import aggregate_x3 as _aggregate_ibm_narrative_x3
    from apps_rg.runtime.spine.section_x3_finalize import finalize_section_lane_x3

    x3 = finalize_section_lane_x3(
        artifact_dir=artifact_dir,
        section_id="ibm_narrative",
        runtime_payload=runtime_payload,
        aggregate_x3_fn=_aggregate_ibm_narrative_x3,
        resume_display_text=narrative or raw_output,
        claim_ledger=claim_ledger,
        x2_gates=x2,
        x1d_judges=x1d,
        runtime_generation_status=runtime_generation_status,
        product_quality_status=product_quality_status,
        canonical_claims_for_hash=canon_doc.get("claims"),
        section_input_usage_ledger=usage_doc,
    )
    finalize_section_l2_after_output(artifact_dir, "ibm_narrative", runtime_payload)
    finalize_section_runtime_exhaust_before_l6(
        artifact_dir, "ibm_narrative", runtime_payload, repo_root=REPO_ROOT
    )

    bundle = compute_lane_proof_bundle(
        args,
        section_id="ibm_narrative",
        runtime_generation_status=runtime_generation_status,
        x1d_judges=x1d,
        x2_gates=x2,
        x3=x3,
    )
    mocked_rows = any(str(j.get("evaluator_mode")) == "MOCKED" for j in x1d)
    blocked_rows = any(str(j.get("evaluator_mode", "")).startswith("BLOCKED_") for j in x1d)
    decisive_blockers: list[str] = []
    if bundle.get("test_only_mock_judges"):
        decisive_blockers.append("mocked X1D judges present")
    if mocked_rows and x3.mocked_judges:
        decisive_blockers.append("runtime X1D judge rows evaluated in MOCKED mode")
    if preflight_blocked:
        decisive_blockers.extend(list(preflight_art.get("preflight_decisive_blockers") or []))
    if judge_allowed_mock or bundle.get("test_only_mock_judges"):
        recommended_next_action = "rerun with live X1D judges for clean X3 ALLOW"
    elif preflight_blocked:
        recommended_next_action = (
            "configure missing judge credentials; Gemini expects GOOGLE_API_KEY "
            "(GEMINI_API_KEY is a deprecated legacy alias)."
        )
    elif runtime_generation_status == "REAL_LLM":
        recommended_next_action = (
            "review x3_disposition.json; ensure deterministic X2 gates pass and configured model-backed judges pass "
            "(clean X3 ALLOW requires every_active X1D judge MODEL_BACKED_PASS)."
        )
    else:
        recommended_next_action = (
            "restore REAL_LLM narrative generation before attempting clean X3 ALLOW with model-backed judges."
        )
    generation_class_label = classify_generation_class(
        runtime_generation_status=runtime_generation_status,
        offline_contract_stub_active=False,
        test_only_mock_provider=bool(bundle.get("test_only_mock_provider")),
    )
    judge_class_label = classify_judge_class(x1d)
    proof_class_label = classify_proof_class(bundle=bundle, x3_code=x3.x3_code, x3_pass=bool(x3.pass_))
    certification_class_label = classify_certification_class(
        bundle=bundle, x3_code=x3.x3_code, x3_pass=bool(x3.pass_)
    )

    readiness_doc = build_clean_x3_allow_readiness_document(
        section_id="ibm_narrative",
        run_id=str(runtime_payload["run_id"]),
        clean_allow_possible_at_start=bool(
            preflight_art.get("all_required_available") and not judge_allowed_mock
        ),
        required_judges=list(judge_keys),
        provider_preflight_status_by_judge=(
            dict(preflight_art["provider_preflight_status_by_judge"])
            if isinstance(preflight_art.get("provider_preflight_status_by_judge"), dict)
            else {}
        ),
        mocked_judges_present=bool(mocked_rows),
        blocked_judges_present=bool(blocked_rows),
        mocked_judge_flags_active=judge_allowed_mock,
        x2_hard_gates_required=len(x2),
        x2_hard_gates_passed=sum(1 for g in x2 if g.get("pass")),
        x3_code=x3.x3_code,
        proceed_to_runtime=bool(x3.proceed_to_runtime),
        product_authorized=bool(x3.pass_),
        proof_eligible=bool(bundle.get("proof_eligible")),
        proof_scope=str(bundle.get("proof_scope") or ""),
        decisive_blockers=decisive_blockers,
        recommended_next_action=recommended_next_action,
        preflight_artifact_written=True,
    )
    write_json(artifact_dir / "clean_x3_allow_readiness.json", readiness_doc)

    x2_fail_count = sum(1 for g in x2 if not g.get("pass"))
    decisive_accounting_label_value = compute_decisive_accounting_label(
        command_fault=False,
        runtime_generation_status=runtime_generation_status,
        x2_failure_count=x2_fail_count,
        x3_code=x3.x3_code,
        x3_pass=bool(x3.pass_),
        proceed_to_runtime=bool(x3.proceed_to_runtime),
        mock_judges_active=bool(judge_allowed_mock),
        proof_eligible=bool(bundle.get("proof_eligible")),
        preflight_blocked=bool(preflight_blocked),
        bundle_proof_scope=str(bundle.get("proof_scope") or ""),
    )

    l2_output["product_quality_status"] = product_quality_status
    l2_output["product_quality_reason"] = product_quality_reason
    from apps_rg.runtime.section_repair_ledger import attach_ledger_summary_to_l2

    attach_ledger_summary_to_l2(l2_output, artifact_dir)
    attach_lane_proof_bundle_fields(
        l2_output,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    l2_output["generation_class"] = generation_class_label
    l2_output["judge_class"] = judge_class_label
    l2_output["proof_class"] = proof_class_label
    l2_output["certification_class"] = certification_class_label
    l2_output["decisive_accounting_label"] = decisive_accounting_label_value
    write_json(artifact_dir / "l2_output.json", l2_output)

    l6_temp = float(args.temperature)
    l6_max = NARRATIVE_MAX_OUTPUT_TOKENS
    gate_section_l6_shadow_after_exhaust(artifact_dir, runtime_payload)
    l6 = build_l6_shadow_package(
        artifact_dir=artifact_dir,
        repo_root=REPO_ROOT,
        prompt_id=PROMPT_ID,
        temperature=l6_temp,
        max_tokens=l6_max,
    )
    write_json(artifact_dir / "l6_shadow_eval_package.json", l6)

    rl2 = {
        "provider_attempted": args.provider,
        "runtime_generation_status": runtime_generation_status,
        "prompt_hash": prompt_hash,
        "model": model_name,
        "raw_model_output": raw_output,
        "narrative_sentence": narrative,
        "product_quality_status": product_quality_status,
        "x3_code": x3.x3_code,
    }
    attach_lane_proof_bundle_fields(
        rl2,
        runtime_generation_status=runtime_generation_status,
        bundle=bundle,
    )
    rl2["generation_class"] = generation_class_label
    rl2["judge_class"] = judge_class_label
    rl2["proof_class"] = proof_class_label
    rl2["certification_class"] = certification_class_label

    _smr_in = {
        "run_id": runtime_payload["run_id"],
        "lane_id": "ibm_narrative",
        "prompt_id": PROMPT_ID,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "output_payload_hash": (parsed_for_x2 or {}).get("output_payload_hash"),
        "claim_ledger_hash": (parsed_for_x2 or {}).get("claim_ledger_hash"),
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
                "x2_narrative_seniority_floor",
                "x2_narrative_no_consulting_language",
                "x2_narrative_technical_specificity_floor",
                "x2_narrative_not_bullet_recap",
                "x2_narrative_upstream_graph_proof_required",
                "x2_narrative_base_prose_ngram_overlap",
                "x2_narrative_e0_ngram_overlap",
            ],
        },
    }
    merge_normalized_srfs_reporting_into_dict(
        _smr_in,
        section_id="ibm_narrative",
        runtime_payload=runtime_payload,
        x2_gates=x2,
        selected_fact_plan=l2_output.get("selected_fact_plan") if isinstance(l2_output, dict) else None,
        claim_ledger=claim_ledger,
    )
    write_json(artifact_dir / "section_metric_receipt.json", _smr_in)

    write_json(
        artifact_dir / "real_l2_generation_result.json",
        rl2,
    )

    banner_lines: list[str] = []
    allow_exit = bool(getattr(args, "allow_non_allow_exit_zero", False))
    if allow_exit and x3.x3_code != "X3_ALLOW":
        banner_lines.extend(
            [
                "*** PROCESS EXIT OVERRIDDEN FOR INSPECTION ONLY. PRODUCT X3 IS NOT ALLOW.",
                "*** x3_disposition.json is authoritative for disposition; CLI exit codes may not reflect authorization.",
                "",
            ]
        )
    if judge_allowed_mock:
        banner_lines.extend(["Mocked judges cannot satisfy clean X3 ALLOW.", ""])

    lines = [
        *banner_lines,
        "IBM_NARRATIVE_OUTPUT:",
        narrative if narrative else f"BLOCKED: {parse_error}",
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
    lines.extend(["", "X3_DISPOSITION:", json.dumps(x3.to_dict(), indent=2), "", "L6_SHADOW_EVAL_PACKAGE:", str(artifact_dir / "l6_shadow_eval_package.json"), "offline_only=true"])
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
        "ibm_narrative",
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
        section_id="ibm_narrative",
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
        decisive_accounting_label=decisive_accounting_label_value,
        shell_exit_overridden_for_inspection=bool(getattr(args, "allow_non_allow_exit_zero", False)),
        product_authorized=bool(x3.pass_),
        x3_json_source_of_truth=True,
        not_release_signoff=True,
        generation_class=generation_class_label,
        judge_class=judge_class_label,
        proof_class=proof_class_label,
        certification_class=certification_class_label,
        run_bundle_index_document_metadata={
            "generation_class": generation_class_label,
            "judge_class": judge_class_label,
            "proof_class": proof_class_label,
            "certification_class": certification_class_label,
        },
    )
    exit_code = 0 if allow_non_allow_exit_zero_ok(args) else (0 if x3.x3_code == "X3_ALLOW" else 2)
    return {
        "artifact_dir": artifact_dir,
        "repo_root": REPO_ROOT,
        "lane_key": LANE_KEY,
        "args": args,
        "runtime_payload": runtime_payload,
        "section_compiled": section_compiled,
        "messages": messages,
        "prompt_hash": prompt_hash,
        "input_payload_hash": input_payload_hash,
        "x3": x3,
        "output_text": output_text,
        "runtime_generation_status": runtime_generation_status,
        "allowed_fact_ids": allowed_fact_ids,
        "exit_code": exit_code,
    }




def run_ibm_narrative_execution(
    args: argparse.Namespace,
    *,
    artifact_dir_override: Path | None = None,
    trace_runtime_path: str = "apps_rg.runtime.sections.ibm_narrative_lane_runtime",
    print_output: bool = False,
) -> dict[str, Any]:
    """Compat alias — canonical trace path is sections.ibm_narrative_lane."""
    return run_ibm_narrative_lane_execution(
        args,
        artifact_dir_override=artifact_dir_override,
        trace_runtime_path=trace_runtime_path,
        print_output=print_output,
    )


__all__ = ["run_ibm_narrative_lane_execution", "run_ibm_narrative_execution"]
