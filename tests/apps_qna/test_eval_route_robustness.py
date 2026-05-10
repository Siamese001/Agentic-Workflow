"""W5.2 — paraphrase-robustness eval harness.

Wave 5 phase 5.2 of ``apps-qna-dag-enhancements-e4c7b2``. Acceptance
criterion for the plan: route-stability >= 0.80 across a 20+ question
paraphrase sample, measured against the unified BGE-M3 semantic router.

Design
------
Each "base" question names an expected route. Each base has 2-3 hand-
curated paraphrases that a reasonable interviewer might use for the
same underlying intent. The harness runs ``SemanticRouter.best`` on
every question and computes:

    stability = |{paraphrases whose top-1 matches the base's top-1}|
                / |{paraphrases}|

The harness also prints a per-route breakdown so a failing run points
directly at the routes that need descriptor work.

Skips gracefully when the spine primitive is running under keyword
fallback — the 0.80 floor is a statement about the BGE-M3 path only.
"""

from __future__ import annotations

import pytest

from apps_qna.config.route_registry import load_route_registry
from apps_qna.router.semantic_router import SemanticRouter


# ``(expected_route_id, [base_question, paraphrase1, paraphrase2, ...])``.
# Paraphrase sets follow real interview phrasings and stay scoped to one
# route's semantics — do not introduce cross-route ambiguity here.
_PARAPHRASE_SETS: list[tuple[str, list[str]]] = [
    (
        "architecture",
        [
            "How would you build an agentic architecture for our team?",
            "Walk me through how you'd design an agentic architecture for our org",
            "Describe your architecture for a multi-agent system",
        ],
    ),
    (
        "governance",
        [
            "How do you handle hallucinations and guardrails?",
            "What guardrails do you put around hallucinations?",
            "How do you prevent hallucinations with governance controls?",
        ],
    ),
    (
        "rca",
        [
            "What went wrong on your last big project? Root cause please.",
            "Walk me through a root-cause analysis you ran on a failed project",
            "Tell me about a post-mortem and the root cause you identified",
        ],
    ),
    (
        "productization",
        [
            "What's your approach to ROI and planner adoption?",
            "How do you drive planner adoption and ROI for a new platform?",
            "Describe your productization playbook for planner adoption and ROI",
        ],
    ),
    (
        "ds_to_platform",
        [
            "How does MMM relate to incrementality and Meridian?",
            "Explain how MMM, incrementality and Meridian fit together",
            "Walk me through MMM incrementality using Meridian",
        ],
    ),
    (
        "global_engineering",
        [
            "How do you run a distributed pods / DGS engineering org?",
            "Describe running a DGS pods engineering organization",
            "How do you manage a pods-based DGS engineering team?",
        ],
    ),
    (
        "star_proof",
        [
            "Give me an example of prior work you have shipped.",
            "Share a STAR example of a prior project you shipped",
            "Tell me about a prior shipped project as a STAR example",
        ],
    ),
    (
        "cross_exam",
        [
            "Be more specific — what tools exactly did you use?",
            "Be more specific about the exact tools you used",
            "Name specifically which tools you used — I need specifics",
        ],
    ),
    (
        "executive_fit",
        [
            "Why this company? Why this role for you?",
            "Why are you interested in this role at this company?",
            "What draws you to this company and this role?",
        ],
    ),
]


def _total_question_count() -> int:
    return sum(len(qs) for _, qs in _PARAPHRASE_SETS)


@pytest.fixture(scope="module")
def router() -> SemanticRouter:
    return SemanticRouter(load_route_registry())


def test_paraphrase_sample_size_meets_plan_acceptance() -> None:
    """Plan §Acceptance: sample must have >= 20 paraphrase questions."""
    assert _total_question_count() >= 20, _total_question_count()


def test_paraphrase_robustness_meets_eighty_percent_floor(
    router: SemanticRouter,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Plan §Acceptance: paraphrase-robustness >= 0.80 on BGE-M3.

    Per-route breakdown is printed to stdout so a failing run immediately
    names the underperforming routes. Run with ``pytest -s`` to see it.
    """
    total_paraphrases = 0
    total_matches = 0
    per_route_stats: dict[str, tuple[int, int]] = {}
    embedding_mode_seen = False

    for expected_route_id, questions in _PARAPHRASE_SETS:
        base_best = router.best(questions[0])
        if base_best is None:
            # Base-question abstention is itself a failure of the
            # descriptor — count it against the route.
            matches = 0
            paraphrases = len(questions) - 1
        else:
            if base_best.mode == "embedding":
                embedding_mode_seen = True
            base_route = base_best.route_id
            matches = 0
            paraphrases = 0
            for paraphrase in questions[1:]:
                paraphrases += 1
                best = router.best(paraphrase)
                if best is not None and best.route_id == base_route:
                    matches += 1
        per_route_stats[expected_route_id] = (matches, paraphrases)
        total_matches += matches
        total_paraphrases += paraphrases

    stability = (
        total_matches / total_paraphrases if total_paraphrases else 0.0
    )

    # Emit a deterministic, grep-friendly report.
    print()
    print("=" * 70)
    print(
        f"W5.2 paraphrase-robustness report — {total_matches}/{total_paraphrases} "
        f"stability={stability:.3f}"
    )
    print("=" * 70)
    for route_id, (matches, paraphrases) in per_route_stats.items():
        rate = matches / paraphrases if paraphrases else 0.0
        print(f"  {route_id:<20} {matches}/{paraphrases}   stability={rate:.3f}")
    print("=" * 70)

    if not embedding_mode_seen:
        pytest.skip(
            "Spine primitive in keyword-fallback mode; 0.80 floor "
            "applies to the BGE-M3 embedding path only."
        )

    assert stability >= 0.80, (
        f"paraphrase-robustness {stability:.3f} below 0.80 floor "
        f"(plan §Acceptance). Per-route: {per_route_stats}"
    )
