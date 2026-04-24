"""Bus-U reason-prior publication adapter (W3.1).

Publishes approved reason priors (L1 planning hints derived from
approved-after-review learning events) to the next-run surface via UWG.
Mirrors the shape of ``rubric_publication_adapter`` so both channels share
the same proposal-only / UWG-sole-ink-path discipline.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ReasonPriorProposal:
    proposal_id: str
    priority: int                   # higher = stronger nudge at L1 planning
    applies_to_intent: str          # intent class key (e.g. "rag.answer")
    prior_body: dict[str, Any]      # opaque to adapter; L1 consumes
    rationale: str
    submitted_by: str
    created_at: str


def _proposal_id(intent: str, body: dict[str, Any]) -> str:
    payload = json.dumps({"i": intent, "b": body}, sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"reason-prior-{intent}-{digest}"


def build_proposal(
    applies_to_intent: str,
    prior_body: dict[str, Any],
    priority: int,
    rationale: str,
    submitted_by: str,
    created_at: str,
) -> ReasonPriorProposal:
    if priority < 0 or priority > 10:
        raise ValueError("priority must be in [0, 10]")
    return ReasonPriorProposal(
        proposal_id=_proposal_id(applies_to_intent, prior_body),
        priority=priority,
        applies_to_intent=applies_to_intent,
        prior_body=prior_body,
        rationale=rationale,
        submitted_by=submitted_by,
        created_at=created_at,
    )


def publish_via_uwg(proposal: ReasonPriorProposal, writer: Any) -> str:
    payload = json.dumps(proposal.__dict__, sort_keys=True).encode("utf-8")
    version_id = writer.write(component="reason_prior_proposal", payload=payload)
    logger.info(
        "reason-prior proposal %s published via UWG (version=%s, intent=%s, priority=%d)",
        proposal.proposal_id, version_id, proposal.applies_to_intent, proposal.priority,
    )
    return version_id
