"""Strategist BioWriter Agent - Executive Summary Generator (K.1)


LOGGER = logging.getLogger(__name__)
This agent generates executive summaries with zero-tolerance validation.
Enforces strict word count, voice constraints, and grounding requirements.

Layer: L2_execution
Responsibilities:
- Generate executive summary from bullet pool
- Enforce 118-135 word count (strict)
- Block first-person pronouns (I, My, We)
- Validate all claims against evidence

Non-responsibilities:
- Headline generation
- Bullet synthesis
- Gap analysis
"""


import logging
import re
from typing import Any, Dict, List, Optional

from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BioWriterConfig:
    """TODO: Add docstring."""

    min_words: int = 118
    max_words: int = 135
    VOICE: str = "THIRD_PERSON_IMPLIED"
    TEMPERATURE: float = 0.6
    max_attempts: int = 3


@dataclass
class BioWriterResult:
    """Docstring."""
    summary: str
    word_count: int
    validation_results: List[Any]
    temperature_log: List[Dict[str, Any]]
    success: bool
    attempts: int


class StrategistBioWriter:
    """
    K.1 - Executive Summary Generator

    Zero Tolerance Constraints:
    - Length: Strict 118-135 words
    - Voice: Third-Person Implied ONLY (block I/My/We)
    - Grounding: All claims must exist in Bullet_Pool
    """

    FIRST_PERSON_PATTERNS = [
        r'\bI\b', r'\bmy\b', r'\bme\b', r'\bmine\b',
        r'\bwe\b', r'\bour\b', r'\bus\b', r'\bours\b'
    ]

    def __init__(
        self,
        config: Optional[BioWriterConfig] = None,
        gate_executor: Optional[Any] = None,
        recovery_loop: Optional[Any] = None
    ):
        self.config = config or BioWriterConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutor()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature
        )

    def generate_summary(
        self,
        bullet_pool: List[str],
        context: Dict[str, Any]
    ) -> BioWriterResult:
        """
        Generate executive summary with validation loop.

        Args:
            bullet_pool: List of achievement bullets for grounding
            context: Additional context (JD, industry, etc.)

        Returns:
            BioWriterResult with summary and validation details
        """
        self.recovery_loop.reset(self.config.temperature)
        validation_results = []

        for attempt in range(1, self.config.max_attempts + 1):
            summary = self._generate_content(
                bullet_pool=bullet_pool,
                context=context,
                temperature=self.recovery_loop.current_temperature,
                attempt=attempt
            )

            hygiene_result = self.gate_executor.execute_hygiene_scan(summary)
            validation_results.append(hygiene_result)

            if not hygiene_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=hygiene_result.gate_id,
                    message=hygiene_result.message,
                    details=hygiene_result.details
                )
                if not recovery.should_retry:
                    break
                continue

            voice_result = self._validate_voice(summary)
            validation_results.append(voice_result)

            if not voice_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=voice_result.gate_id,
                    message=voice_result.message,
                    details=voice_result.details
                )
                if not recovery.should_retry:
                    break
                continue

            word_count_result = self.gate_executor.execute_word_count_gate(
                content=summary,
                min_words=self.config.min_words,
                max_words=self.config.max_words,
                gate_id='VG_MANDATORY_WORD_COUNT_COMPLIANCE'
            )
            validation_results.append(word_count_result)

            if not word_count_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=word_count_result.gate_id,
                    message=word_count_result.message,
                    details=word_count_result.details
                )
                if not recovery.should_retry:
                    break
                continue

            grounding_result = self.gate_executor.execute_grounding_check(
                content=summary,
                evidence_pool=bullet_pool,
                gate_id='VG_SUMMARY_GROUNDING_CHECK'
            )
            validation_results.append(grounding_result)

            if not grounding_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=grounding_result.gate_id,
                    message=grounding_result.message,
                    details=grounding_result.details
                )
                if not recovery.should_retry:
                    break
                continue

            self.gate_executor.results = validation_results

            return BioWriterResult(
                summary=summary,
                word_count=len(summary.split()),
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True,
                attempts=attempt
            )

        return BioWriterResult(
            summary="",
            word_count=0,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False,
            attempts=self.config.max_attempts
        )

    def _generate_content(
        self,
        bullet_pool: List[str],
        context: Dict[str, Any],
        temperature: float,
        attempt: int
    ) -> str:
        """
        Generate summary content using LLM.
        This is a placeholder - actual implementation would call LLM.
        """
        prompt = self._build_prompt(bullet_pool, context, attempt)

        return f"Placeholder summary for attempt {attempt} at temp {temperature}"

    def _build_prompt(
        self,
        bullet_pool: List[str],
        context: Dict[str, Any],
        attempt: int
    ) -> str:
        """Build prompt for summary generation"""
        evidence_section = "\n".join(
            f"- {bullet}" for bullet in bullet_pool[:10])

        prompt = f"""Generate an executive summary for a resume.

STRICT REQUIREMENTS:
1. Word Count: EXACTLY 118-135 words (count carefully)
2. Voice: Third-person implied ONLY (NO "I", "my", "we", "our")
3. Grounding: Every claim must come from the evidence below
4. Style: Professional, specific, achievement-focused

EVIDENCE POOL:
{evidence_section}

TARGET INDUSTRY: {context.get('industry', 'Technology')}
SENIORITY: {context.get('seniority', 'Senior')}

ATTEMPT: {attempt}/3

Generate the executive summary now:"""

        return prompt

    def _validate_voice(self, content: str) -> Any:
        """
        Validate third-person voice constraint.
        BLOCKS if first-person pronouns detected.
        """
        violations = []

        for pattern in self.FIRST_PERSON_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                violations.append({
                    'pronoun': match.group(),
                    'position': match.start(),
                    'context': content[max(0, match.start() - 20):match.end() + 20]
                })

        if violations:
            return ValidationResult(
                gate_id='VG_THIRD_PERSON_VOICE',
                passed=False,
                severity='BLOCK',
                message=f"BLOCKED: {len(violations)} first-person pronouns detected",
                details={'violations': violations[:5]}
            )

        return ValidationResult(
            gate_id='VG_THIRD_PERSON_VOICE',
            passed=True,
            severity='INFO',
            message="Voice constraint satisfied - third-person only",
            signature=f"VOICE:OK:{hash(content) % 10000}"
        )


def create_strategist_biowriter(
    config: Optional[BioWriterConfig] = None
) -> StrategistBioWriter:
    """Factory function to create StrategistBioWriter instance"""
    return StrategistBioWriter(config=config)