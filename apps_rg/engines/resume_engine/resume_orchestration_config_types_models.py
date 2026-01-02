from __future__ import annotations
"""Dataclass models for resume_orchestration_config_types.

Local Runtime DTOs (Allowed) - App-specific configuration models.
Phase 7: Underscore fields eliminated for SSOT alignment.
"""
from typing import Any, Optional, Protocol, Dict, List

import logging
from dataclasses import dataclass, field
from typing import Any, List, Optional

Logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant


LOGGER = logging.getLogger(__name__)


@dataclass
class WordCountConstraint:  # Local Runtime DTO (Allowed)
    """Word count constraint for a section."""
    min: Optional[int] = None
    max: Optional[int] = None
    scope: str = 'total'
    unit: str = 'words'

    def validate(self: Any, count: int) -> bool:
        """Validate word count against constraints."""
        if self.min is not None and count < self.min:
            return False
        if self.max is not None and count > self.max:
            return False
        return True


@dataclass
class CharCountConstraint:  # Local Runtime DTO (Allowed)
    """Character count constraint for a section."""
    min: Optional[int] = None
    max: Optional[int] = None


    def validate(self: Any, count: int) -> bool:
        """Validate character count against constraints."""
        if self.min is not None and count < self.min:
            return False
        if self.max is not None and count > self.max:
            return False
        return True


@dataclass
class ReasoningConfig:  # Local Runtime DTO (Allowed)
    """Reasoning configuration for K-node execution."""
    temperature: float = 0.7
    RagType: RAGType = RAGType.HYBRID
    rag_total_calls: int = 5
    rag_hops: int = 2
    ClaimVerificationMode: ClaimVerificationMode = ClaimVerificationMode.BALANCED
    hybrid_cot_tot: bool = True
    cot_min_paths: Optional[int] = 1
    tot_branches: Optional[int] = 3
    min_tot_depth: Optional[int] = 2
    self_consistency: int = 3
    reflexion: bool = True
    routing_tier: Optional[RoutingTier] = None


@dataclass
class ProvenanceRule:  # Local Runtime DTO (Allowed)
    """Provenance rule for bullet generation."""
    verbatim: int
    transformed: int
    synthetic: int

    @property
    def total(self: Any) -> int:
        """Total bullet count."""
        return self.verbatim + self.transformed + self.synthetic

    @property
    def pattern(self: Any) -> str:
        """Provenance pattern string."""
        return f'{self.verbatim}V-{self.transformed}T-{self.synthetic}S'

@dataclass
class ValidationGate:  # Local Runtime DTO (Allowed)
    """Validation gate configuration."""
    gate_id: str
    execution_point: str
    blocking: bool
    Severity: ValidationSeverity
    checks: List[str] = field(default_factory=list)
    on_fail: str = 'HALT'
    halt_message: Optional[str] = None

