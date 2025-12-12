"""Achv Bullet Synthesizer Agent - Achievement Bullet Generator (K.5A & K.6A)

This agent generates achievement bullets with strict provenance tracking.
Enforces 3V-3T-1S (Unify) and 2V-3T-1S (IBM) patterns with zero-tolerance word counts.

Layer: L2_execution
Responsibilities:
- Generate achievement bullets with provenance tracking
- Enforce 3V-3T-1S pattern for K.5A (Unify format)
- Enforce 2V-3T-1S pattern for K.6A (IBM format)
- Validate exact word counts per bullet
- Generate QA Report with provenance log

Non-responsibilities:
- Overview synthesis
- Headline generation
- Executive summary
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from runtime.shared.integrity_gate_executor import IntegrityGateExecutor, ValidationResult
from runtime.shared.adaptive_recovery_loop import AdaptiveRecoveryLoop


class BulletFormat(Enum):
    UNIFY = "UNIFY"
    IBM = "IBM"


class ProvenanceType(Enum):
    VERB = "V"
    TECH = "T"
    SOFT = "S"


@dataclass
class ProvenancePattern:
    format_type: BulletFormat
    verb_count: int
    tech_count: int
    soft_count: int
    
    def __str__(self) -> str:
        return f"{self.verb_count}V-{self.tech_count}T-{self.soft_count}S"


@dataclass
class BulletProvenanceLog:
    bullet_text: str
    word_count: int
    provenance_items: Dict[ProvenanceType, List[str]]
    pattern_match: bool
    expected_pattern: str
    actual_pattern: str


@dataclass
class BulletSynthesizerConfig:
    format_type: BulletFormat = BulletFormat.UNIFY
    temperature: float = 0.6
    max_attempts: int = 3
    
    @property
    def min_words(self) -> int:
        return 28 if self.format_type == BulletFormat.UNIFY else 24
    
    @property
    def max_words(self) -> int:
        return 33 if self.format_type == BulletFormat.UNIFY else 30
    
    @property
    def bullet_count(self) -> int:
        return 7 if self.format_type == BulletFormat.UNIFY else 6
    
    @property
    def provenance_pattern(self) -> ProvenancePattern:
        if self.format_type == BulletFormat.UNIFY:
            return ProvenancePattern(BulletFormat.UNIFY, verb_count=3, tech_count=3, soft_count=1)
        else:
            return ProvenancePattern(BulletFormat.IBM, verb_count=2, tech_count=3, soft_count=1)


@dataclass
class BulletSynthesizerResult:
    bullets: List[str]
    provenance_logs: List[BulletProvenanceLog]
    qa_report: Dict[str, Any]
    validation_results: List[ValidationResult]
    temperature_log: List[Dict[str, Any]]
    success: bool
    attempts: int


class AchvBulletSynthesizer:
    """
    K.5A & K.6A - Achievement Bullet Generator with Provenance
    
    Zero Tolerance Constraints:
    - K.5A (Unify): 3V-3T-1S pattern, 28-33 words each, 7 bullets
    - K.6A (IBM): 2V-3T-1S pattern, 24-30 words each, 6 bullets
    - VG_BULLET_PROVENANCE_CHECK BLOCKS if pattern invalid
    """
    
    VERB_KEYWORDS = {
        'led', 'drove', 'architected', 'built', 'managed', 'delivered', 'launched',
        'scaled', 'optimized', 'transformed', 'implemented', 'established', 'directed',
        'spearheaded', 'orchestrated', 'executed', 'pioneered', 'accelerated'
    }
    
    TECH_KEYWORDS = {
        'python', 'java', 'aws', 'azure', 'kubernetes', 'docker', 'react', 'node.js',
        'postgresql', 'mongodb', 'redis', 'kafka', 'spark', 'tensorflow', 'pytorch',
        'microservices', 'api', 'ci/cd', 'devops', 'cloud', 'ml', 'ai', 'data pipeline'
    }
    
    SOFT_KEYWORDS = {
        'leadership', 'collaboration', 'communication', 'strategic', 'cross-functional',
        'stakeholder', 'mentorship', 'team building', 'agile', 'innovation', 'vision'
    }
    
    def __init__(
        self,
        config: Optional[BulletSynthesizerConfig] = None,
        gate_executor: Optional[IntegrityGateExecutor] = None,
        recovery_loop: Optional[AdaptiveRecoveryLoop] = None
    ):
        self.config = config or BulletSynthesizerConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutor()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature
        )
        
    def generate_bullets(
        self,
        experience_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> BulletSynthesizerResult:
        """
        Generate achievement bullets with provenance tracking.
        
        Args:
            experience_data: Raw experience data for bullet generation
            context: Additional context (JD, industry, etc.)
            
        Returns:
            BulletSynthesizerResult with bullets and provenance logs
        """
        self.recovery_loop.reset(self.config.temperature)
        validation_results = []
        
        for attempt in range(1, self.config.max_attempts + 1):
            bullets = self._generate_bullet_set(
                experience_data=experience_data,
                context=context,
                temperature=self.recovery_loop.current_temperature,
                attempt=attempt
            )
            
            if len(bullets) != self.config.bullet_count:
                count_result = ValidationResult(
                    gate_id='VG_BULLET_COUNT',
                    passed=False,
                    severity='BLOCK',
                    message=f"BLOCKED: Expected {self.config.bullet_count} bullets, got {len(bullets)}",
                    details={'expected': self.config.bullet_count, 'actual': len(bullets)}
                )
                validation_results.append(count_result)
                
                recovery = self.recovery_loop.record_failure(
                    gate_id=count_result.gate_id,
                    message=count_result.message,
                    details=count_result.details
                )
                if not recovery.should_retry:
                    break
                continue
            
            provenance_logs = []
            all_bullets_valid = True
            
            for i, bullet in enumerate(bullets, 1):
                hygiene_result = self.gate_executor.execute_hygiene_scan(bullet)
                validation_results.append(hygiene_result)
                
                if not hygiene_result.passed:
                    all_bullets_valid = False
                    break
                
                word_count_result = self._validate_bullet_word_count(bullet, i)
                validation_results.append(word_count_result)
                
                if not word_count_result.passed:
                    all_bullets_valid = False
                    break
                
                provenance_log = self._analyze_provenance(bullet)
                provenance_logs.append(provenance_log)
                
                provenance_result = self._validate_provenance_pattern(provenance_log, i)
                validation_results.append(provenance_result)
                
                if not provenance_result.passed:
                    all_bullets_valid = False
                    break
            
            if not all_bullets_valid:
                recovery = self.recovery_loop.record_failure(
                    gate_id='VG_BULLET_PROVENANCE_CHECK',
                    message="Bullet validation failed",
                    details={'failed_bullet': i}
                )
                if not recovery.should_retry:
                    break
                continue
            
            qa_report = self._generate_qa_report(bullets, provenance_logs)
            
            self.gate_executor.results = validation_results
            
            return BulletSynthesizerResult(
                bullets=bullets,
                provenance_logs=provenance_logs,
                qa_report=qa_report,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                success=True,
                attempts=attempt
            )
        
        return BulletSynthesizerResult(
            bullets=[],
            provenance_logs=[],
            qa_report={},
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            success=False,
            attempts=self.config.max_attempts
        )
    
    def _generate_bullet_set(
        self,
        experience_data: Dict[str, Any],
        context: Dict[str, Any],
        temperature: float,
        attempt: int
    ) -> List[str]:
        """
        Generate set of bullets using LLM.
        Placeholder for actual LLM integration.
        """
        pattern = self.config.provenance_pattern
        
        bullets = [
            f"Led cloud migration initiative using AWS and Kubernetes, reducing infrastructure costs by 40% while improving system reliability",
            f"Architected microservices platform with Python and Node.js, enabling 3x faster feature deployment through strategic API design",
            f"Managed cross-functional team of 12 engineers, delivering $2M revenue-generating product using agile methodologies and CI/CD automation",
            f"Drove data pipeline optimization with Spark and PostgreSQL, processing 10M+ daily transactions with 99.9% uptime",
            f"Built ML-powered recommendation engine using TensorFlow, increasing user engagement by 35% through collaborative innovation",
            f"Implemented DevOps best practices with Docker and Jenkins, reducing deployment time from 4 hours to 15 minutes",
            f"Established technical mentorship program, developing 8 junior engineers into senior contributors through strategic leadership"
        ]
        
        return bullets[:self.config.bullet_count]
    
    def _validate_bullet_word_count(self, bullet: str, bullet_num: int) -> ValidationResult:
        """
        Validate bullet word count is within range.
        BLOCKS if outside min-max range.
        """
        words = bullet.split()
        word_count = len(words)
        
        if self.config.min_words <= word_count <= self.config.max_words:
            return ValidationResult(
                gate_id=f'VG_BULLET_{bullet_num}_WORD_COUNT',
                passed=True,
                severity='INFO',
                message=f"Bullet {bullet_num} word count compliant: {word_count} words",
                signature=f"BULLET{bullet_num}:WC:OK"
            )
        
        return ValidationResult(
            gate_id=f'VG_BULLET_{bullet_num}_WORD_COUNT',
            passed=False,
            severity='BLOCK',
            message=f"BLOCKED: Bullet {bullet_num} word count {word_count} outside range ({self.config.min_words}-{self.config.max_words})",
            details={
                'bullet_num': bullet_num,
                'word_count': word_count,
                'min': self.config.min_words,
                'max': self.config.max_words
            }
        )
    
    def _analyze_provenance(self, bullet: str) -> BulletProvenanceLog:
        """
        Analyze bullet for provenance items (Verbs, Tech, Soft).
        Returns provenance log with categorized items.
        """
        bullet_lower = bullet.lower()
        words = set(re.findall(r'\b\w+\b', bullet_lower))
        
        provenance_items = {
            ProvenanceType.VERB: [],
            ProvenanceType.TECH: [],
            ProvenanceType.SOFT: []
        }
        
        for word in words:
            if word in self.VERB_KEYWORDS:
                provenance_items[ProvenanceType.VERB].append(word)
            if word in self.TECH_KEYWORDS:
                provenance_items[ProvenanceType.TECH].append(word)
            if word in self.SOFT_KEYWORDS:
                provenance_items[ProvenanceType.SOFT].append(word)
        
        expected_pattern = str(self.config.provenance_pattern)
        actual_pattern = f"{len(provenance_items[ProvenanceType.VERB])}V-{len(provenance_items[ProvenanceType.TECH])}T-{len(provenance_items[ProvenanceType.SOFT])}S"
        
        pattern_match = (
            len(provenance_items[ProvenanceType.VERB]) >= self.config.provenance_pattern.verb_count and
            len(provenance_items[ProvenanceType.TECH]) >= self.config.provenance_pattern.tech_count and
            len(provenance_items[ProvenanceType.SOFT]) >= self.config.provenance_pattern.soft_count
        )
        
        return BulletProvenanceLog(
            bullet_text=bullet,
            word_count=len(bullet.split()),
            provenance_items=provenance_items,
            pattern_match=pattern_match,
            expected_pattern=expected_pattern,
            actual_pattern=actual_pattern
        )
    
    def _validate_provenance_pattern(
        self,
        provenance_log: BulletProvenanceLog,
        bullet_num: int
    ) -> ValidationResult:
        """
        Validate provenance pattern matches expected pattern.
        BLOCKS if pattern is invalid.
        """
        if provenance_log.pattern_match:
            return ValidationResult(
                gate_id='VG_BULLET_PROVENANCE_CHECK',
                passed=True,
                severity='INFO',
                message=f"Bullet {bullet_num} provenance valid: {provenance_log.actual_pattern}",
                signature=f"PROV{bullet_num}:OK",
                details={
                    'expected': provenance_log.expected_pattern,
                    'actual': provenance_log.actual_pattern,
                    'items': {k.value: v for k, v in provenance_log.provenance_items.items()}
                }
            )
        
        return ValidationResult(
            gate_id='VG_BULLET_PROVENANCE_CHECK',
            passed=False,
            severity='BLOCK',
            message=f"BLOCKED: Bullet {bullet_num} provenance invalid - expected {provenance_log.expected_pattern}, got {provenance_log.actual_pattern}",
            details={
                'bullet_num': bullet_num,
                'expected': provenance_log.expected_pattern,
                'actual': provenance_log.actual_pattern,
                'items': {k.value: v for k, v in provenance_log.provenance_items.items()}
            }
        )
    
    def _generate_qa_report(
        self,
        bullets: List[str],
        provenance_logs: List[BulletProvenanceLog]
    ) -> Dict[str, Any]:
        """Generate QA Report with provenance tracking"""
        return {
            'format_type': self.config.format_type.value,
            'bullet_count': len(bullets),
            'expected_pattern': str(self.config.provenance_pattern),
            'word_count_range': f"{self.config.min_words}-{self.config.max_words}",
            'provenance_summary': {
                'total_bullets': len(provenance_logs),
                'pattern_matches': sum(1 for log in provenance_logs if log.pattern_match),
                'pattern_failures': sum(1 for log in provenance_logs if not log.pattern_match)
            },
            'detailed_provenance': [
                {
                    'bullet_num': i + 1,
                    'word_count': log.word_count,
                    'pattern': log.actual_pattern,
                    'match': log.pattern_match,
                    'verbs': log.provenance_items[ProvenanceType.VERB],
                    'tech': log.provenance_items[ProvenanceType.TECH],
                    'soft': log.provenance_items[ProvenanceType.SOFT]
                }
                for i, log in enumerate(provenance_logs)
            ]
        }


def create_achv_bullet_synthesizer(
    config: Optional[BulletSynthesizerConfig] = None
) -> AchvBulletSynthesizer:
    """Factory function to create AchvBulletSynthesizer instance"""
    return AchvBulletSynthesizer(config=config)
