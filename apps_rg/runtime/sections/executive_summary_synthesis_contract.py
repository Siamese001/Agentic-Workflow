"""SSOT: SVP executive-summary synthesis arc (U0 targeting → L2 prompt → pre-X2 regen → judge remediation → L6 shadow).

JD/briefing themes are targeting-only (never proof). All prose claims remain bound to ALLOWED_SOURCE_FACT_IDS.
"""

from __future__ import annotations

from typing import Any

# Targeting emphasis themes (JD shapes ranking only — jd_used_as_proof=false).
QUANT_METRIC_DISPLAY_FACT_ID = "fact_quant_hpc_001"
FSA_CREDENTIAL_FACT_ID = "fact_quant_hpc_003"

# Approved S2–S5 transitions (max two stock bridges per paragraph — see I0).
APPROVED_NON_STOCK_OPENERS: tuple[str, ...] = (
    "From that commercial base,",
    "Against that lineage backdrop,",
    "In parallel,",
    "That operating foundation also",
    "The same platform discipline",
)

EXEC_SUMMARY_STOCK_BRIDGE_PREFIXES: tuple[str, ...] = (
    "from that",
    "against that",
    "complementing that",
    "building on that",
    "through that",
    "with that governance",
)

# C0 display override for framing-sensitive facts whose claim_text contains
# phrases that trigger X2 display gates (e.g. derivatives inventory in S5).
# Applied by format_selected_facts_for_c0 unconditionally — before claim_text
# and before the evidence capsule path — to guarantee the forbidden phrase never
# reaches the LLM prompt. Keyed by fact_id.
FACT_C0_DISPLAY_OVERRIDES: dict[str, str] = {
    FSA_CREDENTIAL_FACT_ID: (
        "FSA-chartered quantitative foundation, built through early-career "
        "capital modeling and portfolio stress analytics."
    ),
}

SVP_JD_EMPHASIS_THEMES: tuple[str, ...] = (
    "enterprise architecture governance",
    "innovation programs and incubation",
    "multi-year IT strategy and roadmap",
    "federated / post-merger integration",
    "AI and data platform commercialization",
)

SENTENCE_ARC_SVP_STRATEGY: tuple[dict[str, str], ...] = (
    {
        "brushstroke_id": "B1_executive_identity",
        "arc_role": "strategy_thesis",
        "guidance": (
            "Technology strategy / enterprise technology executive thesis; avoid narrow engineering-manager label; "
            "frame enterprise IT direction + innovation-program posture for decentralized regulated enterprises "
            "(targeting vocabulary — not JD-as-proof); avoid generic 'regulated enterprise scale' filler."
        ),
    },
    {
        "brushstroke_id": "B2_governed_platform_system",
        "arc_role": "platform_arc",
        "guidance": (
            "Connect governed AI platform and runtime architecture to enterprise IT direction; "
            "one causal clause, max two mechanism terms verbatim from facts."
        ),
    },
    {
        "brushstroke_id": "B2_governed_platform_system",
        "arc_role": "scale_operating_model",
        "guidance": (
            "S3: weave platform scale, operating model, and commercialization as connective prose — when "
            "fact_engineering_platform_006 is cited, include $22M IP-led revenue and/or 20% margin expansion in display "
            "(team 8→28 may share the clause); not a standalone achievement bullet; "
            "avoid SRFS-forbidden phrases (reusable platform services adopted across enterprise programs, engineering scale-out)."
        ),
    },
    {
        "brushstroke_id": "B3_control_evidence_discipline",
        "arc_role": "governance_innovation",
        "guidance": (
            "S4: governance, lineage, or regulatory discipline linked to IT strategy velocity — when fact_governance_003 "
            "is cited, surface the allowed reporting-error reduction percent in display; not a control checklist; "
            "use parallel thematic sequencing when lineage and HPC facts are separate threads (no forced 'extended to' bridges)."
        ),
    },
    {
        "brushstroke_id": "B4_business_role_fit",
        "arc_role": "commercial_strategy",
        "guidance": (
            "S5: one strategic clause pairing FSA/quant foundation (fact_quant_hpc_003) with the allowed "
            "stress-testing or HPC outcome percent from fact_quant_hpc_001 in display — cite both source_fact_ids "
            "in the claim_ledger row; never list derivatives pricing, multi-Greek hedging, employer names, or cert-label stacks."
        ),
    },
    {
        "brushstroke_id": "B4_business_role_fit",
        "arc_role": "enterprise_capstone",
        "guidance": (
            "S6: forward capstone grounded in the sentence's source_fact_ids (e.g. fact_quant_hpc_003 quant foundation); "
            "may echo composition_plan s6_targeting_forward_anchor for decentralized units / innovation mandate "
            "(targeting-only — jd_used_as_proof=false); must add a NEW forward idea (not 'extend that arc toward' recap); "
            "no TARGET_COMPANY, no repetition of S2–S5 noun phrases; do not open with 'Looking ahead,'."
        ),
    },
)


