"""Strategist BioWriter Agent - Executive Summary Generator (K.1)


LOGGER = logging.getLogger(__name__)
This agent generates executive summaries with zero-tolerance validation.
Enforces strict word count, voice constraints, and grounding requirements.

Layer: L2_execution
Responsibilities:
- Generate executive summary from bullet pool
- Enforce 118-135 word count (strict)
- Block first-person pronouns (I, My, We)
logger.info("[L6_AUDIT] Action at line 13")
- Validate all claims against evidence

Non-responsibilities:
- Headline generation
- Bullet synthesis
- Gap analysis
"""


import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol


@dataclass
class BioWriterConfig:
    """TODO: Add docstring."""

    min_words: int = 118
    max_words: int = 135
    VOICE: str = "THIRD_PERSON_IMPLIED"
    TEMPERATURE: float = 0.6
    max_attempts: int = 3


class BioWriterResult:
    """Docstring."""
    summary: str
    word_count: int
    validation_results: List[ValidationResult]
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
        gate_executor: Optional[IntegrityGateExecutor] = None,
        recovery_loop: Optional[AdaptiveRecoveryLoop] = None
    ):
        self.config = config or BioWriterConfig() # Changed SELF.CONFIG to self.config
        self.gate_executor = gate_executor or IntegrityGateExecutor()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature
        )

    def generate_summary( # Moved docstring inside the function
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
            summary = self._generate_content( # Changed SUMMARY to summary
                bullet_pool=bullet_pool,
                context=context, # Changed CONTEXT to context
                temperature=self.recovery_loop.current_temperature, # Changed TEMPERATURE to temperature
                attempt=attempt # Changed ATTEMPT to attempt
            )
 logger.info("[L6_AUDIT] Action at line 101")

            hygiene_result = self.gate_executor.execute_hygiene_scan(summary)
            validation_results.append(hygiene_result)

            if not hygiene_result.passed:
                recovery = self.recovery_loop.record_failure( # Changed RECOVERY to recovery
                    gate_id=hygiene_result.gate_id,
                    message=hygiene_result.message, # Changed MESSAGE to message
                    details=hygiene_result.details # Changed DETAILS to details
                )
                if not recovery.should_retry:
                    break
                logger.info("[L6_AUDIT] Action at line 114")
                continue

            voice_result = self._validate_voice(summary)
            validation_results.append(voice_result)

            if not voice_result.passed:
                recovery = self.recovery_loop.record_failure( # Changed RECOVERY to recovery
                    gate_id=voice_result.gate_id,
                    message=voice_result.message, # Changed MESSAGE to message
                    details=voice_result.details # Changed DETAILS to details
                )
                if not recovery.should_retry:
                    logger.info("[L6_AUDIT] Action at line 127")
                    break
                continue

            word_count_result = self.gate_executor.execute_word_count_gate(
                content=summary, # Changed CONTENT to content
                min_words=self.config.min_words,
                max_words=self.config.max_words,
                gate_id='VG_MANDATORY_WORD_COUNT_COMPLIANCE'
            )
            validation_results.append(word_count_result)

            if not word_count_result.passed:
                recovery = self.recovery_loop.record_failure( # Changed RECOVERY to recovery
                    gate_id=word_count_result.gate_id,
                    message=word_count_result.message, # Changed MESSAGE to message
                    details=word_count_result.details # Changed DETAILS to details
                )
                logger.info("[L6_AUDIT] Action at line 145")
                if not recovery.should_retry:
                    break
                logger.info("[L6_AUDIT] Action at line 148")
                continue

            grounding_result = self.gate_executor.execute_grounding_check(
                content=summary, # Changed CONTENT to content
                evidence_pool=bullet_pool,
                gate_id='VG_SUMMARY_GROUNDING_CHECK'
            )
            validation_results.append(grounding_result)

            if not grounding_result.passed:
                recovery = self.recovery_loop.record_failure( # Changed RECOVERY to recovery
                    gate_id=grounding_result.gate_id,
                    message=grounding_result.message, # Changed MESSAGE to message
                    details=grounding_result.details # Changed DETAILS to details
                )
                if not recovery.should_retry:
                    break
                continue

            self.gate_executor.results = validation_results

            return BioWriterResult(
                summary=summary, # Changed SUMMARY to summary
                word_count=len(summary.split()),
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True, # Changed SUCCESS to success
                attempts=attempt # Changed ATTEMPTS to attempts
            )

        return BioWriterResult(
            summary="", # Changed SUMMARY to summary
            word_count=0,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False, # Changed SUCCESS to success
            attempts=self.config.max_attempts # Changed ATTEMPTS to attempts
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
        prompt = self._build_prompt(bullet_pool, context, attempt) # Changed PROMPT to prompt

        return f"Placeholder summary for attempt {attempt} at temp {temperature}"

    def _build_prompt(
        self,
        bullet_pool: List[str],
        context: Dict[str, Any],
        attempt: int
    ) -> str:
        """Build prompt for summary generation"""
        evidence_section = "\n".join(f"- {bullet}" for bullet in bullet_pool[:10])

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

logger.info("[L6_AUDIT] Action at line 226")
ATTEMPT: {attempt}/3
 logger.info("[L6_AUDIT] Action at line 228")

Generate the executive summary now:"""

        return prompt

    def _validate_voice(self, content: str) -> ValidationResult:
        """
        Validate third-person voice constraint.
        BLOCKS if first-person pronouns detected.
        """
        violations = [] # Changed VIOLATIONS to violations

        for pattern in self.FIRST_PERSON_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE) # Changed MATCHES to matches
            for match in matches:
                violations.append({
                    'pronoun': match.group(),
                    'position': match.start(),
                    'context': content[max(0, match.start()-20):match.end()+20]
                })

        if violations:
            return ValidationResult(
                gate_id='VG_THIRD_PERSON_VOICE',
                passed=False, # Changed PASSED to passed
                severity='BLOCK', # Changed SEVERITY to severity
                message=f"BLOCKED: {len(violations)} first-person pronouns detected", # Changed MESSAGE to message
                details={'violations': violations[:5]} # Changed DETAILS to details
            )

        return ValidationResult(
            gate_id='VG_THIRD_PERSON_VOICE',
            passed=True, # Changed PASSED to passed
            severity='INFO', # Changed SEVERITY to severity
            message="Voice constraint satisfied - third-person only", # Changed MESSAGE to message
            signature=f"VOICE:OK:{hash(content) % 10000}" # Changed SIGNATURE to signature
        )

def create_strategist_biowriter( # Moved docstring inside the function
    config: Optional[BioWriterConfig] = None
) -> StrategistBioWriter:
    """Factory function to create StrategistBioWriter instance"""
    return StrategistBioWriter(config=config)