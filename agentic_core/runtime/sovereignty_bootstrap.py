"""agentic_core/runtime/sovereignty_bootstrap.py

Single-use bootstrap sequence for the sovereignty runtime.

Bootstrap Order
---------------
1. Load policy configuration from the provided policy file.
2. Initialize the hierarchy validator with the loaded policy.
3. Initialize the determinism engine for replay safety.
4. Start the execution trace for the bootstrap session.
5. Acquire the capability authority token.
6. Seal the bootstrap state (no further mutations allowed).
7. Finalize and return the sealed runtime context.

Design Invariants
-----------------
- ``bootstrap()`` may only be called ONCE per instance. A second call raises
  ``RuntimeError``.
- ``seal_and_finalize()`` may only be called AFTER ``bootstrap()`` has
  completed. Calling it before raises ``RuntimeError``.
- All exceptions propagate — fail-closed by design.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def get_hierarchy_validator(policy: dict[str, Any]) -> Any:
    """Placeholder — returns a hierarchy validator for the given policy."""
    raise NotImplementedError("get_hierarchy_validator not yet wired")


def initialize_determinism_engine() -> None:
    """Placeholder — initializes the determinism engine."""


def start_execution_trace(label: str = "bootstrap") -> str:
    """Placeholder — starts an execution trace and returns a trace ID."""
    import uuid

    return str(uuid.uuid4())


class SovereigntyBootstrap:
    """Single-use bootstrap for the sovereignty runtime.

    Bootstrap Order:
    1. Load policy file
    2. Initialize hierarchy validator
    3. Initialize determinism engine
    4. Start execution trace
    5. Acquire capability authority
    6. Seal bootstrap state
    7. Finalize runtime context
    """

    def __init__(self) -> None:
        self._bootstrapped = False
        self._sealed = False
        self._trace_id: str | None = None

    def bootstrap(self, policy_file: Path) -> dict[str, Any]:
        """Execute the 7-step bootstrap sequence. May only be called once."""
        if self._bootstrapped:
            raise RuntimeError(
                "SovereigntyBootstrap.bootstrap() may only be called once per instance"
            )
        self._bootstrapped = True

        # Step 1: Load policy
        policy = json.loads(policy_file.read_text(encoding="utf-8"))
        logger.info("Bootstrap step 1: policy loaded (version=%s)", policy.get("version"))

        # Step 2: Hierarchy validator
        validator = get_hierarchy_validator(policy)
        config_hash = validator.config_hash

        # Step 3: Determinism engine
        initialize_determinism_engine()

        # Step 4: Execution trace
        self._trace_id = start_execution_trace("sovereignty_bootstrap")

        # Step 5: Capability authority
        from agentic_core.runtime.execution_bound_token import get_capability_authority

        authority = get_capability_authority()
        authority_hash = authority.authority_public_hash

        logger.info(
            "Bootstrap complete: config_hash=%s, trace=%s, authority=%s",
            config_hash,
            self._trace_id,
            authority_hash,
        )

        return {
            "config_hash": config_hash,
            "trace_id": self._trace_id,
            "authority_hash": authority_hash,
        }

    def seal_and_finalize(self) -> dict[str, Any]:
        """Seal the bootstrap state. Must be called after bootstrap()."""
        if not self._bootstrapped:
            raise RuntimeError(
                "seal_and_finalize() requires bootstrap() to have been called first"
            )
        if self._sealed:
            raise RuntimeError("Already sealed")
        self._sealed = True
        logger.info("Bootstrap sealed and finalized (trace=%s)", self._trace_id)
        return {"sealed": True, "trace_id": self._trace_id}


__all__ = [
    "SovereigntyBootstrap",
    "get_hierarchy_validator",
    "initialize_determinism_engine",
    "start_execution_trace",
]
