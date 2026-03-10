"""
[SSOT] Zero-Tolerance Word Count Enforcement Engine.
Implements 'Regeneration Engine' pattern from legacy system.
Ensures output strictly adheres to min/max constraints.
"""

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

from .regeneration_validator import RegenerationEngine
from .validation_gate import ValidationGate

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    is_valid: bool
    word_count: int
    min_required: int
    max_allowed: int
    violation_type: str | None


class WordCountEnforcementEngine:
    """
    Enforces word count constraints and issues cryptographic proofs.
    """

    def __init__(self, config: dict[str, Any] = None):
        self.config = config or {}
        # Integration: Validation Gate
        self.gate = ValidationGate("VG_WORD_COUNT")
        # Integration: Regeneration Engine (Strategy Pattern)
        self.regenerator = RegenerationEngine()
        # Constraints from v61.27.10
        self.constraints = {
            "executive_summary": {"min": 120, "max": 140},
            "resume_overview": {"min": 25, "max": 33},
            "experience_bullets": {"per_bullet_min": 28, "per_bullet_max": 33},
        }

    def validate_content(self, content: str, content_type: str) -> ValidationResult:
        constraints = self.constraints.get(content_type)
        if not constraints:
            # Open constraints if not defined
            return ValidationResult(True, len(content.split()), 0, 9999, None)

        word_count = len(content.split())
        min_w = constraints["min"]
        max_w = constraints["max"]

        if word_count < min_w:
            return ValidationResult(False, word_count, min_w, max_w, "UNDERFLOW")
        if word_count > max_w:
            return ValidationResult(False, word_count, min_w, max_w, "OVERFLOW")

        return ValidationResult(True, word_count, min_w, max_w, None)

    def enforce_with_regeneration(
        self,
        content: str,
        content_type: str,
        max_attempts: int = 3,
    ) -> dict[str, Any]:
        """
        Attempt to enforce constraints and return signed result.
        Returns Dict containing {content, signature, metadata}.
        """
        current_content = content

        for _attempt in range(max_attempts):
            result = self.validate_content(current_content, content_type)
            if result.is_valid:
                # Sign the valid result
                payload = {
                    "content_hash": hashlib.sha256(current_content.encode()).hexdigest(),
                    "word_count": result.word_count,
                    "status": "VALID",
                }
                signature = self.gate.sign_payload(payload)

                return {
                    "content": current_content,
                    "signature": signature,
                    "validation_payload": payload,
                }

            # Delegated Regeneration (Strategy Pattern)
            # This replaces the hardcoded if/else logic with a formal engine call
            current_content = self.regenerator.regenerate(
                current_content,
                result.violation_type,
                {"min_required": result.min_required, "max_allowed": result.max_allowed},
            )

        raise ValueError(f"Failed to enforce word count for {content_type} after {max_attempts} attempts.")
