"""L4 State: Semantic Cache Admission Gate.

Separates semantic cache admission from durable learning by enforcing four
admission criteria before a retrieval result is allowed into Redis DB-0:

  1. **Support validation** — at least one retrieved document directly supports
     the query (support_score >= support_threshold).
  2. **Completeness** — the retrieved set covers the query family sufficiently
     (completeness_score >= completeness_threshold).
  3. **Policy clearance** — no policy conflict flag is set for this query.
  4. **Replay safety** — no replay-sensitive contamination in the result set.

Only entries passing all four gates are admitted.  The gate outcome is recorded
as a ``CacheAdmissionDecision`` (frozen dataclass) and can be stored in the
``rag_admit`` key schema (see ``cache_key_builders.build_rag_admission_key``).

Design invariants
-----------------
1. No wall-clock reads — ``timestamp_utc`` is caller-supplied.
2. No side effects — this module only evaluates and records decisions.
3. Fail-closed on errors: if any gate check raises, admission is DENIED.
4. Thresholds are explicit parameters — no hidden magic constants in logic.
5. The gate does NOT write to Redis itself; callers use the returned decision
   to determine whether to call the cache ``set`` method.

Architecture connection
-----------------------
This implements the architecture design point:
  "Only admit Redis cache entries when:
   - support validation passes
   - completeness score passes threshold
   - no policy conflict
   - no replay-sensitive contamination"
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Literal

from system_learning.enforcement.determinism import deterministic_json, stable_sha256_json

logger = logging.getLogger(__name__)

# Default thresholds — callers should override for their domain
_DEFAULT_SUPPORT_THRESHOLD: float = 0.6
_DEFAULT_COMPLETENESS_THRESHOLD: float = 0.5


# ---------------------------------------------------------------------------
# Admission decision record
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CacheAdmissionDecision:
    """Frozen record of a single cache admission gate evaluation.

    Attributes
    ----------
    artifact_type:
        Always ``CACHE_ADMISSION_DECISION``.
    query_hash:
        SHA-256 hexdigest of the query (u0_hash).
    policy_hash:
        SHA-256 hexdigest of the active policy.
    embedder_version:
        Embedder version tag used for this retrieval.
    admitted:
        True if all four gates passed.
    deny_reasons:
        Tuple of stable deny reason codes (empty when admitted).
    support_score:
        Support validation score supplied by the caller.
    completeness_score:
        Completeness score supplied by the caller.
    policy_conflict:
        True if a policy conflict was detected.
    replay_contaminated:
        True if replay-sensitive content was found in the result set.
    timestamp_utc:
        Unix timestamp provided by the caller.
    """

    artifact_type: Literal["CACHE_ADMISSION_DECISION"]
    query_hash: str
    policy_hash: str
    embedder_version: str
    admitted: bool
    deny_reasons: tuple[str, ...]
    support_score: float
    completeness_score: float
    policy_conflict: bool
    replay_contaminated: bool
    timestamp_utc: int

    def to_dict(self) -> dict[str, object]:
        return {
            "admitted": self.admitted,
            "artifact_type": self.artifact_type,
            "completeness_score": self.completeness_score,
            "deny_reasons": list(self.deny_reasons),
            "embedder_version": self.embedder_version,
            "policy_conflict": self.policy_conflict,
            "policy_hash": self.policy_hash,
            "query_hash": self.query_hash,
            "replay_contaminated": self.replay_contaminated,
            "support_score": self.support_score,
            "timestamp_utc": self.timestamp_utc,
        }

    def to_json(self) -> str:
        return deterministic_json(self.to_dict())

    def stable_hash(self) -> str:
        return stable_sha256_json(self.to_dict())


# Stable deny reason codes
DENY_SUPPORT_BELOW_THRESHOLD = "SUPPORT_BELOW_THRESHOLD"
DENY_COMPLETENESS_BELOW_THRESHOLD = "COMPLETENESS_BELOW_THRESHOLD"
DENY_POLICY_CONFLICT = "POLICY_CONFLICT"
DENY_REPLAY_CONTAMINATED = "REPLAY_CONTAMINATED"


# ---------------------------------------------------------------------------
# CacheAdmissionGate
# ---------------------------------------------------------------------------


class CacheAdmissionGate:
    """Evaluates four admission criteria before allowing a retrieval result
    into the semantic cache.

    Usage
    -----
    .. code-block:: python

        gate = CacheAdmissionGate(
            support_threshold=0.65,
            completeness_threshold=0.55,
        )

        decision = gate.evaluate(
            query_hash="a3f7b291..." * 2,   # 64-char SHA-256
            policy_hash="deadbeef..." * 2,
            embedder_version="bge-m3-v1",
            support_score=0.72,
            completeness_score=0.60,
            policy_conflict=False,
            replay_contaminated=False,
            timestamp_utc=1700000000,
        )

        if decision.admitted:
            redis_cache.set(admission_key, result_bytes, ttl_seconds=3600)
    """

    def __init__(
        self,
        support_threshold: float = _DEFAULT_SUPPORT_THRESHOLD,
        completeness_threshold: float = _DEFAULT_COMPLETENESS_THRESHOLD,
    ) -> None:
        if not (0.0 <= support_threshold <= 1.0):
            raise ValueError(f"support_threshold must be in [0, 1], got {support_threshold}")
        if not (0.0 <= completeness_threshold <= 1.0):
            raise ValueError(f"completeness_threshold must be in [0, 1], got {completeness_threshold}")
        self.support_threshold = support_threshold
        self.completeness_threshold = completeness_threshold
        self._stats: dict[str, int] = {
            "admitted": 0,
            "denied_support": 0,
            "denied_completeness": 0,
            "denied_policy": 0,
            "denied_replay": 0,
            "errors": 0,
        }

    def evaluate(
        self,
        *,
        query_hash: str,
        policy_hash: str,
        embedder_version: str,
        support_score: float,
        completeness_score: float,
        policy_conflict: bool,
        replay_contaminated: bool,
        timestamp_utc: int,
    ) -> CacheAdmissionDecision:
        """Evaluate all four admission gates and return a decision record.

        Fail-closed: any unexpected error during evaluation produces a DENIED
        decision with ``INTERNAL_ERROR`` in deny_reasons.

        Parameters
        ----------
        query_hash:
            SHA-256 hexdigest of the query (u0_hash).
        policy_hash:
            SHA-256 hexdigest of the active policy.
        embedder_version:
            Embedder version tag (no colons).
        support_score:
            Float in [0, 1] — support validation score from the RAG evaluator.
        completeness_score:
            Float in [0, 1] — completeness score from the RAG evaluator.
        policy_conflict:
            True if the policy layer detected a conflict for this query.
        replay_contaminated:
            True if the result set contains replay-sensitive content.
        timestamp_utc:
            Unix timestamp provided by the caller.

        Returns
        -------
        CacheAdmissionDecision
            Frozen decision record.  ``admitted=True`` means all gates passed.
        """
        try:
            deny_reasons: list[str] = []

            if support_score < self.support_threshold:
                deny_reasons.append(DENY_SUPPORT_BELOW_THRESHOLD)
                self._stats["denied_support"] += 1

            if completeness_score < self.completeness_threshold:
                deny_reasons.append(DENY_COMPLETENESS_BELOW_THRESHOLD)
                self._stats["denied_completeness"] += 1

            if policy_conflict:
                deny_reasons.append(DENY_POLICY_CONFLICT)
                self._stats["denied_policy"] += 1

            if replay_contaminated:
                deny_reasons.append(DENY_REPLAY_CONTAMINATED)
                self._stats["denied_replay"] += 1

            admitted = len(deny_reasons) == 0
            if admitted:
                self._stats["admitted"] += 1
            else:
                logger.debug(
                    "[CacheAdmissionGate] DENIED query_hash=%s reasons=%s",
                    query_hash[:16],
                    deny_reasons,
                )

            return CacheAdmissionDecision(
                artifact_type="CACHE_ADMISSION_DECISION",
                query_hash=query_hash,
                policy_hash=policy_hash,
                embedder_version=embedder_version,
                admitted=admitted,
                deny_reasons=tuple(deny_reasons),
                support_score=support_score,
                completeness_score=completeness_score,
                policy_conflict=policy_conflict,
                replay_contaminated=replay_contaminated,
                timestamp_utc=timestamp_utc,
            )

        except Exception as exc:
            self._stats["errors"] += 1
            logger.warning("[CacheAdmissionGate] Evaluation error (fail-closed): %s", exc)
            return CacheAdmissionDecision(
                artifact_type="CACHE_ADMISSION_DECISION",
                query_hash=query_hash,
                policy_hash=policy_hash,
                embedder_version=embedder_version,
                admitted=False,
                deny_reasons=("INTERNAL_ERROR",),
                support_score=support_score,
                completeness_score=completeness_score,
                policy_conflict=policy_conflict,
                replay_contaminated=replay_contaminated,
                timestamp_utc=timestamp_utc,
            )

    def get_stats(self) -> dict[str, Any]:
        """Return admission gate statistics."""
        total = sum(self._stats.values()) - self._stats["errors"]
        return {
            **self._stats,
            "total_evaluated": total,
            "admit_rate": (self._stats["admitted"] / total if total > 0 else 0.0),
            "support_threshold": self.support_threshold,
            "completeness_threshold": self.completeness_threshold,
        }


__all__ = [
    "CacheAdmissionDecision",
    "CacheAdmissionGate",
    "DENY_COMPLETENESS_BELOW_THRESHOLD",
    "DENY_POLICY_CONFLICT",
    "DENY_REPLAY_CONTAMINATED",
    "DENY_SUPPORT_BELOW_THRESHOLD",
]
