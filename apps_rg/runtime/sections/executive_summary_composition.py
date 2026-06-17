"""Graph-backed executive summary composition plan (painting-plan enforcement)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    FSA_CREDENTIAL_FACT_ID,
    QUANT_METRIC_DISPLAY_FACT_ID,
    SENTENCE_ARC_SVP_STRATEGY,
    format_s6_briefing_forward_targeting_anchor,
)
from apps_rg.runtime.validators.executive_summary_x2 import split_sentences

COMPOSITION_STYLE = "executive_painting"
COMPOSITION_PLAN_SCHEMA = "executive_summary_composition_plan_v1"

BRUSHSTROKE_ROLES = (
    "B1_executive_identity",
    "B2_governed_platform_system",
    "B3_control_evidence_discipline",
    "B4_business_role_fit",
)

# Six-sentence product band: index 0..5 maps to brushstroke + arc role (runtime + PA injection).
SENTENCE_ARC_DEFAULT: tuple[dict[str, str], ...] = (
    {
        "brushstroke_id": "B1_executive_identity",
        "arc_role": "thesis",
        "guidance": "Executive thesis and regulated platform scope; no mechanism inventory.",
    },
    {
        "brushstroke_id": "B2_governed_platform_system",
        "arc_role": "platform_system",
        "guidance": "One synthesized platform/runtime clause; max two mechanism terms verbatim from facts.",
    },
    {
        "brushstroke_id": "B2_governed_platform_system",
        "arc_role": "operating_model",
        "guidance": "Lifecycle, scale-out, or operating-model substance from allowed facts.",
    },
    {
        "brushstroke_id": "B3_control_evidence_discipline",
        "arc_role": "governance_evidence",
        "guidance": "Governance, lineage, or validation discipline when facts support it.",
    },
    {
        "brushstroke_id": "B4_business_role_fit",
        "arc_role": "commercial_outcomes",
        "guidance": "Metrics and commercial outcomes woven into narrative; not a bullet dump.",
    },
    {
        "brushstroke_id": "B4_business_role_fit",
        "arc_role": "integrated_capstone",
        "guidance": "Integrated credibility or enterprise-direction capstone from allowed facts only.",
    },
)

MECHANISM_TERMS = (
    "routing",
    "retrieval",
    "graphrag",
    "graph-aware retrieval",
    "telemetry",
    "sandboxing",
    "sandboxed",
    "orchestration",
    "multi-agent",
    "policy",
    "replay",
    "write control",
    "gates",
    "deterministic",
    "vector services",
    "microservices",
    "pipelines",
)

GENERIC_AI_HYPE = (
    "cutting-edge",
    "state-of-the-art",
    "world-class",
    "best-in-class",
    "synergy",
    "leverage ai",
    "unlock value",
    "paradigm",
    "disruptive innovation",
)

EXEC_VOICE_BAD_OPENERS = (
    "engineering executive with expertise in",
    "with extensive experience",
    "an experienced leader",
    "an experienced engineering executive",
    "seasoned executive",
    "results-driven",
    "proven track record",
    "dynamic leader",
)

_KEYWORD_SKILL_REFS: tuple[tuple[str, str], ...] = (
    ("agentic", "skill_governed_agentic_systems_architecture"),
    ("deterministic routing", "skill_deterministic_route_selection"),
    ("routing", "skill_deterministic_route_selection"),
    ("orchestration", "skill_managed_workflow_orchestration"),
    ("graphrag", "skill_graph_aware_relationship_grounding"),
    ("retrieval", "skill_dense_sparse_exact_retrieval_design"),
    ("governance", "skill_ai_governance_certification"),
    ("basel", "skill_sr_basel_ccar_lineage_regulatory"),
    ("ccar", "skill_sr_basel_ccar_lineage_regulatory"),
    ("revenue", "skill_agentic_platform_commercialization"),
    ("commercial", "skill_agentic_platform_commercialization"),
    ("platform lifecycle", "skill_reusable_agentic_platform_architecture"),
)


def _fact_id_base(fid: str) -> str:
    s = str(fid or "").strip()
    return s.split("_metric_", 1)[0] if "_metric_" in s else s


_CERT_DISPLAY_OPTIONAL_PREFIXES = ("fact_certs",)


def _filter_required_display_fact_ids(role: str, req_ids: list[str]) -> list[str]:
    """B4 may cite cert facts in ledger; do not require cert labels in display prose (I0 alignment)."""
    if role != "B4_business_role_fit":
        return req_ids
    return [
        fid
        for fid in req_ids
        if not any(fid.startswith(prefix) for prefix in _CERT_DISPLAY_OPTIONAL_PREFIXES)
    ]


def _classify_fact_brushstroke_role(fact_id: str, claim_text: str) -> str:
    fid = _fact_id_base(fact_id).lower()
    low = claim_text.lower()
    if any(x in fid for x in ("revenue", "sales", "commercial", "margin", "ops")):
        return "B4_business_role_fit"
    if any(x in fid for x in ("cert", "quant", "hpc", "actuarial")):
        return "B4_business_role_fit"
    if any(x in fid for x in ("exec", "leadership")) or "organization" in low and "ml engineering" in low:
        return "B1_executive_identity"
    if any(x in fid for x in ("governance", "regulatory", "risk", "ccar", "basel", "lineage", "validation")):
        return "B3_control_evidence_discipline"
    if any(
        tok in low
        for tok in (
            "governed",
            "agentic",
            "routing",
            "orchestration",
            "retrieval",
            "platform",
            "microservices",
            "architecture",
            "lifecycle",
        )
    ):
        return "B2_governed_platform_system"
    return "B2_governed_platform_system"


def _skill_ids_for_facts_from_track_expansion(
    selected_facts: list[dict[str, Any]],
    proof_pool_metadata: dict[str, Any] | None,
) -> list[str]:
    """Scope graph skill refs to skills linked to the given facts (track expansion SSOT)."""
    if not isinstance(proof_pool_metadata, dict):
        return []
    te = proof_pool_metadata.get("track_weighted_graph_expansion")
    if not isinstance(te, dict):
        return []
    fact_bases = {
        _fact_id_base(str(f.get("fact_id") or ""))
        for f in selected_facts
        if isinstance(f, dict) and str(f.get("fact_id") or "").strip()
    }
    if not fact_bases:
        return []
    refs: list[str] = []
    for sk in te.get("selected_skills") or []:
        if not isinstance(sk, dict):
            continue
        sid = str(sk.get("skill_id") or "").strip()
        if not sid:
            continue
        fid = str(sk.get("fact_id") or "").strip()
        link_facts = [str(x).strip() for x in (sk.get("fact_id_links") or []) if str(x).strip()]
        matched = bool(fid and _fact_id_base(fid) in fact_bases)
        if not matched:
            matched = any(_fact_id_base(lf) in fact_bases for lf in link_facts)
        if matched:
            refs.append(sid)
    return sorted(set(refs))


def _infer_graph_skill_refs(
    selected_facts: list[dict[str, Any]],
    *,
    proof_pool_metadata: dict[str, Any] | None,
) -> list[str]:
    scoped = _skill_ids_for_facts_from_track_expansion(selected_facts, proof_pool_metadata)
    if scoped:
        return scoped
    refs: list[str] = []
    if isinstance(proof_pool_metadata, dict):
        for sid in proof_pool_metadata.get("c03_selected_skill_ids") or []:
            s = str(sid).strip()
            if s:
                refs.append(s)
    if refs:
        return sorted(set(refs))
    blob = " ".join(str(r.get("claim_text") or "") for r in selected_facts if isinstance(r, dict)).lower()
    for needle, skill_id in _KEYWORD_SKILL_REFS:
        if needle in blob:
            refs.append(skill_id)
    return sorted(set(refs))


def _brushstroke_for_role(
    role: str,
    facts: list[dict[str, Any]],
    allowed: set[str],
    *,
    proof_pool_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    role_facts = [
        f
        for f in facts
        if isinstance(f, dict) and _classify_fact_brushstroke_role(str(f.get("fact_id") or ""), str(f.get("claim_text") or "")) == role
    ]
    if not role_facts and role == "B1_executive_identity" and facts:
        role_facts = [facts[0]]
    req_ids = _filter_required_display_fact_ids(
        role,
        sorted(
            {
                _fact_id_base(str(f.get("fact_id") or ""))
                for f in role_facts
                if _fact_id_base(str(f.get("fact_id") or "")) in allowed
            }
        ),
    )
    skill_refs = _infer_graph_skill_refs(role_facts, proof_pool_metadata=proof_pool_metadata)
    image_goals = {
        "B1_executive_identity": "Establish executive identity and regulated enterprise platform scope.",
        "B2_governed_platform_system": "Paint the governed agentic platform system (runtime, retrieval, orchestration).",
        "B3_control_evidence_discipline": "Show control, lineage, validation, and audit-ready evidence discipline.",
        "B4_business_role_fit": "Close with commercial, scale, and credibility outcomes tied to role fit.",
    }
    return {
        "brushstroke_id": role,
        "brushstroke_role": role,
        "image_goal": image_goals.get(role, "Executive portrait brushstroke."),
        "allowed_graph_skill_ids": skill_refs,
        "required_fact_ids": req_ids,
        "allowed_source_fact_ids": req_ids,
        "support_status": "SUPPORTED" if req_ids else "SKIPPED",
        "forbidden_failures": [
            "mechanism_inventory_in_thesis",
            "unsupported_claim",
            "jd_or_briefing_as_proof",
        ],
    }


def bind_facts_to_brushstrokes(
    facts: list[dict[str, Any]],
    *,
    allowed_fact_ids: set[str],
    proof_pool_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map allowed facts to B1–B4 brushstroke roles (selection-time metadata)."""
    allowed = {_fact_id_base(x) for x in allowed_fact_ids}
    bindings: list[dict[str, Any]] = []
    for fact in facts:
        if not isinstance(fact, dict):
            continue
        fid = str(fact.get("fact_id") or "")
        role = _classify_fact_brushstroke_role(fid, str(fact.get("claim_text") or ""))
        bindings.append(
            {
                "fact_id": fid,
                "fact_id_base": _fact_id_base(fid),
                "brushstroke_role": role,
                "in_allowed_pool": _fact_id_base(fid) in allowed,
            }
        )
    covered_roles = sorted({b["brushstroke_role"] for b in bindings if b.get("in_allowed_pool")})
    missing_roles = [r for r in BRUSHSTROKE_ROLES if r not in covered_roles]
    return {
        "brushstroke_fact_bindings": bindings,
        "brushstroke_required_ids": list(BRUSHSTROKE_ROLES),
        "brushstroke_covered_ids": covered_roles,
        "brushstroke_missing_ids": missing_roles,
        "graph_skill_refs": _infer_graph_skill_refs(facts, proof_pool_metadata=proof_pool_metadata),
    }


