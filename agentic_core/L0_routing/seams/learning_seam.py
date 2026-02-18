"""
Seam for adaptive learning intent delegation — approved L0 interface.

This seam defines the LearningArtifactIntent frozen dataclass and the
LearningPersistenceService protocol.  Per SFE-1 (intent artifacts, not
delegation) agents emit frozen intents; only L2 persists them.

Per SFE-3 (seams precede consumers) this file MUST exist before any
agent integration code references LearningArtifactIntent.

Hardening item: H5 — Frozen LearningArtifactIntent with pre-L2 hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Protocol


def _canonical_bytes(
    agent_id: str,
    execution_id: str,
    outcome: str,
    metrics: tuple[tuple[str, float], ...],
    context_hash: str,
) -> bytes:
    """Produce deterministic canonical bytes for hash computation.

    Uses sorted-key JSON with no whitespace variance, matching the
    CanonicalSerializationSpec from the enterprise plan.
    """
    payload = {
        "agent_id": agent_id,
        "context_hash": context_hash,
        "execution_id": execution_id,
        "metrics": [[k, v] for k, v in metrics],
        "outcome": outcome,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class LearningArtifactIntent:
    """Immutable intent object emitted by agents for L2 persistence.

    Fields are frozen at construction.  ``intent_hash`` is the
    sha-256 of the canonical serialisation of all other fields and
    MUST be computed before the intent leaves the emitting layer.

    L2 verifies ``intent_hash`` on receipt before persisting.
    """

    agent_id: str
    execution_id: str
    outcome: str
    metrics: tuple[tuple[str, float], ...]
    context_hash: str
    intent_hash: str

    @staticmethod
    def create(
        *,
        agent_id: str,
        execution_id: str,
        outcome: str,
        metrics: tuple[tuple[str, float], ...],
        context_hash: str,
    ) -> LearningArtifactIntent:
        """Construct an intent with a pre-computed hash.

        This is the ONLY approved construction path.  Direct
        ``__init__`` is allowed but callers are responsible for
        providing a correct ``intent_hash``.
        """
        canonical = _canonical_bytes(
            agent_id=agent_id,
            execution_id=execution_id,
            outcome=outcome,
            metrics=metrics,
            context_hash=context_hash,
        )
        intent_hash = hashlib.sha256(canonical).hexdigest()
        return LearningArtifactIntent(
            agent_id=agent_id,
            execution_id=execution_id,
            outcome=outcome,
            metrics=metrics,
            context_hash=context_hash,
            intent_hash=intent_hash,
        )

    def verify(self) -> bool:
        """Re-derive hash and compare — used by L2 on receipt."""
        canonical = _canonical_bytes(
            agent_id=self.agent_id,
            execution_id=self.execution_id,
            outcome=self.outcome,
            metrics=self.metrics,
            context_hash=self.context_hash,
        )
        return hashlib.sha256(canonical).hexdigest() == self.intent_hash


class LearningPersistenceService(Protocol):
    """Protocol that L2 implements to persist learning intents.

    No layer other than L2 may implement durable writes.
    """

    def persist_learning_intent(self, intent: LearningArtifactIntent) -> bool:
        """Persist a verified learning intent.

        Returns True on success, False on rejection.
        Implementations MUST call ``intent.verify()`` before
        writing.
        """
        ...
