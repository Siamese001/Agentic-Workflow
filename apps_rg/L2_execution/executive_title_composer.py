"""Executive Title Composer Agent - Headline Generator (K.4)

This agent generates resume headlines with industry-first validation.
Enforces GICS sector precedence and strict character limits.

Layer: L2_execution
Responsibilities:
- Generate professional headline with industry-first segment
- Enforce 8-13 word limit and ≤90 character limit
- Validate first segment is GICS sector (not technology)
- Block technology-first headlines

Non-responsibilities:
- Executive summary generation
- Bullet synthesis
- Content grounding
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from runtime.shared.integrity_gate_executor import IntegrityGateExecutor, ValidationResult
from runtime.shared.adaptive_recovery_loop import AdaptiveRecoveryLoop


@dataclass
class TitleComposerConfig:
    min_words: int = 8
    max_words: int = 13
    max_chars: int = 90
    temperature: float = 0.5
    max_attempts: int = 3


@dataclass
class TitleComposerResult:
    headline: str
    segments: List[str]
    word_count: int
    char_count: int
    validation_results: List[ValidationResult]
    temperature_log: List[Dict[str, Any]]
    success: bool
    attempts: int


class ExecutiveTitleComposer:
    """
    K.4 - Headline Generator
    
    Industry-First Constraint:
    - Segment 1 MUST be Industry/Sector (e.g., "FinTech")
    - BLOCK if Segment 1 is Technology (e.g., "AI", "Cloud", "Data")
    - Limits: 8-13 words total, ≤90 chars
    """
    
    GICS_SECTORS = {
        'FinTech', 'Financial Services', 'Banking', 'Insurance', 'Investment Management',
        'Healthcare', 'Pharmaceuticals', 'Biotechnology', 'Medical Devices',
        'Retail', 'E-Commerce', 'Consumer Goods', 'Luxury Goods',
        'Manufacturing', 'Industrial', 'Automotive', 'Aerospace',
        'Energy', 'Oil & Gas', 'Renewable Energy', 'Utilities',
        'Real Estate', 'Construction', 'Infrastructure',
        'Telecommunications', 'Media', 'Entertainment',
        'Education', 'EdTech', 'Professional Services',
        'Logistics', 'Supply Chain', 'Transportation',
        'Hospitality', 'Travel', 'Food & Beverage',
        'Government', 'Public Sector', 'Non-Profit'
    }
    
    TECHNOLOGY_KEYWORDS = {
        'AI', 'Artificial Intelligence', 'Machine Learning', 'ML',
        'Cloud', 'Cloud Computing', 'AWS', 'Azure', 'GCP',
        'Data', 'Data Science', 'Analytics', 'Big Data',
        'Software', 'SaaS', 'Platform', 'DevOps',
        'Cybersecurity', 'Security', 'Blockchain', 'Crypto',
        'IoT', 'Mobile', 'Web', 'API', 'Microservices'
    }
    
    def __init__(
        self,
        config: Optional[TitleComposerConfig] = None,
        gate_executor: Optional[IntegrityGateExecutor] = None,
        recovery_loop: Optional[AdaptiveRecoveryLoop] = None
    ):
        self.config = config or TitleComposerConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutor()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature
        )
        
    def generate_headline(
        self,
        context: Dict[str, Any]
    ) -> TitleComposerResult:
        """
        Generate headline with industry-first validation.
        
        Args:
            context: Context including industry, role, skills
            
        Returns:
            TitleComposerResult with headline and validation details
        """
        self.recovery_loop.reset(self.config.temperature)
        validation_results = []
        
        for attempt in range(1, self.config.max_attempts + 1):
            headline = self._generate_content(
                context=context,
                temperature=self.recovery_loop.current_temperature,
                attempt=attempt
            )
            
            hygiene_result = self.gate_executor.execute_hygiene_scan(headline)
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
            
            segments = [s.strip() for s in headline.split('|')]
            word_count = len(headline.split())
            char_count = len(headline)
            
            length_result = self._validate_length(headline, word_count, char_count)
            validation_results.append(length_result)
            
            if not length_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=length_result.gate_id,
                    message=length_result.message,
                    details=length_result.details
                )
                if not recovery.should_retry:
                    break
                continue
            
            industry_result = self.gate_executor.execute_industry_first_gate(
                headline=headline,
                valid_industries=self.GICS_SECTORS,
                gate_id='VG_INDUSTRY_FIRST_COMPLIANCE'
            )
            validation_results.append(industry_result)
            
            if not industry_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=industry_result.gate_id,
                    message=industry_result.message,
                    details=industry_result.details
                )
                if not recovery.should_retry:
                    break
                continue
            
            tech_first_result = self._validate_not_tech_first(segments)
            validation_results.append(tech_first_result)
            
            if not tech_first_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=tech_first_result.gate_id,
                    message=tech_first_result.message,
                    details=tech_first_result.details
                )
                if not recovery.should_retry:
                    break
                continue
            
            self.gate_executor.results = validation_results
            
            return TitleComposerResult(
                headline=headline,
                segments=segments,
                word_count=word_count,
                char_count=char_count,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True,
                attempts=attempt
            )
        
        return TitleComposerResult(
            headline="",
            segments=[],
            word_count=0,
            char_count=0,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False,
            attempts=self.config.max_attempts
        )
    
    def _generate_content(
        self,
        context: Dict[str, Any],
        temperature: float,
        attempt: int
    ) -> str:
        """
        Generate headline content using LLM.
        Placeholder for actual LLM integration.
        """
        industry = context.get('industry', 'Technology')
        role = context.get('role', 'Executive')
        
        return f"{industry} | {role} | Strategic Leader"
    
    def _validate_length(
        self,
        headline: str,
        word_count: int,
        char_count: int
    ) -> ValidationResult:
        """
        Validate headline length constraints.
        BLOCKS if outside word/char limits.
        """
        violations = []
        
        if word_count < self.config.min_words:
            violations.append(f"Word count {word_count} below minimum {self.config.min_words}")
        elif word_count > self.config.max_words:
            violations.append(f"Word count {word_count} exceeds maximum {self.config.max_words}")
        
        if char_count > self.config.max_chars:
            violations.append(f"Character count {char_count} exceeds maximum {self.config.max_chars}")
        
        if violations:
            return ValidationResult(
                gate_id='VG_HEADLINE_LENGTH',
                passed=False,
                severity='BLOCK',
                message=f"BLOCKED: {len(violations)} length violations",
                details={
                    'violations': violations,
                    'word_count': word_count,
                    'char_count': char_count
                }
            )
        
        return ValidationResult(
            gate_id='VG_HEADLINE_LENGTH',
            passed=True,
            severity='INFO',
            message=f"Length compliant: {word_count} words, {char_count} chars",
            signature=f"LENGTH:OK:{hash(headline) % 10000}"
        )
    
    def _validate_not_tech_first(self, segments: List[str]) -> ValidationResult:
        """
        Validate first segment is NOT a technology keyword.
        BLOCKS if technology-first detected.
        """
        if not segments:
            return ValidationResult(
                gate_id='VG_NOT_TECH_FIRST',
                passed=False,
                severity='BLOCK',
                message="BLOCKED: No segments found in headline"
            )
        
        first_segment = segments[0]
        
        if first_segment in self.TECHNOLOGY_KEYWORDS:
            return ValidationResult(
                gate_id='VG_NOT_TECH_FIRST',
                passed=False,
                severity='BLOCK',
                message=f"BLOCKED: First segment '{first_segment}' is a technology keyword",
                details={
                    'first_segment': first_segment,
                    'tech_keywords': list(self.TECHNOLOGY_KEYWORDS)[:10]
                }
            )
        
        return ValidationResult(
            gate_id='VG_NOT_TECH_FIRST',
            passed=True,
            severity='INFO',
            message=f"Not tech-first: '{first_segment}' is industry/role",
            signature=f"NOTTECH:OK:{hash(first_segment) % 10000}"
        )


def create_executive_title_composer(
    config: Optional[TitleComposerConfig] = None
) -> ExecutiveTitleComposer:
    """Factory function to create ExecutiveTitleComposer instance"""
    return ExecutiveTitleComposer(config=config)
