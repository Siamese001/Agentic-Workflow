"""L5 safety exception hierarchy.

Evidence-only boundary: these exceptions carry no runtime dispositions,
gate verdicts, or durable-write authority.  They signal producer-side
failures (malformed inputs, authority widening attempts, digest mismatches)
so callers can decide how to handle them.

This module is import-clean: no provider SDKs, no app-specific literals,
no network calls, no filesystem writes, and no runtime disposition imports.
"""
from __future__ import annotations


class L5CertificationError(Exception):
    """Base exception for L5 certification producer failures.

    Raised for hard structural faults that prevent the producer from
    assembling a well-formed packet (e.g. schema violations that cannot
    be expressed as L5_NOT_CERTIFIED without corrupting the evidence model).
    """


class L5AuthorityWideningError(L5CertificationError):
    """Raised when the producer detects an authority-widening attempt.

    The producer must not invent principal, capability, sandbox, provider,
    model, tool, network, or filesystem authority beyond what is present in
    the explicit inputs and child receipts.  When a widening is detected,
    this error is raised so callers fail closed.
    """


class L5DigestMismatchError(L5CertificationError):
    """Raised when a child receipt or egress receipt digest does not match
    the canonical l5_governance_context_digest computed by the producer.

    Fail-closed: a digest mismatch means the evidence set is incoherent and
    a valid L5CertificationPacket cannot be constructed.
    """


class L5MalformedReceiptError(L5CertificationError):
    """Raised when a child or egress receipt is structurally invalid in a way
    that cannot be represented by L5_NOT_CERTIFIED without loss of auditability.

    Distinct from missing-required-child (which returns L5_NOT_CERTIFIED) —
    this is reserved for inputs that violate the contract dataclass invariants
    so severely that the producer cannot safely interpret them.
    """


__all__ = [
    "L5CertificationError",
    "L5AuthorityWideningError",
    "L5DigestMismatchError",
    "L5MalformedReceiptError",
]
