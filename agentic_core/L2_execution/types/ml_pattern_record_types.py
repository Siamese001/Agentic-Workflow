"""
L2 MLPatternRecord — Phase 4

Versioned pattern metadata with domain isolation + policy/model hash binding.
All stored healing patterns carry domain_hash, policy_hash, model_hash, and
schema_version. Retrieval enforces compatibility; mismatches are rejected
deterministically (no silent fallback).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class PatternCompatibilityError(Exception):
    """
    Raised when a retrieved pattern is incompatible with the active config.

    Violation codes:
        DOMAIN_HASH_MISMATCH   — pattern domain does not match query domain
        POLICY_HASH_MISMATCH   — pattern policy_hash != active PolicyConfig hash
        MODEL_HASH_MISMATCH    — pattern model_hash != active ModelConfig hash
    """

    DOMAIN_MISMATCH = "DOMAIN_HASH_MISMATCH"
    POLICY_MISMATCH = "POLICY_HASH_MISMATCH"
    MODEL_MISMATCH = "MODEL_HASH_MISMATCH"

    def __init__(self, violation_code: str, message: str) -> None:
        self.violation_code = violation_code
        super().__init__(f"[{violation_code}] {message}")


@dataclass
class MLPatternRecord:
    """
    Versioned healing pattern record stored in L4.

    Required fields:
        schema_version  — int, incremented on breaking schema changes
        domain_id       — str, e.g. "agentic_core", "apps_lic", "apps_rg"
        domain_hash     — sha256 of domain_id (deterministic domain binding)
        policy_hash     — sha256 of active PolicyConfig.canonical_bytes()
        model_hash      — sha256 of active ModelConfig.canonical_bytes()
        pattern_id      — str, unique identifier for this pattern
        payload         — dict, the actual healing strategy/pattern data
        record_hash     — sha256 of canonical_bytes() excluding record_hash
    """

    schema_version: int
    domain_id: str
    domain_hash: str
    policy_hash: str
    model_hash: str
    pattern_id: str
    payload: dict[str, Any]
    record_hash: str

    def __post_init__(self) -> None:
        if self.schema_version < 1:
            raise ValueError(f"schema_version must be >= 1, got {self.schema_version}")
        if not self.domain_id:
            raise ValueError("domain_id must be non-empty")
        if len(self.domain_hash) != 64:
            raise ValueError(f"domain_hash must be 64 hex chars, got len={len(self.domain_hash)}")
        if len(self.policy_hash) != 64:
            raise ValueError(f"policy_hash must be 64 hex chars, got len={len(self.policy_hash)}")
        if len(self.model_hash) != 64:
            raise ValueError(f"model_hash must be 64 hex chars, got len={len(self.model_hash)}")
        if not self.pattern_id:
            raise ValueError("pattern_id must be non-empty")
        if not isinstance(self.payload, dict):
            raise TypeError(f"payload must be a dict, got {type(self.payload).__name__}")
        if len(self.record_hash) != 64:
            raise ValueError(f"record_hash must be 64 hex chars, got len={len(self.record_hash)}")

    def canonical_bytes(self) -> bytes:
        """Deterministic serialization excluding record_hash."""
        doc = {
            "domain_hash": self.domain_hash,
            "domain_id": self.domain_id,
            "model_hash": self.model_hash,
            "pattern_id": self.pattern_id,
            "payload": self.payload,
            "policy_hash": self.policy_hash,
            "schema_version": self.schema_version,
        }
        return json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()

    @staticmethod
    def compute_domain_hash(domain_id: str) -> str:
        return _sha256(domain_id.encode())

    @staticmethod
    def compute_record_hash(
        schema_version: int,
        domain_id: str,
        domain_hash: str,
        policy_hash: str,
        model_hash: str,
        pattern_id: str,
        payload: dict[str, Any],
    ) -> str:
        doc = {
            "domain_hash": domain_hash,
            "domain_id": domain_id,
            "model_hash": model_hash,
            "pattern_id": pattern_id,
            "payload": payload,
            "policy_hash": policy_hash,
            "schema_version": schema_version,
        }
        raw = json.dumps(doc, sort_keys=True, separators=(",", ":"), default=str).encode()
        return _sha256(raw)

    @classmethod
    def build(
        cls,
        domain_id: str,
        policy_hash: str,
        model_hash: str,
        pattern_id: str,
        payload: dict[str, Any],
        schema_version: int = 1,
    ) -> MLPatternRecord:
        """Factory: compute domain_hash and record_hash automatically."""
        domain_hash = cls.compute_domain_hash(domain_id)
        record_hash = cls.compute_record_hash(
            schema_version=schema_version,
            domain_id=domain_id,
            domain_hash=domain_hash,
            policy_hash=policy_hash,
            model_hash=model_hash,
            pattern_id=pattern_id,
            payload=payload,
        )
        return cls(
            schema_version=schema_version,
            domain_id=domain_id,
            domain_hash=domain_hash,
            policy_hash=policy_hash,
            model_hash=model_hash,
            pattern_id=pattern_id,
            payload=payload,
            record_hash=record_hash,
        )


def enforce_pattern_compatibility(
    record: MLPatternRecord, query_domain_id: str, active_policy_hash: str, active_model_hash: str
) -> None:
    """
    Enforce domain isolation + policy/model hash compatibility.

    Raises PatternCompatibilityError deterministically on any mismatch.
    No silent fallback.
    """
    expected_domain_hash = MLPatternRecord.compute_domain_hash(query_domain_id)
    if record.domain_hash != expected_domain_hash:
        raise PatternCompatibilityError(
            PatternCompatibilityError.DOMAIN_MISMATCH,
            f"Pattern domain_hash {record.domain_hash[:8]}... does not match query domain '{query_domain_id}' (expected {expected_domain_hash[:8]}...)",
        )
    if record.policy_hash != active_policy_hash:
        raise PatternCompatibilityError(
            PatternCompatibilityError.POLICY_MISMATCH,
            f"Pattern policy_hash {record.policy_hash[:8]}... != active policy_hash {active_policy_hash[:8]}...",
        )
    if record.model_hash != active_model_hash:
        raise PatternCompatibilityError(
            PatternCompatibilityError.MODEL_MISMATCH,
            f"Pattern model_hash {record.model_hash[:8]}... != active model_hash {active_model_hash[:8]}...",
        )
