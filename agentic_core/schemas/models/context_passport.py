"""
Context Passport Schema
=======================
Defines the dual-state memory architecture (HardState vs SoftState) and 
thermal configuration for the Sovereign agentic runtime.

This module consolidates:
- ThermalProfile & ThermalConfig (Temperature/Creativity controls)
- HardState (Immutable, DAG-owned evidence)
- SoftState (Mutable, LLM-owned scratchpad)
- SignalContext (The container passing through the workflow)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ==========================================
# Thermal Configuration
# ==========================================

class ThermalProfile(str, Enum):
    """Predefined thermal configurations for different node types."""
    CREATIVITY_MAX = "creativity_max"
    CREATIVITY_HIGH = "creativity_high"
    BALANCED = "balanced"
    STRUCTURED = "structured"
    PRECISION = "precision"

@dataclass
class ThermalConfig:
    """Dynamic thermal configuration for LLM parameters."""
    profile: ThermalProfile = ThermalProfile.BALANCED
    temperature: float = 0.7
    top_p: float = 0.85
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    max_tokens: Optional[int] = None
    node_overrides: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def get_params_for_node(self, node_id: str) -> Dict[str, float]:
        """Get thermal parameters for a specific node."""
        if node_id in self.node_overrides:
            return {
                "temperature": self.node_overrides[node_id].get("temperature", self.temperature),
                "top_p": self.node_overrides[node_id].get("top_p", self.top_p),
                "frequency_penalty": self.node_overrides[node_id].get("frequency_penalty", self.frequency_penalty),
                "presence_penalty": self.node_overrides[node_id].get("presence_penalty", self.presence_penalty)
            }
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }

    def set_node_profile(self, node_id: str, profile: ThermalProfile) -> None:
        """Set a thermal profile for a specific node."""
        profile_configs = {
            ThermalProfile.CREATIVITY_MAX: {"temperature": 0.9, "top_p": 0.95},
            ThermalProfile.CREATIVITY_HIGH: {"temperature": 0.8, "top_p": 0.90},
            ThermalProfile.BALANCED: {"temperature": 0.7, "top_p": 0.85},
            ThermalProfile.STRUCTURED: {"temperature": 0.3, "top_p": 0.70},
            ThermalProfile.PRECISION: {"temperature": 0.1, "top_p": 0.50}
        }
        self.node_overrides[node_id] = profile_configs[profile]


# ==========================================
# State Architecture (Hard & Soft)
# ==========================================

@dataclass(frozen=True)
class HardState:
    """
    Immutable, DAG-owned state that the LLM cannot edit directly.
    
    This contains critical execution metadata, security_scopes, and structural
    information that must remain stable throughout the workflow.
    """
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: Optional[str] = None
    node_id: Optional[str] = None
    security_scopes: set = field(default_factory=set)
    file_paths: Dict[str, str] = field(default_factory=dict)
    schemas: Dict[str, str] = field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_trace(self, event: str, data: Dict[str, Any]) -> 'HardState':
        """Add an event to the execution trace (returns new instance)."""
        new_trace = self.execution_trace + [{
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }]
        return HardState(
            execution_id=self.execution_id,
            workflow_id=self.workflow_id,
            node_id=self.node_id,
            security_scopes=self.security_scopes,
            file_paths=self.file_paths,
            schemas=self.schemas,
            execution_trace=new_trace,
            created_at=self.created_at
        )

@dataclass
class SoftState:
    """
    Mutable, LLM-owned scratchpad for high-temperature creativity.
    
    This is where the LLM can draft, speculate, and iterate without risking
    system stability. Content here must be validated before promotion to HardState.
    """
    drafts: Dict[str, Any] = field(default_factory=dict)
    scratchpad: List[str] = field(default_factory=list)
    creative_variants: List[Dict[str, Any]] = field(default_factory=list)
    speculative_content: Dict[str, Any] = field(default_factory=dict)
    revision_history: List[Dict[str, Any]] = field(default_factory=list)

    def add_draft(self, key: str, content: Any) -> None:
        """Add content to the drafts."""
        self.drafts[key] = content

    def add_scratch_note(self, note: str) -> None:
        """Add a note to the scratchpad."""
        self.scratchpad.append(note)

    def record_revision(self, key: str, old_value: Any, new_value: Any) -> None:
        """Record a revision in the history."""
        self.revision_history.append({
            "key": key,
            "old_value": old_value,
            "new_value": new_value,
            "timestamp": datetime.utcnow().isoformat()
        })


# ==========================================
# Claims & Context
# ==========================================

@dataclass
class SignedClaim:
    """A factual claim with source attribution and confidence score."""
    claim: str
    source: str
    confidence: float
    evidence: Optional[str] = None
    verified_at: Optional[datetime] = None

    def __post_init__(self):
        if self.verified_at is None:
            self.verified_at = datetime.utcnow()

class SignalContext(BaseModel):
    """
    The Thermostatic Context Passport that enables high-temperature creativity
    while maintaining structural integrity through dual-state isolation.
    """
    hard_state: HardState = Field(default_factory=HardState)
    soft_state: SoftState = Field(default_factory=SoftState)
    thermal_config: ThermalConfig = Field(default_factory=ThermalConfig)
    signed_claims: List[SignedClaim] = Field(default_factory=list)
    context_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def update_timestamp(self) -> None:
        """Update the last modified timestamp."""
        self.last_modified = datetime.utcnow()

    def add_signed_claim(self, claim: str, source: str, confidence: float, evidence: Optional[str] = None) -> None:
        """Add a signed claim to the context."""
        signed_claim = SignedClaim(claim=claim, source=source, confidence=confidence, evidence=evidence)
        self.signed_claims.append(signed_claim)
