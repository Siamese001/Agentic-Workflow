"""W1 Phase 5 — Veto Protocol Contract.

All veto stages (lexical pre-veto, cross-encoder, LLM-judge) implement
the VetoStage Protocol, ensuring interchangeable, fail-closed behavior.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


class VetoStatus(enum.Enum):
    """Veto decision status — fail-closed design."""
    
    SAFE = "SAFE"
    """Veto approves reuse — semantic equivalence verified."""
    
    UNSAFE_DIFFERENT_INTENT = "UNSAFE_DIFFERENT_INTENT"
    """Veto blocks reuse — semantically different or opposite intent detected."""
    
    UNSAFE_POLICY_DRIFT = "UNSAFE_POLICY_DRIFT"
    """Veto blocks reuse — policy/tenant/freshness contract violation."""
    
    VETO = "VETO"
    """Generic veto — reuse blocked (catch-all for non-specific safety concerns)."""
    
    UNKNOWN = "UNKNOWN"
    """Ambiguous / insufficient confidence — fail-closed, treat as VETO."""
    
    ERROR = "ERROR"
    """Veto stage error (model load failure, timeout, parse error) — fail-closed."""
    
    DELEGATE = "DELEGATE"
    """Pre-veto delegates to next stage (Layer 1 → Layer 2). Not a final verdict."""
    
    def is_blocking(self) -> bool:
        """Return True if this status blocks cache reuse (fail-closed)."""
        return self in {
            VetoStatus.UNSAFE_DIFFERENT_INTENT,
            VetoStatus.UNSAFE_POLICY_DRIFT,
            VetoStatus.VETO,
            VetoStatus.UNKNOWN,
            VetoStatus.ERROR,
        }
    
    def allows_reuse(self) -> bool:
        """Return True only if this status explicitly allows reuse."""
        return self == VetoStatus.SAFE


@dataclass(frozen=True)
class VetoResult:
    """Immutable result from a veto stage evaluation."""
    
    status: VetoStatus
    """The veto decision status."""
    
    stage_name: str
    """Identifier of the veto stage that produced this result."""
    
    confidence: float = field(default=0.0)
    """Confidence score [0.0, 1.0] — 0.0 if not applicable or error."""
    
    rationale: str = field(default="")
    """Human-readable explanation of the decision."""
    
    metadata: dict[str, Any] = field(default_factory=dict)
    """Stage-specific metadata (e.g., cross-encoder score, LLM token count)."""
    
    latency_ms: float = field(default=0.0)
    """Time taken for this stage's evaluation."""
    
    def blocks_reuse(self) -> bool:
        """Fail-closed: block unless explicitly SAFE."""
        return not self.status.allows_reuse()
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON artifacts."""
        return {
            "status": self.status.value,
            "stage_name": self.stage_name,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
            "blocks_reuse": self.blocks_reuse(),
        }
    
    @classmethod
    def safe(
        cls,
        stage_name: str,
        confidence: float = 1.0,
        rationale: str = "",
        latency_ms: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> "VetoResult":
        """Factory for SAFE results."""
        return cls(
            status=VetoStatus.SAFE,
            stage_name=stage_name,
            confidence=confidence,
            rationale=rationale or f"{stage_name}: semantic equivalence verified",
            latency_ms=latency_ms,
            metadata=metadata or {},
        )
    
    @classmethod
    def veto(
        cls,
        stage_name: str,
        reason: str,
        confidence: float = 1.0,
        latency_ms: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> "VetoResult":
        """Factory for VETO results (generic safety block)."""
        return cls(
            status=VetoStatus.VETO,
            stage_name=stage_name,
            confidence=confidence,
            rationale=f"{stage_name}: VETO — {reason}",
            latency_ms=latency_ms,
            metadata=metadata or {},
        )
    
    @classmethod
    def unsafe_intent(
        cls,
        stage_name: str,
        contradiction: str,
        confidence: float = 1.0,
        latency_ms: float = 0.0,
    ) -> "VetoResult":
        """Factory for UNSAFE_DIFFERENT_INTENT results."""
        return cls(
            status=VetoStatus.UNSAFE_DIFFERENT_INTENT,
            stage_name=stage_name,
            confidence=confidence,
            rationale=f"{stage_name}: UNSAFE_DIFFERENT_INTENT — {contradiction}",
            latency_ms=latency_ms,
        )
    
    @classmethod
    def unsafe_policy(
        cls,
        stage_name: str,
        violation: str,
        confidence: float = 1.0,
        latency_ms: float = 0.0,
    ) -> "VetoResult":
        """Factory for UNSAFE_POLICY_DRIFT results."""
        return cls(
            status=VetoStatus.UNSAFE_POLICY_DRIFT,
            stage_name=stage_name,
            confidence=confidence,
            rationale=f"{stage_name}: UNSAFE_POLICY_DRIFT — {violation}",
            latency_ms=latency_ms,
        )
    
    @classmethod
    def unknown(
        cls,
        stage_name: str,
        reason: str = "insufficient confidence",
        latency_ms: float = 0.0,
    ) -> "VetoResult":
        """Factory for UNKNOWN results (fail-closed)."""
        return cls(
            status=VetoStatus.UNKNOWN,
            stage_name=stage_name,
            confidence=0.0,
            rationale=f"{stage_name}: UNKNOWN — {reason} (treated as VETO)",
            latency_ms=latency_ms,
        )
    
    @classmethod
    def error(
        cls,
        stage_name: str,
        error: str,
        latency_ms: float = 0.0,
    ) -> "VetoResult":
        """Factory for ERROR results (fail-closed)."""
        return cls(
            status=VetoStatus.ERROR,
            stage_name=stage_name,
            confidence=0.0,
            rationale=f"{stage_name}: ERROR — {error} (fail-closed, treated as VETO)",
            latency_ms=latency_ms,
            metadata={"error": error},
        )
    
    @classmethod
    def delegate(
        cls,
        stage_name: str,
        reason: str = "ambiguous, delegating to next stage",
        latency_ms: float = 0.0,
    ) -> "VetoResult":
        """Factory for DELEGATE results (Layer 1 pre-veto only)."""
        return cls(
            status=VetoStatus.DELEGATE,
            stage_name=stage_name,
            confidence=0.0,
            rationale=f"{stage_name}: DELEGATE — {reason}",
            latency_ms=latency_ms,
        )


@runtime_checkable
class VetoStage(Protocol):
    """Protocol that all veto stages must implement.
    
    This enables interchangeable use of lexical pre-veto, cross-encoder,
    and LLM-judge as composable safety layers.
    """
    
    @property
    def name(self) -> str:
        """Return the stage identifier (e.g., 'lexical_intent', 'llm_judge')."""
        ...
    
    def evaluate(
        self,
        query: str,
        cached_query: str,
        cached_answer: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> VetoResult:
        """Evaluate whether cache reuse is safe.
        
        Args:
            query: The incoming user query
            cached_query: The query associated with the cached entry
            cached_answer: The cached response (optional, for LLM-judge)
            context: Additional context (e.g., safety tier, action sensitivity)
        
        Returns:
            VetoResult with status and metadata. Must be fail-closed:
            - Any error/exception internally must return VetoResult.error()
            - Any timeout must return VetoResult.error()
            - Any parse failure must return VetoResult.error()
        """
        ...
    
    def is_available(self) -> bool:
        """Return True if this stage can be used (model loaded, resources available)."""
        ...


# Sentinel result for when no veto stage is configured
NO_VETO_CONFIGURED = VetoResult.error(
    stage_name="none",
    error="No veto stage configured — fail-closed",
)