def format_s6_briefing_forward_targeting_anchor(
    *,
    briefing_text: str = "",
    jd_text: str = "",
) -> str:
    """Targeting-only S6 forward themes from JD/briefing (never proof)."""
    blob = f"{briefing_text} {jd_text}".lower()
    themes: list[str] = []
    if any(tok in blob for tok in ("decentral", "autonomous unit", "federated", "operating unit")):
        themes.append("decentralized operating units")
    if "innovation" in blob:
        themes.append("innovation incubation and architecture standards")
    if "enterprise architecture" in blob or " ea " in f" {blob} ":
        themes.append("enterprise architecture governance")
    if "multi-year" in blob or "roadmap" in blob:
        themes.append("multi-year IT strategy roadmap")
    if not themes:
        themes.append("enterprise IT direction and innovation-program posture")
    joined = "; ".join(themes)
    return (
        f"TARGETING_FORWARD_ANCHOR (targeting only — jd_used_as_proof=false): {joined}."
    )


def format_svp_jd_emphasis_line() -> str:
    themes = "; ".join(SVP_JD_EMPHASIS_THEMES)
    return (
        f"- JD/briefing may tilt emphasis among evidenced themes only ({themes}) — never cite JD as proof.\n"
    )


_INTEROP_PROOF_MARKERS = (
    "interop",
    "federated",
    "accession",
    "brokerage",
    "enterprise_architecture",
    "ea_",
)

_UNSUPPORTED_INDUSTRY_REGEN_PHRASES = (
    "insurance brokerage",
    "insurance-sector",
    "insurance sector",
    "federated insurance",
    "insurance operations",
    "insurance-brokerage",
)


def has_svp_targeting_proof_gap(*, allowed_fact_ids: set[str] | frozenset[str]) -> bool:
    """True when allowlist lacks EA/interop/federated proof IDs (Brown SVP lane)."""
    allowed = {str(x).lower() for x in allowed_fact_ids}
    has_interop_proof = any(any(m in fid for m in _INTEROP_PROOF_MARKERS) for fid in allowed)
    return not has_interop_proof


def format_judge_regen_proof_boundary_guard() -> str:
    """Regen-turn guard when TARGETING_GAP is active — blocks X2 industry-claim failures."""
    return (
        "PROOF_BOUNDARY_REGEN: JD/briefing are targeting-only (jd_used_as_proof=false). "
        "Do NOT introduce insurance brokerage, insurance operations, federated insurance, or other "
        "industry-sector nouns in resume_display_text unless an ALLOWED_SOURCE_FACT_ID claim_text "
        "explicitly supports that domain."
    )


def format_judge_regen_proof_gap_reframe_line() -> str:
    """Replacement guidance when verbatim judge feedback asks for unsupported industry framing."""
    return (
        "- PROOF_GAP_REFRAME: Sharpen S1/S6 with targeting vocabulary only (decentralized operating units, "
        "federated operating-model posture, innovation-program mandate) — never add insurance-sector "
        "nouns unless ALLOWED_SOURCE_FACT_IDS support them."
    )


