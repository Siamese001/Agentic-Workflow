"""K.5 CTA Agent - Route-Specific Call-to-Action Generation.

This agent generates route-specific CTAs with strict character/word limits
and archetype-appropriate phrasing.
"""

import logging


logger = logging.getLogger(__name__)


@dataclass
class K5Output:
    """K.5 CTA output."""

    cta: str
    route: str
    archetype: str
    word_count: int
    char_count: int
    metadata: dict[str, Any]


# Route-specific CTA templates (from outreach_orchestration_config.py)
CTA_TEMPLATES = {
    "CONNECTION_REQ": {
        "template": "Would you be open to a brief chat about {topic}?",
        "word_limit": 5,
        "char_limit": 300,  # Part of overall CONNECTION_REQ 300 char limit
        "examples": [
            "Open to a brief chat?",
            "Available for a quick call?",
            "Interested in connecting?",
        ],
    },
    "INMAIL": {
        "template": "Would you be available for a {duration} call {timeframe} to discuss {topic}?",
        "word_limit": 20,
        "char_limit": None,
        "examples": [
            "Available for a 15-minute call this week to discuss AI strategy?",
            "Open to a brief conversation next week about ML infrastructure?",
        ],
    },
    "SHORT_NEW": {
        "template": "Open to connecting?",
        "word_limit": 10,
        "char_limit": None,  # Part of overall 360-380 char limit
        "examples": [
            "Open to connecting?",
            "Interested in a brief chat?",
        ],
    },
    "FOLLOW_UP": {
        "template": "Following up on {prior_topic} - available for a call {timeframe}?",
        "word_limit": 20,
        "char_limit": None,
        "examples": [
            "Following up on our AI discussion - available this week?",
        ],
    },
}


class K5_CTAAgent(Agent):
    """K.5 specialist agent for CTA generation.

    This agent generates route-specific CTAs with:
    - Strict word/character limits per route
    - Archetype-appropriate phrasing
    - Time-bound explicit asks
    - Connection-only CTAs for CONNECTION_REQ (no meeting ask)
    """

    def __init__(
        self,
        config: ReasoningConfig,
        route: str,
        archetype: str,
    ):
        """Initialize K.5 CTA agent.

        Args:
            config: Reasoning configuration
            route: Message route
            archetype: Recipient archetype
        """
        super().__init__(config, k_node_id="K.5", element="CTA")

        self.route = route
        self.archetype = archetype
        self.template = CTA_TEMPLATES.get(route, CTA_TEMPLATES["INMAIL"])

        logger.info(
            f"K.5 CTA Agent initialized: route={route}, word_limit={self.template['word_limit']}"
        )

    async def execute(self, context: dict[str, Any]) -> K5Output:
        """Execute K.5 CTA generation.

        Args:
            context: Execution context with:
                - topic: str - Discussion topic
                - duration: Optional[str] - Call duration (for INMAIL)
                - timeframe: Optional[str] - Timeframe (for INMAIL/FOLLOW_UP)
                - prior_topic: Optional[str] - Prior topic (for FOLLOW_UP)
                - regeneration_feedback: Optional[str]

        Returns:
            K5Output with CTA
        """
        logger.info(f"Executing K.5 CTA generation for {self.route}")

        # Extract context
        topic = context.get("topic", "your work")
        duration = context.get("duration", "15-minute")
        timeframe = context.get("timeframe", "this week")
        prior_topic = context.get("prior_topic", "our previous discussion")
        regeneration_feedback = context.get("regeneration_feedback")

        # Build prompt
        if regeneration_feedback:
            prompt = self._build_regeneration_prompt(context, regeneration_feedback)
        else:
            prompt = self._build_initial_prompt(topic, duration, timeframe, prior_topic)

        # Generate CTA
        response = await self._call_llm(prompt)
        cta = response.strip()

        # Calculate metrics
        word_count = len(cta.split())
        char_count = len(cta)

        # Build output
        output = K5Output(
            cta=cta,
            route=self.route,
            archetype=self.archetype,
            word_count=word_count,
            char_count=char_count,
            metadata={
                "k_node_id": self.k_node_id,
                "word_limit": self.template["word_limit"],
                "char_limit": self.template["char_limit"],
                "temperature": self.config.temperature,
            },
        )

        logger.info(f"K.5 CTA generation complete: {word_count} words, {char_count} chars")

        return output

    def _build_initial_prompt(
        self,
        topic: str,
        duration: str,
        timeframe: str,
        prior_topic: str,
    ) -> str:
        """Build initial CTA generation prompt.

        Args:
            topic: Discussion topic
            duration: Call duration
            timeframe: Timeframe
            prior_topic: Prior topic (for FOLLOW_UP)

        Returns:
            Formatted prompt
        """
        word_limit = self.template["word_limit"]
        char_limit = self.template["char_limit"]

        # Route-specific instructions
        if self.route == "CONNECTION_REQ":
            route_instructions = """
CRITICAL: CONNECTION_REQ CTAs must be connection-only (no meeting ask).
- Max 5 words
- Part of overall 300 character limit
- Examples: "Open to connecting?", "Interested in a brief chat?"
"""
        elif self.route == "INMAIL":
            route_instructions = f"""
INMAIL CTAs must include:
- Specific duration ({duration})
- Time-bound ask ({timeframe})
- Explicit topic ({topic})
- Max 20 words
"""
        elif self.route == "SHORT_NEW":
            route_instructions = """
SHORT_NEW CTAs must be:
- Connection-only (no meeting ask)
- Max 10 words
- Part of overall 360-380 character limit
"""
        else:  # FOLLOW_UP
            route_instructions = f"""
FOLLOW_UP CTAs must:
- Reference prior topic ({prior_topic})
- Include timeframe ({timeframe})
- Max 20 words
"""

        prompt = f"""Generate a professional CTA for a LinkedIn {self.route} message to a {self.archetype}.

CRITICAL CONSTRAINTS:
- Word limit: {word_limit} words (STRICT)
{f"- Character limit: {char_limit} chars (STRICT)" if char_limit else ""}
- Single sentence
- Explicit ask
- Time-bound (where applicable)

{route_instructions}

EXAMPLES:
{chr(10).join(f"- {ex}" for ex in self.template["examples"])}

Generate the CTA now (single sentence, {word_limit} words max):
"""

        return prompt

    def _build_regeneration_prompt(
        self,
        context: dict[str, Any],
        feedback: str,
    ) -> str:
        """Build regeneration prompt with validation feedback.

        Args:
            context: Original context
            feedback: Validation feedback

        Returns:
            Regeneration prompt
        """
        previous_cta = context.get("previous_cta", "")

        prompt = f"""REGENERATION REQUIRED

{feedback}

PREVIOUS CTA:
{previous_cta}

CONSTRAINTS:
- Word limit: {self.template["word_limit"]} words
{f"- Character limit: {self.template['char_limit']} chars" if self.template["char_limit"] else ""}
- Single sentence
- Explicit ask

Generate the corrected CTA:
"""

        return prompt
