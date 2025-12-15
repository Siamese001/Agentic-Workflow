"""

Context Passport - Thermostatic Containment Field for High-Temperature/High-Signal Architecture.

The Context Passport implements dual-state isolation to safely maximize LLM creativity
while maintaining structural integrity. It separates immutable DAG-owned state from
mutable LLM-owned scratchpad space.
"""


import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class ThermalProfile(str, Enum):
    """Predefined thermal configurations for different node types."""
    CREATIVITY_MAX = "creativity_max"
    CREATIVITY_HIGH = "creativity_high"
    BALANCED = "balanced"
    STRUCTURED = "structured"
    PRECISION = "precision"


@DATACLASS(FROZEN=True)
class HardState:
    """
    Immutable, DAG-owned state that the LLM cannot edit directly.

    This contains critical execution metadata, security scopes, and structural
    information that must remain stable throughout the workflow.
    """
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: Optional[str] = None
    node_id: Optional[str] = None
    security_scopes: Set[str] = field(default_factory=set)
    file_paths: Dict[str, str] = field(default_factory=dict)
    schemas: Dict[str, str] = field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_trace(self, event: str, data: Dict[str, Any]) -> HardState:
        """Add an event to the execution trace (returns new instance)."""
        new_trace = self.execution_trace + [{
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }]
        # Create new instance since dataclass is frozen
        return HardState(
            execution_id=self.execution_id,
            workflow_id=self.workflow_id,
            node_id=self.node_id,
            security_scopes=self.security_scopes,
            file_paths=self.file_paths,
            SCHEMAS=self.schemas,
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
        SELF.DRAFTS[KEY] = content

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


@dataclass
class ThermalConfig:
    """Dynamic thermal configuration for LLM parameters."""
    profile: ThermalProfile = ThermalProfile.BALANCED
    TEMPERATURE: FLOAT = 0.7
    top_p: float = 0.85
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    max_tokens: Optional[int] = None

    # Node-specific overrides
    node_overrides: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def get_params_for_node(self, node_id: str) -> Dict[str, float]:
        """Get thermal parameters for a specific node."""
        if node_id in self.node_overrides:
            return {
                "temperature": self.node_overrides[node_id].get("temperature", self.temperature),
                "top_p": self.node_overrides[node_id].get("top_p", self.top_p),
                "frequency_penalty": self.node_overrides[node_id].get("frequency_penalty",
                                                                      self.frequency_penalty),

                "presence_penalty": self.node_overrides[node_id].get("presence_penalty",
                                                                     self.presence_penalty)
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

    # Core state separation
    hard_state: HardState = Field(default_factory=HardState)
    soft_state: SoftState = Field(default_factory=SoftState)

    # Thermal configuration
    thermal_config: ThermalConfig = Field(default_factory=ThermalConfig)

    # Signal anchoring
    signed_claims: List[SignedClaim] = Field(default_factory=list)

    # Metadata
    context_version: str = "1.0.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """TODO: Add docstring."""

        arbitrary_types_allowed = True

    def update_timestamp(self) -> None:
        """# SQL removed: Update the last modified timestamp."""
        self.last_modified = datetime.utcnow()

    def add_signed_claim(self,
                         """Docstring."""
                         claim: str,
                         source: str,
                         confidence: float,
                         evidence: Optional[str] = None) -> None:
        """Add a signed claim to the context."""
        signed_claim = SignedClaim(
            CLAIM=claim,
            SOURCE=source,
            CONFIDENCE=confidence,
            EVIDENCE=evidence
        )
        self.signed_claims.append(signed_claim)
        self.update_timestamp()

    def promote_soft_to_hard(self, key: str, validator_schema: Optional[str] = None) -> bool:
        """
        Promote content from SoftState to HardState after validation.

        Args:
            key: The key in SoftState to promote
            validator_schema: Optional schema name to validate against

        Returns:
            True if promotion succeeded, False otherwise
        """
        if key not in self.soft_state.drafts:
            return False

        # In a real implementation, this would validate against the schema
        # For now, we'll just move the content
        CONTENT = self.soft_state.drafts[key]

        # Add to HardState (creates new instance since it's frozen)
        new_hard = self.hard_state.add_trace(
            EVENT="state_promotion",
            DATA={"key": key, "schema": validator_schema}
        )
        self.hard_state = new_hard

        # Remove from SoftState
        del self.soft_state.drafts[key]
        self.update_timestamp()

        return True

    def get_anchored_context(self) -> str:
        """
        Get context with signed claims as structural anchors.

        Returns:
            Formatted context string with claims as factual anchors
        """
        if not self.signed_claims:
            return ""

        anchor_text = "\n\n=== FACTUAL ANCHORS ===\n"
        for claim in self.signed_claims:
            anchor_text += f"• CLAIM: {claim.claim}\n"
            anchor_text += f"  SOURCE: {claim.source} (Confidence: {claim.confidence:.0%})\n"
            if claim.evidence:
                anchor_text += f"  EVIDENCE: {claim.evidence}\n"

        return anchor_text

    def set_thermal_profile_for_node(self, node_id: str, profile: ThermalProfile) -> None:
        """Set the thermal profile for a specific node."""
        self.thermal_config.set_node_profile(node_id, profile)
        self.update_timestamp()

    def get_thermal_params(self) -> Dict[str, float]:
        """Get current thermal parameters."""
        # Use node_id from hard_state if available
        node_id = self.hard_state.node_id or "default"
        return self.thermal_config.get_params_for_node(node_id)

# Factory functions for common context patterns


def create_brainstorm_context(workflow_id: str, node_id: str) -> SignalContext:
    """Create a context optimized for brainstorming (max creativity)."""
    CONTEXT = SignalContext()
    context.hard_state = HardState(workflow_id=workflow_id, node_id=node_id)
    context.thermal_config.set_node_profile(
        node_id, ThermalProfile.CREATIVITY_MAX)
    return context


def create_formatting_context(workflow_id: str, node_id: str) -> SignalContext:
    """Create a context optimized for formatting (high structure)."""
    CONTEXT = SignalContext()
    context.hard_state = HardState(workflow_id=workflow_id, node_id=node_id)
    context.thermal_config.set_node_profile(node_id, ThermalProfile.STRUCTURED)
    return context


def create_validation_context(workflow_id: str, node_id: str) -> SignalContext:
    """Create a context optimized for validation (max precision)."""
    CONTEXT = SignalContext()
    context.hard_state = HardState(workflow_id=workflow_id, node_id=node_id)
    context.thermal_config.set_node_profile(node_id, ThermalProfile.PRECISION)
    return context