def filter_judge_remediation_feedback_for_proof_gap(
    lines: list[str],
    *,
    allowed_fact_ids: set[str] | frozenset[str],
) -> tuple[list[str], dict[str, Any]]:
    """Drop/reframe judge delta lines that instruct unsupported industry claims."""
    if not has_svp_targeting_proof_gap(allowed_fact_ids=allowed_fact_ids):
        return list(lines), {"proof_gap_filter": "inactive", "dropped_count": 0}

    kept: list[str] = []
    dropped: list[str] = []
    for line in lines:
        low = str(line).lower()
        if any(phrase in low for phrase in _UNSUPPORTED_INDUSTRY_REGEN_PHRASES):
            dropped.append(line)
            continue
        if "insurance" in low and any(
            tok in low
            for tok in (
                "brokerage context",
                "insurance-sector",
                "insurance sector",
                "federated insurance",
                "insurance operations",
            )
        ):
            dropped.append(line)
            continue
        kept.append(line)

    meta: dict[str, Any] = {
        "proof_gap_filter": "active",
        "dropped_count": len(dropped),
        "dropped_preview": [d[:120] for d in dropped[:4]],
    }
    if dropped:
        reframe = format_judge_regen_proof_gap_reframe_line()
        if reframe not in kept:
            kept.insert(0, reframe)
        meta["reframe_inserted"] = True
    return kept, meta


def format_strategy_targeting_gap_note(*, allowed_fact_ids: set[str] | frozenset[str]) -> str:
    """When JD themes lack proof IDs, require gap_notes + concept translation (not JD-as-proof)."""
    allowed = {str(x).lower() for x in allowed_fact_ids}
    has_interop_proof = any(any(m in fid for m in _INTEROP_PROOF_MARKERS) for fid in allowed)
    concept_block = (
        "TARGETING_CONCEPT_MAP (targeting only — NOT PROOF):\n"
        "- Translate allowed platform/governance/commercial/regulated-delivery facts into executive concepts: "
        "enterprise IT strategy, architecture modernization, innovation incubation, lineage-ready operating models, "
        "and regulated enterprise scale — without claiming insurance brokerage, federated M&A integration, or "
        "interoperability product experience unless matching ALLOWED_SOURCE_FACT_IDs exist.\n"
        "- Do not keyword-stuff JD phrases; use causal synthesis so an SVP IT Strategy reader sees strategic fit.\n"
    )
    if has_interop_proof:
        return concept_block
    return (
        concept_block
        + "TARGETING_GAP: No EA/interop/federated proof IDs in allowlist — set "
        "gap_notes.svp_targeting_theme_gap_explained=true; emphasize platform/governance/commercial facts only "
        "(jd_used_as_proof=false).\n"
    )


