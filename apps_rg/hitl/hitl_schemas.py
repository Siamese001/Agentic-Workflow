"""Deterministic HITL schemas for apps_rg governance replay."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BoundedOption:
    option_id: str
    label: str
    description: str
    is_recommended: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeAuthorGateDecisionRequest:
    request_id: str
    trigger_kind: str
    run_id: str
    input_manifest_hash: str
    recommendations: tuple[str, ...]
    confidence_score: float
    evidence_refs: tuple[str, ...]
    bounded_options: tuple[BoundedOption, ...]
    replay_key: str

    def to_dict(self) -> dict[str, object]:
        row = asdict(self)
        row["bounded_options"] = [option.to_dict() for option in self.bounded_options]
        return row


@dataclass(frozen=True)
class HumanReviewDecision:
    decision_id: str
    request_id: str
    chosen_option_id: str
    decision_timestamp: str
    input_manifest_hash: str
    decision_hash: str
    replay_key: str

    @staticmethod
    def compute_hash(
        decision_id: str,
        chosen_option_id: str,
        input_manifest_hash: str,
    ) -> str:
        payload = decision_id + chosen_option_id + input_manifest_hash
        return hashlib.sha256(payload.encode()).hexdigest()

    def verify_hash(self) -> bool:
        return self.decision_hash == self.compute_hash(
            self.decision_id,
            self.chosen_option_id,
            self.input_manifest_hash,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def make_decision_request(
    *,
    trigger_kind: str,
    run_id: str,
    input_manifest_hash: str,
    recommendations: list[str] | tuple[str, ...],
    confidence_score: float,
    evidence_refs: list[str] | tuple[str, ...],
    bounded_options: list[BoundedOption] | tuple[BoundedOption, ...],
    replay_key: str,
) -> RuntimeAuthorGateDecisionRequest:
    """Build a replay-bound HITL decision request."""
    request_id = str(uuid.uuid4())
    return RuntimeAuthorGateDecisionRequest(
        request_id=request_id,
        trigger_kind=trigger_kind,
        run_id=run_id,
        input_manifest_hash=input_manifest_hash,
        recommendations=tuple(recommendations),
        confidence_score=confidence_score,
        evidence_refs=tuple(evidence_refs),
        bounded_options=tuple(bounded_options),
        replay_key=replay_key,
    )


__all__ = [
    "BoundedOption",
    "HumanReviewDecision",
    "RuntimeAuthorGateDecisionRequest",
    "make_decision_request",
]
