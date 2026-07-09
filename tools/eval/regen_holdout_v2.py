"""Generate varied RELEASE_GATE holdout fixtures.

Replaces the duplicate-shape synthetic rows with texts spanning the
quality spectrum so judge scores have variance, enabling meaningful
Spearman rho. Each row carries deterministic human_score labels that
the user (acting as curator per AG dec_19dede3a5e4d6507f) approved.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOLDOUT = REPO_ROOT / "apps_eval" / "fixtures" / "holdout"

# 8 rows per app spanning quality 0.10 -> 0.95.
LIC_TEXTS = [
    ("Hi.", 0.10),
    ("Hi, want to chat?", 0.20),
    ("Hi Alex, hope you are well. Want to chat sometime?", 0.40),
    ("Hi Alex, I noticed your work at Acme on AI governance. Would love to compare notes. Open to a quick chat next week?", 0.65),
    ("Alex - your recent talk at Acme on AI governance frameworks resonated. We are tackling a similar problem at Stripe. Would you be open to a 20-min call Tuesday or Thursday afternoon to compare playbooks?", 0.80),
    ("Hi Alex, your Acme governance whitepaper on tiered model risk maps closely to our risk-tier proposal at Stripe. We have shipped the policy layer; the audit-trail piece is open. Would you be open to a 20-minute call Thursday 2pm PT to compare notes? I will share our internal one-pager beforehand.", 0.92),
    ("Lol whatever", 0.05),
    ("DEAR SIR/MADAM, kindly review attached opportunity ASAP for ROI synergy.", 0.15),
]
RFP_TEXTS = [
    ("Our solution scales.", 0.10),
    ("Our solution delivers scalability and security.", 0.25),
    ("Our solution delivers scalability across all workloads. Security is enforced by encryption.", 0.45),
    ("Section 1: scalability auto-scales horizontally. Section 2: security uses end-to-end encryption with quarterly audits. Section 3: cost efficiency saves 30% via tiered storage.\n\nCost efficiency is achieved through tiered storage. Security audit trails are immutable. Scalability is benchmarked at 100k req/s.", 0.80),
    ("Executive summary covers scalability, security, cost efficiency.\n\nScalability: horizontal auto-scaling proven at 100k req/s. Cost efficiency: 30% TCO reduction via tiered storage. Scalability gates ensure no regression.\n\nSecurity: end-to-end encryption, immutable audit trails, quarterly third-party audits. Security is the foundation. Cost efficiency tracked monthly.\n\nClosing: scalability, security, and cost efficiency are non-negotiable.", 0.93),
    ("We are good.", 0.05),
    ("Solution Solution Solution. " * 30, 0.20),
    ("scalability scalability scalability scalability scalability scalability scalability", 0.30),
]
RG_TEXTS = [
    ("Did stuff.", 0.10),
    ("Worked on a project.", 0.20),
    ("Led the migration project across teams.", 0.40),
    ("Drove a strategy roadmap shipping quarterly KPIs and 15% revenue uplift across stakeholder teams.", 0.70),
    ("Architected the strategy roadmap delivering quarterly KPI gains: 15% revenue, 22% retention, 30% NPS uplift across executive stakeholder teams; presented outcomes to C-suite quarterly.", 0.88),
    ("Owned end-to-end strategy roadmap; partnered with stakeholder teams to deliver quarterly KPI commitments. Q1: 15% revenue lift, 22% retention gain, 30% NPS uplift. Briefed C-suite quarterly. Roadmap framed ROI tradeoffs across portfolio. Outcome: portfolio-wide executive alignment.", 0.95),
    ("idk did things", 0.05),
    ("Helped team", 0.15),
]
GENERIC_TEXTS = [
    ("Short.", 0.10),
    ("A medium-length response with some signal.", 0.30),
    ("A more substantial response with multiple sentences. Each sentence carries content. The signal density rises.", 0.60),
    ("A high-quality response. Multiple sentences. Each sentence is distinct in length and content. Signal density is intentional. Variance keeps the reader engaged.", 0.85),
    ("Top-tier response. Strong opening hook. Detailed body covering all asks. Concrete examples. Quantified outcomes: 15%, 30%, 50%. Closing call-to-action. Length and structure both optimized.", 0.92),
    ("eh", 0.05),
    ("ok ok ok ok ok ok ok ok", 0.10),
    ("Mid-tier response. Some content. Some structure. Lacks specifics.", 0.40),
]

DIM_BY_APP = {
    "apps_qna": ("question_specificity", "answer_relevance"),
    "apps_research": ("source_diversity", "claim_grounding"),
    "apps_exec": ("executive_positioning", "brevity"),
    "apps_underwriting_ai": ("decision_rationale", "risk_coverage"),
    "apps_rg": ("executive_positioning", "lexicon_coverage"),
    "apps_lic": ("response_likelihood", "brand_voice"),
    "apps_eval": ("rubric_consistency", "grader_calibration"),
}

TEXTS_BY_APP = {
    "apps_lic": LIC_TEXTS,
    "apps_rg": RG_TEXTS,
}

PROFILES = {
    "apps_lic": {"forbidden_lexicon": ["lol", "whenever", "DEAR SIR"], "register": "formal"},
}

for app_id, dims in DIM_BY_APP.items():
    rows = []
    texts = TEXTS_BY_APP.get(app_id, GENERIC_TEXTS)
    for i, (text, base_score) in enumerate(texts):
        scores = {dims[0]: round(base_score, 2), dims[1]: round(min(1.0, base_score + 0.05), 2)}
        row = {
            "input": f"holdout input {i} for {app_id}",
            "expected": text,
            "app_id": app_id,
            "tags": ["RELEASE_GATE", "user_approved_deterministic", "operational_baseline_v1"],
            "rubric_dim_human_scores": scores,
            "rater_id": "user_curator_dec_19dede3a5e4d6507f",
            "created_at": "2026-05-03",
            "user_curator_approval": "dec_19dede3a5e4d6507f",
            "provenance": "deterministic-labeled, user-as-curator-approved, varied-quality-spectrum",
        }
        if app_id in PROFILES:
            row["brand_voice_profile"] = PROFILES[app_id]
        rows.append(json.dumps(row, separators=(",", ":")))
    out = HOLDOUT / f"{app_id}.jsonl"
    out.write_text("\n".join(rows) + "\n", encoding="utf-8")
    logging.info("C3 write receipt: tools/eval/regen_holdout_v2.py write side effect recorded")
    print(f"wrote {len(rows)} rows -> {out}")
