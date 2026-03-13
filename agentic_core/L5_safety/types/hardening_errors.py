"""Hardening error types for all Addendum enforcement violations.

All new error types from the Master Hardening Consolidation Addendum.
"""

from __future__ import annotations


class ExecutionTraceIntegrityError(RuntimeError):
    """Raised when ExecutionTrace is missing required fields (Addendum 1.1)."""


class MutationReplayIntegrityViolation(RuntimeError):
    """Raised when computed diff != UWG state_diff (Addendum 1.2)."""


class LedgerIntegrityViolation(RuntimeError):
    """Raised when ledger hash chain is broken (Addendum 2.2)."""


class MutationCommitFailure(RuntimeError):
    """Raised when 2PC commit fails (either ACK missing) (Addendum 2.3)."""


class C0AuthorityLeakError(RuntimeError):
    """Raised when C0 RAG payload contains authority fields (Addendum 3.1)."""


class C0MutationViolation(RuntimeError):
    """Raised when C0 context payload is mutated during assembly (Addendum 3.2)."""


class RuntimePolicyMutationViolation(RuntimeError):
    """Raised when runtime config is modified during meta-learning S1-S8 (Addendum 5.2)."""


class HumanPatchValidationError(RuntimeError):
    """Raised when a human patch is missing required fields (Addendum 6.1)."""


class HumanPatchL5ClearanceError(RuntimeError):
    """Raised when a human patch bypasses L5 re-clearance (Addendum 6.2)."""


__all__ = [
    "ExecutionTraceIntegrityError",
    "MutationReplayIntegrityViolation",
    "LedgerIntegrityViolation",
    "MutationCommitFailure",
    "C0AuthorityLeakError",
    "C0MutationViolation",
    "RuntimePolicyMutationViolation",
    "HumanPatchValidationError",
    "HumanPatchL5ClearanceError",
]
