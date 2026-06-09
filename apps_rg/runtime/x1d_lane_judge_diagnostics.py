"""Per-lane X1D judge diagnostics for E2E proof (apps_rg-local).

Separates preflight credential availability from runtime judge execution outcomes and quality.
Used by whole-run exit reason codes and lane-dev diagnostics.

Does not import agentic_core.
"""

from __future__ import annotations

from typing import Any, Mapping

from apps_rg.runtime.section_judge_policy import REQUIRED_JUDGE_PROVIDER_KEYS

# Rollup column -> provider_key (matches generated_lane_rollup judge_rows)
_COL_TO_PROVIDER: dict[str, str] = {
    "gemini": "gemini_pro",
    "openai": "openai_chatgpt",
    "anthropic": "anthropic_claude",
}
_PROVIDER_TO_COL: dict[str, str] = {provider: col for col, provider in _COL_TO_PROVIDER.items()}


def _status_upper(raw: Any) -> str:
    return str(raw or "").strip().upper()


def classify_judge_status(
    raw_status: Any,
    *,
    preflight_credential_available: bool,
) -> dict[str, Any]:
    """Map a lane rollup provider status string to a stable category.

    Returns keys: mapped_judge_status, model_backed, execution_mismatch, quality_fail, unknown,
    provider_unavailable_at_execution, schema_or_parser_blocked, rate_limit_blocked, error_class.
    """
    raw = _status_upper(raw_status)
    out: dict[str, Any] = {
        "raw_judge_status": str(raw_status or "").strip(),
        "mapped_judge_status": "",
        "model_backed": None,
        "execution_mismatch": False,
        "quality_fail": False,
        "unknown": False,
        "provider_unavailable_at_execution": False,
        "schema_or_parser_blocked": False,
        "rate_limit_blocked": False,
        "error_class": "",
    }

    if not raw or raw in {"UNKNOWN", "MISSING"}:
        out["mapped_judge_status"] = "UNKNOWN"
        out["unknown"] = True
        return out

    if "MODEL_BACKED_PASS" in raw or raw.startswith("MODEL_BACKED_PASS"):
        out["mapped_judge_status"] = "MODEL_BACKED_PASS"
        out["model_backed"] = True
        return out

    if "MODEL_BACKED_FAIL" in raw:
        out["mapped_judge_status"] = "MODEL_BACKED_FAIL"
        out["model_backed"] = True
        out["quality_fail"] = True
        return out

    if raw.startswith("BLOCKED_SCHEMA_VALIDATION_ERROR") or raw.startswith("BLOCKED_RESPONSE_PARSE_ERROR"):
        out["schema_or_parser_blocked"] = True
        out["error_class"] = "SCHEMA_OR_RESPONSE_PARSE_BLOCKED"
        out["provider_unavailable_at_execution"] = True
        out["mapped_judge_status"] = "JUDGE_SCHEMA_OR_PARSER_BLOCKED"
        return out

    if raw.startswith("BLOCKED_RATE_LIMIT") or "RATE_LIMIT" in raw:
        out["rate_limit_blocked"] = True
        out["error_class"] = "PROVIDER_RATE_LIMIT_AT_EXECUTION"
        out["provider_unavailable_at_execution"] = True
        if preflight_credential_available:
            out["mapped_judge_status"] = "JUDGE_EXECUTION_PROVIDER_MISMATCH"
            out["execution_mismatch"] = True
        else:
            out["mapped_judge_status"] = "PROVIDER_UNAVAILABLE"
        return out

    if "BLOCKED" in raw or "UNAVAILABLE" in raw:
        out["provider_unavailable_at_execution"] = True
        out["error_class"] = "BLOCKED_OR_UNAVAILABLE"
        if preflight_credential_available:
            out["mapped_judge_status"] = "JUDGE_EXECUTION_PROVIDER_MISMATCH"
            out["execution_mismatch"] = True
        else:
            out["mapped_judge_status"] = "PROVIDER_UNAVAILABLE"
        return out

    out["mapped_judge_status"] = "UNKNOWN"
    out["unknown"] = True
    return out


