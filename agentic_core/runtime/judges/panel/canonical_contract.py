"""Canonical judge contract — stable digest for multi-provider panels."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping


_REQUIRED_TASK = "GRADE_ONLY"


@dataclass(frozen=True)
class CanonicalJudgeContract:
    """Immutable grading contract consumed by all panel providers."""

    section_id: str
    user_prompt: str
    deterministic_gate_summary: Mapping[str, Any]
    judge_task: str = _REQUIRED_TASK
    output_schema_ref: str = ""
    proof_boundary: Mapping[str, Any] | None = None
    canonical_hash: str | None = None

    def contract_hash(self) -> str:
        if self.canonical_hash:
            return self.canonical_hash
        return compute_contract_hash(self)

    def input_hash(self) -> str:
        return compute_contract_hash(self)[:16]


def compute_contract_hash(contract: CanonicalJudgeContract) -> str:
    """SHA-256 hex of canonical serialization (all providers must log this)."""
    payload = {
        "judge_task": contract.judge_task,
        "section_id": contract.section_id,
        "user_prompt": contract.user_prompt,
        "deterministic_gate_summary": dict(contract.deterministic_gate_summary),
        "output_schema_ref": contract.output_schema_ref,
        "proof_boundary": dict(contract.proof_boundary or {}),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_contract(contract: CanonicalJudgeContract) -> list[str]:
    """Return human-readable validation errors (empty if OK)."""
    errors: list[str] = []
    if str(contract.judge_task).upper() != _REQUIRED_TASK:
        errors.append(f"judge_task must be {_REQUIRED_TASK!r}, got {contract.judge_task!r}")
    if not str(contract.section_id).strip():
        errors.append("section_id is required")
    if not str(contract.user_prompt).strip():
        errors.append("user_prompt is required")
    if not contract.deterministic_gate_summary:
        errors.append("deterministic_gate_summary is required")
    boundary = contract.proof_boundary or {}
    for flag in (
        "jd_is_targeting_context_only",
        "briefing_is_targeting_context_only",
        "judges_must_not_rewrite",
    ):
        if flag in boundary and boundary[flag] is not True:
            errors.append(f"proof_boundary.{flag} must be true when present")
    return errors


__all__ = [
    "CanonicalJudgeContract",
    "compute_contract_hash",
    "validate_contract",
]
