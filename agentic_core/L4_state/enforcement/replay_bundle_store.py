"""
Phase 9 — ReplayBundleStore + ReplayVerifier.

L4 in-process store for ReplayBundle artifacts (non-mutating to knowledge index).
ReplayVerifier checks integrity (hash recomputation) and prior-only constraints.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from agentic_core.L4_state.types.replay_bundle import ReplayBundle


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# ReplayBundleStore
# ---------------------------------------------------------------------------


@dataclass
class ReplayBundleStore:
    """
    L4 in-process store for ReplayBundle artifacts.

    Keyed by replay_hash. Idempotent: duplicate hash = no-op.
    Non-mutating to knowledge index (Pinecone/Redis).
    """

    _store: dict[str, ReplayBundle] = field(default_factory=dict)

    def store_replay_bundle(self, bundle: ReplayBundle) -> str:
        """
        Persist a ReplayBundle. Returns replay_hash.
        Idempotent: storing the same bundle twice is a no-op.
        """
        self._store[bundle.replay_hash] = bundle
        return bundle.replay_hash

    def fetch_replay_bundle(self, replay_hash: str) -> ReplayBundle | None:
        """Return the ReplayBundle for the given replay_hash, or None."""
        return self._store.get(replay_hash)

    def count(self) -> int:
        return len(self._store)


# ---------------------------------------------------------------------------
# VerifiedReplay result
# ---------------------------------------------------------------------------


@dataclass
class VerifiedReplay:
    """Result of a successful replay verification."""

    replay_hash: str
    mission_id: str
    execution_start_tick: int
    execution_end_tick: int
    checks_passed: list[str]


# ---------------------------------------------------------------------------
# ReplayVerificationError
# ---------------------------------------------------------------------------


class ReplayVerificationError(Exception):
    """
    Raised when replay bundle verification fails.

    Attributes
    ----------
    code   : str — violation code
    detail : str — human-readable description
    """

    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"[{code}]" + (f" {detail}" if detail else ""))


# ---------------------------------------------------------------------------
# ReplayVerifier
# ---------------------------------------------------------------------------


class ReplayVerifier:
    """
    Verifies a ReplayBundle for:
    1. Hash integrity — replay_hash recomputation matches stored value.
    2. Prior-only constraints — all referenced prior signals/violations have
       commit_tick strictly less than execution_start_tick.
    3. Component presence — referenced hashes exist in provided registries.

    All checks are deterministic and raise ReplayVerificationError on failure.
    """

    def verify(
        self,
        bundle: ReplayBundle,
        *,
        known_config_hashes: set[str] | None = None,
        known_citation_hashes: set[str] | None = None,
        known_signal_hashes: set[str] | None = None,
        known_violation_hashes: set[str] | None = None,
        known_intent_hashes: set[str] | None = None,
        known_result_hashes: set[str] | None = None,
        prior_signal_tick: int | None = None,
        prior_violation_ticks: dict[str, int] | None = None,
    ) -> VerifiedReplay:
        """
        Verify a ReplayBundle.

        Parameters
        ----------
        bundle                 : ReplayBundle
        known_config_hashes    : set of valid config hash strings (optional)
        known_citation_hashes  : set of valid citation_hash strings (optional)
        known_signal_hashes    : set of valid signal_hash strings (optional)
        known_violation_hashes : set of valid violation event_hash strings (optional)
        known_intent_hashes    : set of valid tool intent_hash strings (optional)
        known_result_hashes    : set of valid tool result_hash strings (optional)
        prior_signal_tick      : commit_tick of the prior detection signal (optional)
        prior_violation_ticks  : {event_hash: commit_tick} for prior violations (optional)

        Returns
        -------
        VerifiedReplay on success.

        Raises
        ------
        ReplayVerificationError on any failure.
        """
        checks: list[str] = []

        # 1. Hash integrity: recompute and compare
        recomputed = _sha256(bundle.canonical_bytes())
        if recomputed != bundle.replay_hash:
            raise ReplayVerificationError(
                code="REPLAY_HASH_MISMATCH",
                detail=(f"replay_hash mismatch: stored={bundle.replay_hash!r}, recomputed={recomputed!r}"),
            )
        checks.append("hash_integrity")

        # 2. Component presence checks (only when registries provided)
        if known_config_hashes is not None:
            for k, v in bundle.active_config_hashes.items():
                if v and v not in known_config_hashes:
                    raise ReplayVerificationError(
                        code="MISSING_CONFIG_HASH",
                        detail=f"config hash {v!r} (key={k!r}) not found in registry",
                    )
            checks.append("config_hashes_present")

        if known_citation_hashes is not None and bundle.retrieval_used:
            if bundle.citation_hash not in known_citation_hashes:
                raise ReplayVerificationError(
                    code="MISSING_CITATION_HASH",
                    detail=f"citation_hash {bundle.citation_hash!r} not found",
                )
            checks.append("citation_hash_present")

        if known_signal_hashes is not None and bundle.prior_detection_signal_hash:
            if bundle.prior_detection_signal_hash not in known_signal_hashes:
                raise ReplayVerificationError(
                    code="MISSING_SIGNAL_HASH",
                    detail=f"prior_detection_signal_hash {bundle.prior_detection_signal_hash!r} not found",
                )
            checks.append("signal_hash_present")

        if known_violation_hashes is not None:
            for vh in bundle.prior_violation_event_hashes:
                if vh not in known_violation_hashes:
                    raise ReplayVerificationError(
                        code="MISSING_VIOLATION_HASH",
                        detail=f"violation event_hash {vh!r} not found",
                    )
            checks.append("violation_hashes_present")

        if known_intent_hashes is not None:
            for ih in bundle.tool_intent_hashes:
                if ih not in known_intent_hashes:
                    raise ReplayVerificationError(
                        code="MISSING_INTENT_HASH",
                        detail=f"tool intent_hash {ih!r} not found",
                    )
            checks.append("intent_hashes_present")

        if known_result_hashes is not None:
            for rh in bundle.tool_result_hashes:
                if rh not in known_result_hashes:
                    raise ReplayVerificationError(
                        code="MISSING_RESULT_HASH",
                        detail=f"tool result_hash {rh!r} not found",
                    )
            checks.append("result_hashes_present")

        # 3. Prior-only constraints
        if prior_signal_tick is not None and bundle.prior_detection_signal_hash:
            if prior_signal_tick >= bundle.execution_start_tick:
                raise ReplayVerificationError(
                    code="SAME_CYCLE_SIGNAL",
                    detail=(
                        f"prior_detection_signal commit_tick ({prior_signal_tick}) "
                        f">= execution_start_tick ({bundle.execution_start_tick}): "
                        f"same-cycle influence detected"
                    ),
                )
            checks.append("signal_prior_only")

        if prior_violation_ticks is not None:
            for vh, tick in prior_violation_ticks.items():
                if tick >= bundle.execution_start_tick:
                    raise ReplayVerificationError(
                        code="SAME_CYCLE_VIOLATION",
                        detail=(
                            f"violation {vh!r} commit_tick ({tick}) "
                            f">= execution_start_tick ({bundle.execution_start_tick}): "
                            f"same-cycle influence detected"
                        ),
                    )
            if prior_violation_ticks:
                checks.append("violations_prior_only")

        return VerifiedReplay(
            replay_hash=bundle.replay_hash,
            mission_id=bundle.mission_id,
            execution_start_tick=bundle.execution_start_tick,
            execution_end_tick=bundle.execution_end_tick,
            checks_passed=checks,
        )
