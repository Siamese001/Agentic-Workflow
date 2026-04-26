"""PA.3 H0 Healer Re-Entry Validator (spec lines 1010–1063).

H0 healing hints are PROPOSED corrections, never automatic authority. They
must:

    1. Carry the same policy_hash and blueprint_hash as the failed run.
    2. Not widen scope beyond the failed task.
    3. Respect the configured retry threshold (default 2).
    4. Survive S0/D0/I0 authority — never override fences.
"""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_MAX_RETRIES: int = 2


@dataclass(frozen=True)
class H0ReentryResult:
    accepted: bool
    same_policy_hash: bool
    same_blueprint_hash: bool
    no_scope_widening: bool
    retry_count_within_threshold: bool
    retry_count: int
    max_retries: int
    rejection_reason: str = ""


def validate_h0_reentry(
    *,
    h0_content: str,
    h0_policy_hash: str,
    h0_blueprint_hash: str,
    current_policy_hash: str,
    current_blueprint_hash: str,
    retry_count: int,
    max_retries: int = DEFAULT_MAX_RETRIES,
    original_task_keywords: tuple[str, ...] = (),
    h0_task_keywords: tuple[str, ...] = (),
) -> H0ReentryResult:
    """Validate a healer-proposed H0 hint per spec re-entry rules."""
    same_policy = bool(h0_policy_hash) and h0_policy_hash == current_policy_hash
    same_blueprint = bool(h0_blueprint_hash) and h0_blueprint_hash == current_blueprint_hash

    no_widening = True
    if original_task_keywords and h0_task_keywords:
        new_keywords = set(h0_task_keywords) - set(original_task_keywords)
        # If the H0 introduces concepts absent from the original task it has widened scope.
        no_widening = len(new_keywords) <= 1

    within_retry = retry_count <= max_retries

    rejection = ""
    if not h0_content:
        rejection = "h0_empty"
    elif not same_policy:
        rejection = "h0_policy_hash_mismatch"
    elif not same_blueprint:
        rejection = "h0_blueprint_hash_mismatch"
    elif not no_widening:
        rejection = "h0_scope_widening_detected"
    elif not within_retry:
        rejection = "h0_retry_threshold_exceeded"

    accepted = bool(h0_content) and same_policy and same_blueprint and no_widening and within_retry
    return H0ReentryResult(
        accepted=accepted,
        same_policy_hash=same_policy,
        same_blueprint_hash=same_blueprint,
        no_scope_widening=no_widening,
        retry_count_within_threshold=within_retry,
        retry_count=retry_count,
        max_retries=max_retries,
        rejection_reason=rejection,
    )


__all__ = ["DEFAULT_MAX_RETRIES", "H0ReentryResult", "validate_h0_reentry"]
