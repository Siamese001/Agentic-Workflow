"""Interview card corpus definitions for apps_qna BGE-M3 indexing.

Defines 22 behavioral interview questions mapped to the 22 card types
in apps_qna, with 5 archetype variants (junior, mid, senior, staff, principal).
Total corpus: 110 question variants.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Archetype = Literal["junior", "mid", "senior", "staff", "principal"]

ARCHETYPES: list[Archetype] = ["junior", "mid", "senior", "staff", "principal"]


@dataclass(frozen=True)
class InterviewCard:
    """One interview card variant.

    Attributes:
        card_id: Unique identifier (e.g., "ARCHITECTURE_CORE_junior")
        interview_slug: URL-friendly identifier
        base_card_type: One of the 22 card types from apps_qna
        archetype: Skill level variant
        question_text: The behavioral interview question
        expected_evidence: Key evidence markers to look for in answers
        card_template: Associated template file from apps_qna
    """

    card_id: str
    interview_slug: str
    base_card_type: str
    archetype: Archetype
    question_text: str
    expected_evidence: list[str]
    card_template: str


# Base behavioral questions mapped to the 22 card types
_BASE_QUESTIONS: dict[str, dict] = {
    "RUNTIME_ROOT": {
        "template": "00_runtime_root.md.j2",
        "question": "Describe a production incident where you had to make a rapid decision with incomplete information. How did you establish your decision-making framework under pressure?",
        "evidence": ["decision_framework", "incomplete_data", "production_pressure", "outcome"],
    },
    "ROUTING_MANIFEST": {
        "template": "01_routing_manifest.md.j2",
        "question": "Tell me about a time you had to navigate conflicting stakeholder requirements. How did you prioritize and communicate your approach?",
        "evidence": ["stakeholder_management", "prioritization", "communication", "conflict_resolution"],
    },
    "LIVE_MODE": {
        "template": "02_live_mode.md.j2",
        "question": "Give an example of when you had to adapt your communication style for a technical vs. non-technical audience in a high-stakes presentation.",
        "evidence": ["audience_adaptation", "technical_communication", "executive_presence", "clarity"],
    },
    "INTERVIEWER_LENS": {
        "template": "03_interviewer_lens.md.j2",
        "question": "Describe how you've prepared for interviews with different personas (e.g., peer, manager, executive). How do you tailor your preparation?",
        "evidence": ["persona_analysis", "preparation_depth", "adaptability", "empathy"],
    },
    "COMPANY_OVERLAY": {
        "template": "04_company_overlay.md.j2",
        "question": "Tell me about a time you researched a company's culture and strategy before an important meeting. How did that research influence your approach?",
        "evidence": ["research_depth", "cultural_fit", "strategic_alignment", "preparation"],
    },
    "ARCHITECTURE_CORE": {
        "template": "05_architecture_core.md.j2",
        "question": "Walk me through a system architecture you designed. How did you balance scalability, reliability, and time-to-market?",
        "evidence": ["system_design", "tradeoffs", "scalability", "reliability", "decision_rationale"],
    },
    "DATA_PLATFORM": {
        "template": "06_data_platform.md.j2",
        "question": "Describe a data pipeline or platform you built. How did you ensure data quality and observability at scale?",
        "evidence": ["data_engineering", "data_quality", "observability", "scale"],
    },
    "MEASUREMENT": {
        "template": "07_measurement.md.j2",
        "question": "Tell me about a time you defined success metrics for a project. How did you choose between leading and lagging indicators?",
        "evidence": ["metrics_design", "measurement_strategy", "kpis", "attribution"],
    },
    "GOVERNANCE": {
        "template": "08_governance.md.j2",
        "question": "Describe how you've implemented governance controls in a fast-moving engineering organization. How did you balance governance with velocity?",
        "evidence": ["governance_design", "risk_management", "compliance", "velocity_balance"],
    },
    "SEMANTIC_GROUNDING": {
        "template": "09_semantic_grounding.md.j2",
        "question": "Give an example of how you've used semantic contracts or data dictionaries to prevent miscommunication between teams.",
        "evidence": ["semantic_contracts", "data_modeling", "cross_team_alignment", "clarity"],
    },
    "DS_TO_PLATFORM": {
        "template": "10_ds_to_platform.md.j2",
        "question": "Tell me about a time you transitioned a one-off data science solution into a reusable platform capability.",
        "evidence": ["platform_thinking", "abstraction", "reusability", "technical_debt"],
    },
    "GLOBAL_ENGINEERING": {
        "template": "11_global_engineering.md.j2",
        "question": "Describe how you've led or collaborated with distributed engineering teams across time zones. What challenges did you face?",
        "evidence": ["distributed_teams", "async_collaboration", "cultural_sensitivity", "communication"],
    },
    "PRODUCTIZATION": {
        "template": "12_productization.md.j2",
        "question": "Tell me about a time you turned an internal tool or prototype into a productized offering. How did you think about the transition?",
        "evidence": ["product_thinking", "user_experience", "scalability", "business_model"],
    },
    "EXECUTIVE_FIT": {
        "template": "13_executive_fit.md.j2",
        "question": "Describe a situation where you had to influence senior leadership to change direction. How did you build your case?",
        "evidence": ["executive_communication", "influence", "data_driven", "stakeholder_management"],
    },
    "STAR_BANK": {
        "template": "14_star_bank.md.j2",
        "question": "Walk me through your strongest STAR-format story that demonstrates your leadership at the {archetype} level.",
        "evidence": ["star_format", "situation", "task", "action", "result", "leadership_evidence"],
    },
    "RCA": {
        "template": "15_rca.md.j2",
        "question": "Describe a complex production issue you root-caused. What was your methodology for identifying the true root cause?",
        "evidence": ["root_cause_analysis", "methodical_approach", "five_whys", "systems_thinking"],
    },
    "CROSS_EXAM": {
        "template": "16_cross_exam.md.j2",
        "question": "Tell me about a time your technical decision was challenged. How did you defend your position or acknowledge the better approach?",
        "evidence": ["technical_rigor", "humility", "intellectual_honesty", "decision_quality"],
    },
    "QUESTIONS_AND_90_DAY_PLAN": {
        "template": "17_questions_and_90_day_plan.md.j2",
        "question": "What questions would you ask in your first week? Describe your 90-day plan for this {archetype} role.",
        "evidence": ["curiosity", "strategic_thinking", "onboarding_plan", "prioritization"],
    },
    "SOURCE_REGISTER": {
        "template": "19_source_register.md.j2",
        "question": "How do you track and cite your sources when making technical recommendations? Give an example where this discipline mattered.",
        "evidence": ["source_discipline", "attribution", "decision_traceability", "rigor"],
    },
    "GLOSSARY": {
        "template": "20_glossary.md.j2",
        "question": "Describe a time you had to establish shared terminology to prevent miscommunication in a cross-functional project.",
        "evidence": ["communication_clarity", "taxonomy", "cross_functional", "alignment"],
    },
    "LIKELY_QUESTIONS": {
        "template": "21_likely_questions.md.j2",
        "question": "How do you anticipate and prepare for questions that interviewers are likely to ask about your background?",
        "evidence": ["preparation", "self_awareness", "anticipation", "readiness"],
    },
    "LEARNINGS": {
        "template": "22_learnings.md.j2",
        "question": "Tell me about a significant professional failure and what you learned from it. How has that learning influenced your approach?",
        "evidence": ["growth_mindset", "vulnerability", "reflection", "behavioral_change"],
    },
}

# Archetype-specific adaptations
_ARCHETYPE_ADAPTATIONS: dict[Archetype, dict] = {
    "junior": {
        "prefix": "As someone early in your career",
        "scope": "individual contributor",
        "scale": "small team or feature",
    },
    "mid": {
        "prefix": "With a few years of experience",
        "scope": "senior individual contributor",
        "scale": "component or subsystem",
    },
    "senior": {
        "prefix": "As an experienced professional",
        "scope": "tech lead or senior IC",
        "scale": "system or product area",
    },
    "staff": {
        "prefix": "At the staff engineer level",
        "scope": "staff engineer or architect",
        "scale": "multi-system or organization",
    },
    "principal": {
        "prefix": "As a principal-level leader",
        "scope": "principal engineer or distinguished engineer",
        "scale": "company-wide or industry",
    },
}


def _adapt_question_for_archetype(base_question: str, archetype: Archetype) -> str:
    """Adapt a base question for a specific archetype.

    Replaces {archetype} placeholders and adds archetype-appropriate framing.
    """
    adaptation = _ARCHETYPE_ADAPTATIONS[archetype]

    # Replace placeholders
    question = base_question.replace("{archetype}", archetype)

    # Add archetype prefix for STAR_BANK and QUESTIONS_AND_90_DAY_PLAN
    if "STAR_BANK" in question or "90-day plan" in question:
        question = f"{adaptation['prefix']}, {question[0].lower()}{question[1:]}"

    return question


def generate_corpus() -> list[InterviewCard]:
    """Generate the full interview card corpus.

    Returns:
        List of 110 InterviewCard variants (22 cards × 5 archetypes)
    """
    corpus: list[InterviewCard] = []

    for card_type, base in _BASE_QUESTIONS.items():
        for archetype in ARCHETYPES:
            card_id = f"{card_type}_{archetype}"
            interview_slug = f"{card_type.lower()}_{archetype}"

            question = _adapt_question_for_archetype(base["question"], archetype)

            # Add archetype scope to expected evidence
            evidence = base["evidence"].copy()
            evidence.append(f"{archetype}_scope")

            card = InterviewCard(
                card_id=card_id,
                interview_slug=interview_slug,
                base_card_type=card_type,
                archetype=archetype,
                question_text=question,
                expected_evidence=evidence,
                card_template=base["template"],
            )
            corpus.append(card)

    return corpus


def get_corpus_by_archetype(archetype: Archetype) -> list[InterviewCard]:
    """Get all cards for a specific archetype."""
    return [c for c in generate_corpus() if c.archetype == archetype]


def get_card_by_slug(interview_slug: str) -> InterviewCard | None:
    """Look up a card by its interview slug."""
    for card in generate_corpus():
        if card.interview_slug == interview_slug:
            return card
    return None


if __name__ == "__main__":
    # Validate corpus generation
    corpus = generate_corpus()
    print(f"Generated {len(corpus)} interview card variants")
    print(f"  - Cards per archetype: {len(corpus) // len(ARCHETYPES)}")
    print(f"  - Archetypes: {', '.join(ARCHETYPES)}")

    for archetype in ARCHETYPES:
        archetype_cards = get_corpus_by_archetype(archetype)
        print(f"  - {archetype}: {len(archetype_cards)} cards")

    # Sample output
    sample = corpus[0]
    print(f"\nSample card: {sample.card_id}")
    print(f"  Slug: {sample.interview_slug}")
    print(f"  Question: {sample.question_text[:100]}...")
    print(f"  Evidence markers: {', '.join(sample.expected_evidence[:3])}")
