"""Specificity Prose Engine Agent - Cover Letter Generator (K.10)

This agent generates high-signal cover letters with company-specific details.
Enforces 3 paragraphs @ 85-100 words each with ≥4 company-specific details.

Layer: L2_execution
Responsibilities:
- Generate cover letter with 3 paragraphs
- Enforce 85-100 words per paragraph
- Include ≥4 company-specific details
- Pass find-replace test for specificity

Non-responsibilities:
- Resume generation
- Bullet synthesis
- Headline composition
"""


from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from runtime.shared.integrity_gate_executor import IntegrityGateExecutor, ValidationResult
from runtime.shared.adaptive_recovery_loop import AdaptiveRecoveryLoop

@dataclass
class SpecificityProseConfig:
    paragraph_count: int = 3
    min_words_per_paragraph: int = 85
    max_words_per_paragraph: int = 100
    min_company_specifics: int = 4
    temperature: float = 0.65
    max_attempts: int = 3

@dataclass
class CompanySpecificDetail:
    detail: str
    category: str
    source: str

@dataclass
class SpecificityProseResult:
    cover_letter: str
    paragraphs: List[str]
    company_specifics: List[CompanySpecificDetail]
    find_replace_test_passed: bool
    validation_results: List[ValidationResult]
    temperature_log: List[Dict[str, Any]]
    success: bool
    attempts: int

