"""Executive Title Composer (K.4) - Industry-First Headline Generation.

This agent generates professional headlines with strict Industry-First positioning,
enforcing 8-13 word total count and ≤90 character limit with technology keyword
blocking in Segment 1.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from runtime.shared.agent_base import Agent, ReasoningConfig


logger = logging.getLogger(__name__)


@dataclass
class ExecutiveTitleOutput:
    """Executive title composer output."""
    headline: str
    segment_1: str  # Industry/Domain
    segment_2: str  # Leadership/Role
    segment_3: str  # Value Proposition
    total_words: int
    total_chars: int
    industry_first_compliant: bool
    metadata: Dict[str, Any]


# Technology keywords forbidden in Segment 1 (Industry-First enforcement)
TECHNOLOGY_KEYWORDS_FORBIDDEN_SEGMENT_1 = [
    "AI", "ML", "Python", "Java", "Cloud", "AWS", "GCP", "Azure",
    "Kubernetes", "Docker", "React", "Angular", "Node.js", "TensorFlow",
    "PyTorch", "Spark", "Kafka", "Redis", "MongoDB", "PostgreSQL",
    "API", "REST", "GraphQL", "Microservices", "DevOps", "CI/CD",
]


class Executive_Title_Composer(Agent):
    """K.4 specialist agent for headline generation with Industry-First positioning.
    
    This agent generates headlines with:
    - Industry-First positioning (no technology in Segment 1)
    - 8-13 words total (ZERO TOLERANCE)
    - ≤90 characters (ZERO TOLERANCE)
    - 3-segment structure: Domain | Leadership | Value Prop
    - BLOCK on technology keywords in Segment 1
    """
    
    def __init__(
        self,
        config: ReasoningConfig,
        word_count_min: int = 8,
        word_count_max: int = 13,
        char_limit: int = 90,
    ):
        """Initialize Executive Title Composer.
        
        Args:
            config: Reasoning configuration
            word_count_min: Minimum total words (default 8)
            word_count_max: Maximum total words (default 13)
            char_limit: Maximum characters (default 90)
        """
        super().__init__(config, k_node_id="K.4", element="Executive Title")
        
        self.word_count_min = word_count_min
        self.word_count_max = word_count_max
        self.char_limit = char_limit
        
        logger.info(
            f"Executive_Title_Composer initialized: "
            f"words={word_count_min}-{word_count_max}, chars≤{char_limit}"
        )
    
    async def execute(self, context: Dict[str, Any]) -> ExecutiveTitleOutput:
        """Execute K.4 headline generation.
        
        Args:
            context: Execution context with:
                - target_industry: str - Target industry/domain
                - leadership_level: str - Leadership level
                - value_proposition: str - Key value proposition
                - job_title: str - Target job title
                - regeneration_feedback: Optional[str]
                
        Returns:
            ExecutiveTitleOutput with headline and segments
        """
        logger.info("Executing K.4 Executive Title Composer")
        
        # Extract context
        target_industry = context.get("target_industry", "")
        leadership_level = context.get("leadership_level", "")
        value_proposition = context.get("value_proposition", "")
        job_title = context.get("job_title", "")
        regeneration_feedback = context.get("regeneration_feedback")
        
        # Build prompt
        if regeneration_feedback:
            prompt = self._build_regeneration_prompt(context, regeneration_feedback)
        else:
            prompt = self._build_initial_prompt(
                target_industry, leadership_level, value_proposition, job_title
            )
        
        # Generate headline
        response = await self._call_llm(prompt)
        headline = response.strip()
        
        # Parse segments
        segments = self._parse_segments(headline)
        segment_1 = segments[0] if len(segments) > 0 else ""
        segment_2 = segments[1] if len(segments) > 1 else ""
        segment_3 = segments[2] if len(segments) > 2 else ""
        
        # Calculate metrics
        total_words = len(headline.replace("|", "").split())
        total_chars = len(headline)
        
        # Check Industry-First compliance
        industry_first_compliant = self._check_industry_first(segment_1)
        
        # Build output
        output = ExecutiveTitleOutput(
            headline=headline,
            segment_1=segment_1.strip(),
            segment_2=segment_2.strip(),
            segment_3=segment_3.strip(),
            total_words=total_words,
            total_chars=total_chars,
            industry_first_compliant=industry_first_compliant,
            metadata={
                "k_node_id": self.k_node_id,
                "temperature": self.config.temperature,
                "word_count_range": f"{self.word_count_min}-{self.word_count_max}",
                "char_limit": self.char_limit,
            },
        )
        
        logger.info(
            f"K.4 generation complete: {total_words} words, {total_chars} chars, "
            f"Industry-First={industry_first_compliant}"
        )
        
        return output
    
    def _build_initial_prompt(
        self,
        target_industry: str,
        leadership_level: str,
        value_proposition: str,
        job_title: str,
    ) -> str:
        """Build initial generation prompt.
        
        Args:
            target_industry: Target industry/domain
            leadership_level: Leadership level
            value_proposition: Value proposition
            job_title: Target job title
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Generate a professional LinkedIn headline with INDUSTRY-FIRST positioning.

