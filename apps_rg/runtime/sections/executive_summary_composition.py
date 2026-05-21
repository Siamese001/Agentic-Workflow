"""Graph-backed executive summary composition plan (painting-plan enforcement)."""

from __future__ import annotations

import re
from typing import Any

from apps_rg.runtime.validators.executive_summary_x2 import split_sentences

COMPOSITION_STYLE = "executive_painting"
COMPOSITION_PLAN_SCHEMA = "executive_summary_composition_plan_v1"

BRUSHSTROKE_ROLES = (
    "B1_executive_identity",
    "B2_governed_platform_system",
    "B3_control_evidence_discipline",
    "B4_business_role_fit",
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


def _classify_fact_brushstroke_role(fact_id: str, claim_text: str) -> str:
    fid = _fact_id_base(fact_id).lower()
    low = claim_text.lower()
    if any(x in fid for x in ("exec", "leadership")) or "organization" in low and "ml engineering" in low:
        return "B1_executive_identity"
    if any(x in fid for x in ("governance", "regulatory", "risk", "ccar", "basel", "lineage", "validation")):
        return "B3_control_evidence_discipline"
    if any(x in fid for x in ("revenue", "sales", "commercial", "margin", "ops")):
        return "B4_business_role_fit"
    if any(x in fid for x in ("cert", "quant", "hpc", "actuarial")):
        return "B4_business_role_fit"
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


def _infer_graph_skill_refs(
    selected_facts: list[dict[str, Any]],
    *,
    proof_pool_metadata: dict[str, Any] | None,
) -> list[str]:
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


def _brushstroke_for_role(role: str, facts: list[dict[str, Any]], allowed: set[str]) -> dict[str, Any]:
    role_facts = [
        f
        for f in facts
        if isinstance(f, dict) and _classify_fact_brushstroke_role(str(f.get("fact_id") or ""), str(f.get("claim_text") or "")) == role
    ]
    if not role_facts and role == "B1_executive_identity" and facts:
        role_facts = [facts[0]]
    req_ids = sorted(
        {
            _fact_id_base(str(f.get("fact_id") or ""))
            for f in role_facts
            if _fact_id_base(str(f.get("fact_id") or "")) in allowed
        }
    )
    skill_refs = _infer_graph_skill_refs(role_facts, proof_pool_metadata=None)
    image_goals = {
        "B1_executive_identity": "Establish SVP Engineering identity and regulated enterprise platform scope.",
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


def build_executive_summary_composition_plan(
    *,
    selected_facts: list[dict[str, Any]],
    allowed_fact_ids: set[str],
    target_role: str,
    target_company: str,
    proof_pool_metadata: dict[str, Any] | None = None,
    srfs_integration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic composition plan from SRFS/graph proof pool (runtime authority)."""
    facts = [f for f in selected_facts if isinstance(f, dict)]
    allowed = {_fact_id_base(x) for x in allowed_fact_ids}
    graph_refs = _infer_graph_skill_refs(facts, proof_pool_metadata=proof_pool_metadata)
    brushstrokes = [_brushstroke_for_role(role, facts, allowed) for role in BRUSHSTROKE_ROLES]
    dominant = "B2_governed_platform_system"
    if graph_refs:
        dominant = "B2_governed_platform_system"
    elif any("governance" in str(f.get("fact_id") or "").lower() for f in facts):
        dominant = "B3_control_evidence_discipline"
    return {
        "schema": COMPOSITION_PLAN_SCHEMA,
        "composition_style": COMPOSITION_STYLE,
        "target_picture": (
            f"Executive portrait of Amit as an SVP Engineering leader for governed agentic AI platforms "
            f"aligned to {target_role.strip() or 'the target role'} at {target_company.strip() or 'the target company'}."
        ),
        "dominant_arc": dominant,
        "dominant_brushstroke_id": dominant,
        "brushstrokes": brushstrokes,
        "graph_skill_refs": graph_refs,
        "srfs_active": bool(srfs_integration and str(srfs_integration.get("artifact_path_resolved") or "").strip()),
        "graph_backed_composition_claimed": bool(graph_refs) or bool(
            proof_pool_metadata and proof_pool_metadata.get("graph_skills_proof_pool")
        ),
    }


def normalize_exec_summary_recruiter_openers(resume_display_text: str) -> str:
    """Deterministic voice repair: replace thin recruiter openers without weakening X2."""
    text = str(resume_display_text or "").strip()
    if not text:
        return text
    low = text.lower()
    replacements = (
        ("engineering executive with expertise in", "Engineering executive building"),
        ("engineering executive with expertise", "Engineering executive building"),
    )
    for old, new in replacements:
        if low.startswith(old):
            return new + text[len(old) :]
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
    if not isinstance(out.get("sentence_map"), list) or not out.get("sentence_map"):
        out["sentence_map"] = [
            {
                "sentence_index": i,
                "sentence_text": s,
                "brushstroke_id": BRUSHSTROKE_ROLES[min(i, len(BRUSHSTROKE_ROLES) - 1)],
            }
            for i, s in enumerate(sentences)
        ]
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


def check_srfs_sentence_responsibility_shape_painting(
    resume_display_text: str,
    srfs_integration: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    """SRFS arc with painting-plan S1 (replaces rigid S1 mechanism-term ban)."""
    if not srfs_integration or not str(srfs_integration.get("artifact_path_resolved") or "").strip():
        return True, "skipped_no_selected_role_fact_set"
    from apps_rg.runtime.validators.executive_summary_x2 import (
        _srfs_credibility_sentence_opener_ok,
        _srfs_lane_no_commercial_org_cred,
        _srfs_outcomes_sentence_opener_ok,
    )

    sentences = [s.strip() for s in split_sentences(resume_display_text) if str(s).strip()]
    n = len(sentences)
    if n not in (4, 5):
        return (
            False,
            f"x2_exec_summary_srfs_sentence_responsibility_shape requires 4 or 5 sentences; found {n}",
        )
    ok1, r1 = check_s1_dominant_brushstroke_thesis(sentences[0])
    if not ok1:
        return False, r1

    bad2 = _srfs_lane_no_commercial_org_cred(sentences[1], "S2 mechanism-only")
    if bad2:
        return False, bad2
    inv2, r2 = is_mechanism_inventory_sentence(sentences[1])
    if inv2 and r2 in (
        "mechanism_list_through_connector",
        "mechanism_comma_list",
        "mechanism_chain_inventory",
    ):
        return False, f"S2 platform brushstroke: {r2}"

    bad3 = _srfs_lane_no_commercial_org_cred(sentences[2], "S3 lifecycle bridge")
    if bad3:
        return False, bad3

    if n == 5:
        bad4 = _srfs_outcomes_sentence_opener_ok(sentences[3])
        if bad4:
            return False, bad4
        bad5 = _srfs_credibility_sentence_opener_ok(sentences[4])
        if bad5:
            return False, bad5
    else:
        bad4 = _srfs_outcomes_sentence_opener_ok(sentences[3])
        if bad4:
            return False, bad4
        tl = sentences[3].strip().lower()
        if tl.startswith("holds certifications") or tl.startswith("credentials"):
            return False, "S4 combined must not start with Holds certifications or Credentials"
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
            except (OSError, json.JSONDecodeError):  # guardian: allow-return-none-swallow
                return None
            return doc if isinstance(doc, dict) else None
    return None


def check_composition_plan_present(
    parsed_output: dict[str, Any] | None,
    *,
    artifacts_dir: Any | None,
    srfs_integration: dict[str, Any] | None,
) -> tuple[bool, str | None]:
    if not srfs_integration or not str(srfs_integration.get("artifact_path_resolved") or "").strip():
        return True, "skipped_no_srfs"
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
