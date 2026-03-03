"""
agentic_core/runtime/sovereignty_bootstrap.py

Deterministic initialization sequence for cryptographic sovereignty.

Bootstrap order (must not be reordered):
  1. Hash policy file  -> policy_hash
  2. Load hierarchy config  -> hierarchy_hash
  3. Load capability authority  -> authority_hash
  4. Initialize determinism engine with all three hashes
  5. Start execution trace
  6. (After all artifacts are added) seal determinism engine
  7. Bind core_digest to trace
"""

import hashlib
from pathlib import Path

from agentic_core.L5_safety.enforcement.hierarchy_validator_enforcer import get_hierarchy_validator
from agentic_core.runtime.execution_trace import (
    bind_determinism_to_trace,
    start_execution_trace,
)
from agentic_core.runtime.mathematical_determinism import (
    get_determinism_engine,
    initialize_determinism_engine,
)


class SovereigntyBootstrap:
    """Single-use bootstrap controller for the cryptographic sovereignty system."""

    def __init__(self) -> None:
        self.initialized: bool = False
        self.policy_hash: str | None = None
        self.hierarchy_hash: str | None = None
        self.authority_hash: str | None = None
        self._trace_id: str | None = None

    def bootstrap(self, policy_file: Path) -> str:
        """Bootstrap sovereignty and return the execution trace_id.

        Raises RuntimeError if called more than once.
        """
        if self.initialized:
            raise RuntimeError("SovereigntyBootstrap.bootstrap() must only be called once per process.")

        self.policy_hash = _hash_file(policy_file)

        hierarchy_validator = get_hierarchy_validator()
        self.hierarchy_hash = hierarchy_validator.config_hash

        from agentic_core.runtime.execution_bound_token import get_capability_authority

        authority = get_capability_authority()
        self.authority_hash = authority.authority_public_hash

        initialize_determinism_engine(
            self.policy_hash,
            self.hierarchy_hash,
            self.authority_hash,
        )

        self._trace_id = start_execution_trace(
            plan_hash=self.policy_hash,
            policy_hash=self.policy_hash,
            hierarchy_hash=self.hierarchy_hash,
        )

        self.initialized = True
        return self._trace_id

    def seal_and_finalize(self):
        """Seal the determinism engine and bind the digest to the active trace.

        Call this after all determinism artifacts have been registered.
        Returns the DeterminismProof.
        """
        if not self.initialized:
            raise RuntimeError("Cannot seal: SovereigntyBootstrap.bootstrap() not yet called.")
        engine = get_determinism_engine()
        proof = engine.seal()
        bind_determinism_to_trace(proof.core_digest)
        return proof

    def get_hashes(self):
        """Return (policy_hash, hierarchy_hash, authority_hash)."""
        if not self.initialized:
            raise RuntimeError("Sovereignty not yet bootstrapped.")
        return (self.policy_hash, self.hierarchy_hash, self.authority_hash)


def _hash_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


_sovereignty_bootstrap = SovereigntyBootstrap()


def bootstrap_sovereignty(policy_file: Path) -> str:
    """Bootstrap the global sovereignty system. Returns trace_id."""
    return _sovereignty_bootstrap.bootstrap(policy_file)


def seal_determinism_and_finalize():
    """Seal global determinism engine and bind digest to trace. Returns proof."""
    return _sovereignty_bootstrap.seal_and_finalize()


def get_sovereignty_hashes():
    """Return (policy_hash, hierarchy_hash, authority_hash)."""
    return _sovereignty_bootstrap.get_hashes()
