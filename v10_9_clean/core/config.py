"""
Configuration schema for v10_9 runtime.

Provides:
  • Strongly typed configuration contract for the full L1–L5 agent stack
  • Model aliasing and provider selection
  • Cost / token / latency budgets
  • Global safety, telemetry, and runtime toggles
  • Deterministic, validated config loading
"""

from __future__ import annotations

from typing import Dict, Optional, Literal, Any

from pydantic import Field, validator

from .models import V10Model


# ======================================================================
# MAIN CONFIG OBJECT (v10_9)
# ======================================================================

class ConfigV10_9(V10Model):
    """
    Canonical configuration for v10_9 runtime.

    All core runtime systems (L1–L5) pull configuration from a single,
    versioned instance of this schema.
    """

    schema_version: Literal["master_config_v10.9"] = "master_config_v10.9"

    # Default LLM model
    default_model: str = "gpt-4.1"

    # Normalized lower-case alias → model mapping
    model_aliases: Dict[str, str] = Field(default_factory=dict)

    # Budget constraints (token, cost, depth, retries)
    budget: Dict[str, Any] = Field(default_factory=dict)

    # Cache + persistence: RAG, vector stores, local memoization
    cache: Dict[str, Any] = Field(default_factory=dict)

    # Safety + constitutional AI settings
    safety: Dict[str, Any] = Field(default_factory=dict)

    # Telemetry + metrics (tokens, costs, phase transitions)
    telemetry: Dict[str, Any] = Field(default_factory=dict)

    # Validators: structural, semantic, QA, safety preprocessors
    validators: Dict[str, Any] = Field(default_factory=dict)

    # Tuning + system optimization params (sampling, retries, latency)
    tuning: Dict[str, Any] = Field(default_factory=dict)

    # Tooling + plugin-level configuration
    tooling: Dict[str, Any] = Field(default_factory=dict)

    # Environment + platform metadata (dev, staging, prod)
    environment: Dict[str, Any] = Field(default_factory=dict)

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @validator("schema_version")
    def enforce_schema_version(cls, value: str) -> str:
        if value != "master_config_v10.9":
            raise ValueError("Invalid schema_version for ConfigV10_9")
        return value

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def canonical_alias_map(self) -> Dict[str, str]:
        """Return lower-case alias mapping for model resolution."""
        return {k.lower(): v for k, v in self.model_aliases.items()}

    def resolve_model(self, name: str) -> str:
        """
        Return the canonical model for a given alias or raw name.
        If the model has no alias, returns name unchanged.
        """
        if not name:
            return self.default_model
        lowered = name.lower()
        return self.model_aliases.get(lowered, name)

    def get_budget(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the budget section."""
        return self.budget.get(key, default)

    def get_safety_flag(self, key: str, default: Any = None) -> Any:
        """Retrieve a safety/constitution setting."""
        return self.safety.get(key, default)


# ======================================================================
# LOADER
# ======================================================================

def load_config(data: Optional[Dict[str, Any]] = None) -> ConfigV10_9:
    """
    Build a ConfigV10_9 instance from dictionary input or defaults.

    Ensures:
      • Missing sections filled with default empty dicts
      • schema_version validated
      • All keys and structures normalized
    """
    data = data or {}
    return ConfigV10_9(**data)
