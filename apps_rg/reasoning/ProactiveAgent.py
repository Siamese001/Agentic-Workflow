"""Proactive RG agent — subclasses ``BaseProactiveAgent``."""

from apps_shared.reasoning.BaseProactiveAgent import BaseProactiveAgent


class ProactiveAgent(BaseProactiveAgent):
    """Resume-generation proactive scaffolding (wired in downstream dispatch)."""

    def __post_init__(self) -> None:
        super().__post_init__()


__all__ = ["ProactiveAgent"]
