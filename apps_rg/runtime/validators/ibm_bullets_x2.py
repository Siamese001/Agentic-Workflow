"""Deterministic X2 gates for ibm_bullets runtime slice (five IBM employment bullets)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    EM_DASH,
    FIRST_PERSON_PATTERN,
    GENERIC_FILLER,
    INLINE_SOURCE_PATTERN,
    REQUIRED_JUDGE_PROVIDERS,
    check_claim_ledger_claim_text_non_empty,
    check_json_parse_valid,
    check_judge_rows_present,
    check_judge_schema_valid,
    has_jd_phrase_copy,
)

IBM_BULLET_IDS = (
    "bul_ibm_001",
    "bul_ibm_002",
    "bul_ibm_003",
    "bul_ibm_004",
    "bul_ibm_005",
)
IBM_DEFAULT_DISTRIBUTION = {"HEAVY": 0, "MODERATE": 3, "LIGHT_PROTECTED": 2, "total": 5}
VALID_INTENSITIES = frozenset({"HEAVY", "MODERATE", "LIGHT_PROTECTED"})
TEXT_COVERAGE_INTEGRITY_GATE_ID = "x2_text_claim_coverage_integrity"

# Category-style prefix at start of resume bullet (themes belong in bullet_theme / metadata only).
TAXONOMY_LABEL_PREFIX_PATTERN = re.compile(r"^[A-Z][A-Za-z /,&-]{3,60}:\s+")

UNIFY_RUNTIME_TERM_PATTERNS = (
    r"\bagentic\s+ai\b",
    r"\bagentic\s+runtime\b",
    r"\bgraphrag\b",
    r"\bmulti[- ]?agent\s+orchestration\b",
    r"\bdeterministic\s+routing\b",
    r"\bsandboxed\s+execution\b",
    r"\breplayable\s+traces\b",
    r"\bgoverned\s+ai\s+runtime\b",
    r"\bprompt\s+assembly\b",
    r"\bjudge\s+mesh\b",
    r"\bgoverned\s+spine\b",
    r"\bc0\b",
    r"\bl2\b",
    r"\bexit\b",
    r"\buwg\b",
)

REQUIRED_TOP_LEVEL = {
    "bullets",
    "selected_fact_plan",
    "claim_ledger",
    "jd_alignment",
    "gap_notes",
    "change_log",
    "rewrite_distribution",
    "self_check",
}

CORE_METRIC_TOKENS = ("$15M", "99.9%", "30%", "25%", "50%")

_COVERAGE_WS_RE = re.compile(r"\s+")


def _norm_claim_ws(text: str) -> str:
    return _COVERAGE_WS_RE.sub(" ", str(text or "").strip())


def _ibm_root_from_source_fact_ids(source_fact_ids: list[Any]) -> str | None:
    for raw in source_fact_ids or []:
        s = str(raw)
        if s.startswith("bul_ibm_"):
            return s.split("_metric_")[0]
    return None


def build_ibm_bullets_text_claim_coverage(
    bullets: list[dict[str, Any]],
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> dict[str, Any]:
    """Structural bullet↔ledger coverage for IBM bullets (``bul_ibm_001``..``005`` only).

    Mirrors unify_bullets structural coverage shape without embedding ``bul_unify_*`` placeholders
    that would false-trigger ``x2_no_unify_fact_leakage`` on serialized ``parsed_output``.
    """
    ledger_by_root: dict[str, dict[str, Any]] = {}
    duplicate_roots: list[str] = []
    unresolved_roots = 0
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        ids = list(row.get("source_fact_ids") or [])
        root = _ibm_root_from_source_fact_ids(ids)
        if root is None:
            if str(row.get("claim_text") or "").strip():
                unresolved_roots += 1
            continue
        if root in ledger_by_root:
            duplicate_roots.append(root)
        ledger_by_root[root] = row

    by_bullet_id = {str(b.get("bullet_id")): b for b in bullets if b.get("bullet_id")}
    coverage_rows: list[dict[str, Any]] = []
    overall_pass = True
    integrity_notes: list[str] = []

    if duplicate_roots:
        overall_pass = False
        integrity_notes.append(f"duplicate_ledger_roots:{sorted(set(duplicate_roots))}")
    if unresolved_roots:
        overall_pass = False
        integrity_notes.append(f"ledger_rows_missing_ibm_root:{unresolved_roots}")

    for ordinal, bid in enumerate(IBM_BULLET_IDS, start=1):
        bullet = by_bullet_id.get(bid)
        ledger_row = ledger_by_root.get(bid)
        btxt = str((bullet or {}).get("bullet_text") or "").strip()
        sentence_text = f"- {bid}: {btxt}"

        if bullet is None or ledger_row is None:
            overall_pass = False
            coverage_rows.append(
                {
                    "sentence_index": ordinal,
                    "bullet_id": bid,
                    "sentence_text": sentence_text,
                    "material_claims": [
                        {
                            "claim_text": "",
                            "source_fact_ids": [],
                            "support_status": "UNSUPPORTED",
                            "reason": "missing bullet or claim_ledger row for bullet_id",
                        }
                    ],
                    "sentence_pass": False,
                }
            )
            continue

        ct = str(ledger_row.get("claim_text") or "").strip()
        source_ids = list(ledger_row.get("source_fact_ids") or [])
        valid_source_ids = [
            sid for sid in source_ids if sid in allowed_fact_ids or "_metric_" in str(sid)
        ]
        ids_ok = bool(valid_source_ids)
        text_align = _norm_claim_ws(ct) == _norm_claim_ws(btxt)

        sentence_pass = True
        material_claims: list[dict[str, Any]] = []
        if not text_align:
            overall_pass = False
            sentence_pass = False
            material_claims.append(
                {
                    "claim_text": ct,
                    "source_fact_ids": source_ids,
                    "support_status": "MISALIGNED_TEXT",
                    "reason": "claim_ledger claim_text must align with bullet_text (normalized whitespace).",
                }
            )
        elif not ids_ok:
            overall_pass = False
            sentence_pass = False
            material_claims.append(
                {
                    "claim_text": ct,
                    "source_fact_ids": source_ids,
                    "support_status": "UNSUPPORTED",
                    "reason": "source_fact_ids not in allowed_fact_ids.",
                }
            )
        else:
            material_claims.append(
                {
                    "claim_text": ct,
                    "source_fact_ids": source_ids,
                    "support_status": "SUPPORTED",
                    "reason": "Structural row aligned to bullet_id and claim_ledger.",
                }
            )

        coverage_rows.append(
            {
                "sentence_index": ordinal,
                "bullet_id": bid,
                "sentence_text": sentence_text,
                "material_claims": material_claims,
                "sentence_pass": sentence_pass,
            }
        )

    return {
        "coverage_schema": "ibm_bullets_structural_v1",
        "sentences": coverage_rows,
        "overall_pass": overall_pass,
        "integrity_notes": integrity_notes,
    }


def check_ibm_bullets_text_claim_coverage_integrity(
    bullets: list[dict[str, Any]],
    claim_ledger: list[dict[str, Any]],
    text_claim_coverage: dict[str, Any] | None,
    allowed_fact_ids: set[str],
) -> tuple[bool, str | None]:
    """Deterministic gate: stored coverage must match a structural rebuild (no stale loops)."""
    expected = build_ibm_bullets_text_claim_coverage(bullets, claim_ledger, allowed_fact_ids)
    actual = text_claim_coverage if isinstance(text_claim_coverage, dict) else {}
    if actual.get("sentences") != expected.get("sentences"):
        return False, "text_claim_coverage.sentences mismatch vs structural rebuild"
    if actual.get("overall_pass") != expected.get("overall_pass"):
        return (
            False,
            f"overall_pass mismatch observed={actual.get('overall_pass')} expected={expected.get('overall_pass')}",
        )
    return True, None


# Metric ownership: REQUIRED_ANCHOR — metric must appear on assigned canonical bullet text.
IBM_METRIC_ANCHOR_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("99.9",), "bul_ibm_001"),
    (("30%", "30 %"), "bul_ibm_002"),
    (("25%", "25 %"), "bul_ibm_003"),
    (("50%", "50 %"), "bul_ibm_004"),
    (("$15m", "$15 m"), "bul_ibm_005"),
)


def _ibm_metric_anchors_on_assigned_bullets(bullets: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    by_id = {str(b.get("bullet_id")): b for b in bullets if b.get("bullet_id")}
    failures: list[str] = []
    for needles, root in IBM_METRIC_ANCHOR_RULES:
        bullet = by_id.get(root)
        if bullet is None:
            failures.append(f"missing_bullet:{root}")
            continue
        tl = str(bullet.get("bullet_text") or "").lower()
        if not any(n.lower() in tl for n in needles):
            failures.append(f"{root}_missing_metric_token")
    return (not failures, failures)


@dataclass
class X2GateResult:
    gate_id: str
    gate_type: str
    pass_: bool
    observed_value: Any
    threshold: Any
    failure_reason: str | None
    evidence_ref: str

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["pass"] = data.pop("pass_")
        return data


def _combined_bullet_text(bullets: list[dict[str, Any]]) -> str:
    return "\n".join(str(b.get("bullet_text", "")) for b in bullets)


def ibm_bullet_text_has_taxonomy_label_prefix(text: str) -> bool:
    """True when ``bullet_text`` starts with a category-style ``Title: `` prefix (deterministic gate helper)."""

    return bool(TAXONOMY_LABEL_PREFIX_PATTERN.match((text or "").strip()))


def _taxonomy_prefix_violations(bullets: list[dict[str, Any]]) -> list[str]:
    bad: list[str] = []
    for b in bullets:
        if not isinstance(b, dict):
            continue
        bt = str(b.get("bullet_text") or "").strip()
        bid = str(b.get("bullet_id") or "").strip()
        if ibm_bullet_text_has_taxonomy_label_prefix(bt):
            bad.append(bid or bt[:72])
    return bad


def _count_intensities(bullets: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"HEAVY": 0, "MODERATE": 0, "LIGHT_PROTECTED": 0}
    for bullet in bullets:
        intensity = str(bullet.get("rewrite_intensity", "")).upper()
        if intensity in counts:
            counts[intensity] += 1
    return counts


def _all_source_fact_ids(parsed: dict[str, Any] | None, claim_ledger: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for bullet in (parsed or {}).get("bullets") or []:
        for fid in bullet.get("source_fact_ids") or []:
            ids.add(str(fid))
    for claim in claim_ledger:
        for fid in claim.get("source_fact_ids") or []:
            ids.add(str(fid))
        if claim.get("source_fact_id"):
            ids.add(str(claim["source_fact_id"]))
    return ids


def _metric_granularity_ok(bullets: list[dict[str, Any]], claim_ledger: list[dict[str, Any]]) -> bool:
    """Metric-bearing bullet or ledger text must cite the matching bul_ibm_* root."""

    rules: list[tuple[tuple[str, ...], str]] = [
        (("99.9",), "bul_ibm_001"),
        (("30%", "30 %"), "bul_ibm_002"),
        (("25%", "25 %"), "bul_ibm_003"),
        (("50%", "50 %"), "bul_ibm_004"),
        (("$15m", "$15 m"), "bul_ibm_005"),
    ]

    def check_text(text: str, ids_raw: list[str]) -> bool:
        tl = text.lower()
        ids_lower = [i.lower() for i in ids_raw]
        for needles, root in rules:
            if any(n.lower() in tl for n in needles):
                if not any(root in i for i in ids_lower):
                    return False
        return True

    for b in bullets:
        if not check_text(str(b.get("bullet_text", "")), [str(i) for i in (b.get("source_fact_ids") or [])]):
            return False
    for c in claim_ledger:
        if not check_text(str(c.get("claim_text", "")), [str(i) for i in (c.get("source_fact_ids") or [])]):
            return False
    return True


def run_ibm_bullets_x2_gates(
    *,
    bullets: list[dict[str, Any]],
    parsed_output: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    jd_text: str,
    runtime_generation_status: str,
    artifacts_dir: Path | None = None,
    provider_requested: str | None = None,
    provider_attempted: str | None = None,
    model_name: str | None = None,
    raw_output: str | None = None,
    x1d_judges: list[dict[str, Any]] | None = None,
    rewrite_distribution: dict[str, Any] | None = None,
    srfs_source_fact_slice_gate_active: bool = False,
    proof_pool_metadata: dict[str, Any] | None = None,
    proof_pool_ref: str = "",
    proof_pool_digest: str = "",
    base_resume: dict[str, Any] | None = None,
    runtime_payload: dict[str, Any] | None = None,
) -> list[X2GateResult]:
    if runtime_payload:
        allowed_fact_ids = {
            str(x) for x in (runtime_payload.get("allowed_fact_ids") or allowed_fact_ids)
        }
        proof_pool_digest = str(
            runtime_payload.get("canonical_evidence_set_digest") or proof_pool_digest
        )
        meta = dict(proof_pool_metadata or {})
        meta.setdefault(
            "canonical_evidence_set_digest",
            runtime_payload.get("canonical_evidence_set_digest"),
        )
        meta.setdefault("id_alias_map", (runtime_payload.get("canonical_section_evidence_set") or {}).get("id_alias_map"))
        proof_pool_metadata = meta
    gates: list[X2GateResult] = []

    def add(
        gate_id: str,
        passed: bool,
        observed: Any,
        threshold: Any = None,
        failure: str | None = None,
    ) -> None:
        gates.append(
            X2GateResult(
                gate_id=gate_id,
                gate_type="deterministic",
                pass_=passed,
                observed_value=observed,
                threshold=threshold,
                failure_reason=failure,
                evidence_ref=gate_id,
            )
        )

    from apps_rg.runtime.sections.graph_story_authority import (
        x2_gate_base_resume_story_forbidden,
        x2_gate_graph_only_proof_pool,
    )

    graph_ok, graph_obs, graph_exp, graph_detail = x2_gate_graph_only_proof_pool(
        proof_pool_metadata, section_id="ibm_bullets"
    )
    add(
        "x2_ibm_augmented_skills_graph_proof_pool_only",
        graph_ok,
        graph_obs,
        graph_exp,
        str(graph_detail),
    )

    story_ok, story_obs, story_exp, story_detail = x2_gate_base_resume_story_forbidden(
        section_id="ibm_bullets",
        parsed_output=parsed_output,
        base_resume=base_resume,
        runtime_payload=runtime_payload,
    )
    add(
        "x2_ibm_graph_only_no_base_resume_bullets",
        story_ok,
        story_obs,
        story_exp,
        str(story_detail),
    )

    combined = _combined_bullet_text(bullets)
    combined_lower = combined.lower()
    dist = rewrite_distribution or (parsed_output or {}).get("rewrite_distribution") or {}
    intensity_counts = _count_intensities(bullets)

    add("x2_ibm_bullet_count_5", len(bullets) == 5, len(bullets), 5, "Must output exactly 5 IBM bullets.")

    ledger_text_ok, ledger_text_reason = check_claim_ledger_claim_text_non_empty(claim_ledger)
    if not ledger_text_ok and ledger_text_reason:
        hint_parts = []
        for i, row in enumerate(claim_ledger):
            if not isinstance(row, dict):
                continue
            ct = row.get("claim_text")
            if ct is None or (isinstance(ct, str) and not str(ct).strip()):
                b_hint = row.get("bullet_id")
                sfx = ""
                if b_hint is None and row.get("source_fact_ids"):
                    sfx = f"ledger_idx={i} source_fact_ids={row.get('source_fact_ids')!r}"
                else:
                    sfx = f"ledger_idx={i} bullet_id_hint={b_hint!r} source_fact_ids={row.get('source_fact_ids')!r}"
                hint_parts.append(sfx)
        if hint_parts:
            ledger_text_reason = f"{ledger_text_reason}; " + "; ".join(hint_parts)
    add(
        "x2_claim_ledger_claim_text_non_empty",
        ledger_text_ok,
        ledger_text_reason or ("ok" if ledger_text_ok else "failed"),
        "non-empty trimmed claim_text for every ledger row",
        ledger_text_reason,
    )

    po_raw = parsed_output or {}
    cov_gate_payload = po_raw.get("text_claim_coverage") if isinstance(po_raw.get("text_claim_coverage"), dict) else {}
    cov_ok, cov_reason = check_ibm_bullets_text_claim_coverage_integrity(
        bullets=bullets,
        claim_ledger=claim_ledger,
        text_claim_coverage=cov_gate_payload,
        allowed_fact_ids=allowed_fact_ids,
    )
    add(
        TEXT_COVERAGE_INTEGRITY_GATE_ID,
        cov_ok,
        cov_reason or "structural_alignment_ok",
        "matches structural rebuild",
        cov_reason,
    )

    anchor_ok, anchor_fail = _ibm_metric_anchors_on_assigned_bullets(bullets)
    add(
        "x2_ibm_metric_anchor_bullet_ownership",
        anchor_ok,
        anchor_fail or "ok",
        "each core metric on assigned bul_ibm_* bullet_text",
        None if anchor_ok else f"Metric anchor ownership failed: {anchor_fail}",
    )

    dist_valid = (
        dist.get("HEAVY") == IBM_DEFAULT_DISTRIBUTION["HEAVY"]
        and dist.get("MODERATE") == IBM_DEFAULT_DISTRIBUTION["MODERATE"]
        and dist.get("LIGHT_PROTECTED") == IBM_DEFAULT_DISTRIBUTION["LIGHT_PROTECTED"]
        and (dist.get("total") == 5 or sum(intensity_counts.values()) == 5)
    )
    add(
        "x2_ibm_rewrite_distribution_valid",
        dist_valid
        and intensity_counts["HEAVY"] == 0
        and intensity_counts["MODERATE"] == 3
        and intensity_counts["LIGHT_PROTECTED"] == 2,
        {"declared": dist, "observed": intensity_counts},
        IBM_DEFAULT_DISTRIBUTION,
        "IBM rewrite distribution must be 0 HEAVY, 3 MODERATE, 2 LIGHT_PROTECTED.",
    )

    add(
        "x2_ibm_heavy_rewrites_zero",
        intensity_counts["HEAVY"] == 0,
        intensity_counts["HEAVY"],
        0,
        "HEAVY rewrites are forbidden for IBM bullets.",
    )

    metrics_preserved = (
        ("$15M" in combined or "$15m" in combined_lower)
        and "99.9%" in combined
        and "30%" in combined
        and "25%" in combined
        and "50%" in combined
    )
    add(
        "x2_ibm_metrics_preserved",
        metrics_preserved,
        combined[:240],
        CORE_METRIC_TOKENS,
        "Core IBM metrics ($15M, 99.9%, 30%, 25%, 50%) must appear in bullet text.",
    )

    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        proof_source_from_metadata,
        scope_ids_membership_only,
    )

    source_ids = set(_all_source_fact_ids(parsed_output, claim_ledger))
    proof_source = proof_source_from_metadata(proof_pool_metadata)
    if proof_source in ("srfs", "broad_skills_ledger"):
        scope_ok, _, forbidden_hits, not_in_pool = scope_ids_membership_only(
            source_ids,
            allowed_fact_ids=set(allowed_fact_ids),
            forbidden_prefixes=("bul_unify_", "bul_insurtech_", "bul_ey_"),
        )
        scope_threshold = "active_proof_pool_membership"
        scope_fail = "Fact scope must match active IBM proof pool."
        if forbidden_hits or not_in_pool:
            scope_fail += f" forbidden={forbidden_hits} out_of_pool={not_in_pool}"
    else:
        scope_ok = bool(source_ids) and all(str(sid).startswith("bul_ibm_") for sid in source_ids)
        scope_ok = scope_ok and all(
            sid.split("_metric_")[0] in allowed_fact_ids or sid in allowed_fact_ids for sid in source_ids
        )
        scope_threshold = "bul_ibm_*"
        scope_fail = "Fact scope must be IBM bullets only."
    add("x2_ibm_only_fact_scope", scope_ok, sorted(source_ids), scope_threshold, None if scope_ok else scope_fail)

    serialized = json.dumps(parsed_output or {}, sort_keys=True).lower()
    add(
        "x2_no_unify_fact_leakage",
        "bul_unify_" not in serialized,
        "bul_unify_",
        "absent",
        "Unify bullet fact leakage detected.",
    )

    term_hits = [pat for pat in UNIFY_RUNTIME_TERM_PATTERNS if re.search(pat, combined, re.I)]
    add(
        "x2_no_unify_runtime_terms",
        not term_hits,
        term_hits,
        [],
        "Unify runtime vocabulary leaked into IBM bullets.",
    )

    add(
        "x2_no_agentic_inflation",
        not re.search(r"\bagentic\b", combined, re.I),
        "agentic token",
        "absent",
        "Agentic inflation language in IBM bullets.",
    )

    prefix_hits = _taxonomy_prefix_violations(bullets)
    add(
        "x2_no_taxonomy_label_prefix_in_display_text",
        not prefix_hits,
        prefix_hits,
        [],
        "bullet_text must not start with a category-style Title: prefix.",
    )

    jd_copy, jd_phrase = has_jd_phrase_copy(combined, jd_text)
    add(
        "x2_no_jd_only_claims",
        not jd_copy,
        jd_phrase or "none",
        "no JD copy as proof",
        "JD phrase copied into bullet proof.",
    )

    output_ids = {str(b.get("bullet_id")) for b in bullets if b.get("bullet_id")}
    ledger_roots: set[str] = set()
    for claim in claim_ledger:
        for fid in claim.get("source_fact_ids") or []:
            ledger_roots.add(str(fid).split("_metric_")[0])
    if proof_source in ("srfs", "broad_skills_ledger"):
        allowed_bases = {str(x).split("_metric_")[0] for x in allowed_fact_ids} | set(allowed_fact_ids)
        coverage_ok = (
            bool(output_ids)
            and all(bid in allowed_bases for bid in output_ids)
            and all(rid in allowed_bases for rid in ledger_roots)
            and len(claim_ledger) >= len(output_ids)
        )
        coverage_threshold = "active_pool_bullet_ids"
        coverage_msg = "Every output bullet_id and ledger root must be in active proof pool."
    else:
        required_bullet_ids = set(IBM_BULLET_IDS)
        coverage_ok = required_bullet_ids <= output_ids and required_bullet_ids <= ledger_roots
        coverage_threshold = sorted(required_bullet_ids)
        coverage_msg = "Every bul_ibm_* bullet must appear in output and claim_ledger."
    add(
        "x2_claim_ledger_coverage_100",
        coverage_ok and len(claim_ledger) >= len(output_ids) and len(output_ids) >= 1,
        {"output_ids": sorted(output_ids), "ledger_roots": sorted(ledger_roots)},
        coverage_threshold,
        coverage_msg,
    )

    add(
        "x2_metric_fact_id_granularity",
        _metric_granularity_ok(bullets, claim_ledger),
        len(claim_ledger),
        "metric claims map to bul_ibm_*",
        "Metric claims lack matching bul_ibm_* source_fact_ids in claim_ledger.",
    )

    add(
        "x2_no_inline_source_tags",
        not INLINE_SOURCE_PATTERN.search(combined),
        "inline tags",
        "absent",
        "Inline source tags found in bullet text.",
    )
    add(
        "x2_no_first_person",
        not FIRST_PERSON_PATTERN.search(combined),
        "first person",
        "absent",
        "First-person pronoun found.",
    )
    add("x2_no_em_dash", EM_DASH not in combined, "em dash", "absent", "Em dash found.")
    filler_hit = next((f for f in GENERIC_FILLER if f.lower() in combined.lower()), None)
    add("x2_no_generic_filler", filler_hit is None, filler_hit or "none", "absent", "Generic filler phrase found.")

    json_ok, json_reason = check_json_parse_valid(parsed_output, raw_output)
    add("x2_json_parse_valid", json_ok, json_reason, None, json_reason)

    provider_ok = provider_requested == provider_attempted if provider_requested else True
    add(
        "x2_provider_requested_attempted",
        provider_ok,
        f"{provider_requested}->{provider_attempted}",
        "match",
        "Provider requested does not match attempted.",
    )
    no_silent_mock = not (provider_requested == "qwen_vllm" and runtime_generation_status == "MOCKED")
    add(
        "x2_no_silent_mock_fallback",
        no_silent_mock,
        runtime_generation_status,
        "REAL_LLM when qwen requested",
        "Silent mock fallback detected.",
    )

    judges_ok, judges_reason = check_judge_rows_present(x1d_judges)
    add("x2_x1d_required_judges_present", judges_ok, judges_reason, REQUIRED_JUDGE_PROVIDERS, judges_reason)

    if x1d_judges:
        blocked_invalid = []
        for judge in x1d_judges:
            if str(judge.get("evaluator_mode", "")).startswith("BLOCKED_"):
                schema_ok, _ = check_judge_schema_valid(judge)
                if not schema_ok:
                    blocked_invalid.append(judge.get("provider_key"))
        add(
            "x2_x1d_schema_valid",
            not blocked_invalid,
            blocked_invalid,
            [],
            f"Blocked judges with invalid schema: {blocked_invalid}",
        )
    else:
        add("x2_x1d_schema_valid", False, "no judges", "present", "No X1D judges.")

    from apps_rg.runtime.validators.section_input_usage_x2 import append_section_input_usage_x2_gates

    if srfs_source_fact_slice_gate_active or proof_pool_metadata:
        from apps_rg.runtime.sections import selected_role_fact_set as _srfs_w4
        from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
            evaluate_proof_pool_source_fact_gate,
            proof_pool_x2_gate_id,
        )

        coll_ib = _srfs_w4.collect_source_fact_ids_from_bullets_and_ledger(parsed_output, claim_ledger)
        ok_ib, env_ib, fail_ib = evaluate_proof_pool_source_fact_gate(
            section_id="ibm_bullets",
            collected_ids=coll_ib,
            allowed_fact_ids=set(allowed_fact_ids),
            proof_pool_metadata=proof_pool_metadata,
            proof_pool_ref=proof_pool_ref,
            proof_pool_digest=proof_pool_digest,
        )
        add(
            proof_pool_x2_gate_id(
                "ibm_bullets",
                proof_pool_metadata=proof_pool_metadata,
                srfs_slice_gate_active=srfs_source_fact_slice_gate_active,
            ),
            ok_ib,
            env_ib,
            "active_proof_pool_allowlist_exact",
            fail_ib,
        )

    append_section_input_usage_x2_gates(
        gates,
        artifacts_dir=artifacts_dir or Path("artifacts/apps_rg/runtime_proofs/ibm_bullets"),
        allowed_fact_ids=allowed_fact_ids,
        claim_ledger=claim_ledger,
        text_claim_coverage=(parsed_output or {}).get("text_claim_coverage")
        if isinstance(parsed_output, dict)
        else None,
        runtime_payload=runtime_payload,
    )

    return gates


__all__ = [
    "IBM_BULLET_IDS",
    "IBM_DEFAULT_DISTRIBUTION",
    "IBM_METRIC_ANCHOR_RULES",
    "REQUIRED_TOP_LEVEL",
    "TEXT_COVERAGE_INTEGRITY_GATE_ID",
    "TAXONOMY_LABEL_PREFIX_PATTERN",
    "build_ibm_bullets_text_claim_coverage",
    "check_ibm_bullets_text_claim_coverage_integrity",
    "ibm_bullet_text_has_taxonomy_label_prefix",
    "run_ibm_bullets_x2_gates",
]
