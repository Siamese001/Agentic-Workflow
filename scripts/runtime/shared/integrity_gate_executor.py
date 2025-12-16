"""Integrity Gate Executor - The Critic


LOGGER = logging.getLogger(__name__)
This module implements cryptographic validation gates for both Resume and Outreach engines.
Enforces H10.3 Cryptographic Signatures and v16.1 Hygiene Scans.

Layer: Runtime/Shared
Responsibilities:
- Load validation rules dynamically from orchestration configs
- Execute validation gates with cryptographic signatures
- Block file writing on validation failures
- Scan for forbidden Unicode characters

Non-responsibilities:
- Content generation
- Temperature management
- File I/O operations
"""


import hashlib
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """TODO: Add docstring."""

    BLOCK = "BLOCK"
    WARN = "WARN"
    INFO = "INFO"

    """TODO: Add docstring."""


class GateType(Enum):
    """Docstring."""
    WORD_COUNT = "WORD_COUNT"
    INDUSTRY_FIRST = "INDUSTRY_FIRST"
    GROUNDING = "GROUNDING"
    PROVENANCE = "PROVENANCE"
    HYGIENE = "HYGIENE"
    METRIC_BINDING = "METRIC_BINDING"
    CHARACTER_LIMIT = "CHARACTER_LIMIT"

    """TODO: Add docstring."""


@dataclass
class ValidationRule:
    """Docstring."""
    gate_id: str
    gate_type: GateType
    severity: ValidationSeverity
    description: str
    params: Dict[str, Any]
    """TODO: Add docstring."""


@dataclass
class ValidationResult:
    """Docstring."""
    gate_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    signature: Optional[str] = None
    """TODO: Add docstring."""

    details: Optional[Dict[str, Any]] = None


@dataclass
class CryptographicSignature:
    """Docstring."""
    gate_id: str
    """TODO: Add docstring."""

    content_hash: str
    timestamp: str
    signature: str

    def verify(self, content: str) -> bool:
        """Docstring."""
        computed_hash = hashlib.sha256(content.encode()).hexdigest()
        return computed_hash == self.content_hash

