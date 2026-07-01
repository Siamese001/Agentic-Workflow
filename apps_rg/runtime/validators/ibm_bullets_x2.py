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
    "self_check",
}

CORE_METRIC_TOKENS = ("20%", "weeks to hours")

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
    (("weeks to hours", "weeks-to-hours"), "bul_ibm_002"),
    (("20%", "20 %"), "bul_ibm_005"),
)


def _ibm_metric_anchors_on_assigned_bullets(
    bullets: list[dict[str, Any]],
    plan_facts: list[dict[str, Any]] | None = None,
) -> tuple[bool, list[str]]:
    """Each bul_ibm_* must have ANY recognizable metric token in its bullet_text.

    Accepts EITHER the canonical IBM_METRIC_ANCHOR_RULES token (when PROVIDER_MODEL + canonical
    bullet alignment holds) OR the active plan_fact's metric_raw (when the
    augmented_skills_graph selector has reassigned the bullet slot to a different fact
    with its own metric). Closes Bug:IbmLockedMetricInjectionGarblesGraphSelectedBullets
    by refusing to force the canonical metric onto bullets whose graph-selected fact
    carries a different one.
    """
    by_id = {str(b.get("bullet_id")): b for b in bullets if b.get("bullet_id")}
    plan_by_bid = {
        str(f.get("fact_id") or "").strip(): f
        for f in plan_facts or []
        if isinstance(f, dict)
    }
    # W5 (apps-rg-aig-remaining-lanes-closeout-d4e1f7): the live selected_fact_plan is
    # slot-keyed ({"bul_ibm_001": {...}}), not a {"facts": [...]} list, so plan_by_bid came up
    # empty and the no-metric escape below never fired — anchors then fell back to the canonical
    # tokens, three of which (30%, 25%, $15M) are HOLD-forbidden figures the hold-metric gate
    # blocks. Accept slot-keyed dict rows here so a slot whose plan fact carries no metric is
    # legitimately metric-free instead of being forced into the contradiction.
    for f in plan_facts or []:
        if isinstance(f, dict) and not f.get("fact_id"):
            for k, v in f.items():
                if isinstance(v, dict) and str(k).startswith("bul_ibm_") and k not in plan_by_bid:
                    plan_by_bid[str(k)] = v
    failures: list[str] = []
    for needles, root in IBM_METRIC_ANCHOR_RULES:
        bullet = by_id.get(root)
        if bullet is None:
            failures.append(f"missing_bullet:{root}")
            continue
        tl = str(bullet.get("bullet_text") or "").lower()
        has_canonical = any(n.lower() in tl for n in needles)
        if has_canonical:
            continue
        plan_fact = plan_by_bid.get(root) or {}
        plan_metric = str(plan_fact.get("metric_raw") or "").strip().lower()
        plan_has_metric = bool(plan_fact.get("has_metric") or plan_metric)
        # Graph selector chose a fact with NO metric for this slot -> the bullet
        # legitimately has no metric to claim. Don't fabricate one.
        if plan_fact and not plan_has_metric:
            continue
        if plan_metric and plan_metric in tl:
            continue
        # Also accept any visible token from the plan_fact's metric_raw.
        if plan_metric:
            for chunk in re.findall(r"[\$\d][\$\d\.\,\%a-z\-]*", plan_metric):
                if chunk and chunk in tl:
                    has_canonical = True
                    break
            if has_canonical:
                continue
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


