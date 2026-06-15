"""Executive summary prompt token budget policy (apps_rg lane-local).

Deterministic pre-dispatch trim of **optional-only** prompt payload. Never silently alters the
evidence contract or generation prompt shape (SRFS arc, I0 sovereign regions, R0 schema body,
HIGH fact lines, INPUT_AUTHORITY). If optional trims cannot fit the budget, fail closed before
Qwen — do not dispatch a shape-degraded prompt that causes downstream 3-sentence / SRFS gate failures.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from apps_rg.runtime.bindings.section_prompt_adapter import SectionCompiledPrompt
from apps_rg.runtime.sections.executive_summary_context_limits import (
    CHARS_PER_TOKEN_ESTIMATE,
    DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX,
    ESTIMATE_SAFETY_MULTIPLIER,
    RESERVED_SYSTEM_SCHEMA_TOKENS,
    resolve_first_pass_input_utilization_max,
    resolve_provider_context_window,
)

SECTION_ID = "executive_summary"
FAIL_CLOSED_REASON = "TOKEN_BUDGET_EXCEEDED_AFTER_TRIM"
FAIL_CLOSED_REASON_FIRST_PASS_95PCT = "TOKEN_BUDGET_EXCEEDED_FIRST_PASS_95PCT"
FAIL_SHAPE_ALTERED = "EVIDENCE_CONTRACT_OR_PROMPT_SHAPE_ALTERED"

# Backward-compatible alias (tests/imports).
FIRST_PASS_INPUT_UTILIZATION_MAX = DEFAULT_FIRST_PASS_INPUT_UTILIZATION_MAX
_CONTEXT_SOURCE_ENV = "ENV_VLLM_MAX_MODEL_LEN"
_CONTEXT_SOURCE_SERVER = "SERVER_MODELS_METADATA"
_CONTEXT_SOURCE_UNKNOWN = "UNKNOWN"
TRIM_STRATEGY = "executive_summary_optional_trim_only_v2"
ESTIMATE_METHOD = "approximate_chars_div_3_with_safety_margin"

_CHARS_PER_TOKEN = CHARS_PER_TOKEN_ESTIMATE
_ESTIMATE_SAFETY_MULTIPLIER = ESTIMATE_SAFETY_MULTIPLIER
_RESERVED_SYSTEM_SCHEMA_TOKENS = RESERVED_SYSTEM_SCHEMA_TOKENS

_SLOT_MARKER_RE = re.compile(r"<!--\s*SLOT:\s*([A-Z0-9]+)\s*-->")
_FACT_LINE_RE = re.compile(r"^\s*-\s+([A-Za-z0-9_]+):\s+(.*)$", re.MULTILINE)

PROTECTED_COMPONENT_LABELS: tuple[str, ...] = (
    "system",
    "response_schema",
    "evidence_law",
    "allowed_source_fact_ids",
    "selected_role_fact_set",
    "claim_ledger_rules",
    "jd_targeting_only_rule",
)

# Optional-only trims (style/targeting). Shape-altering compressions are forbidden.
_OPTIONAL_TRIM_COMPONENTS: frozenset[str] = frozenset(
    {
        "e0_examples",
        "y0_style_preferences",
        "jd_briefing_prose",
        "jd_briefing_prose_tight",
        "jd_text_prose",
        "c0_optional_fact_line",
    }
)

_TRIM_NOTICE = "\n[# APPS_RG_EXEC_SUMMARY_TOKEN_BUDGET_TRIM]\n"

# SRFS generation-shape markers — must survive any applied trim when present in the pre-trim prompt.
_SRFS_SHAPE_MARKERS: tuple[str, ...] = (
    "SRFS_FIVE_PART_EXEC_ARCH_V1",
    "SRFS_SENTENCE_RESP_SEP_V1",
    "SELECTED_ROLE_FACT_SET_APPENDIX:",
    "x2_exec_summary_sentence_count_6",
    "x2_exec_summary_paragraph_max_words",
)

_I0_SOVEREIGN_REGIONS: tuple[tuple[str, str], ...] = (
    ("<authority_boundary", "</authority_boundary>"),
    ("<evidence_law", "</evidence_law>"),
    ("<output_contract", "</output_contract>"),
)


class ExecutiveSummaryTokenBudgetExceeded(Exception):
    """Fail-closed when protected prompt content cannot fit without altering evidence/shape."""

    def __init__(self, *, receipt: dict[str, Any]) -> None:
        self.receipt = receipt
        guidance = receipt.get("operator_guidance")
        summary = (
            str(guidance.get("operator_summary"))
            if isinstance(guidance, dict) and guidance.get("operator_summary")
            else None
        )
        super().__init__(summary or receipt.get("fail_closed_reason") or FAIL_CLOSED_REASON)


@dataclass(frozen=True)
class ContextWindowProvenance:
    provider_context_window: int
    provider_context_window_source: str
    server_context_window_verified: bool
    server_context_window_warning: str | None
    server_observed_context_window: int | None = None


def _truthy_env_flag(name: str) -> bool:
    return str(os.environ.get(name, "") or "").strip().lower() in ("1", "true", "yes", "on")


def _server_context_window_from_models_payload(
    payload: dict[str, Any],
    *,
    model_id: str,
) -> int | None:
    """Best-effort parse of vLLM/OpenAI-compatible ``/v1/models`` rows."""
    rows = payload.get("data") if isinstance(payload.get("data"), list) else []
    needle = str(model_id or "").strip().lower()
    for row in rows:
        if not isinstance(row, dict):
            continue
        rid = str(row.get("id") or "").strip()
        if needle and needle not in rid.lower():
            continue
        for key in ("max_model_len", "context_length", "max_context_length", "max_sequence_length"):
            raw = row.get(key)
            if raw is not None:
                try:
                    return max(4096, int(raw))
                except (TypeError, ValueError):
                    continue
        root = row.get("root")
        if isinstance(root, dict):
            for key in ("max_model_len", "context_length"):
                raw = root.get(key)
                if raw is not None:
                    try:
                        return max(4096, int(raw))
                    except (TypeError, ValueError):
                        continue
    return None


def resolve_context_window_provenance(*, model: str | None = None) -> ContextWindowProvenance:
    """Resolve context window with labeled provenance (W2.1). Auto-detect is opt-in only."""
    env_window = resolve_provider_context_window()

    # The Qwen/vLLM server ``/v1/models`` context-window probe was removed with the
    # local-model provider; the context window is the operator-declared section budget.
    return ContextWindowProvenance(
        provider_context_window=env_window,
        provider_context_window_source=_CONTEXT_SOURCE_ENV,
        server_context_window_verified=False,
        server_context_window_warning=(
            "operator-declared section context window; not server-proven (local provider removed)"
        ),
        server_observed_context_window=None,
    )


def context_window_provenance_receipt_fields(
    provenance: ContextWindowProvenance,
) -> dict[str, Any]:
    return {
        "provider_context_window": provenance.provider_context_window,
        "provider_context_window_source": provenance.provider_context_window_source,
        "server_context_window_verified": provenance.server_context_window_verified,
        "server_context_window_warning": provenance.server_context_window_warning,
        "server_observed_context_window": provenance.server_observed_context_window,
    }


def first_pass_95pct_limit_tokens(available_input_tokens: int) -> int:
    return max(0, int(available_input_tokens * resolve_first_pass_input_utilization_max()))


def first_pass_utilization_pct(estimated_tokens: int, available_input_tokens: int) -> float:
    if available_input_tokens <= 0:
        return 100.0 if estimated_tokens > 0 else 0.0
    return round(min(999.0, estimated_tokens / available_input_tokens * 100.0), 2)


def exceeds_first_pass_95pct_policy(estimated_tokens: int, available_input_tokens: int) -> bool:
    """W2.2: deterministic fail-closed when optional trim still leaves >95% utilization."""
    return estimated_tokens > first_pass_95pct_limit_tokens(available_input_tokens)


def _estimate_chars_to_tokens(char_count: int) -> int:
    if char_count <= 0:
        return 0
    return max(1, int((char_count // _CHARS_PER_TOKEN) * _ESTIMATE_SAFETY_MULTIPLIER))


def _runtime_input_source_hints(runtime_payload: dict[str, Any] | None) -> dict[str, str]:
    payload = runtime_payload if isinstance(runtime_payload, dict) else {}
    hints: dict[str, str] = {}
    for key in ("manual_brief", "briefing_path", "jd_path", "jd_file"):
        raw = str(payload.get(key) or "").strip()
        if raw:
            hints[key] = raw
    sel = payload.get("briefing_selection_receipt")
    if isinstance(sel, dict):
        for key in ("selected_path", "briefing_path", "source_path"):
            raw = str(sel.get(key) or "").strip()
            if raw:
                hints.setdefault("briefing_selected_path", raw)
    return hints


def build_token_budget_operator_guidance(
    receipt: dict[str, Any],
    *,
    runtime_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Actionable operator guidance when scratch dispatch is blocked for token budget."""
    payload = runtime_payload if isinstance(runtime_payload, dict) else {}
    after = int(receipt.get("compiled_prompt_tokens_after_trim") or 0)
    available = int(receipt.get("available_input_tokens") or 0)
    first_limit = int(receipt.get("first_pass_95pct_limit_tokens") or 0)
    util_pct = float(receipt.get("first_pass_utilization_pct") or 0.0)
    util_max = float(receipt.get("first_pass_input_utilization_max") or resolve_first_pass_input_utilization_max())
    fail_reason = str(receipt.get("fail_closed_reason") or FAIL_CLOSED_REASON)
    trim_applied = bool(receipt.get("trim_applied"))
    trimmed = receipt.get("trimmed_components") if isinstance(receipt.get("trimmed_components"), list) else []

    if fail_reason == FAIL_SHAPE_ALTERED:
        return {
            "operator_summary": (
                "Prompt token budget exceeded and optional trim cannot fit without altering "
                "evidence/SRFS shape — do not shorten briefing/JD further in-place; fix compile inputs."
            ),
            "operator_message": (
                "TOKEN BUDGET BLOCKED (evidence shape would change)\n"
                "Optional briefing/JD trims are exhausted. Further cuts would alter protected "
                "SRFS / evidence-law / HIGH-fact content.\n"
                "See token_budget_receipt.json forbidden_trim_violations."
            ),
            "tokens_over_budget": max(0, after - available),
            "tokens_to_remove_estimate": max(0, after - available),
            "suggestions": [],
            "protected_signal": list(PROTECTED_COMPONENT_LABELS),
        }

    if fail_reason == FAIL_CLOSED_REASON_FIRST_PASS_95PCT:
        budget_line = first_limit
        over = max(0, after - first_limit)
        headline = (
            f"Prompt too large after optional trim ({after} est. input tokens, "
            f"{util_pct:.1f}% of {available} available; cap {util_max:.0%} = {first_limit}). "
            f"Shorten briefing and/or JD by ~{over} estimated tokens — see suggestions."
        )
    else:
        budget_line = available
        over = max(0, after - available)
        headline = (
            f"Prompt too large after optional trim ({after} est. tokens vs {available} hard input cap). "
            f"Shorten briefing and/or JD by ~{over} estimated tokens — see suggestions."
        )

    suggestions: list[dict[str, Any]] = []
    source_hints = _runtime_input_source_hints(payload)
    briefing_text = str(payload.get("briefing") or "")
    jd_text = str(payload.get("jd_text") or "")
    briefing_est = _estimate_chars_to_tokens(len(briefing_text))
    jd_est = _estimate_chars_to_tokens(len(jd_text))

    brief_hint = (
        source_hints.get("briefing_selected_path")
        or source_hints.get("manual_brief")
        or source_hints.get("briefing_path")
    )

    if briefing_text:
        suggestions.append(
            {
                "priority": 1,
                "target": "briefing",
                "action": (
                    "Shorten `*_briefing.md` targeting SSOT: keep role themes, constraints, and "
                    "company hooks — remove narrative background, duplicated JD bullets, and "
                    "long citations."
                ),
                "preserves_signal": (
                    "Must-have role themes, constraints, targeting hooks; HIGH/C0 facts and "
                    "selected_fact_plan unchanged."
                ),
                "estimated_input_tokens_if_removed_entirely": briefing_est,
                "source_hint": brief_hint,
            }
        )
        suggestions.append(
            {
                "priority": 2,
                "target": "briefing",
                "action": (
                    f"Trim briefing prose by ≥{over} estimated tokens: delete redundant paragraphs, "
                    "merge duplicate themes, move long quotes to a footnote file (not in prompt)."
                ),
                "preserves_signal": "Keep numbered must-haves, risks, and differentiation bullets.",
                "estimated_input_tokens_if_halved": max(1, briefing_est // 2),
            }
        )

    if jd_text:
        suggestions.append(
            {
                "priority": 3,
                "target": "jd",
                "action": (
                    "Shorten JD to targeting-only: retain title, 5–8 must-have responsibilities, "
                    "and differentiators; drop boilerplate benefits, legal text, and repeated "
                    "qualification lists already captured in briefing."
                ),
                "preserves_signal": (
                    "JD targeting themes and constraints; evidence facts and claim ledger "
                    "unchanged."
                ),
                "estimated_input_tokens_if_removed_entirely": jd_est,
            }
        )

    already_trimmed = {str(c.get("component") or "") for c in trimmed if isinstance(c, dict)}
    if "e0_examples" in already_trimmed:
        suggestions.append(
            {
                "priority": 4,
                "target": "style_examples",
                "action": (
                    "Runtime already removed E0 style examples. If still over budget, reduce "
                    "style-example blocks at the source template — not HIGH facts or SRFS arc."
                ),
                "preserves_signal": "Generation shape (SRFS), evidence law, required facts.",
            }
        )
    if trim_applied and already_trimmed:
        suggestions.append(
            {
                "priority": 5,
                "target": "runtime_trim",
                "action": (
                    "Automatic optional trim already applied: "
                    + ", ".join(sorted(already_trimmed))
                    + ". Further reduction must come from shorter briefing/JD source files."
                ),
                "preserves_signal": "Protected components listed in token_budget_receipt.json.",
            }
        )

    suggestions.append(
        {
            "priority": 9,
            "target": "do_not_cut",
            "action": (
                "Do not delete or paraphrase: selected_fact_plan / HIGH facts, evidence_law, "
                "SRFS arc, claim_ledger rules, allowed_source_fact_ids, or response_schema."
            ),
            "preserves_signal": "All proof-backed claims and X2 sentence/paragraph gates.",
        }
    )

    lines = [
        "TOKEN BUDGET BLOCKED — shorten briefing and/or JD (targeting prose only)",
        headline,
        f"Receipt: token_budget_receipt.json | fail_closed_reason={fail_reason}",
        "",
        "Reduce estimated input tokens without sacrificing proof signal:",
    ]
    for idx, sug in enumerate(suggestions, start=1):
        if sug.get("target") == "do_not_cut":
            continue
        lines.append(f"{idx}. [{sug.get('target')}] {sug.get('action')}")
        lines.append(f"   Keeps: {sug.get('preserves_signal')}")
    lines.append("")
    lines.append("Protected (never cut for token budget):")
    lines.append(
        "  HIGH/required facts, selected_fact_plan, evidence_law, SRFS shape, "
        "claim_ledger, response_schema."
    )
    if over > 0:
        lines.append("")
        lines.append(
            f"Target reduction: ≥{over} estimated input tokens "
            f"(to reach {budget_line} under current policy)."
        )

    return {
        "operator_summary": headline,
        "operator_message": "\n".join(lines),
        "tokens_over_budget": over,
        "tokens_to_remove_estimate": over,
        "first_pass_utilization_pct": util_pct,
        "first_pass_input_utilization_max": util_max,
        "available_input_tokens": available,
        "compiled_prompt_tokens_after_trim": after,
        "suggestions": suggestions,
        "protected_signal": list(PROTECTED_COMPONENT_LABELS),
        "input_source_hints": source_hints,
    }


def attach_token_budget_operator_guidance(
    receipt: dict[str, Any],
    *,
    runtime_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    guidance = build_token_budget_operator_guidance(receipt, runtime_payload=runtime_payload)
    receipt["operator_guidance"] = guidance
    receipt["operator_summary"] = guidance.get("operator_summary")
    receipt["operator_message"] = guidance.get("operator_message")
    return receipt


def _raise_token_budget_exceeded(
    receipt: dict[str, Any],
    *,
    runtime_payload: dict[str, Any],
) -> None:
    attach_token_budget_operator_guidance(receipt, runtime_payload=runtime_payload)
    raise ExecutiveSummaryTokenBudgetExceeded(receipt=receipt)


@dataclass(frozen=True)
class RegenDispatchBudgetCheck:
    estimated_input_tokens: int
    max_output_tokens: int
    reserved_tokens: int
    provider_context_window: int
    available_input_tokens: int
    headroom_tokens: int
    headroom_pct: float
    dispatch_allowed: bool
    block_reason: str | None
    provider_context_window_source: str = _CONTEXT_SOURCE_ENV
    server_context_window_verified: bool = False
    server_context_window_warning: str | None = None


def estimate_regen_thread_tokens(messages: list[dict[str, str]]) -> int:
    """Conservative estimate for full chat ``messages[]`` passed to regen dispatch."""
    parts = [str(m.get("content") or "") for m in messages if isinstance(m, dict)]
    return estimate_tokens_approximate("\n".join(parts))


def regen_dispatch_allowed(
    messages: list[dict[str, str]],
    *,
    max_output_tokens: int,
    provider_context_window: int | None = None,
    model: str | None = None,
) -> RegenDispatchBudgetCheck:
    """Pre-dispatch budget check for regen/repair Qwen calls (advisory when regen caps disabled)."""
    from apps_rg.runtime.sections.executive_summary_repair_policy import (
        regen_artificial_caps_enabled,
    )

    provenance = (
        resolve_context_window_provenance(model=model)
        if provider_context_window is None
        else ContextWindowProvenance(
            provider_context_window=int(provider_context_window),
            provider_context_window_source=_CONTEXT_SOURCE_ENV,
            server_context_window_verified=False,
            server_context_window_warning="explicit provider_context_window override",
            server_observed_context_window=None,
        )
    )
    ctx = int(provenance.provider_context_window)
    max_out = max(1, int(max_output_tokens))
    reserved = _RESERVED_SYSTEM_SCHEMA_TOKENS
    available = max(0, ctx - max_out - reserved)
    est_in = estimate_regen_thread_tokens(messages)
    headroom = available - est_in
    headroom_pct = round((headroom / available * 100.0) if available > 0 else 0.0, 2)
    allowed = est_in <= available
    block_reason = None if allowed else "regen_input_exceeds_available_context_window"
    if not regen_artificial_caps_enabled():
        allowed = True
        block_reason = None
    return RegenDispatchBudgetCheck(
        estimated_input_tokens=est_in,
        max_output_tokens=max_out,
        reserved_tokens=reserved,
        provider_context_window=ctx,
        available_input_tokens=available,
        headroom_tokens=headroom,
        headroom_pct=headroom_pct,
        dispatch_allowed=allowed,
        block_reason=block_reason,
        provider_context_window_source=provenance.provider_context_window_source,
        server_context_window_verified=provenance.server_context_window_verified,
        server_context_window_warning=provenance.server_context_window_warning,
    )


def estimate_tokens_approximate(text: str) -> int:
    """Conservative token estimate; receipt labels method as approximate."""
    if not text:
        return 0
    base = max(1, len(text) // _CHARS_PER_TOKEN)
    return max(1, int(base * _ESTIMATE_SAFETY_MULTIPLIER))


def graph_product_pool_active(runtime_payload: dict[str, Any]) -> bool:
    """True when executive_summary uses in-memory graph/product proof (not JSON file envelope)."""
    plan = runtime_payload.get("selected_fact_plan") or {}
    if list(plan.get("facts") or []):
        return True
    pp = runtime_payload.get("proof_pool_metadata") or {}
    if not isinstance(pp, dict):
        return False
    from apps_rg.runtime.product_evidence_authority import is_product_evidence_authority_active

    if is_product_evidence_authority_active(pp):
        return True
    return bool(pp.get("graph_skills_proof_pool"))


def srfs_mode_active(runtime_payload: dict[str, Any]) -> bool:
    """Deprecated alias for graph_product_pool_active (SRFS JSON authority removed)."""
    return graph_product_pool_active(runtime_payload)


def protected_fact_ids_from_payload(runtime_payload: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for raw in runtime_payload.get("allowed_fact_ids") or []:
        fid = str(raw).strip()
        if fid:
            ids.add(fid)
    plan = runtime_payload.get("selected_fact_plan") or {}
    for fact in plan.get("facts") or []:
        if isinstance(fact, dict):
            fid = str(fact.get("fact_id") or "").strip()
            if fid:
                ids.add(fid)
            metric = str(fact.get("metric_raw") or "").strip()
            if fid and metric:
                from apps_rg.runtime.sections.graph_evidence_contract import metric_derivative_fact_id

                ids.add(metric_derivative_fact_id(fid, metric))
    return ids


def _extract_fact_lines(content: str, protected_ids: set[str]) -> dict[str, str]:
    """Map fact_id -> full ``- id: claim`` line text for protected HIGH rows."""
    lines: dict[str, str] = {}
    for m in _FACT_LINE_RE.finditer(content):
        fid, claim = m.group(1), m.group(2)
        if fid in protected_ids:
            lines[fid] = f"- {fid}: {claim}".rstrip()
    return lines


def _extract_input_authority_allowed_json(content: str) -> str | None:
    key = "ALLOWED_SOURCE_FACT_IDS (JSON array):"
    pos = content.find(key)
    if pos < 0:
        return None
    tail = content[pos + len(key) :].lstrip()
    if not tail.startswith("["):
        return None
    depth = 0
    for i, ch in enumerate(tail):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return tail[: i + 1]
    return None


def _extract_region(segment: str, open_tag: str, close_tag: str) -> str:
    start = segment.find(open_tag)
    if start < 0:
        return ""
    end = segment.find(close_tag, start)
    if end < 0:
        return ""
    return segment[start : end + len(close_tag)]


def _slot_segment(content: str, slot_id: str, *, stop_at: str | None = None) -> str:
    marker = f"<!-- SLOT: {slot_id} -->"
    idx = content.find(marker)
    if idx < 0:
        return ""
    next_m = _SLOT_MARKER_RE.search(content, idx + len(marker))
    end = next_m.start() if next_m else len(content)
    if stop_at:
        stop_idx = content.find(stop_at, idx)
        if stop_idx >= 0:
            end = min(end, stop_idx)
    return content[idx:end]


def _extract_balanced_json_object(text: str, start: int) -> str:
    """Return the first balanced ``{...}`` or ``[...]`` JSON slice from ``start``."""
    if start < 0 or start >= len(text):
        return ""
    opener = text[start]
    if opener not in "{[":
        return ""
    closer = "}" if opener == "{" else "]"
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == opener:
            depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return ""


def _extract_r0_schema_json(content: str) -> str:
    """Proof-bearing response schema JSON only — excludes SRFS style appendix in R0."""
    segment = _slot_segment(content, "R0")
    if not segment:
        return ""
    for needle in ('{"type"', '{\n  "type"'):
        j = segment.find(needle)
        if j >= 0:
            obj = _extract_balanced_json_object(segment, j)
            if obj:
                return obj
    return ""


def extract_evidence_contract_snapshot(
    content: str,
    protected_ids: set[str],
) -> dict[str, Any]:
    """Stable digest inputs for proof contract — must be identical after any applied trim."""
    c0_seg = _slot_segment(content, "C0")
    i0_seg = _slot_segment(content, "I0")
    plan_idx = content.find("SELECTED_FACT_PLAN")
    plan_seg = content[plan_idx : content.find("INPUT_AUTHORITY:", plan_idx)] if plan_idx >= 0 else c0_seg
    return {
        "protected_fact_lines": _extract_fact_lines(plan_seg or c0_seg, protected_ids),
        "allowed_source_fact_ids_json": _extract_input_authority_allowed_json(content),
        "i0_authority_boundary": _extract_region(i0_seg, "<authority_boundary", "</authority_boundary>"),
        "i0_evidence_law": _extract_region(i0_seg, "<evidence_law", "</evidence_law>"),
        "i0_output_contract": _extract_region(i0_seg, "<output_contract", "</output_contract>"),
        "r0_schema_json": _extract_r0_schema_json(content),
        "allowed_source_fact_ids_header_present": "ALLOWED_SOURCE_FACT_IDS" in content,
        "input_authority_present": "INPUT_AUTHORITY:" in content,
    }


def evidence_contract_digest(snapshot: dict[str, Any]) -> str:
    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def verify_evidence_contract_unchanged(
    before: str,
    after: str,
    protected_ids: set[str],
) -> list[str]:
    """Return violations if trim altered proof contract material."""
    violations: list[str] = []
    snap_b = extract_evidence_contract_snapshot(before, protected_ids)
    snap_a = extract_evidence_contract_snapshot(after, protected_ids)
    if evidence_contract_digest(snap_b) != evidence_contract_digest(snap_a):
        violations.append("evidence_contract_digest_mismatch")
    for fid in sorted(protected_ids):
        if fid not in after:
            violations.append(f"missing_protected_fact_id:{fid}")
        elif snap_b["protected_fact_lines"].get(fid) != snap_a["protected_fact_lines"].get(fid):
            violations.append(f"altered_protected_fact_line:{fid}")
    if snap_b["allowed_source_fact_ids_json"] != snap_a["allowed_source_fact_ids_json"]:
        violations.append("altered_allowed_source_fact_ids_json")
    for key in ("i0_authority_boundary", "i0_evidence_law", "i0_output_contract"):
        if snap_b[key] != snap_a[key]:
            violations.append(f"altered_{key}")
    if snap_b["r0_schema_json"] != snap_a["r0_schema_json"]:
        violations.append("altered_r0_schema_json")
    return violations


def verify_prompt_shape_preserved(before: str, after: str, *, srfs_mode: bool) -> list[str]:
    """Return violations when generation-shape instructions were removed or replaced."""
    violations: list[str] = []
    for slot in ("S0", "I0", "C0", "U0", "R0"):
        marker = f"<!-- SLOT: {slot} -->"
        if marker in before and marker not in after:
            violations.append(f"missing_slot_marker:{slot}")
    if "NO FABRICATION" in before.upper() and "NO FABRICATION" not in after.upper():
        if "proof substrate" not in after.lower():
            violations.append("missing_evidence_law_in_s0")
    if srfs_mode:
        for mk in _SRFS_SHAPE_MARKERS:
            if mk in before and mk not in after:
                violations.append(f"missing_srfs_shape_marker:{mk}")
        if "<srfs_style_only_oneshot" in before and "<srfs_style_only_oneshot" not in after:
            violations.append("removed_srfs_style_only_oneshot_block")
        if "token-budget compressed SRFS contract" in after:
            violations.append("replaced_srfs_style_only_oneshot_with_stub")
    if "<!-- SLOT: R0 -->" in before:
        b_schema = _extract_r0_schema_json(before)
        a_schema = _extract_r0_schema_json(after)
        if b_schema and b_schema != a_schema:
            violations.append("altered_r0_embedded_schema")
        if "R0 compressed for token budget" in after:
            violations.append("r0_template_prose_replaced")
    if "I0 compressed for token budget" in after:
        violations.append("i0_sovereign_slot_replaced")
    return violations


def _replace_between(
    text: str,
    start_marker: str,
    end_marker: str,
    replacement: str,
) -> tuple[str, bool]:
    start = text.find(start_marker)
    if start < 0:
        return text, False
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        return text, False
    end += len(end_marker)
    return text[:start] + replacement + text[end:], True


def _trim_xml_block(text: str, open_tag_prefix: str, close_tag: str, replacement: str) -> tuple[str, bool]:
    m = re.search(rf"<{re.escape(open_tag_prefix)}[^>]*>", text)
    if not m:
        return text, False
    start = m.start()
    close_idx = text.find(close_tag, m.end())
    if close_idx < 0:
        return text, False
    close_idx += len(close_tag)
    return text[:start] + replacement + text[close_idx:], True


def _trim_slot(content: str, slot_id: str, replacement: str) -> tuple[str, bool]:
    marker = f"<!-- SLOT: {slot_id} -->"
    idx = content.find(marker)
    if idx < 0:
        return content, False
    next_m = _SLOT_MARKER_RE.search(content, idx + len(marker))
    end = next_m.start() if next_m else len(content)
    segment = content[idx:end]
    if len(segment.strip()) <= len(replacement.strip()) + len(marker):
        return content, False
    new_segment = marker + "\n" + replacement.strip() + "\n"
    return content[:idx] + new_segment + content[end:], True


def _compress_briefing_in_jd_block(jd_block: str, max_briefing_chars: int) -> tuple[str, bool]:
    key = "BRIEFING (targeting only"
    pos = jd_block.find(key)
    if pos < 0:
        return jd_block, False
    line_end = jd_block.find("\n", pos)
    if line_end < 0:
        line_end = len(jd_block)
    line = jd_block[pos:line_end]
    prefix, _, briefing_body = line.partition("): ")
    if not briefing_body or len(briefing_body) <= max_briefing_chars:
        return jd_block, False
    keep = max(256, max_briefing_chars)
    compressed = (
        f"{prefix}): {briefing_body[:keep]}"
        f"{_TRIM_NOTICE}Briefing prose compressed for token budget (targeting-only; not proof)."
    )
    return jd_block[:pos] + compressed + jd_block[line_end:], True


def _compress_jd_text_line(content: str, max_jd_chars: int) -> tuple[str, bool]:
    key = "JD_TEXT (targeting only"
    pos = content.find(key)
    if pos < 0:
        return content, False
    line_end = content.find("\n", pos)
    if line_end < 0:
        line_end = len(content)
    line = content[pos:line_end]
    prefix, _, jd_body = line.partition("): ")
    if not jd_body or len(jd_body) <= max_jd_chars:
        return content, False
    keep = max(256, max_jd_chars)
    compressed = (
        f"{prefix}): {jd_body[:keep]}"
        f"{_TRIM_NOTICE}JD_TEXT compressed for token budget (targeting-only; not proof)."
    )
    return content[:pos] + compressed + content[line_end:], True


def _trim_optional_fact_lines(c0_text: str, protected_ids: set[str]) -> tuple[str, list[dict[str, Any]]]:
    lines = c0_text.splitlines()
    out: list[str] = []
    trimmed: list[dict[str, Any]] = []
    for line in lines:
        m = re.match(r"^\s*-\s+([A-Za-z0-9_]+):\s", line)
        if m:
            fid = m.group(1)
            if fid not in protected_ids and fid.startswith(("fact_", "bul_", "skill_", "cand_")):
                trimmed.append(
                    {
                        "component": "c0_optional_fact_line",
                        "fact_id": fid,
                        "reason": "lower_priority_fact_line_removed",
                    }
                )
                continue
        out.append(line)
    if not trimmed:
        return c0_text, trimmed
    return "\n".join(out), trimmed


def trim_executive_summary_prompt_content(
    content: str,
    *,
    protected_ids: set[str],
    available_input_tokens: int,
) -> tuple[str, list[dict[str, Any]], bool]:
    """Optional-only trim pass. Never compresses I0/R0/SRFS arc blocks."""
    trimmed_components: list[dict[str, Any]] = []
    current = content
    target = available_input_tokens

    def _over() -> bool:
        return estimate_tokens_approximate(current) > target

    if not _over():
        return current, trimmed_components, False

    before = estimate_tokens_approximate(current)

    # E0 examples (style-only)
    new_content, did = _trim_slot(
        current,
        "E0",
        "E0 compressed for token budget — use SRFS/C0 proof and I0 output contract only.",
    )
    if did:
        after = estimate_tokens_approximate(new_content)
        trimmed_components.append(
            {
                "component": "e0_examples",
                "tokens_before": before,
                "tokens_after": after,
                "reason": "optional_style_examples",
            }
        )
        current, before = new_content, after

    if _over():
        new_content, did = _trim_slot(
            current,
            "Y0",
            "Y0 compressed for token budget — follow I0 and S0 voice constraints.",
        )
        if did:
            after = estimate_tokens_approximate(new_content)
            trimmed_components.append(
                {
                    "component": "y0_style_preferences",
                    "tokens_before": before,
                    "tokens_after": after,
                    "reason": "optional_style_preferences",
                }
            )
            current, before = new_content, after

    if _over():
        jd_idx = current.find("<!-- SLOT: C0")
        if jd_idx < 0:
            jd_idx = current.find("jd_requirements")
        next_slot = _SLOT_MARKER_RE.search(current, jd_idx + 1 if jd_idx >= 0 else 0)
        jd_end = next_slot.start() if next_slot else len(current)
        jd_region = current[jd_idx:jd_end] if jd_idx >= 0 else current
        max_brief = 1200 if target < 9000 else 2400
        new_jd, did = _compress_briefing_in_jd_block(jd_region, max_brief)
        if did:
            new_content = current[:jd_idx] + new_jd + current[jd_end:] if jd_idx >= 0 else new_jd
            after = estimate_tokens_approximate(new_content)
            trimmed_components.append(
                {
                    "component": "jd_briefing_prose",
                    "tokens_before": before,
                    "tokens_after": after,
                    "reason": "targeting_only_briefing_compression",
                }
            )
            current, before = new_content, after

    if _over():
        new_content, did = _compress_jd_text_line(current, max_jd_chars=1800)
        if did:
            after = estimate_tokens_approximate(new_content)
            trimmed_components.append(
                {
                    "component": "jd_text_prose",
                    "tokens_before": before,
                    "tokens_after": after,
                    "reason": "targeting_only_jd_compression",
                }
            )
            current, before = new_content, after

    if _over():
        jd_idx = current.find("<!-- SLOT: C0")
        if jd_idx < 0:
            jd_idx = current.find("jd_requirements")
        next_slot = _SLOT_MARKER_RE.search(current, jd_idx + 1 if jd_idx >= 0 else 0)
        jd_end = next_slot.start() if next_slot else len(current)
        jd_region = current[jd_idx:jd_end] if jd_idx >= 0 else current
        new_jd, did = _compress_briefing_in_jd_block(jd_region, 600)
        if did:
            new_content = current[:jd_idx] + new_jd + current[jd_end:] if jd_idx >= 0 else new_jd
            after = estimate_tokens_approximate(new_content)
            trimmed_components.append(
                {
                    "component": "jd_briefing_prose_tight",
                    "tokens_before": before,
                    "tokens_after": after,
                    "reason": "targeting_only_briefing_second_pass",
                }
            )
            current, before = new_content, after

    if _over():
        c0_idx = current.find("SELECTED_FACT_PLAN")
        if c0_idx >= 0:
            c0_end = current.find("INPUT_AUTHORITY:", c0_idx)
            if c0_end < 0:
                c0_end = len(current)
            c0_region = current[c0_idx:c0_end]
            new_c0, fact_trims = _trim_optional_fact_lines(c0_region, protected_ids)
            if fact_trims:
                new_content = current[:c0_idx] + new_c0 + current[c0_end:]
                after = estimate_tokens_approximate(new_content)
                for ft in fact_trims:
                    trimmed_components.append(
                        {**ft, "tokens_before": before, "tokens_after": after}
                    )
                current, before = new_content, after

    for comp in trimmed_components:
        name = str(comp.get("component") or "")
        if name not in _OPTIONAL_TRIM_COMPONENTS:
            raise ValueError(f"internal_error: non-optional trim component {name!r}")

    return current, trimmed_components, bool(trimmed_components)


def apply_executive_summary_token_budget_policy(
    section_compiled: SectionCompiledPrompt,
    *,
    runtime_payload: dict[str, Any],
    provider: str,
    model: str,
    requested_max_output_tokens: int,
    provider_context_window: int | None = None,
) -> tuple[SectionCompiledPrompt, dict[str, Any]]:
    """Apply optional-only trims; block before Qwen if evidence/shape would change or budget still exceeded."""
    provenance = (
        resolve_context_window_provenance(model=model)
        if provider_context_window is None
        else ContextWindowProvenance(
            provider_context_window=int(provider_context_window),
            provider_context_window_source=_CONTEXT_SOURCE_ENV,
            server_context_window_verified=False,
            server_context_window_warning="explicit provider_context_window override",
            server_observed_context_window=None,
        )
    )
    ctx = int(provenance.provider_context_window)
    max_out = max(1, int(requested_max_output_tokens))
    reserved = _RESERVED_SYSTEM_SCHEMA_TOKENS
    available = max(0, ctx - max_out - reserved)
    srfs = srfs_mode_active(runtime_payload)

    art = section_compiled.artifact
    msgs = [dict(m) for m in art.messages]
    if not msgs:
        raise ValueError("executive_summary compile produced no messages")

    content_before = str(msgs[0].get("content") or "")
    before_tokens = estimate_tokens_approximate(content_before)
    capsule_applied = bool(runtime_payload.get("evidence_capsule_active"))
    est = runtime_payload.get("prompt_token_estimates") or {}
    before_capsule_est = int(est["before_capsule_prompt_estimate"]) if est.get(
        "before_capsule_prompt_estimate"
    ) is not None else None
    after_capsule_est = int(est["after_capsule_prompt_estimate"]) if est.get(
        "after_capsule_prompt_estimate"
    ) is not None else (before_tokens if capsule_applied else None)
    protected_ids = protected_fact_ids_from_payload(runtime_payload)
    digest_before = evidence_contract_digest(
        extract_evidence_contract_snapshot(content_before, protected_ids)
    )

    from apps_rg.runtime.sections.executive_summary_targeting_cap import (
        apply_executive_summary_targeting_cap,
    )

    content_for_trim, targeting_meta = apply_executive_summary_targeting_cap(
        content_before,
        runtime_payload=runtime_payload,
        available_input_tokens=available,
    )
    after_targeting_cap_tokens = estimate_tokens_approximate(content_for_trim)

    trimmed_content, trimmed_components, trim_applied = trim_executive_summary_prompt_content(
        content_for_trim,
        protected_ids=protected_ids,
        available_input_tokens=available,
    )
    after_tokens = estimate_tokens_approximate(trimmed_content)
    digest_after = evidence_contract_digest(
        extract_evidence_contract_snapshot(trimmed_content, protected_ids)
    )

    evidence_violations = verify_evidence_contract_unchanged(
        content_before, trimmed_content, protected_ids
    )
    shape_violations = verify_prompt_shape_preserved(
        content_for_trim, trimmed_content, srfs_mode=srfs
    )
    first_pass_limit = first_pass_95pct_limit_tokens(available)
    exceeds_95 = exceeds_first_pass_95pct_policy(after_tokens, available)
    still_over = after_tokens > available
    shape_altering_required = still_over and not trim_applied
    utilization_pct = first_pass_utilization_pct(after_tokens, available)

    receipt: dict[str, Any] = {
        "status": "PASS",
        "section": SECTION_ID,
        "provider": provider,
        "model": model,
        **context_window_provenance_receipt_fields(provenance),
        "requested_max_output_tokens": max_out,
        "reserved_input_tokens": reserved,
        "available_input_tokens": available,
        "capsule_applied": capsule_applied,
        "before_capsule_prompt_estimate": before_capsule_est,
        "after_capsule_prompt_estimate": after_capsule_est,
        "compiled_prompt_tokens_before_trim": after_targeting_cap_tokens,
        "compiled_prompt_tokens_after_trim": after_tokens,
        "after_targeting_cap_prompt_estimate": after_targeting_cap_tokens,
        "after_optional_trim_estimate": after_tokens,
        "targeting_cap_applied": targeting_meta.get("targeting_cap_applied"),
        "targeting_cap_strategy": targeting_meta.get("targeting_cap_strategy"),
        "targeting_tokens_before_cap": targeting_meta.get("targeting_tokens_before_cap"),
        "targeting_tokens_after_cap": targeting_meta.get("targeting_tokens_after_cap"),
        "targeting_cap_reason": targeting_meta.get("targeting_cap_reason"),
        "targeting_components_capped": targeting_meta.get("targeting_components_capped"),
        "targeting_content_preserved": targeting_meta.get("targeting_content_preserved"),
        "trim_applied": trim_applied,
        "trim_strategy": TRIM_STRATEGY,
        "trimmed_components": trimmed_components,
        "protected_components_preserved": list(PROTECTED_COMPONENT_LABELS),
        "forbidden_trim_violations": evidence_violations + shape_violations,
        "evidence_contract_digest_before": digest_before,
        "evidence_contract_digest_after": digest_after,
        "prompt_shape_preserved": not shape_violations,
        "evidence_contract_preserved": not evidence_violations,
        "shape_altering_trim_forbidden": True,
        "shape_altering_trim_required_to_fit": still_over,
        "first_pass_95pct_policy_enabled": True,
        "first_pass_input_utilization_max": resolve_first_pass_input_utilization_max(),
        "first_pass_95pct_limit_tokens": first_pass_limit,
        "first_pass_utilization_pct": utilization_pct,
        "first_pass_95pct_exceeded": exceeds_95,
        "dispatch_allowed": True,
        "fail_closed_reason": None,
        "token_estimate_method": ESTIMATE_METHOD,
        "token_estimate_safety_multiplier": _ESTIMATE_SAFETY_MULTIPLIER,
        "chars_per_token_ratio": _CHARS_PER_TOKEN,
    }

    if evidence_violations or shape_violations:
        receipt["status"] = "FAIL"
        receipt["fail_closed_reason"] = FAIL_SHAPE_ALTERED
        receipt["dispatch_allowed"] = False
        _raise_token_budget_exceeded(receipt, runtime_payload=runtime_payload)

    if exceeds_95:
        receipt["status"] = "FAIL"
        receipt["fail_closed_reason"] = FAIL_CLOSED_REASON_FIRST_PASS_95PCT
        receipt["dispatch_allowed"] = False
        _raise_token_budget_exceeded(receipt, runtime_payload=runtime_payload)

    if still_over:
        receipt["status"] = "FAIL"
        receipt["fail_closed_reason"] = FAIL_CLOSED_REASON
        receipt["dispatch_allowed"] = False
        _raise_token_budget_exceeded(receipt, runtime_payload=runtime_payload)

    if targeting_meta.get("targeting_cap_applied") or trim_applied:
        msgs[0]["content"] = trimmed_content
        new_art = replace(art, messages=msgs)
        section_compiled = SectionCompiledPrompt(
            section_id=section_compiled.section_id,
            apps_rg_prompt_template_ref=section_compiled.apps_rg_prompt_template_ref,
            artifact=new_art,
        )

    runtime_payload["token_budget_policy"] = {
        "trim_applied": trim_applied,
        "compiled_prompt_tokens_before_trim": before_tokens,
        "compiled_prompt_tokens_after_trim": after_tokens,
        "available_input_tokens": available,
        "evidence_contract_digest_before": digest_before,
        "evidence_contract_digest_after": digest_after,
        "prompt_shape_preserved": True,
        "dispatch_allowed": True,
    }
    return section_compiled, receipt


def write_token_budget_receipt(artifact_dir, receipt: dict[str, Any]) -> None:
    from pathlib import Path

    path = Path(artifact_dir) / "token_budget_receipt.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


__all__ = [
    "ContextWindowProvenance",
    "ExecutiveSummaryTokenBudgetExceeded",
    "FAIL_CLOSED_REASON",
    "FAIL_CLOSED_REASON_FIRST_PASS_95PCT",
    "FAIL_SHAPE_ALTERED",
    "FIRST_PASS_INPUT_UTILIZATION_MAX",
    "PROTECTED_COMPONENT_LABELS",
    "TRIM_STRATEGY",
    "apply_executive_summary_token_budget_policy",
    "attach_token_budget_operator_guidance",
    "build_token_budget_operator_guidance",
    "context_window_provenance_receipt_fields",
    "RegenDispatchBudgetCheck",
    "estimate_regen_thread_tokens",
    "estimate_tokens_approximate",
    "exceeds_first_pass_95pct_policy",
    "first_pass_95pct_limit_tokens",
    "first_pass_utilization_pct",
    "regen_dispatch_allowed",
    "resolve_context_window_provenance",
    "evidence_contract_digest",
    "extract_evidence_contract_snapshot",
    "protected_fact_ids_from_payload",
    "resolve_first_pass_input_utilization_max",
    "resolve_provider_context_window",
    "graph_product_pool_active",
    "srfs_mode_active",
    "trim_executive_summary_prompt_content",
    "verify_evidence_contract_unchanged",
    "verify_prompt_shape_preserved",
    "write_token_budget_receipt",
]
