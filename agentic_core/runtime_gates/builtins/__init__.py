"""Runtime Gate Builtins — Non-bypassable core gates.

Core-owned gates that enforce fundamental invariants:
- candidate_acceptance_guard: Ensures rejected candidates are never written
- prompt_sha_gate: Logs prompt assembly SHA for replay
- input_snapshot_gate: Pins input SHA, detects concurrent edits
- contamination_gate: Cross-company contamination detection
- provenance_contract_gate: Source bullet provenance for claims

These gates are FAIL_CLOSED and NON_BYPASSABLE.
"""

from agentic_core.runtime_gates.builtins.candidate_acceptance_guard import (
    CandidateAcceptanceGuard,
)

__all__ = [
    "CandidateAcceptanceGuard",
]
