"""HumanDecisionArtifact — spec contract [5].

MODIFY_DIFF MUST reference original_plan_hash and force L5 re-clear.
Prior plan signature is STRICTLY INVALID after MODIFY_DIFF.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from typing import Literal

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

ReviewAction = Literal["APPROVE", "MODIFY_DIFF", "REJECT"]


class HumanDecisionViolation(ValueError):
    """Raised when HumanDecisionArtifact invariants are broken."""


@dataclass(frozen=True)
class HumanDecisionArtifact:
    trace_id: str
    policy_hash: str
    reviewer_id: str
    action: ReviewAction
    original_plan_hash: str  # MUST match plan submitted to Path D
    structured_patch_schema: dict  # Only for MODIFY_DIFF; {} otherwise
    reviewer_sig: str = ""
    l5_reclear_required: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise HumanDecisionViolation("trace_id required")
        if not self.original_plan_hash:
            raise HumanDecisionViolation("original_plan_hash required — must reference submitted plan")
        if self.action == "MODIFY_DIFF" and not self.structured_patch_schema:
            raise HumanDecisionViolation("structured_patch_schema required for MODIFY_DIFF")
        # MODIFY_DIFF always forces L5 re-clear
        object.__setattr__(self, "l5_reclear_required", self.action == "MODIFY_DIFF")

    def _signable_dict(self) -> dict:
        return {
            "action": self.action,
            "original_plan_hash": self.original_plan_hash,
            "policy_hash": self.policy_hash,
            "reviewer_id": self.reviewer_id,
            "trace_id": self.trace_id,
        }

    def sign(self, secret: bytes) -> HumanDecisionArtifact:
        mac = hmac.new(
            secret,
            json.dumps(self._signable_dict(), sort_keys=True, separators=(",", ":")).encode("ascii"),
            hashlib.sha256,
        )
        return HumanDecisionArtifact(
            trace_id=self.trace_id,
            policy_hash=self.policy_hash,
            reviewer_id=self.reviewer_id,
            action=self.action,
            original_plan_hash=self.original_plan_hash,
            structured_patch_schema=self.structured_patch_schema,
            reviewer_sig=mac.hexdigest().lower(),
        )

    def verify(self, secret: bytes) -> None:
        if not self.reviewer_sig:
            raise HumanDecisionViolation("reviewer_sig absent")
        mac = hmac.new(
            secret,
            json.dumps(self._signable_dict(), sort_keys=True, separators=(",", ":")).encode("ascii"),
            hashlib.sha256,
        )
        if not hmac.compare_digest(self.reviewer_sig, mac.hexdigest().lower()):
            raise HumanDecisionViolation("reviewer_sig mismatch — artifact tampered")

    def assert_plan_hash_matches(self, submitted_plan_hash: str) -> None:
        """Hard-fail if this artifact references a different plan than what was submitted."""
        if self.original_plan_hash != submitted_plan_hash:
            raise HumanDecisionViolation(
                f"original_plan_hash mismatch: artifact={self.original_plan_hash[:12]} "
                f"submitted={submitted_plan_hash[:12]}"
            )
