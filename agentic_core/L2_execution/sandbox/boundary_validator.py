"""Addendum 1.2: Transcript–Mutation Cross Check (boundary validator).

After execution, verify:
    computed_diff = diff(boundary_snapshot_pre, boundary_snapshot_post)
    assert computed_diff == UWG.state_diff

Violation: Mismatch → raise MutationReplayIntegrityViolation, HARD FAIL.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def _snapshot_hash(snapshot: dict[str, Any]) -> str:
    raw = json.dumps(snapshot, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def compute_boundary_diff(snapshot_pre: dict[str, Any], snapshot_post: dict[str, Any]) -> dict[str, Any]:
    """Compute a deterministic diff between two boundary snapshots.

    Returns a dict mapping changed keys to (pre_value, post_value) tuples.
    Only top-level key changes are tracked for simplicity.
    """
    all_keys = set(snapshot_pre) | set(snapshot_post)
    diff: dict[str, Any] = {}
    for key in sorted(all_keys):
        pre_val = snapshot_pre.get(key)
        post_val = snapshot_post.get(key)
        if pre_val != post_val:
            diff[key] = {"pre": pre_val, "post": post_val}
    return diff


def _diff_hash(diff: dict[str, Any]) -> str:
    raw = json.dumps(diff, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_mutation_replay_integrity(
    snapshot_pre: dict[str, Any], snapshot_post: dict[str, Any], uwg_state_diff: dict[str, Any]
) -> None:
    """Verify that the observed boundary diff matches the UWG-recorded state_diff.

    Raises MutationReplayIntegrityViolation on mismatch.

    Wire into _run_heal_pipeline() Phase 3 validation.
    """
    computed = compute_boundary_diff(snapshot_pre, snapshot_post)
    computed_h = _diff_hash(computed)
    uwg_h = _diff_hash(uwg_state_diff)
    if computed_h != uwg_h:
        logger.error(
            "MutationReplayIntegrityViolation: computed_diff_hash=%s uwg_diff_hash=%s",
            computed_h[:16],
            uwg_h[:16],
        )
        raise MutationReplayIntegrityViolation(
            f"Boundary diff hash mismatch: computed={computed_h[:16]}... uwg={uwg_h[:16]}... Execution transcript does not match recorded mutations."
        )
    logger.debug("Mutation replay integrity OK: diff_hash=%s", computed_h[:16])


__all__ = ["compute_boundary_diff", "verify_mutation_replay_integrity"]
