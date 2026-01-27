# /agentic_core/domain/entities.py
# Core Domain Entities using Pydantic V2
# Strategy: Pure data structures, no business logic
# HARDENED: Self-contained SSOT compliance without external dependencies

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict, field_validator

class BaseEntity(BaseModel):
    """
    Root entity for all persistent domain objects.
    Enforces UUIDs and audit timestamps.
    HARDENED: Strict validation with controlled mutability.
    """
    # Strict configuration for SSOT compliance
    model_config = ConfigDict(
        validate_assignment=True,  # Critical hardening against silent state injection
        arbitrary_types_allowed=False,
        frozen=False,  # Allowed only for state fields like updated_at
        strict=True,   # Enforce strict typing
        extra='forbid'  # Prevent arbitrary field injection
    )
    
    id: UUID = Field(
        default_factory=uuid4, 
        description="Unique identifier for the entity",
        frozen=True  # Identity should never change
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), 
        description="Entity creation timestamp",
        frozen=True  # Creation time is immutable
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Mutable state field for audit tracking",
        frozen=False  # Allowed only for state fields like updated_at
    )

class AgentConfig(BaseEntity):
    """
    Configuration profile for an individual agent.
    HARDENED: Explicit Field definitions with validation constraints.
    """
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=64,
        description="Human-readable agent name",
        frozen=True  # Restored SSOT: Identity must not be mutable
    )
    role: str = Field(
        ...,
        min_length=1,
        description="The system role/persona of the agent",
        frozen=True  # Role is part of identity
    )
    model_name: str = Field(
        default="gpt-4o", 
        description="LLM Model ID for the agent",
        frozen=False  # Model can be upgraded
    )
    temperature: float = Field(
        default=0.0, 
        ge=0.0, 
        le=2.0,
        description="LLM temperature setting (0.0=deterministic, 2.0=creative)",
        frozen=False  # Temperature can be tuned
    )
    max_tokens: int = Field(
        default=4096, 
        gt=0,
        description="Maximum tokens for LLM responses",
        frozen=False  # Token limit can be adjusted
    )
    
    # Metadata for pattern recognition (aligned with domain patterns)
    capabilities: list[str] = Field(
        default_factory=list,
        description="List of agent capabilities",
        frozen=False  # Capabilities can evolve
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional configuration metadata",
        frozen=False  # Metadata can be extended
    )

    def update_timestamp(self) -> None:
        """
        Manually refresh updated_at timestamp.
        HARDENED: Explicit type hints and validation.
        """
        self.updated_at = datetime.now(timezone.utc)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate agent name format.
        HARDENED: Added validation to prevent injection.
        """
        from pydantic_core import PydanticCustomError
        import re
        
        if not v or not v.strip():
            raise PydanticCustomError(
                'value_error',
                'Agent name cannot be empty',
            )
        
        # Prevent potential injection in names
        blocked_chars = ['<', '>', '&', '"', "'", '/', '\\']
        if any(char in v for char in blocked_chars):
            raise PydanticCustomError(
                'value_error',
                'Agent name contains invalid characters: {chars}',
                {'chars': ', '.join(c for c in blocked_chars if c in v)}
            )
        
        # Block javascript: protocol and other URL schemes
        if re.match(r'^\w+:', v, re.IGNORECASE):
            raise PydanticCustomError(
                'value_error',
                'Agent name cannot contain URL schemes',
            )
        
        return v.strip()
    
    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """
        Validate model name against known patterns.
        HARDENED: Restrict to known safe model patterns.
        """
        known_models = ['gpt-4o', 'gpt-4', 'gpt-3.5-turbo', 'claude-3', 'claude-2']
        if v not in known_models:
            raise ValueError(f'Unknown model: {v}. Use one of: {known_models}')
        return v