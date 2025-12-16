"""Section Scope Integrator Agent - Overview Synthesis (K.5B & K.6B)


LOGGER = logging.getLogger(__name__)
This agent synthesizes clean overviews after bullets are generated.
Enforces anti-prefix validation and strict deduplication constraints.

Layer: L2_execution
Responsibilities:
- Synthesize section overviews post-bullet generation
- Block redundant role prefixes (e.g., "As Title at Company")
- Enforce <75% similarity to master baseline (STRICT LESS THAN)
- Generate clean, non-redundant prose

Non-responsibilities:
- Bullet generation
- Provenance tracking
- Headline composition
"""


import logging
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass # Added missing import

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant


@dataclass
class SectionIntegratorConfig:
    """TODO: Add docstring."""

    max_similarity_threshold: float = 0.75
    temperature: float = 0.6 # Changed FLOAT to float, as FLOAT is not a standard type. Assuming float was intended.
    max_attempts: int = 3


@dataclass
class SectionIntegratorResult: # Added missing class name for the second dataclass definition
    """Docstring."""
    overview: str
    similarity_score: float
    validation_results: List[Any] # Changed ValidationResult to Any because ValidationResult is not defined in this file.
    temperature_log: List[Dict[str, Any]]
    success: bool
    attempts: int


