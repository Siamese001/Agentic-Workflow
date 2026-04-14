"""apps_research — Autonomous Research Engine."""

from __future__ import annotations

from importlib import import_module

__all__ = ["outputs", "reasoning", "services", "types", "integrations"]


def __getattr__(name: str):
    if name in __all__:
        return import_module(f"apps_research.{name}")
    raise AttributeError(f"module 'apps_research' has no attribute {name!r}")
