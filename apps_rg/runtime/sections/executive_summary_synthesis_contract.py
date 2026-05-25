"""SSOT: SVP executive-summary synthesis arc (U0 targeting → L2 prompt → pre-X2 regen → judge remediation → L6 shadow).

JD/briefing themes are targeting-only (never proof). All prose claims remain bound to ALLOWED_SOURCE_FACT_IDS.
"""

from __future__ import annotations

from typing import Any

# Targeting emphasis themes (JD shapes ranking only — jd_used_as_proof=false).
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
            "frame enterprise IT direction (not a mechanism or metric list)."
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
            "S3: weave platform scale, operating model, and innovation delivery as connective prose "
            "(team growth, lifecycle, federated architecture) — not a standalone achievement bullet."
        ),
    },
    {
        "brushstroke_id": "B3_control_evidence_discipline",
        "arc_role": "governance_innovation",
        "guidance": (
            "S4: governance, lineage, or regulatory discipline linked to IT strategy and innovation velocity "
            "(targeting may emphasize EA governance / audit-ready delivery) — not a control checklist."
        ),
    },
    {
        "brushstroke_id": "B4_business_role_fit",
        "arc_role": "commercial_strategy",
        "guidance": (
            "S5: at most one high-signal metric clause woven into strategy context; "
            "no metric-inventory stack, no Towers Perrin/ING/Aetna credential dump; no AWS/Databricks cert labels "
            "(one FSA rigor weave allowed when fact-backed)."
        ),
    },
    {
        "brushstroke_id": "B4_business_role_fit",
        "arc_role": "enterprise_capstone",
        "guidance": (
            "S6: integrative capstone — how platform + governance + commercialization + innovation posture "
            "form one enterprise technology direction; forward-looking synthesis from allowed facts only; "
            "no JD/briefing echo, no TARGET_COMPANY, no thin recap of S3–S5."
        ),
    },
)


def format_svp_jd_emphasis_line() -> str:
    themes = "; ".join(SVP_JD_EMPHASIS_THEMES)
    return (
        f"- JD/briefing may tilt emphasis among evidenced themes only ({themes}) — never cite JD as proof.\n"
    )


def format_strategy_targeting_gap_note(*, allowed_fact_ids: set[str] | frozenset[str]) -> str:
    """When JD themes lack proof IDs, require gap_notes instead of JD-as-proof."""
    allowed = {str(x).lower() for x in allowed_fact_ids}
    interop_proof_markers = (
        "interop",
        "federated",
        "accession",
        "brokerage",
        "enterprise_architecture",
        "ea_",
    )
    if any(any(m in fid for m in interop_proof_markers) for fid in allowed):
        return ""
    return (
        "TARGETING_GAP (targeting only): JD/briefing may emphasize EA, interoperability, or "
        "federated/post-merger integration — if no matching ALLOWED_SOURCE_FACT_ID exists, set "
        "gap_notes.svp_targeting_theme_gap_explained=true and shape emphasis from platform/governance "
        "facts only (jd_used_as_proof=false).\n"
    )


def format_strategy_executive_u0_block(*, target_title: str = "") -> str:
    """U0 targeting appendix for SVP IT strategy / innovation lanes (injected at PA compile)."""
    role = (target_title or "SVP IT strategy").strip()
    return (
        "STRATEGY_EXECUTIVE_SYNTHESIS (targeting only — NOT PROOF):\n"
        "- Open as technology strategy / enterprise technology executive (not narrow engineering-manager).\n"
        "- Six sentences = one causal arc: thesis → platform → scale/innovation → governance → commercial (≤1 metric clause) → integrative capstone.\n"
        "- S3–S4: connective prose across platform scale, operating model, and innovation delivery — not sequential mini-bullets.\n"
        "- S5: weave quantitative outcomes into strategy context; never a cert/credential/employer-history inventory.\n"
        "- S6: forward-looking enterprise technology direction synthesized from allowed platform/governance/commercial facts.\n"
        f"{format_svp_jd_emphasis_line()}"
        f"- Target role framing: {role} (positioning only).\n"
        "- NEVER name TARGET_COMPANY in resume_display_text.\n"
        "- Weave team-scale facts (e.g. 8-to-28 engineering growth) into narrative when in ALLOWED_SOURCE_FACT_IDS.\n"
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


def format_judge_regen_x2_floor(*, prior_word_count: int, prior_ledger_rows: int) -> str:
    """Non-negotiable X2 floor when rewriting for judges (prevents thin/dropped-ledger regressions)."""
    return (
        "X2_FLOOR (judge feedback must NOT violate — certification rewrite stays rules-valid):\n"
        f"- Maintain or increase resume word count vs prior draft ({prior_word_count} words minimum).\n"
        f"- Maintain or increase claim_ledger rows vs prior ({prior_ledger_rows} minimum); "
        "add OBJECT rows with distinct source_fact_ids for each major sentence.\n"
        "- Exactly 6 sentences, max 140 words; when fact pool is large, each sentence must stay substantive "
        "(no thin one-clause sentences to sound 'executive').\n"
        "- Weave unused allowed facts into prose and ledger — do not drop evidence to simplify narrative.\n"
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
    "SENTENCE_ARC_SVP_STRATEGY",
    "SVP_JD_EMPHASIS_THEMES",
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
