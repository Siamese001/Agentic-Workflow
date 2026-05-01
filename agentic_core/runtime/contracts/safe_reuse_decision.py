"""W2 — SafeReuseDecision contract.

A single immutable record of the dense-candidate + safety-veto composite
decision for one integrated-runtime invocation. Carries the four
explicit safety-metric aliases approved in W2 to replace the ambiguous
FP/FN terminology:

    * unsafe_reuse_allowed_count            (the safety metric)
    * safe_reuse_blocked_count              (precision/UX cost)
    * hard_negative_allowed_count           (subset of unsafe; adversarial)
    * unknown_error_timeout_parse_fail_block_count

Producer: agentic_core.runtime.entrypoints.integrated_safe_reuse_run
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from agentic_core.runtime.contracts.runtime_gate_verdict_bundle import VetoOutcome


@dataclass(frozen=True)
class SafeReuseDecision:
    """One integrated-runtime cache-reuse decision."""

    # ---- core verdict ----
    allow: bool
    reason_code: str  # SAFE_REUSE | VETOED | NOT_APPLICABLE | FAIL_CLOSED_*

    # ---- evidence ----
    dense_candidate_produced: bool
    veto_invoked: bool
    veto_outcome: VetoOutcome
    d2_similarity: float

    # ---- explicit safety-metric aliases (W2 §Metric cleanup, approved) ----
    unsafe_reuse_allowed_count: int = 0
    safe_reuse_blocked_count: int = 0
    hard_negative_allowed_count: int = 0
    unknown_error_timeout_parse_fail_block_count: int = 0

    # ---- legacy compat (kept to ease cross-reading with W1p6 sweep rows) ----
    legacy_unsafe_fp_count: int = 0
    legacy_safe_positive_block_count: int = 0

    # ---- chain-tying refs ----
    upstream_gate_verdict_ref: str = ""  # sha256 of runtime_gate_verdict_bundle.json payload
    evidence_refs: tuple[str, ...] = ()

    producer_component: str = "agentic_core.runtime.entrypoints.integrated_safe_reuse_run"

    def __post_init__(self) -> None:
        if isinstance(self.veto_outcome, str):
            object.__setattr__(self, "veto_outcome", VetoOutcome(self.veto_outcome))

        # ----- safety invariants enforced at construction time -----
        # 1. allow=True requires dense_candidate_produced=True.
        if self.allow and not self.dense_candidate_produced:
            raise ValueError(
                "SafeReuseDecision: allow=True requires dense_candidate_produced=True"
            )
        # 2. allow=True requires veto_invoked=True.
        if self.allow and not self.veto_invoked:
            raise ValueError(
                "SafeReuseDecision: allow=True requires veto_invoked=True "
                "(lexical-only / unvetoed reuse is forbidden)"
            )
        # 3. allow=True requires veto_outcome == ALLOWED.
        if self.allow and self.veto_outcome is not VetoOutcome.ALLOWED:
            raise ValueError(
                "SafeReuseDecision: allow=True requires "
                f"veto_outcome=ALLOWED; got {self.veto_outcome.value}"
            )
        # 4. Fail-closed buckets MUST NOT yield allow=True.
        fail_closed = {
            VetoOutcome.UNKNOWN,
            VetoOutcome.ERROR,
            VetoOutcome.TIMEOUT,
            VetoOutcome.PARSE_FAIL,
        }
        if self.veto_outcome in fail_closed and self.allow:
            raise ValueError(
                "SafeReuseDecision: fail-closed veto outcome "
                f"{self.veto_outcome.value} cannot produce allow=True"
            )
        # 5. unsafe_reuse_allowed_count > 0 implies allow=True (else inconsistent).
        if self.unsafe_reuse_allowed_count > 0 and not self.allow:
            raise ValueError(
                "SafeReuseDecision: unsafe_reuse_allowed_count>0 cannot occur "
                "with allow=False (the count tracks admitted unsafe reuses)"
            )
        # 6. Producer fingerprint must be production code.
        if not self.producer_component.startswith("agentic_core."):
            raise ValueError(
                "SafeReuseDecision.producer_component must be agentic_core.*; "
                f"got {self.producer_component!r}"
            )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["veto_outcome"] = self.veto_outcome.value
        return d


__all__ = ["SafeReuseDecision"]