def check_exec_summary_brushstroke_coverage_pre_l2(
    composition_plan: dict[str, Any] | None,
    *,
    strict: bool = False,
) -> tuple[str, dict[str, Any]]:
    """Pre-L2 brushstroke gate — block or allow explicit gaps (no graph hallucination)."""
    plan = composition_plan or {}
    brushstrokes = list(plan.get("brushstrokes") or [])
    missing: list[str] = []
    for role in BRUSHSTROKE_ROLES:
        role_rows = [b for b in brushstrokes if b.get("brushstroke_role") == role]
        req = []
        for row in role_rows:
            req.extend(list(row.get("required_fact_ids") or []))
        if not req:
            missing.append(role)
    receipt = {
        "brushstroke_required_ids": list(BRUSHSTROKE_ROLES),
        "brushstroke_covered_ids": [r for r in BRUSHSTROKE_ROLES if r not in missing],
        "brushstroke_missing_ids": missing,
        "brushstroke_fact_bindings": bind_facts_to_brushstrokes(
            [],
            allowed_fact_ids=set(),
        ).get("brushstroke_fact_bindings"),
    }
    if not missing:
        return "PASS", {**receipt, "brushstroke_gate_status": "PASS"}
    if strict:
        return "BLOCKED", {
            **receipt,
            "brushstroke_gate_status": "BLOCKED",
            "gap_notes": [f"missing_brushstroke:{r}" for r in missing],
        }
    return "GAP_ALLOWED", {
        **receipt,
        "brushstroke_gate_status": "GAP_ALLOWED",
        "gap_notes": [f"missing_brushstroke:{r}" for r in missing],
    }


