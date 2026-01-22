"""Psychometric Persona Router - Dynamic reader persona generation.

This module analyzes job descriptions to infer the psychological profile
of the hiring manager and generates a dynamic reader persona to ensure
the resume "feels" right to the specific human reading it.
"""

import logging


logger = logging.getLogger(__name__)


class ArchetypeBase(str, Enum):
    """Base psychological archetypes for hiring managers."""

    VISIONARY = "VISIONARY"  # Focus on Future, Disruption, 0-to-1
    OPERATOR = "OPERATOR"  # Focus on Execution, Efficiency, Scale
    GUARDIAN = "GUARDIAN"  # Focus on Risk, Stability, Compliance
    SCALER = "SCALER"  # Focus on Growth, Metrics, Hiring


class PsychometricProfile(BaseModel):
    """Psychometric profile derived from JD analysis."""

    risk_tolerance: float = Field(..., description="0.0 (Safe) to 1.0 (High Risk)")
    technical_depth: float = Field(..., description="0.0 (Generalist) to 1.0 (Deep Tech)")
    bureaucracy_level: float = Field(..., description="0.0 (Flat/Startup) to 1.0 (Corp)")
    dominant_archetype: ArchetypeBase
    keywords_detected: list[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, description="Confidence in profile accuracy")


class ReaderPersona(BaseModel):
    """Generated reader persona for resume customization."""

    title: str  # e.g. "The Risk-Averse Enterprise Gatekeeper"
    tone_instruction: str  # "Use formal language. Emphasize governance."
    highlight_focus: list[str]  # ["Compliance", "Uptime", "Budget"]
    avoid_topics: list[str] = Field(default_factory=list)
    formatting_preferences: dict[str, str] = Field(default_factory=dict)
    archetype: ArchetypeBase
    profile: PsychometricProfile


