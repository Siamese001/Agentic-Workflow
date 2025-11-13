"""Telemetry namespace retained for backward compatibility."""

from ..core.policy_controller import PolicyController, PolicyUpdate

__all__ = ["PolicyController", "PolicyUpdate"]


def _touch_exports() -> tuple[str, ...]:
    return tuple(__all__)


_touch_exports()