def format_strategy_executive_u0_block(*, target_title: str = "") -> str:
    """U0 targeting appendix for SVP IT strategy / innovation lanes (injected at PA compile)."""
    role = (target_title or "SVP IT strategy").strip()
    return (
        "STRATEGY_EXECUTIVE_SYNTHESIS (targeting only — NOT PROOF):\n"
        "- Required JSON field `executive_strategy_thesis` before `resume_display_text` (one ledger-backed sentence).\n"
        "- Open display S1 as technology strategy / enterprise technology executive (not narrow AI-platform builder only); "
        "avoid generic 'aligns enterprise IT direction' openers — use architecture-governance + innovation-program posture.\n"
        "- At most two S2–S5 sentences may use stock bridges (Building on / Through that / Complementing / With that governance); "
        "vary other transitions (From that commercial base / Against that lineage backdrop / In parallel).\n"
        "- Six sentences = one causal arc serving the thesis; **do not** assign one accomplishment per sentence by default.\n"
        "- S3–S5: connective prose with material dollar/percent outcomes in display when allowed facts carry them "
        "(judges read resume_display_text, not claim_text alone).\n"
        "- S5: when fact_quant_hpc_003 (FSA/quant foundation) and fact_quant_hpc_001 are cited together, weave the "
        "allowed stress-testing/HPC outcome percent into display (not ledger-only); forbidden: derivatives / "
        "multi-Greek / employer inventory lists.\n"
        "- S6: forward capstone grounded in source_fact_ids; may use composition_plan s6_targeting_forward_anchor "
        "(briefing/JD emphasis only); forbidden: 'Looking ahead,' opener, 'extend that arc toward' recap.\n"
        "- S3–S4: honest connectors only; parallel governance and HPC threads need not be falsely causal.\n"
        f"{format_svp_jd_emphasis_line()}"
        f"- Target role framing: {role} (positioning only).\n"
        "- NEVER name TARGET_COMPANY in resume_display_text.\n"
        "- Weave team-scale facts (e.g. 8-to-28 engineering growth) into S2–S4 when in ALLOWED_SOURCE_FACT_IDS.\n"
    )


def format_synthesis_repair_directive(*, strategy_executive: bool) -> str:
    """Pre-X2 same-authority regen addendum (L2 repair path)."""
    if not strategy_executive:
        return ""
    return (
        "SVP_SYNTHESIS_ARC: S3–S4 connect platform scale, innovation delivery, and operating model in causal prose; "
        "S5 — one metric woven into strategy (no metric stack, no credential dump); "
        "S6 — integrative enterprise IT direction capstone (not a recap list). "
        "Shape JD emphasis toward enterprise architecture, innovation programs, and multi-year IT strategy "
        "using allowed facts only (jd_used_as_proof=false). "
    )


def format_judge_regen_mechanical_opener_guard() -> str:
    """X2 mechanical-opener stack guard for judge regen (max 2 sentences with bullet-style openers)."""
    from apps_rg.runtime.validators.executive_summary_x2 import EXEC_SUMMARY_MECHANICAL_OPENERS

    openers = ", ".join(EXEC_SUMMARY_MECHANICAL_OPENERS)
    return (
        f"MECHANICAL_OPENER_GUARD: at most 2 sentences may start with ({openers}); "
        "vary sentence openers for executive synthesis (not a resume bullet chain).\n"
    )


def format_judge_regen_soft_material_preservation(
    *,
    prior_word_count: int,
    prior_ledger_rows: int,
) -> str:
    """Soft regen guidance — no hard word-count floor (W2.3)."""
    return (
        "MATERIAL_PRESERVATION (soft — not a word-count floor; hard X2 gates still apply):\n"
        "- Preserve material claims and ledger-backed support unless removal is required to satisfy "
        "X2 or judge feedback.\n"
        "- Stay within the SSOT max word cap and exactly-six-sentence X2 gate; do not pad or bloat "
        "to match prior length.\n"
        f"- Prior draft reference only: ~{max(0, prior_word_count)} words, "
        f"{max(0, prior_ledger_rows)} claim_ledger rows (no minimum word count).\n"
        "- Weave unused allowed facts into prose and claim_ledger when evidence_utilization failed; "
        "do not drop cited source_fact_ids without cause.\n"
        "- Exactly 6 sentences in resume_display_text; claim_ledger row minimums enforced by X2.\n"
    )


def format_judge_regen_x2_floor(*, prior_word_count: int, prior_ledger_rows: int) -> str:
    """Backward-compatible alias — delegates to soft material preservation (no word minimum)."""
    return format_judge_regen_soft_material_preservation(
        prior_word_count=prior_word_count,
        prior_ledger_rows=prior_ledger_rows,
    )


def failed_x2_gate_ids(failed_gates: list[dict[str, Any]]) -> frozenset[str]:
    """Gate IDs that failed in an X2 gate row list."""
    out: set[str] = set()
    for row in failed_gates:
        if not isinstance(row, dict) or row.get("pass"):
            continue
        gid = str(row.get("gate_id") or "").strip()
        if gid.startswith("x2_"):
            out.add(gid)
    return frozenset(out)


