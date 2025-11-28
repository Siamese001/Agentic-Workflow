"""Minimal stub for google.generativeai SDK usage in tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class GenerativeModel:
    name: str

    def generate_content(self, prompt: str, **_: Any) -> Dict[str, Any]:
        return {
            "model": self.name,
            "prompt": prompt,
            "candidates": [
                {
                    "output": f"stubbed generative output for {prompt[:20]}",
                    "safetyAttributes": {"blocked": False},
                }
            ],
        }


def configure(**_kwargs: Any) -> None:  # pragma: no cover - configuration noop
    return None


__all__ = ["GenerativeModel", "configure"]