def _judges_blob_to_list(blob: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if blob is None:
        return []
    if isinstance(blob, list):
        return [x for x in blob if isinstance(x, dict)]
    j = blob.get("judges")
    if isinstance(j, list):
        return [x for x in j if isinstance(x, dict)]
    return []


def _judge_blob_by_key(blob_list: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for ju in blob_list:
        pk = ju.get("provider_key")
        if pk is not None:
            out[str(pk)] = ju
    return out


def _infer_execution_attempted(blob: dict[str, Any] | None, rollup_enum: str) -> bool:
    if not str(rollup_enum or "").strip():
        return False
    if blob is None:
        return bool(str(rollup_enum or "").strip())
    msg = str(blob.get("exact_provider_error") or "").lower()
    if "environment variable not set" in msg:
        return False
    eval_mode = str(blob.get("evaluator_mode") or "")
    stat = str(blob.get("provider_status") or rollup_enum or "")
    if stat.startswith("MISSING"):
        return False
    # Blocked-but-attempted (HTTP/SDK path ran) retains provider_blocked True with an error artifact.
    if eval_mode.startswith("BLOCKED"):
        return True
    if eval_mode == "MODEL_BACKED":
        return True
    return bool(str(stat or rollup_enum).strip())


def _quality_reason_tail(blob: dict[str, Any] | None, mapped: str) -> str:
    if mapped != "MODEL_BACKED_FAIL" or not blob:
        return ""
    findings = blob.get("findings") or []
    if isinstance(findings, list) and findings:
        parts = []
        for f in findings[:6]:
            if str(f).strip():
                parts.append(str(f).strip())
        joined = "; ".join(parts)
        return joined[:720] + ("…" if len(joined) > 720 else "")
    return ""


def _error_code_and_class_from_blob(blob: dict[str, Any] | None) -> tuple[str, str]:
    if not blob:
        return "", ""
    err_txt = str(blob.get("exact_provider_error") or "")
    lt = err_txt.lower()
    pk = str(blob.get("provider_key") or "")
    prefix = f"{pk}:" if pk else ""

    if "429" in err_txt or "resource_exhausted" in lt:
        return "HTTP_429", f"{prefix}quota_or_rate_limit"
    if "401" in err_txt:
        return "HTTP_401", f"{prefix}auth_error"
    if "403" in err_txt:
        return "HTTP_403", f"{prefix}forbidden"

    ev = str(blob.get("evaluator_mode") or "")
    st = str(blob.get("provider_status") or "")
    if ev.startswith("BLOCKED_RATE_LIMIT") or st.startswith("BLOCKED_RATE_LIMIT"):
        return "BLOCKED_RATE_LIMIT", f"{prefix}rate_limit_adapter"
    if ev.startswith("BLOCKED_SCHEMA") or st.startswith("BLOCKED_SCHEMA"):
        return "BLOCKED_SCHEMA_PATH", f"{prefix}schema_validation_adapter"
    if ev.startswith("BLOCKED_RESPONSE_PARSE") or st.startswith("BLOCKED_RESPONSE_PARSE"):
        return "BLOCKED_PARSE_PATH", f"{prefix}response_parse_adapter"

    return "", ""


def _rollup_gemini_and_anthropic_notes(
    *,
    lanes_out: Mapping[str, Any],
    lane_blobs_map: Mapping[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    gem_seen: dict[str, int] = {}
    anth_seen: dict[str, int] = {}
    fixes: list[str] = []

    for lane_key, lj in lane_blobs_map.items():
        by_pk = _judge_blob_by_key(list(lj))
        g = by_pk.get("gemini_pro")
        if isinstance(g, dict):
            ecc, ech = _error_code_and_class_from_blob(g)
            err = str(g.get("exact_provider_error") or "").lower()
            if "429" in err or "resource_exhausted" in err or ecc == "HTTP_429":
                gem_seen["OBSERVED_HTTP_429_OR_QUOTA"] = gem_seen.get("OBSERVED_HTTP_429_OR_QUOTA", 0) + 1
            elif "401" in err or "403" in err:
                gem_seen["OBSERVED_HTTP_401_OR_403"] = gem_seen.get("OBSERVED_HTTP_401_OR_403", 0) + 1
            elif ecc:
                gem_seen.setdefault(ecc, 0)
                gem_seen[ecc] += 1
        ac = by_pk.get("anthropic_claude")
        if isinstance(ac, dict):
            st = _status_upper(ac.get("provider_status"))
            if "MODEL_BACKED_FAIL" in st:
                findings = "; ".join(str(x) for x in list(ac.get("findings") or [])[:5])
                key = findings[:240] if findings.strip() else "MODEL_BACKED_FAIL_NO_FINDINGS_DETAIL"
                anth_seen[key] = anth_seen.get(key, 0) + 1
            ecc, ech = _error_code_and_class_from_blob(ac)
            if ecc or ech:
                k = ecc or ech
                anth_seen[k] = anth_seen.get(k, 0) + 1

    fixes.append(
        "Preflight (x1d_judge_policy) checks non-empty primary API env vars only — it does "
        "not certify live quota, RPM/RPD tiers, billing, model allowlists, or network reachability."
    )
    fixes.append(
        "Gemini judge HTTP 429 with RESOURCE_EXHAUSTED/free-tier quotas is classified as BLOCKED_RATE_LIMIT "
        "(apps_rg.runtime.judges.executive_summary_x1d) with bounded retries (APPS_RG_GEMINI_JUDGE_MAX_RETRIES)."
    )
    fixes.append(
        "Anthropic MODEL_BACKED_FAIL rows carry model-backed evaluator_mode=MODEL_BACKED — classify as judge "
        "quality/threshold failures, distinct from BLOCKED_PROVIDER_UNAVAILABLE parsing."
    )

    return {
        "gemini_signals_observed": gem_seen if gem_seen else {"UNKNOWN": "no_gemini_failure_blob_signal"},
        "anthropic_signals_observed": anth_seen
        if anth_seen
        else {"UNKNOWN": "no_anthropic_model_backed_fail_blob_signal"},
        "fix_applied": fixes,
        "lanes_inspected_keys": sorted(lanes_out.keys()),
    }


def build_x1d_lane_judge_diagnostics(
    judge_policy: Mapping[str, Any],
    judge_rows: list[dict[str, Any]],
    lane_x1d_judge_blobs: Mapping[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Build ``x1d_lane_judge_diagnostics`` for CI artifact + whole-run breakdown.

    ``judge_rows`` entries match prove harness: keys ``lane``, ``gemini``, ``openai``, ``anthropic``,
    optional ``blocked_judges``, ``soft_failed_judges``, ``x3_code``.

    When ``lane_x1d_judge_blobs`` maps lane -> judges list (from ``x1d_llm_judge_outputs.json``),
    per-judge artifact fields enrich ``judge_results`` (error tails, attempted flags, etc.).
    """
    required = list(REQUIRED_JUDGE_PROVIDER_KEYS)
    blobs_in = lane_x1d_judge_blobs if lane_x1d_judge_blobs is not None else {}
    pp = dict(judge_policy.get("per_provider") or {})
    avail_set = set(judge_policy.get("available_judges") or [])

    lanes_out: dict[str, Any] = {}
    exec_mismatch_list: list[dict[str, str]] = []
    model_pass_ct = 0
    model_fail_ct = 0
    unknown_ct = 0
    provider_unavail_ct = 0
    schema_parser_ct = 0

    blobs_map: dict[str, list[dict[str, Any]]] = {}

    for row in judge_rows:
        lane = str(row.get("lane") or "").strip() or "unknown_lane"
        lane_bucket_pass: list[str] = []
        lane_bucket_fail: list[str] = []
        lane_bucket_unk: list[str] = []
        lane_bucket_pu: list[str] = []
        lane_mismatch: list[str] = []
        lane_schema_parser: list[str] = []
        lane_x3_code = str(row.get("x3_code") or "")

        raw_lane_blob = blobs_in.get(lane) if isinstance(blobs_in, Mapping) else None
        if isinstance(raw_lane_blob, list):
            lj_norm = [x for x in raw_lane_blob if isinstance(x, dict)]
        elif isinstance(raw_lane_blob, dict):
            lj_norm = _judges_blob_to_list(raw_lane_blob)
        else:
            lj_norm = []

        blobs_map[lane] = lj_norm if isinstance(lj_norm, list) else []
        by_pk_blob = _judge_blob_by_key(blobs_map[lane])

        judge_results: list[dict[str, Any]] = []

        for pkey in required:
            col = _PROVIDER_TO_COL.get(pkey, pkey)
            raw_row = row.get(col)
            pre_ok = pkey in avail_set or bool((pp.get(pkey) or {}).get("credential_env_non_empty"))
            info = classify_judge_status(raw_row, preflight_credential_available=pre_ok)
            mapped = str(info.get("mapped_judge_status") or "")
            blob_raw = by_pk_blob.get(pkey)
            blob = blob_raw if isinstance(blob_raw, dict) else None
            rollup_enum = str(raw_row or "").strip()

            ecc, ech = _error_code_and_class_from_blob(blob)

            executed = _infer_execution_attempted(blob, rollup_enum)

            if mapped == "MODEL_BACKED_PASS":
                lane_bucket_pass.append(pkey)
                model_pass_ct += 1
            elif mapped == "MODEL_BACKED_FAIL":
                lane_bucket_fail.append(pkey)
                model_fail_ct += 1
            elif mapped == "JUDGE_EXECUTION_PROVIDER_MISMATCH":
                lane_mismatch.append(pkey)
                exec_mismatch_list.append({"lane": lane, "provider_key": pkey})
            elif mapped == "JUDGE_SCHEMA_OR_PARSER_BLOCKED":
                lane_schema_parser.append(pkey)
                schema_parser_ct += 1
            elif mapped == "PROVIDER_UNAVAILABLE":
                lane_bucket_pu.append(pkey)
                provider_unavail_ct += 1
            elif mapped == "UNKNOWN":
                lane_bucket_unk.append(pkey)
                unknown_ct += 1

            dq = ""
            if info.get("schema_or_parser_blocked"):
                dq = (
                    "SCHEMA_OR_RESPONSE_PARSE_BLOCKED while credentials were configured — classify apart from MODEL_BACKED_QUALITY_FAIL"
                    if info.get("mapped_judge_status") == "JUDGE_SCHEMA_OR_PARSER_BLOCKED"
                    else "Schema/response parse blocker"
                )
            elif executed and info.get("rate_limit_blocked"):
                dq = (
                    "RATE_LIMIT_OR_QUOTA at execution while credentials present — audited as "
                    "JUDGE_EXECUTION_PROVIDER_MISMATCH against preflight (env present != quota)."
                )
            elif info.get("execution_mismatch"):
                dq = (
                    "preflight credentials present but runtime reported blocked/unavailable — "
                    "classify as JUDGE_EXECUTION_PROVIDER_MISMATCH"
                )
            elif info.get("quality_fail"):
                dq = "MODEL_BACKED_FAIL — judge call ran but score/threshold/decisive_failure failed"

            err_tail = ""
            if isinstance(blob, dict) and blob.get("exact_provider_error"):
                er = str(blob.get("exact_provider_error"))
                err_tail = er[:560] + ("…" if len(er) > 560 else "")

            mb_explicit = isinstance(blob, dict) and str(blob.get("evaluator_mode") or "") == "MODEL_BACKED"
            model_backed_flag = mapped in {"MODEL_BACKED_PASS", "MODEL_BACKED_FAIL"} or mb_explicit

            judge_results.append(
                {
                    "provider_key": pkey,
                    "provider_type": (judge_policy.get("provider_types") or {}).get(
                        pkey, "external_cloud_llm_judge"
                    ),
                    "preflight_available": pre_ok,
                    "preflight_credential_available": pre_ok,
                    "execution_attempted": executed,
                    "execution_status": str(
                        (blob.get("provider_status") if blob else "")
                        or (blob.get("evaluator_mode") if blob else "")
                        or rollup_enum
                        or ""
                    ).strip(),
                    "raw_judge_status_enum": rollup_enum,
                    "mapped_judge_status_enum": mapped,
                    "model_backed": bool(model_backed_flag),
                    "error_code": ecc,
                    "error_class": ech or str(info.get("error_class") or ""),
                    "quality_reason": _quality_reason_tail(blob, mapped),
                    "decisive_reason": dq,
                    "exact_provider_error_tail": err_tail,
                    "judge_evaluator_mode": str(blob.get("evaluator_mode") or "") if blob else "",
                    "lane_x3_code": lane_x3_code,
                }
            )

        decisive = ""
        if lane_schema_parser:
            decisive = (
                "SCHEMA_OR_RESPONSE_PARSE_BLOCKED for providers "
                f"{lane_schema_parser!r} — separate from MODEL_BACKED quality fails"
            )
        elif lane_mismatch:
            decisive = (
                f"One or more providers BLOCKED/UNAVAILABLE/RATE_LIMIT at execution while "
                f"preflight marked credentials env present {lane_mismatch!r}"
            )
        elif lane_bucket_fail:
            decisive = (
                "MODEL_BACKED_FAIL on providers "
                f"{lane_bucket_fail!r} — score/threshold or decisive_failure (distinct from credential absence)."
            )
        elif lane_bucket_unk:
            decisive = f"Unknown/missing judge status for providers {lane_bucket_unk!r}"

        lanes_out[lane] = {
            "x3_code": lane_x3_code,
            "required_judges": list(required),
            "judge_results": judge_results,
            "provider_unavailable": lane_bucket_pu,
            "model_backed_pass": lane_bucket_pass,
            "model_backed_fail": lane_bucket_fail,
            "unknown": lane_bucket_unk,
            "provider_execution_mismatch": list(lane_mismatch),
            "provider_execution_schema_or_parser_blocked": lane_schema_parser,
            "lane_contract_pass": set(lane_bucket_pass) == set(required)
            and not lane_mismatch
            and not lane_bucket_fail
            and not lane_bucket_unk
            and not lane_bucket_pu
            and not lane_schema_parser,
            "decisive_reason": decisive,
        }

        # Compatibility aliases (prior diagnostic shape)
        lanes_out[lane]["execution_provider_mismatch"] = lanes_out[lane]["provider_execution_mismatch"]

    every_lane_contract_pass = bool(judge_rows) and all(
        bool(lanes_out.get(str(r.get("lane") or ""), {}).get("lane_contract_pass"))
        for r in judge_rows
    )

    rollup_decision = "PASS"
    rollup_reason = "All lanes: three contract judges MODEL_BACKED_PASS with no mismatch or unknown rows"
    if not judge_rows:
        rollup_decision = "NOT_AVAILABLE"
        rollup_reason = "No judge_rows from rollup"
    elif not every_lane_contract_pass:
        rollup_decision = "PARTIAL"
        if exec_mismatch_list:
            rollup_reason = (
                f"JUDGE_EXECUTION_PROVIDER_MISMATCH on {len(exec_mismatch_list)} lane/provider pair(s): "
                f"{exec_mismatch_list[:12]!r}"
            )
        elif schema_parser_ct:
            rollup_reason = f"SCHEMA_OR_RESPONSE_PARSER_BLOCKED occurrences={schema_parser_ct}"
        elif model_fail_ct:
            rollup_reason = (
                f"MODEL_BACKED_FAIL count={model_fail_ct} (judge quality / threshold — not provider quorum)."
            )
        elif unknown_ct:
            rollup_reason = f"UNKNOWN judge status count={unknown_ct}"
        elif provider_unavail_ct:
            rollup_reason = (
                f"PROVIDER_UNAVAILABLE at execution count={provider_unavail_ct} (preflight did not mark available)"
            )
        else:
            rollup_reason = "Lane rollup incomplete vs contract MODEL_BACKED_PASS for all providers"

    exec_qual = _rollup_gemini_and_anthropic_notes(lanes_out=lanes_out, lane_blobs_map=blobs_map)

    mismatch_events = exec_mismatch_list
    mismatch_count = len(mismatch_events)

    return {
        "lanes": lanes_out,
        "rollup_decision": rollup_decision,
        "rollup_decisive_reason": rollup_reason,
        "execution_quality_rollup": exec_qual,
        "execution_mismatch_events": mismatch_events,
        "provider_execution_mismatch_count": mismatch_count,
        "model_backed_pass_count": model_pass_ct,
        "model_backed_fail_count": model_fail_ct,
        "unknown_count": unknown_ct,
        "counts": {
            "model_backed_pass": model_pass_ct,
            "model_backed_fail": model_fail_ct,
            "unknown": unknown_ct,
            "provider_unavailable": provider_unavail_ct,
            "execution_mismatch": mismatch_count,
            "schema_parser_blocked": schema_parser_ct,
        },
        "failure_breakdown_for_exit": {
            "x1d_judge_execution_mismatch": bool(exec_mismatch_list),
            "x1d_judge_model_backed_fail": model_fail_ct > 0,
            "x1d_judge_unknown_result": unknown_ct > 0,
            "x1d_judge_provider_unavailable_row": provider_unavail_ct > 0
            and (judge_policy.get("quorum_satisfied")),
            "x1d_judge_schema_or_parser_blocked": schema_parser_ct > 0,
        },
    }


def failure_breakdown_for_signals(diag: Mapping[str, Any]) -> dict[str, bool]:
    """Flatten diagnostics into ``compute_whole_run_exit`` boolean flags."""
    fb = diag.get("failure_breakdown_for_exit")
    if isinstance(fb, dict):
        return {k: bool(v) for k, v in fb.items()}
    return {
        "x1d_judge_execution_mismatch": False,
        "x1d_judge_model_backed_fail": False,
        "x1d_judge_unknown_result": False,
        "x1d_judge_provider_unavailable_row": False,
        "x1d_judge_schema_or_parser_blocked": False,
    }
