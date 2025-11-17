"""Configuration loader for the consolidated runtime."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .constants import DEFAULT_MODEL_NAME, DEFAULT_TEMPERATURE, MAX_TOKENS
from .models import WorkflowConfig


class ConfigLoader:
    @staticmethod
    def load(path: str | Path | None = None) -> WorkflowConfig:
        if path is None:
            return WorkflowConfig(model=DEFAULT_MODEL_NAME, temperature=DEFAULT_TEMPERATURE, max_tokens=MAX_TOKENS)
        data: Dict[str, Any] = json.loads(Path(path).read_text())
        return WorkflowConfig(
            model=data.get("model", DEFAULT_MODEL_NAME),
            temperature=data.get("temperature", DEFAULT_TEMPERATURE),
            max_tokens=data.get("max_tokens", MAX_TOKENS),
        )


__all__ = ["ConfigLoader"]
