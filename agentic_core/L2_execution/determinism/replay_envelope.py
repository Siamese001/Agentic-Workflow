"""C1.1: Replay Envelope Build - Freeze container for execution.

10C-REQ-117: Build envelope with replay_key, policy_hash, capability_token, run_id
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ReplayEnvelope:
    """Immutable replay envelope for deterministic execution.

    10C-REQ-117: Contains replay_key, policy_hash, capability_token, run_id,
    run_clock, entropy_seed, stable_id_scope.
    """

    replay_key: str
    policy_hash: str
    capability_token: str
    run_id: str
    run_clock: float  # Deterministic clock start
    entropy_seed: int  # Seeded random source
    stable_id_scope: str  # Namespace for stable IDs
    frozen_state_hash: str = ""  # Hash of frozen state
    ml_model_hashes: dict[str, str] = field(default_factory=dict)

    def envelope_hash(self) -> str:
        """Deterministic hash of envelope contents.

        ml_model_hashes is included so that runs with different model artifacts
        produce distinct digests, satisfying the C1 determinism invariant.
        """
        data = {
            "replay_key": self.replay_key,
            "policy_hash": self.policy_hash,
            "capability_token": self.capability_token,
            "run_id": self.run_id,
            "run_clock": self.run_clock,
            "entropy_seed": self.entropy_seed,
            "stable_id_scope": self.stable_id_scope,
            "ml_model_hashes": self.ml_model_hashes,
        }
        raw = json.dumps(data, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()


class EnvelopeBuilder:
    """Builder for replay envelopes.

    10C-REQ-117: Build replay envelope with required freeze signals.
    """

    def __init__(self) -> None:
        self._replay_key: str = ""
        self._policy_hash: str = ""
        self._capability_token: str = ""
        self._run_id: str = ""
        self._entropy_seed: int = 42  # Default seed
        self._stable_id_scope: str = "default"
        self._ml_model_hashes: dict[str, str] = {}

    def with_replay_key(self, key: str) -> EnvelopeBuilder:
        """Set replay key."""
        self._replay_key = key
        return self

    def with_policy_hash(self, hash_val: str) -> EnvelopeBuilder:
        """Set policy hash."""
        self._policy_hash = hash_val
        return self

    def with_capability_token(self, token: str) -> EnvelopeBuilder:
        """Set capability token."""
        self._capability_token = token
        return self

    def with_run_id(self, run_id: str) -> EnvelopeBuilder:
        """Set run ID."""
        self._run_id = run_id
        return self

    def with_entropy_seed(self, seed: int) -> EnvelopeBuilder:
        """Set entropy seed."""
        self._entropy_seed = seed
        return self

    def with_stable_id_scope(self, scope: str) -> EnvelopeBuilder:
        """Set stable ID scope."""
        self._stable_id_scope = scope
        return self

    def with_ml_model_hash(self, role: str, hash_value: str) -> EnvelopeBuilder:
        """Bind a model artifact hash by role (e.g. 'heal_classifier').

        Must be called at E1 before any ML inference so the replay digest
        covers the exact artifact used during this run.
        """
        self._ml_model_hashes[role] = hash_value
        return self

    def with_coverage_scorer(self, evaluator_version: str) -> EnvelopeBuilder:
        """Bind the retrieval coverage scorer version under the 'coverage_scorer' role.

        Derives a 16-character hex digest from *evaluator_version* and stores it
        via ``with_ml_model_hash`` so the replay envelope hash changes whenever the
        scorer artifact changes — satisfying C1 determinism invariant.

        Advisory-only: this binding records which scorer ran; it does not gate or
        influence the disposition decision.
        """
        version_hash = hashlib.sha256(evaluator_version.encode()).hexdigest()[:16]
        return self.with_ml_model_hash("coverage_scorer", version_hash)

    def build(self) -> ReplayEnvelope:
        """Build the replay envelope."""
        if not all([self._replay_key, self._policy_hash, self._run_id]):
            raise ValueError("replay_key, policy_hash, and run_id are required")

        return ReplayEnvelope(
            replay_key=self._replay_key,
            policy_hash=self._policy_hash,
            capability_token=self._capability_token,
            run_id=self._run_id,
            run_clock=time.time(),  # Snapshot at build time
            entropy_seed=self._entropy_seed,
            stable_id_scope=self._stable_id_scope,
            ml_model_hashes=dict(self._ml_model_hashes),
        )