def enrich_strategy_sentence_arc_bindings(
    sentence_arc: list[dict[str, Any]],
    *,
    allowed_fact_ids: set[str],
    briefing_text: str = "",
    jd_text: str = "",
    strategy_executive: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Attach S5 metric + S6 targeting-forward bindings for judge-aligned composition (W4)."""
    meta: dict[str, Any] = {}
    if not strategy_executive:
        return sentence_arc, meta

    allowed = {_fact_id_base(x) for x in allowed_fact_ids}
    has_metric = QUANT_METRIC_DISPLAY_FACT_ID in allowed
    has_fsa = FSA_CREDENTIAL_FACT_ID in allowed
    out: list[dict[str, Any]] = []
    for row in sentence_arc:
        enriched = dict(row)
        idx = int(enriched.get("sentence_index") or 0)
        if idx == 4 and has_metric and has_fsa:
            enriched["required_source_fact_ids"] = [
                QUANT_METRIC_DISPLAY_FACT_ID,
                FSA_CREDENTIAL_FACT_ID,
            ]
            enriched["s5_metric_display_fact_id"] = QUANT_METRIC_DISPLAY_FACT_ID
            enriched["s5_credential_fact_id"] = FSA_CREDENTIAL_FACT_ID
        if idx == 5:
            anchor = format_s6_briefing_forward_targeting_anchor(
                briefing_text=briefing_text,
                jd_text=jd_text,
            )
            enriched["s6_targeting_forward_anchor"] = anchor
        out.append(enriched)

    if has_metric and has_fsa:
        meta["s5_metric_binding"] = {
            "metric_display_fact_id": QUANT_METRIC_DISPLAY_FACT_ID,
            "credential_fact_id": FSA_CREDENTIAL_FACT_ID,
            "display_metric_required": True,
        }
    meta["s6_targeting_forward_anchor"] = format_s6_briefing_forward_targeting_anchor(
        briefing_text=briefing_text,
        jd_text=jd_text,
    )
    return out, meta


def build_sentence_arc(
    *,
    target_role: str,
    strategy_executive: bool,
) -> list[dict[str, Any]]:
    """Deterministic six-sentence arc map for L2 and post-parse sentence_map."""
    template = SENTENCE_ARC_SVP_STRATEGY if strategy_executive else SENTENCE_ARC_DEFAULT
    out: list[dict[str, Any]] = []
    for idx, row in enumerate(template):
        out.append(
            {
                "sentence_index": idx,
                "brushstroke_id": row["brushstroke_id"],
                "arc_role": row["arc_role"],
                "guidance": row["guidance"],
            }
        )
    if strategy_executive:
        out[0]["guidance"] = (
            f"{out[0]['guidance']} Target role framing: {target_role.strip() or 'SVP IT strategy'} "
            "(targeting only — never cite role title as proof)."
        )
    return out


def format_composition_plan_for_pa(plan: dict[str, Any]) -> str:
    """Compact PA block: brushstrokes + six-sentence arc (pre-L2 painting contract)."""
    lines = [
        "<executive_summary_composition_plan>",
        f"schema: {plan.get('schema') or COMPOSITION_PLAN_SCHEMA}",
        f"dominant_arc: {plan.get('dominant_arc')}",
        f"target_picture: {plan.get('target_picture')}",
    ]
    missing = plan.get("brushstroke_missing_ids") or []
    if missing:
        lines.append(f"brushstroke_gaps (weave if facts exist): {', '.join(missing)}")
    brushstrokes = [bs for bs in (plan.get("brushstrokes") or []) if isinstance(bs, dict)]
    for bs in brushstrokes:
        bid = bs.get("brushstroke_id")
        req = bs.get("required_fact_ids") or []
        lines.append(f"- {bid}: facts={req or '[]'} — {bs.get('image_goal')}")
    lines.append(
        "narrative_arc_weights (thematic emphasis for judge-aligned synthesis — NOT one sentence per brushstroke index):"
    )
    s5_binding = plan.get("s5_metric_binding") or {}
    if s5_binding:
        lines.append(
            "s5_metric_binding: "
            f"display_metric_fact_id={s5_binding.get('metric_display_fact_id')} "
            f"credential_fact_id={s5_binding.get('credential_fact_id')} "
            f"display_metric_required={s5_binding.get('display_metric_required')}"
        )
    # S4 opener directive: when SVP strategy lane has ≥3 brushstrokes covering S2–S4,
    # S2 and S3 will likely consume both stock-bridge slots — prescribe a non-stock
    # opener for S4 to enforce the max-two contract (x2_exec_summary_stock_bridge_max_two).
    strategy_lane = bool(plan.get("strategy_executive") or plan.get("dominant_arc") == "B2_governed_platform_system")
    if strategy_lane and len(brushstrokes) >= 3:
        lines.append(
            "s4_opener_directive: S4 MUST use a non-stock opener "
            '(e.g. "In parallel," / "That operating foundation also," / "The same platform discipline") '
            "— S2 and S3 are expected to consume both available stock-bridge slots "
            "(from that / against that / complementing that / building on that / through that / with that governance); "
            "a third stock bridge in S4 will fail x2_exec_summary_stock_bridge_max_two."
        )
    s6_anchor = str(plan.get("s6_targeting_forward_anchor") or "").strip()
    if s6_anchor:
        lines.append(s6_anchor)
    for row in plan.get("sentence_arc") or []:
        if not isinstance(row, dict):
            continue
        idx = row.get("sentence_index")
        req = row.get("required_source_fact_ids") or []
        req_note = f" required_source_fact_ids={req}" if req else ""
        s6_row_anchor = row.get("s6_targeting_forward_anchor")
        s6_note = f" | {s6_row_anchor}" if s6_row_anchor else ""
        lines.append(
            f"  S{int(idx) + 1} weight [{row.get('brushstroke_id')}/{row.get('arc_role')}]: "
            f"{row.get('guidance')}{req_note}{s6_note}"
        )
    lines.append(
        "S1 must echo executive_strategy_thesis. You may weave multiple brushstroke facts across S2–S5; "
        "sentence order follows the thesis, not fact-pool or brushstroke index order. "
        "Bind substantive claims to claim_ledger rows; prose is clean — no brushstroke labels in display text. "
        "DISPLAY_LEDGER_PARITY: material dollar/percent outcomes in claim_text for S3–S5 must appear in the "
        "matching resume_display_text sentence (judges grade display, not ledger-only metrics)."
    )
    lines.append("</executive_summary_composition_plan>")
    return "\n".join(lines) + "\n"


def build_executive_summary_composition_plan(
    *,
    selected_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    target_role: str,
    target_company: str,
    proof_pool_metadata: dict[str, Any] | None = None,
    briefing_text: str = "",
    jd_text: str = "",
) -> dict[str, Any]:
    """Deterministic composition plan from the graph proof pool (runtime authority)."""
    from apps_rg.runtime.sections.executive_summary_pa import is_strategy_executive_target_title

    facts = [f for f in selected_facts if isinstance(f, dict)]
    allowed = {_fact_id_base(x) for x in allowed_fact_ids}
    role_s = str(target_role or "").strip()
    company_s = str(target_company or "").strip()
    strategy_executive = is_strategy_executive_target_title(role_s)
    graph_refs = _infer_graph_skill_refs(facts, proof_pool_metadata=proof_pool_metadata)
    brushstroke_bind = bind_facts_to_brushstrokes(
        facts, allowed_fact_ids=allowed_fact_ids, proof_pool_metadata=proof_pool_metadata
    )
    brushstrokes = [
        _brushstroke_for_role(role, facts, allowed, proof_pool_metadata=proof_pool_metadata)
        for role in BRUSHSTROKE_ROLES
    ]
    dominant = "B2_governed_platform_system"
    if graph_refs:
        dominant = "B2_governed_platform_system"
    elif any("governance" in str(f.get("fact_id") or "").lower() for f in facts):
        dominant = "B3_control_evidence_discipline"
    if strategy_executive:
        target_picture = (
            "Executive portrait: technology strategy leader aligning governed AI platforms, "
            "regulatory lineage, and digital innovation programs into one enterprise IT direction "
            f"(targeting context: {role_s or 'SVP IT strategy role'}; company name never in prose)."
        )
    else:
        target_picture = (
            f"Executive portrait: governed agentic AI platform leader "
            f"(targeting: {role_s or 'target role'}; company name never in prose)."
        )
    sentence_arc = build_sentence_arc(target_role=role_s, strategy_executive=strategy_executive)
    arc_meta: dict[str, Any] = {}
    if strategy_executive:
        sentence_arc, arc_meta = enrich_strategy_sentence_arc_bindings(
            sentence_arc,
            allowed_fact_ids=allowed,
            briefing_text=str(briefing_text or ""),
            jd_text=str(jd_text or ""),
            strategy_executive=True,
        )
    return {
        "schema": COMPOSITION_PLAN_SCHEMA,
        "composition_style": COMPOSITION_STYLE,
        "target_picture": target_picture,
        "strategy_executive_arc": strategy_executive,
        "dominant_arc": dominant,
        "dominant_brushstroke_id": dominant,
        "brushstrokes": brushstrokes,
        "sentence_arc": sentence_arc,
        **arc_meta,
        "graph_skill_refs": graph_refs,
        "brushstroke_required_ids": brushstroke_bind["brushstroke_required_ids"],
        "brushstroke_covered_ids": brushstroke_bind["brushstroke_covered_ids"],
        "brushstroke_missing_ids": brushstroke_bind["brushstroke_missing_ids"],
        "brushstroke_fact_bindings": brushstroke_bind["brushstroke_fact_bindings"],
        "legacy_fact_selector_active": False,
        "graph_backed_composition_claimed": bool(graph_refs) or bool(
            proof_pool_metadata and proof_pool_metadata.get("graph_skills_proof_pool")
        ),
    }


def normalize_exec_summary_recruiter_openers(resume_display_text: str) -> str:
    """Deterministic voice repair: replace thin recruiter openers without weakening X2."""
    from apps_rg.runtime.validators.executive_summary_x2 import EXEC_SUMMARY_MECHANICAL_OPENERS
    from apps_rg.runtime.validators.executive_summary_sentence_utils import (
        join_executive_summary_sentences,
        split_sentences,
    )

    text = str(resume_display_text or "").strip()
    if not text:
        return text
    low = text.lower()
    replacements = (
        ("engineering executive with expertise in", "Engineering executive building"),
        ("engineering executive with expertise", "Engineering executive building"),
        ("technology strategy executive with extensive experience in", "Technology strategy executive who operationalizes"),
    )
    for old, new in replacements:
        if low.startswith(old):
            text = new + text[len(old) :]
            low = text.lower()
            break
    rebuilt: list[str] = []
    for sent in split_sentences(text):
        words = sent.split()
        while words and words[0].lower().strip(",.;:") in EXEC_SUMMARY_MECHANICAL_OPENERS:
            words = words[1:]
        if not words:
            continue
        clause = " ".join(words).strip()
        if clause and clause[0].islower():
            clause = clause[0].upper() + clause[1:]
        rebuilt.append(clause)
    if rebuilt:
        return join_executive_summary_sentences(rebuilt)
    return text


def attach_composition_to_parsed(
    parsed: dict[str, Any],
    plan: dict[str, Any],
    *,
    resume_display_text: str,
) -> dict[str, Any]:
    """Merge plan + optional model maps; keep resume_display_text as sole user-visible prose."""
    out = dict(parsed)
    text = str(resume_display_text or out.get("resume_display_text") or out.get("executive_summary_text") or "").strip()
    if text:
        out["resume_display_text"] = text
    out["executive_summary_composition_plan"] = plan
    sentences = split_sentences(text)
    arc_rows = list(plan.get("sentence_arc") or [])
    if not isinstance(out.get("sentence_map"), list) or not out.get("sentence_map"):
        out["sentence_map"] = []
        for i, s in enumerate(sentences):
            arc = arc_rows[i] if i < len(arc_rows) and isinstance(arc_rows[i], dict) else {}
            out["sentence_map"].append(
                {
                    "sentence_index": i,
                    "sentence_text": s,
                    "brushstroke_id": arc.get("brushstroke_id")
                    or BRUSHSTROKE_ROLES[min(i, len(BRUSHSTROKE_ROLES) - 1)],
                    "arc_role": arc.get("arc_role"),
                }
            )
    if not isinstance(out.get("brushstroke_map"), list) or not out.get("brushstroke_map"):
        out["brushstroke_map"] = [
            {
                "brushstroke_id": b["brushstroke_id"],
                "brushstroke_role": b["brushstroke_role"],
                "required_fact_ids": b.get("required_fact_ids") or [],
            }
            for b in plan.get("brushstrokes") or []
        ]
    if not isinstance(out.get("graph_skill_refs"), list) or not out.get("graph_skill_refs"):
        out["graph_skill_refs"] = list(plan.get("graph_skill_refs") or [])
    sc = out.get("self_check")
    if not isinstance(sc, dict):
        sc = {}
    sc.setdefault("composition_style", COMPOSITION_STYLE)
    sc.setdefault("painting_plan_emitted", True)
    out["self_check"] = sc
    return out


def mechanism_term_hits(text: str) -> list[str]:
    low = str(text or "").lower()
    hits: list[str] = []
    for term in MECHANISM_TERMS:
        if term in low:
            hits.append(term)
    return hits


def is_mechanism_inventory_sentence(sentence: str) -> tuple[bool, str | None]:
    """True when mechanism language dominates or reads as a stacked inventory."""
    s = str(sentence or "").strip()
    if not s:
        return False, None
    low = s.lower()
    hits = mechanism_term_hits(s)
    if len(hits) >= 3:
        return True, f"mechanism_inventory:{len(hits)}_terms"
    if re.search(r"\bthrough\b", low) and len(hits) >= 2 and ("," in s or " and " in low):
        return True, "mechanism_list_through_connector"
    if s.count(",") >= 2 and len(hits) >= 2:
        return True, "mechanism_comma_list"
    if re.search(
        r"\b(deterministic\s+routing|multi-agent\s+orchestration|graph-aware\s+retrieval|graphrag)\b.*\b(and|,)\b",
        low,
    ):
        return True, "mechanism_chain_inventory"
    return False, None


def check_s1_dominant_brushstroke_thesis(s1: str) -> tuple[bool, str | None]:
    """Thesis-led S1: light technical qualifiers allowed; inventory/domination fails."""
    s = str(s1 or "").strip()
    if not s:
        return False, "S1 thesis empty"
    if re.search(r"[\d$%]", s):
        return False, "S1 thesis: numeric or $/% tokens forbidden"
    for phrase in ("to improve", "to reduce", "to streamline"):
        if phrase in s.lower():
            return False, f"S1 thesis: outcome-bridge phrase {phrase!r}"
    if re.search(r"\bintegrating\b", s.lower()) and len(mechanism_term_hits(s)) >= 2:
        return False, "S1 thesis: integrating + multiple mechanism terms"
    inv, reason = is_mechanism_inventory_sentence(s)
    if inv:
        return False, f"S1 thesis: {reason}"
    return True, "ok"


def _graph_painting_active(proof_pool_metadata: dict[str, Any] | None) -> bool:
    return isinstance(proof_pool_metadata, dict) and bool(
        proof_pool_metadata.get("graph_skills_proof_pool")
    )


def check_graph_painting_sentence_responsibility_shape(
    resume_display_text: str,
    proof_pool_metadata: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    """Graph-backed painting-plan sentence arc."""
    if not _graph_painting_active(proof_pool_metadata):
        return True, "skipped_not_graph_painting"
    from apps_rg.runtime.validators.executive_summary_x2 import (
        _graph_evidence_credibility_sentence_opener_ok,
        _graph_evidence_lane_no_commercial_org_cred,
        _graph_evidence_outcomes_sentence_opener_ok,
    )

    sentences = [s.strip() for s in split_sentences(resume_display_text) if str(s).strip()]
    n = len(sentences)
    if n != 6:
        return (
            False,
            f"x2_exec_summary_graph_evidence_sentence_responsibility_shape requires exactly 6 sentences; found {n}",
        )
    ok1, r1 = check_s1_dominant_brushstroke_thesis(sentences[0])
    if not ok1:
        return False, r1

    bad2 = _graph_evidence_lane_no_commercial_org_cred(sentences[1], "S2 mechanism-only")
    if bad2:
        return False, bad2
    inv2, r2 = is_mechanism_inventory_sentence(sentences[1])
    if inv2 and r2 in (
        "mechanism_list_through_connector",
        "mechanism_comma_list",
        "mechanism_chain_inventory",
    ):
        return False, f"S2 platform brushstroke: {r2}"

    bad3 = _graph_evidence_lane_no_commercial_org_cred(sentences[2], "S3 lifecycle bridge")
    if bad3:
        return False, bad3

    bad4 = _graph_evidence_lane_no_commercial_org_cred(sentences[3], "S4 theme bridge")
    if bad4:
        return False, bad4
    bad5 = _graph_evidence_outcomes_sentence_opener_ok(sentences[4])
    if bad5:
        return False, bad5
    bad6 = _graph_evidence_credibility_sentence_opener_ok(sentences[5])
    if bad6:
        return False, bad6
    return True, "ok"


def resolve_composition_plan(
    parsed_output: dict[str, Any] | None,
    *,
    artifacts_dir: Any | None = None,
) -> dict[str, Any] | None:
    if isinstance(parsed_output, dict):
        plan = parsed_output.get("executive_summary_composition_plan")
        if isinstance(plan, dict) and plan.get("composition_style") == COMPOSITION_STYLE:
            return plan
    if artifacts_dir is not None:
        from pathlib import Path
        import json

        path = Path(artifacts_dir) / "executive_summary_composition_plan.json"
        if path.is_file():
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):  # guardian: allow-return-none-swallow -- P2 burndown: optional composition plan artifact
                return None
            return doc if isinstance(doc, dict) else None
    return None


def check_composition_plan_present(
    parsed_output: dict[str, Any] | None,
    *,
    artifacts_dir: Any | None,
    proof_pool_metadata: dict[str, Any] | None = None,
) -> tuple[bool, str | None]:
    if not _graph_painting_active(proof_pool_metadata):
        return True, "skipped_not_graph_painting"
    plan = resolve_composition_plan(parsed_output, artifacts_dir=artifacts_dir)
    if not plan:
        return False, "executive_summary_composition_plan.json missing or invalid"
    if plan.get("composition_style") != COMPOSITION_STYLE:
        return False, "composition_style must be executive_painting"
    if not isinstance(plan.get("brushstrokes"), list) or not plan.get("brushstrokes"):
        return False, "brushstrokes[] required"
    return True, "ok"


def check_brushstroke_fact_support(
    plan: dict[str, Any] | None,
    claim_ledger: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> tuple[bool, str | None]:
    if not plan:
        return True, "skipped_no_plan"
    allowed = {_fact_id_base(x) for x in allowed_fact_ids}
    cited: set[str] = set()
    for row in claim_ledger:
        if not isinstance(row, dict):
            continue
        for fid in row.get("source_fact_ids") or []:
            base = _fact_id_base(str(fid))
            if base in allowed:
                cited.add(base)
    for bs in plan.get("brushstrokes") or []:
        if not isinstance(bs, dict):
            continue
        if bs.get("support_status") == "UNSUPPORTED":
            return False, f"brushstroke {bs.get('brushstroke_id')} unsupported"
        if bs.get("support_status") == "SKIPPED":
            continue
        req = [_fact_id_base(str(x)) for x in (bs.get("required_fact_ids") or []) if str(x).strip()]
        if req and not any(r in cited or r in allowed for r in req):
            return False, f"brushstroke {bs.get('brushstroke_id')} has no cited allowed facts"
    return True, "ok"


def check_graph_skill_coverage(
    plan: dict[str, Any] | None,
    parsed_output: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    if not plan or not plan.get("graph_backed_composition_claimed"):
        return True, "skipped_not_graph_claimed"
    refs = list(plan.get("graph_skill_refs") or [])
    model_refs = (parsed_output or {}).get("graph_skill_refs") if isinstance(parsed_output, dict) else None
    if isinstance(model_refs, list) and model_refs:
        return True, "ok"
    if refs:
        return True, "ok"
    return False, "graph_skill_refs absent while graph-backed composition claimed"


def check_dominant_brushstroke_coherence(
    resume_display_text: str,
    plan: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    if not plan:
        return True, "skipped_no_plan"
    sentences = split_sentences(resume_display_text)
    if not sentences:
        return False, "empty resume_display_text"
    ok1, reason = check_s1_dominant_brushstroke_thesis(sentences[0])
    if not ok1:
        return False, reason
    dom = str(plan.get("dominant_brushstroke_id") or plan.get("dominant_arc") or "")
    if dom and dom.startswith("B1") and len(mechanism_term_hits(sentences[0])) >= 2:
        return False, "dominant arc B1 but S1 carries multiple mechanism terms"
    return True, "ok"


def check_mechanism_inventory_control(resume_display_text: str) -> tuple[bool, str | None]:
    """Fail stacked mechanism catalogs; allow rich B2/B3 platform/control brushstroke sentences."""
    hard_inventory_reasons = frozenset(
        {
            "mechanism_list_through_connector",
            "mechanism_comma_list",
            "mechanism_chain_inventory",
        }
    )
    for i, sent in enumerate(split_sentences(resume_display_text)):
        inv, reason = is_mechanism_inventory_sentence(sent)
        if not inv:
            continue
        if i in (1, 2) and reason and reason.split(":", 1)[0] not in hard_inventory_reasons:
            if reason.startswith("mechanism_inventory:"):
                continue
        return False, f"sentence {i}: {reason}"
    return True, "ok"


def check_human_exec_voice(resume_display_text: str) -> tuple[bool, str | None]:
    low = resume_display_text.lower().strip()
    for opener in EXEC_VOICE_BAD_OPENERS:
        if low.startswith(opener):
            return False, f"generic_exec_opener:{opener}"
    for hype in GENERIC_AI_HYPE:
        if hype in low:
            return False, f"generic_ai_hype:{hype}"
    return True, "ok"


def check_no_jd_keyword_stuffing_exec(resume_display_text: str, jd_text: str) -> tuple[bool, str | None]:
    from apps_rg.runtime.validators.executive_summary_x2 import has_jd_phrase_copy

    copied, phrase = has_jd_phrase_copy(resume_display_text, jd_text)
    if copied:
        return False, f"jd_phrase_copy:{phrase}"
    jd_low = jd_text.lower()
    if len(jd_low) < 40:
        return True, "ok"
    words = [w for w in re.findall(r"[a-z]{5,}", jd_low) if w not in ("brown", "senior", "vice", "president")]
    hits = [w for w in words[:30] if resume_display_text.lower().count(w) >= 3]
    if len(hits) >= 4:
        return False, f"jd_keyword_stuffing:{','.join(hits[:6])}"
    return True, "ok"