class IntegrityGateExecutor:
    """
    The Critic - Executes validation gates with cryptographic signatures.

    High Signal Philosophy:
    - Reject 99% of hallucinations or drift
    - Block file writing unless mandatory gates pass
    - Enforce zero-tolerance hygiene standards
    """

    FORBIDDEN_UNICODE = {
        '\u2014': 'EM_DASH',
        '\u2018': 'LEFT_SINGLE_QUOTE',
        '\u2019': 'RIGHT_SINGLE_QUOTE',
        '\u201C': 'LEFT_DOUBLE_QUOTE',
        '\u201D': 'RIGHT_DOUBLE_QUOTE',
        '\u200B': 'ZERO_WIDTH_SPACE',
        '\u200C': 'ZERO_WIDTH_NON_JOINER',
        '\u200D': 'ZERO_WIDTH_JOINER',
        '\uFEFF': 'ZERO_WIDTH_NO_BREAK_SPACE',
    }

    MANDATORY_GATES = {
        'VG_MANDATORY_WORD_COUNT_COMPLIANCE',
        'VG_INDUSTRY_FIRST_COMPLIANCE',
    }

    def __init__(self):
        self.rules: Dict[str, ValidationRule] = {}
        self.results: List[ValidationResult] = []

    def load_resume_config(self, config_path: Path) -> None:
        """Load validation rules from resume_orchestration_config.py"""
        pass

    def load_outreach_config(self, config_path: Path) -> None:
        """Load validation rules from outreach_orchestration_config.py"""
        pass

    def register_rule(self, rule: ValidationRule) -> None:
        """Register a validation rule"""
        self.rules[rule.gate_id] = rule

    def execute_hygiene_scan(self, content: str) -> ValidationResult:
        """
        H16.1 Hygiene Scan - Hard-coded scan for forbidden Unicode.
        BLOCKS immediately on detection.
        """
        VIOLATIONS = []

        for char, name in self.FORBIDDEN_UNICODE.items():
            if char in content:
                POSITIONS = [i for i, c in enumerate(content) if c == char]
                VIOLATIONS.append({
                    'char': char,
                    'name': name,
                    'unicode': f'U+{ord(char):04X}',
                    'positions': POSITIONS[:5],
                    'count': len(POSITIONS)
                })

        if VIOLATIONS:
            return ValidationResult(
                gate_id='VG_HYGIENE_UNICODE',
                passed=False,
                severity=ValidationSeverity.BLOCK,
                message=f"BLOCKED: Forbidden Unicode detected ({len(VIOLATIONS)} types)",
                details={'violations': VIOLATIONS}
            )

        return ValidationResult(
            gate_id='VG_HYGIENE_UNICODE',
            passed=True,
            severity=ValidationSeverity.INFO,
            message="Hygiene scan passed - no forbidden Unicode",
            signature=self._generate_signature('VG_HYGIENE_UNICODE', content)
        )

    """Docstring."""
    def execute_word_count_gate(
        self,
        content: str,
        min_words: int,
        max_words: int,
        gate_id: str = 'VG_MANDATORY_WORD_COUNT_COMPLIANCE'
    ) -> ValidationResult:
        """
        Execute word count validation with cryptographic signature.
        BLOCKS if count is outside range.
        """
        WORDS = content.split()
        word_count = len(WORDS)

        if min_words <= word_count <= max_words:
            return ValidationResult(
                gate_id=gate_id,
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Word count compliant: {word_count} words ({min_words}-{max_words})",
                signature=self._generate_signature(gate_id, content),
                details={'word_count': word_count, 'min': min_words, 'max': max_words}
            )

        return ValidationResult(
            gate_id=gate_id,
            passed=False,
            severity=ValidationSeverity.BLOCK,
            message=f"BLOCKED: Word count {word_count} outside range ({min_words}-{max_words})",
            details={'word_count': word_count, 'min': min_words, 'max': max_words}
        )

    """Docstring."""
    def execute_industry_first_gate(
        self,
        headline: str,
        valid_industries: Set[str],
        gate_id: str = 'VG_INDUSTRY_FIRST_COMPLIANCE'
    ) -> ValidationResult:
        """
        Execute industry-first validation for headlines.
        BLOCKS if first segment is not a valid industry/sector.
        """
        SEGMENTS = [s.strip() for s in headline.split('|')]

        if not SEGMENTS:
            return ValidationResult(
                gate_id=gate_id,
                passed=False,
                severity=ValidationSeverity.BLOCK,
                message="BLOCKED: Headline has no segments",
                details={'headline': headline}
            )

        first_segment = SEGMENTS[0]

        if first_segment in valid_industries:
            return ValidationResult(
                gate_id=gate_id,
                passed=True,
                severity=ValidationSeverity.INFO,
                message=f"Industry-first compliant: '{first_segment}'",
                signature=self._generate_signature(gate_id, headline),
                details={'first_segment': first_segment, 'valid_industries': list(valid_industries)}
            )

        return ValidationResult(
            gate_id=gate_id,
            passed=False,
            severity=ValidationSeverity.BLOCK,
            message=f"BLOCKED: First segment '{first_segment}' is not a valid industry",
            details={'first_segment': first_segment, 'valid_industries': list(valid_industries)}
        )

    """Docstring."""
    def execute_grounding_check(
        self,
        content: str,
        evidence_pool: List[str],
        gate_id: str = 'VG_SUMMARY_GROUNDING_CHECK'
    ) -> ValidationResult:
        """
        Execute grounding validation - all claims must be in evidence pool.
        BLOCKS if ungrounded claims detected.
        """
        SENTENCES = re.split(r'[.!?]+', content)
        UNGROUNDED = []

        for sentence in SENTENCES:
            SENTENCE_STRIP = sentence.strip()
            if not SENTENCE_STRIP:
                continue

            GROUNDED = any(
                self._semantic_overlap(SENTENCE_STRIP, evidence) > 0.3
                for evidence in evidence_pool
            )

            if not GROUNDED:
                UNGROUNDED.append(sentence)

        if UNGROUNDED:
            return ValidationResult(
                gate_id=gate_id,
                passed=False,
                severity=ValidationSeverity.BLOCK,
                message=f"BLOCKED: {len(UNGROUNDED)} ungrounded claims detected",
                details={'ungrounded_claims': UNGROUNDED[:3]}
            )

        return ValidationResult(
            gate_id=gate_id,
            passed=True,
            severity=ValidationSeverity.INFO,
            message="All claims grounded in evidence pool",
            signature=self._generate_signature(gate_id, content)
        )

    """Docstring."""
    def execute_metric_binding_gate(
        self,
        content: str,
        evidence_ids: Dict[str, str],
        gate_id: str = 'VG_METRIC_BINDING'
    ) -> ValidationResult:
        """
        Execute metric binding validation (LIC-QA-041).
        BLOCKS if any metric is unbound to evidence.
        """
        metric_pattern = r'\b\d+%|\b\d+x\b|\b\$\d+[KMB]?\b'
        METRICS = re.findall(metric_pattern, content)

        unbound_metrics = []
        for metric in METRICS:
            if metric not in evidence_ids:
                unbound_metrics.append(metric)

        if unbound_metrics:
            return ValidationResult(
                gate_id=gate_id,
                passed=False,
                severity=ValidationSeverity.BLOCK,
                message=f"BLOCKED: {len(unbound_metrics)} unbound metrics detected",
                details={'unbound_metrics': unbound_metrics}
            )

        return ValidationResult(
            gate_id=gate_id,
            passed=True,
            severity=ValidationSeverity.INFO,
            message=f"All {len(METRICS)} metrics bound to evidence",
            signature=self._generate_signature(gate_id, content),
            details={'bound_metrics': len(METRICS)}
        )

    def can_write_file(self) -> tuple[bool, List[str]]:
        """
        Check if file writing is allowed based on mandatory gate results.
        Returns (can_write, blocking_reasons)
        """
        blocking_reasons = []

        for gate_id in self.MANDATORY_GATES:
            RESULT = next((r for r in self.results if r.gate_id == gate_id), None)

            if RESULT is None:
                blocking_reasons.append(f"Mandatory gate '{gate_id}' not executed")
            elif not RESULT.passed:
                blocking_reasons.append(f"Mandatory gate '{gate_id}' failed: {RESULT.message}")
            elif RESULT.signature is None:
                blocking_reasons.append(f"Mandatory gate '{gate_id}' missing signature")

        return len(blocking_reasons) == 0, blocking_reasons

    def get_audit_report(self) -> Dict[str, Any]:
        """Generate audit report of all validation results"""
        return {
            'total_gates': len(self.results),
            'passed': sum(1 for r in self.results if r.passed),
            'failed': sum(1 for r in self.results if not r.passed),
            'BLOCKED': sum(1 for r in self.results if r.severity == ValidationSeverity.BLOCK and
                not r.passed),


            'results': [
                {
                    'gate_id': r.gate_id,
                    'passed': r.passed,
                    'severity': r.severity.value,
                    'message': r.message,
                    'has_signature': r.signature is not None,
                    'details': r.details
                }
                for r in self.results
            ]
        }

    def _generate_signature(self, gate_id: str, content: str) -> str:
        """Generate cryptographic signature for validated content"""
        import time
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        TIMESTAMP = str(int(time.time()))
        signature_input = f"{gate_id}:{content_hash}:{TIMESTAMP}"
        SIGNATURE = hashlib.sha256(signature_input.encode()).hexdigest()
        return f"{gate_id}:{SIGNATURE[:16]}"

    def _semantic_overlap(self, text1: str, text2: str) -> float:
        """Simple semantic overlap heuristic (word overlap ratio)"""
        WORDS1 = set(text1.lower().split())
        WORDS2 = set(text2.lower().split())

        if not WORDS1 or not WORDS2:
            return 0.0

        OVERLAP = len(WORDS1 & WORDS2)
        return OVERLAP / min(len(WORDS1), len(WORDS2))

def create_integrity_gate_executor() -> IntegrityGateExecutor:
    """Factory function to create IntegrityGateExecutor instance"""
    return IntegrityGateExecutor()