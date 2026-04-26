"""End-to-end runtime proof harness (per docs/reference/99_End_to_End_Runtime_Proof_and_Acceptance/).

This package owns ACCEPTANCE PROOF, not runtime authority.

It defines:
- canonical contract dataclasses (99.3)
- proof bundle schema (99.8)
- scenario registry covering golden path (99.1) and route coverage (99.2)
- a reference runtime emitter that produces a complete, deterministic proof bundle
  so the E2E harness can execute even when canonical agentic_core layers have not
  yet been wired to emit these contracts directly. When live layers exist, the
  emitter delegates to them; otherwise it falls back to a deterministic simulation
  whose digests still gate replay, no-bypass, and groundedness validators.

Public surface:
- proof.bundle  -> proof bundle schema + IO
- proof.contracts -> dataclasses for ValidatedRequest..RuntimeExhaustBundle
- proof.digests -> deterministic hashing helpers
- proof.scenarios -> scenario registry (GP-001 + route coverage matrix)
- proof.harness -> reference runtime emitter
- proof.validators -> trace, replay, no-bypass, groundedness validators
"""

from __future__ import annotations

__all__ = [
    "bundle",
    "contracts",
    "digests",
    "scenarios",
    "harness",
    "validators",
]
