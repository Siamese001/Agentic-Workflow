"""W2 — RuntimeGateVerdictBundle contract.

Aggregates the L0 cache-gate verdicts (D1 exact, D2 semantic) plus the
safety-veto verdict that runs in the production integrated entry point
between a D2 hit and any cache reuse. Read-only after construction;
serialized as a JSON artifact in the W2 evidence chain.

Spec reference: .windsurf/plans/rtc-w2-integrated-runtime-r1b-safe-reuse-c7e9f3.md
Producer: agentic_core.runtime.entrypoints.integrated_safe_reuse_run
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class GateOutcome(str, Enum):
    """Per-gate outcome on a single integrated run."""

    HIT = "HIT"
    MISS = "MISS"
    SKIPPED = "SKIPPED"  # gate not consulted (e.g., D2 skipped because D1 hit)


class VetoOutcome(str, Enum):
    """Veto-stage outcome bucket — derived from VetoStatus.

    The four blocking buckets (UNKNOWN / ERROR / TIMEOUT / PARSE_FAIL) are
    surfaced explicitly so the W2 verifier can prove that fail-closed
    states never produce ``allow=True`` in the SafeReuseDecision.
    """

    NOT_INVOKED = "NOT_INVOKED"  # cache miss → veto never ran (legitimate)
    ALLOWED = "ALLOWED"           # VetoStatus.SAFE
    BLOCKED = "BLOCKED"           # VetoStatus.{UNSAFE_*, VETO}
    UNKNOWN = "UNKNOWN"           # VetoStatus.UNKNOWN — fail-closed
    ERROR = "ERROR"               # VetoStatus.ERROR — fail-closed
    TIMEOUT = "TIMEOUT"           # latency-budget exhaustion — fail-closed
    PARSE_FAIL = "PARSE_FAIL"     # malformed verdict — fail-closed


@dataclass(frozen=True)
class RuntimeGateVerdictBundle:
    """Single-run gate-verdict aggregate.

    Fields:
        d1_outcome: GateOutcome for the D1 exact-cache gate.
        d2_outcome: GateOutcome for the D2 semantic-cache gate.
        veto_outcome: VetoOutcome bucket for the safety-veto stage. Set to
            ``NOT_INVOKED`` when neither D1 nor D2 hit; set to one of the
            blocking buckets when veto fail-closed; set to ``ALLOWED`` only
            when the orchestrator returned ``VetoStatus.SAFE``.
        d2_similarity: Similarity score the D2 gate observed (0.0 if not
            evaluated).
        veto_primary_mode: Operative veto mode (e.g. ``C_PRIMARY_LLM_JUDGE``).
            Empty string when veto did not run.
        llm_judge_invocation_count: How many times the LLM-judge stage ran
            during this evaluation. Must be >0 whenever
            ``veto_primary_mode == "C_PRIMARY_LLM_JUDGE"`` and
            ``veto_outcome == ALLOWED`` — enforces "lexical-only cannot pass".
        veto_latency_ms: Wall-clock spent inside the orchestrator.
        reason_codes: Tuple of route/veto reason codes (e.g.,
            ``("d2_semantic_hit", "veto_safe")``).
        producer_component: SSOT producer fingerprint. MUST identify the
            production module — never the harness.
    """

    d1_outcome: GateOutcome
    d2_outcome: GateOutcome
    veto_outcome: VetoOutcome
    d2_similarity: float = 0.0
    veto_primary_mode: str = ""
    llm_judge_invocation_count: int = 0
    veto_latency_ms: float = 0.0
    reason_codes: tuple[str, ...] = ()
    producer_component: str = "agentic_core.runtime.entrypoints.integrated_safe_reuse_run"

    def __post_init__(self) -> None:  # noqa: D401
        # Cast & validate enum fields (frozen dataclass — use object.__setattr__).
        if isinstance(self.d1_outcome, str):
            object.__setattr__(self, "d1_outcome", GateOutcome(self.d1_outcome))
        if isinstance(self.d2_outcome, str):
            object.__setattr__(self, "d2_outcome", GateOutcome(self.d2_outcome))
        if isinstance(self.veto_outcome, str):
            object.__setattr__(self, "veto_outcome", VetoOutcome(self.veto_outcome))
        if not 0.0 <= float(self.d2_similarity) <= 1.0:
            raise ValueError(
                f"RuntimeGateVerdictBundle.d2_similarity must be in [0,1]; "
                f"got {self.d2_similarity}"
            )
        if self.llm_judge_invocation_count < 0:
            raise ValueError("llm_judge_invocation_count must be non-negative")
        # Anti-cheat: producer_component must point into agentic_core.
        if not self.producer_component.startswith("agentic_core."):
            raise ValueError(
                "RuntimeGateVerdictBundle.producer_component must be a "
                "production module under agentic_core.* (got "
                f"{self.producer_component!r})"
            )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["d1_outcome"] = self.d1_outcome.value
        d["d2_outcome"] = self.d2_outcome.value
        d["veto_outcome"] = self.veto_outcome.value
        return d


__all__ = [
    "GateOutcome",
    "RuntimeGateVerdictBundle",
    "VetoOutcome",
]
