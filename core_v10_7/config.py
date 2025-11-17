"""Configuration schema enforcement for the v10_7 runtime layer."""
from __future__ import annotations

from typing import Dict, Literal, Optional

from pydantic import Field, validator

from .models import V10Model


class ConfigV10_7(V10Model):
    """Strongly typed configuration for v10_7 runtime components."""

    schema_version: Literal["master_config_v10.7"] = "master_config_v10.7"
    default_model: str = "gpt-4o"
    model_aliases: Dict[str, str] = Field(default_factory=dict)
    cache: Dict[str, object] = Field(default_factory=dict)
    budget: Dict[str, object] = Field(default_factory=dict)
    telemetry: Dict[str, object] = Field(default_factory=dict)
    validators: Dict[str, object] = Field(default_factory=dict)
    tuning: Dict[str, object] = Field(default_factory=dict)

    @validator("schema_version")
    def enforce_schema_version(cls, value: str) -> str:
        if value != "master_config_v10.7":
            raise ValueError("Invalid schema_version for ConfigV10_7")
        return value

    def canonical_alias_map(self) -> Dict[str, str]:
        """Return a normalized alias map for model resolution."""

        return {k.lower(): v for k, v in self.model_aliases.items()}


def load_config(data: Optional[Dict[str, object]] = None) -> ConfigV10_7:
    """Build a ConfigV10_7 instance from raw data or defaults."""

    data = data or {}
    return ConfigV10_7(**data)
