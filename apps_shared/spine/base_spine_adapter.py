"""
Base Spine Adapter — shared contract for LIC/RG adapters.

Provides deterministic CID derivation, call-order invariants, and
mutation discipline enforcement. All app-specific adapters must
subclass this base to ensure cross-app consistency.
"""
from __future__ import annotations
from typing import Any
from agentic_core.interfaces.execution import CIDRegistry, ExecutionCycle
from apps_shared.utils.determinism_util import canonical_hash, strip_nondeterministic
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

class BaseSpineAdapter:
    """
    Shared base contract for all spine adapters.

    Enforces:
    - Deterministic CID derivation with app-specific prefix
    - Call order invariant: new_cycle before orchestrator.execute
    - Mutation discipline: never mutate caller-owned dicts
    - Import stability: no optional runtime imports

    Subclasses must provide:
    - prefix (e.g., "lic-", "rg-")
    - orchestrator dependency wiring
    """
    _HASH_BODY_LENGTH: int = 16

    def __init__(self, cid_registry: CIDRegistry, orchestrator: Any, *, prefix: str, max_reentry_attempts: int=3) -> None:
        """Initialize base adapter with dependencies and prefix.

        Args:
            cid_registry: CIDRegistry instance for lifecycle management
            orchestrator: ExecutionOrchestrator instance (or compatible)
            prefix: App-specific prefix (must end with "-" and be lowercase)
            max_reentry_attempts: Maximum re-entry attempts for retry logic

        Raises:
            ValueError: If prefix format is invalid
        """
        self._validate_prefix(prefix)
        self._prefix = prefix
        self._cid_registry = cid_registry
        self._orchestrator = orchestrator
        self._max_reentry_attempts = max_reentry_attempts

    def _validate_prefix(self, prefix: str) -> None:
        """Validate prefix format according to contract requirements."""
        if not prefix.endswith('-'):
            raise ValueError(f"Prefix must end with '-': {prefix}")
        if prefix.lower() != prefix:
            raise ValueError(f'Prefix must be lowercase: {prefix}')
        if len(prefix) < 2:
            raise ValueError(f'Prefix too short: {prefix}')

    def _derive_cid(self, intent_input: dict[str, Any]) -> str:
        """
        Derive deterministic CID from intent input.

        CID format: {prefix}{hash_body}
        where hash_body is fixed-length hash of canonicalized payload.
        """
        stripped = strip_nondeterministic(intent_input)
        hash_body = canonical_hash(stripped)[:self._HASH_BODY_LENGTH]
        return f'{self._prefix}{hash_body}'

    def _enrich_intent_input(self, intent_input: dict[str, Any], cid: str, cycle_attempt: int) -> dict[str, Any]:
        """
        Create enriched intent input without mutating caller's dict.

        Enforces mutation discipline by creating a fresh dict.
        """
        enriched = dict(intent_input)
        enriched['_cid'] = cid
        enriched['_cycle_attempt'] = cycle_attempt
        return enriched

    def execute(self, intent_input: dict[str, Any]) -> dict[str, Any]:
        """
        Execute intent through canonical spine with enforced invariants.

        Steps:
        1) Derive deterministic CID from intent input
        2) Register CID in CIDRegistry (call order invariant)
        3) Create enriched intent input (mutation discipline)
        4) Delegate to orchestrator
        5) Return result dict with CID

        Args:
            intent_input: Dict containing intent data

        Returns:
            Result dict from orchestrator augmented with CID
        """
        cid = self._derive_cid(intent_input)
        cycle: ExecutionCycle = self._cid_registry.new_cycle(cid)
        enriched = self._enrich_intent_input(intent_input, cid, cycle.attempt)
        result = self._orchestrator.execute(enriched)
        final_result = dict(result)
        final_result['cid'] = cid
        return final_result

    @property
    def prefix(self) -> str:
        """Get the adapter's prefix (read-only)."""
        return self._prefix
