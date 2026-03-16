"""
[SSOT] Zero-Tolerance Word Count Enforcement Engine.
Implements 'Regeneration Engine' pattern from legacy system.
Ensures output strictly adheres to min/max constraints.
"""

import hashlib
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from .regeneration_validator import RegenerationEngine
from .validation_gate import ValidationGate

_emit_applies_guardrail("p0", "validation_result_validator", "p0_governance")
_emit_reads_policy_state("p0", "validation_result_validator", "policy_binding")
_emit_snapshots_state("p0", "validation_result_validator", "state_snapshot")
emit_replay_key("p0", "validation_result_validator")
emit_determinism_digest("p0", "validation_result_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        self.gate = ValidationGate("VG_WORD_COUNT")
        self.regenerator = RegenerationEngine()
        self.constraints = {
            "executive_summary": {"min": 120, "max": 140},
            "resume_overview": {"min": 25, "max": 33},
            "experience_bullets": {"per_bullet_min": 28, "per_bullet_max": 33},
        }

    def validate_content(self, content: str, content_type: str) -> ValidationResult:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "WordCountEnforcementEngine.validate_content")

        constraints = self.constraints.get(content_type)
        if not constraints:
            return ValidationResult(True, len(content.split()), 0, 9999, None)
        word_count = len(content.split())
        min_w = constraints["min"]
        max_w = constraints["max"]
        if word_count < min_w:
            return ValidationResult(False, word_count, min_w, max_w, "UNDERFLOW")
        if word_count > max_w:
            return ValidationResult(False, word_count, min_w, max_w, "OVERFLOW")
        return ValidationResult(True, word_count, min_w, max_w, None)

    # guardian: allow-magic-config
    def enforce_with_regeneration(
        self, content: str, content_type: str, max_attempts: int = 3
    ) -> dict[str, Any]:
        """
        Attempt to enforce constraints and return signed result.
        Returns Dict containing {content, signature, metadata}.
        """
        current_content = content
        for _attempt in range(max_attempts):
            result = self.validate_content(current_content, content_type)
            if result.is_valid:
                payload = {
                    "content_hash": hashlib.sha256(current_content.encode()).hexdigest(),
                    "word_count": result.word_count,
                    "status": "VALID",
                }
                signature = self.gate.sign_payload(payload)
                return {"content": current_content, "signature": signature, "validation_payload": payload}
            current_content = self.regenerator.regenerate(
                current_content,
                result.violation_type,
                {"min_required": result.min_required, "max_allowed": result.max_allowed},
            )
        raise ValueError(f"Failed to enforce word count for {content_type} after {max_attempts} attempts.")
