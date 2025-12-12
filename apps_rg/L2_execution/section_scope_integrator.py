"""Section Scope Integrator Agent - Overview Synthesis (K.5B & K.6B)

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

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from runtime.shared.integrity_gate_executor import IntegrityGateExecutor, ValidationResult
from runtime.shared.adaptive_recovery_loop import AdaptiveRecoveryLoop


@dataclass
class SectionIntegratorConfig:
    max_similarity_threshold: float = 0.75
    temperature: float = 0.6
    max_attempts: int = 3


@dataclass
class SectionIntegratorResult:
    overview: str
    similarity_score: float
    validation_results: List[ValidationResult]
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
        gate_executor: Optional[IntegrityGateExecutor] = None,
        recovery_loop: Optional[AdaptiveRecoveryLoop] = None
    ):
        self.config = config or SectionIntegratorConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutor()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature
        )
        
    def generate_overview(
        self,
        bullets: List[str],
        master_baseline: str,
        context: Dict[str, Any]
    ) -> SectionIntegratorResult:
        """
        Generate section overview with anti-prefix and deduplication validation.
        
        Args:
            bullets: Generated achievement bullets
            master_baseline: Master baseline for similarity comparison
            context: Additional context (role, company, etc.)
            
        Returns:
            SectionIntegratorResult with overview and validation details
        """
        self.recovery_loop.reset(self.config.temperature)
        validation_results = []
        
        for attempt in range(1, self.config.max_attempts + 1):
            overview = self._generate_content(
                bullets=bullets,
                context=context,
                temperature=self.recovery_loop.current_temperature,
                attempt=attempt
            )
            
            hygiene_result = self.gate_executor.execute_hygiene_scan(overview)
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
            
            prefix_result = self._validate_no_redundant_prefix(overview)
            validation_results.append(prefix_result)
            
            if not prefix_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=prefix_result.gate_id,
                    message=prefix_result.message,
                    details=prefix_result.details
                )
                if not recovery.should_retry:
                    break
                continue
            
            similarity_score = self._calculate_similarity(overview, master_baseline)
            
            dedup_result = self._validate_deduplication(overview, similarity_score)
            validation_results.append(dedup_result)
            
            if not dedup_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=dedup_result.gate_id,
                    message=dedup_result.message,
                    details=dedup_result.details
                )
                if not recovery.should_retry:
                    break
                continue
            
            self.gate_executor.results = validation_results
            
            return SectionIntegratorResult(
                overview=overview,
                similarity_score=similarity_score,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True,
                attempts=attempt
            )
        
        return SectionIntegratorResult(
            overview="",
            similarity_score=1.0,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False,
            attempts=self.config.max_attempts
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
        return "Directed strategic technology initiatives across cloud infrastructure and data engineering, delivering scalable solutions that drove measurable business impact and operational excellence."
    
    def _validate_no_redundant_prefix(self, overview: str) -> ValidationResult:
        """
        Validate overview does not begin with redundant role prefix.
        BLOCKS if forbidden prefix detected.
        """
        for pattern in self.FORBIDDEN_PREFIXES:
            match = re.match(pattern, overview, re.IGNORECASE)
            if match:
                return ValidationResult(
                    gate_id='VG_OVERVIEW_ANTI_PREFIX',
                    passed=False,
                    severity='BLOCK',
                    message=f"BLOCKED: Overview begins with redundant prefix: '{match.group()}'",
                    details={
                        'matched_pattern': pattern,
                        'matched_text': match.group(),
                        'overview_preview': overview[:100]
                    }
                )
        
        return ValidationResult(
            gate_id='VG_OVERVIEW_ANTI_PREFIX',
            passed=True,
            severity='INFO',
            message="No redundant prefix detected",
            signature=f"ANTIPREFIX:OK"
        )
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts.
        Uses word overlap ratio as heuristic.
        """
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1 & words2)
        union = len(words1 | words2)
        
        return overlap / union if union > 0 else 0.0
    
    def _validate_deduplication(
        self,
        overview: str,
        similarity_score: float
    ) -> ValidationResult:
        """
        Validate overview is <75% similar to master baseline.
        STRICT LESS THAN policy (not ≤).
        """
        if similarity_score < self.config.max_similarity_threshold:
            return ValidationResult(
                gate_id='VG_OVERVIEW_DEDUPLICATION',
                passed=True,
                severity='INFO',
                message=f"Deduplication passed: {similarity_score:.1%} similarity (threshold: <{self.config.max_similarity_threshold:.0%})",
                signature=f"DEDUP:OK:{int(similarity_score*100)}",
                details={'similarity_score': similarity_score, 'threshold': self.config.max_similarity_threshold}
            )
        
        return ValidationResult(
            gate_id='VG_OVERVIEW_DEDUPLICATION',
            passed=False,
            severity='BLOCK',
            message=f"BLOCKED: Overview similarity {similarity_score:.1%} >= threshold {self.config.max_similarity_threshold:.0%}",
            details={
                'similarity_score': similarity_score,
                'threshold': self.config.max_similarity_threshold,
                'policy': 'STRICT_LESS_THAN'
            }
        )


def create_section_scope_integrator(
    config: Optional[SectionIntegratorConfig] = None
) -> SectionScopeIntegrator:
    """Factory function to create SectionScopeIntegrator instance"""
    return SectionScopeIntegrator(config=config)