def _metric_granularity_ok(
    bullets: list[dict[str, Any]],
    claim_ledger: list[dict[str, Any]],
    plan_facts: list[dict[str, Any]] | None = None,
) -> bool:
    """Metric-bearing bullet or ledger text must cite the matching bul_ibm_* root.

    Skips the canonical pairing assertion when the active plan_fact for the *citing*
    bullet/claim carries its own ``metric_raw`` that already appears in the text — in
    that case the augmented_skills_graph selector intentionally reassigned the slot and
    the canonical token in the text is graph-selected, not canonical-drift. Closes the
    second half of Bug:IbmLockedMetricInjectionGarblesGraphSelectedBullets.
    """

    rules: list[tuple[tuple[str, ...], str]] = list(IBM_METRIC_ANCHOR_RULES)

    plan_by_bid: dict[str, dict[str, Any]] = {
        str(f.get("fact_id") or "").strip(): f
        for f in (plan_facts or [])
        if isinstance(f, dict) and str(f.get("fact_id") or "").strip()
    }

    def _plan_metric_for(ids_raw: list[str]) -> str:
        """Return the metric_raw for the first matching plan_fact, lowercased."""
        for fid in ids_raw:
            base = str(fid).split("_metric_")[0]
            plan_fact = plan_by_bid.get(base) or plan_by_bid.get(str(fid))
            if plan_fact:
                m = str(plan_fact.get("metric_raw") or "").strip().lower()
                if m:
                    return m
        return ""

    def check_text(text: str, ids_raw: list[str]) -> bool:
        tl = text.lower()
        ids_lower = [i.lower() for i in ids_raw]
        plan_metric = _plan_metric_for(ids_raw)
        for needles, root in rules:
            if not any(n.lower() in tl for n in needles):
                continue
            if any(root in i for i in ids_lower):
                continue
            # Canonical metric appears in text but not cited to canonical root —
            # accept ONLY when the plan_fact for the citing slot owns this metric.
            if plan_metric and any(n.lower() in plan_metric for n in needles):
                continue
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

    from apps_rg.runtime.c0.graph_story_authority import (
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

    from apps_rg.runtime.sections.ibm_bullets_graph_evidence import (
        IBM_TRACK_RANKED_SELECTION_METHOD,
        check_ibm_bullets_phase2_career_track_scope,
    )

    selected_plan = (
        (runtime_payload or {}).get("selected_fact_plan")
        if runtime_payload
        else (parsed_output or {}).get("selected_fact_plan")
    )
    selection_method = str(
        (proof_pool_metadata or {}).get("selection_method")
        or (selected_plan or {}).get("selection_method")
        or ""
    )
    if selection_method == IBM_TRACK_RANKED_SELECTION_METHOD:
        phase2_ok, phase2_obs = check_ibm_bullets_phase2_career_track_scope(
            proof_pool_metadata=proof_pool_metadata,
            selected_fact_plan=selected_plan,
        )
        add(
            "x2_ibm_phase2_career_track_scope",
            phase2_ok,
            phase2_obs,
            "track_data_tech_cloud_ml_only; employment 2017-04 to 2022-10",
            None
            if phase2_ok
            else str(phase2_obs.get("reason") or phase2_obs),
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

    add("x2_ibm_bullet_count_5", len(bullets) == 5, len(bullets), 5, "Must output exactly 5 IBM bullets.")

    from apps_rg.runtime.validators.bullet_line_discipline_x2 import (
        register_bullet_line_discipline_x2_gates,
    )

    register_bullet_line_discipline_x2_gates(
        add,
        bullets,
        lane_prefix="ibm",
        section_id="ibm_bullets",
    )

    po_raw = parsed_output or {}
    missing_top_level = sorted(k for k in REQUIRED_TOP_LEVEL if k not in po_raw)
    add(
        "x2_required_top_level_json_keys",
        not missing_top_level,
        missing_top_level,
        sorted(REQUIRED_TOP_LEVEL),
        f"Missing required top-level JSON keys: {', '.join(missing_top_level)}" if missing_top_level else None,
    )

    from apps_rg.runtime.reasoning.employment_bullet_output_sanitize import (
        find_rewrite_intensity_model_violations,
    )

    intensity_violations = find_rewrite_intensity_model_violations(
        parsed_output=po_raw,
        bullets=bullets,
    )
    add(
        "x2_ibm_no_rewrite_intensity_model",
        not intensity_violations,
        intensity_violations or "absent",
        "no rewrite_distribution / rewrite_intensity fields",
        f"Retired rewrite-intensity model fields present: {', '.join(intensity_violations)}"
        if intensity_violations
        else None,
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

    plan_facts_for_anchors = list((selected_plan or {}).get("facts") or [])
    if not plan_facts_for_anchors and isinstance(selected_plan, dict):
        # Slot-keyed plan shape ({"bul_ibm_001": {...}}) — adapt to fact rows so the anchor
        # check sees each slot's real metric state (see _ibm_metric_anchors_on_assigned_bullets).
        plan_facts_for_anchors = [
            {"fact_id": k, **v}
            for k, v in selected_plan.items()
            if isinstance(v, dict) and str(k).startswith("bul_ibm_")
        ]
    anchor_ok, anchor_fail = _ibm_metric_anchors_on_assigned_bullets(
        bullets, plan_facts=plan_facts_for_anchors
    )
    add(
        "x2_ibm_metric_anchor_bullet_ownership",
        anchor_ok,
        anchor_fail or "ok",
        "each core metric on assigned bul_ibm_* bullet_text (canonical or plan-fact metric_raw)",
        None if anchor_ok else f"Metric anchor ownership failed: {anchor_fail}",
    )

    # Role-episode wave: forbid HOLD/DO_NOT_PROMOTE canonical metric set ($15M, 25/30/35/40%).
    from apps_rg.runtime.sections.ibm_role_episode_evidence import (
        PROMOTABLE_METRIC_OUTCOME_IDS,
        scan_forbidden_metrics_in_text,
    )

    forbidden_hits = scan_forbidden_metrics_in_text(combined)
    add(
        "x2_ibm_hold_metric_forbidden_in_output",
        not forbidden_hits,
        forbidden_hits or "none",
        "no $15M/$30M or overloaded 25/30/35/40% in bullet text",
        f"Forbidden metrics in output: {forbidden_hits}" if forbidden_hits else None,
    )

    # Promotable metrics: optional per bullet when has_metric=true and metric_outcome_ids bound.
    metrics_preserved = not forbidden_hits
    metrics_obs: Any = {"forbidden_absent": not forbidden_hits, "promotable_ids": list(PROMOTABLE_METRIC_OUTCOME_IDS)}
    metrics_thr = "no HOLD/DO_NOT_PROMOTE metrics; promotable only via metric_outcome_ids"
    metrics_fail = None if metrics_preserved else f"Forbidden metrics: {forbidden_hits}"
    add(
        "x2_ibm_metrics_preserved",
        metrics_preserved,
        metrics_obs,
        metrics_thr,
        metrics_fail,
    )

    # W2: graph_skill_node_ids required per bullet in change_log (Bullet Proof Bundle Redesign)
    po_change_log = list((parsed_output or {}).get("change_log") or [])
    bullets_missing_skill_ids: list[str] = []
    cl_bullet_ids: set[str] = set()
    for cl_entry in po_change_log:
        if not isinstance(cl_entry, dict):
            continue
        bid_cl = str(cl_entry.get("bullet_id") or "")
        if not bid_cl.startswith("bul_ibm_"):
            continue
        cl_bullet_ids.add(bid_cl)
        skill_ids = (
            cl_entry.get("graph_skill_node_ids")
            or cl_entry.get("skill_ids_used")
            or []
        )
        if not skill_ids:
            bullets_missing_skill_ids.append(bid_cl)
    for b in bullets:
        bid_b = str(b.get("bullet_id") or "")
        if bid_b.startswith("bul_ibm_") and bid_b not in cl_bullet_ids:
            bullets_missing_skill_ids.append(bid_b)
    add(
        "x2_ibm_bullet_graph_skill_node_ids_required",
        not bullets_missing_skill_ids,
        bullets_missing_skill_ids or "all_present",
        "non-empty graph_skill_node_ids per bul_ibm_* in change_log",
        (
            f"Missing graph_skill_node_ids in change_log for: {bullets_missing_skill_ids}"
            if bullets_missing_skill_ids
            else None
        ),
    )

    # Role episode bundle binding required per bullet (not flat skill-only proof).
    from apps_rg.runtime.sections.ibm_role_episode_evidence import (
        IBM_BULLET_SLOT_BUNDLE_MAP,
        PROMOTABLE_METRIC_OUTCOME_IDS,
        is_flat_skill_only_graph_packet,
    )

    pp_meta = dict(proof_pool_metadata or {})
    bundles_present = bool(pp_meta.get("role_episode_bundles")) or bool(
        (runtime_payload or {}).get("role_episode_bundle_ids")
    )
    flat_only = is_flat_skill_only_graph_packet(pp_meta) and not bundles_present
    add(
        "x2_ibm_role_episode_bundles_in_proof_pool",
        bundles_present and not flat_only,
        {
            "bundles_present": bundles_present,
            "flat_skill_only": flat_only,
            "consumption_mode": pp_meta.get("role_episode_bundle_consumption_mode"),
        },
        "role_episode_bundles in proof_pool_metadata",
        "IBM proof pool missing role_episode_bundles or flat skill-only context"
        if not bundles_present or flat_only
        else None,
    )

    bullets_missing_bundle_id: list[str] = []
    bullets_metric_unsupported: list[str] = []
    allowed_outcomes = set(PROMOTABLE_METRIC_OUTCOME_IDS)
    by_bullet_id = {str(b.get("bullet_id")): b for b in bullets if b.get("bullet_id")}
    for cl_entry in po_change_log:
        if not isinstance(cl_entry, dict):
            continue
        bid_cl = str(cl_entry.get("bullet_id") or "")
        if not bid_cl.startswith("bul_ibm_"):
            continue
        reb = str(cl_entry.get("role_episode_bundle_id") or "").strip()
        expected = IBM_BULLET_SLOT_BUNDLE_MAP.get(bid_cl, "")
        if not reb:
            bullets_missing_bundle_id.append(bid_cl)
        elif expected and reb != expected:
            bullets_missing_bundle_id.append(f"{bid_cl}:wrong_bundle={reb}")
        skill_ids = list(
            cl_entry.get("graph_skill_node_ids") or cl_entry.get("skill_ids_used") or []
        )
        if not skill_ids:
            bullets_missing_skill_ids.append(bid_cl)
        metric_ids = [str(x) for x in (cl_entry.get("metric_outcome_ids") or [])]
        bullet_row = by_bullet_id.get(bid_cl) or {}
        if bullet_row.get("has_metric") and metric_ids:
            if not all(mid in allowed_outcomes for mid in metric_ids):
                bullets_metric_unsupported.append(f"{bid_cl}:invalid_metric_outcome_ids")

    for b in bullets:
        bid_b = str(b.get("bullet_id") or "")
        if bid_b.startswith("bul_ibm_") and bid_b not in cl_bullet_ids:
            bullets_missing_bundle_id.append(bid_b)

    add(
        "x2_ibm_bullet_role_episode_bundle_id_required",
        not bullets_missing_bundle_id,
        bullets_missing_bundle_id or "all_present",
        "role_episode_bundle_id per bul_ibm_* in change_log",
        (
            f"Missing or wrong role_episode_bundle_id: {bullets_missing_bundle_id}"
            if bullets_missing_bundle_id
            else None
        ),
    )

    add(
        "x2_ibm_metric_outcome_id_required_when_has_metric",
        not bullets_metric_unsupported,
        bullets_metric_unsupported or "all_traceable",
        "metric_outcome_ids from PROMOTABLE allow-list when has_metric=true",
        (
            f"Unsupported metric outcome binding: {bullets_metric_unsupported}"
            if bullets_metric_unsupported
            else None
        ),
    )

    # W3: N-gram overlap anti-leakage gates (WARN mode — calibrate before hard-fail activation)
    from apps_rg.runtime.validators.bullet_ngram_overlap_x2 import (
        GATE_ID_BASE_RESUME,
        GATE_ID_E0_EXAMPLE,
        run_bullet_ngram_overlap_gates,
    )

    ngram_base_pass, ngram_base_results, ngram_e0_pass, ngram_e0_results = run_bullet_ngram_overlap_gates(
        bullets,
        section_id="ibm_bullets",
        warn_only=True,
    )
    ngram_base_violations = [r for r in ngram_base_results if r.failure_reason]
    add(
        GATE_ID_BASE_RESUME + "_ibm",
        ngram_base_pass,
        [r.failure_reason for r in ngram_base_violations] or "all_below_threshold",
        f"<= {int(0.25 * 100)}% 4-gram overlap with base resume (WARN mode)",
        "; ".join(r.failure_reason for r in ngram_base_violations if r.failure_reason) or None,
    )
    ngram_e0_violations = [r for r in ngram_e0_results if r.failure_reason]
    add(
        GATE_ID_E0_EXAMPLE + "_ibm",
        ngram_e0_pass,
        [r.failure_reason for r in ngram_e0_violations] or "all_below_threshold",
        f"<= {int(0.20 * 100)}% 4-gram overlap with E0 examples (WARN mode)",
        "; ".join(r.failure_reason for r in ngram_e0_violations if r.failure_reason) or None,
    )

    # W4: Quality floor gates (seniority proxy, technical specificity, generic consulting blocklist)
    from apps_rg.runtime.validators.bullet_quality_floor_x2 import (
        run_bullet_quality_floor_gates,
    )
    from apps_rg.runtime.sections.ibm_bullets_graph_evidence import IBM_BULLET_MECHANISM_VOCAB

    sen_pass, sen_results, tech_pass, tech_results, cons_pass, cons_results = (
        run_bullet_quality_floor_gates(
            bullets,
            section_id="ibm_bullets",
            mechanism_vocab_by_slot=IBM_BULLET_MECHANISM_VOCAB,
        )
    )
    sen_failures = [r.failure_reason for r in sen_results if r.failure_reason]
    add(
        "x2_bullet_seniority_floor",
        sen_pass,
        sen_failures or "all_pass",
        "score >= 1 (strong_verb OR scale_signal + no weak_verb)",
        "; ".join(sen_failures) if sen_failures else None,
    )
    tech_failures = [r.failure_reason for r in tech_results if r.failure_reason]
    add(
        "x2_bullet_technical_specificity_floor",
        tech_pass,
        tech_failures or "all_pass",
        "at least one named mechanism/technology per bullet",
        "; ".join(tech_failures) if tech_failures else None,
    )
    cons_failures = [r.failure_reason for r in cons_results if r.failure_reason]
    add(
        "x2_no_generic_consulting_substitution",
        cons_pass,
        cons_failures or "all_pass",
        "zero consulting-speak substitution phrases per bullet",
        "; ".join(cons_failures) if cons_failures else None,
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

    # Leakage scan excludes the model's free-form ``self_check`` attestation (W5,
    # apps-rg-aig-remaining-lanes-closeout-d4e1f7): an attestation key naming the forbidden
    # marker (e.g. "no_bul_unify_references") false-trips the substring scan.
    serialized = json.dumps(
        {k: v for k, v in (parsed_output or {}).items() if k != "self_check"},
        sort_keys=True,
    ).lower()
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
        _metric_granularity_ok(bullets, claim_ledger, plan_facts=plan_facts_for_anchors),
        len(claim_ledger),
        "metric claims map to bul_ibm_* (canonical pairing OR plan-fact metric ownership)",
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
    no_silent_mock = not (provider_requested == "external_claude" and runtime_generation_status == "MOCKED")
    add(
        "x2_no_silent_mock_fallback",
        no_silent_mock,
        runtime_generation_status,
        "REAL_LLM when PROVIDER_MODEL requested",
        "Silent mock fallback detected.",
    )

    from apps_rg.runtime.section_judge_policy import get_section_judge_policy

    required_judge_providers = list(
        get_section_judge_policy("ibm_bullets").required_judge_providers
    )

    judges_ok, judges_reason = check_judge_rows_present(
        x1d_judges,
        required_providers=required_judge_providers,
    )
    add(
        "x2_x1d_required_judges_present",
        judges_ok,
        judges_reason,
        required_judge_providers,
        judges_reason,
    )

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
        from apps_rg.runtime.sections import graph_evidence_contract as _graph_evidence
        from apps_rg.runtime.validators.proof_pool_source_fact_validation import (
            evaluate_proof_pool_source_fact_gate,
            proof_pool_x2_gate_id,
        )

        coll_ib = _graph_evidence.collect_source_fact_ids_from_bullets_and_ledger(parsed_output, claim_ledger)
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


IBM_BULLET_GRAPH_SKILL_NODE_IDS_GATE_ID = "x2_ibm_bullet_graph_skill_node_ids_required"
IBM_BULLET_METRIC_SOURCE_GATE_ID = "x2_ibm_metric_source_required"

__all__ = [
    "IBM_BULLET_GRAPH_SKILL_NODE_IDS_GATE_ID",
    "IBM_BULLET_IDS",
    "IBM_BULLET_METRIC_SOURCE_GATE_ID",
    "IBM_METRIC_ANCHOR_RULES",
    "REQUIRED_TOP_LEVEL",
    "TEXT_COVERAGE_INTEGRITY_GATE_ID",
    "TAXONOMY_LABEL_PREFIX_PATTERN",
    "build_ibm_bullets_text_claim_coverage",
    "check_ibm_bullets_text_claim_coverage_integrity",
    "ibm_bullet_text_has_taxonomy_label_prefix",
    "run_ibm_bullets_x2_gates",
]
