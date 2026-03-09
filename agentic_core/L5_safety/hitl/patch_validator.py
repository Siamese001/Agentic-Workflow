"""Addendum 6.1: Human-in-the-Loop Patch Validator.

Every MODIFY_DIFF patch MUST include:
  - original_plan_hash
  - structured_patch_schema
  - reviewer_signature

Violation: Missing fields → raise HumanPatchValidationError.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError

logger = logging.getLogger(__name__)

_REQUIRED_FIELDS = frozenset({"original_plan_hash", "structured_patch_schema", "reviewer_signature"})


@dataclass
class ValidatedPatch:
    """A patch that has passed HITL validation."""

    original_plan_hash: str
    structured_patch_schema: dict[str, Any]
    reviewer_signature: str
    patch_hash: str
    raw: dict[str, Any]


def validate_patch(patch: dict[str, Any]) -> ValidatedPatch:
    """Validate a MODIFY_DIFF patch has all required HITL fields.

    Raises HumanPatchValidationError if any required field is missing or empty.
    Returns a ValidatedPatch on success.
    """
    missing = [f for f in sorted(_REQUIRED_FIELDS) if not patch.get(f)]
    if missing:
        raise HumanPatchValidationError(
            f"HITL patch missing required field(s): {missing}. "
            "All MODIFY_DIFF patches must include: original_plan_hash, "
            "structured_patch_schema, reviewer_signature."
        )

    patch_hash = hashlib.sha256(
        json.dumps(patch, sort_keys=True, ensure_ascii=True, default=str).encode()
    ).hexdigest()

    logger.info(
        "HITL patch validated: reviewer=%s patch_hash=%s",
        patch.get("reviewer_signature", "")[:16],
        patch_hash[:16],
    )

    return ValidatedPatch(
        original_plan_hash=patch["original_plan_hash"],
        structured_patch_schema=patch["structured_patch_schema"],
        reviewer_signature=patch["reviewer_signature"],
        patch_hash=patch_hash,
        raw=patch,
    )


__all__ = ["validate_patch", "ValidatedPatch"]
