"""Claude-only pool selector: score self-consistency candidates and pick per-slot winners."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Literal

from apps_rg.runtime.judges.executive_summary_x1d import (
    PROVIDERS,
    JudgeOutput,
    _artifact_path,
    _extract_anthropic_message_text,
    _extract_json_from_text,
    _resolve_anthropic_model,
    build_x1d_judge_system_prompt,
)
from apps_rg.runtime.env_bootstrap import bootstrap_apps_rg_env
from apps_rg.runtime.reasoning.bullet_lane_self_consistency import SelfConsistencyPath
from apps_rg.runtime.judges.employment_bullet_judge_rubric import pool_selector_scoring_instruction
from apps_rg.runtime.reasoning.competencies_graph_pool import (
    COMPETENCIES_CANDIDATE_CATEGORY_COUNT,
    COMPETENCIES_FINAL_CATEGORY_COUNT,
    COMPETENCIES_SC_PATH_COUNT,
    merge_competencies_graph_pool_top_eight,
    min_competencies_selection_score,
)
from apps_rg.runtime.reasoning.employment_bullet_pool import (
    FINAL_BULLET_COUNT,
    is_employment_bullet_lane,
    min_selection_score_for_lane,
    sc_path_count_for_lane,
)
from apps_rg.runtime.sections.executive_summary_context_limits import (
    resolve_bullet_selector_briefing_max_chars,
    resolve_bullet_selector_jd_max_chars,
)

SlotKind = Literal["bullets", "competencies"]


@dataclass(frozen=True)
class PoolSelectionResult:
    merged_parsed: dict[str, Any]
    selections: list[dict[str, Any]]
    judge_output: JudgeOutput | None
    selection_mode: str
    source_path_by_slot: dict[str, int]


def _sha16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _bullet_by_id(parsed: dict[str, Any], bullet_id: str) -> dict[str, Any] | None:
    for row in parsed.get("bullets") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("bullet_id") or "").strip() == bullet_id:
            return row
    return None


def inject_positional_bullet_ids_into_pool(
    paths: list[SelfConsistencyPath],
    required_bullet_ids: tuple[str, ...] | None,
) -> int:
    """Assign bullet_id positionally to pool samples that omit it.

    Closes Bug:BulletPoolSelectorBulletIdMissing (Brown SVP full_resume_183cf9252e02 ibm_bullets
    X3_BLOCK loop). Qwen self-consistency samples often emit bullets shaped
    ``{bullet_theme, bullet_text}`` without ``bullet_id``. ``_bullet_by_id`` then returns ``None``
    for every required slot, ``_format_bullet_pool`` writes ``[bid] MISSING`` for all 20 paths, and
    ``run_claude_bullet_pool_selection`` produces zero merged bullets — even though Qwen's text
    is fully populated. We replicate the canonical positional fallback already in
    ``ibm_bullets_lane.normalize_parsed_output`` lines 268-270 / equivalents in unify_bullets
    so the selector sees a non-empty pool.

    Returns the number of bullets that received a positional bullet_id assignment.
    Mutates ``path.parsed`` rows in place. Safe to call when ``required_bullet_ids`` is None or
    empty (no-op) — selector callers that don't require slot mapping keep prior behavior.
    """
    if not required_bullet_ids:
        return 0
    injected = 0
    for path in paths:
        parsed = path.parsed if path is not None else None
        if not isinstance(parsed, dict):
            continue
        bullets = parsed.get("bullets")
        if not isinstance(bullets, list):
            continue
        for idx, row in enumerate(bullets):
            if not isinstance(row, dict):
                continue
            existing = str(row.get("bullet_id") or "").strip()
            if existing:
                continue
            if idx >= len(required_bullet_ids):
                break
            text = str(row.get("bullet_text") or "").strip()
            if not text:
                continue
            row["bullet_id"] = required_bullet_ids[idx]
            row.setdefault("bullet_id_origin", "positional_pool_fallback")
            injected += 1
    return injected


def _as_str_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _allowed_fact_ids_from_context(targeting_context: dict[str, Any] | None) -> set[str]:
    return set(_as_str_list((targeting_context or {}).get("allowed_fact_ids")))


def _source_id_allowed(source_id: str, allowed_fact_ids: set[str]) -> bool:
    sid = str(source_id or "").strip()
    if not sid:
        return False
    if not allowed_fact_ids:
        return True
    if sid in allowed_fact_ids:
        return True
    root = sid.split("_metric_", 1)[0]
    return root in allowed_fact_ids


def _candidate_source_ids(row: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    ids.extend(_as_str_list(row.get("source_fact_ids")))
    ids.extend(_as_str_list(row.get("source_fact_id")))
    return ids


def _filter_claim_ledger_for_allowed_sources(
    claim_ledger: Any,
    allowed_fact_ids: set[str],
) -> list[dict[str, Any]]:
    if not isinstance(claim_ledger, list):
        return []
    out: list[dict[str, Any]] = []
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        sids = _candidate_source_ids(row)
        if not allowed_fact_ids or (sids and all(_source_id_allowed(s, allowed_fact_ids) for s in sids)):
            out.append(dict(row))
    return out


def _selector_requires_valid_candidates(
    *,
    slot_kind: SlotKind,
    targeting_context: dict[str, Any] | None,
) -> bool:
    if slot_kind != "bullets":
        return False
    tc = targeting_context or {}
    return bool(tc.get("selector_requires_valid_candidates")) and bool(
        _allowed_fact_ids_from_context(tc)
    )


def _selector_valid_bullet_paths(
    paths: list[SelfConsistencyPath],
    *,
    required_bullet_ids: tuple[str, ...],
    targeting_context: dict[str, Any] | None,
) -> tuple[list[SelfConsistencyPath], dict[str, Any]]:
    """Return selector-visible paths after deterministic source/FEC eligibility filtering."""
    allowed_fact_ids = _allowed_fact_ids_from_context(targeting_context)
    strict = _selector_requires_valid_candidates(
        slot_kind="bullets",
        targeting_context=targeting_context,
    )
    receipt: dict[str, Any] = {
        "strict": strict,
        "allowed_fact_id_count": len(allowed_fact_ids),
        "required_bullet_ids": list(required_bullet_ids),
        "paths": [],
    }
    if not strict:
        return paths, receipt

    required = set(required_bullet_ids)
    filtered_paths: list[SelfConsistencyPath] = []
    for path in paths:
        parsed = path.parsed
        path_row: dict[str, Any] = {
            "path_index": path.path_index,
            "input_bullet_count": 0,
            "eligible_bullet_count": 0,
            "rejections": [],
        }
        if not isinstance(parsed, dict):
            path_row["rejections"].append({"reason": "parsed_missing"})
            filtered_paths.append(replace(path, parsed=None))
            receipt["paths"].append(path_row)
            continue

        eligible_bullets: list[dict[str, Any]] = []
        bullets = parsed.get("bullets") if isinstance(parsed.get("bullets"), list) else []
        path_row["input_bullet_count"] = len(bullets)
        for bullet in bullets:
            if not isinstance(bullet, dict):
                path_row["rejections"].append({"reason": "bullet_not_object"})
                continue
            bid = str(bullet.get("bullet_id") or "").strip()
            if bid not in required:
                path_row["rejections"].append(
                    {"bullet_id": bid, "reason": "bullet_id_not_required"}
                )
                continue
            source_ids = _candidate_source_ids(bullet)
            if not source_ids:
                path_row["rejections"].append(
                    {"bullet_id": bid, "reason": "missing_source_fact_ids"}
                )
                continue
            blocked = [sid for sid in source_ids if not _source_id_allowed(sid, allowed_fact_ids)]
            if blocked:
                path_row["rejections"].append(
                    {
                        "bullet_id": bid,
                        "reason": "source_fact_id_not_allowed",
                        "source_fact_ids": blocked,
                    }
                )
                continue
            eligible_bullets.append(dict(bullet))

        path_row["eligible_bullet_count"] = len(eligible_bullets)
        next_parsed: dict[str, Any] | None = None
        if eligible_bullets:
            next_parsed = dict(parsed)
            next_parsed["bullets"] = eligible_bullets
            next_parsed["claim_ledger"] = _filter_claim_ledger_for_allowed_sources(
                parsed.get("claim_ledger"),
                allowed_fact_ids,
            )
        filtered_paths.append(replace(path, parsed=next_parsed))
        receipt["paths"].append(path_row)

    return filtered_paths, receipt


def _category_by_label(parsed: dict[str, Any], label: str) -> dict[str, Any] | None:
    norm = label.strip().lower()
    for key in ("competencies", "categories"):
        for row in parsed.get(key) or []:
            if not isinstance(row, dict):
                continue
            if str(row.get("category_label") or "").strip().lower() == norm:
                return row
    return None


def _is_competencies_graph_pool(section_id: str, slot_kind: SlotKind) -> bool:
    return str(section_id or "").strip().lower() == "competencies" and slot_kind == "competencies"


def _competencies_graph_selection_prompt(
    *,
    pool_text: str,
    targeting_context: dict[str, Any] | None,
    min_score_threshold: float,
    regen_note: str = "",
) -> str:
    n_paths = COMPETENCIES_SC_PATH_COUNT
    n_final = COMPETENCIES_FINAL_CATEGORY_COUNT
    n_candidate = COMPETENCIES_CANDIDATE_CATEGORY_COUNT
    jd = (targeting_context or {}).get("jd_text") or ""
    briefing = (targeting_context or {}).get("briefing") or ""
    skills_ref = (targeting_context or {}).get("skills_graph_ref") or ""
    return (
        "You are the sole selector for competencies (graph_8x8_v1).\n"
        f"{n_paths} Qwen self-consistency paths produced candidate category sets (up to {n_candidate} labels). "
        f"Select exactly {n_final} categories — the top {n_final} by score that PASS graph/fact reality.\n"
        "Constraints:\n"
        "- augmented_skills_graph / selected_fact_plan are the only proof authority (JD and briefing are "
        "targeting emphasis only — never cite facts.skills or base-resume skill rows as proof).\n"
        "- Score each unique category_label variant on phrase_quality, evidence_alignment, distinctness, "
        "and anti_keyword_stuffing.\n"
        f"- Minimum score floor: only select variants with score >= {min_score_threshold:.2f} AND passes=true.\n"
        f"- Output exactly {n_final} selections when possible; each row must include category_label, "
        "path_index, score, passes, and rationale.\n"
        f"{regen_note}\n\n"
        f"JD (targeting only):\n{jd[:resolve_bullet_selector_jd_max_chars()]}\n\n"
        f"Briefing (targeting only):\n{briefing[:resolve_bullet_selector_briefing_max_chars()]}\n\n"
        f"Skills graph ref: {skills_ref}\n\n"
        "Return JSON only:\n"
        '{"selections":[{"category_label":"...","path_index":0,"score":0.85,"passes":true,"rationale":"..."}],'
        f'"pool_summary":{{"paths_scored":{n_paths},"final_category_count":{n_final},'
        f'"candidate_category_count":{n_candidate},'
        f'"min_score_threshold":{min_score_threshold:.2f},"selector":"anthropic_claude","mode":"graph_8x8"}}}}\n\n'
        "CANDIDATE POOL:\n"
        f"{pool_text}"
    )


def _format_bullet_pool(paths: list[SelfConsistencyPath], required_ids: tuple[str, ...]) -> str:
    blocks: list[str] = []
    for path in paths:
        if path.parsed is None:
            continue
        lines = [f"=== PATH {path.path_index} (temperature={path.temperature}) ==="]
        for bid in required_ids:
            bullet = _bullet_by_id(path.parsed, bid)
            if bullet is None:
                lines.append(f"[{bid}] MISSING")
            else:
                lines.append(f"[{bid}] text={bullet.get('bullet_text', '')}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _format_competency_pool(paths: list[SelfConsistencyPath]) -> str:
    blocks: list[str] = []
    for path in paths:
        if path.parsed is None:
            continue
        lines = [f"=== PATH {path.path_index} (temperature={path.temperature}) ==="]
        for cat in (path.parsed.get("competencies") or path.parsed.get("categories") or []):
            if not isinstance(cat, dict):
                continue
            label = str(cat.get("category_label") or "").strip()
            terms = cat.get("terms") or []
            phrase_bits: list[str] = []
            if isinstance(terms, list):
                for t in terms[:6]:
                    if isinstance(t, dict):
                        phrase_bits.append(str(t.get("text") or ""))
                    else:
                        phrase_bits.append(str(t))
            lines.append(f"[{label}] terms={', '.join(p for p in phrase_bits if p)}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _employment_bullet_selection_prompt(
    *,
    section_id: str,
    pool_text: str,
    required_bullet_ids: tuple[str, ...],
    targeting_context: dict[str, Any] | None,
    min_score_threshold: float,
    regen_note: str = "",
) -> str:
    n_final = FINAL_BULLET_COUNT.get(section_id, len(required_bullet_ids))
    n_paths = sc_path_count_for_lane(section_id)
    ids_line = ", ".join(required_bullet_ids)
    jd = (targeting_context or {}).get("jd_text") or ""
    briefing = (targeting_context or {}).get("briefing") or ""
    skills_ref = (targeting_context or {}).get("skills_graph_ref") or ""
    return (
        f"You are the sole selector for {section_id} employment bullets.\n"
        f"{n_paths} Qwen self-consistency paths produced candidate sets. Pick the top {n_final} bullets that PASS "
        f"quality — exactly one winning variant per bullet_id: {ids_line}.\n"
        "Constraints:\n"
        "- Skills graph / selected_fact_plan facts are the only proof authority (JD and briefing are targeting "
        "emphasis only — never copy JD phrases as proof).\n"
        f"- {pool_selector_scoring_instruction(section_id)}\n"
        f"- Minimum score floor: only select variants with score >= {min_score_threshold:.2f} AND passes=true. "
        f"If no variant for a slot meets the floor, set passes=false for that slot.\n"
        f"- Output exactly {n_final} selections when possible; each selected row must include score and passes.\n"
        f"{regen_note}\n\n"
        f"JD (targeting only):\n{jd[:resolve_bullet_selector_jd_max_chars()]}\n\n"
        f"Briefing (targeting only):\n{briefing[:resolve_bullet_selector_briefing_max_chars()]}\n\n"
        f"Skills graph ref: {skills_ref}\n\n"
        "Return JSON only:\n"
        '{"selections":[{"bullet_id":"...","path_index":0,"score":0.85,"passes":true,"rationale":"..."}],'
        f'"pool_summary":{{"paths_scored":{n_paths},"final_bullet_count":{n_final},'
        f'"min_score_threshold":{min_score_threshold:.2f},"selector":"anthropic_claude"}}}}\n\n'
        "CANDIDATE POOL:\n"
        f"{pool_text}"
    )


def _selection_prompt(
    *,
    section_id: str,
    slot_kind: SlotKind,
    pool_text: str,
    required_bullet_ids: tuple[str, ...] | None,
    targeting_context: dict[str, Any] | None,
    min_score_threshold: float | None = None,
    regen_note: str = "",
) -> str:
    if _is_competencies_graph_pool(section_id, slot_kind):
        floor = (
            min_score_threshold
            if min_score_threshold is not None
            else min_competencies_selection_score()
        )
        return _competencies_graph_selection_prompt(
            pool_text=pool_text,
            targeting_context=targeting_context,
            min_score_threshold=floor,
            regen_note=regen_note,
        )
    if slot_kind == "bullets" and is_employment_bullet_lane(section_id) and required_bullet_ids:
        floor = (
            min_score_threshold
            if min_score_threshold is not None
            else min_selection_score_for_lane(section_id)
        )
        return _employment_bullet_selection_prompt(
            section_id=section_id,
            pool_text=pool_text,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
            min_score_threshold=floor,
            regen_note=regen_note,
        )
    if slot_kind == "bullets":
        ids_line = ", ".join(required_bullet_ids or ())
        task = (
            f"Select the best bullet_text per bullet_id from the self-consistency pool for section {section_id}. "
            f"Required ids: {ids_line}. "
            "Score each variant on factual_support, impact_clarity, ats_alignment_without_stuffing, "
            "rewrite_quality, and distinctness across bullets. "
            "Pick exactly one winning path_index per bullet_id."
        )
        schema = (
            '{"selections":[{"bullet_id":"...","path_index":0,"score":0.0,"rationale":"..."}],'
            '"pool_summary":{"paths_scored":N,"selector":"anthropic_claude"}}'
        )
    else:
        task = (
            f"Select the best competency category block per category_label from the self-consistency pool "
            f"for section {section_id}. "
            "Score each variant on phrase_quality, evidence_alignment, distinctness across categories, "
            "and anti_keyword_stuffing. Pick exactly one winning path_index per category_label."
        )
        schema = (
            '{"selections":[{"category_label":"...","path_index":0,"score":0.0,"rationale":"..."}],'
            '"pool_summary":{"paths_scored":N,"selector":"anthropic_claude"}}'
        )
    ctx = ""
    if targeting_context:
        ctx = f"\nTargeting context (emphasis only, not proof): {json.dumps(targeting_context, ensure_ascii=False)[:1200]}\n"
    return (
        f"{task}\n{ctx}\n"
        "Return JSON only.\n"
        f"Schema: {schema}\n\n"
        "CANDIDATE POOL:\n"
        f"{pool_text}"
    )


def _parse_selections(text: str) -> dict[str, Any] | None:
    return _extract_json_from_text(text)


def _load_selection_doc_from_judge_artifacts(
    judge_out: JudgeOutput,
    artifact_dir: Path | None,
) -> dict[str, Any] | None:
    if artifact_dir is not None:
        parse_path = _artifact_path(
            "anthropic_claude",
            "provider_parse_result",
            artifact_base=artifact_dir,
        )
        if parse_path.is_file():
            try:
                doc = json.loads(parse_path.read_text(encoding="utf-8"))
                result = doc.get("result")
                if isinstance(result, dict) and isinstance(result.get("selections"), list):
                    return result
            except (json.JSONDecodeError, OSError):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                pass
        raw_path = _artifact_path(
            "anthropic_claude",
            "provider_response_raw",
            artifact_base=artifact_dir,
        )
        if raw_path.is_file():
            try:
                doc = json.loads(raw_path.read_text(encoding="utf-8"))
                text = _extract_anthropic_message_text(doc)
                return _parse_selections(text)
            except (json.JSONDecodeError, OSError, TypeError):  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
                pass
    if judge_out.rationale:
        return _parse_selections(str(judge_out.rationale))
    return None


def _call_anthropic_pool_selector(
    *,
    api_key: str,
    prompt: str,
    model: str,
    input_hash: str,
    model_source: str,
    artifact_dir: Path | None,
) -> tuple[JudgeOutput, dict[str, Any] | None]:
    """Anthropic call for pool JSON (not GRADE_ONLY rubric schema)."""
    import urllib.error
    import urllib.request
    from datetime import datetime, timezone

    from apps_rg.runtime.judges.executive_summary_x1d import (
        _judge_live_https_allowed_under_pytest,
        _make_blocked_output,
        _pytest_network_disabled_blocked_output,
        _resolved_x1d_judge_max_output_tokens,
        _write_artifact,
    )

    max_tokens = _resolved_x1d_judge_max_output_tokens(attempt=1)
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "system": build_x1d_judge_system_prompt(compact=True),
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }
    req_path = _artifact_path("anthropic_claude", "provider_request", artifact_base=artifact_dir)
    _write_artifact(
        req_path,
        {
            "payload": payload,
            "input_hash": input_hash,
            "purpose": "bullet_pool_claude_selector",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
    if not _judge_live_https_allowed_under_pytest():
        blocked = _pytest_network_disabled_blocked_output(
            provider_key="anthropic_claude",
            input_hash=input_hash,
            model=model,
            service_label="Anthropic",
        )
        return blocked, None

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw_response = response.read().decode()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        blocked = _make_blocked_output(
            "anthropic_claude",
            input_hash,
            "BLOCKED_PROVIDER_UNAVAILABLE",
            "BLOCKED_PROVIDER_UNAVAILABLE",
            f"Anthropic pool selector HTTP {exc.code}: {body[:400]}",
            model_name=model,
        )
        return blocked, None

    raw_path = _artifact_path("anthropic_claude", "provider_response_raw", artifact_base=artifact_dir)
    _write_artifact(raw_path, {"raw_response": raw_response, "input_hash": input_hash})
    try:
        data = json.loads(raw_response)
        text = _extract_anthropic_message_text(data)
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        blocked = _make_blocked_output(
            "anthropic_claude",
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            f"Anthropic pool selector parse error: {exc}",
            raw_response_ref=str(raw_path),
            model_name=model,
        )
        return blocked, None

    selection_doc = _parse_selections(text)
    sel_path = _artifact_path("anthropic_claude", "provider_parse_result", artifact_base=artifact_dir)
    _write_artifact(
        sel_path,
        {"result": selection_doc, "raw_response_ref": str(raw_path), "purpose": "bullet_pool_claude_selector"},
    )
    if selection_doc is None:
        blocked = _make_blocked_output(
            "anthropic_claude",
            input_hash,
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "BLOCKED_RESPONSE_PARSE_ERROR",
            "Pool selector JSON missing selections array",
            raw_response_ref=str(raw_path),
            model_name=model,
        )
        return blocked, None

    judge_stub = JudgeOutput(
        judge_id="x1d_anthropic_claude_bullet_pool_selector",
        provider_name="Anthropic Claude",
        provider_key="anthropic_claude",
        evaluator_mode="MODEL_BACKED",
        provider_status="MODEL_BACKED_PASS",
        model_name=model,
        provider_available=True,
        provider_blocked=False,
        exact_provider_error=None,
        raw_response_ref=str(raw_path),
        input_hash=input_hash,
        pass_=True,
        rationale=str(model_source),
    )
    return judge_stub, selection_doc


def _fallback_first_complete_path(
    paths: list[SelfConsistencyPath],
    *,
    slot_kind: SlotKind,
    required_bullet_ids: tuple[str, ...] | None,
    targeting_context: dict[str, Any] | None = None,
) -> PoolSelectionResult:
    for path in paths:
        if path.parsed is None:
            continue
        if slot_kind == "bullets" and required_bullet_ids:
            if all(_bullet_by_id(path.parsed, bid) is not None for bid in required_bullet_ids):
                return PoolSelectionResult(
                    merged_parsed=dict(path.parsed),
                    selections=[],
                    judge_output=None,
                    selection_mode="fallback_first_complete_path",
                    source_path_by_slot={bid: path.path_index for bid in required_bullet_ids},
                )
        elif slot_kind == "competencies":
            comps = path.parsed.get("competencies") or path.parsed.get("categories")
            if isinstance(comps, list) and len(comps) >= COMPETENCIES_FINAL_CATEGORY_COUNT:
                tc = targeting_context or {}
                merged, source_map = merge_competencies_graph_pool_top_eight(
                    paths,
                    [],
                    base_parsed=dict(path.parsed),
                    allowed_fact_ids=set(tc.get("allowed_fact_ids") or []),
                    allowed_skill_ids=set(tc.get("allowed_skill_ids") or []),
                    resume_support_blob_lower=str(tc.get("resume_support_blob_lower") or ""),
                )
                return PoolSelectionResult(
                    merged_parsed=merged,
                    selections=[],
                    judge_output=None,
                    selection_mode="competencies_graph_top_8_heuristic",
                    source_path_by_slot=source_map,
                )
    if slot_kind == "competencies":
        tc = targeting_context or {}
        merged, source_map = merge_competencies_graph_pool_top_eight(
            paths,
            [],
            base_parsed=paths[0].parsed if paths and paths[0].parsed else {},
            allowed_fact_ids=set(tc.get("allowed_fact_ids") or []),
            allowed_skill_ids=set(tc.get("allowed_skill_ids") or []),
            resume_support_blob_lower=str(tc.get("resume_support_blob_lower") or ""),
        )
        return PoolSelectionResult(
            merged_parsed=merged,
            selections=[],
            judge_output=None,
            selection_mode="competencies_graph_top_8_heuristic",
            source_path_by_slot=source_map,
        )
    base = paths[0].parsed if paths and paths[0].parsed else {}
    return PoolSelectionResult(
        merged_parsed=dict(base) if isinstance(base, dict) else {},
        selections=[],
        judge_output=None,
        selection_mode="fallback_empty",
        source_path_by_slot={},
    )


def _selection_passes(row: dict[str, Any]) -> bool:
    if "passes" not in row:
        return True
    val = row.get("passes")
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("true", "1", "yes")


def merge_bullet_selections(
    paths: list[SelfConsistencyPath],
    selections: list[dict[str, Any]],
    *,
    required_bullet_ids: tuple[str, ...],
    base_parsed: dict[str, Any] | None = None,
    min_score_threshold: float | None = None,
) -> tuple[dict[str, Any], dict[str, int]]:
    path_by_index = {p.path_index: p for p in paths}
    anchor = dict(base_parsed or (paths[0].parsed if paths else {}) or {})
    bullets_out: list[dict[str, Any]] = []
    source_map: dict[str, int] = {}

    for bid in required_bullet_ids:
        slot_selections = [
            s
            for s in selections
            if str(s.get("bullet_id") or "").strip() == bid and _selection_passes(s)
        ]
        if min_score_threshold is not None:
            slot_selections = [
                s for s in slot_selections if float(s.get("score") or 0.0) >= min_score_threshold
            ]
        sel = max(slot_selections, key=lambda s: float(s.get("score") or 0.0), default=None)
        if sel is None:
            sel = next((s for s in selections if str(s.get("bullet_id") or "").strip() == bid), None)
        path_idx = int(sel.get("path_index", 0)) if isinstance(sel, dict) else 0
        path = path_by_index.get(path_idx) or paths[0]
        bullet = _bullet_by_id(path.parsed or {}, bid) if path and path.parsed else None
        if bullet is None:
            for p in paths:
                if p.parsed and _bullet_by_id(p.parsed, bid):
                    bullet = _bullet_by_id(p.parsed, bid)
                    path_idx = p.path_index
                    break
        if bullet is not None:
            bullets_out.append(dict(bullet))
            source_map[bid] = path_idx

    merged = dict(anchor)
    merged["bullets"] = bullets_out
    ledger_rows: list[dict[str, Any]] = []
    for bid, pidx in source_map.items():
        src_path = path_by_index.get(pidx)
        if not src_path or not src_path.parsed:
            continue
        for row in src_path.parsed.get("claim_ledger") or []:
            if not isinstance(row, dict):
                continue
            sids = row.get("source_fact_ids") or []
            if bid in [str(x) for x in sids] or bid == str(row.get("bullet_id") or ""):
                ledger_rows.append(dict(row))
    if ledger_rows:
        merged["claim_ledger"] = ledger_rows
    elif anchor.get("claim_ledger"):
        merged["claim_ledger"] = list(anchor.get("claim_ledger") or [])
    return merged, source_map


def merge_competency_selections(
    paths: list[SelfConsistencyPath],
    selections: list[dict[str, Any]],
    *,
    base_parsed: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, int]]:
    path_by_index = {p.path_index: p for p in paths}
    anchor = dict(base_parsed or (paths[0].parsed if paths else {}) or {})
    labels_seen: set[str] = set()
    comps_out: list[dict[str, Any]] = []
    source_map: dict[str, int] = {}

    for sel in selections:
        if not isinstance(sel, dict):
            continue
        label = str(sel.get("category_label") or "").strip()
        if not label:
            continue
        path_idx = int(sel.get("path_index", 0))
        path = path_by_index.get(path_idx)
        cat = _category_by_label(path.parsed or {}, label) if path and path.parsed else None
        if cat is not None:
            comps_out.append(dict(cat))
            labels_seen.add(label.lower())
            source_map[label.lower()] = path_idx

    if not comps_out:
        for path in paths:
            if path.parsed and isinstance(path.parsed.get("competencies"), list):
                return dict(path.parsed), {}

    for path in paths:
        if not path.parsed:
            continue
        for cat in (path.parsed.get("competencies") or path.parsed.get("categories") or []):
            if not isinstance(cat, dict):
                continue
            label = str(cat.get("category_label") or "").strip()
            key = label.lower()
            if key and key not in labels_seen:
                comps_out.append(dict(cat))
                labels_seen.add(key)
                source_map[key] = path.path_index

    merged = dict(anchor)
    merged["competencies"] = comps_out
    if paths and paths[0].parsed and paths[0].parsed.get("claim_ledger"):
        merged["claim_ledger"] = list(paths[0].parsed.get("claim_ledger") or [])
    return merged, source_map


def run_claude_bullet_pool_selection(
    *,
    section_id: str,
    slot_kind: SlotKind,
    paths: list[SelfConsistencyPath],
    required_bullet_ids: tuple[str, ...] | None = None,
    targeting_context: dict[str, Any] | None = None,
    artifact_dir: Path | None = None,
    mode: str = "blocked_if_unavailable",
    min_score_threshold: float | None = None,
    regen_note: str = "",
) -> PoolSelectionResult:
    """Invoke Claude only; merge per-slot winners into one parsed section payload."""
    valid_paths = [p for p in paths if p.parsed is not None]
    if not valid_paths:
        return _fallback_first_complete_path(
            paths,
            slot_kind=slot_kind,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
        )

    validity_receipt: dict[str, Any] | None = None
    if slot_kind == "bullets":
        inject_positional_bullet_ids_into_pool(valid_paths, required_bullet_ids)
        valid_paths, validity_receipt = _selector_valid_bullet_paths(
            valid_paths,
            required_bullet_ids=required_bullet_ids or (),
            targeting_context=targeting_context,
        )
        valid_paths = [p for p in valid_paths if p.parsed is not None]
        if artifact_dir is not None and validity_receipt is not None:
            (artifact_dir / "bullet_pool_candidate_validity.json").write_text(
                json.dumps(validity_receipt, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        if not valid_paths and _selector_requires_valid_candidates(
            slot_kind=slot_kind,
            targeting_context=targeting_context,
        ):
            return PoolSelectionResult(
                merged_parsed={},
                selections=[],
                judge_output=None,
                selection_mode="blocked_no_selector_eligible_candidates",
                source_path_by_slot={},
            )
        pool_text = _format_bullet_pool(valid_paths, required_bullet_ids or ())
    else:
        pool_text = _format_competency_pool(valid_paths)

    prompt = _selection_prompt(
        section_id=section_id,
        slot_kind=slot_kind,
        pool_text=pool_text,
        required_bullet_ids=required_bullet_ids,
        targeting_context=targeting_context,
        min_score_threshold=min_score_threshold,
        regen_note=regen_note,
    )
    input_hash = _sha16(prompt)

    if mode == "mocked":
        return _fallback_first_complete_path(
            valid_paths,
            slot_kind=slot_kind,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
        )

    meta = PROVIDERS.get("anthropic_claude") or {}
    bootstrap_apps_rg_env()
    api_key = os.environ.get(str(meta.get("env", "ANTHROPIC_API_KEY")), "").strip()
    if not api_key:
        return _fallback_first_complete_path(
            valid_paths,
            slot_kind=slot_kind,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
        )

    model, model_source = _resolve_anthropic_model(meta, section_id=section_id)
    judge_out, parsed_sel = _call_anthropic_pool_selector(
        api_key=api_key,
        prompt=prompt,
        model=model,
        input_hash=input_hash,
        model_source=model_source,
        artifact_dir=artifact_dir,
    )

    if artifact_dir is not None:
        (artifact_dir / "bullet_pool_claude_selector_judge.json").write_text(
            json.dumps(judge_out.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if parsed_sel is None:
        parsed_sel = _load_selection_doc_from_judge_artifacts(judge_out, artifact_dir)
    if parsed_sel is None and judge_out.pass_ is False:
        return _fallback_first_complete_path(
            valid_paths,
            slot_kind=slot_kind,
            required_bullet_ids=required_bullet_ids,
            targeting_context=targeting_context,
        )

    selections = list((parsed_sel or {}).get("selections") or [])
    base = valid_paths[0].parsed
    tc = targeting_context or {}
    if slot_kind == "bullets" and required_bullet_ids:
        floor = min_score_threshold
        if floor is None and is_employment_bullet_lane(section_id):
            floor = min_selection_score_for_lane(section_id)
        merged, source_map = merge_bullet_selections(
            valid_paths,
            selections,
            required_bullet_ids=required_bullet_ids,
            base_parsed=base,
            min_score_threshold=floor,
        )
        selection_mode = "claude_employment_top_n_pass"
    elif _is_competencies_graph_pool(section_id, slot_kind):
        floor = min_score_threshold or min_competencies_selection_score()
        merged, source_map = merge_competencies_graph_pool_top_eight(
            valid_paths,
            selections,
            base_parsed=base,
            min_score_threshold=floor,
            allowed_fact_ids=set(tc.get("allowed_fact_ids") or []),
            allowed_skill_ids=set(tc.get("allowed_skill_ids") or []),
            resume_support_blob_lower=str(tc.get("resume_support_blob_lower") or ""),
        )
        selection_mode = "claude_competencies_top_8_pass"
    else:
        merged, source_map = merge_competency_selections(valid_paths, selections, base_parsed=base)
        selection_mode = "claude_per_slot_selection"

    return PoolSelectionResult(
        merged_parsed=merged,
        selections=selections,
        judge_output=judge_out,
        selection_mode=selection_mode,
        source_path_by_slot=source_map,
    )


__all__ = [
    "PoolSelectionResult",
    "merge_bullet_selections",
    "merge_competency_selections",
    "run_claude_bullet_pool_selection",
]