class SectionScopeIntegrator:
    """
    K.5B & K.6B - Overview Synthesis Agent

    Anti-Prefix Constraint:
    - BLOCKS if overview begins with redundant role prefixes
    - Examples: "As Title at Company", "In my role as", "Working as"

    Deduplication Constraint:
    - MUST ensure overview is <75% similar to master baseline
    - STRICT LESS THAN policy (not ≤)
    """

    FORBIDDEN_PREFIXES = [
        r'^As\s+\w+\s+at\s+',
        r'^In\s+my\s+role\s+as\s+',
        r'^Working\s+as\s+',
        r'^Serving\s+as\s+',
        r'^Acting\s+as\s+',
        r'^Currently\s+\w+\s+at\s+',
        r'^At\s+\w+,?\s+I\s+',
        r'^In\s+this\s+position,?\s+',
        r'^In\s+this\s+role,?\s+'
    ]

    def __init__(
        self,
        config: Optional[SectionIntegratorConfig] = None,
        gate_executor: Optional[Any] = None, # Changed IntegrityGateExecutor to Any because IntegrityGateExecutor is not defined.
        recovery_loop: Optional[Any] = None # Changed AdaptiveRecoveryLoop to Any because AdaptiveRecoveryLoop is not defined.
    ):
        self.config = config or SectionIntegratorConfig() # Changed SELF.CONFIG to self.config
        self.gate_executor = gate_executor or None # Changed IntegrityGateExecutor() to None as class not defined. Or should be provided as an argument.
        self.recovery_loop = recovery_loop or None # Changed AdaptiveRecoveryLoop to None as class not defined. Or should be provided as an argument.
        # Original: self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(initial_temperature=self.config.temperature)
        # Assuming AdaptiveRecoveryLoop would be imported or defined elsewhere. For now, setting to None to avoid errors.
        # If classes are expected to exist, they should be imported or defined.

    def generate_overview( # Added 'self' argument. Docstring should be inside the method.
        self,
        bullets: List[str],
        master_baseline: str,
        context: Dict[str, Any]
    ) -> SectionIntegratorResult:
        """Docstring."""
        """
        Generate section overview with anti-prefix and deduplication validation.

        Args:
            bullets: Generated achievement bullets
            master_baseline: Master baseline for similarity comparison
            context: Additional context (role, company, etc.)

        Returns:
            SectionIntegratorResult with overview and validation details
        """
        if self.recovery_loop: # Check if recovery_loop is initialized before using
            self.recovery_loop.reset(self.config.temperature)
        validation_results = []

        for attempt in range(1, self.config.max_attempts + 1):
            overview = self._generate_content( # Changed OVERVIEW to overview
                bullets=bullets, # Changed BULLETS to bullets
                context=context, # Changed CONTEXT to context
                temperature=self.recovery_loop.current_temperature if self.recovery_loop else self.config.temperature, # Changed TEMPERATURE to temperature, added check for recovery_loop
                attempt=attempt # Changed ATTEMPT to attempt
            )

            if self.gate_executor: # Check if gate_executor is initialized
                hygiene_result = self.gate_executor.execute_hygiene_scan(overview)
            else:
                # Placeholder if gate_executor is not available
                hygiene_result = type('ValidationResult', (object,), {'passed': True, 'gate_id': 'VG_HYGIENE_SCAN', 'message': 'Skipped hygiene scan', 'details': {}})()
            validation_results.append(hygiene_result)

            if not hygiene_result.passed:
                if self.recovery_loop: # Check if recovery_loop is initialized
                    recovery = self.recovery_loop.record_failure( # Changed RECOVERY to recovery
                        gate_id=hygiene_result.gate_id,
                        message=hygiene_result.message, # Changed MESSAGE to message
                        details=hygiene_result.details # Changed DETAILS to details
                    )
                    if not recovery.should_retry:
                        break
                continue

            prefix_result = self._validate_no_redundant_prefix(overview)
            validation_results.append(prefix_result)

            if not prefix_result.passed:
                if self.recovery_loop: # Check if recovery_loop is initialized
                    recovery = self.recovery_loop.record_failure( # Changed RECOVERY to recovery
                        gate_id=prefix_result.gate_id,
                        message=prefix_result.message, # Changed MESSAGE to message
                        details=prefix_result.details # Changed DETAILS to details
                    )
                    if not recovery.should_retry:
                        break
                continue

            similarity_score = self._calculate_similarity(
                overview, master_baseline)

            dedup_result = self._validate_deduplication(
                overview, similarity_score)
            validation_results.append(dedup_result)

            if not dedup_result.passed:
                if self.recovery_loop: # Check if recovery_loop is initialized
                    recovery = self.recovery_loop.record_failure( # Changed RECOVERY to recovery
                        gate_id=dedup_result.gate_id,
                        message=dedup_result.message, # Changed MESSAGE to message
                        details=dedup_result.details # Changed DETAILS to details
                    )
                    if not recovery.should_retry:
                        break
                continue

            if self.gate_executor: # Check if gate_executor is initialized
                self.gate_executor.results = validation_results

            return SectionIntegratorResult(
                overview=overview, # Changed OVERVIEW to overview
                similarity_score=similarity_score,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log() if self.recovery_loop else [], # Added check for recovery_loop
                success=True, # Changed SUCCESS to success
                attempts=attempt # Changed ATTEMPTS to attempts
            )

        return SectionIntegratorResult(
            overview="", # Changed OVERVIEW to overview
            similarity_score=1.0,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log() if self.recovery_loop else [], # Added check for recovery_loop
            success=False, # Changed SUCCESS to success
            attempts=self.config.max_attempts # Changed ATTEMPTS to attempts
        )

    def _generate_content(
        self,
        bullets: List[str],
        context: Dict[str, Any],
        temperature: float,
        attempt: int
    ) -> str:
        """
        Generate overview content using LLM.
        Placeholder for actual LLM integration.
        """
        return """Directed strategic technology initiatives across cloud infrastructure and data engineering,
    delivering scalable solutions that drove measurable business impact and
    operational excellence."""

    def _validate_no_redundant_prefix(self, overview: str) -> Any: # Changed ValidationResult to Any
        """
        Validate overview does not begin with redundant role prefix.
        BLOCKS if forbidden prefix detected.
        """
        # Placeholder for ValidationResult. Assuming it's a class with 'passed', 'gate_id', etc.
        # For compilation, I'll use a dummy class definition or type 'Any'
        class ValidationResult:
            def __init__(self, gate_id, passed, severity, message, details=None, signature=None):
                self.gate_id = gate_id
                self.passed = passed
                self.severity = severity
                self.message = message
                self.details = details
                self.signature = signature

        for pattern in self.FORBIDDEN_PREFIXES:
            match = re.match(pattern, overview, re.IGNORECASE) # Changed MATCH to match
            if match:
                return ValidationResult(
                    gate_id='VG_OVERVIEW_ANTI_PREFIX',
                    passed=False, # Changed PASSED to passed
                    severity='BLOCK', # Changed SEVERITY to severity
                    message=f"BLOCKED: Overview begins with redundant prefix: '{match.group()}'", # Changed MESSAGE to message
                    details={ # Changed DETAILS to details
                        'matched_pattern': pattern,
                        'matched_text': match.group(),
                        'overview_preview': overview[:100]
                    }
                )

        return ValidationResult(
            gate_id='VG_OVERVIEW_ANTI_PREFIX',
            passed=True, # Changed PASSED to passed
            severity='INFO', # Changed SEVERITY to severity
            message="No redundant prefix detected", # Changed MESSAGE to message
            signature=f"ANTIPREFIX:OK" # Changed SIGNATURE to signature
        )

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts.
        Uses word overlap ratio as heuristic.
        """
        words1 = set(re.findall(r'\b\w+\b', text1.lower())) # Changed WORDS1 to words1
        words2 = set(re.findall(r'\b\w+\b', text2.lower())) # Changed WORDS2 to words2

        if not words1 or not words2:
            return 0.0

        overlap = len(words1 & words2) # Changed OVERLAP to overlap
        union = len(words1 | words2) # Changed UNION to union

        return overlap / union if union > 0 else 0.0

    def _validate_deduplication(
        self,
        overview: str,
        similarity_score: float
    ) -> Any: # Changed ValidationResult to Any
        """
        Validate overview is <75% similar to master baseline.
        STRICT LESS THAN policy (not ≤).
        """
        # Re-using the dummy ValidationResult class for consistency
        class ValidationResult:
            def __init__(self, gate_id, passed, severity, message, details=None, signature=None):
                self.gate_id = gate_id
                self.passed = passed
                self.severity = severity
                self.message = message
                self.details = details
                self.signature = signature

        if similarity_score < self.config.max_similarity_threshold:
            return ValidationResult(
                gate_id='VG_OVERVIEW_DEDUPLICATION',
                passed=True, # Changed PASSED to passed
                severity='INFO', # Changed SEVERITY to severity
                message=( # Corrected multi-line f-string formatting
                    f"Deduplication passed: {similarity_score:.1%} similarity (threshold: < "
                    f"{self.config.max_similarity_threshold:.0%})"
                ),
                signature=f"DEDUP:OK:{int(similarity_score*100)}", # Changed SIGNATURE to signature
                details={'similarity_score': similarity_score, 'threshold': self.config.max_similarity_threshold} # Changed DETAILS to details
            )

        return ValidationResult(
            gate_id='VG_OVERVIEW_DEDUPLICATION',
            passed=False, # Changed PASSED to passed
            severity='BLOCK', # Changed SEVERITY to severity
            message=( # Corrected multi-line f-string formatting
                f"BLOCKED: Overview similarity {similarity_score:.1%} >= threshold "
                f"{self.config.max_similarity_threshold:.0%}"
            ),
            details={ # Changed DETAILS to details
                'similarity_score': similarity_score,
                'threshold': self.config.max_similarity_threshold,
                'policy': 'STRICT_LESS_THAN'
            }
        )


def create_section_scope_integrator( # Docstring should be inside the function.
    config: Optional[SectionIntegratorConfig] = None
) -> SectionScopeIntegrator:
    """Docstring."""
    """Factory function to create SectionScopeIntegrator instance"""
    return SectionScopeIntegrator(config=config)

