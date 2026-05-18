"""Deterministic X2 gates for unify_bullets runtime slice."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import (
    ALLOWED_MODELS,
    EM_DASH,
    FIRST_PERSON_PATTERN,
    GENERIC_FILLER,
    INLINE_SOURCE_PATTERN,
    REQUIRED_JUDGE_PROVIDERS,
    check_claim_ledger_claim_text_non_empty,
    check_json_parse_valid,
    check_judge_raw_responses_written,
    check_judge_rows_present,
    check_judge_schema_valid,
    has_jd_phrase_copy,
)

TEXT_COVERAGE_INTEGRITY_GATE_ID = "x2_text_claim_coverage_integrity"

UNIFY_BULLET_IDS = (
    "bul_unify_001",
    "bul_unify_002",
    "bul_unify_003",
    "bul_unify_004",
    "bul_unify_005",
    "bul_unify_006",
)
DEFAULT_DISTRIBUTION = {"HEAVY": 2, "MODERATE": 3, "LIGHT_PROTECTED": 1, "total": 6}
PROTECTED_BULLET_DEFAULT = "bul_unify_006"
VALID_INTENSITIES = frozenset({"HEAVY", "MODERATE", "LIGHT_PROTECTED"})
FORBIDDEN_FACT_PREFIXES = ("bul_ibm_", "bul_insurtech_", "bul_ey_", "exp_ibm_", "exp_insurtech_", "exp_ey_")

_COVERAGE_WS_RE = re.compile(r"\s+")


def _norm_claim_ws(text: str) -> str:
    return _COVERAGE_WS_RE.sub(" ", str(text or "").strip())


def _unify_root_from_source_fact_ids(source_fact_ids: list[Any]) -> str | None:
    for raw in source_fact_ids or []:
        s = str(raw)
        if s.startswith("bul_unify_"):
            return s.split("_metric_")[0]
    return None


def build_unify_bullets_text_claim_coverage(
    bullets: list[dict[str, Any]],
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> dict[str, Any]:
    """Structural bullet→ledger coverage (one sentence row per canonical bullet_id).

    Unlike resume prose coverage (token overlap), unify bullets map deterministically:
    ``bul_unify_NNN`` ↔ exactly one ledger row sharing that root ``source_fact_ids`` prefix.
    """
    ledger_by_root: dict[str, dict[str, Any]] = {}
    duplicate_roots: list[str] = []
    unresolved_roots = 0
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        ids = list(row.get("source_fact_ids") or [])
        root = _unify_root_from_source_fact_ids(ids)
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
        integrity_notes.append(f"ledger_rows_missing_unify_root:{unresolved_roots}")

    for ordinal, bid in enumerate(UNIFY_BULLET_IDS, start=1):
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
        "coverage_schema": "unify_bullets_structural_v1",
        "sentences": coverage_rows,
        "overall_pass": overall_pass,
        "integrity_notes": integrity_notes,
    }


def check_unify_bullets_text_claim_coverage_integrity(
    bullets: list[dict[str, Any]],
    claim_ledger: list[dict[str, Any]],
    text_claim_coverage: dict[str, Any] | None,
    allowed_fact_ids: set[str],
) -> tuple[bool, str | None]:
    """Deterministic gate: stored coverage must match a structural rebuild (no stale loops)."""
    expected = build_unify_bullets_text_claim_coverage(bullets, claim_ledger, allowed_fact_ids)
    actual = text_claim_coverage if isinstance(text_claim_coverage, dict) else {}
    if actual.get("sentences") != expected.get("sentences"):
        return False, "text_claim_coverage.sentences mismatch vs structural rebuild"
    if actual.get("overall_pass") != expected.get("overall_pass"):
        return (
            False,
            f"overall_pass mismatch observed={actual.get('overall_pass')} expected={expected.get('overall_pass')}",
        )
    return True, None


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


def run_unify_bullets_x2_gates(
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
) -> list[X2GateResult]:
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

    combined = _combined_bullet_text(bullets)
    dist = rewrite_distribution or (parsed_output or {}).get("rewrite_distribution") or {}
    intensity_counts = _count_intensities(bullets)

    po_raw = parsed_output or {}
    missing_top_level = sorted(k for k in REQUIRED_TOP_LEVEL if k not in po_raw)
    add(
        "x2_required_top_level_json_keys",
        not missing_top_level,
        missing_top_level,
        sorted(REQUIRED_TOP_LEVEL),
        f"Missing required top-level JSON keys: {', '.join(missing_top_level)}" if missing_top_level else None,
    )

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

    cov_gate_payload = po_raw.get("text_claim_coverage") if isinstance(po_raw.get("text_claim_coverage"), dict) else {}
    cov_ok, cov_reason = check_unify_bullets_text_claim_coverage_integrity(
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

    add("x2_unify_bullet_count_6", len(bullets) == 6, len(bullets), 6, "Must output exactly 6 bullets.")

    dist_valid = (
        dist.get("HEAVY") == DEFAULT_DISTRIBUTION["HEAVY"]
        and dist.get("MODERATE") == DEFAULT_DISTRIBUTION["MODERATE"]
        and dist.get("LIGHT_PROTECTED") == DEFAULT_DISTRIBUTION["LIGHT_PROTECTED"]
        and (dist.get("total") == 6 or sum(intensity_counts.values()) == 6)
    )
    add(
        "x2_unify_rewrite_distribution_valid",
        dist_valid and intensity_counts == {
            k: DEFAULT_DISTRIBUTION[k] for k in ("HEAVY", "MODERATE", "LIGHT_PROTECTED")
        },
        {"declared": dist, "observed": intensity_counts},
        DEFAULT_DISTRIBUTION,
        "Rewrite distribution must be 2 HEAVY, 3 MODERATE, 1 LIGHT_PROTECTED.",
    )

    add("x2_unify_max_heavy_3", intensity_counts["HEAVY"] <= 3, intensity_counts["HEAVY"], 3, "HEAVY count exceeds 3.")
    add(
        "x2_unify_min_light_protected_1",
        intensity_counts["LIGHT_PROTECTED"] >= 1,
        intensity_counts["LIGHT_PROTECTED"],
        1,
        "At least one LIGHT_PROTECTED bullet required.",
    )

    protected = next((b for b in bullets if b.get("bullet_id") == PROTECTED_BULLET_DEFAULT), None)
    protected_ok = bool(protected) and str(protected.get("rewrite_intensity", "")).upper() == "LIGHT_PROTECTED"
    protected_text = (protected or {}).get("bullet_text", "")
    metrics_ok = all(
        token in protected_text
        for token in ("$22M", "20%", "8", "28")
    )
    add(
        "x2_unify_protected_bullet_preserved_or_justified",
        protected_ok and metrics_ok,
        {"bullet_id": PROTECTED_BULLET_DEFAULT, "intensity": (protected or {}).get("rewrite_intensity")},
        "LIGHT_PROTECTED + core metrics",
        "Protected bul_unify_006 must be LIGHT_PROTECTED with $22M, 20%, and 8-to-28 scale.",
    )

    metrics_preserved = all(
        phrase in combined
        for phrase in ("$22M", "20%", "six months to three weeks")
    ) and ("8" in combined and "28" in combined)
    add(
        "x2_unify_metrics_preserved",
        metrics_preserved,
        combined[:200],
        "core metrics present",
        "Core metrics ($22M, 20%, 8 to 28, six months to three weeks) must appear in bullets.",
    )

    from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
        proof_source_from_metadata,
        scope_ids_membership_only,
    )

    source_ids = set(_all_source_fact_ids(parsed_output, claim_ledger))
    proof_source = proof_source_from_metadata(proof_pool_metadata)
    if proof_source in ("srfs", "broad_skills_ledger"):
        scope_ok, illegal_prefix_ids, forbidden_hits, not_in_allowlist = scope_ids_membership_only(
            source_ids,
            allowed_fact_ids=set(allowed_fact_ids),
            forbidden_prefixes=FORBIDDEN_FACT_PREFIXES,
        )
        scope_threshold = "active_proof_pool_membership"
    else:
        illegal_prefix_ids = sorted({str(s) for s in source_ids if not str(s).startswith("bul_unify_")})
        forbidden_hits = sorted(
            {str(s) for s in source_ids if any(str(s).startswith(prefix) for prefix in FORBIDDEN_FACT_PREFIXES)}
        )
        not_in_allowlist = sorted(
            {
                str(s)
                for s in source_ids
                if str(s).startswith("bul_unify_")
                and str(s) not in allowed_fact_ids
                and str(s).split("_metric_")[0] not in allowed_fact_ids
            }
        )
        scope_ok = bool(source_ids) and not illegal_prefix_ids and not forbidden_hits and not not_in_allowlist
        scope_threshold = "bul_unify_*"
    scope_parts: list[str] = []
    if illegal_prefix_ids:
        scope_parts.append(f"tokens_not_bul_unify_prefix={illegal_prefix_ids}")
    if forbidden_hits:
        scope_parts.append(f"forbidden_cross_lane_tokens={forbidden_hits}")
    if not_in_allowlist:
        scope_parts.append(f"tokens_not_in_allowed_fact_pool={not_in_allowlist}")
    scope_failure = (
        "Fact scope must match active proof pool."
        + (f" ({'; '.join(scope_parts)})" if scope_parts else "")
    )
    add(
        "x2_unify_only_fact_scope",
        scope_ok,
        sorted(source_ids),
        scope_threshold,
        None if scope_ok else scope_failure,
    )

    serialized = json.dumps(parsed_output or {}, sort_keys=True).lower()
    add("x2_no_ibm_fact_leakage", "bul_ibm_" not in serialized, "bul_ibm_", "absent", "IBM fact leakage detected.")
    add(
        "x2_no_insurtech_fact_leakage",
        "bul_insurtech_" not in serialized,
        "bul_insurtech_",
        "absent",
        "InsurTech fact leakage detected.",
    )
    add("x2_no_ey_fact_leakage", "bul_ey_" not in serialized, "bul_ey_", "absent", "EY fact leakage detected.")

    jd_copy, jd_phrase = has_jd_phrase_copy(combined, jd_text)
    add(
        "x2_no_jd_only_claims",
        not jd_copy,
        jd_phrase or "none",
        "no JD copy as proof",
        "JD phrase copied into bullet proof.",
    )

    output_ids = {str(b.get("bullet_id")) for b in bullets if b.get("bullet_id")}
    ledger_ids = set()
    for claim in claim_ledger:
        for fid in claim.get("source_fact_ids") or []:
            ledger_ids.add(str(fid).split("_metric_")[0])
    if proof_source in ("srfs", "broad_skills_ledger"):
        pool_bullet_ids = {str(x) for x in allowed_fact_ids if str(x).startswith("bul_unify_")}
        required_bullet_ids = pool_bullet_ids or output_ids
        coverage_ok = output_ids <= set(allowed_fact_ids) | pool_bullet_ids and bool(output_ids)
        coverage_ok = coverage_ok and all(
            any(rid in allowed_fact_ids or rid.split("_metric_")[0] in allowed_fact_ids for rid in ledger_ids)
            for rid in ledger_ids
        ) if ledger_ids else coverage_ok
        coverage_threshold = "active_pool_bullet_ids"
        coverage_msg = "Every output bullet_id and ledger root must be in active proof pool."
    else:
        required_bullet_ids = set(UNIFY_BULLET_IDS)
        coverage_ok = required_bullet_ids <= output_ids and required_bullet_ids <= ledger_ids
        coverage_threshold = sorted(required_bullet_ids)
        coverage_msg = "Every bul_unify_* bullet must appear in output and claim_ledger."
    add(
        "x2_claim_ledger_coverage_100",
        coverage_ok and len(claim_ledger) >= len(output_ids) and len(output_ids) >= 1,
        {"output_ids": sorted(output_ids), "ledger_roots": sorted(ledger_ids)},
        coverage_threshold,
        coverage_msg,
    )

    metric_granular_ok = True
    for claim in claim_ledger:
        text = str(claim.get("claim_text", "")).lower()
        ids = claim.get("source_fact_ids") or []
        if "$22m" in text or "margin" in text:
            metric_granular_ok = metric_granular_ok and any("bul_unify_006" in str(i) for i in ids)
        if "six months" in text or "three weeks" in text:
            metric_granular_ok = metric_granular_ok and any("bul_unify_004" in str(i) for i in ids)
    add(
        "x2_metric_fact_id_granularity",
        metric_granular_ok,
        len(claim_ledger),
        "metric claims map to bul_unify_004/006",
        "Metric claims lack granular source_fact_ids.",
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
            proof_source_from_metadata,
        )

        coll = _srfs_w4.collect_source_fact_ids_from_bullets_and_ledger(parsed_output, claim_ledger)
        ok_sl, env_sl, fail_sl = evaluate_proof_pool_source_fact_gate(
            section_id="unify_bullets",
            collected_ids=coll,
            allowed_fact_ids=set(allowed_fact_ids),
            proof_pool_metadata=proof_pool_metadata,
            proof_pool_ref=proof_pool_ref,
            proof_pool_digest=proof_pool_digest,
        )
        pt = str((proof_pool_metadata or {}).get("proof_pool_type") or "")
        gate_id = (
            "x2_unify_bullets_source_fact_ids_within_srfs_slice"
            if pt == "selected_role_fact_set"
            or (srfs_source_fact_slice_gate_active and pt not in ("broad_skills_ledger", "base_resume_fallback"))
            else "x2_unify_bullets_active_proof_pool_source_fact_ids"
        )
        add(
            gate_id,
            ok_sl,
            env_sl,
            "active_proof_pool_allowlist_exact",
            fail_sl,
        )

    append_section_input_usage_x2_gates(
        gates,
        artifacts_dir=artifacts_dir or Path("artifacts/apps_rg/runtime_proofs/unify_bullets"),
        allowed_fact_ids=allowed_fact_ids,
        claim_ledger=claim_ledger,
        text_claim_coverage=(parsed_output or {}).get("text_claim_coverage")
        if isinstance(parsed_output, dict)
        else None,
    )

    return gates