class PersonaRouter:
    """Analyzes JD to generate dynamic reader personas."""

    def __init__(self):
        """Initialize persona router with keyword dictionaries."""
        # Risk tolerance keywords
        self.risk_high_keywords = [
            "hacker",
            "ninja",
            "disrupt",
            "disruption",
            "greenfield",
            "mvp",
            "fast-paced",
            "agile",
            "startup",
            "venture",
            "innovative",
            "breakthrough",
            "game-changer",
            "revolutionary",
            "bold",
            "fail fast",
            "iterate",
            "pivot",
            "unleash",
            "daring",
        ]

        self.risk_low_keywords = [
            "proven",
            "stable",
            "audit",
            "compliance",
            "iso27001",
            "sox",
            "enterprise",
            "fortune",
            "regulated",
            "secure",
            "risk management",
            "governance",
            "established",
            "mature",
            "reliable",
            "consistent",
            "conservative",
            "methodical",
            "careful",
            "thorough",
            "process",
        ]

        # Technical depth keywords
        self.tech_deep_keywords = [
            "kernel",
            "cuda",
            "latency",
            "distributed systems",
            "microservices",
            "architecture",
            "scalability",
            "performance",
            "optimization",
            "low-level",
            "systems programming",
            "algorithms",
            "data structures",
            "concurrency",
            "parallel computing",
            "infrastructure",
            "devops",
            "kubernetes",
            "aws",
            "gcp",
            "azure",
            "cloud native",
        ]

        self.tech_general_keywords = [
            "business",
            "strategy",
            "leadership",
            "management",
            "communication",
            "collaboration",
            "teamwork",
            "project management",
            "stakeholder",
            "cross-functional",
            "partnership",
            "relationship",
            "client facing",
            "presentation",
            "negotiation",
            "influence",
            "persuade",
        ]

        # Bureaucracy level keywords
        self.bureaucracy_high_keywords = [
            "approval process",
            "hierarchy",
            "reporting structure",
            "chain of command",
            "corporate",
            "matrix organization",
            "cross-functional collaboration",
            "stakeholder management",
            "executive",
            "board",
            "committee",
            "review board",
            "policy",
            "procedure",
            "standard operating procedure",
            "sop",
            "compliance",
        ]

        self.bureaucracy_low_keywords = [
            "flat organization",
            "no bureaucracy",
            "direct access",
            "autonomy",
            "ownership",
            "startup culture",
            "fast decision making",
            "lean",
            "agile",
            "scrum",
            "sprints",
            "daily standup",
            "open door",
            "meritocracy",
        ]

        # Archetype-specific keywords
        self.archetype_keywords = {
            ArchetypeBase.VISIONARY: [
                "vision",
                "mission",
                "future",
                "transform",
                "reimagine",
                "pioneer",
                "trailblazer",
                "innovate",
                "breakthrough",
                "disrupt",
                "revolution",
                "next-generation",
                "paradigm shift",
                "game-changing",
            ],
            ArchetypeBase.OPERATOR: [
                "execute",
                "scale",
                "optimize",
                "efficiency",
                "process",
                "operations",
                "deliver",
                "implement",
                "drive",
                "achieve",
                "metrics",
                "performance",
                "productivity",
                "streamline",
                "operational excellence",
            ],
            ArchetypeBase.GUARDIAN: [
                "protect",
                "secure",
                "risk",
                "compliance",
                "governance",
                "stability",
                "reliability",
                "safety",
                "audit",
                "control",
                "mitigate",
                "safeguard",
                "ensure",
                "guarantee",
                "maintain",
                "preserve",
            ],
            ArchetypeBase.SCALER: [
                "grow",
                "growth",
                "scale",
                "expand",
                "multiply",
                "accelerate",
                "revenue",
                "market share",
                "user base",
                "hiring",
                "team building",
                "recruitment",
                "onboarding",
                "training",
                "leadership pipeline",
            ],
        }

        logger.info("Initialized PersonaRouter with keyword dictionaries")

    def analyze_jd(self, jd_text: str) -> ReaderPersona:
        """Analyze job description text to generate reader persona.

        Args:
            jd_text: Raw job description text

        Returns:
            Generated reader persona
        """
        # Normalize text
        text = jd_text.lower()

        # Calculate psychometric scores
        risk_score = self._calculate_dimension_score(
            text, self.risk_high_keywords, self.risk_low_keywords
        )

        tech_score = self._calculate_dimension_score(
            text, self.tech_deep_keywords, self.tech_general_keywords
        )

        bureaucracy_score = self._calculate_dimension_score(
            text, self.bureaucracy_high_keywords, self.bureaucracy_low_keywords
        )

        # Determine dominant archetype
        archetype, archetype_keywords = self._determine_archetype(text)

        # Build psychometric profile
        profile = PsychometricProfile(
            risk_tolerance=risk_score,
            technical_depth=tech_score,
            bureaucracy_level=bureaucracy_score,
            dominant_archetype=archetype,
            keywords_detected=archetype_keywords,
            confidence_score=self._calculate_confidence(risk_score, tech_score, bureaucracy_score),
        )

        # Generate reader persona
        persona = self._generate_persona(profile)

        logger.info(f"Generated persona: {persona.title} (Archetype: {archetype.value})")
        return persona

    def _calculate_dimension_score(
        self, text: str, high_keywords: list[str], low_keywords: list[str]
    ) -> float:
        """Calculate a 0.0-1.0 score for a dimension.

        Args:
            text: Normalized JD text
            high_keywords: Keywords indicating high score
            low_keywords: Keywords indicating low score

        Returns:
            Score between 0.0 and 1.0
        """
        high_count = sum(1 for keyword in high_keywords if keyword in text)
        low_count = sum(1 for keyword in low_keywords if keyword in text)

        # Normalize to 0-1 range
        total = high_count + low_count
        if total == 0:
            return 0.5  # Neutral when no keywords found

        return high_count / total

    def _determine_archetype(self, text: str) -> tuple[ArchetypeBase, list[str]]:
        """Determine dominant archetype from text.

        Args:
            text: Normalized JD text

        Returns:
            Tuple of (archetype, matching keywords)
        """
        scores = {}
        matched_keywords = {}

        for archetype, keywords in self.archetype_keywords.items():
            matches = [kw for kw in keywords if kw in text]
            scores[archetype] = len(matches)
            matched_keywords[archetype] = matches

        # Find archetype with most matches
        dominant_archetype = max(scores, key=scores.get)

        return dominant_archetype, matched_keywords[dominant_archetype]

    def _calculate_confidence(
        self, risk_score: float, tech_score: float, bureaucracy_score: float
    ) -> float:
        """Calculate confidence score for the profile.

        Args:
            risk_score: Risk tolerance score
            tech_score: Technical depth score
            bureaucracy_score: Bureaucracy level score

        Returns:
            Confidence score between 0.0 and 1.0
        """
        # High confidence when scores are not neutral (close to 0.5)
        deviation_from_neutral = (
            abs(risk_score - 0.5) + abs(tech_score - 0.5) + abs(bureaucracy_score - 0.5)
        ) / 3

        return min(deviation_from_neutral * 2, 1.0)

    def _generate_persona(self, profile: PsychometricProfile) -> ReaderPersona:
        """Generate reader persona from psychometric profile.

        Args:
            profile: Psychometric profile

        Returns:
            Reader persona
        """
        archetype = profile.dominant_archetype

        # Generate persona based on archetype and scores
        if archetype == ArchetypeBase.VISIONARY:
            return self._generate_visionary_persona(profile)
        elif archetype == ArchetypeBase.OPERATOR:
            return self._generate_operator_persona(profile)
        elif archetype == ArchetypeBase.GUARDIAN:
            return self._generate_guardian_persona(profile)
        elif archetype == ArchetypeBase.SCALER:
            return self._generate_scaler_persona(profile)
        else:
            # Default fallback
            return self._generate_default_persona(profile)

    def _generate_visionary_persona(self, profile: PsychometricProfile) -> ReaderPersona:
        """Generate visionary persona.

        Args:
            profile: Psychometric profile

        Returns:
            Visionary reader persona
        """
        if profile.risk_tolerance > 0.8:
            title = "The Disruption-Seeking Innovator"
            tone = "Use bold, forward-looking language. Emphasize speed and innovation."
            highlights = ["Innovation", "Speed", "Impact", "Transformation"]
            avoids = ["Process", "Stability", "Compliance"]
        else:
            title = "The Strategic Visionary"
            tone = "Balance vision with practicality. Show big-picture thinking."
            highlights = ["Strategy", "Vision", "Growth", "Leadership"]
            avoids = ["Technical details", "Process overhead"]

        return ReaderPersona(
            title=title,
            tone_instruction=tone,
            highlight_focus=highlights,
            avoid_topics=avoids,
            formatting_preferences={"style": "dynamic", "length": "concise"},
            archetype=ArchetypeBase.VISIONARY,
            profile=profile,
        )

    def _generate_operator_persona(self, profile: PsychometricProfile) -> ReaderPersona:
        """Generate operator persona.

        Args:
            profile: Psychometric profile

        Returns:
            Operator reader persona
        """
        if profile.technical_depth > 0.7:
            title = "The Engineering Operator"
            tone = "Be precise and technical. Focus on execution and metrics."
            highlights = ["Execution", "Metrics", "Efficiency", "Results"]
            avoids = ["Vision statements", "Corporate jargon"]
        else:
            title = "The Business Operator"
            tone = "Focus on operational excellence and team leadership."
            highlights = ["Operations", "Process", "Team", "Delivery"]
            avoids = ["Technical deep dives", "Theoretical concepts"]

        return ReaderPersona(
            title=title,
            tone_instruction=tone,
            highlight_focus=highlights,
            avoid_topics=avoids,
            formatting_preferences={"style": "structured", "length": "detailed"},
            archetype=ArchetypeBase.OPERATOR,
            profile=profile,
        )

    def _generate_guardian_persona(self, profile: PsychometricProfile) -> ReaderPersona:
        """Generate guardian persona.

        Args:
            profile: Psychometric profile

        Returns:
            Guardian reader persona
        """
        if profile.bureaucracy_level > 0.7:
            title = "The Risk-Averse Enterprise Gatekeeper"
            tone = "Use formal language. Emphasize governance and compliance."
            highlights = ["Compliance", "Security", "Stability", "Risk Management"]
            avoids = ["Hacks", "Shortcuts", "Unproven tech"]
        else:
            title = "The Prudent Steward"
            tone = "Balance innovation with responsibility. Show careful decision-making."
            highlights = ["Reliability", "Best Practices", "Quality", "Due Diligence"]
            avoids = ["Risky experiments", "Unstructured approaches"]

        return ReaderPersona(
            title=title,
            tone_instruction=tone,
            highlight_focus=highlights,
            avoid_topics=avoids,
            formatting_preferences={"style": "formal", "length": "thorough"},
            archetype=ArchetypeBase.GUARDIAN,
            profile=profile,
        )

    def _generate_scaler_persona(self, profile: PsychometricProfile) -> ReaderPersona:
        """Generate scaler persona.

        Args:
            profile: Psychometric profile

        Returns:
            Scaler reader persona
        """
        if profile.risk_tolerance > 0.6:
            title = "The Growth Accelerator"
            tone = "Focus on rapid growth and scaling achievements."
            highlights = ["Growth", "Scale", "Hiring", "Metrics"]
            avoids = ["Slow processes", "Conservative approaches"]
        else:
            title = "The Sustainable Builder"
            tone = "Emphasize sustainable growth and team building."
            highlights = ["Sustainable Growth", "Team Building", "Process", "Leadership"]
            avoids = ["Burnout culture", "Growth at all costs"]

        return ReaderPersona(
            title=title,
            tone_instruction=tone,
            highlight_focus=highlights,
            avoid_topics=avoids,
            formatting_preferences={"style": "results-oriented", "length": "impact-focused"},
            archetype=ArchetypeBase.SCALER,
            profile=profile,
        )

    def _generate_default_persona(self, profile: PsychometricProfile) -> ReaderPersona:
        """Generate default persona fallback.

        Args:
            profile: Psychometric profile

        Returns:
            Default reader persona
        """
        return ReaderPersona(
            title="The Professional Evaluator",
            tone_instruction="Use clear, professional language. Focus on results.",
            highlight_focus=["Results", "Impact", "Skills", "Experience"],
            avoid_topics=["Jargon", "Fluff"],
            formatting_preferences={"style": "professional", "length": "balanced"},
            archetype=profile.dominant_archetype,
            profile=profile,
        )

    def route_resume(self, jd_text: str) -> ReaderPersona:
        """Route resume based on JD analysis.

        Args:
            jd_text: Job description text

        Returns:
            Reader persona for resume customization
        """
        return self.analyze_jd(jd_text)

    def get_prompt_template(self, persona: ReaderPersona) -> str:
        """Get prompt template for a persona.

        Args:
            persona: Reader persona

        Returns:
            Prompt template string
        """
        template = f"""
You are writing a resume for {persona.title}.

Tone Instructions:
{persona.tone_instruction}

Key Areas to Highlight:
{", ".join(persona.highlight_focus)}

Topics to Avoid:
{", ".join(persona.avoid_topics) if persona.avoid_topics else "None"}

Formatting Preferences:
{", ".join(f"{k}: {v}" for k, v in persona.formatting_preferences.items())}

Remember: This reader has the following psychometric profile:
- Risk Tolerance: {persona.profile.risk_tolerance:.2f}
- Technical Depth: {persona.profile.technical_depth:.2f}
- Bureaucracy Level: {persona.profile.bureaucracy_level:.2f}
- Archetype: {persona.archetype.value}

Tailor the resume accordingly.
        """.strip()

        return template


# Global router instance
_persona_router: PersonaRouter | None = None


def get_persona_router() -> PersonaRouter:
    """Get global persona router instance.

    Returns:
        PersonaRouter instance
    """
    global _persona_router
    if _persona_router is None:
        _persona_router = PersonaRouter()
    return _persona_router


# Convenience function
def analyze_job_description(jd_text: str) -> ReaderPersona:
    """Analyze job description and return reader persona.

    Args:
        jd_text: Job description text

    Returns:
        Generated reader persona
    """
    router = get_persona_router()
    return router.analyze_jd(jd_text)
