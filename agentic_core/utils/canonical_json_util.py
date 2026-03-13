"""
CanonicalJSON — SSOT serializer for cryptographic boundaries.

This is the ONLY authorized JSON serialization path for:
- InstructionPacket signing surface
- SandboxEnvelope signing surface
- ExecutionTrace hashing
- Determinism digest construction

AST enforcement (ops_scripts/ci/ast_canonical_scanner.py) will fail any
direct json.dumps usage in L2 execution paths outside this module.

Normalization rules (identical to canonical_serializer_util):
  1. Sorted keys (recursive)
  2. Compact separators (",", ":") — no whitespace variance
  3. ensure_ascii=True
  4. UTF-8 byte encoding only
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


class CanonicalJSON:
    """Single source of truth for deterministic JSON serialization."""

    @staticmethod
    def serialize(obj: Any) -> str:
        """Return deterministic JSON string (sorted keys, compact separators)."""
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    @staticmethod
    def serialize_bytes(obj: Any) -> bytes:
        """Return deterministic UTF-8 bytes for HMAC/hash computation."""
        return CanonicalJSON.serialize(obj).encode("utf-8")

    @staticmethod
    def serialize_hash(obj: Any) -> str:
        """Return SHA-256 hex digest of canonical serialization."""
        return hashlib.sha256(CanonicalJSON.serialize_bytes(obj)).hexdigest()


__all__ = ["CanonicalJSON"]
