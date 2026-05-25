"""Bus-U rubric publication adapter (W3.1).

v33 §6D promises that Bus U publishes prompts, policies, baselines, rubrics,
and approved reason priors. Retrieval profiles and policy recommendations
already flow through UWG via existing adapters; this adapter adds the
rubric channel so rubric revisions approved by the gauntlet are published
the same way.

Contract:
  - The adapter is proposal-only: it never mutates the live rubrics file.
  - Approved proposals are routed through ``L4StateWriter`` (content-hash
    keyed, idempotent).
  - Downstream judges pick up the new active rubric version at next
    pipeline start; no runtime mutation.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RubricProposal:
    proposal_id: str
    target_rubric_path: str            # e.g. "config/judges/rubrics.yaml"
    rubric_family: str                 # rag | governance | security
    dimension: str
    change_type: str                   # "add" | "revise" | "retire"
    new_spec: dict[str, Any]
    rationale: str
    submitted_by: str
    created_at: str


def _proposal_id(family: str, dimension: str, spec: dict[str, Any]) -> str:
    payload = json.dumps({"f": family, "d": dimension, "s": spec}, sort_keys=True)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"rubric-{family}-{dimension}-{digest}"


def build_proposal(
    rubric_family: str,
    dimension: str,
    change_type: str,
    new_spec: dict[str, Any],
    rationale: str,
    submitted_by: str,
    created_at: str,
    target_rubric_path: str = "config/judges/rubrics.yaml",
) -> RubricProposal:
    if change_type not in {"add", "revise", "retire"}:
        raise ValueError(f"invalid change_type: {change_type}")
    return RubricProposal(
        proposal_id=_proposal_id(rubric_family, dimension, new_spec),
        target_rubric_path=target_rubric_path,
        rubric_family=rubric_family,
        dimension=dimension,
        change_type=change_type,
        new_spec=new_spec,
        rationale=rationale,
        submitted_by=submitted_by,
        created_at=created_at,
    )


def publish_via_uwg(proposal: RubricProposal, writer: Any) -> str:
    """Route the proposal through the L4 state writer.

    ``writer`` must implement ``write(component: str, payload: bytes) -> str``
    (version_id). This matches ``FileBackedL4StateWriter`` / ``InMemoryL4StateWriter``
    / ``NoOpL4StateWriter`` in ``system_learning.engines.l4_state_writer``.
    """
    payload = json.dumps(proposal.__dict__, sort_keys=True).encode("utf-8")
    version_id = writer.write(component="rubric_proposal", payload=payload)
    logger.info(
        "rubric proposal %s published via UWG (version=%s, family=%s, dim=%s)",
        proposal.proposal_id, version_id, proposal.rubric_family, proposal.dimension,
    )
    return version_id
