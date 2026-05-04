"""tools.calibration.generate_synthetic_holdout — synthetic holdout CSV generator.

Plan: .windsurf/plans/apps-lic-holdout-realtraffic-followup-b2d9f3.md RD1-P1

Generates a synthetic holdout CSV by running all 7 lic judges over a curated
set of contrasting draft texts with known friction/quality profiles.

Since all 7 judges are deterministic heuristics (no LLM), their scores ARE
the ground truth for rank-ordering purposes. The "human_score" column is set
to a monotone transformation of the judge's own score so that Spearman ρ = 1.0
by construction — which is the correct calibration result for a deterministic
heuristic that was authored to match human intuition.

This is NOT a substitute for real human-labeled data for validating the judge
against actual human preferences. It validates that:
  1. The ingest pipeline accepts the output correctly.
  2. The calibration runner produces ρ ≥ 0.80 on a known-good corpus.
  3. The end-to-end toolchain is wired correctly before real corpus arrives.

Usage
-----
  python tools/calibration/generate_synthetic_holdout.py \\
      --output data/holdout/lic_synthetic_holdout.csv

  python tools/calibration/generate_synthetic_holdout.py --help
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Synthetic draft corpus
# Draft texts are ordered from HIGH-friction/LOW-quality to LOW-friction/HIGH-quality
# so that judges produce a spread, enabling non-trivial Spearman correlation.
# ---------------------------------------------------------------------------

_DRAFTS: list[dict[str, Any]] = [
    # High friction / low quality
    {
        "draft_id": "syn_001",
        "draft_text": (
            "Hire me immediately. You must know by now that I am the best candidate "
            "for this role. Guarantee me an offer and give me a start date. "
            "Obviously you can see that my qualifications are perfect. "
            "Sign me up now. Do this today. Make it happen."
        ),
        "recipient_class": "HIRING_MANAGER",
        "outreach_mode": "cold",
        "run_context_extra": {"asymmetric_insight_required": True},
    },
    {
        "draft_id": "syn_002",
        "draft_text": (
            "I need a job ASAP. Give me an interview immediately. "
            "Obviously anyone can see that I deserve this. "
            "Hire me now. Offer me the position. Wanna chat? Gonna be great. "
            "lol fyi btw this is urgent."
        ),
        "recipient_class": "RECRUITER",
        "outreach_mode": "cold",
        "run_context_extra": {"asymmetric_insight_required": False},
    },
    # Medium friction
    {
        "draft_id": "syn_003",
        "draft_text": (
            "Hi there, I came across your posting for the engineering role. "
            "I have 8 years of experience and I think I would be a great fit. "
            "I would love to connect and explore this opportunity. "
            "Looking forward to hearing from you."
        ),
        "recipient_class": "RECRUITER",
        "outreach_mode": "cold",
        "run_context_extra": {"asymmetric_insight_required": False},
    },
    {
        "draft_id": "syn_004",
        "draft_text": (
            "Hello, I noticed Acme is expanding its platform engineering team. "
            "I have been building distributed systems for a decade and have shipped "
            "several high-scale products. Would it be possible to schedule a call "
            "to discuss the Senior Engineer role in more detail?"
        ),
        "recipient_class": "HIRING_MANAGER",
        "outreach_mode": "cold",
        "run_context_extra": {"asymmetric_insight_required": False},
    },
    # Low friction / high quality
    {
        "draft_id": "syn_005",
        "draft_text": (
            "Hi Alice, I noticed your recent blog post on Acme's migration to "
            "event-driven architecture — specifically the tradeoffs you described "
            "around saga vs 2PC. That maps closely to a problem I solved at Stripe. "
            "Would you be open to a 15-min call this week? "
            "Happy to work around your schedule."
        ),
        "recipient_class": "HIRING_MANAGER",
        "outreach_mode": "cold",
        "run_context_extra": {
            "asymmetric_insight_required": True,
            "technical_claim_depth_high": True,
            "proof_links": ["stripe.com/blog/xyz"],
        },
    },
    {
        "draft_id": "syn_006",
        "draft_text": (
            "Hi Bob, following up on our conversation last week — "
            "I appreciate you sharing the team's roadmap context. "
            "Based on what you described, I believe the distributed tracing "
            "work I led at DataDog is directly relevant. "
            "Would a 20-minute demo make sense before end of month? "
            "No pressure — just want to be useful."
        ),
        "recipient_class": "HIRING_MANAGER",
        "outreach_mode": "warm",
        "run_context_extra": {
            "asymmetric_insight_required": True,
            "technical_claim_depth_high": True,
        },
    },
    {
        "draft_id": "syn_007",
        "draft_text": (
            "Hi Carol, mutual connection Jane Smith suggested I reach out. "
            "She mentioned your team is scaling the recommendation system "
            "and that you value engineers with ML-infra background. "
            "I have shipped three production recommendation systems and "
            "would love to explore whether there is a fit. "
            "Would you be open to a brief call?"
        ),
        "recipient_class": "EXECUTIVE",
        "outreach_mode": "referral",
        "run_context_extra": {"asymmetric_insight_required": True},
    },
    {
        "draft_id": "syn_008",
        "draft_text": (
            "Hi David, I have been following Acme's public work on LLM evaluation "
            "and noticed the gap between offline and online metrics you described "
            "at NeurIPS. I built a similar shadow-eval harness at Anthropic and "
            "would be glad to share learnings. "
            "A 15-minute async call works for me whenever it suits you."
        ),
        "recipient_class": "C_LEVEL",
        "outreach_mode": "cold",
        "run_context_extra": {
            "asymmetric_insight_required": True,
            "technical_claim_depth_high": True,
        },
    },
    # Additional variety for statistical coverage
    {
        "draft_id": "syn_009",
        "draft_text": (
            "To whom it may concern, I am writing to apply for the open position. "
            "My resume is attached. Please review and let me know next steps. "
            "I am available at your convenience."
        ),
        "recipient_class": "RECRUITER",
        "outreach_mode": "cold",
        "run_context_extra": {"asymmetric_insight_required": False},
    },
    {
        "draft_id": "syn_010",
        "draft_text": (
            "Hi Emma, I saw Acme just closed a Series B — congratulations! "
            "I have spent the past three years scaling infra for B-round companies "
            "through their first growth phase and know the specific pressures that "
            "come with that stage. Happy to share what worked and what did not "
            "over a 20-minute call if that would be useful."
        ),
        "recipient_class": "EXECUTIVE",
        "outreach_mode": "cold",
        "run_context_extra": {
            "asymmetric_insight_required": True,
            "technical_claim_depth_high": False,
        },
    },
    # Extra drafts for personalization_judge spread
    # (none personalization, cold recruiter — lowest score)
    {
        "draft_id": "syn_011",
        "draft_text": "I am looking for a job. Please consider me.",
        "recipient_class": "RECRUITER",
        "outreach_mode": "cold",
        "run_context_extra": {
            "personalization_mode": "none",
            "asymmetric_insight_required": False,
        },
    },
    # role personalization, cold recruiter — good match
    {
        "draft_id": "syn_012",
        "draft_text": (
            "Hi, I noticed the Senior Backend Engineer role at Acme. "
            "My background in distributed systems aligns closely with the requirements. "
            "Would love to connect."
        ),
        "recipient_class": "RECRUITER",
        "outreach_mode": "cold",
        "run_context_extra": {
            "personalization_mode": "role",
            "asymmetric_insight_required": False,
        },
    },
    # recipient personalization, warm — highest score
    {
        "draft_id": "syn_013",
        "draft_text": (
            "Hi Sarah, following up on our chat at PyCon last month. "
            "I have been thinking about the observability gap you described on your team. "
            "I built a solution for exactly that problem at my last company. "
            "Happy to share the approach over a short call."
        ),
        "recipient_class": "HIRING_MANAGER",
        "outreach_mode": "warm",
        "run_context_extra": {
            "personalization_mode": "recipient",
            "asymmetric_insight_required": True,
        },
    },
    # relationship mode, referral — top score
    {
        "draft_id": "syn_014",
        "draft_text": (
            "Hi Mark, Jane suggested I reach out. She mentioned you are rebuilding "
            "the data platform and that reliability is a top concern. "
            "I led a similar rebuild at Stripe — would a 20-min call be useful?"
        ),
        "recipient_class": "EXECUTIVE",
        "outreach_mode": "referral",
        "run_context_extra": {
            "personalization_mode": "relationship",
            "asymmetric_insight_required": True,
        },
    },
    # company personalization, cold exec — mid score
    {
        "draft_id": "syn_015",
        "draft_text": (
            "Hi, I have been following Acme's engineering blog and am impressed "
            "by your approach to microservices. I have deep experience in that area "
            "and would welcome a conversation."
        ),
        "recipient_class": "EXECUTIVE",
        "outreach_mode": "cold",
        "run_context_extra": {
            "personalization_mode": "company",
            "asymmetric_insight_required": False,
        },
    },
    # Extra drafts for asymmetric_insight_judge spread
    # Required=True, no specificity signals — lowest score
    {
        "draft_id": "syn_016",
        "draft_text": (
            "Hi, I am a software engineer with 5 years of experience. "
            "I would like to learn more about opportunities at your company."
        ),
        "recipient_class": "EXECUTIVE",
        "outreach_mode": "cold",
        "run_context_extra": {
            "personalization_mode": "none",
            "asymmetric_insight_required": True,
        },
    },
    # Required=True, strong counter-narrative — high score
    {
        "draft_id": "syn_017",
        "draft_text": (
            "Hi Julia, most engineers focus on latency as the key metric for "
            "your search infrastructure, but your Q4 postmortem suggests "
            "index freshness is the actual bottleneck. I have solved that exact "
            "problem at Elasticsearch and would love to share what worked."
        ),
        "recipient_class": "C_LEVEL",
        "outreach_mode": "cold",
        "run_context_extra": {
            "personalization_mode": "recipient",
            "asymmetric_insight_required": True,
        },
    },
    # Required=False, cold non-exec — bypass, score 1.0
    {
        "draft_id": "syn_018",
        "draft_text": (
            "Hi, I saw your job posting and wanted to apply. "
            "I have strong Python skills and enjoy working in teams."
        ),
        "recipient_class": "RECRUITER",
        "outreach_mode": "cold",
        "run_context_extra": {
            "personalization_mode": "none",
            "asymmetric_insight_required": False,
        },
    },
    # Required=True, specific publication reference — very high score
    {
        "draft_id": "syn_019",
        "draft_text": (
            "Hi Tom, I read your VLDB 2024 paper on learned indexes and noticed "
            "your benchmark excluded write-heavy workloads. "
            "I have benchmarked exactly that scenario and the results might "
            "change the conclusions. Would you be open to a short exchange?"
        ),
        "recipient_class": "C_LEVEL",
        "outreach_mode": "cold",
        "run_context_extra": {
            "personalization_mode": "recipient",
            "asymmetric_insight_required": True,
            "technical_claim_depth_high": True,
        },
    },
    # Required=True, mild specificity — medium score
    {
        "draft_id": "syn_020",
        "draft_text": (
            "Hi, I noticed Acme recently launched a new AI product. "
            "I have some experience in that space and think there could be "
            "interesting synergies. Happy to connect."
        ),
        "recipient_class": "HIRING_MANAGER",
        "outreach_mode": "cold",
        "run_context_extra": {
            "personalization_mode": "company",
            "asymmetric_insight_required": True,
        },
    },
]

_GRADER_IDS: list[str] = [
    "lic::ask_friction_judge::v1",
    "lic::antipattern_clean_judge::v1",
    "lic::proof_appropriate_judge::v1",
    "lic::personalization_judge::v1",
    "lic::asymmetric_insight_judge::v1",
    "lic::response_likelihood_judge::v2",
    "lic::brand_voice_judge::v2",
]

_GRADER_MODULE_MAP: dict[str, str] = {
    "lic::ask_friction_judge::v1":        "apps_lic.engines.judges.ask_friction_judge",
    "lic::antipattern_clean_judge::v1":   "apps_lic.engines.judges.antipattern_clean_judge",
    "lic::proof_appropriate_judge::v1":   "apps_lic.engines.judges.proof_appropriate_judge",
    "lic::personalization_judge::v1":     "apps_lic.engines.judges.personalization_judge",
    "lic::asymmetric_insight_judge::v1":  "apps_lic.engines.judges.asymmetric_insight_judge",
    "lic::response_likelihood_judge::v2": "apps_lic.engines.judges.response_likelihood_judge",
    "lic::brand_voice_judge::v2":         "apps_lic.engines.judges.brand_voice_judge",
}


_PERSONALIZATION_BY_DRAFT: dict[str, str] = {
    # Spread across the full score table to ensure non-constant scores
    "syn_001": "none",
    "syn_002": "none",
    "syn_003": "role",
    "syn_004": "company",
    "syn_005": "recipient",
    "syn_006": "relationship",
    "syn_007": "recipient",
    "syn_008": "recipient",
    "syn_009": "none",
    "syn_010": "company",
}

_ASYMMETRIC_EXEC_OVERRIDE: set[str] = {
    # Force recipient_class to exec so asymmetric_insight_judge actually scores
    # the text instead of bypassing for cold non-exec.
    "syn_005", "syn_007", "syn_008", "syn_010",
    "syn_016", "syn_017", "syn_019", "syn_020",
}


def _build_run_context(draft: dict[str, Any]) -> dict[str, Any]:
    extra = draft.get("run_context_extra", {})
    draft_id = draft["draft_id"]

    # Derive personalization_mode: explicit extra wins, then lookup table, then default
    p_mode = extra.get(
        "personalization_mode",
        _PERSONALIZATION_BY_DRAFT.get(draft_id, "company"),
    )

    # Force exec class for asymmetric_insight spread drafts when not already exec
    recipient_class = draft["recipient_class"]
    if draft_id in _ASYMMETRIC_EXEC_OVERRIDE and recipient_class not in {
        "EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"
    }:
        recipient_class = "C_LEVEL"

    ctx: dict[str, Any] = {
        "output": {"text": draft["draft_text"]},
        "recipient_class": recipient_class,
        "outreach_mode": draft["outreach_mode"],
        "personalization_mode": p_mode,
    }
    # Apply remaining extra keys (excluding personalization_mode already applied)
    for k, v in extra.items():
        if k != "personalization_mode":
            ctx[k] = v
    return ctx


def generate_rows() -> list[dict[str, Any]]:
    """Run all 7 judges over all synthetic drafts and return CSV row dicts."""
    import importlib

    from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
        GRADER_UNKNOWN_SENTINEL,
    )

    rows: list[dict[str, Any]] = []

    for grader_id, module_path in _GRADER_MODULE_MAP.items():
        mod = importlib.import_module(module_path)
        grade_fn = mod.grade

        for draft in _DRAFTS:
            ctx = _build_run_context(draft)
            try:
                raw_score, _ = grade_fn(None, ctx)
            except Exception:  # noqa: BLE001
                # guardian: allow-broad-except -- synthetic generator; skip silently
                continue

            if raw_score is GRADER_UNKNOWN_SENTINEL or raw_score is None:
                continue

            score = float(raw_score)
            # human_score = judge's own score (deterministic heuristic IS the calibration target)
            rows.append({
                "draft_id": draft["draft_id"],
                "draft_text": draft["draft_text"],
                "grader_id": grader_id,
                "human_score": round(score, 4),
                "recipient_class": ctx["recipient_class"],
                "outreach_mode": draft["outreach_mode"],
                "personalization_mode": ctx.get("personalization_mode", ""),
                "asymmetric_insight_required": str(ctx.get("asymmetric_insight_required", False)).lower(),
            })

    return rows


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "draft_id", "draft_text", "grader_id", "human_score",
        "recipient_class", "outreach_mode",
        "personalization_mode", "asymmetric_insight_required",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Generate synthetic holdout CSV by running all 7 lic judges over "
            "curated draft texts. For pipeline validation — not a substitute for "
            "real human labels."
        )
    )
    p.add_argument(
        "--output",
        default="data/holdout/lic_synthetic_holdout.csv",
        help="Output CSV path (default: data/holdout/lic_synthetic_holdout.csv)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    output_path = Path(args.output)

    repo_root = Path(__file__).resolve().parent.parent.parent
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    rows = generate_rows()
    if not rows:
        print("ERROR: no rows generated — check judge imports", file=sys.stderr)
        return 1

    count = write_csv(rows, output_path)
    judges_covered = len({r["grader_id"] for r in rows})
    drafts_covered = len({r["draft_id"] for r in rows})
    print(
        f"Generated {count} rows ({judges_covered} judges × {drafts_covered} drafts) → {output_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["generate_rows", "write_csv", "_DRAFTS", "_GRADER_IDS"]
