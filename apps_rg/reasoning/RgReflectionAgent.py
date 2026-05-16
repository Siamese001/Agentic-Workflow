"""RG reflection agent — subclasses ``BaseReflectionAgent``."""

from apps_shared.reasoning.BaseReflectionAgent import BaseReflectionAgent


class RgReflectionAgent(BaseReflectionAgent):
    """Post-execution reflection agent for RG."""


__all__ = ["RgReflectionAgent"]
