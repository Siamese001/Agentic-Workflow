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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
)

_emit_applies_guardrail("p0", "human_decision_artifact_types", "p0_governance")
_emit_snapshots_state("p0", "human_decision_artifact_types", "state_snapshot")

ReviewAction = Literal["APPROVE", "MODIFY_DIFF", "REJECT"]


class HumanDecisionViolation(ValueError):
    """Raised when HumanDecisionArtifact invariants are broken."""


@dataclass(frozen=True)
class HumanDecisionArtifact:
    trace_id: str
    policy_hash: str
    reviewer_id: str
    action: ReviewAction
    original_plan_hash: str
    structured_patch_schema: dict
    reviewer_sig: str = ""
    l5_reclear_required: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        if not self.trace_id:
            raise HumanDecisionViolation("trace_id required")
        if not self.original_plan_hash:
            raise HumanDecisionViolation("original_plan_hash required — must reference submitted plan")
        if self.action == "MODIFY_DIFF" and (not self.structured_patch_schema):
            raise HumanDecisionViolation("structured_patch_schema required for MODIFY_DIFF")
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "HumanDecisionArtifact.sign")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:HumanDecisionArtifact.sign".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
                f"original_plan_hash mismatch: artifact={self.original_plan_hash[:12]} submitted={submitted_plan_hash[:12]}"
            )