class SpecificityProseEngine:
    """
    K.10 - Cover Letter Generator

    Specificity Constraints:
    - 3 Paragraphs @ 85-100 words per paragraph
    - MUST INCLUDE ≥4 company-specific details
    - Details must pass find-replace test (not generic)
    """

    COMPANY_SPECIFIC_CATEGORIES = {
        'PRODUCT': ['product', 'platform', 'service', 'solution', 'offering'],
        'MISSION': ['mission', 'vision', 'values', 'purpose', 'goal'],
        'ACHIEVEMENT': ['milestone', 'launch', 'acquisition', 'funding', 'award'],
        'CULTURE': ['culture', 'team', 'environment', 'approach', 'philosophy'],
        'TECHNOLOGY': ['technology', 'stack', 'infrastructure', 'architecture', 'innovation']
    }

    def __init__(
        self,
        config: Optional[SpecificityProseConfig] = None,
        gate_executor: Optional[IntegrityGateExecutor] = None,
        recovery_loop: Optional[AdaptiveRecoveryLoop] = None
    ):
        self.config = config or SpecificityProseConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutor()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature
        )

    def generate_cover_letter(
        self,
        company_research: Dict[str, Any],
        resume_highlights: List[str],
        context: Dict[str, Any]
    ) -> SpecificityProseResult:
        """
        Generate cover letter with company-specific details.

        Args:
            company_research: Research data about target company
            resume_highlights: Key achievements from resume
            context: Additional context (JD, role, etc.)

        Returns:
            SpecificityProseResult with cover letter and validation details
        """
        self.recovery_loop.reset(self.config.temperature)
        validation_results = []

        for attempt in range(1, self.config.max_attempts + 1):
            cover_letter = self._generate_content(
                company_research=company_research,
                resume_highlights=resume_highlights,
                context=context,
                temperature=self.recovery_loop.current_temperature,
                attempt=attempt
            )

            hygiene_result = self.gate_executor.execute_hygiene_scan(cover_letter)
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

            paragraphs = self._split_paragraphs(cover_letter)

            paragraph_result = self._validate_paragraph_structure(paragraphs)
            validation_results.append(paragraph_result)

            if not paragraph_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=paragraph_result.gate_id,
                    message=paragraph_result.message,
                    details=paragraph_result.details
                )
                if not recovery.should_retry:
                    break
                continue

            company_specifics = self._extract_company_specifics(
                cover_letter,
                company_research
            )

            specificity_result = self._validate_company_specifics(company_specifics)
            validation_results.append(specificity_result)

            if not specificity_result.passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=specificity_result.gate_id,
                    message=specificity_result.message,
                    details=specificity_result.details
                )
                if not recovery.should_retry:
                    break
                continue

            find_replace_test_passed = self._execute_find_replace_test(
                cover_letter,
                company_specifics
            )

            find_replace_result = ValidationResult(
                gate_id='VG_FIND_REPLACE_TEST',
                passed=find_replace_test_passed,
                severity='BLOCK' if not find_replace_test_passed else 'INFO',
                message=f"Find-replace test {'passed' if find_replace_test_passed else 'FAILED'}",
                signature=f"FINDREPLACE:{'OK' if find_replace_test_passed else 'FAIL'}"
            )
            validation_results.append(find_replace_result)

            if not find_replace_test_passed:
                recovery = self.recovery_loop.record_failure(
                    gate_id=find_replace_result.gate_id,
                    message=find_replace_result.message,
                    details={'company_specifics_count': len(company_specifics)}
                )
                if not recovery.should_retry:
                    break
                continue

            self.gate_executor.results = validation_results

            return SpecificityProseResult(
                cover_letter=cover_letter,
                paragraphs=paragraphs,
                company_specifics=company_specifics,
                find_replace_test_passed=find_replace_test_passed,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True,
                attempts=attempt
            )

        return SpecificityProseResult(
            cover_letter="",
            paragraphs=[],
            company_specifics=[],
            find_replace_test_passed=False,
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False,
            attempts=self.config.max_attempts
        )

    def _generate_content(
        self,
        company_research: Dict[str, Any],
        resume_highlights: List[str],
        context: Dict[str, Any],
        temperature: float,
        attempt: int
    ) -> str:
        """
        Generate cover letter content using LLM.
        Placeholder for actual LLM integration.
        """
        company_name = company_research.get('name', 'Your Company')
        product = company_research.get('product', 'innovative platform')
        mission = company_research.get('mission', 'transform the industry')

        return f"""I am writing to express my strong interest in the Chief Technology Officer position at {company_name}. Your company's {product} represents a compelling opportunity to drive technological innovation at scale, and I am particularly drawn to your mission to {mission}.

Throughout my career, I have consistently delivered transformative results in similar high-growth environments. At my previous role, I led a cloud migration initiative that reduced infrastructure costs by 40% while improving system reliability, directly aligning with {company_name}'s focus on operational excellence. I also architected a microservices platform that enabled 3x faster feature deployment, demonstrating the kind of scalable architecture that would support your expansion goals.

I would welcome the opportunity to discuss how my experience in building high-performing engineering teams and delivering strategic technology initiatives can contribute to {company_name}'s continued success. Thank you for considering my application, and I look forward to the possibility of contributing to your innovative work in transforming the industry."""

    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs

    def _validate_paragraph_structure(self, paragraphs: List[str]) -> ValidationResult:
        """
        Validate paragraph count and word counts.
        BLOCKS if structure is invalid.
        """
        if len(paragraphs) != self.config.paragraph_count:
            return ValidationResult(
                gate_id='VG_PARAGRAPH_STRUCTURE',
                passed=False,
                severity='BLOCK',
                message=f"BLOCKED: Expected {self.config.paragraph_count} paragraphs,
                    got {len(paragraphs)}",
                    
                details={'expected': self.config.paragraph_count, 'actual': len(paragraphs)}
            )

        violations = []
        for i, para in enumerate(paragraphs, 1):
            word_count = len(para.split())
            if word_count < self.config.min_words_per_paragraph:
                violations.append(f"Paragraph {i}: {word_count} words (min {self.config.min_words_per_paragraph})")
            elif word_count > self.config.max_words_per_paragraph:
                violations.append(f"Paragraph {i}: {word_count} words (max {self.config.max_words_per_paragraph})")

        if violations:
            return ValidationResult(
                gate_id='VG_PARAGRAPH_STRUCTURE',
                passed=False,
                severity='BLOCK',
                message=f"BLOCKED: {len(violations)} paragraph word count violations",
                details={'violations': violations}
            )

        return ValidationResult(
            gate_id='VG_PARAGRAPH_STRUCTURE',
            passed=True,
            severity='INFO',
            message=f"Paragraph structure valid: {len(paragraphs)} paragraphs with correct word counts",
                
            signature=f"PARA:OK:{len(paragraphs)}"
        )

    def _extract_company_specifics(
        self,
        cover_letter: str,
        company_research: Dict[str, Any]
    ) -> List[CompanySpecificDetail]:
        """Extract company-specific details from cover letter"""
        specifics = []

        company_name = company_research.get('name', '')
        if company_name and company_name in cover_letter:
            count = cover_letter.count(company_name)
            for i in range(count):
                specifics.append(CompanySpecificDetail(
                    detail=company_name,
                    category='COMPANY_NAME',
                    source='company_research'
                ))

        for category, keywords in self.COMPANY_SPECIFIC_CATEGORIES.items():
            for keyword in keywords:
                for key, value in company_research.items():
                    if isinstance(value, str) and keyword in value.lower():
                        if value in cover_letter:
                            specifics.append(CompanySpecificDetail(
                                detail=value,
                                category=category,
                                source=f'company_research.{key}'
                            ))

        return specifics[:10]

    def _validate_company_specifics(
        self,
        company_specifics: List[CompanySpecificDetail]
    ) -> ValidationResult:
        """
        Validate ≥4 company-specific details present.
        BLOCKS if insufficient specifics.
        """
        if len(company_specifics) >= self.config.min_company_specifics:
            return ValidationResult(
                gate_id='VG_COMPANY_SPECIFICS',
                passed=True,
                severity='INFO',
                message=f"Company specifics satisfied: {len(company_specifics)} details (min {self.config.min_company_specifics})",
                    
                signature=f"SPECIFICS:OK:{len(company_specifics)}",
                details={
                    'count': len(company_specifics),
                    'categories': list(set(s.category for s in company_specifics))
                }
            )

        return ValidationResult(
            gate_id='VG_COMPANY_SPECIFICS',
            passed=False,
            severity='BLOCK',
            message=f"BLOCKED: Insufficient company specifics - {len(company_specifics)} details (min {self.config.min_company_specifics})",
                
            details={'count': len(company_specifics),
                'min_required': self.config.min_company_specifics}
        )

    def _execute_find_replace_test(
        self,
        cover_letter: str,
        company_specifics: List[CompanySpecificDetail]
    ) -> bool:
        """
        Execute find-replace test - letter should break if specifics removed.
        Returns True if test passes (letter is truly specific).
        """
        if len(company_specifics) < self.config.min_company_specifics:
            return False

        test_letter = cover_letter
        for specific in company_specifics:
            test_letter = test_letter.replace(specific.detail, '[COMPANY]')

        generic_ratio = test_letter.count('[COMPANY]') / max(len(cover_letter.split()), 1)

        return generic_ratio > 0.02

def create_specificity_prose_engine(
    config: Optional[SpecificityProseConfig] = None
) -> SpecificityProseEngine:
    """Factory function to create SpecificityProseEngine instance"""
    return SpecificityProseEngine(config=config)
