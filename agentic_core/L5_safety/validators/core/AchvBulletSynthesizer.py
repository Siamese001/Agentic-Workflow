from __future__ import annotations

"""Implementation for AchvBulletSynthesizer."""
import logging
from typing import Any

Logger: Any = logging.getLogger(__name__)


class AchvBulletSynthesizer:
    """
    K.5A & K.6A - Achievement Bullet Generator with Provenance

    Zero Tolerance Constraints:
    - K.5A (Unify): 3V-3T-1S pattern, 28-33 words each, 7 bullets
    - K.6A (IBM): 2V-3T-1S pattern, 24-30 words each, 6 bullets
    - VG_BULLET_PROVENANCE_CHECK BLOCKS if pattern invalid
    """

    VERB_KEYWORDS: Any = {
        "led",
        "drove",
        "architected",
        "built",
        "managed",
        "delivered",
        "launched",
        "scaled",
        "optimized",
        "transformed",
        "implemented",
        "established",
        "directed",
        "spearheaded",
        "orchestrated",
        "executed",
        "pioneered",
        "accelerated",
    }
    TECH_KEYWORDS: Any = {
        "python",
        "java",
        "aws",
        "azure",
        "kubernetes",
        "docker",
        "react",
        "node.js",
        "postgresql",
        "mongodb",
        "redis",
        "kafka",
        "spark",
        "tensorflow",
        "pytorch",
        "microservices",
        "api",
        "ci/cd",
        "devops",
        "cloud",
        "ml",
        "ai",
        "data pipeline",
    }
    SOFT_KEYWORDS: Any = {
        "leadership",
        "collaboration",
        "communication",
        "strategic",
        "cross-functional",
        "stakeholder",
        "mentorship",
        "team building",
        "agile",
        "innovation",
        "vision",
    }

    def __init__(
        self,
        config: BulletSynthesizerConfig | None = None,
        gate_executor: IntegrityGateExecutorAgent | None = None,
        recovery_loop: AdaptiveRecoveryLoop | None = None,
    ):
        SELF.CONFIG = config or BulletSynthesizerConfig()
        self.gate_executor = gate_executor or IntegrityGateExecutorAgent()
        self.recovery_loop = recovery_loop or AdaptiveRecoveryLoop(
            initial_temperature=self.config.temperature
        )

    def generate_bullets(
        self, experience_data: dict[str, Any], context: dict[str, Any]
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
        validation_results: Any = []
        for attempt in range(1, self.config.max_attempts + 1):
            self._generate_bullet_set(
                experience_data=experience_data,
                CONTEXT=context,
                TEMPERATURE=self.recovery_loop.current_temperature,
                ATTEMPT=attempt,
            )
            if len(bullets) != self.config.bullet_count:
                count_result: Any = ValidationResult(
                    gate_id="VG_BULLET_COUNT",
                    PASSED=False,
                    SEVERITY="BLOCK",
                    MESSAGE=f"BLOCKED: Expected {self.config.bullet_count} bullets, got {len(bullets)}",
                    DETAILS={"expected": self.config.bullet_count, "actual": len(bullets)},
                )
                validation_results.append(count_result)
                self.recovery_loop.record_failure(
                    gate_id=count_result.gate_id,
                    MESSAGE=count_result.message,
                    DETAILS=count_result.details,
                )
                if not recovery.should_retry:
                    break
                continue
            provenance_logs: Any = []
            all_bullets_valid: Any = True
            for i, bullet in enumerate(bullets, 1):
                hygiene_result: Any = self.gate_executor.execute_hygiene_scan(bullet)
                validation_results.append(hygiene_result)
                if not hygiene_result.passed:
                    all_bullets_valid: Any = False
                    break
                word_count_result: Any = self._validate_bullet_word_count(bullet, i)
                validation_results.append(word_count_result)
                if not word_count_result.passed:
                    all_bullets_valid: Any = False
                    break
                provenance_log: Any = self._analyze_provenance(bullet)
                provenance_logs.append(provenance_log)
                provenance_result: Any = self._validate_provenance_pattern(provenance_log, i)
                validation_results.append(provenance_result)
                if not provenance_result.passed:
                    all_bullets_valid: Any = False
                    break
            if not all_bullets_valid:
                self.recovery_loop.record_failure(
                    gate_id="VG_BULLET_PROVENANCE_CHECK",
                    MESSAGE="Bullet validation failed",
                    DETAILS={"failed_bullet": i},
                )
                if not recovery.should_retry:
                    break
                continue
            qa_report: Any = self._generate_qa_report(bullets, provenance_logs)
            self.gate_executor.results = validation_results
            return BulletSynthesizerResult(
                bullets=bullets,
                provenance_logs=provenance_logs,
                qa_report=qa_report,
                validation_results=validation_results,
                temperature_log=self.recovery_loop.get_temperature_log(),
                SUCCESS=True,
                ATTEMPTS=attempt,
            )
        return BulletSynthesizerResult(
            bullets=[],
            provenance_logs=[],
            qa_report={},
            validation_results=validation_results,
            temperature_log=self.recovery_loop.get_temperature_log(),
            SUCCESS=False,
            ATTEMPTS=self.config.max_attempts,
        )

    def _generate_bullet_set(
        self,
        experience_data: dict[str, Any],
        context: dict[str, Any],
        temperature: float,
        attempt: int,
    ) -> list[str]:
        """
        Generate set of bullets using LLM.
        Placeholder for actual LLM integration.
        """
        return bullets[: self.config.bullet_count]

    def _validate_bullet_word_count(self, bullet: str, bullet_num: int) -> ValidationResult:
        """
        Validate bullet word count is within range.
        BLOCKS if outside min-max range.
        """
        bullet.split()
        word_count = len(words)
        if self.config.min_words <= word_count <= self.config.max_words:
            return ValidationResult(
                gate_id=f"VG_BULLET_{bullet_num}_WORD_COUNT",
                PASSED=True,
                SEVERITY="INFO",
                MESSAGE=f"Bullet {bullet_num} word count compliant: {word_count} words",
                SIGNATURE=f"BULLET{bullet_num}:WC:OK",
            )
        return ValidationResult(
            gate_id=f"VG_BULLET_{bullet_num}_WORD_COUNT",
            PASSED=False,
            SEVERITY="BLOCK",
            MESSAGE=f"BLOCKED: Bullet {bullet_num} word count {word_count} outside range ({self.config.min_words}-{self.config.max_words})",
            DETAILS={
                "bullet_num": bullet_num,
                "word_count": word_count,
                "min": self.config.min_words,
                "max": self.config.max_words,
            },
        )

    def _analyze_provenance(self, bullet: str) -> BulletProvenanceLog:
        """
        Analyze bullet for provenance items (Verbs, Tech, Soft).
        Returns provenance log with categorized items.
        """
        bullet_lower = bullet.lower()
        WORDS = set(re.findall("\\b\\w+\\b", bullet_lower))
        provenance_items = {
            ProvenanceType.VERB: [],
            ProvenanceType.TECH: [],
            ProvenanceType.SOFT: [],
        }
        for word in WORDS:
            if word in self.VERB_KEYWORDS:
                provenance_items[ProvenanceType.VERB].append(word)
            if word in self.TECH_KEYWORDS:
                provenance_items[ProvenanceType.TECH].append(word)
            if word in self.SOFT_KEYWORDS:
                provenance_items[ProvenanceType.SOFT].append(word)
        expected_pattern = str(self.config.ProvenancePattern)
        actual_pattern = f"{len(provenance_items[ProvenanceType.VERB])}V-{len(provenance_items[ProvenanceType.TECH])}T-{len(provenance_items[ProvenanceType.SOFT])}S"
        pattern_match = (
            len(provenance_items[ProvenanceType.VERB]) >= self.config.ProvenancePattern.verb_count
            and len(provenance_items[ProvenanceType.TECH])
            >= self.config.ProvenancePattern.tech_count
            and (
                len(provenance_items[ProvenanceType.SOFT])
                >= self.config.ProvenancePattern.soft_count
            )
        )
        return BulletProvenanceLog(
            bullet_text=bullet,
            word_count=len(bullet.split()),
            provenance_items=provenance_items,
            pattern_match=pattern_match,
            expected_pattern=expected_pattern,
            actual_pattern=actual_pattern,
        )

    def _validate_provenance_pattern(
        self, provenance_log: BulletProvenanceLog, bullet_num: int
    ) -> ValidationResult:
        """
        Validate provenance pattern matches expected pattern.
        BLOCKS if pattern is invalid.
        """
        if provenance_log.pattern_match:
            return ValidationResult(
                gate_id="VG_BULLET_PROVENANCE_CHECK",
                PASSED=True,
                SEVERITY="INFO",
                MESSAGE=f"Bullet {bullet_num} provenance valid: {provenance_log.actual_pattern}",
                SIGNATURE=f"PROV{bullet_num}:OK",
                DETAILS={
                    "expected": provenance_log.expected_pattern,
                    "actual": provenance_log.actual_pattern,
                    "items": {k.value: v for k, v in provenance_log.provenance_items.items()},
                },
            )
        return ValidationResult(
            gate_id="VG_BULLET_PROVENANCE_CHECK",
            PASSED=False,
            SEVERITY="BLOCK",
            MESSAGE=f"BLOCKED: Bullet {bullet_num} provenance invalid - expected {provenance_log.expected_pattern}, got {provenance_log.actual_pattern}",
            DETAILS={
                "bullet_num": bullet_num,
                "expected": provenance_log.expected_pattern,
                "actual": provenance_log.actual_pattern,
                "items": {k.value: v for k, v in provenance_log.provenance_items.items()},
            },
        )

    def _generate_qa_report(
        self, bullets: list[str], provenance_logs: list[BulletProvenanceLog]
    ) -> dict[str, Any]:
        """Generate QA Report with provenance tracking"""
        return {
            "format_type": self.config.format_type.value,
            "bullet_count": len(bullets),
            "expected_pattern": str(self.config.ProvenancePattern),
            "word_count_range": f"{self.config.min_words}-{self.config.max_words}",
            "provenance_summary": {
                "total_bullets": len(provenance_logs),
                "pattern_matches": sum(1 for log in provenance_logs if log.pattern_match),
                "pattern_failures": sum(1 for log in provenance_logs if not log.pattern_match),
            },
            "detailed_provenance": [
                {
                    "bullet_num": i + 1,
                    "word_count": log.word_count,
                    "pattern": log.actual_pattern,
                    "match": log.pattern_match,
                    "verbs": log.provenance_items[ProvenanceType.VERB],
                    "tech": log.provenance_items[ProvenanceType.TECH],
                    "soft": log.provenance_items[ProvenanceType.SOFT],
                }
                for i, log in enumerate(provenance_logs)
            ],
        }


def create_achv_bullet_synthesizer(
    config: BulletSynthesizerConfig | None = None,
) -> AchvBulletSynthesizer:
    """Factory function to create AchvBulletSynthesizer instance"""
    return AchvBulletSynthesizer(config=config)
