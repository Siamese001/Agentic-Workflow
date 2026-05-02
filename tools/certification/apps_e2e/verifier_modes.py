"""Verifier mode enum + dispatch helper.

Plan: apps-e2e-two-gate-certification-d8b3a1 §5.

Three modes:
  - smoke   — bundle valid + every declared *_ref hash-verifies. Receipts
              that aren't in the bundle are NOT required.
  - warn    — like smoke but always exits 0; emits gap diff to stderr.
  - strict  — receipts in required_receipts(spec) MUST be declared, present,
              hash-verified, registered in the artifact manifest with the
              correct ArtifactKind, and the computed certification_level
              MUST be SPINE_COMPLETE_CERTIFIED for certification_required apps.

`--mode` is REQUIRED on the verifier CLI (no default — forces a deliberate
choice in scripts).
"""
from __future__ import annotations

from enum import Enum


class VerifierMode(str, Enum):
    SMOKE = "smoke"
    WARN = "warn"
    STRICT = "strict"

    @classmethod
    def values(cls) -> frozenset[str]:
        return frozenset(member.value for member in cls)


def parse_mode(value: str) -> VerifierMode:
    """Parse a mode string to a VerifierMode. Case-insensitive. Raises ValueError on unknown."""
    if not value:
        raise ValueError("--mode is required (smoke, warn, or strict)")
    v = value.strip().lower()
    for m in VerifierMode:
        if m.value == v:
            return m
    raise ValueError(f"unknown verifier mode {value!r}; expected one of {sorted(VerifierMode.values())}")


def exit_code_for(mode: VerifierMode, has_violations: bool) -> int:
    """Compute the exit code for a verifier run.

    smoke    -> 1 if violations else 0
    warn     -> 0 always
    strict   -> 1 if violations else 0
    """
    if mode == VerifierMode.WARN:
        return 0
    return 1 if has_violations else 0


__all__ = ["VerifierMode", "parse_mode", "exit_code_for"]