CRITICAL CONSTRAINTS (ZERO TOLERANCE):
1. Total words: {self.word_count_min}-{self.word_count_max} words (STRICT)
2. Total characters: ≤{self.char_limit} characters (STRICT)
3. 3-segment structure: Domain | Leadership | Value Prop
4. Segment 1 (Domain): MUST be industry/domain - NO technology keywords
5. Use pipe (|) as separator between segments

INDUSTRY-FIRST POSITIONING:
- Segment 1: Industry/Domain (e.g., "Healthcare AI", "Financial Services", "Enterprise SaaS")
- Segment 2: Leadership/Role (e.g., "Engineering Leader", "VP of Product")
- Segment 3: Value Proposition (e.g., "Scaling Teams & Systems", "Driving Innovation")

FORBIDDEN in Segment 1:
{', '.join(TECHNOLOGY_KEYWORDS_FORBIDDEN_SEGMENT_1[:10])}

TARGET CONTEXT:
- Industry: {target_industry}
- Leadership Level: {leadership_level}
- Value Proposition: {value_proposition}
- Job Title: {job_title}

EXAMPLES:
- "Healthcare AI | Engineering Leader | Scaling ML Systems at Enterprise Scale" (11 words, 76 chars)
- "Financial Services | VP of Engineering | Building High-Performance Teams" (10 words, 74 chars)
- "Enterprise SaaS | Chief Technology Officer | Driving Product Innovation" (10 words, 72 chars)

Generate the headline now (use | as separator):
"""
        
        return prompt
    
    def _build_regeneration_prompt(
        self,
        context: Dict[str, Any],
        feedback: str,
    ) -> str:
        """Build regeneration prompt with validation feedback.
        
        Args:
            context: Original context
            feedback: Validation feedback
            
        Returns:
            Regeneration prompt
        """
        previous_headline = context.get("previous_headline", "")
        
        prompt = f"""REGENERATION REQUIRED

{feedback}

PREVIOUS HEADLINE:
{previous_headline}

CONSTRAINTS:
- Total words: {self.word_count_min}-{self.word_count_max} (STRICT)
- Total characters: ≤{self.char_limit} (STRICT)
- Segment 1: NO technology keywords (Industry-First)
- Use | as separator

Generate the corrected headline:
"""
        
        return prompt
    
    def _parse_segments(self, headline: str) -> List[str]:
        """Parse headline into 3 segments.
        
        Args:
            headline: Full headline
            
        Returns:
            List of 3 segments
        """
        segments = headline.split("|")
        
        # Ensure exactly 3 segments
        while len(segments) < 3:
            segments.append("")
        
        return segments[:3]
    
    def _check_industry_first(self, segment_1: str) -> bool:
        """Check Industry-First compliance.
        
        Segment 1 must NOT contain technology keywords.
        
        Args:
            segment_1: First segment (Domain)
            
        Returns:
            True if compliant, False if technology keywords found
        """
        segment_1_upper = segment_1.upper()
        
        for keyword in TECHNOLOGY_KEYWORDS_FORBIDDEN_SEGMENT_1:
            if keyword.upper() in segment_1_upper:
                logger.warning(
                    f"Industry-First violation: Technology keyword '{keyword}' "
                    f"found in Segment 1: '{segment_1}'"
                )
                return False
        
        return True