def gate_ids_from_x2_reject_reason(reject_reason: str) -> frozenset[str]:
    """Parse ``gate_id: detail`` segments from ``format_x2_gate_failures_reject_reason`` output."""
    out: set[str] = set()
    for part in str(reject_reason or "").split(";"):
        chunk = part.strip()
        if not chunk or ":" not in chunk:
            continue
        gid = chunk.split(":", 1)[0].strip()
        if gid.startswith("x2_"):
            out.add(gid)
    return frozenset(out)


def format_x2_gate_failures_reject_reason(failed_gates: list[dict[str, Any]]) -> str:
    """Map post-regen X2 gate rows into synthesis-repair reject_reason vocabulary."""
    parts: list[str] = []
    for row in failed_gates:
        if not isinstance(row, dict) or row.get("pass"):
            continue
        gid = str(row.get("gate_id") or "x2_gate")
        reason = str(row.get("reason") or row.get("message") or "fail")
        parts.append(f"{gid}: {reason}")
    return "; ".join(parts) if parts else "x2_regen_failed"


def format_judge_remediation_synthesis_default() -> str:
    """Default synthesis line when judge feedback is sparse (post-X1D regen)."""
    return (
        "improve integrated SVP narrative: S2–S5 must use connective tissue (each sentence "
        "references the prior theme — not six standalone achievement bullets); "
        "S3–S4 weave platform scale, operating model, and innovation delivery; "
        "S5 single woven metric clause inside strategy context (no credential/employer dump); "
        "S6 integrative enterprise IT direction capstone from allowed facts only (no vendor cert laundry list; "
        "optional single FSA rigor clause only when fact_quant_hpc supports it); "
        "tilt emphasis toward enterprise architecture, federated integration, innovation incubation, "
        "multi-year IT strategy from JD (targeting only; jd_used_as_proof=false)"
    )


def format_judge_regen_connective_tissue_guard() -> str:
    """Require causal links between sentences for certification-grade synthesis."""
    return (
        "CONNECTIVE_TISSUE: S2 must bridge from S1 thesis (e.g. 'This platform foundation…', "
        "'Building on that direction…'); S3–S5 each open with a causal link to the prior sentence, "
        "not a bare Led/Built/Implemented/Re-architected resume bullet. "
        "Avoid one-fact-per-sentence inventory; read as one executive paragraph.\n"
    )


def format_l6_judge_soft_fail_recommendation(*, soft_judges: list[str]) -> str:
    judges = ", ".join(soft_judges) if soft_judges else "soft-fail judge"
    return (
        f"Executive summary judge soft-fail ({judges}): regenerate with SVP synthesis contract — "
        "connective S3–S4 (platform + innovation + operating model), ≤1 metric in S5, "
        "integrative S6 capstone; JD themes for emphasis only (enterprise architecture, innovation, IT strategy); "
        "enable APPS_RG_EXEC_SUMMARY_JUDGE_REGEN=1 when X2 is green and one judge fails on synthesis."
    )


__all__ = [
    "FSA_CREDENTIAL_FACT_ID",
    "QUANT_METRIC_DISPLAY_FACT_ID",
    "SENTENCE_ARC_SVP_STRATEGY",
    "SVP_JD_EMPHASIS_THEMES",
    "format_s6_briefing_forward_targeting_anchor",
    "failed_x2_gate_ids",
    "gate_ids_from_x2_reject_reason",
    "format_judge_regen_x2_floor",
    "format_x2_gate_failures_reject_reason",
    "format_judge_regen_connective_tissue_guard",
    "format_judge_remediation_synthesis_default",
    "format_l6_judge_soft_fail_recommendation",
    "format_strategy_executive_u0_block",
    "format_synthesis_repair_directive",
    "format_svp_jd_emphasis_line",
]
