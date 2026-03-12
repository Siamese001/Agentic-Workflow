from __future__ import annotations
import hashlib
from typing import Any, NamedTuple
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
HealedPlan = dict[str, Any]

class StaleSignatureViolation(Exception):
    """Raised when a healed plan is executed with a stale signature."""
    pass

class InvalidationResult(NamedTuple):
    """The result of invalidating a plan's signature."""
    invalidated_plan: HealedPlan
    new_policy_hash: str

def invalidate_signature_and_rehash(plan: HealedPlan) -> InvalidationResult:
    """
    Strips cryptographic signatures and regenerates the policy hash for a healed plan.

    This is a critical step for Guarantee #4. After a plan is modified by a
    healing agent, its original approval signature is no longer valid. This
    function ensures the old signature is removed and a new policy hash is
    generated from the modified content, forcing a full L5 re-validation.

    Args:
        plan: The healed plan that has been modified.

    Returns:
        An InvalidationResult containing the plan with its signature stripped
        and a new policy hash for re-validation.
    """
    invalidated_plan = plan.copy()
    invalidated_plan.pop('l5_signature', None)
    invalidated_plan.pop('l5_approval_timestamp', None)
    invalidated_plan.pop('policy_hash', None)
    import json
    canonical_string = json.dumps(invalidated_plan, sort_keys=True, separators=(',', ':')).encode('utf-8')
    new_policy_hash = hashlib.sha256(canonical_string).hexdigest()
    invalidated_plan['policy_hash'] = new_policy_hash
    return InvalidationResult(invalidated_plan=invalidated_plan, new_policy_hash=new_policy_hash)

def verify_no_stale_signature(plan: HealedPlan):
    """
    Verifies that a plan about to be executed does not contain a stale signature.

    This would be called by the execution gateway before committing a change.
    It's a final check to prevent a bypass of the re-clear loop.

    Args:
        plan: The plan to be checked.

    Raises:
        StaleSignatureViolation: If a signature is present on a healed plan that
                                 should have been invalidated.
    """
    if 'healed_by' in plan and 'l5_signature' in plan:
        raise StaleSignatureViolation('Healed plan contains a stale L5 signature. It must be re-validated.')
