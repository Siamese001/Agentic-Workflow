from __future__ import annotations
"""
Tone & Communication Style Schemas
==================================
Defines the communication profiles and generation configurations for 
the Sovereign system. These models ensure output consistency and 
stylistic alignment.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator

# ==========================================
# Style Enums
# ==========================================

class ToneType(str, Enum):
    """Primary tone types for communication style analysis."""
    AUTHORITATIVE = "authoritative"
    EMPATHETIC = "empathetic"
    ANALYTICAL = "analytical"
    ENTHUSIASTIC = "enthusiastic"
    DIRECT = "direct"

# ==========================================
# Communication Profiles
# ==========================================

class StyleProfile(BaseModel):
    """Profile defining a communication style."""
    primary_tone: ToneType = Field(..., description="Primary tone type")
    formality_level: float = Field(default=0.7, ge=0.0, le=1.0, description="Formality level (0=Casual, 1=Academic)")
    emoji_frequency: float = Field(default=0.2, ge=0.0, le=1.0, description="Emoji usage frequency")
    sentence_length_avg: int = Field(default=15, ge=5, le=50, description="Target words per sentence")
    vocabulary_complexity: float = Field(default=0.5, ge=0.0, le=1.0, description="Vocabulary complexity")
    ConfidenceLevel: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in analysis")

    class Config:
        """Pydantic configuration for profile mutability."""
        validate_assignment = True

# ==========================================
# Generation Parameters
# ==========================================

class GenerationConfig(BaseModel):
    """Configuration for LLM generation based on tone profile."""
    system_prompt_fragment: str = Field(..., description="Instruction to inject into prompts")
    temperature_setting: float = Field(..., ge=0.1, le=1.0, description="LLM temperature")
    banned_phrases: List[str] = Field(default_factory=list, description="Phrases to avoid")
    preferred_transitions: List[str] = Field(default_factory=list, description="Preferred transition words")
    max_sentence_length: int = Field(default=25, ge=5, le=100, description="Max words per sentence")

    @validator('temperature_setting')
    def clamp_temperature(cls, v):
        """Ensure temperature is within valid range."""
        return max(0.1, min(1.0, v))
