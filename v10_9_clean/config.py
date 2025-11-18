# config.py
"""
Shared Configuration — v10_9

Central config object for the whole runtime.
"""

from __future__ import annotations
from typing import Dict, Any, Literal, Optional
from pydantic import Field, validator
from .models import V10Model


class ConfigV10_9(V10Model):
    schema_version: Literal["master_config_v10.9"] = "master_config_v10.9"

    default_model: str = "gpt-4.1"
    model_aliases: Dict[str, str] = Field(default_factory=dict)

    budget: Dict[str, Any] = Field(default_factory=dict)
    cache: Dict[str, Any] = Field(default_factory=dict)
    safety: Dict[str, Any] = Field(default_factory=dict)
    telemetry: Dict[str, Any] = Field(default_factory=dict)
    validators: Dict[str, Any] = Field(default_factory=dict)
    tuning: Dict[str, Any] = Field(default_factory=dict)
    tooling: Dict[str, Any] = Field(default_factory=dict)
    environment: Dict[str, Any] = Field(default_factory=dict)

    @validator("schema_version")
    def check_version(cls, v: str) -> str:
        if v != "master_config_v10.9":
            raise ValueError("Invalid schema version")
        return v

    def canonical_alias_map(self) -> Dict[str, str]:
        return {k.lower(): v for k, v in self.model_aliases.items()}

    def resolve_model(self, name: str) -> str:
        if not name:
            return self.default_model
        return self.model_aliases.get(name.lower(), name)


def load_config(data: Optional[Dict[str, Any]] = None) -> ConfigV10_9:
    return ConfigV10_9(**(data or {}))
